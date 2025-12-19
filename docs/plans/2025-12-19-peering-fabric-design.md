# Phase 2: Peering Fabric Design

**Date:** 2025-12-19
**Status:** Approved
**Author:** Collaborative design session

## Overview

This design introduces a generic abstraction for shared peering environments (Internet Exchanges, cloud exchanges, private peering LANs, etc.) that integrates with NetBox's existing infrastructure models.

## Goals

1. Model any shared peering environment generically (not IX-specific)
2. Track physical/logical connections to peering fabrics
3. Leverage NetBox's native models (Interface, IPAddress, VLAN, Prefix) without duplication
4. Support multiple routers per fabric
5. Support multiple networks/VLANs per fabric
6. Maintain feature parity with Peering Manager's IX functionality

## Non-Goals

- PeeringDB integration (Phase 3)
- Configuration templating (Phase 5)
- Session state monitoring (Phase 7)

---

## Data Model

### PeeringFabricType

Organizational model for classifying fabric types. User-defined taxonomy.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | CharField(100) | Yes | Display name (e.g., "Internet Exchange") |
| `slug` | SlugField(100) | Yes | URL-friendly identifier |
| `description` | CharField(200) | No | Brief description |
| `color` | ColorField | No | UI display color |

**Examples:** Internet Exchange, Cloud Exchange, Private Peering LAN, Meet-Me Room, Ethernet Fabric

---

### PeeringFabric

The overall peering environment/exchange.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | CharField(100) | Yes | Display name (e.g., "AMS-IX", "Equinix Fabric NYC") |
| `slug` | SlugField(100) | Yes | URL-friendly identifier |
| `description` | CharField(200) | No | Brief description |
| `type` | FK(PeeringFabricType) | No | Classification of this fabric |
| `status` | ChoiceField | Yes | active, planned, decommissioned |
| `peeringdb_id` | PositiveIntegerField | No | PeeringDB IX ID (for future integration) |
| `site` | FK(dcim.Site) | No | Physical location |
| `tenant` | FK(tenancy.Tenant) | No | Operator/owner of the fabric |
| `peer_group` | FK(BGPPeerGroup) | No | Default peer group for sessions on this fabric |
| `comments` | TextField | No | Markdown-formatted notes |
| `tags` | M2M(extras.Tag) | No | NetBox tags |

**Relationships:**
- Has many `PeeringNetwork` (the LANs within this fabric)

---

### PeeringNetwork

A specific peering LAN within a fabric. A fabric may have multiple networks (e.g., production peering, GRX service, reseller VLAN).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fabric` | FK(PeeringFabric) | Yes | Parent fabric |
| `name` | CharField(100) | Yes | Display name (e.g., "Production Peering", "GRX") |
| `prefix` | FK(ipam.Prefix) | Yes | The peering LAN subnet |
| `vlan` | FK(ipam.VLAN) | No | Associated VLAN |
| `status` | ChoiceField | Yes | active, planned, decommissioned |
| `description` | CharField(200) | No | Brief description |
| `comments` | TextField | No | Markdown-formatted notes |

**Constraints:**
- `prefix` is required (a peering network must have a defined subnet)
- Unique together: `fabric` + `name`

**Relationships:**
- Belongs to one `PeeringFabric`
- Has many `PeeringConnection`
- Has many `BGPSession` (sessions on this network)

---

### PeeringConnection

Your router's attachment to a peering network. Leverages NetBox's Interface model for IP addresses, MAC, and VLAN assignments.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `peering_network` | FK(PeeringNetwork) | Yes | The network this connection attaches to |
| `interface` | FK(dcim.Interface) | Yes | The interface (physical, virtual, or sub-interface) |
| `status` | ChoiceField | Yes | active, planned, decommissioned |
| `description` | CharField(200) | No | Brief description |

**Derived from NetBox (not stored):**
- `device` → `interface.device`
- `ip_addresses` → `interface.ip_addresses` filtered by `peering_network.prefix`
- `mac_address` → `interface.mac_address`
- `vlan` → `interface.untagged_vlan` or `interface.tagged_vlans`

**Constraints:**
- Unique together: `peering_network` + `interface`
- Interface can be physical, virtual, LAG, or sub-interface

**Validation:**
- At least one IP address on the interface should be within the peering network's prefix

---

### BGPSession (Existing Model - Enhancement)

Add optional reference to PeeringNetwork.

| New Field | Type | Required | Description |
|-----------|------|----------|-------------|
| `peering_network` | FK(PeeringNetwork) | No | The peering network this session operates on |

**Behavior:**
- If `peering_network` is set, the session is considered a "fabric session"
- The `PeeringConnection` is inferred by matching `local_address` to an interface's IP within the network's prefix
- Validation: if `peering_network` is set, `local_address` should be within `peering_network.prefix`

---

## Model Hierarchy

```
PeeringFabricType (organizational)
    │
    └── classifies
            │
            ▼
PeeringFabric (AMS-IX)
    │
    ├── PeeringNetwork (Production Peering)
    │       ├── prefix: 203.0.113.0/24
    │       ├── vlan: 100
    │       │
    │       ├── PeeringConnection (Router-A / xe-0/0/0.100)
    │       │       └── IP: 203.0.113.10 (from interface)
    │       │
    │       ├── PeeringConnection (Router-B / xe-0/0/0.100)
    │       │       └── IP: 203.0.113.11 (from interface)
    │       │
    │       └── BGPSession (AMS-IX-RS1)
    │               ├── local_address: 203.0.113.10
    │               ├── remote_address: 203.0.113.253
    │               └── peering_network: → Production Peering
    │
    └── PeeringNetwork (GRX Service)
            ├── prefix: 192.0.2.0/24
            ├── vlan: 200
            │
            └── PeeringConnection (Router-A / xe-0/0/1.200)
                    └── IP: 192.0.2.10 (from interface)
```

---

## Status Choices

Shared across all new models:

```python
class PeeringStatusChoices(ChoiceSet):
    STATUS_ACTIVE = "active"
    STATUS_PLANNED = "planned"
    STATUS_DECOMMISSIONED = "decommissioned"

    CHOICES = [
        (STATUS_ACTIVE, "Active", "green"),
        (STATUS_PLANNED, "Planned", "cyan"),
        (STATUS_DECOMMISSIONED, "Decommissioned", "gray"),
    ]
```

---

## API & GraphQL

All models will have:
- REST API serializers and viewsets
- GraphQL types and filters
- Standard NetBox bulk operations (create, edit, delete, import)

---

## Navigation

Add new menu section under Peering Manager:

```
Peering Manager
├── BGP
│   ├── Sessions
│   ├── Peer Groups
│   └── ...
├── Fabrics          ← NEW
│   ├── Fabric Types
│   ├── Fabrics
│   ├── Networks
│   └── Connections
└── Policy
    ├── Routing Policies
    └── ...
```

---

## Migration Strategy

1. Create new models (no data migration needed - additive only)
2. Add `peering_network` field to BGPSession (nullable)
3. Existing sessions continue to work without peering_network reference

---

## Implementation Tasks

1. Create `PeeringFabricType` model with full CRUD
2. Create `PeeringFabric` model with full CRUD
3. Create `PeeringNetwork` model with full CRUD
4. Create `PeeringConnection` model with full CRUD
5. Add `peering_network` FK to `BGPSession`
6. Create forms, tables, filtersets for all new models
7. Create API serializers and viewsets
8. Create GraphQL types and filters
9. Update navigation menu
10. Create migrations
11. Add initializer support for demo data
12. Write tests

---

## Future Considerations (Not in Scope)

- **PeeringDB Integration (Phase 3):** Auto-populate fabric data from PeeringDB using `peeringdb_id`
- **Route Server Detection:** Flag sessions as route server sessions
- **Peer Discovery:** Discover available peers on a fabric via PeeringDB
- **IX-API Integration:** For IXes that support IX-API

---

## Decision Log

| Decision | Rationale |
|----------|-----------|
| Generic "PeeringFabric" instead of "InternetExchange" | Supports IXes, cloud exchanges, private LANs, and future peering paradigms |
| Separate PeeringNetwork model | Fabrics can have multiple LANs (production, GRX, reseller, etc.) |
| PeeringConnection references Interface only | Leverage NetBox's IP/MAC/VLAN on Interface, avoid data duplication |
| BGPSession references PeeringNetwork (not Connection) | Simpler; connection can be inferred from local_address |
| PeeringFabricType as organizational model | User-defined taxonomy, NetBox convention |
| prefix required on PeeringNetwork | A peering network must have a defined subnet |
