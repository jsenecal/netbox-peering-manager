# Feature Gap Analysis: netbox-peering-manager vs Peering Manager

This document provides a comprehensive comparison between the [original Peering Manager](https://github.com/peering-manager/peering-manager) project and the netbox-peering-manager NetBox plugin, identifying feature gaps and proposing a phased implementation roadmap.

## Executive Summary

netbox-peering-manager is a NetBox plugin that leverages NetBox's existing infrastructure (devices, sites, ASNs, IP addresses, tenants) while adding BGP-specific functionality. The original Peering Manager is a standalone application with its own data models for everything.

**Key Advantage of netbox-peering-manager:** Tight integration with NetBox eliminates data duplication and provides a single source of truth for network infrastructure.

**Key Gaps:** Configuration templating and session state monitoring.

**Recently Completed:** Session security and policy enhancements (Phase 4), PeeringDB selective sync integration (Phase 3), Internet Exchange support via Peering Fabric models (Phase 2), IRR prefix list synchronization (Phase 1.5).

---

## Feature Comparison Matrix

| Feature Category | Peering Manager | netbox-peering-manager | Gap Status |
|-----------------|-----------------|------------------------|------------|
| **Core Infrastructure** |
| Sites/Locations | Own model | Uses NetBox dcim.Site | ✅ Leveraged |
| Devices/Routers | Own Router model | Uses NetBox dcim.Device | ✅ Leveraged |
| ASN Management | Own AS model | Uses NetBox ipam.ASN | ⚠️ Partial |
| IP Addresses | Own model | Uses NetBox ipam.IPAddress | ✅ Leveraged |
| Tenants | N/A | Uses NetBox tenancy.Tenant | ✅ Leveraged |
| **BGP Sessions** |
| Direct Peering Sessions | ✅ DirectPeeringSession | ✅ BGPSession | ✅ Equivalent |
| IX Peering Sessions | ✅ IXPeeringSession | ❌ Missing | 🔴 Gap |
| Session Status | ✅ | ✅ | ✅ Equivalent |
| Relationship Types | ✅ | ✅ | ✅ Implemented |
| BFD Configuration | ✅ | ✅ | ✅ Implemented |
| Multihop TTL | ✅ | ✅ | ✅ Implemented |
| MD5 Password | ✅ | ✅ | ✅ Implemented |
| Service Reference | ✅ | ✅ | ✅ Implemented |
| Enabled Flag | ✅ | ✅ | ✅ Implemented |
| **Internet Exchanges** |
| IX Model | ✅ | ✅ PeeringFabric + PeeringFabricType | ✅ Implemented |
| IX Connections | ✅ | ✅ PeeringConnection | ✅ Implemented |
| IX Peering LAN | ✅ | ✅ PeeringNetwork | ✅ Implemented |
| **Routing Policy** |
| Basic Policies | ✅ | ✅ | ✅ Equivalent |
| Policy Rules | ✅ | ✅ | ✅ Equivalent |
| Policy Type (in/out) | ✅ | N/A | Skipped (YAGNI) |
| Policy Weight | ✅ | ✅ | ✅ Implemented |
| Address Family | ✅ | ✅ | ✅ Implemented |
| **BGP Communities** |
| Basic Communities | ✅ | ✅ | ✅ Equivalent |
| Community Lists | ✅ | ✅ | ✅ Equivalent |
| Community Type | ✅ ingress/egress | ❌ Missing | 🟡 Enhancement |
| Value Validation | ✅ RFC format | ✅ RFC format | ✅ Implemented |
| **Prefix Lists** |
| Basic Prefix Lists | ✅ | ✅ | ✅ Equivalent |
| Prefix List Rules | ✅ | ✅ | ✅ Equivalent |
| **AS Path Lists** |
| Basic AS Path Lists | ✅ | ✅ | ✅ Equivalent |
| AS Path Rules | ✅ | ✅ | ✅ Equivalent |
| **Peer Groups** |
| Basic Peer Groups | ✅ BGPGroup | ✅ BGPPeerGroup | ✅ Equivalent |
| **External Integrations** |
| PeeringDB Sync | ✅ Full | ✅ Selective sync | ✅ Implemented |
| IRR Integration | ✅ | ✅ IRRSource + PrefixList sync | ✅ Implemented |
| IX-API | ✅ | ❌ Missing | 🟡 Future |
| NetBox Integration | ✅ Reference only | ✅ Native | ✅ Better |
| **Configuration Management** |
| Config Templates | ✅ Jinja2 | ❌ Missing | 🔴 Gap |
| Template Rendering | ✅ | ❌ Missing | 🔴 Gap |
| Multi-vendor Support | ✅ | ❌ Missing | 🔴 Gap |
| **Operational** |
| Session State Polling | ✅ NAPALM | ❌ Missing | 🟡 Future |
| Webhooks | ✅ | ✅ NetBox native | ✅ Leveraged |
| REST API | ✅ | ✅ | ✅ Equivalent |
| GraphQL | ❌ | ✅ | ✅ Better |

**Legend:**
- ✅ Implemented/Equivalent
- ⚠️ Partial implementation
- 🟡 Enhancement needed
- 🔴 Major gap

---

## Detailed Gap Analysis

### 1. Internet Exchange Management ✅ COMPLETED

**Current State:** Fully implemented via Peering Fabric models.

**Implementation:**
- `PeeringFabricType` - Classifies fabric types (IX, Cloud Exchange, Private LAN)
- `PeeringFabric` - Represents IX or peering environment with PeeringDB ID support
- `PeeringNetwork` - Specific peering LAN with prefix and VLAN
- `PeeringConnection` - Router interface attachment to peering network
- `BGPSession.peering_network` - Optional link to peering network for IX sessions

**Model Structure:**

```
PeeringFabricType
├── name, slug, description, color

PeeringFabric
├── name, slug, description
├── type (FK to PeeringFabricType)
├── status, peeringdb_id
├── site (FK to dcim.Site)
├── tenant (FK to tenancy.Tenant)
├── peer_group (FK to BGPPeerGroup)
└── comments, tags

PeeringNetwork
├── fabric (FK to PeeringFabric)
├── name, status, description
├── prefix (FK to ipam.Prefix)
├── vlan (FK to ipam.VLAN)
└── comments, tags

PeeringConnection
├── peering_network (FK to PeeringNetwork)
├── interface (FK to dcim.Interface)
├── status, description
└── device (property from interface)

BGPSession (extended)
└── peering_network (optional FK to PeeringNetwork)
```

### 2. ASN Enhancements (MEDIUM PRIORITY)

**Current State:** Uses NetBox's `ipam.ASN` model directly.

**Missing Fields (need custom fields or extended model):**
- `affiliated` - Boolean flag for own ASNs
- `irr_as_set` - IRR AS-SET name for prefix validation
- `ipv4_max_prefixes` - Maximum IPv4 prefixes to accept
- `ipv6_max_prefixes` - Maximum IPv6 prefixes to accept

**Options:**
1. Use NetBox custom fields on ASN model
2. Create a `PeerASN` model that extends/references `ipam.ASN`
3. Request upstream NetBox changes

### 3. PeeringDB Integration ✅ COMPLETED

**Current State:** Selective sync approach implemented - only sync IXes you're connected to.

**Implemented Features:**
- `PeeringFabricPeeringDB` - One-to-one complement model storing IX metadata from PeeringDB
- `PeeringNetworkPeeringDB` - One-to-one complement model storing IXLAN metadata
- `PeeringDBPeer` - Cached peer data for discovery at each fabric
- `PeeringDBClient` - API client with tenacity retry logic (3 attempts, exponential backoff)
- `PeeringDBSyncService` - Orchestrates sync operations with SyncResult tracking
- Management command: `sync_peeringdb` with `--fabric`, `--ix-id`, `--discover-only` options
- Views for searching PeeringDB IXes, creating fabrics from PeeringDB, syncing
- API serializers with nested PeeringDB info
- AJAX-powered IX search in UI

**Configuration:**
```python
PLUGINS_CONFIG = {
    'netbox_peering_manager': {
        'peeringdb_url': None,           # Falls back to default
        'peeringdb_api_key': None,       # Optional for contact info
        'peeringdb_timeout': None,       # Falls back to 30s
        'peeringdb_local_asns': [],      # Your ASN(s) for filtering
    }
}
```

### 4. MD5 Password Support ✅ COMPLETED

**Current State:** Implemented with encrypted storage.

**Implementation:**
- `password` field on BGPSession using NetBox's encrypted storage
- Secure storage and retrieval via NetBox's secrets framework

### 5. Routing Policy Enhancements (PARTIALLY COMPLETED)

**Current State:** Weight field added for evaluation order.

**Implemented:**
- `weight` - Evaluation order (higher = first)

**Skipped/Deferred:**
- `type` (ingress/egress) - Not needed; handled by M2M relationship names (import_policies, export_policies)
- `address_family` - Deferred to future need

### 6. Community Enhancements (LOW PRIORITY)

**Current State:** Basic value with simple regex validation.

**Missing:**
- `type` field (ingress/egress application)
- RFC-compliant value validation:
  - Standard: `<16-bit>:<16-bit>`
  - Extended: `(origin|target):<asn>:<value>`
  - Large: `<32-bit>:<32-bit>:<32-bit>`

### 7. Configuration Templating (MEDIUM PRIORITY)

**Current State:** No config generation capability.

**Required:**
- Jinja2 template storage model
- Template context with session/policy data
- Render endpoint for generating configs
- Multi-vendor template examples

**NetBox Integration:**
- Leverage NetBox's existing config template framework
- Or create plugin-specific templates

### 8. Session State Monitoring (LOW PRIORITY - FUTURE)

**Current State:** No live state polling.

**Required:**
- NAPALM integration for device connectivity
- Background job to poll session states
- Store last known state and timestamp
- Alerting on state changes

---

## Phased Implementation Roadmap

### Phase 1: Session Enhancements & Relationship Model ✅ COMPLETED

- [x] Relationship model (transit, customer, peer, IXP)
- [x] BFD profile model
- [x] BGPSession fields: relationship, bfd, multihop_ttl, service_reference, enabled
- [x] Forms, tables, views, filtersets
- [x] API and GraphQL support
- [x] Migrations

### Phase 1.5: IRR Prefix List Sync ✅ COMPLETED

- [x] IRRSource model for configuring IRR servers (RADB, RIPE, etc.)
- [x] Automatic prefix list synchronization from IRR AS-SETs
- [x] Background job support for periodic sync
- [x] Tenacity retry logic for resilient IRR queries
- [x] Filtersets for IRRSource and PrefixList
- [x] API and GraphQL support

### Phase 2: Internet Exchange Support ✅ COMPLETED

**Priority:** HIGH
**Estimated Effort:** Large

**Models created:**
1. `PeeringFabricType` - Classification of fabric types (IX, Cloud Exchange, etc.)
2. `PeeringFabric` - Peering environment (IX, cloud exchange, private LAN)
3. `PeeringNetwork` - Specific peering LAN within a fabric
4. `PeeringConnection` - Router attachment to a peering network

**Design Decision:** Extended `BGPSession` with optional `peering_network` field instead of creating a separate `IXPeeringSession` model. This provides flexibility while maintaining a single session model.

**Tasks:**
- [x] Design and create PeeringFabricType model
- [x] Design and create PeeringFabric model
- [x] Design and create PeeringNetwork model
- [x] Design and create PeeringConnection model
- [x] Extend BGPSession with peering_network field
- [x] Create forms, tables, filtersets, views
- [x] Create API serializers and viewsets
- [x] Create GraphQL types
- [x] Add navigation menu items
- [x] Create migrations
- [x] Add URL patterns
- [x] Add initializer support
- [x] Write tests

### Phase 3: PeeringDB Integration ✅ COMPLETED

**Priority:** HIGH
**Estimated Effort:** Medium

**Design Decision:** Selective sync approach - only sync IXes you're connected to, not the entire PeeringDB database. This enables peer discovery without the overhead of full data caching.

**Tasks:**
- [x] Add plugin configuration for PeeringDB (url, api_key, timeout, local_asns)
- [x] Create PeeringDB complement models (PeeringFabricPeeringDB, PeeringNetworkPeeringDB, PeeringDBPeer)
- [x] Create PeeringDB exception classes
- [x] Create PeeringDB API client with tenacity retry logic
- [x] Create PeeringDB sync service with SyncResult tracking
- [x] Create management command: `sync_peeringdb` (--fabric, --ix-id, --discover-only)
- [x] Discover IX peers feature via PeeringDBPeer cache
- [x] UI for searching PeeringDB IXes and triggering sync
- [x] Create fabric from PeeringDB view
- [x] API serializers with nested PeeringDB info
- [x] Tests for PeeringDB client and sync service

### Phase 4: Session Security & Policy Enhancements ✅ COMPLETED

**Priority:** MEDIUM
**Estimated Effort:** Medium

**Tasks:**
- [x] Add `password` field to BGPSession (plain CharField for MD5 auth)
- [x] Add `weight` field to RoutingPolicy (for evaluation ordering)
- [x] Add `address_family` field to RoutingPolicy (IPv4/IPv6/null)
- [x] Enhanced Community validation (RFC-compliant: standard, large, extended formats)
- [x] Migrate PrefixList.family to NetBox core IPAddressFamilyChoices (integers 4/6)
- [x] Update forms, tables, filtersets, API serializers, GraphQL types

**Skipped (YAGNI):**
- Policy `type` (ingress/egress) - handled by M2M relationship names (import_policies, export_policies)
- Community `type` - usage context determines application

### Phase 5: Configuration Templating

**Priority:** MEDIUM
**Estimated Effort:** Medium-Large

**Tasks:**
- [ ] Create ConfigurationTemplate model (or use NetBox's)
- [ ] Implement Jinja2 rendering with BGP context
- [ ] Create template variables documentation
- [ ] Add custom Jinja2 filters for BGP
- [ ] Create API endpoint for config rendering
- [ ] Provide example templates (Junos, IOS-XR, EOS, Nokia)
- [ ] Management command for bulk rendering

### Phase 6: ASN Extensions

**Priority:** MEDIUM
**Estimated Effort:** Small-Medium

**Options to evaluate:**
1. **Custom Fields Approach:**
   - Add custom fields to ipam.ASN via plugin
   - Pros: No new models, leverages NetBox
   - Cons: Less control, migration complexity

2. **PeerASN Model Approach:**
   - Create PeerASN model referencing ipam.ASN
   - Add: affiliated, irr_as_set, max_prefixes
   - Pros: Full control, clean separation
   - Cons: Some duplication

**Tasks:**
- [ ] Evaluate approaches with user feedback
- [ ] Implement chosen approach
- [ ] Add UI for managing extended ASN data
- [ ] Integrate with PeeringDB sync

### Phase 7: Operational Monitoring (FUTURE)

**Priority:** LOW
**Estimated Effort:** Large

**Tasks:**
- [ ] Add NAPALM integration
- [ ] Create session state polling job
- [ ] Add `operational_state` field to BGPSession
- [ ] Add `last_state_change` timestamp
- [ ] Create monitoring dashboard view
- [ ] Add alerting/webhook triggers for state changes

---

## Architecture Decisions

### Decision 1: Separate IX Session Model vs Extended BGPSession

**Option A: Separate IXPeeringSession model**
- Pros: Clean separation, IX-specific fields, matches Peering Manager
- Cons: Code duplication, two places to look for sessions

**Option B: Extend BGPSession with optional IX fields**
- Pros: Single session model, simpler queries
- Cons: Nullable fields, less clear data model

**Recommendation:** Option A - Create separate `IXPeeringSession` model for clarity and to match established patterns in Peering Manager. Use abstract base class for shared functionality.

### Decision 2: ASN Extensions

**Recommendation:** Start with **PeerASN model** approach. This provides:
- Clean data model
- Full control over fields and behavior
- Easy PeeringDB sync target
- No dependency on NetBox custom field behavior

### Decision 3: Configuration Templates

**Recommendation:** Create plugin-specific `ConfigurationTemplate` model rather than using NetBox's config templates. Reasons:
- BGP-specific context variables
- Custom Jinja2 filters for routing policy rendering
- Independence from NetBox config context changes

---

## Dependencies and Prerequisites

### External Libraries
- `tenacity` - Retry logic for IRR queries and PeeringDB API ✅ Added
- `requests` - HTTP client for PeeringDB REST API (already in NetBox) ✅ Used
- `napalm` - Device connectivity (Phase 7)

### NetBox Version Requirements
- NetBox 4.4+ (current compatibility)
- Monitor for relevant upstream changes

---

## Success Metrics

1. **Feature Parity:** Cover 80%+ of Peering Manager's core functionality
2. **User Adoption:** Provide clear migration path from Peering Manager
3. **Integration Quality:** Seamless NetBox integration, no data duplication
4. **Documentation:** Complete user and developer documentation
5. **Test Coverage:** Maintain >80% test coverage

---

## References

- [Peering Manager Documentation](https://peering-manager.readthedocs.io/)
- [Peering Manager GitHub](https://github.com/peering-manager/peering-manager)
- [NetBox Plugin Development](https://docs.netbox.dev/en/stable/plugins/development/)
- [PeeringDB API](https://www.peeringdb.com/apidocs/)
