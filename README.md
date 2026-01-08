# Scripts

This repository stores Python scripts used by the Paton research group at Colorado State University.

[Paton Lab Homepage](https://patonlab.colostate.edu) | [GitHub Organization](https://github.com/patonlab)

## Contents

- **[check_acme.py](check_acme.py)** - Monitors ACME cluster internal nodes (node01-node20) by connecting through a head node and sends Slack alerts for down nodes
- **[check_machines.py](check_machines.py)** - Checks health status and CPU load of group Linux machines and sends periodic reports to Slack
- **[paton_pymol_style.py](paton_pymol_style.py)** - PyMOL visualization configuration with custom functions for ball-and-stick models, VDW surfaces, molecular orbitals, and spin density plots

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
