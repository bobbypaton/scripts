#!/usr/bin/env python3
"""
Hugging Face Spaces Analytics
Fetches space metadata, tracks visits, and summarizes analytics for HF Spaces.

Usage:
    python hf_spaces_analytics.py spaces
    python hf_spaces_analytics.py spaces --authors patonlab bobbypaton
    python hf_spaces_analytics.py visits

Visit tracking (for use inside a Space):
    from hf_spaces_analytics import log_visit
    log_visit()
"""

import argparse
import csv
import io
import os
import sys
from datetime import datetime, timezone
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

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

try:
    from huggingface_hub import HfApi, hf_hub_download
    from huggingface_hub.utils import EntryNotFoundError
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub", "-q"])
    from huggingface_hub import HfApi, hf_hub_download
    from huggingface_hub.utils import EntryNotFoundError


# ── Visit tracking config ────────────────────────────────────────────────────
ANALYTICS_REPO = "patonlab/analytics"   # your private dataset repo
ANALYTICS_FILE = "visits.csv"           # filename inside that repo
SPACE_NAME     = "patonlab/alfabet_bde" # default label stored in each row
# ─────────────────────────────────────────────────────────────────────────────


def _get_token():
    return os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")


# ── Visit tracking ───────────────────────────────────────────────────────────

def log_visit(space=SPACE_NAME):
    """Append one row to visits.csv in the analytics dataset repo."""
    token = _get_token()
    if not token:
        print("[visit_counter] HF_TOKEN not set — skipping visit log.")
        return

    api = HfApi(token=token)
    now = datetime.now(timezone.utc).isoformat()

    # Try to download existing CSV
    existing_rows = []
    try:
        path = hf_hub_download(
            repo_id=ANALYTICS_REPO,
            filename=ANALYTICS_FILE,
            repo_type="dataset",
            token=token,
        )
        with open(path, newline="") as f:
            existing_rows = list(csv.DictReader(f))
    except EntryNotFoundError:
        pass  # first visit ever — file doesn't exist yet

    existing_rows.append({"space": space, "timestamp": now})

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["space", "timestamp"])
    writer.writeheader()
    writer.writerows(existing_rows)

    api.upload_file(
        path_or_fileobj=buf.getvalue().encode(),
        path_in_repo=ANALYTICS_FILE,
        repo_id=ANALYTICS_REPO,
        repo_type="dataset",
        commit_message=f"visit: {space} @ {now}",
    )
    print(f"[visit_counter] Logged visit for {space} at {now}")


def get_visit_rows():
    """Return a list of {'space': ..., 'timestamp': ...} dicts from the analytics repo."""
    token = _get_token()
    if not token:
        return []
    try:
        path = hf_hub_download(
            repo_id=ANALYTICS_REPO,
            filename=ANALYTICS_FILE,
            repo_type="dataset",
            token=token,
        )
        with open(path, newline="") as f:
            return list(csv.DictReader(f))
    except EntryNotFoundError:
        return []


def get_visit_counts():
    """Return a dict of {space_name: visit_count} from the analytics repo."""
    counts = {}
    for row in get_visit_rows():
        counts[row["space"]] = counts.get(row["space"], 0) + 1
    return counts


def print_visit_summary():
    """Print visit analytics with total, this-year, and monthly breakdowns."""
    rows = get_visit_rows()
    if not rows:
        print("No visit data yet.")
        return

    now = datetime.now(timezone.utc)
    current_year = now.year

    # Build per-month counts keyed by (year, month)
    # Generate the last 12 months as ordered keys
    months = []
    for i in range(11, -1, -1):
        y = now.year
        m = now.month - i
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))

    # Aggregate per space
    spaces = {}
    for row in rows:
        space = row["space"]
        try:
            ts = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
        except (ValueError, KeyError):
            continue
        if space not in spaces:
            spaces[space] = {"total": 0, "year": 0, "months": {}}
        spaces[space]["total"] += 1
        if ts.year == current_year:
            spaces[space]["year"] += 1
        key = (ts.year, ts.month)
        if key in dict.fromkeys(months):
            spaces[space]["months"][key] = spaces[space]["months"].get(key, 0) + 1

    # Month column headers
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_hdrs = [f"{month_names[m-1]}" for y, m in months]

    # Print table
    col_w = 5
    name_w = 35
    # 2 leading spaces + name_w + (Total + Year + 12 months) columns with separating spaces
    table_w = 2 + name_w + (14 * (1 + col_w))
    sep_line = f"  {'-'*name_w} {'-'*col_w} {'-'*col_w}" + f" {'-'*col_w}" * 12
    print(f"{'='*table_w}")
    print(f"🤗  HF Spaces Visit Summary")
    print(f"{'='*table_w}")
    header = f"  {'Space':<{name_w}} {'Total':>{col_w}} {str(current_year):>{col_w}}"
    for h in month_hdrs:
        header += f" {h:>{col_w}}"
    print(header)
    print(sep_line)

    grand_total = 0
    grand_year = 0
    grand_months = {k: 0 for k in months}

    for space in sorted(spaces, key=lambda s: -spaces[s]["total"]):
        d = spaces[space]
        grand_total += d["total"]
        grand_year += d["year"]
        short_name = space.split("/")[-1] if "/" in space else space
        line = f"  {short_name:<{name_w}} {d['total']:>{col_w}} {d['year']:>{col_w}}"
        for key in months:
            n = d["months"].get(key, 0)
            grand_months[key] += n
            line += f" {n:>{col_w}}" if n else f" {'·':>{col_w}}"
        print(line)

    # Totals row
    line = f"  {'TOTAL':<{name_w}} {grand_total:>{col_w}} {grand_year:>{col_w}}"
    for key in months:
        n = grand_months[key]
        line += f" {n:>{col_w}}" if n else f" {'·':>{col_w}}"
    print(sep_line)
    print(line)
    print(f"{'='*table_w}\n")


# ── Spaces analytics ─────────────────────────────────────────────────────────

def fetch_spaces(author, token=None):
    """Fetch all spaces for a given author via HF API."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    spaces = []
    url = "https://huggingface.co/api/spaces"
    params = {"author": author, "limit": 100, "full": "true"}

    while url:
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 401:
            print("  ⚠ 401 Unauthorized — try passing --token hf_xxx for private spaces")
            break
        if resp.status_code != 200:
            print(f"  ⚠ HTTP {resp.status_code} for {author}: {resp.text[:200]}")
            break
        data = resp.json()
        if not data:
            break
        spaces.extend(data)
        # Pagination: HF uses Link header
        link = resp.headers.get("Link", "")
        url = None
        params = {}
        if 'rel="next"' in link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split(";")[0].strip().strip("<>")
                    break

    return spaces


def fmt_date(iso):
    if not iso:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso[:10]


def print_spaces_summary(spaces, author):
    if not spaces:
        print(f"  No spaces found for '{author}'.")
        return

    total_likes = sum(s.get("likes", 0) for s in spaces)
    sdks = {}
    for s in spaces:
        sdk = s.get("cardData", {}).get("sdk") or s.get("sdk", "unknown")
        sdks[sdk] = sdks.get(sdk, 0) + 1

    running = sum(1 for s in spaces if s.get("runtime", {}).get("stage") == "RUNNING")
    private = sum(1 for s in spaces if s.get("private", False))

    print(f"\n{'='*60}")
    print(f"  Author : {author}")
    print(f"  Spaces : {len(spaces)}  |  Likes (total): {total_likes}")
    print(f"  Running: {running}  |  Private: {private}")
    print(f"  SDKs   : {', '.join(f'{k}({v})' for k,v in sorted(sdks.items()))}")
    print(f"{'='*60}")
    print(f"  {'Space':<40} {'Likes':>6}  {'SDK':<12}  {'Created':<12}  {'Status'}")
    print(f"  {'-'*40} {'-'*6}  {'-'*12}  {'-'*12}  {'-'*10}")

    for s in sorted(spaces, key=lambda x: x.get("likes", 0), reverse=True):
        name = s.get("id", "?").split("/")[-1]
        likes = s.get("likes", 0)
        sdk = s.get("cardData", {}).get("sdk") or s.get("sdk", "?")
        created = fmt_date(s.get("createdAt", ""))
        stage = s.get("runtime", {}).get("stage") or s.get("status", "?")
        print(f"  {name:<40} {likes:>6}  {sdk:<12}  {created:<12}  {stage}")


# ── Callable entry points ─────────────────────────────────────────────────────

def run_spaces(authors=None, token=None):
    """Fetch and print spaces summary. Callable from other scripts."""
    if authors is None:
        authors = ["patonlab"]
    if token is None:
        token = _get_token()

    print("\n🤗 Hugging Face Spaces Analytics")
    print(f"   Fetching data for: {', '.join(authors)}")
    if token:
        print("   Using API token ✓")
    print()

    all_spaces = []
    for author in authors:
        print(f"→ Fetching spaces for '{author}'...")
        spaces = fetch_spaces(author, token)
        print(f"  Found {len(spaces)} space(s).")
        print_spaces_summary(spaces, author)
        all_spaces.extend(spaces)

    if len(authors) > 1 and all_spaces:
        total_likes = sum(s.get("likes", 0) for s in all_spaces)
        print(f"{'='*60}")
        print(f"  COMBINED TOTAL")
        print(f"  Spaces : {len(all_spaces)}  |  Total likes: {total_likes}")
        print(f"{'='*60}\n")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="HF Spaces Analytics")
    sub = parser.add_subparsers(dest="command")

    # spaces subcommand
    sp = sub.add_parser("spaces", help="Fetch and summarize HF Spaces metadata")
    sp.add_argument(
        "--authors", nargs="+",
        default=["patonlab"],
        help="HF usernames or org names (default: patonlab bobbypaton)"
    )
    sp.add_argument(
        "--token", default=None,
        help="HF API token (or set HF_TOKEN / HUGGINGFACE_TOKEN env var)"
    )

    # visits subcommand
    sub.add_parser("visits", help="Print visit count summary from analytics repo")

    args = parser.parse_args()

    if args.command == "visits":
        print_visit_summary()
    elif args.command == "spaces":
        run_spaces(authors=args.authors, token=args.token or _get_token())
    else:
        parser.print_help()


# ── Example integration (for use inside a HF Space) ─────────────────────────
# In your app's main entry point (e.g. app.py), add:
#
#   from hf_spaces_analytics import log_visit
#   log_visit()   # <-- one line, runs at startup
#
# For Gradio specifically, put it just before gr.launch():
#
#   import gradio as gr
#   from hf_spaces_analytics import log_visit
#   log_visit()
#   demo.launch()
#
# For a Gradio "on load" event (fires each time UI loads in browser):
#
#   with gr.Blocks() as demo:
#       demo.load(fn=log_visit)
#   demo.launch()
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
