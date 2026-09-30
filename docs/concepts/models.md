# Models

This page lists every model the plugin defines, what each field means, and
what happens to related objects on delete. For how the models relate to
netbox-routing and core NetBox, read [Architecture](architecture.md) first.

Nine models are full NetBox models: they have tags, custom fields, change
logging, journaling, a UI, a REST endpoint, and a GraphQL type. Three more
are plain cache tables filled by PeeringDB sync.

## Status values

`PeeringFabric`, `PeeringNetwork`, and `PeeringConnection` share one status
choice set:

| Value | Label | Color |
|-------|-------|-------|
| `active` | Active | green |
| `planned` | Planned | cyan |
| `decommissioned` | Decommissioned | gray |

## Peering models

### Relationship

A user-defined session classification such as transit, customer, or peer.

| Field | Notes |
|-------|-------|
| `name` | Unique. |
| `slug` | Unique. |
| `description` | Optional. |
| `color` | Badge color, defaults to gray (`9e9e9e`). |
| `comments` | Optional. |

Deleting a relationship clears it from the sessions that used it.

### PeerASN

Peering metadata for one `ipam.ASN`. One-to-one: an ASN has at most one
`PeerASN`, and deleting the ASN deletes it.

| Field | Notes |
|-------|-------|
| `asn` | The `ipam.ASN` being extended. Required. |
| `affiliated` | True when your organization operates this ASN. |
| `irr_as_set` | IRR AS-SET name, for example `AS-EXAMPLE` or `RIPE::AS-EXAMPLE`. |
| `ipv4_max_prefixes`, `ipv6_max_prefixes` | Optional max-prefix limits. |
| `peeringdb_id` | PeeringDB network ID. Unique when set. |
| `peeringdb_last_sync` | Set when the record was last refreshed from PeeringDB. |
| `comments` | Optional. |

The display name comes from the ASN: its description, or `AS<number>` when
the description is empty.

### PeeringSession

Peering metadata for one `netbox_routing.BGPPeer`. One-to-one.

| Field | Notes |
|-------|-------|
| `bgp_peer` | The `BGPPeer` being extended. Required. |
| `relationship` | Optional `Relationship`. |
| `peering_network` | Optional `PeeringNetwork` the session runs on. |
| `service_reference` | Free text: ticket number, order ID, circuit ID. |

The link to `BGPPeer` is protected: a peer cannot be deleted while a
peering session still wraps it. Delete the session first.

## Fabric models

### PeeringFabricType

A classification for fabrics, for example Internet Exchange or Private
Peering LAN. Fields: `name` (unique), `slug` (unique), `description`,
`color`. Deleting a type clears it from its fabrics.

### PeeringFabric

A shared peering environment.

| Field | Notes |
|-------|-------|
| `name`, `slug` | `name` must be unique per site, or globally unique when no site is set. |
| `description` | Optional. |
| `type` | Optional `PeeringFabricType`. |
| `status` | See [status values](#status-values). Defaults to active. |
| `site` | Optional `dcim.Site`. Cleared if the site is deleted. |
| `tenant` | Optional `tenancy.Tenant`. A tenant in use by a fabric cannot be deleted. |
| `peer_group` | Optional `netbox_routing.BGPPeerTemplate` meant as the default for sessions on this fabric. Informational: nothing applies it automatically. |
| `comments` | Optional. |

Deleting a fabric deletes its networks, its PeeringDB link, and its peer
cache.

### PeeringNetwork

One peering LAN inside a fabric. An IX with separate IPv4 and IPv6 prefixes
has one network per prefix.

| Field | Notes |
|-------|-------|
| `fabric` | Parent fabric. Required. |
| `name` | Unique within the fabric. |
| `prefix` | The `ipam.Prefix` of the LAN. Required. A prefix in use by a network cannot be deleted. |
| `vlan` | Optional `ipam.VLAN`. |
| `status` | See [status values](#status-values). |
| `description`, `comments` | Optional. |

Deleting a network deletes its connections and clears it from its
sessions.

### PeeringConnection

Your router's attachment to a peering network.

| Field | Notes |
|-------|-------|
| `peering_network` | Required. |
| `interface` | The `dcim.Interface` on the LAN. Required. An interface in use by a connection cannot be deleted. |
| `status` | See [status values](#status-values). |
| `description` | Optional. |

A given interface can be attached to a given network only once. Two
computed properties are available in the shell: `device` (the interface's
device) and `ip_addresses` (the interface's IP addresses that fall inside
the network's prefix).

## IRR models

### IRRSource

One [fastbgpq4](https://github.com/jsenecal/fastbgpq4) instance to query.

| Field | Notes |
|-------|-------|
| `name`, `slug` | Both unique. |
| `url` | fastbgpq4 base URL, for example `http://fastbgpq4:8000`. |
| `sources` | Optional comma-separated IRR registries, for example `RIPE,RADB,ARIN`. Blank uses the fastbgpq4 default. |
| `cache_ttl` | Optional cache lifetime in seconds passed to fastbgpq4. |
| `sync_interval` | Intended minutes between syncs. Defaults to 1440. |
| `enabled` | A disabled source refuses the sync-all job. |
| `description`, `comments` | Optional. |

### IRRPrefixListConfig

Marks one `netbox_routing.PrefixList` as managed from IRR data.
One-to-one, and deleted together with the prefix list.

| Field | Notes |
|-------|-------|
| `prefix_list` | The `PrefixList` being managed. Required. |
| `irr_source` | The `IRRSource` to query. |
| `source_as_set` | The AS-SET to expand, for example `AS-HURRICANE`. |
| `sync_interval` | Intended minutes between syncs. Defaults to 1440. |

`irr_source` and `source_as_set` must be set together or left empty
together. A config with both is "IRR-managed" and can be synced. See
[IRR prefix lists](../user-guide/irr-prefix-lists.md) for how the sync is
triggered and what the interval fields do.

## PeeringDB cache tables

These rows are written by [PeeringDB sync](../user-guide/peeringdb-sync.md).
They have no tags, no change log, and no endpoint of their own.

| Model | One row per | Notes |
|-------|-------------|-------|
| `PeeringFabricPeeringDB` | Linked fabric | The IX ID is unique: one fabric per exchange. |
| `PeeringNetworkPeeringDB` | Linked network | Several networks can share one IXLAN ID, because a dual-stack IXLAN produces one network per prefix. |
| `PeeringDBPeer` | Member port on a fabric | Replaced on every sync. |

The cached fields, and the PeeringDB fields each one comes from, are
listed under [field mapping](../integrations/peeringdb.md#field-mapping).
