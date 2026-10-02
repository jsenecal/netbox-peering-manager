# netbox-routing

[netbox-routing](https://github.com/DanSheps/netbox-routing) is a hard
dependency. It owns every BGP protocol object; this plugin only references
them. This page lists exactly which netbox-routing objects are touched and
how, so you know what each side is responsible for.

## Requirements

- A netbox-routing release the plugin supports. The minimum is declared in
  the package metadata, so `pip` enforces it; the range for each plugin
  release is in the [compatibility table](https://github.com/jsenecal/netbox-peering-manager#compatibility).
- `netbox_routing` listed **before** `netbox_peering_manager` in `PLUGINS`.
  NetBox refuses to start otherwise.

Install steps are in
[Installation](../getting-started/installation.md).

## Objects referenced

| netbox-routing model | Referenced by | Link |
|----------------------|---------------|------|
| `BGPPeer` | `PeeringSession.bgp_peer` | One-to-one |
| `PrefixList` | `IRRPrefixListConfig.prefix_list` | One-to-one |
| `BGPPeerTemplate` | `PeeringFabric.peer_group` | Foreign key |

What happens on either side when one of these objects is deleted is
described per model on the [Models](../concepts/models.md) page. The rule
operators run into most: a BGP peer cannot be deleted while a peering
session wraps it.

## Objects read

Configuration rendering reads further netbox-routing objects without
holding references to them:

| Object | Read for |
|--------|----------|
| `BGPRouter` | Finding a device's routers. Only routers assigned to a **device** are considered. |
| `BGPScope` | Walking from a router to its peers. |
| `BGPPeer` | Name, description, status, enabled flag, local and remote AS, source and peer addresses, password, TTL. |
| `BGPPeerTemplate` | The peer group name. |
| `BFDProfile` | Transmit and receive intervals, multiplier, hold time. |
| `BGPPeerAddressFamily` | The address family, and the names of its inbound and outbound route maps and prefix lists. |

The resulting structure is documented in
[Configuration templating](../user-guide/configuration-templating.md#the-context).

## Objects written

Only IRR sync writes to netbox-routing, and only to prefix list contents.
Each run, inside one transaction:

- deletes all `PrefixListEntry` rows of the managed prefix list, then
- creates one custom prefix and one `permit` `PrefixListEntry` per prefix
  returned by the IRR, numbered from 1 in the order returned.

Entries carry no `ge` or `le` bounds: the prefix list matches exactly the
prefixes the registry lists.

The `PrefixList` row itself (name, family, description) is never
modified, and no other netbox-routing object is ever created, changed, or
deleted by this plugin. In particular, the plugin does **not** create BGP
peers: PeeringDB sync fills a peer cache, not netbox-routing.

## Division of labor in the UI

| Task | Where |
|------|-------|
| Define routers, scopes, peers, peer templates, BFD profiles | netbox-routing menus |
| Define route maps, prefix lists, communities, AS-path lists | netbox-routing menus |
| Classify a peer, attach it to a fabric network, record a service reference | **Peering &rarr; Peering Sessions** |
| Record max-prefix limits and the IRR AS-SET of a remote AS | **Peering &rarr; Peer ASNs** |
| Populate a prefix list from IRR | **Peering &rarr; IRR** |

## REST API nesting

Endpoints of this plugin embed netbox-routing objects using
netbox-routing's own serializers. A peering session response contains the
nested `bgp_peer` representation, and an IRR prefix list config contains
the nested `prefix_list`. When writing, pass the related object's ID.

## Upgrading netbox-routing

Because the plugin reads netbox-routing model fields directly, upgrade
both plugins together and consult the
[compatibility table](https://github.com/jsenecal/netbox-peering-manager#compatibility) first. The plugin's test
suite runs on every supported NetBox version against the newest
netbox-routing release that satisfies the requirement.

## Coming from v0.1.x

Releases before 0.2.0 shipped their own BGP session, peer group, routing
policy, prefix list, and community models. 0.2.0 removed all of them in
favor of netbox-routing. There is no automatic data migration; the
procedure is described in the
[README](https://github.com/jsenecal/netbox-peering-manager#upgrading-from-v01x).
