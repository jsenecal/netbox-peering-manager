# Architecture

netbox-peering-manager is deliberately small. It does not model BGP. It
adds the peering-specific layer that sits on top of BGP objects owned by
[netbox-routing](https://github.com/DanSheps/netbox-routing), which in turn
sit on top of core NetBox objects.

## Three layers

| Layer | Owns | Examples |
|-------|------|----------|
| Core NetBox | Inventory and addressing | `dcim.Device`, `dcim.Interface`, `dcim.Site`, `ipam.ASN`, `ipam.Prefix`, `ipam.IPAddress`, `ipam.VLAN`, `tenancy.Tenant`, `extras.ConfigTemplate` |
| netbox-routing | BGP protocol objects | `BGPRouter`, `BGPScope`, `BGPPeer`, `BGPPeerTemplate`, `BGPPeerAddressFamily`, `BFDProfile`, `PrefixList`, `PrefixListEntry`, route maps |
| netbox-peering-manager | Peering context | `PeeringFabric`, `PeeringNetwork`, `PeeringConnection`, `PeeringSession`, `PeerASN`, `Relationship`, `IRRSource`, `IRRPrefixListConfig` |

The plugin declares `required_plugins = ["netbox_routing"]`, so NetBox
will not load it without netbox-routing. Enabling both is covered in
[Installation](../getting-started/installation.md#install-netbox-peering-manager).

## How the layers connect

```
core NetBox              netbox-routing            netbox-peering-manager
-----------              --------------            ----------------------
ipam.ASN  <------------------------------------ 1:1  PeerASN
                         BGPPeer  <------------ 1:1  PeeringSession
                                                       |-- Relationship
                                                       `-- PeeringNetwork
                         PrefixList  <--------- 1:1  IRRPrefixListConfig
                                                       `-- IRRSource
                         BGPPeerTemplate  <---- FK   PeeringFabric
dcim.Site, Tenant  <--------------------------- FK   PeeringFabric
ipam.Prefix, VLAN  <--------------------------- FK   PeeringNetwork
dcim.Interface  <------------------------------ FK   PeeringConnection
```

A fabric contains networks, a network carries connections and sessions:

```
PeeringFabricType
  `-- PeeringFabric            (an IX, cloud exchange, or private LAN)
        `-- PeeringNetwork     (one peering LAN / prefix)
              |-- PeeringConnection   (your router interface on that LAN)
              `-- PeeringSession      (wraps one netbox-routing BGPPeer)
```

## The extension-model pattern

Three models extend an object owned by another app through a one-to-one
link instead of subclassing or copying it:

- `PeeringSession` extends `netbox_routing.BGPPeer`.
- `PeerASN` extends `ipam.ASN`.
- `IRRPrefixListConfig` extends `netbox_routing.PrefixList`.

The parent object stays the single source of truth for protocol data. The
extension row only stores what is specific to peering: the relationship
type, the fabric network, the service reference, the IRR AS-SET, the
max-prefix limits.

The practical consequence: creating a peering session is always two
steps. First the `BGPPeer` in netbox-routing, then the `PeeringSession`
that wraps it. See
[your first peering session](../getting-started/first-session.md).

## Services

Logic that is not plain CRUD lives outside the models:

| Component | Module | Role |
|-----------|--------|------|
| `PeeringDBClient` | `services/peeringdb.py` | Rate-limited HTTP client for the PeeringDB REST API |
| `PeeringDBSyncService` | `services/peeringdb_sync.py` | Maps PeeringDB IX, IXLAN, and peer data onto fabrics, networks, and the peer cache |
| `IRRClient` | `irr_client.py` | HTTP client for a fastbgpq4 instance |
| `SyncPrefixListJob`, `SyncAllPrefixListsJob` | `jobs.py` | NetBox `JobRunner` jobs that rewrite prefix list entries from IRR data |
| `ConfigRenderer` | `services/config_renderer.py` | Builds the denormalized template context for configuration rendering |

Two execution models are in play:

- **PeeringDB sync runs inline.** The UI button, the "Create from
  PeeringDB" view, and the `sync_peeringdb` management command all call
  the sync service directly and wait for it to finish.
- **IRR sync runs in the background.** The UI enqueues a job on the NetBox
  RQ worker, so a worker must be running.

## Surfaces

| Surface | Location |
|---------|----------|
| Web UI | `/plugins/peering-manager/` (menu: **Peering**) |
| REST API | `/api/plugins/peering-manager/` - see the [REST API reference](../reference/rest-api.md) |
| GraphQL | `netbox_peering_manager_*` query fields on the NetBox GraphQL endpoint |
| Management commands | `sync_peeringdb`, `load_all_initializer_data` - see [management commands](../reference/management-commands.md) |
| Jinja2 filters | Registered globally for NetBox template rendering - see [Jinja2 filters](../reference/jinja2-filters.md) |

The field-level description of every model is on the
[Models](models.md) page.
