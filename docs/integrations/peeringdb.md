# PeeringDB

This page describes how the plugin talks to the
[PeeringDB API](https://docs.peeringdb.com/api_specs/): which endpoints it
calls, how responses map onto NetBox objects, and how it behaves under
rate limiting and failure. For the operator workflow, see
[PeeringDB sync](../user-guide/peeringdb-sync.md).

## Client

All requests go through `PeeringDBClient`
(`netbox_peering_manager.services`). It is read-only: the plugin never
writes to PeeringDB.

| Aspect | Behavior |
|--------|----------|
| Authentication | Anonymous, or `Authorization: Api-Key <key>` when an API key is configured. |
| User agent | `netbox-peering-manager/<version>`. |
| Retries | Up to 3 attempts on network errors and rate-limit responses, with exponential backoff between 2 and 10 seconds. |
| HTTP 429 | Waits for the `Retry-After` value (60 seconds when absent), then retries. |

The base URL, API key, timeout, and pacing between requests are plugin
settings; their defaults are in
[Configuration](../getting-started/configuration.md#settings-reference).
An API key is optional but raises PeeringDB's request allowance, which
matters when you sync many fabrics in one run.

## Endpoints used

| PeeringDB endpoint | Used for |
|--------------------|----------|
| `ix/<id>` | IX details for a linked fabric. |
| `ix?name__contains=` | The search box on "Create from PeeringDB". Returns at most 20 matches to the UI. |
| `ixlan?ix_id=` | The IXLANs of an exchange. |
| `ixpfx?ixlan_id=` | The prefixes of an IXLAN, when creating networks. |
| `netixlan?ixlan_id__in=` | Every member port on the exchange, fetched for all IXLANs in one batched request. |
| `net?asn=` | A network record, when syncing a `PeerASN`. |

A full sync of one fabric costs a handful of requests regardless of how
many members the exchange has, because member ports are fetched in a
single batched call.

## Field mapping

### IX to fabric

Stored on the fabric's PeeringDB record, not on the fabric itself.

| PeeringDB `ix` | Stored as |
|----------------|-----------|
| `id` | `ix_id` |
| `name` | `name` |
| `city` | `city` |
| `country` | `country` |
| `website` | `website` |
| `tech_email` | `tech_email` |

When a fabric is created from PeeringDB, its own name and slug are taken
from the IX name once, at creation. Later syncs never rename the fabric.

### IXLAN to network

| PeeringDB | Stored as |
|-----------|-----------|
| `ixlan.id` | `ixlan_id` on the network's PeeringDB record |
| `ixlan.name` | Network name at creation (`IXLAN-<id>` when PeeringDB has no name), and `name` on the PeeringDB record |
| `ixlan.mtu` | `mtu` |
| `ixlan.rs_asn` | `rs_asn` |
| `ixlan.dot1q_support` | `dot1q_support` |
| `ixpfx.prefix` | The network's `ipam.Prefix`, created in IPAM when missing |

One network is created per IXLAN prefix. When the generated name is
already taken inside the fabric, a numeric suffix is appended, which is
how the IPv4 and IPv6 networks of a dual-stack IXLAN get distinct names.

### Member port to peer cache

| PeeringDB `netixlan` | `PeeringDBPeer` field |
|----------------------|-----------------------|
| `asn` | `asn` |
| `name` | `name` (`AS<number>` when empty) |
| `ipaddr4` | `ipv4_addr` |
| `ipaddr6` | `ipv6_addr` |
| `is_rs_peer` | `is_rs_peer` |
| `speed` | `speed`, in Mbps |

### Network to PeerASN

| PeeringDB `net` | `PeerASN` field |
|-----------------|-----------------|
| `id` | `peeringdb_id` |
| `info_prefixes4` | `ipv4_max_prefixes` |
| `info_prefixes6` | `ipv6_max_prefixes` |
| `irr_as_set` | `irr_as_set` |

## Failure behavior

A fabric sync returns a result object rather than raising. It carries the
counters shown in the UI (`networks_created`, `networks_updated`,
`peers_synced`) and an `errors` list; `success` is true when that list is
empty.

| Situation | Outcome |
|-----------|---------|
| Fabric has no PeeringDB link | One error, nothing attempted. |
| IX or network not found on PeeringDB | Reported as an error for that step. |
| Network error or timeout | Retried, then reported as an error. |
| Rate limited | Waits and retries, then reported as an error if it persists. |
| A duplicate peer row | Skipped silently. |

The client raises three exception types, all subclasses of
`PeeringDBError` in `netbox_peering_manager.services.exceptions`:
`PeeringDBNotFoundError`, `PeeringDBRateLimitError`, and
`PeeringDBAPIError` (which carries the HTTP `status_code`).

## Using the client directly

The client is usable from `nbshell` for one-off lookups:

```python
from netbox_peering_manager.services import PeeringDBClient

client = PeeringDBClient()
client.search_ix("LINX")            # list of IX dicts
client.get_ix(18)                    # one IX dict
client.get_network(64500)            # one network dict, by ASN
client.get_networks_batch([64500, 64501])
```

Constructor arguments `base_url`, `api_key`, `timeout`, and `rate_limit`
override the plugin settings for that instance, which is convenient for
pointing a script at a PeeringDB mirror.

## Data scope

The plugin reads IX, IXLAN, IXLAN prefix, member port, and network
records. The technical contact email of an IX is stored when PeeringDB
returns it. Nothing is fetched for exchanges you have not linked.
