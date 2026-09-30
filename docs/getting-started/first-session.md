# Your first peering session

A **PeeringSession** is a thin one-to-one wrapper around a
`netbox_routing.BGPPeer`. The BGP layer (peer IPs, ASNs, BFD, address
families, route maps, prefix lists, peer template) is owned by
netbox-routing. The peering layer adds:

- `relationship` - the kind of session (transit, customer, peer, IXP).
- `peering_network` - which IX LAN this session sits on (if any).
- `service_reference` - a free-form string for ticket / order tracking.

This page walks through the full sequence: create the supporting objects,
build the netbox-routing peer, wrap it with a `PeeringSession`.

## Prerequisites

Before opening a peering session you typically have:

- A `PeeringFabric` and at least one `PeeringNetwork` (see
  [your first fabric](first-fabric.md)).
- A `PeeringConnection` from your router to that network so the local IP
  exists on an interface in NetBox IPAM.
- A NetBox `ipam.ASN` for the remote peer's AS number (auto-created by
  PeeringDB sync if you used Path 1, or imported manually from RIPE/ARIN
  data).
- A `netbox_routing.BGPRouter` for your local router with a `BGPScope`
  (global or VRF).

## Step 1: classify the session

Open **Peering &rarr; Relationship Types &rarr; Add** and create the
relationship taxonomy you want, for example:

| Slug      | Name      | Color    |
|-----------|-----------|----------|
| transit   | Transit   | red      |
| customer  | Customer  | blue     |
| peer      | Peer      | green    |
| ixp-rs    | IX Route Server | yellow |

You only need to do this once. Relationship types are reused across every
session and surface as a colored badge in tables.

## Step 2: capture peer-side metadata

Create a `PeerASN` for the remote peer. This object extends `ipam.ASN`
with the data you need for prefix lists and templates:

1. Navigate to **Peering &rarr; Peer ASNs &rarr; Add**.
2. Pick the underlying `ipam.ASN`.
3. Fill in:
   - `affiliated`: True if you operate this ASN. Use it for sibling
     networks or anycast siblings.
   - `irr_as_set`: The IRR AS-SET you intend to filter against, e.g.
     `AS-CUSTOMER` or `RIPE::AS-EXAMPLE`.
   - `ipv4_max_prefixes` / `ipv6_max_prefixes`: per-AFI limits.
   - `peeringdb_id` (optional): if you populated it manually; the
     `PeeringDBSyncService.sync_peer_asn()` method fills it in
     automatically along with prefix limits and the IRR AS-SET.

You can sync everything from PeeringDB in one shot:

```python
from netbox_peering_manager.models import PeerASN
from netbox_peering_manager.services import PeeringDBSyncService

service = PeeringDBSyncService()
peer = PeerASN.objects.get(asn__asn=64500)
service.sync_peer_asn(peer)
peer.refresh_from_db()
print(peer.irr_as_set, peer.ipv4_max_prefixes, peer.ipv6_max_prefixes)
```

## Step 3: create the underlying BGPPeer

This step lives in netbox-routing. From the UI: **Routing &rarr; BGP &rarr;
Peers &rarr; Add**. Required fields, in plain English:

- **Scope**: the `BGPScope` on your `BGPRouter`. Sessions are attached to
  scopes (global table or per-VRF).
- **Peer**: the remote `IPAddress` (their side of the IX LAN).
- **Source**: your local `IPAddress` (your side of the IX LAN).
- **Local AS / Remote AS**: link to `ipam.ASN` records.
- **Peer group** (`BGPPeerTemplate`): optional. Inherit timers, AFIs,
  policies. The `peer_group` you set on the parent `PeeringFabric` is a
  reasonable default.
- **BFD**, **TTL / multihop**, **password**: as applicable.
- **Address families**: add `BGPPeerAddressFamily` rows for each AFI/SAFI
  you want. Attach `RoutingPolicy` (route maps) and `PrefixList` for in /
  out filtering.

If you prefer the shell:

```python
from ipam.models import ASN, IPAddress
from netbox_routing.models import BGPPeer, BGPRouter, BGPScope

router = BGPRouter.objects.get(name="rt1.mtl")
scope = BGPScope.objects.get(router=router, scope=None)  # global

peer = BGPPeer.objects.create(
    scope=scope,
    peer=IPAddress.objects.get(address="198.51.100.42/24"),
    source=IPAddress.objects.get(address="198.51.100.1/24"),
    local_as=ASN.objects.get(asn=64500),
    remote_as=ASN.objects.get(asn=64512),
    name="AS64512 - Example Peer (LINX)",
    enabled=True,
)
```

## Step 4: wrap with a PeeringSession

Now layer the peering metadata on top.

1. Navigate to **Peering &rarr; Peering Sessions &rarr; Add**.
2. Pick the `BGPPeer` you just created. The form enforces the one-to-one
   constraint - each `BGPPeer` can have at most one `PeeringSession`.
3. Pick the `Relationship` (transit / customer / peer / etc.).
4. Pick the `PeeringNetwork` (your IX LAN).
5. Optionally fill in `service_reference` (ticket ID, NOC reference, etc.).

From the shell:

```python
from netbox_peering_manager.models import (
    PeeringNetwork, PeeringSession, Relationship,
)

network = PeeringNetwork.objects.get(fabric__name="LINX LON1", name__startswith="LINX")
relation = Relationship.objects.get(slug="peer")

PeeringSession.objects.create(
    bgp_peer=peer,
    relationship=relation,
    peering_network=network,
    service_reference="NOC-12345",
)
```

## Step 5: render config

Once a session exists, you can feed it through the
[configuration templating](../user-guide/configuration-templating.md) flow.
The fastest way to verify everything is wired up:

```bash
curl -X POST http://netbox/api/plugins/bgp/render-config/ \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": 7, "device": 42}'
```

`template` is the ID of a NetBox `ConfigTemplate` (see the example
templates under `docs/examples/templates/`). `device` is the device whose
`BGPRouter` the session lives on. The response contains the rendered
config plus a `session_count` metadata field.

## What you should see in the UI

- The session row appears on the `PeeringSession` list with relationship
  badge and service reference.
- The relationship detail page shows a session table including this row.
- The peer ASN detail page shows a session table for every session whose
  remote AS matches.
- The peering network detail page shows the session under its sessions
  table and the corresponding `PeeringConnection` if you have one.

## Common pitfalls

- **`BGPPeer` already has a `PeeringSession`.** Each `BGPPeer` is 1:1 with
  a session. Edit the existing session instead of creating a new one.
- **`PeeringNetwork` is on the wrong fabric.** Sessions can be attached to
  any network, but during config rendering the per-session
  `peering_network.fabric.name` is what shows up in the template context.
  Pick the correct LAN.
- **No `PeeringConnection`.** The model graph allows sessions without a
  matching connection. The UI does not warn about it. If your templates
  expect `device.interfaces[*].peering_connections` to enumerate sessions,
  populate a connection too.
