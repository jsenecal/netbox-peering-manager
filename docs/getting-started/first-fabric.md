# Your first peering fabric

A **PeeringFabric** represents a shared peering environment: an Internet
Exchange, a cloud exchange, or a private peering LAN. It carries metadata
(name, type, status, site, tenant), an optional default
`netbox_routing.BGPPeerTemplate` to use as a peer group baseline, and an
optional one-to-one link to PeeringDB through `PeeringFabricPeeringDB`.

There are two paths to your first fabric: import one from PeeringDB
(recommended for real IXes), or build one by hand for a private LAN that
PeeringDB does not know about.

## Path 1: import from PeeringDB

This is the fast path. The plugin ships a dedicated view that searches
PeeringDB by IX name, lets you pick one, and creates a fabric prefilled
from PeeringDB data.

1. Navigate to **Peering &rarr; Fabrics &rarr; Create from PeeringDB**.
2. Type at least two characters of the IX name in the search box. The
   AJAX endpoint at `/plugins/bgp/peeringdb/search/` calls
   `PeeringDBClient.search_ix` and returns up to 20 matches.
3. Pick the IX. Submit.
4. The view calls `PeeringFabric.objects.create()` with the PeeringDB
   name, then `link_fabric_to_peeringdb(fabric, ix_id, sync=True)` which:
   - Creates the `PeeringFabricPeeringDB` link record.
   - Runs a full PeeringDB sync (IX details, IXLANs as PeeringNetworks,
     peers cached as `PeeringDBPeer`).

You land on the new fabric's detail page with PeeringDB metadata, networks,
and a peer cache populated. From the shell, the same flow looks like:

```python
from django.utils.text import slugify
from netbox_peering_manager.models import PeeringFabric
from netbox_peering_manager.services import PeeringDBClient, link_fabric_to_peeringdb

client = PeeringDBClient()
ix = client.get_ix(31)  # LINX

fabric = PeeringFabric.objects.create(
    name=ix["name"],
    slug=slugify(ix["name"])[:100],
    description=f"Imported from PeeringDB IX {ix['id']}",
)
result = link_fabric_to_peeringdb(fabric, ix_id=ix["id"], sync=True)
print(result.networks_created, result.networks_updated, result.peers_synced)
```

## Path 2: build a private fabric by hand

Use this when you operate a private peering LAN, a metro fabric, or a cloud
exchange that has no PeeringDB record.

1. Navigate to **Peering &rarr; Fabrics &rarr; Fabric Types &rarr; Add**.
   Create a type such as `Private Peering LAN` with a recognizable color.
2. Navigate to **Peering &rarr; Fabrics &rarr; Fabrics &rarr; Add**. Fill
   in the fabric:
   - **Name** and **Slug**: e.g. `MTL-PRIV-PEER-1` / `mtl-priv-peer-1`.
     The model enforces uniqueness on `(name, site)` if a site is set, or
     just on `name` otherwise.
   - **Type**: the `PeeringFabricType` you just created.
   - **Status**: Active, Planned, or Decommissioned (from
     `PeeringStatusChoices`).
   - **Site** and **Tenant**: optional, link to NetBox DCIM/tenancy.
   - **Peer group** (`peer_group`): a `netbox_routing.BGPPeerTemplate` that
     sessions on this fabric default to. This is a convenience field for
     templates; nothing enforces it on the data model.

## Add at least one PeeringNetwork

A fabric without a network cannot have peering sessions attached.
`PeeringNetwork` is the per-LAN object. If you imported from PeeringDB, one
or more networks already exist (one per IXLAN prefix, named after the
IXLAN). Otherwise, add one manually:

1. Navigate to **Peering &rarr; Fabrics &rarr; Networks &rarr; Add**.
2. Pick the fabric. Pick a `Prefix` from IPAM (the L2 LAN prefix, e.g.
   `198.51.100.0/24`). Optionally pick a `VLAN`.
3. Set the status. Save.

`PeeringNetwork` has a unique constraint on `(fabric, name)`, so each
network within a fabric must have a distinct name.

## Add a PeeringConnection

A `PeeringConnection` ties one of your routers to a peering network. It
records the device interface that physically attaches to the LAN.

1. Navigate to **Peering &rarr; Fabrics &rarr; Connections &rarr; Add**.
2. Pick the **Peering Network**.
3. Pick the **Interface** (a `dcim.Interface` on the device that lands on
   the peering LAN).
4. Set the status. Save.

The connection's `ip_addresses` property returns NetBox `IPAddress` objects
on that interface that fall inside the peering network's prefix - useful
for sanity-checking that you have actually configured a local IP on the
router before opening sessions.

## Verify

From the fabric's detail page you should now see:

- A `PeeringDB Info` panel (IX ID, city, country, last sync) if linked to
  PeeringDB.
- A list of `PeeringNetwork` rows.
- A list of `PeeringConnection` rows for any of your routers attached to
  those networks.
- An empty `PeeringSession` table - sessions are next.

## Next: create your first session

Continue to [your first peering session](first-session.md) to build the
underlying `BGPPeer` in netbox-routing, wrap it in a `PeeringSession`, and
attach it to the network.
