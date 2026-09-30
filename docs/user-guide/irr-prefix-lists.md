# IRR prefix lists

The plugin can fill a netbox-routing prefix list from Internet Routing
Registry data. You name an AS-SET, the plugin asks a
[fastbgpq4](https://github.com/jsenecal/fastbgpq4) service to expand it,
and the prefix list entries are rewritten to match.

This page is the operator workflow. The wire-level details of the
fastbgpq4 calls are on the [IRR integration](../integrations/irr.md) page.

## Before you start

- A fastbgpq4 instance reachable **from the NetBox RQ worker**. The sync
  runs on the worker, not in the web process.
- A running NetBox RQ worker.
- The prefix list you want to manage, created in netbox-routing.

## 1. Create an IRR source

**Peering &rarr; IRR &rarr; IRR Sources &rarr; Add**. Give it a name and
the base URL of your fastbgpq4 instance, without any path. The remaining
fields are optional and described under
[IRRSource](../concepts/models.md#irrsource).

One source per fastbgpq4 instance is usually enough. Create several when
you want different registry selections for different prefix lists.

## 2. Attach a prefix list

**Peering &rarr; IRR &rarr; IRR Prefix List Configs &rarr; Add**. Pick the
netbox-routing prefix list to manage, the source from step 1, and the
AS-SET to expand. Field rules are under
[IRRPrefixListConfig](../concepts/models.md#irrprefixlistconfig).

The prefix list's **address family** decides what is requested. An IPv4
prefix list receives only IPv4 prefixes and an IPv6 list only IPv6. To
filter both families for one peer, create two prefix lists and two
configs with the same AS-SET.

## 3. Sync

Open the config and click **Sync from IRR**. This enqueues a background
job and returns immediately. Follow it under **Operations &rarr; Jobs**.

!!! warning "The sync replaces every entry"

    Entries you added by hand are lost on the next run. Keep manual
    exceptions in a separate, unmanaged prefix list. What exactly is
    written is described under
    [netbox-routing integration](../integrations/netbox-routing.md#objects-written).

The replacement is atomic. If fastbgpq4 is unreachable or the AS-SET
cannot be expanded, the job fails and the previous entries stay in place.

The finished job records what happened:

| Key | Meaning |
|-----|---------|
| `as_set`, `irr_source`, `prefix_list`, `family` | What was queried. |
| `prefixes` | Prefixes returned by the IRR. |
| `deleted_entries`, `created_entries` | Entries removed and written. |
| `error` | Present only on failure. |

## Syncing on a schedule

Both IRR sources and prefix list configs have a **Sync Interval** field in
minutes. The field records the interval you intend; the plugin does not
start recurring jobs by itself. Register the schedule once from `nbshell`:

```python
from netbox_peering_manager.jobs import SyncPrefixListJob
from netbox_peering_manager.models import IRRPrefixListConfig

managed = IRRPrefixListConfig.objects.filter(irr_source__isnull=False).exclude(source_as_set="")
for config in managed:
    SyncPrefixListJob.enqueue_once(instance=config, interval=config.sync_interval)
```

`enqueue_once` is idempotent: running the snippet again keeps an unchanged
schedule and replaces one whose interval changed. NetBox re-enqueues the
job after each run. Run the snippet again after adding configs.

## Syncing everything on a source

`SyncAllPrefixListsJob` walks every managed prefix list of one source in a
single job:

```python
from netbox_peering_manager.jobs import SyncAllPrefixListsJob
from netbox_peering_manager.models import IRRSource

SyncAllPrefixListsJob.enqueue(instance=IRRSource.objects.get(slug="radb"))
```

A failing prefix list does not stop the others. The job data reports
`total_configs`, `synced`, `failed`, and an `errors` list naming each
prefix list that failed; the job is marked errored if any did. A disabled
source refuses to run.

## Using the result

The managed prefix list is an ordinary netbox-routing prefix list. Attach
it to a BGP peer address family as an inbound or outbound filter, and it
appears in the [template context](configuration-templating.md) under that
session's `address_families`.

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| "This prefix list config is not IRR-managed" | The config has no IRR source and AS-SET. |
| Job stays pending | No RQ worker is running. |
| Job fails with a connection error | The worker cannot reach the fastbgpq4 URL. Test from the worker host, not the web host. |
| Job fails after about five minutes | fastbgpq4 did not finish expanding a very large AS-SET in time. |
| Prefix list is empty after a successful job | The AS-SET expands to nothing in the selected registries, or for that address family. |
| "IRR source is disabled" | The sync-all job was started on a disabled source. |
