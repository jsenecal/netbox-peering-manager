# netbox-peering-manager

> A peering management plugin for [NetBox](https://github.com/netbox-community/netbox): IX points, peering sessions, IRR prefix list synchronization. Source of truth and configuration management layer for external BGP sessions (transit, customers, peering).

[![PyPI](https://img.shields.io/pypi/v/netbox-peering-manager.svg)](https://pypi.org/project/netbox-peering-manager/)
[![Python](https://img.shields.io/pypi/pyversions/netbox-peering-manager.svg)](https://pypi.org/project/netbox-peering-manager/)
[![NetBox](https://img.shields.io/badge/NetBox-plugin-success.svg)](https://github.com/jsenecal/netbox-peering-manager#compatibility)
[![CI](https://github.com/jsenecal/netbox-peering-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/jsenecal/netbox-peering-manager/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/jsenecal/netbox-peering-manager/branch/main/graph/badge.svg)](https://codecov.io/gh/jsenecal/netbox-peering-manager)
[![Documentation](https://img.shields.io/badge/docs-jsenecal.github.io-blue)](https://jsenecal.github.io/netbox-peering-manager/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Starting with v0.2.0, this plugin builds on top of [netbox-routing](https://github.com/DanSheps/netbox-routing), which provides the core BGP data models (peers, peer groups, routing policies, prefix lists, communities, BFD profiles, etc). netbox-peering-manager extends those models with peering-specific functionality rather than duplicating them.

## Compatibility

| Plugin version | NetBox version | netbox-routing        | Python    |
|----------------|----------------|-----------------------|-----------|
| 0.4.x          | 4.6-4.7        | 0.4.3+                | 3.12-3.14 |
| 0.3.x          | 4.5-4.7        | 0.4.2+                | 3.12-3.14 |
| 0.2.x          | 4.5            | 0.4.x                 | 3.12-3.14 |
| 0.1.x          | 4.4            | not used (standalone) | 3.10+     |

- NetBox 4.7 needs plugin 0.3.1 or later, which in turn needs netbox-routing 0.4.3 or later.
- On NetBox 4.5, stay on netbox-routing 0.4.x. netbox-routing 0.5 does not migrate there.

## Features

This plugin provides the following on top of netbox-routing:

**Peering Session Management:**
* Peering Sessions — thin wrapper around netbox-routing's BGPPeer, adding relationship type, peering network association, and service reference tracking
* Relationship Types — classify sessions as transit, peer, customer, IXP, etc.
* Peer ASNs — extends NetBox ASN with peering-specific attributes (IRR AS-SET, max prefixes, PeeringDB ID)

**Internet Exchange Support:**
* Peering Fabric Types — classify fabric types (IX, cloud exchange, private LAN)
* Peering Fabrics — represent IX or peering environments with PeeringDB integration
* Peering Networks — IX LANs with prefix/VLAN associations
* Peering Connections — device interface attachments to peering networks

**IRR Prefix List Synchronization:**
* IRR Sources — configure IRR query endpoints (via [fastbgpq4](https://github.com/jsenecal/fastbgpq4))
* IRR Prefix List Configs — link netbox-routing PrefixLists to IRR sources for automatic sync
* Background jobs for single and bulk prefix list synchronization

**External Integrations:**
* PeeringDB selective sync (IX discovery, peer discovery)
* Configuration templating (Jinja2 with multi-vendor support via NetBox ConfigTemplates)

**Provided by netbox-routing (required dependency):**
* BGP Peers and Peer Templates (peer groups)
* BGP Routers and Scopes
* Routing Policies (route maps) with address family support
* Prefix Lists and Prefix List Entries
* Communities and Community Lists
* AS Path Lists
* BFD Profiles

## Installation

netbox-peering-manager requires [netbox-routing](https://github.com/DanSheps/netbox-routing) and will not load without it. Installing the plugin from PyPI pulls it in:

```bash
pip install netbox-peering-manager
```

Enable both plugins in your NetBox `configuration.py`. `netbox_routing` must come first:

```python
PLUGINS = [
    'netbox_routing',
    'netbox_peering_manager',
]
```

Run the migrations and restart NetBox:

```bash
cd /opt/netbox/netbox
python manage.py migrate
```

The [installation guide](https://jsenecal.github.io/netbox-peering-manager/getting-started/installation/) covers the full sequence, including pinning versions and verifying the install.

## Configuration

```python
PLUGINS_CONFIG = {
    'netbox_peering_manager': {
        # Enable top-level navigation menu (default: True)
        'top_level_menu': True,

        # PeeringDB integration (all optional)
        'peeringdb_url': None,           # Falls back to default PeeringDB API
        'peeringdb_api_key': None,       # Optional, needed for contact info
        'peeringdb_timeout': None,       # Falls back to 30s
        'peeringdb_local_asns': [],      # Your ASN(s) for filtering
    }
}
```

## Model Architecture

netbox-routing provides the core BGP models (peers, peer templates, prefix lists, route maps, BFD profiles) and this plugin adds peering-specific extension models on top: `PeeringSession` extends a `BGPPeer`, `PeerASN` extends an `ipam.ASN`, and `IRRPrefixListConfig` extends a `PrefixList`. Fabrics, networks, and connections model the IX infrastructure.

See [Architecture](https://jsenecal.github.io/netbox-peering-manager/concepts/architecture/) for the model graph and [Models](https://jsenecal.github.io/netbox-peering-manager/concepts/models/) for every field.

## External Dependencies

### IRR Prefix List Synchronization (fastbgpq4)

The plugin can populate netbox-routing prefix lists from Internet Routing Registry (IRR) databases. This feature requires [fastbgpq4](https://github.com/jsenecal/fastbgpq4), a separate REST API service that wraps [bgpq4](https://github.com/bgp/bgpq4), and a running NetBox RQ worker (`make rqworker` in development, or your production worker service).

- [IRR prefix lists](https://jsenecal.github.io/netbox-peering-manager/user-guide/irr-prefix-lists/) - setup and sync workflow
- [IRR / fastbgpq4 integration](https://jsenecal.github.io/netbox-peering-manager/integrations/irr/) - why a separate service, and the API contract

## Configuration Templating

netbox-peering-manager provides a configuration rendering service that builds Jinja2 template context from your BGP data. It uses NetBox's built-in `ConfigTemplate` model for template storage.

The template context, the rendering workflow, and the custom Jinja2 filters are documented on the docs site:

- [Configuration templating](https://jsenecal.github.io/netbox-peering-manager/user-guide/configuration-templating/) - context variables and session fields
- [Jinja2 filters](https://jsenecal.github.io/netbox-peering-manager/reference/jinja2-filters/) - `as_path_regex`, `ip_network`, `group_by`, `to_community_list`, `to_prefix_set`

### Example Templates

Example templates are provided in [`docs/examples/templates/`](docs/examples/templates/) for:
- **Juniper Junos** (`junos-bgp.j2`)
- **Cisco IOS-XR** (`ios-xr-bgp.j2`)
- **Arista EOS** (`eos-bgp.j2`)
- **Nokia SR OS** (`nokia-sros-bgp.j2`)

### API Endpoint

Render configuration via the REST API:

```
POST /api/plugins/bgp/render-config/
```

## Development

This plugin uses a VS Code devcontainer for development. The devcontainer provides a complete NetBox environment with both netbox-routing and netbox-peering-manager installed in editable mode.

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

Both netbox-routing and netbox-peering-manager are installed in editable mode (`pip install -e`), so changes to the code will be reflected immediately. You may need to restart the NetBox service for some changes.

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

## Upgrading from v0.1.x

v0.2.0 is a **breaking change**. All BGP routing models (BGPSession, BGPPeerGroup, BFD, RoutingPolicy, PrefixList, Community, ASPathList, and their rule models) have been removed in favor of netbox-routing.

**Migration steps:**

1. Install netbox-routing and run its migrations
2. Migrate your data from the old plugin tables to netbox-routing models (manual process — see below)
3. Update `PLUGINS` configuration to include both `netbox_routing` and `netbox_peering_manager`
4. Clear old migration state and drop **all** plugin tables (they will be recreated by the new migration):

   ```sql
   -- Connect to your NetBox database and run:

   -- Remove old migration records
   DELETE FROM django_migrations WHERE app = 'netbox_peering_manager';

   -- Drop ALL plugin tables — the new migration recreates the ones it needs
   DO $$
   DECLARE
       r RECORD;
   BEGIN
       FOR r IN
           SELECT tablename FROM pg_tables
           WHERE tablename LIKE 'netbox_peering_manager_%'
       LOOP
           EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
       END LOOP;
   END $$;
   ```

5. Upgrade netbox-peering-manager to v0.2.0 and run migrations:

   ```bash
   cd /opt/netbox/netbox
   python manage.py migrate netbox_peering_manager
   ```

6. Update any configuration templates to use the new context variables (see [Configuration Templating](#configuration-templating))
