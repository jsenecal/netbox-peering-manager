# Configuration

The plugin is configured through the standard `PLUGINS_CONFIG` mechanism in
NetBox `configuration.py`. All settings are optional. Sensible defaults are
declared in the plugin's `PluginConfig.default_settings`.

## Settings reference

```python
PLUGINS_CONFIG = {
    "netbox_peering_manager": {
        "top_level_menu": True,
        "peeringdb_url": None,
        "peeringdb_api_key": None,
        "peeringdb_timeout": None,
        "peeringdb_local_asns": [],
    },
}
```

| Setting                 | Type            | Default                          | Description |
|-------------------------|-----------------|----------------------------------|-------------|
| `top_level_menu`        | bool            | `True`                           | When true, expose a dedicated "Peering" top-level menu with Peering / Fabrics / IRR groups. When false, links are flattened into the main plugins menu. |
| `peeringdb_url`         | str or None     | `None` (`https://www.peeringdb.com/api`) | Override the PeeringDB API base URL. Useful for local mirrors or paid private instances. |
| `peeringdb_api_key`     | str or None     | `None`                           | PeeringDB API key. Sent as `Authorization: Api-Key <value>`. Required only for fields that PeeringDB gates behind authentication (contact emails, some operational data). |
| `peeringdb_timeout`     | int or None     | `30`                             | HTTP timeout in seconds for PeeringDB requests. |
| `peeringdb_local_asns`  | list[int]       | `[]`                             | ASNs your organization owns. Listed ASNs are excluded from the cached `PeeringDBPeer` table during sync so you do not import yourself as a peer. |

The PeeringDB client also reads an undocumented `peeringdb_rate_limit` key
(seconds between requests, default 2.0) directly via `get_plugin_config`.
Set it explicitly if you operate a private PeeringDB mirror with looser
rate limits or, conversely, if you want to be a more conservative client.

## Recommended baseline

For a typical production install with PeeringDB and a single home ASN:

```python
PLUGINS_CONFIG = {
    "netbox_peering_manager": {
        "top_level_menu": True,
        "peeringdb_api_key": "PDB-XXXXXXXXXXXXXXXX",
        "peeringdb_timeout": 60,
        "peeringdb_local_asns": [64500],
    },
}
```

If you operate multiple ASNs (transit subsidiaries, an experimental ASN,
etc.) put all of them into `peeringdb_local_asns`. They will be filtered
out of every IX peer cache.

## Storing secrets

`peeringdb_api_key` is a secret. Read it from an environment variable or a
secrets manager rather than committing it to `configuration.py`:

```python
import os

PLUGINS_CONFIG = {
    "netbox_peering_manager": {
        "peeringdb_api_key": os.environ.get("PEERINGDB_API_KEY"),
    },
}
```

In Docker / Kubernetes deployments, mount the key as an environment variable
on the NetBox web container and the RQ worker container. The PeeringDB
client is constructed inside the request / job lifecycle, so both
processes need access to the key.

## Top-level menu vs. flattened menu

The plugin emits a `PluginMenu` with three groups:

- **Peering**: Peering Sessions, Peer ASNs, Relationship Types.
- **Fabrics**: Fabric Types, Fabrics, Create from PeeringDB, Networks,
  Connections.
- **IRR**: IRR Sources, IRR Prefix List Configs.

This is the layout used when `top_level_menu = True`. With
`top_level_menu = False`, the same items are emitted as a flat
`menu_items` tuple, which NetBox displays under the generic Plugins menu.
The flattened layout is fine for sandbox installs but the grouped layout
scales better once you have more than a handful of fabrics.

## RQ worker

IRR sync jobs (`SyncPrefixListJob`, `SyncAllPrefixListsJob`) are NetBox
`JobRunner` tasks. They run inside the standard NetBox RQ worker process.
Make sure that worker is running and has access to:

- The NetBox database (it writes `PrefixListEntry` rows back).
- Whatever fastbgpq4 endpoint you configured on each `IRRSource`.

In the bundled devcontainer / Makefile, the worker is started with
`make rqworker`. In production, make sure your `netbox-rq` systemd unit (or
equivalent) is running.

## Verifying configuration

```bash
cd /opt/netbox/netbox
python manage.py nbshell
```

```python
from django.conf import settings
settings.PLUGINS_CONFIG["netbox_peering_manager"]
# {'top_level_menu': True, 'peeringdb_url': None, 'peeringdb_api_key': '***', ...}

from netbox_peering_manager.services import PeeringDBClient
client = PeeringDBClient()
client.get_ix(31)  # 31 = LINX in PeeringDB
```

A successful response confirms that the API URL, timeout, and API key are
all wired up correctly. A 401 means your API key is wrong; a 429 means
rate limiting kicked in (the client backs off and retries automatically up
to three times).

## Next: bring up your first fabric

Once the plugin is configured, the next step is
[creating your first peering fabric](first-fabric.md) - either from
scratch or by importing one from PeeringDB.
