# netbox-peering-manager

[NetBox Peering Manager](https://github.com/jsenecal/netbox-peering-manager) is a BGP session management plugin for [NetBox](https://github.com/netbox-community/netbox). Meant as a way to document Internet Exchanges points and peering sessions, it also provides a source of truth and configuration management for external BGP sessions of all kind (transit, customers, peering, etc).

This project gets its name from the [original *Peering Manager* project](https://github.com/peering-manager/peering-manager), and most functionality is inspired by that project. I needed a tighter integration and the existing models within NetBox allowed to do much more rather than copy/pasting/api glueing information between the two tools (even though they both have a lot in common).

Currently the codebase is mostly a fork of the original [NetBox BGP Plugin](https://github.com/k01ek/netbox-bgp) by [Nikolay Yuzefovich](https://github.com/k01ek) but over time the two will diverge significantly as I work on the plugin.

## Features

This plugin provides the following Models:

**Core BGP Models:**
* BGP Sessions (with MD5 auth, BFD, multihop support)
* BGP Peer Groups
* Peer ASNs (extends NetBox ASN with peering-specific attributes)
* Relationship Types (transit, peer, customer, IXP)
* BFD Profiles

**Policy & Filtering:**
* Routing Policies (with weight and address family)
* BGP Communities (standard, extended, large)
* Community Lists
* Prefix Lists
* AS Path Lists

**Internet Exchange Support:**
* Peering Fabrics (IX, cloud exchange, private LAN)
* Peering Networks (IX LANs with prefix/VLAN)
* Peering Connections (device interface attachments)

**External Integrations:**
* PeeringDB selective sync
* IRR prefix list synchronization
* Configuration templating (Jinja2 with multi-vendor support)

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

## External Dependencies

### IRR Prefix List Synchronization (fastbgpq4)

The plugin supports automatic prefix list synchronization from Internet Routing Registry (IRR) databases. This feature requires [fastbgpq4](https://github.com/jsenecal/fastbgpq4), a separate REST API service that wraps [bgpq4](https://github.com/bgp/bgpq4) for querying IRR databases like RADB, RIPE, ARIN, etc.

**Why a separate service?**

bgpq4 is a command-line tool, not a library. fastbgpq4 provides a REST API interface that allows netbox-peering-manager to query IRR data without requiring bgpq4 to be installed on the NetBox server itself. This also enables caching, async queries for large AS-SETs, and centralized IRR query infrastructure.

**Setup:**

1. Deploy fastbgpq4 (see [fastbgpq4 documentation](https://github.com/jsenecal/fastbgpq4) for installation options including Docker)

2. In NetBox, create an IRR Source under *Peering Manager > IRR Sources* with:
   - **Name**: A descriptive name (e.g., "RADB via fastbgpq4")
   - **URL**: The fastbgpq4 API base URL (e.g., `http://fastbgpq4:8000`)
   - **Sources** (optional): Comma-separated IRR sources to query (e.g., `RADB,RIPE,ARIN`)
   - **Cache TTL** (optional): Cache duration for query results

3. On your PeerASN records, set the **IRR AS-SET** field (e.g., `AS-HURRICANE`, `AS15169:AS-GOOGLE`)

4. Create Prefix Lists with:
   - **IRR Source**: Select your configured IRR source
   - **Source AS-SET**: The AS-SET to query (e.g., `AS-HURRICANE`)
   - **Family**: IPv4 or IPv6

5. Use the sync action on Prefix Lists to populate them from IRR data

**Background Jobs:**

IRR synchronization runs as NetBox background jobs via the RQ worker:
- **Sync Prefix List from IRR** - Syncs a single prefix list
- **Sync All Prefix Lists from IRR** - Syncs all prefix lists associated with an IRR source

Ensure the NetBox RQ worker is running (`make rqworker` in development, or your production worker service).

**API Endpoint:**

The plugin queries fastbgpq4 at `GET /api/v1/as-set/expand` with parameters:
- `target`: The AS-SET to expand
- `format`: Response format (json)
- `sources`: IRR sources to query
- `cache_ttl`: Cache duration

For large AS-SETs, fastbgpq4 returns a 202 status with a job ID, and the plugin polls for completion.

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
