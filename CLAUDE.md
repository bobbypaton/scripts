# CLAUDE.md

## Project Overview

Paton Lab research group utility scripts for monitoring computational infrastructure, molecular visualization, and usage metrics.

## Repository Structure

```
check_acme.py                    # ACME cluster node monitoring (SSH jump through head node)
check_machines.py                # Group Linux machine health/CPU load monitoring
paton_pymol_style.py             # PyMOL publication-quality visualization config
metrics/
  hf_spaces_analytics.py         # HF Spaces analytics + visit tracking
  gh_traffic.py                  # GitHub traffic collection (views, clones)
  weekly_report.py               # Weekly Slack report (cron-scheduled)
  data/                          # Collected CSV data (gitignored)
.env                             # Credentials and config (gitignored)
.env.example                     # Template for .env setup
requirements.txt                 # paramiko >= 3.0.0, requests >= 2.31.0
```

## Development Conventions

- **Python 3.7+** compatibility — no type hints
- Shebang: `#!/usr/bin/env python` on executable scripts
- Import order: standard library first, then external packages
- Custom `.env` loading (no external dotenv package) — implemented inline in each script
- Configuration constants at the top of each file
- All credentials and hostnames live in `.env`, never hardcoded

## Running Scripts

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in environment config
cp .env.example .env

# Test mode (prints to stdout instead of Slack)
python check_machines.py --test
python check_acme.py --test
python metrics/weekly_report.py --test
```

## Key Patterns

- **Slack integration**: Monitoring and metrics scripts post formatted messages via webhook URLs
- **SSH**: Password-based auth via paramiko; check_acme uses SSH jumping through a head node, check_machines connects directly
- **Error handling**: Try-except with specific exception types (paramiko, requests); scripts continue processing on individual failures
- **Parallelism**: check_acme uses `ThreadPoolExecutor` (5 workers); check_machines runs sequentially
- **Metrics**: GitHub traffic collected to local CSVs (deduplicated on overlap); HF visit tracking via private dataset repo; weekly Slack reports via cron
