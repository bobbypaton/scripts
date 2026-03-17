#!/usr/bin/env python
"""
Weekly Metrics Report
Runs GitHub traffic collection + summary and HF Spaces analytics,
then posts the combined output to Slack.

Usage:
    python weekly_report.py
    python weekly_report.py --test   # print to stdout instead of Slack

Crontab entry (Monday 8am):
    0 8 * * 1 cd /Users/rpaton/Documents/scripts && python metrics/weekly_report.py
"""

import argparse
import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

# Load environment variables from .env file
env_file = Path(__file__).resolve().parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

import requests

# Add metrics dir to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gh_traffic
import hf_spaces_analytics


def capture_output(func, *args, **kwargs):
    """Run a function and capture its stdout."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        func(*args, **kwargs)
    return buf.getvalue()


def build_github_reports():
    """Collect GitHub traffic and return a list of (title_suffix, text) pairs."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return [("GitHub Metrics", "GITHUB_TOKEN not set, skipping.")]

    # Collect silently, then generate summary
    capture_output(
        gh_traffic.fetch_and_collect,
        orgs=["patonlab"],
        repos=[],
        token=token,
        verbose=False,
    )
    full = capture_output(gh_traffic.print_summary, token, overview=False).strip()

    # Split into separate tables to stay under Slack's code block char limit
    # Tables are separated by a blank line between closing '=' and opening '='
    import re
    parts = re.split(r'\n\n+', full)

    # Map parts to titles
    reports = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "Views" in part:
            reports.append(("GitHub Repository Views", part))
        elif "Clones" in part:
            reports.append(("GitHub Repository Clones", part))
        else:
            reports.append(("GitHub Metrics", part))

    return reports if reports else [("GitHub Metrics", full)]


def build_hf_report():
    """Fetch HF Spaces analytics and visit summary."""
    hf_token = (os.environ.get("HF_TOKEN")
                or os.environ.get("HUGGINGFACE_TOKEN"))

    sections = []
    sections.append(capture_output(
        hf_spaces_analytics.run_spaces,
        authors=["patonlab"],
        token=hf_token,
    ))
    sections.append(capture_output(hf_spaces_analytics.print_visit_summary).strip())
    return "\n\n".join(s.strip() for s in sections if s.strip())


def post_to_slack(title, text, webhook_url):
    """Post a message to Slack via webhook."""
    payload = {"text": f"*{title}*\n```{text}```"}
    resp = requests.post(
        webhook_url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    if resp.status_code != 200:
        print(f"Slack error: {resp.status_code} {resp.text}", file=sys.stderr)
    else:
        print(f"Posted '{title}' to Slack.")


def main():
    parser = argparse.ArgumentParser(description="Weekly Metrics Report")
    parser.add_argument(
        "--test", action="store_true",
        help="Print to stdout instead of posting to Slack"
    )
    args = parser.parse_args()

    gh_reports = build_github_reports()
    hf_report = build_hf_report()

    if args.test:
        for _, text in gh_reports:
            print(text)
        print(hf_report)
        return

    webhook_url = os.environ.get("SLACK_WEBHOOK_METRICS")
    if not webhook_url:
        print("Error: SLACK_WEBHOOK_METRICS not set in .env", file=sys.stderr)
        print("Falling back to stdout:\n")
        for _, text in gh_reports:
            print(text)
        print(hf_report)
        sys.exit(1)

    from datetime import datetime
    date_str = datetime.now().strftime("%m/%d/%Y")
    for title, text in gh_reports:
        post_to_slack(f"{title} {date_str}", text, webhook_url)
    post_to_slack(f"Weekly Hugging Face Metrics {date_str}", hf_report, webhook_url)


if __name__ == "__main__":
    main()
