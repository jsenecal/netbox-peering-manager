# netbox-peering-manager

> A peering management plugin for [NetBox](https://github.com/netbox-community/netbox): IX points, peering sessions, IRR prefix list synchronization. Source of truth and configuration management layer for external BGP sessions (transit, customers, peering).

[![PyPI](https://img.shields.io/pypi/v/netbox-peering-manager.svg)](https://pypi.org/project/netbox-peering-manager/)
[![Python](https://img.shields.io/pypi/pyversions/netbox-peering-manager.svg)](https://pypi.org/project/netbox-peering-manager/)
[![NetBox](https://img.shields.io/badge/NetBox-4.5%2B-success.svg)](https://github.com/netbox-community/netbox)
[![CI](https://github.com/jsenecal/netbox-peering-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/jsenecal/netbox-peering-manager/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/jsenecal/netbox-peering-manager/branch/main/graph/badge.svg)](https://codecov.io/gh/jsenecal/netbox-peering-manager)
[![Documentation](https://img.shields.io/badge/docs-jsenecal.github.io-blue)](https://jsenecal.github.io/netbox-peering-manager/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Starting with v0.2.0, this plugin builds on top of [netbox-routing](https://github.com/DanSheps/netbox-routing), which provides the core BGP data models (peers, peer groups, routing policies, prefix lists, communities, BFD profiles, etc). netbox-peering-manager extends those models with peering-specific functionality rather than duplicating them.

## Compatibility

| Plugin version | NetBox version | Python    |
|----------------|----------------|-----------|
| 0.2.x          | 4.5            | 3.12-3.14 |

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

## Compatibility

| NetBox Version | Plugin Version | netbox-routing Version |
|----------------|----------------|------------------------|
| NetBox 4.5.x   | >= 0.2.0       | 0.4.x+                |
| NetBox 4.4.x   | 0.1.x          | N/A (standalone)       |

## Prerequisites

**netbox-routing** must be installed and enabled before installing netbox-peering-manager. The plugin declares `netbox_routing` as a required plugin and will not load without it.

```bash
pip install git+https://github.com/DanSheps/netbox-routing.git@14318f1c
```

Enable it in your NetBox configuration:

```python
PLUGINS = [
    'netbox_routing',
    'netbox_peering_manager',
]
```

> **Important:** `netbox_routing` must appear before `netbox_peering_manager` in the `PLUGINS` list.

## Installation

Install the plugin (this will also pull in netbox-routing as a dependency):

```bash
pip install git+https://github.com/jsenecal/netbox-peering-manager.git
```

Enable both plugins in `/opt/netbox/netbox/netbox/configuration.py`:

```python
PLUGINS = [
    'netbox_routing',
    'netbox_peering_manager',
]
```

Run database migrations:

```bash
cd /opt/netbox/netbox
python manage.py migrate
```

Restart NetBox and add `netbox-peering-manager` to your `local_requirements.txt`.

See [NetBox Documentation](https://docs.netbox.dev/en/stable/plugins/#installing-plugins) for details.

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

netbox-peering-manager v0.2.0 follows a layered architecture where netbox-routing provides the core BGP models and this plugin adds peering-specific extensions:

```
netbox-routing (dependency)          netbox-peering-manager (this plugin)
─────────────────────────────        ────────────────────────────────────
BGPPeer ◄──────────────────────────── PeeringSession (1:1)
  ├── peer (remote IP)                 ├── relationship (FK → Relationship)
  ├── source (local IP)                ├── peering_network (FK → PeeringNetwork)
  ├── remote_as / local_as             └── service_reference
  ├── peer_group (BGPPeerTemplate)
  ├── bfd (BFDProfile)               Relationship
  ├── address_families[]               ├── name, slug, color
  └── enabled, status, ttl
                                     PeerASN (1:1 → ipam.ASN)
PrefixList ◄─────────────────────────  ├── affiliated, irr_as_set
  ├── name, family                     ├── max prefixes (v4/v6)
  └── entries[]                        └── peeringdb_id

                                     IRRPrefixListConfig (1:1 → PrefixList)
                                       ├── irr_source (FK → IRRSource)
                                       ├── source_as_set
                                       └── sync_interval

                                     IRRSource
                                       ├── name, url, sources
                                       └── enabled, sync_interval

                                     PeeringFabric / PeeringNetwork / PeeringConnection
                                       └── IX infrastructure models
```

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

3. Create an IRR Prefix List Config linking a netbox-routing Prefix List to the IRR Source:
   - **Prefix List**: Select a netbox-routing prefix list
   - **IRR Source**: Select your configured IRR source
   - **Source AS-SET**: The AS-SET to query (e.g., `AS-HURRICANE`)

4. Use the sync action to populate the prefix list entries from IRR data

**Background Jobs:**

IRR synchronization runs as NetBox background jobs via the RQ worker:
- **Sync Prefix List from IRR** — Syncs a single prefix list
- **Sync All Prefix Lists from IRR** — Syncs all prefix lists associated with an IRR source

Ensure the NetBox RQ worker is running (`make rqworker` in development, or your production worker service).

## Configuration Templating

netbox-peering-manager provides a configuration rendering service that builds Jinja2 template context from your BGP data. It uses NetBox's built-in `ConfigTemplate` model for template storage.

### Template Context Variables

The `ConfigRenderer` service provides the following context:

| Variable | Type | Description |
|----------|------|-------------|
| `device` | dict | Device info: `name`, `platform.name`, `platform.slug`, `site.name`, `site.slug` |
| `sessions` | list[dict] | Peering sessions (see below) |
| `peer_groups` | list[dict] | Deduplicated peer groups: `id`, `name` |
| `route_maps` | list[dict] | Deduplicated route maps: `id`, `name` |
| `prefix_lists` | list[dict] | Reserved for future use |
| `communities` | list[dict] | Reserved for future use |

### Session Context

Each session in `sessions` contains:

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | BGP peer name |
| `description` | str | Peer description |
| `enabled` | bool | Whether the peer is enabled |
| `status` | str | Peer status |
| `local_asn` | int | Local AS number |
| `peer_asn` | int | Remote AS number |
| `local_ip` | str | Local IP address |
| `remote_ip` | str | Remote IP address |
| `password` | str | MD5 authentication password |
| `ttl` | int | TTL / multihop value |
| `relationship` | str | Relationship type name |
| `service_reference` | str | Service ticket reference |
| `peer_name` | str | PeerASN name (if exists) |
| `irr_as_set` | str | IRR AS-SET from PeerASN |
| `ipv4_max_prefixes` | int | Max IPv4 prefixes from PeerASN |
| `ipv6_max_prefixes` | int | Max IPv6 prefixes from PeerASN |
| `bfd_profile` | dict | BFD config: `name`, `minimum_interval`, `minimum_rx_interval`, `multiplier`, `hold` |
| `peer_group` | dict | Peer group: `id`, `name` |
| `peering_network` | dict | IX network: `id`, `name`, `fabric` |
| `afi_safis` | list[str] | Address families (e.g., `["ipv4-unicast"]`) |
| `address_families` | list[dict] | Per-AFI config with `route_map_in`, `route_map_out`, `prefix_list_in`, `prefix_list_out` |

### Custom Jinja2 Filters

The plugin registers custom Jinja2 filters for use in templates:

| Filter | Description |
|--------|-------------|
| `as_path_regex` | Convert AS path to regex pattern |
| `ip_network` | Parse IP network string |
| `group_by` | Group objects by attribute |
| `to_community_list` | Format community list entries |
| `to_prefix_set` | Format prefix set entries |

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
