# netbox-peering-manager

[NetBox Peering Manager](https://github.com/jsenecal/netbox-peering-manager) is a BGP session management plugin for [NetBox](https://github.com/netbox-community/netbox). Meant as a way to document Internet Exchanges points and peering sessions, it also provides a source of truth and configuration management for external BGP sessions of all kind (transit, customers, peering, etc).

This project gets its name from the [original *Peering Manager* project](https://github.com/peering-manager/peering-manager), and most functionality is inspired by that project. I needed a tighter integration and the existing models within NetBox allowed to do much more rather than copy/pasting/api glueing information between the two tools (even though they both have a lot in common).

Currently the codebase is mostly a fork of the original [NetBox BGP Plugin](https://github.com/k01ek/netbox-bgp) by [Nikolay Yuzefovich](https://github.com/k01ek) but over time the two will diverge significantly as I work on the plugin.

## Features

This plugin provides the following Models:
* BGP Sessions
* BGP Peer Groups
* BGP Communities
* Routing Policies
* Prefix Lists
* AS Path Lists
* Relationship Types (transit, peer, customer, etc.)
* BFD Profiles

## Compatibility

| NetBox Version | Plugin Version |
|----------------|----------------|
| NetBox 4.4.x   | >= 0.0.1       |

## Installation

The plugin can be installed with pip:

```bash
pip install git+https://github.com/jsenecal/netbox-peering-manager.git
```

Enable the plugin in /opt/netbox/netbox/netbox/configuration.py:
```python
PLUGINS = ['netbox_peering_manager']
```

Restart NetBox and add `netbox-peering-manager` to your local_requirements.txt

See [NetBox Documentation](https://docs.netbox.dev/en/stable/plugins/#installing-plugins) for details

## Configuration

The following options are available:
* `device_ext_page`: String (default right) Device related BGP sessions display mode. The following values are available:
  - `left`: Display BGP sessions in the left column of the device detail page
  - `right`: Display BGP sessions in the right column of the device detail page
  - `full_width`: Display BGP sessions in full width at the bottom of the device detail page
  - `tab`: Display BGP sessions in a dedicated tab on the device detail page
  - Set empty value to disable device BGP sessions display
* `top_level_menu`: Bool (default False) Enable top level section navigation menu for the plugin.

## Development

This plugin uses a VS Code devcontainer for development. The devcontainer provides a complete NetBox environment with the plugin installed in editable mode.

### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/jsenecal/netbox-peering-manager.git
   cd netbox-peering-manager
   ```

2. Open the project in VS Code:
   ```bash
   code .
   ```

3. When prompted, click "Reopen in Container" or run the command "Dev Containers: Reopen in Container" from the Command Palette (F1)

4. Wait for the container to build and start. This may take a few minutes on the first run.

5. Once the container is ready, NetBox will be accessible at `http://localhost:8001`
   - Username: `admin`
   - Password: `admin`

### Development Workflow

The plugin is installed in editable mode (`pip install -e`), so changes to the code will be reflected immediately. You may need to restart the NetBox service for some changes.

#### Using Make Commands

The project includes a Makefile with convenient targets for common development tasks:

```bash
# Show all available make targets with descriptions
make help

# Quick Start / Composite Commands
make all              # Full setup: install, migrate, collect static, load demo data
make rebuild          # Rebuild: reinstall plugin, run migrations, collect static
make setup            # Install/reinstall the plugin in editable mode

# Development Server & Shells
make runserver        # Start NetBox development server on port 8001
make shell            # Open Django shell
make nbshell          # Open NetBox shell (with NetBox utilities)
make dbshell          # Open database shell

# Database Migrations
make makemigrations   # Create new migrations for the plugin
make migrate          # Apply database migrations
make showmigrations   # Show migration status

# Testing & Code Quality
make test             # Run plugin tests (includes migration check)
make test-verbose     # Run tests with verbose output
make lint             # Run ruff linting checks
make format           # Auto-format code with ruff
make fix              # Run ruff with --fix for auto-fixes

# NetBox Utilities
make trace_paths      # Run NetBox trace_paths utility
make collectstatic    # Collect static files
make createsuperuser  # Create a superuser account
make rqworker         # Start RQ worker for background tasks

# Demo Data (NetBox Initializers)
make initializers            # Setup and load demo data
make example_initializers    # Copy example initializers to .devcontainer
make load_initializers       # Load initializer data from .devcontainer/initializers

# Maintenance
make clean            # Clean build artifacts
make reinstall        # Alias for setup
```

#### Manual Commands

You can also run Django management commands directly:

```bash
# From within the devcontainer terminal
cd /opt/netbox/netbox
python manage.py runserver 0.0.0.0:8001
python manage.py test netbox_peering_manager
python manage.py makemigrations netbox_peering_manager
python manage.py migrate
```

## Screenshots

BGP Session
![BGP Session](docs/img/session.png)

BGP Sessions
![BGP Session Table](docs/img/sessions.png)

Community
![Community](docs/img/commun.png)

Peer Group
![Peer Group](docs/img/peer_group.png)

Routing Policy
![Routing Policy](docs/img/routepolicy.png)

Prefix List
![Prefix List](docs/img/preflist.png)
