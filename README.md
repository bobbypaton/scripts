# Scripts

This repository stores Python scripts used by the Paton research group at Colorado State University.

[Paton Lab Homepage](https://patonlab.colostate.edu) | [GitHub Organization](https://github.com/patonlab)

## Contents

- **[check_acme.py](check_acme.py)** - Monitors ACME cluster internal nodes (node01-node20) by connecting through a head node and sends Slack alerts for down nodes
- **[check_machines.py](check_machines.py)** - Checks health status and CPU load of group Linux machines and sends periodic reports to Slack

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
- `HEAD_NODE_USER` - SSH username for ACME head node (default: rpaton)
- `SSH_USER` - Default SSH username for machine checks (default: rpaton)
- `SSH_PASSWORD` - SSH password for machine authentication

## Usage

### check_acme.py

Monitors ACME cluster nodes by connecting through the head node at 129.82.77.43.

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

**Monitored machines:**
- acme.chem.colostate.edu
- dynamo.chem.colostate.edu
- buzzsaw.chem.colostate.edu
- skymarshal.chem.colostate.edu
- drstrange.chem.colostate.edu
- droctavius.chem.colostate.edu
- drmaximus.chem.colostate.edu
- fireball.chem.colostate.edu
- subzero.chem.colostate.edu

**Features:**
- Ping connectivity checks
- SSH-based load average monitoring
- Status indicators (🟢 healthy, 🟡 high load, 🔴 offline)
- Custom username mapping for specific hosts

## Contributing

Group members are welcome to add new scripts. Please:
1. Add appropriate documentation and usage examples
2. Update the README with script descriptions
3. Include any new dependencies in `requirements.txt`
4. Use environment variables for sensitive configuration

## License

Internal use by the Paton research group at Colorado State University.
