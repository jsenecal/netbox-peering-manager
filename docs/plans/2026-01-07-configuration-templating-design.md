# Configuration Templating Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add BGP configuration templating using NetBox's existing ConfigTemplate model with custom Jinja2 filters and a render endpoint.

**Architecture:** Leverage NetBox's `extras.ConfigTemplate` for template storage and rendering. Add a plugin render endpoint that builds BGP-specific context (device, sessions, policies) and passes it to templates. Provide custom Jinja2 filters for vendor-specific syntax generation.

**Tech Stack:** NetBox ConfigTemplate, Jinja2, Django REST Framework

---

## Design Decisions

### 1. Template Storage
**Decision:** Use NetBox's existing `extras.ConfigTemplate` model.

**Rationale:**
- No new models needed
- Users familiar with NetBox config templates
- Inherits NetBox's template management UI
- Supports data sources, sync, versioning

### 2. Template Association
**Decision:** No model associations - template passed to render endpoint at runtime.

**Rationale:**
- Maximum flexibility
- No migrations needed
- User chooses template at render time
- Supports multiple templates per device

### 3. Context Structure
**Decision:** Rich, denormalized context with all BGP objects.

```python
{
    "device": {
        "id": 456,
        "name": "router1",
        "platform": {"name": "junos", "slug": "junos"},
        "site": {"name": "Frankfurt", "slug": "fra"},
    },
    "sessions": [
        {
            "id": 1,
            "name": "Peer-AS65001",
            "peer_asn": 65001,
            "local_ip": "192.0.2.1",
            "remote_ip": "192.0.2.2",
            "status": "active",
            "enabled": True,
            "relationship": "peer",
            "password": "secret123",
            "multihop_ttl": 2,
            "bfd_profile": {"name": "fast", "interval": 100, "multiplier": 3},
            "peer_group": {"name": "PEERS", ...},
            "peering_network": {"name": "DE-CIX Frankfurt", ...},
            "import_policies": [{"name": "IMPORT-PEER", "weight": 100, ...}],
            "export_policies": [{"name": "EXPORT-PEER", "weight": 100, ...}],
            "afi_safis": ["ipv4-unicast", "ipv6-unicast"],
        },
    ],
    "peer_groups": [...],
    "routing_policies": [...],
    "prefix_lists": [...],
    "communities": [...],
}
```

### 4. Custom Jinja2 Filters
**Decision:** Add BGP-specific filters registered via PluginConfig.

**Filters:**
- `as_path_regex(vendor)` - Convert ASN to AS-path regex
- `to_prefix_set(vendor)` - Convert PrefixList to vendor syntax
- `to_community_list(vendor)` - Convert Community to vendor syntax
- `group_by(attr)` - Group objects by attribute
- `ip_network` - Parse prefix into network/mask components

### 5. API Endpoint
**Decision:** Plugin endpoint following NetBox's `ConfigTemplateRenderMixin` pattern.

```
POST /api/plugins/peering-manager/render-config/
```

**Request:**
```json
{
    "template": 123,
    "device": 456,
    "sessions": [1, 2, 3]
}
```

- If only `device`: all sessions for that device
- If only `sessions`: those specific sessions
- If both: sessions filtered to that device

**Query params:**
- `?include_context=true` - Include context in response

**Response (follows NetBox pattern):**
```json
{
    "configtemplate": {
        "id": 123,
        "name": "junos-bgp",
        "url": "/api/extras/config-templates/123/"
    },
    "content": "router bgp 65000\n...",
    "device": {"id": 456, "name": "router1"},
    "session_count": 5
}
```

With `?include_context=true`:
```json
{
    "configtemplate": {...},
    "content": "...",
    "context": {
        "device": {...},
        "sessions": [...],
        ...
    }
}
```

**Error responses:**
- 400 - Missing template, or neither device nor sessions provided
- 404 - Template/device/session not found
- 500 - Template render error (with error details)

### 6. Example Templates
**Decision:** Provide examples in documentation, not as fixtures.

**Location:** `docs/examples/templates/`

**Platforms:**
- `junos-bgp.j2` - Juniper Junos
- `ios-xr-bgp.j2` - Cisco IOS-XR
- `eos-bgp.j2` - Arista EOS
- `nokia-sros-bgp.j2` - Nokia SR OS

---

## Component Structure

```
netbox_peering_manager/
├── services/
│   └── config_renderer.py      # Context builder + render logic
├── templatetags/
│   └── peering_filters.py      # Custom Jinja2 filters
├── api/
│   ├── views.py                # Add RenderConfigView
│   └── urls.py                 # Add render-config/ endpoint

docs/examples/templates/
├── junos-bgp.j2
├── ios-xr-bgp.j2
├── eos-bgp.j2
└── nokia-sros-bgp.j2
```

---

## Implementation Tasks

1. Create `services/config_renderer.py` with `ConfigRenderer` class
2. Create `templatetags/peering_filters.py` with custom filters
3. Register filters in `PluginConfig.jinja2_filters`
4. Create `RenderConfigView` API endpoint
5. Add URL route for `/render-config/`
6. Create request serializer for validation
7. Write tests for context builder
8. Write tests for custom filters
9. Write tests for render endpoint
10. Create example templates in docs
11. Update documentation

---

## Dependencies

- NetBox 4.4+ (ConfigTemplate model)
- No new external libraries required

---

## References

- [NetBox ConfigTemplate](https://docs.netbox.dev/en/stable/models/extras/configtemplate/)
- [NetBox API mixins](https://github.com/netbox-community/netbox/blob/develop/netbox/extras/api/mixins.py)
