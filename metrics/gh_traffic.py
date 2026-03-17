#!/usr/bin/env python3
"""
GitHub Traffic Logger
Fetches traffic stats (views, clones) for GitHub repos and appends them to local
CSVs. Run weekly via cron to avoid losing the 14-day window.

Usage:
    python gh_traffic.py
    python gh_traffic.py --orgs patonlab bobbypaton
    python gh_traffic.py --repos patonlab/aqme patonlab/goodvibes
    python gh_traffic.py --test

Setup:
    Set GITHUB_TOKEN in your .env file (needs push access to target repos).
    Create a token at https://github.com/settings/tokens with 'repo' scope.
"""

import argparse
import csv
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

# ── Config ────────────────────────────────────────────────────────────────────
DEFAULT_ORGS = ["patonlab"]
DATA_DIR = Path(__file__).resolve().parent / "data"
VIEWS_CSV = DATA_DIR / "gh_views.csv"
CLONES_CSV = DATA_DIR / "gh_clones.csv"
API_BASE = "https://api.github.com"
# ─────────────────────────────────────────────────────────────────────────────


def get_token():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN not set. Add it to .env or export it.")
        sys.exit(1)
    return token


def api_get(endpoint, token):
    """Make an authenticated GET request to the GitHub API."""
    resp = requests.get(
        f"{API_BASE}{endpoint}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    if resp.status_code == 403 and "rate limit" in resp.text.lower():
        print("  ⚠ GitHub API rate limit reached")
        return None
    if resp.status_code != 200:
        print(f"  ⚠ HTTP {resp.status_code} for {endpoint}: {resp.text[:200]}")
        return None
    return resp.json()


def list_org_repos(org, token):
    """List all repos for an org/user (public + private if token has access)."""
    repos = []
    page = 1
    while True:
        data = api_get(f"/orgs/{org}/repos?per_page=100&page={page}&type=all", token)
        if data is None:
            # Try as user instead of org
            data = api_get(f"/users/{org}/repos?per_page=100&page={page}&type=all", token)
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return [r["full_name"] for r in repos]


def append_csv(filepath, fieldnames, rows):
    """Append rows to a CSV, creating with headers if it doesn't exist."""
    exists = filepath.exists() and filepath.stat().st_size > 0
    with open(filepath, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def fetch_and_log_traffic(repo, token, test=False):
    """Fetch all traffic data for a repo and append to CSVs."""
    collected = datetime.now(timezone.utc).isoformat()
    new_views = 0
    new_clones = 0

    # Views (daily breakdown)
    data = api_get(f"/repos/{repo}/traffic/views", token)
    if data and data.get("views"):
        rows = []
        for v in data["views"]:
            rows.append({
                "repo": repo,
                "date": v["timestamp"][:10],
                "views": v["count"],
                "unique_views": v["uniques"],
                "collected": collected,
            })
        new_views = len(rows)
        if not test:
            append_csv(VIEWS_CSV, ["repo", "date", "views", "unique_views", "collected"], rows)

    # Clones (daily breakdown)
    data = api_get(f"/repos/{repo}/traffic/clones", token)
    if data and data.get("clones"):
        rows = []
        for c in data["clones"]:
            rows.append({
                "repo": repo,
                "date": c["timestamp"][:10],
                "clones": c["count"],
                "unique_clones": c["uniques"],
                "collected": collected,
            })
        new_clones = len(rows)
        if not test:
            append_csv(CLONES_CSV, ["repo", "date", "clones", "unique_clones", "collected"], rows)

    return new_views, new_clones


def deduplicate_csv(filepath, verbose=True):
    """Remove duplicate rows from a CSV based on all columns except 'collected'."""
    if not filepath.exists():
        return
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Deduplicate by all fields except 'collected' (keep first occurrence)
    seen = set()
    unique = []
    key_fields = [f for f in fieldnames if f != "collected"]
    for row in rows:
        key = tuple(row[f] for f in key_fields)
        if key not in seen:
            seen.add(key)
            unique.append(row)

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique)

    removed = len(rows) - len(unique)
    if removed and verbose:
        print(f"  Deduplicated {filepath.name}: removed {removed} duplicate rows")


def fetch_repo_stats(repo, token):
    """Fetch stars, forks, and watchers for a repo."""
    data = api_get(f"/repos/{repo}", token)
    if not data:
        return 0, 0, 0
    return (
        data.get("stargazers_count", 0),
        data.get("forks_count", 0),
        data.get("subscribers_count", 0),  # watchers (subscribers) in API
    )


def _load_daily_rows():
    """Load view and clone CSV rows, returning (view_rows, clone_rows)."""
    view_rows = []
    clone_rows = []
    if VIEWS_CSV.exists():
        with open(VIEWS_CSV, newline="") as f:
            view_rows = list(csv.DictReader(f))
    if CLONES_CSV.exists():
        with open(CLONES_CSV, newline="") as f:
            clone_rows = list(csv.DictReader(f))
    return view_rows, clone_rows


def _build_month_keys(view_rows, clone_rows):
    """Determine the last 12 months that have data, ordered oldest-first."""
    now = datetime.now(timezone.utc)
    months = []
    for i in range(11, -1, -1):
        y = now.year
        m = now.month - i
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))
    return months


def print_summary(token=None, overview=True, top=12):
    """Print a summary of stored traffic data with live repo stats and monthly breakdown."""
    view_rows, clone_rows = _load_daily_rows()

    if not view_rows and not clone_rows:
        print("\n  No data yet. Run a collection first.\n")
        return

    now = datetime.now(timezone.utc)
    current_year = now.year
    months = _build_month_keys(view_rows, clone_rows)
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Aggregate per repo: totals, year, and monthly
    repos = {}
    empty = {"views": 0, "unique_views": 0, "clones": 0, "unique_clones": 0,
             "year_views": 0, "year_clones": 0, "month_views": {}, "month_clones": {}}

    for row in view_rows:
        repo = row["repo"]
        if repo not in repos:
            repos[repo] = {k: (dict(v) if isinstance(v, dict) else v) for k, v in empty.items()}
        repos[repo]["views"] += int(row["views"])
        repos[repo]["unique_views"] += int(row["unique_views"])
        date = row["date"]
        y, m = int(date[:4]), int(date[5:7])
        if y == current_year:
            repos[repo]["year_views"] += int(row["views"])
        key = (y, m)
        repos[repo]["month_views"][key] = repos[repo]["month_views"].get(key, 0) + int(row["views"])

    for row in clone_rows:
        repo = row["repo"]
        if repo not in repos:
            repos[repo] = {k: (dict(v) if isinstance(v, dict) else v) for k, v in empty.items()}
        repos[repo]["clones"] += int(row["clones"])
        repos[repo]["unique_clones"] += int(row["unique_clones"])
        date = row["date"]
        y, m = int(date[:4]), int(date[5:7])
        if y == current_year:
            repos[repo]["year_clones"] += int(row["clones"])
        key = (y, m)
        repos[repo]["month_clones"][key] = repos[repo]["month_clones"].get(key, 0) + int(row["clones"])

    # Fetch live repo stats if token is available
    has_stats = token is not None
    if has_stats:
        for repo in repos:
            stars, forks, watchers = fetch_repo_stats(repo, token)
            repos[repo].update({"stars": stars, "forks": forks, "watchers": watchers})

    # ── Overview table ────────────────────────────────────────────────────
    if overview:
        print(f"\n{'='*90}")
        print(f"  GitHub Traffic Summary")
        print(f"{'='*90}")

        sep = f"  {'-'*40} {'-'*8} {'-'*8} {'-'*8} {'-'*8}"
        header = f"  {'Repo':<40} {'Views':>8} {'Uniq':>8} {'Clones':>8} {'Uniq':>8}"
        if has_stats:
            sep += f" {'-'*6} {'-'*6} {'-'*6}"
            header += f" {'Stars':>6} {'Forks':>6} {'Watch':>6}"
        print(f"\n{header}")
        print(sep)

        for repo in sorted(repos, key=lambda r: -repos[r]["views"]):
            d = repos[repo]
            line = f"  {repo:<40} {d['views']:>8} {d['unique_views']:>8} {d['clones']:>8} {d['unique_clones']:>8}"
            if has_stats:
                line += f" {d['stars']:>6} {d['forks']:>6} {d['watchers']:>6}"
            print(line)

        total = {k: sum(d[k] for d in repos.values()) for k in ["views", "unique_views", "clones", "unique_clones"]}
        print(sep)
        line = f"  {'TOTAL':<40} {total['views']:>8} {total['unique_views']:>8} {total['clones']:>8} {total['unique_clones']:>8}"
        if has_stats:
            line += f" {sum(d['stars'] for d in repos.values()):>6}"
            line += f" {sum(d['forks'] for d in repos.values()):>6}"
            line += f" {sum(d['watchers'] for d in repos.values()):>6}"
        print(line)

    # ── Monthly views breakdown ───────────────────────────────────────────
    col_w = 5
    name_w = max(len(r) for r in repos) + 2
    month_hdrs = [month_names[m - 1] for y, m in months]

    # Table width: 2 leading spaces + name_w + (Total + Year + 12 months) columns
    table_w = 2 + name_w + (14 * (1 + col_w))
    sep_line = f"  {'-'*name_w} {'-'*col_w} {'-'*col_w}" + f" {'-'*col_w}" * 12

    print(f"\n{'='*table_w}")
    print(f"🤖  GitHub Repository Views (top {top})")
    print(f"{'='*table_w}")
    header = f"  {'Repo':<{name_w}} {'Total':>{col_w}} {str(current_year):>{col_w}}"
    for h in month_hdrs:
        header += f" {h:>{col_w}}"
    print(header)
    print(sep_line)

    grand = {"total": 0, "year": 0, "months": {k: 0 for k in months}}
    sorted_by_views = sorted(repos, key=lambda r: -repos[r]["views"])
    for i, repo in enumerate(sorted_by_views):
        d = repos[repo]
        grand["total"] += d["views"]
        grand["year"] += d["year_views"]
        for key in months:
            grand["months"][key] = grand["months"].get(key, 0) + d["month_views"].get(key, 0)
        if i < top:
            line = f"  {repo:<{name_w}} {d['views']:>{col_w}} {d['year_views']:>{col_w}}"
            for key in months:
                n = d["month_views"].get(key, 0)
                line += f" {n:>{col_w}}" if n else f" {'·':>{col_w}}"
            print(line)

    print(sep_line)
    line = f"  {'TOTAL':<{name_w}} {grand['total']:>{col_w}} {grand['year']:>{col_w}}"
    for key in months:
        n = grand["months"][key]
        line += f" {n:>{col_w}}" if n else f" {'·':>{col_w}}"
    print(line)

    # ── Monthly clones breakdown ──────────────────────────────────────────
    print(f"\n{'='*table_w}")
    print(f"🤖  GitHub Repository Clones (top {top})")
    print(f"{'='*table_w}")
    header = f"  {'Repo':<{name_w}} {'Total':>{col_w}} {str(current_year):>{col_w}}"
    for h in month_hdrs:
        header += f" {h:>{col_w}}"
    print(header)
    print(sep_line)

    grand = {"total": 0, "year": 0, "months": {k: 0 for k in months}}
    sorted_by_clones = sorted(repos, key=lambda r: -repos[r]["clones"])
    for i, repo in enumerate(sorted_by_clones):
        d = repos[repo]
        grand["total"] += d["clones"]
        grand["year"] += d["year_clones"]
        for key in months:
            grand["months"][key] = grand["months"].get(key, 0) + d["month_clones"].get(key, 0)
        if i < top:
            line = f"  {repo:<{name_w}} {d['clones']:>{col_w}} {d['year_clones']:>{col_w}}"
            for key in months:
                n = d["month_clones"].get(key, 0)
                line += f" {n:>{col_w}}" if n else f" {'·':>{col_w}}"
            print(line)

    print(sep_line)
    line = f"  {'TOTAL':<{name_w}} {grand['total']:>{col_w}} {grand['year']:>{col_w}}"
    for key in months:
        n = grand["months"][key]
        line += f" {n:>{col_w}}" if n else f" {'·':>{col_w}}"
    print(line)

    print(f"{'='*table_w}\n")


def fetch_and_collect(orgs=None, repos=None, token=None, test=False, verbose=True):
    """Collect traffic data for given orgs/repos. Callable from other scripts."""
    if orgs is None:
        orgs = DEFAULT_ORGS
    if repos is None:
        repos = []
    else:
        repos = list(repos)

    for org in orgs:
        if verbose:
            print(f"→ Listing repos for '{org}'...")
        org_repos = list_org_repos(org, token)
        if verbose:
            print(f"  Found {len(org_repos)} repo(s).")
        repos.extend(org_repos)

    if not repos:
        if verbose:
            print("No repos found.")
        return

    # Create data directory
    if not test:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"\n→ Collecting traffic for {len(repos)} repo(s)...")
    total_views = 0
    total_clones = 0
    for repo in sorted(repos):
        views, clones = fetch_and_log_traffic(repo, token, test=test)
        if verbose:
            status = f"{views} view days, {clones} clone days"
            if test:
                status += " (dry run)"
            print(f"  {repo:<40} {status}")
        total_views += views
        total_clones += clones

    # Deduplicate after collection (handles overlapping 14-day windows)
    if not test:
        for csv_file in [VIEWS_CSV, CLONES_CSV]:
            deduplicate_csv(csv_file, verbose=verbose)

    if verbose:
        print(f"\nDone. Logged {total_views} view rows, {total_clones} clone rows.")
        if not test:
            print(f"Data stored in {DATA_DIR}/")


def main():
    parser = argparse.ArgumentParser(description="GitHub Traffic Logger")
    sub = parser.add_subparsers(dest="command")

    # collect subcommand
    collect = sub.add_parser("collect", help="Fetch and log traffic data")
    collect.add_argument(
        "--orgs", nargs="+", default=DEFAULT_ORGS,
        help="GitHub orgs/users to fetch all repos for (default: patonlab)"
    )
    collect.add_argument(
        "--repos", nargs="+", default=[],
        help="Specific repos (owner/name) to fetch"
    )
    collect.add_argument(
        "--test", action="store_true",
        help="Dry run — print what would be logged without writing CSVs"
    )

    # summary subcommand
    summary = sub.add_parser("summary", help="Print summary of stored traffic data")
    summary.add_argument(
        "--top", type=int, default=12,
        help="Number of repos to show in monthly tables (default: 12)"
    )

    args = parser.parse_args()

    if args.command == "summary":
        token = os.environ.get("GITHUB_TOKEN")
        print_summary(token, top=args.top)
    elif args.command == "collect":
        token = get_token()
        fetch_and_collect(orgs=args.orgs, repos=args.repos, token=token, test=args.test)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
