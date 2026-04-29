# Installation

netbox-peering-manager is a NetBox plugin and follows the standard NetBox
plugin install flow. The only non-obvious step is that
[netbox-routing](https://github.com/DanSheps/netbox-routing) must already
be installed, enabled, and migrated before you enable this plugin: it
declares `netbox_routing` as a required plugin and will refuse to load
otherwise.

## Requirements

- NetBox 4.5.x (the plugin pins `min_version = "4.5.0"` and
  `max_version = "4.5.99"`).
- Python 3.12, 3.13, or 3.14.
- PostgreSQL (whatever NetBox itself supports).
- A running NetBox RQ worker if you plan to use IRR prefix-list sync jobs
  (`make rqworker` in the dev setup, or your production worker service).
- Optional: a running [fastbgpq4](https://github.com/jsenecal/fastbgpq4)
  instance if you plan to use IRR sync.
- Optional: a PeeringDB API key if you plan to read fields that PeeringDB
  gates behind authentication (contact info, etc.).

## Install netbox-routing first

```bash
source /opt/netbox/venv/bin/activate
pip install 'netbox-routing>=0.4'
```

Add it to `PLUGINS` in `configuration.py` and run migrations:

```python
PLUGINS = [
    "netbox_routing",
]
```

```bash
cd /opt/netbox/netbox
python manage.py migrate
```

Restart NetBox and confirm that the routing models show up in the UI under
the Routing menu before moving on.

## Install netbox-peering-manager

```bash
source /opt/netbox/venv/bin/activate
pip install netbox-peering-manager
```

Add the plugin to `PLUGINS` in `configuration.py`. Order matters:
`netbox_routing` must come first, because Django evaluates the `required_plugins`
declaration during app loading.

```python
PLUGINS = [
    "netbox_routing",
    "netbox_peering_manager",
]
```

Run the plugin migrations:

```bash
cd /opt/netbox/netbox
python manage.py migrate netbox_peering_manager
```

Restart NetBox (`systemctl restart netbox netbox-rq` on a typical install).
You should now see a top-level **Peering** menu in the navigation, with
sub-menus for Peering, Fabrics, and IRR.

## Pinning for production

Pin both plugins in your `local_requirements.txt` so upgrades are
deterministic:

```
netbox-routing==0.4.0
netbox-peering-manager==0.2.2
```

Re-run `pip install -r local_requirements.txt && python manage.py migrate`
after every NetBox or plugin upgrade.

## Verify the install

Open the NetBox shell and confirm the apps and the JobRunners are
registered:

```bash
cd /opt/netbox/netbox
python manage.py nbshell
```

```python
from django.apps import apps
apps.get_app_config("netbox_peering_manager")
# <BGPConfig: BGP>

from netbox_peering_manager.jobs import SyncPrefixListJob, SyncAllPrefixListsJob
SyncPrefixListJob.Meta.name
# 'Sync Prefix List from IRR'
```

If both lines work, the plugin is loaded correctly.

## Upgrading

The plugin is published to [PyPI](https://pypi.org/project/netbox-peering-manager/).
Standard upgrade flow:

```bash
source /opt/netbox/venv/bin/activate
pip install --upgrade netbox-peering-manager
cd /opt/netbox/netbox
python manage.py migrate netbox_peering_manager
systemctl restart netbox netbox-rq
```

If you are migrating from v0.1.x (NetBox 4.4) to v0.2.x (NetBox 4.5), see
the **Upgrading from v0.1.x** section in the project README. That migration
is destructive: it drops every `netbox_peering_manager_*` table and rebuilds
them, and assumes you have already migrated your BGP data into
netbox-routing.

## Next steps

- [Configure the plugin](configuration.md) (PeeringDB credentials, top-level
  menu, local ASNs).
- [Create your first peering fabric](first-fabric.md) and pull data from
  PeeringDB.
- [Create your first peering session](first-session.md) on top of a
  netbox-routing BGP peer.
