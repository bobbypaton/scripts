import paramiko
import json
import sys
import argparse
import os
import requests
import concurrent.futures
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
HEAD_NODE_IP = "129.82.77.43"
HEAD_NODE_USER = os.getenv("HEAD_NODE_USER", "rpaton")

# List of nodes: node01, node02... node20
NODES = [f"node{i:02d}" for i in range(1, 21)]

# Load credentials from environment variables
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_ACME")

# Timeouts and thread pool settings
SSH_TIMEOUT = 10
PING_TIMEOUT = 1
MAX_WORKERS = 5
RETRY_ATTEMPTS = 1

# --- CORE LOGIC ---

def check_node_via_jump(node_hostname, retry=True):
    """
    Connects to head node and attempts to reach the target node.
    Returns tuple of (node_hostname, is_up, error_message)
    """
    gateway = None
    try:
        # Connect to the Head Node
        gateway = paramiko.SSHClient()
        gateway.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # This assumes SSH keys are set up for passwordless access
        gateway.connect(
            HEAD_NODE_IP,
            username=HEAD_NODE_USER,
            timeout=SSH_TIMEOUT
        )

        # Execute ping check from the head node
        _, stdout, _ = gateway.exec_command(
            f"ping -c 1 -W {PING_TIMEOUT} {node_hostname}"
        )

        # Wait for command to finish
        exit_status = stdout.channel.recv_exit_status()

        is_up = exit_status == 0

        # Retry once if node appears down
        if not is_up and retry and RETRY_ATTEMPTS > 0:
            return check_node_via_jump(node_hostname, retry=False)

        return node_hostname, is_up, None

    except paramiko.AuthenticationException as e:
        error_msg = f"Authentication failed: {str(e)}"
        print(f"Error connecting to {node_hostname} via {HEAD_NODE_IP}: {error_msg}", file=sys.stderr)
        return node_hostname, False, error_msg
    except paramiko.SSHException as e:
        error_msg = f"SSH error: {str(e)}"
        print(f"Error connecting to {node_hostname} via {HEAD_NODE_IP}: {error_msg}", file=sys.stderr)
        return node_hostname, False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"Error connecting to {node_hostname} via {HEAD_NODE_IP}: {error_msg}", file=sys.stderr)
        return node_hostname, False, error_msg
    finally:
        if gateway:
            gateway.close()

def send_slack_alert(down_nodes):
    if not SLACK_WEBHOOK_URL:
        raise ValueError("SLACK_WEBHOOK_URL environment variable is not set")

    message = {
        "text": "🚨 *ACME Alert: Internal Nodes Down!*",
        "attachments": [{
            "color": "danger",
            "text": f"The following nodes are unreachable from head node ({HEAD_NODE_IP}):\n" +
                    ", ".join([f"`{n}`" for n in down_nodes])
        }]
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(message),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Slack notification: {e}", file=sys.stderr)
        return False

def verify_head_node_connection():
    """Verify we can connect to the head node before checking all nodes."""
    gateway = None
    try:
        gateway = paramiko.SSHClient()
        gateway.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        gateway.connect(
            HEAD_NODE_IP,
            username=HEAD_NODE_USER,
            timeout=SSH_TIMEOUT
        )
        return True
    except paramiko.AuthenticationException:
        print(f"ERROR: Authentication failed for {HEAD_NODE_USER}@{HEAD_NODE_IP}", file=sys.stderr)
        print("Make sure SSH keys are set up for passwordless access.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: Cannot connect to head node {HEAD_NODE_IP}: {e}", file=sys.stderr)
        return False
    finally:
        if gateway:
            gateway.close()


def main():
    parser = argparse.ArgumentParser(description="Check ACME internal node health via head node")
    parser.add_argument("--test", action="store_true", help="Print report to stdout instead of sending to Slack")
    args = parser.parse_args()

    # Validate required environment variables
    if not args.test and not SLACK_WEBHOOK_URL:
        print("ERROR: SLACK_WEBHOOK_URL environment variable must be set", file=sys.stderr)
        sys.exit(1)

    # Verify head node connection first
    print(f"Verifying connection to head node {HEAD_NODE_IP}...")
    if not verify_head_node_connection():
        sys.exit(1)

    print(f"Starting check for {len(NODES)} nodes via {HEAD_NODE_IP}...")

    # Using ThreadPoolExecutor because SSH is I/O bound
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(check_node_via_jump, NODES))

    down_nodes = [name for name, is_up, _ in results if not is_up]
    up_nodes = [name for name, is_up, _ in results if is_up]

    print(f"\n{'='*50}")
    print(f"Results: {len(up_nodes)} up, {len(down_nodes)} down")
    print(f"{'='*50}")

    if up_nodes:
        print(f"✓ Up ({len(up_nodes)}): {', '.join(up_nodes)}")

    if down_nodes:
        print(f"✗ Down ({len(down_nodes)}): {', '.join(down_nodes)}")

        if args.test:
            print("\n[TEST MODE] Slack alert would have been sent")
        else:
            success = send_slack_alert(down_nodes)
            if success:
                print("\nSlack alert sent successfully.")
            else:
                print("\nFailed to send Slack alert.", file=sys.stderr)
                sys.exit(1)
    else:
        print("\n✓ All internal nodes are reachable.")

if __name__ == "__main__":
    main()

