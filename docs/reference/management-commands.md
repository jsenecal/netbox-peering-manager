# Management commands

The plugin adds two `manage.py` commands. Run them from the NetBox
directory with the NetBox virtual environment active:

```bash
source /opt/netbox/venv/bin/activate
cd /opt/netbox/netbox
python manage.py <command>
```

## sync_peeringdb

Synchronizes linked fabrics from PeeringDB. It performs the same sync as
the **Sync from PeeringDB** button; what that sync changes is described in
[PeeringDB sync](../user-guide/peeringdb-sync.md#what-a-sync-changes).

```
python manage.py sync_peeringdb [--fabric PK] [--ix-id ID] [--discover-only]
```

| Option | Effect |
|--------|--------|
| (none) | Sync every fabric that has a PeeringDB link. |
| `--fabric PK` | Sync one fabric, selected by its NetBox ID. |
| `--ix-id ID` | Sync the fabric linked to this PeeringDB IX ID. |
| `--discover-only` | Refresh only the peer cache. Fabric metadata and networks are left untouched. Combines with any of the above. |

When both `--ix-id` and `--fabric` are given, `--ix-id` wins.

`--ix-id` selects an existing link. It does not create a fabric or a
link; do that first, as described in
[PeeringDB sync](../user-guide/peeringdb-sync.md#linking-a-fabric).

### Output

One block per fabric:

```
Syncing LINX LON1...
  Synced: 0 networks created, 2 updated, 871 peers
```

or, when the sync reported problems:

```
Syncing LINX LON1...
  Errors: PeeringDB API error syncing peers: ...
```

### Exit status

| Situation | Exit status |
|-----------|-------------|
| Sync completed, with or without reported errors | 0 |
| No fabric has a PeeringDB link | 0, with a warning |
| `--fabric` names a fabric that does not exist or is not linked | Non-zero |
| `--ix-id` matches no linked fabric | Non-zero |

A failed sync of one fabric is printed but does not change the exit
status and does not stop the remaining fabrics. If you schedule the
command, alert on the word `Errors` in its output rather than on the exit
status.

### Scheduling

```
# /etc/cron.d/netbox-peeringdb
15 3 * * *  netbox  cd /opt/netbox/netbox && /opt/netbox/venv/bin/python manage.py sync_peeringdb
0  * * * *  netbox  cd /opt/netbox/netbox && /opt/netbox/venv/bin/python manage.py sync_peeringdb --discover-only
```

This runs a full sync nightly and refreshes peer caches hourly. Requests
are paced to respect PeeringDB rate limits, so a run over many fabrics
takes a while; that is expected.

## load_all_initializer_data

Loads seed data from YAML files. It is only usable when the
[netbox-initializers](https://github.com/tobiasge/netbox-initializers)
plugin is installed, and is mainly used to populate development and demo
environments.

```
python manage.py load_all_initializer_data --path /path/to/initializers
```

It first runs the stock netbox-initializers loader for core NetBox
objects, then runs the initializers registered by plugins, which the stock
command skips.

The plugin ships one initializer:

| File in `--path` | Creates |
|------------------|---------|
| `peering_manager_relationships.yml` | Relationship types |

```yaml
# peering_manager_relationships.yml
- name: Transit
  slug: transit
  description: Upstream transit provider
  color: aa1409

- name: Peer
  slug: peer
  description: Settlement-free private peering
  color: 2196f3
```

Entries are matched on `slug`. A relationship whose slug already exists is
left as it is, so the command is safe to run repeatedly. `tags` and custom
field values are accepted per entry. A missing file is skipped.

If any initializer raises, the command prints the traceback and exits
non-zero.
