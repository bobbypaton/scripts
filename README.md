# Scripts

This repository stores Python scripts used by the Paton research group at Colorado State University.

[Paton Lab Homepage](https://patonlab.colostate.edu) | [GitHub Organization](https://github.com/patonlab)

## Contents

- **[check_acme.py](check_acme.py)** - Monitors ACME cluster internal nodes (node01-node20) by connecting through a head node and sends Slack alerts for down nodes
- **[check_machines.py](check_machines.py)** - Checks health status and CPU load of group Linux machines and sends periodic reports to Slack
- **[paton_pymol_style.py](paton_pymol_style.py)** - PyMOL visualization configuration with custom functions for ball-and-stick models, VDW surfaces, molecular orbitals, and spin density plots
- **[metrics/hf_spaces_analytics.py](metrics/hf_spaces_analytics.py)** - HF Spaces analytics: fetches space metadata (likes, SDK, status) and tracks visits to a private HF Dataset repo
- **[metrics/gh_traffic.py](metrics/gh_traffic.py)** - GitHub traffic logger: collects views and clones to local CSVs (run weekly via cron)
- **[metrics/weekly_report.py](metrics/weekly_report.py)** - Combines all metrics and posts a weekly summary to Slack

## Requirements

- Python 3.7+
- SSH key-based authentication set up for ACME head node (for `check_acme.py`)
- Password-based SSH access to monitored machines (for `check_machines.py`)

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Environment Variables

Create a `.env` file with the following variables:

- `SLACK_WEBHOOK_ACME` - Slack webhook URL for ACME node alerts
- `SLACK_WEBHOOK_UNIX` - Slack webhook URL for machine health reports
- `SLACK_WEBHOOK_METRICS` - Slack webhook URL for weekly metrics report
- `HEAD_NODE_IP` - IP address of the ACME head node
- `HEAD_NODE_USER` - SSH username for ACME head node
- `SSH_USER` - Default SSH username for machine checks
- `SSH_PASSWORD` - SSH password for machine authentication
- `MACHINES` - Comma-separated list of machine hostnames to monitor
- `SSH_USERS_MAP` - Optional per-host SSH username overrides (`host:user` pairs, comma-separated)
- `HF_TOKEN` - Hugging Face API token with write access (for `hf_spaces_analytics.py`)
- `HUGGINGFACE_TOKEN` - Hugging Face API token (for `hf_spaces_analytics.py`, optional)
- `GITHUB_TOKEN` - GitHub personal access token with `repo` scope (for `gh_traffic.py`)

## Usage

### check_acme.py

Monitors ACME cluster nodes by connecting through a head node (configured via `HEAD_NODE_IP` env var).

```bash
# Run check and send alerts to Slack
python check_acme.py

# Test mode (print to stdout instead of Slack)
python check_acme.py --test
```

**Features:**
- Checks 20 internal nodes (node01-node20) via SSH jump through head node
- Parallel checking with configurable thread pool
- Automatic retry for failed ping attempts
- Sends Slack alerts with list of down nodes

### check_machines.py

Monitors health and load of group Linux machines.

```bash
# Run check and send report to Slack
python check_machines.py

# Test mode (print to stdout instead of Slack)
python check_machines.py --test
```

**Monitored machines** are configured via the `MACHINES` environment variable (comma-separated hostnames).

**Features:**
- Ping connectivity checks (with retry for wake-on-LAN hosts)
- SSH-based load average monitoring
- Status indicators (🟢 healthy, 🟡 high load, 🔴 offline)
- Custom username mapping for specific hosts

### metrics/hf_spaces_analytics.py

HF Spaces analytics and visit tracking in one script.

```bash
# Fetch space metadata (likes, SDK, status) for default authors
python metrics/hf_spaces_analytics.py spaces

# Custom authors / token
python metrics/hf_spaces_analytics.py spaces --authors patonlab bobbypaton --token hf_xxx

# Print visit count summary from analytics repo
python metrics/hf_spaces_analytics.py visits
```

To track visits from inside a Space, import and call `log_visit()` at app startup. See the file for Gradio-specific examples. Requires `HF_TOKEN` set as a Space secret.

### metrics/gh_traffic.py

Collects GitHub traffic stats (views, clones) and stores them in local CSVs. GitHub only retains 14 days of traffic data, so run this weekly via cron.

```bash
# Collect traffic for all patonlab repos
python metrics/gh_traffic.py collect

# Collect for specific orgs or repos
python metrics/gh_traffic.py collect --orgs patonlab bobbypaton
python metrics/gh_traffic.py collect --repos patonlab/aqme patonlab/goodvibes

# Dry run (print without writing)
python metrics/gh_traffic.py collect --test

# View summary of stored data (overview + monthly breakdown)
python metrics/gh_traffic.py summary

# Show top 20 repos in monthly tables (default: 12)
python metrics/gh_traffic.py summary --top 20
```

Requires `GITHUB_TOKEN` with `repo` scope. Data is saved to `metrics/data/` (gitignored).

### metrics/weekly_report.py

Runs all metrics collection and posts a combined summary to Slack.

```bash
# Post to Slack
python metrics/weekly_report.py

# Print to stdout instead
python metrics/weekly_report.py --test
```

Requires `SLACK_WEBHOOK_METRICS`. Scheduled weekly via launchd (Monday 8am) — see `~/Library/LaunchAgents/com.patonlab.weekly-report.plist`.

### paton_pymol_style.py

PyMOL configuration script for publication-quality molecular visualizations.

**Setup:**
Load this script in PyMOL or add to your `.pymolrc` file:
```bash
# In PyMOL
run /path/to/paton_pymol_style.py

# Or add to ~/.pymolrc
run ~/path/to/paton_pymol_style.py
```

**Available commands:**
- `ballnstick <selection>` - Create ball-and-stick representation with custom colors
- `Add_VDW <selection>` - Add transparent van der Waals surface
- `Add_homo <name>` - Visualize HOMO from cube file
- `Add_lumo <name>` - Visualize LUMO from cube file
- `Add_spin <name>` - Visualize spin density from cube file
- `spin_density_plot <name> <isovalue>` - Custom spin density with adjustable isovalue
- `nci <name> <min> <max>` - Visualize non-covalent interactions

**Features:**
- Bondi van der Waals radii for all elements
- High-quality rendering settings optimized for publication
- CMYK color space for print compatibility
- Customizable molecular orbital and density visualizations

## Contributing

Group members are welcome to add new scripts. Please:
1. Add appropriate documentation and usage examples
2. Update the README with script descriptions
3. Include any new dependencies in `requirements.txt`
4. Use environment variables for sensitive configuration

## License

Internal use by the Paton research group at Colorado State University.
