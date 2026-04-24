#!/usr/bin/env python
import subprocess
import requests
import json
import sys
import argparse
import paramiko
import os
from pathlib import Path

# Load environment variables from .env file
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

# --- CONFIGURATION ---
# Machine list from comma-separated env var
MACHINES = [m.strip() for m in os.getenv("MACHINES", "").split(",") if m.strip()]

# Load credentials from environment variables
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_UNIX")
SSH_USER = os.getenv("SSH_USER")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")

# Special username mappings for specific hosts (format: "host1:user1,host2:user2")
SSH_USERS = {}
if os.getenv("SSH_USERS_MAP"):
    for entry in os.getenv("SSH_USERS_MAP").split(","):
        entry = entry.strip()
        if ":" in entry:
            host, user = entry.split(":", 1)
            SSH_USERS[host.strip()] = user.strip()

# Timeouts and thresholds
PING_TIMEOUT = 1
SSH_TIMEOUT = 3

# ---------------------

def get_node_status(host):
    # Ping check
    ping = subprocess.run(
        ["/sbin/ping", "-c", "1", "-W", str(PING_TIMEOUT), host],
        capture_output=True
    )
    if ping.returncode != 0:
        # Retry with a longer window: hosts configured for wake-on-LAN
        # may take a few seconds to come online after the first probe.
        ping = subprocess.run(
            ["/sbin/ping", "-c", "5", "-W", "2", host],
            capture_output=True
        )
        if ping.returncode != 0:
            return "🔴 OFFLINE", "Critical"

    # Load check via SSH
    client = None
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Get the appropriate username for this host
        username = SSH_USERS.get(host, SSH_USER)

        client.connect(
            host,
            username=username,
            password=SSH_PASSWORD,
            timeout=SSH_TIMEOUT
        )

        stdin, stdout, stderr = client.exec_command("nproc; uptime")
        lines = stdout.read().decode('utf-8').strip().splitlines()

        if len(lines) < 2:
            return "⚪ SSH ERROR: Invalid output", "Warning"

        nproc = int(lines[0].strip())
        load_line = lines[-1]

        # Parse load average more defensively
        if "load average:" not in load_line:
            return "⚪ SSH ERROR: Cannot parse load", "Warning"

        load_str = load_line.split("load average:")[1].split(",")[0].strip()
        load_val = float(load_str)

        if load_val > nproc:
            return f"🟡 HIGH LOAD ({load_str})", "Warning"
        return f"🟢 HEALTHY ({load_str})", "OK"

    except paramiko.AuthenticationException:
        return "⚪ SSH ERROR: Authentication failed", "Warning"
    except paramiko.SSHException as e:
        return f"⚪ SSH ERROR: {str(e)}", "Warning"
    except (ValueError, IndexError) as e:
        return f"⚪ PARSE ERROR: {str(e)}", "Warning"
    except Exception as e:
        return f"⚪ ERROR: {str(e)}", "Warning"
    finally:
        if client:
            client.close()

def send_slack_report(full_status_list):
    if not SLACK_WEBHOOK_URL:
        raise ValueError("SLACK_WEBHOOK_URL environment variable is not set")

    report_body = "\n".join(full_status_list)

    payload = {
        "text": "Group Linux Machines Health Report",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📊 Group Linux Machines Health Report"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Checked {len(MACHINES)} machines (current CPU load):\n\n{report_body}"}
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": "Next automated check: Monday at 08:00 AM"}]
            }
        ]
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Slack notification: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Check cluster health")
    parser.add_argument("--test", action="store_true", help="Print report to stdout instead of sending to Slack")
    args = parser.parse_args()

    # Validate required environment variables
    if not MACHINES:
        print("ERROR: MACHINES environment variable must be set (comma-separated hostnames)", file=sys.stderr)
        sys.exit(1)

    if not SSH_USER:
        print("ERROR: SSH_USER environment variable must be set", file=sys.stderr)
        sys.exit(1)

    if not args.test and not SLACK_WEBHOOK_URL:
        print("ERROR: SLACK_WEBHOOK_UNIX environment variable must be set", file=sys.stderr)
        sys.exit(1)

    if not SSH_PASSWORD:
        print("ERROR: SSH_PASSWORD environment variable must be set", file=sys.stderr)
        sys.exit(1)

    full_report = []

    for host in MACHINES:
        status_text, severity = get_node_status(host)
        full_report.append(f"*{host}*: {status_text}")

    if args.test:
        print("\n".join(full_report))
    else:
        success = send_slack_report(full_report)
        if success:
            print("Report sent to Slack successfully.")
        else:
            print("Failed to send report to Slack.", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
