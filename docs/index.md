# NetBox Peering Manager

A [NetBox](https://github.com/netbox-community/netbox) 4.5+ plugin that turns
your NetBox install into a source of truth for external BGP peering. It models
Internet Exchange (IX) infrastructure, peering sessions, peer ASN metadata,
and Internet Routing Registry (IRR) prefix-list synchronization, and feeds
all of it into multi-vendor configuration templates.

The plugin is a thin layer on top of
[netbox-routing](https://github.com/DanSheps/netbox-routing). All the heavy
BGP modeling (peers, peer templates, prefix lists, route maps, communities,
BFD profiles) lives in netbox-routing. This plugin adds the peering-specific
concepts on top: peering fabrics and networks, peer ASN metadata, IRR sync,
relationship taxonomy, and PeeringDB integration.

## What it gives you

- **Peering fabric and network modeling** for Internet Exchanges, cloud
  exchanges, and private peering LANs, with PeeringDB-driven discovery.
- **Peering sessions** layered on `netbox_routing.BGPPeer` so each session
  has a relationship type, a peering network reference, and a service
  reference (ticket / order ID).
- **Peer ASN profiles** that extend `ipam.ASN` with IRR AS-SET, IPv4 / IPv6
  max-prefix limits, and a PeeringDB network ID.
- **PeeringDB sync** for IX details, IXLAN networks, and connected peers,
  with selective import (no global slurp).
- **IRR prefix-list sync** through [fastbgpq4](https://github.com/jsenecal/fastbgpq4),
  scheduled as NetBox `JobRunner` jobs against `netbox_routing.PrefixList`
  entries.
- **Configuration templating** via NetBox `ConfigTemplate` plus a denormalized
  context builder and a small set of vendor-agnostic Jinja2 filters
  (Cisco / Junos out of the box).
- **REST API** under `/api/plugins/bgp/` for everything the UI exposes,
  plus a `render-config/` endpoint that returns rendered device configs.

## How the docs are organized

- [Getting Started](getting-started/installation.md) - install, configure,
  bring up your first fabric and session end to end.
- [Concepts](concepts/architecture.md) - the model graph, where each piece
  comes from (this plugin vs. netbox-routing vs. core NetBox), and the
  reasoning behind it.
- [User Guide](user-guide/peeringdb-sync.md) - the day-to-day workflows:
  PeeringDB sync, IRR prefix-list sync, and configuration rendering.
- [Integrations](integrations/peeringdb.md) - how the plugin talks to
  PeeringDB, fastbgpq4, and netbox-routing, and what knobs each side exposes.
- [Reference](reference/rest-api.md) - REST endpoint catalog, Jinja2 filter
  signatures, management commands.
- [Development](development/contributing.md) - contributing notes, testing
  layout, mock patterns.

## Quick links

- [GitHub repository](https://github.com/jsenecal/netbox-peering-manager)
- [Issue tracker](https://github.com/jsenecal/netbox-peering-manager/issues)
- [PyPI: netbox-peering-manager](https://pypi.org/project/netbox-peering-manager/)
- [netbox-routing (required dependency)](https://github.com/DanSheps/netbox-routing)
- [fastbgpq4 (IRR sync backend)](https://github.com/jsenecal/fastbgpq4)
- [PeeringDB API documentation](https://docs.peeringdb.com/api_specs/)

## Compatibility at a glance

| NetBox    | Plugin   | netbox-routing | Python    |
|-----------|----------|----------------|-----------|
| 4.5.x     | 0.2.x    | 0.4.x+         | 3.12-3.14 |
| 4.4.x     | 0.1.x    | n/a            | 3.10+     |

`netbox_routing` is a required plugin and must appear before
`netbox_peering_manager` in `PLUGINS`. See the
[installation guide](getting-started/installation.md) for the full sequence.
