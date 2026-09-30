# PeeringDB sync

PeeringDB sync keeps a fabric aligned with its Internet Exchange record on
[PeeringDB](https://www.peeringdb.com/). It refreshes the IX metadata,
makes sure every IXLAN prefix exists as a peering network, and rebuilds a
cache of who else is present on the exchange.

Sync is selective. Nothing is imported globally: only fabrics you have
linked to a PeeringDB IX ID are ever queried.

This page covers the day-to-day workflow. For the API calls, field
mapping, rate limits, and error handling behind it, see the
[PeeringDB integration](../integrations/peeringdb.md) page.

## Linking a fabric

A fabric is "linked" when it has a PeeringDB IX ID. There are three ways
to create the link.

**Create the fabric from PeeringDB.** Go to **Peering &rarr; Fabrics
&rarr; Create from PeeringDB**, search for the IX by name, and submit. The
fabric is created, linked, and synced in one step. The walkthrough is in
[your first peering fabric](../getting-started/first-fabric.md).

**Link an existing fabric in the UI.** Edit the fabric and fill in the
PeeringDB IX ID field. Saving stores the link but does not sync. Clearing
the field and saving removes the link and its cached PeeringDB metadata.

**Link from the shell.** Useful in migration scripts:

```python
from netbox_peering_manager.models import PeeringFabric
from netbox_peering_manager.services import link_fabric_to_peeringdb

fabric = PeeringFabric.objects.get(slug="linx-lon1")
result = link_fabric_to_peeringdb(fabric, ix_id=18)  # syncs by default
print(result.success, result.errors)
```

Pass `sync=False` to store the link without syncing.

An IX ID can be linked to one fabric only.

## Running a sync

### From the UI

Open a linked fabric. The PeeringDB panel shows the IX ID, name, location,
and last sync time, with a **Sync from PeeringDB** button. The sync runs
inside the web request, so the page waits until it finishes. Expect a few
seconds: the client pauses between PeeringDB requests to respect rate
limits.

When it completes, a banner reports the number of networks created,
networks updated, and peers cached, or lists the errors.

### From the command line

```bash
cd /opt/netbox/netbox
python manage.py sync_peeringdb
```

With no options this syncs every linked fabric, which makes it the form to
schedule. Selecting a single fabric, refreshing only the peer cache, exit
codes, and a cron example are covered in the
[management commands reference](../reference/management-commands.md#sync_peeringdb).

## What a sync changes

A full sync does three things, in order.

1. **IX details.** The fabric's PeeringDB panel is refreshed. The fabric's
   own name, slug, and other fields are never overwritten.
2. **Networks.** For each IXLAN on the exchange, the networks already
   linked to it get their IXLAN metadata refreshed. An IXLAN with no
   linked network gets one network per prefix, which for a dual-stack
   exchange means one IPv4 and one IPv6 network.
3. **Peer cache.** The fabric's cached peers are deleted and rebuilt from
   the current PeeringDB membership.

Exchange membership changes far more often than the exchange itself, so
the sync can also be limited to step 3. Exactly which PeeringDB fields
land where is listed under
[field mapping](../integrations/peeringdb.md#field-mapping).

Things worth knowing:

- **Prefixes are created when missing.** If the IXLAN prefix is not in
  NetBox IPAM, the sync creates the `ipam.Prefix` with a description
  naming the fabric and IXLAN. An existing prefix is reused as is.
- **Existing networks are adopted, not duplicated.** If the fabric already
  has a network on that prefix, the sync links it to the IXLAN instead of
  creating a second one.
- **Networks are never deleted.** A prefix that disappears from PeeringDB
  leaves its network in place for you to decommission.
- **Your own ASNs can be excluded** from the peer cache. See
  [Configuration](../getting-started/configuration.md).
- **Peers without any IP address are skipped.**

## Using the peer cache

The peer cache answers "who could I peer with here" without another call
to PeeringDB. It is not displayed in the UI; query it from `nbshell`:

```python
from netbox_peering_manager.models import PeeringFabric

fabric = PeeringFabric.objects.get(slug="linx-lon1")

# Everyone on the exchange, largest ports first
for peer in fabric.peeringdb_peers.order_by("-speed")[:20]:
    print(peer.asn, peer.name, peer.ipv4_addr, peer.ipv6_addr, peer.speed)

# Route server participants only
fabric.peeringdb_peers.filter(is_rs_peer=True).count()
```

Rows are replaced on every sync, so do not attach anything to them.

## Syncing a peer ASN

A `PeerASN` can be filled from its PeeringDB network record (see
[field mapping](../integrations/peeringdb.md#network-to-peerasn)). There is
no UI button for this yet; run it from `nbshell`:

```python
from netbox_peering_manager.models import PeerASN
from netbox_peering_manager.services import PeeringDBSyncService

service = PeeringDBSyncService()
for peer_asn in PeerASN.objects.filter(affiliated=False):
    service.sync_peer_asn(peer_asn)
```

`sync_peer_asn` returns `False` when PeeringDB has no network for that ASN
or the request fails, and leaves the record unchanged. Be aware that a
successful sync **overwrites** `irr_as_set` and both max-prefix fields
with the PeeringDB values, including when PeeringDB has them empty.

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| No **Sync from PeeringDB** button | The fabric is not linked. Set its PeeringDB IX ID. |
| The command reports a missing PeeringDB link | Same. The command never creates links. |
| Sync is slow | Expected. Requests are spaced out, and a rate-limit response makes the client wait before retrying. |
| Errors mention rate limiting | Configure a PeeringDB API key for a higher request allowance. |
| A network was not created for an IXLAN | The IXLAN has no prefix on PeeringDB. |
