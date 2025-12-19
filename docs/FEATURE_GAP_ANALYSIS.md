# Feature Gap Analysis: netbox-peering-manager vs Peering Manager

This document provides a comprehensive comparison between the [original Peering Manager](https://github.com/peering-manager/peering-manager) project and the netbox-peering-manager NetBox plugin, identifying feature gaps and proposing a phased implementation roadmap.

## Executive Summary

netbox-peering-manager is a NetBox plugin that leverages NetBox's existing infrastructure (devices, sites, ASNs, IP addresses, tenants) while adding BGP-specific functionality. The original Peering Manager is a standalone application with its own data models for everything.

**Key Advantage of netbox-peering-manager:** Tight integration with NetBox eliminates data duplication and provides a single source of truth for network infrastructure.

**Key Gaps:** Internet Exchange management, PeeringDB integration, configuration templating, and session state monitoring.

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
| MD5 Password | ✅ | ❌ Missing | 🔴 Gap |
| Service Reference | ✅ | ✅ | ✅ Implemented |
| Enabled Flag | ✅ | ✅ | ✅ Implemented |
| **Internet Exchanges** |
| IX Model | ✅ | ❌ Missing | 🔴 Gap |
| IX Connections | ✅ | ❌ Missing | 🔴 Gap |
| IX Peering LAN | ✅ | ❌ Missing | 🔴 Gap |
| **Routing Policy** |
| Basic Policies | ✅ | ✅ | ✅ Equivalent |
| Policy Rules | ✅ | ✅ | ✅ Equivalent |
| Policy Type (in/out) | ✅ | ❌ Missing | 🟡 Enhancement |
| Policy Weight | ✅ | ❌ Missing | 🟡 Enhancement |
| Address Family | ✅ | ❌ Missing | 🟡 Enhancement |
| **BGP Communities** |
| Basic Communities | ✅ | ✅ | ✅ Equivalent |
| Community Lists | ✅ | ✅ | ✅ Equivalent |
| Community Type | ✅ ingress/egress | ❌ Missing | 🟡 Enhancement |
| Value Validation | ✅ RFC format | ❌ Basic regex | 🟡 Enhancement |
| **Prefix Lists** |
| Basic Prefix Lists | ✅ | ✅ | ✅ Equivalent |
| Prefix List Rules | ✅ | ✅ | ✅ Equivalent |
| **AS Path Lists** |
| Basic AS Path Lists | ✅ | ✅ | ✅ Equivalent |
| AS Path Rules | ✅ | ✅ | ✅ Equivalent |
| **Peer Groups** |
| Basic Peer Groups | ✅ BGPGroup | ✅ BGPPeerGroup | ✅ Equivalent |
| **External Integrations** |
| PeeringDB Sync | ✅ Full | ❌ Missing | 🔴 Gap |
| IRR Integration | ✅ | ❌ Missing | 🔴 Gap |
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

### 1. Internet Exchange Management (HIGH PRIORITY)

**Current State:** No IX-specific models exist.

**Peering Manager Features:**
- `InternetExchange` model with name, slug, status, PeeringDB ID, local AS
- `Connection` model for IX port details (VLAN, MAC, IPv4/IPv6, router, interface)
- `InternetExchangePeeringSession` for IX-based BGP sessions
- Route server session support

**Required Implementation:**

```
InternetExchange
├── name, slug, status
├── local_as (FK to ipam.ASN)
├── peeringdb_id
├── import_policies, export_policies
└── comments, tags

IXConnection
├── internet_exchange (FK)
├── router (FK to dcim.Device)
├── interface (FK to dcim.Interface)
├── vlan (int)
├── mac_address
├── ipv4_address, ipv6_address (FK to ipam.IPAddress)
└── status

IXPeeringSession (extends BGPSession or separate)
├── internet_exchange (FK)
├── connection (FK to IXConnection)
├── is_route_server (bool)
└── ... standard session fields
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

### 3. PeeringDB Integration (HIGH PRIORITY)

**Current State:** No PeeringDB integration.

**Required Features:**
- Sync AS information (name, IRR AS-SET, max prefixes)
- Discover available peers at IXes
- Import IX information and peering LANs
- Periodic sync via background jobs

**Implementation Approach:**
- Use `peeringdb` Python library
- Create management commands for sync
- Add background job support (NetBox's job framework)
- Store PeeringDB IDs on relevant models

### 4. MD5 Password Support (MEDIUM PRIORITY)

**Current State:** No password field on BGPSession.

**Required:**
- `password` field (encrypted storage)
- Support for both plaintext and encrypted formats
- Integration with NetBox's secrets framework or custom encryption

### 5. Routing Policy Enhancements (LOW PRIORITY)

**Current State:** Basic name/description only.

**Missing Fields:**
- `type` - ingress or egress
- `weight` - Evaluation order (higher = first)
- `address_family` - IPv4, IPv6, or both

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

### Phase 2: Internet Exchange Support

**Priority:** HIGH
**Estimated Effort:** Large

**Models to create:**
1. `InternetExchange` - IX definition
2. `IXConnection` - Physical/logical connection to IX
3. `IXPeeringSession` - BGP session over IX (or extend BGPSession)

**Tasks:**
- [ ] Design and create InternetExchange model
- [ ] Design and create IXConnection model
- [ ] Decide: separate IXPeeringSession vs extending BGPSession
- [ ] Create forms, tables, filtersets, views
- [ ] Create API serializers and viewsets
- [ ] Create GraphQL types
- [ ] Add navigation menu items
- [ ] Create migrations
- [ ] Add initializer support
- [ ] Write tests

### Phase 3: PeeringDB Integration

**Priority:** HIGH
**Estimated Effort:** Medium

**Tasks:**
- [ ] Add peeringdb library dependency
- [ ] Create PeeringDB sync service
- [ ] Add `peeringdb_id` field to InternetExchange
- [ ] Create management command: `sync_peeringdb`
- [ ] Add background job for periodic sync
- [ ] Sync AS information to custom fields or PeerASN model
- [ ] Discover IX peers feature
- [ ] UI for triggering sync and viewing status

### Phase 4: Session Security & Policy Enhancements

**Priority:** MEDIUM
**Estimated Effort:** Medium

**Tasks:**
- [ ] Add `password` field to BGPSession (encrypted)
- [ ] Add `type` (ingress/egress) to RoutingPolicy
- [ ] Add `weight` to RoutingPolicy
- [ ] Add `address_family` to RoutingPolicy
- [ ] Add `type` to Community
- [ ] Enhance community value validation (RFC formats)
- [ ] Update forms and API

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

### External Libraries to Add
- `peeringdb` - PeeringDB API client
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
