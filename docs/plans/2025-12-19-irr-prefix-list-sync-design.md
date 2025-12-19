# IRR Prefix List Sync Design

## Overview

Automatically generate PrefixList/PrefixListRule entries from AS-SETs by integrating with fastbgpq4, a FastAPI service that wraps bgpq4 for IRR queries.

**Goal:** Allow users to define a PrefixList backed by an AS-SET (e.g., "AS-HURRICANE"), with automatic synchronization of prefix rules from IRR data.

**Architecture:** PrefixList gains optional AS-SET source field. Background jobs periodically sync rules from fastbgpq4. Manual sync trigger available via UI.

**Tech Stack:** NetBox Job Framework, fastbgpq4 API, httpx for async HTTP

---

## Data Model

### New Model: IRRSource

Stores fastbgpq4 connection configuration:

```python
class IRRSource(NetBoxModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    url = models.URLField(help_text="fastbgpq4 API URL")
    sources = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated IRR sources (e.g., RIPE,RADB,ARIN)"
    )
    cache_ttl = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Override default cache TTL in seconds"
    )
    sync_interval = models.PositiveIntegerField(
        default=1440,
        help_text="Minutes between automatic syncs"
    )
    enabled = models.BooleanField(default=True)
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)
```

### PrefixList Additions

```python
# Add to existing PrefixList model
source_as_set = models.CharField(
    max_length=100,
    blank=True,
    help_text="AS-SET to sync from IRR (e.g., AS-HURRICANE)"
)
irr_source = models.ForeignKey(
    'IRRSource',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='prefix_lists'
)
```

**Behavior:**
- When `source_as_set` is populated, the PrefixList becomes IRR-managed
- The existing `family` field (ipv4/ipv6/both) controls which prefixes are fetched
- IRR-managed lists are fully replaced on sync (no manual rules mixed in)

---

## Sync Job & Workflow

### Background Job: SyncPrefixListFromIRR

Registered with NetBox's job framework:

```python
class SyncPrefixListFromIRR(Job):
    prefix_list = ObjectVar(model=PrefixList)

    class Meta:
        name = "Sync Prefix List from IRR"

    def run(self, data, commit):
        prefix_list = data['prefix_list']
        irr_source = prefix_list.irr_source

        # 1. Build fastbgpq4 request
        # 2. Call API, handle async response if needed
        # 3. Delete existing PrefixListRules
        # 4. Create new rules from IRR response
        # 5. Log results
```

### Periodic Sync Job: SyncAllIRRPrefixLists

Scheduled job that syncs all IRR-backed PrefixLists:

- Groups by IRRSource for efficiency
- Respects `irr_source.sync_interval` (skips if not due)
- Skips disabled IRRSources (`enabled = False`)
- Handles fastbgpq4 async responses (polls job endpoint)

### Manual Trigger

- Button on PrefixList detail view: "Sync from IRR"
- Enqueues `SyncPrefixListFromIRR` job immediately
- User sees job status in NetBox's job results

### fastbgpq4 Integration

```python
import httpx

async def fetch_prefixes(irr_source: IRRSource, as_set: str, family: str):
    params = {
        "target": as_set,
        "format": "json",
    }
    if irr_source.sources:
        params["sources"] = irr_source.sources
    if irr_source.cache_ttl:
        params["cache_ttl"] = irr_source.cache_ttl

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{irr_source.url}/api/v1/as-set/expand",
            params=params,
            timeout=30.0
        )

        if response.status_code == 202:
            # Async mode - poll for results
            job_data = response.json()
            return await poll_job(client, irr_source.url, job_data["job_id"])

        return response.json()["data"]
```

---

## UI & API

### IRRSource Views

- List, detail, edit, delete, bulk operations
- Navigation: Add under existing "Policies" menu group
- Table columns: name, url, sources, sync_interval, enabled

### PrefixList Enhancements

**Detail View:**
- Show IRR status badge when `source_as_set` is set
- "Sync from IRR" button (triggers job)
- Link to related job history

**Form:**
- Add `source_as_set` and `irr_source` fields
- Help text explaining IRR-managed behavior
- Validation: `source_as_set` requires `irr_source` (and vice versa)

**Table:**
- Add `source_as_set` column, filterable

### Visual Indicators

```
PrefixList: "AS-HURRICANE-Filters"
├── Source AS-SET: AS-HURRICANE [IRR-managed badge]
├── IRR Source: Primary IRR
├── Family: both
├── Rules: 1,247 prefixes
└── [Sync from IRR] button
```

### API Additions

- `IRRSourceSerializer`, `IRRSourceViewSet`
- Endpoint: `/api/plugins/netbox_peering_manager/irr-source/`
- `PrefixListSerializer`: Add `source_as_set`, `irr_source` fields
- Custom action: `POST /api/plugins/netbox_peering_manager/prefix-list/{id}/sync/`

### GraphQL

- `IRRSourceType` with filters
- Update `PrefixListType` with `source_as_set`, `irr_source` fields

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| fastbgpq4 unreachable | Job fails, logs error, existing rules preserved |
| AS-SET not found in IRR | Job fails with "AS-SET not found", rules preserved |
| Empty result (no prefixes) | Delete all rules, log warning |
| fastbgpq4 returns async (202) | Poll job endpoint until complete, with timeout |
| Invalid IRRSource URL | Validation error on save |

### PrefixListRule Generation

```python
# From fastbgpq4 JSON response: {"nn": ["192.0.2.0/24", "198.51.100.0/24", ...]}
for index, prefix in enumerate(prefixes):
    PrefixListRule.objects.create(
        prefix_list=prefix_list,
        index=index * 10,  # Leave gaps
        action="permit",
        prefix_custom=prefix,  # Use prefix_custom, not FK
    )
```

---

## Plugin Settings

```python
# In plugin configuration
PLUGIN_SETTINGS = {
    'irr_sync_timeout': 300,      # Max seconds to wait for fastbgpq4
    'irr_poll_interval': 2,       # Seconds between async polls
    'irr_default_sync_interval': 1440,  # Default minutes between syncs
}
```

---

## Validation Rules

1. `source_as_set` requires `irr_source` to be set
2. `irr_source` without `source_as_set` is allowed (for future use)
3. Warn in UI if manually editing rules on IRR-managed PrefixList
4. AS-SET format validation (basic pattern match)

---

## Files to Create/Modify

**New Files:**
- `netbox_peering_manager/models/irr_source.py` - IRRSource model
- `netbox_peering_manager/jobs.py` - Sync jobs
- `netbox_peering_manager/irr_client.py` - fastbgpq4 API client
- Templates for IRRSource views

**Modified Files:**
- `netbox_peering_manager/models.py` - Add fields to PrefixList
- `netbox_peering_manager/forms.py` - IRRSource forms, update PrefixList form
- `netbox_peering_manager/tables.py` - IRRSource table, update PrefixList table
- `netbox_peering_manager/views.py` - IRRSource views, sync action
- `netbox_peering_manager/filtersets.py` - IRRSource filterset
- `netbox_peering_manager/api/serializers.py` - IRRSource serializer
- `netbox_peering_manager/api/views.py` - IRRSource viewset, sync action
- `netbox_peering_manager/api/urls.py` - Register routes
- `netbox_peering_manager/graphql/` - Types, filters, schema
- `netbox_peering_manager/navigation.py` - Add menu item
- `netbox_peering_manager/migrations/` - New migration

---

## Dependencies

- `httpx` - Async HTTP client for fastbgpq4 API calls
- fastbgpq4 service running and accessible

---

## Success Criteria

1. User can create IRRSource pointing to fastbgpq4 instance
2. User can create PrefixList with `source_as_set` and `irr_source`
3. Manual sync populates PrefixListRules from IRR data
4. Background job syncs all IRR-backed PrefixLists on schedule
5. Job history visible in NetBox UI
6. API supports all operations including sync trigger
