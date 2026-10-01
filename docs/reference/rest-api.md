# REST API

Everything the UI manages is available under:

```
/api/plugins/bgp/
```

The endpoints are standard NetBox model endpoints. Authentication,
pagination, `?brief=true`, bulk create / update / delete, tag and custom
field handling, and object permissions all work as described in the
[NetBox REST API documentation](https://netboxlabs.com/docs/netbox/integrations/rest-api/).
This page lists only what is specific to the plugin.

## Endpoints

| Endpoint | Model |
|----------|-------|
| `relationship/` | Relationship |
| `peer-asn/` | PeerASN |
| `peering-session/` | PeeringSession |
| `peering-fabric-type/` | PeeringFabricType |
| `peering-fabric/` | PeeringFabric |
| `peering-network/` | PeeringNetwork |
| `peering-connection/` | PeeringConnection |
| `irr-source/` | IRRSource |
| `irr-prefix-list-config/` | IRRPrefixListConfig |
| `render-config/` | Not a model. See [render-config](#render-config). |

Field meanings are on the [Models](../concepts/models.md) page.

## Filters

Every list endpoint accepts `q` for free-text search plus the standard
NetBox filters (`id`, `tag`, `created`, `last_updated`, ...). The
plugin-specific filters are:

| Endpoint | Filters | `q` searches |
|----------|---------|--------------|
| `relationship/` | `name`, `slug`, `description` | name, slug, description |
| `peer-asn/` | `asn_id`, `affiliated`, `irr_as_set`, `peeringdb_id` | AS number, ASN description, AS-SET |
| `peering-session/` | `bgp_peer_id`, `relationship_id`, `peering_network_id`, `service_reference` | BGP peer name, relationship name, network name, service reference |
| `peering-fabric-type/` | `name`, `slug`, `description` | name, slug, description |
| `peering-fabric/` | `name`, `slug`, `status`, `type_id`, `site_id`, `tenant_id`, `tenant`, `tenant_group_id`, `tenant_group` | name, slug, description |
| `peering-network/` | `name`, `fabric_id`, `status` | name, fabric name, description |
| `peering-connection/` | `peering_network_id`, `device_id`, `interface`, `status` | network name, interface name, description |
| `irr-source/` | `name`, `slug`, `url`, `enabled` | name, slug, description, URL |
| `irr-prefix-list-config/` | `prefix_list_id`, `irr_source_id`, `source_as_set` (substring match), `sync_interval` | prefix list name, AS-SET, IRR source name |

`status` takes `active`, `planned`, or `decommissioned` and can be
repeated to match several values.

```bash
# Sessions on one peering network
curl -H "Authorization: Token $NETBOX_TOKEN" \
  "https://netbox.example.com/api/plugins/bgp/peering-session/?peering_network_id=7"

# Your routers' attachments on a device
curl -H "Authorization: Token $NETBOX_TOKEN" \
  "https://netbox.example.com/api/plugins/bgp/peering-connection/?device_id=42"
```

## Things that differ from the UI

- **`irr-source/` names the fastbgpq4 URL `api_endpoint`.** In API
  responses `url` is, as everywhere in NetBox, the link to the object
  itself. Read and write the fastbgpq4 base URL through `api_endpoint`.
- **`peering-fabric/` exposes PeeringDB data read-only.** The `peeringdb`
  field returns the fabric's cached IX record, or null for an unlinked
  fabric. The link cannot be created or changed through the API; use the
  fabric edit form or the shell.
- **Sync operations are not exposed.** Neither PeeringDB sync nor IRR sync
  has an API action. Use the UI, the
  [management command](management-commands.md), or the shell snippets in
  [IRR prefix lists](../user-guide/irr-prefix-lists.md).
- **The PeeringDB peer cache has no endpoint.**

## Creating a peering session

Related objects are passed by ID. The BGP peer must already exist in
netbox-routing and must not already have a peering session.

```bash
curl -X POST https://netbox.example.com/api/plugins/bgp/peering-session/ \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "bgp_peer": 118,
        "relationship": 3,
        "peering_network": 7,
        "service_reference": "NOC-12345"
      }'
```

`relationship` and `peering_network` are optional and accept `null`.

## render-config

```
POST /api/plugins/bgp/render-config/
```

Renders a NetBox Config Template against the peering context of a device
or of specific sessions. The context is described in
[Configuration templating](../user-guide/configuration-templating.md#the-context).

### Request body

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `template` | int | Yes | ID of the `ConfigTemplate` to render. |
| `device` | int or null | One of `device` / `sessions` | ID of a device. |
| `sessions` | list of int | One of `device` / `sessions` | IDs of peering sessions. |

How the two combine is described under
[which sessions are rendered](../user-guide/configuration-templating.md#which-sessions-are-rendered).

### Query parameters

| Parameter | Effect |
|-----------|--------|
| `include_context=true` | Adds the template context to a JSON response under `context`. |

### Response

The format follows the `Accept` header.

`Accept: application/json` (default):

```json
{
  "configtemplate": {"id": 7, "url": "...", "display": "junos-bgp", "name": "junos-bgp"},
  "content": "protocols {\n    bgp {\n ...",
  "device": {"id": 42, "name": "rt1.mtl"},
  "session_count": 12
}
```

`device` is present only when a device was given. The nested
`configtemplate` object is NetBox's brief representation and may carry
additional fields depending on the NetBox version.

`Accept: text/plain`: the rendered configuration as the raw response body,
with no metadata.

### Errors

| Status | When |
|--------|------|
| 400 | Invalid body: unknown template, device, or session ID, or neither `device` nor `sessions` given. |
| 403 | Missing or invalid credentials. |
| 500 | The template failed to render. The message is under `detail`, or is the plain body for `text/plain`. |

### Access control

The endpoint requires an authenticated request and nothing more: it does
not evaluate NetBox object permissions on the template, the device, or the
sessions. Rendered output and the `include_context` dump contain BGP
passwords. Issue API tokens accordingly.

## GraphQL

Each model also has a single-object and a list query on the NetBox GraphQL
endpoint, named `netbox_peering_manager_<model>` and
`netbox_peering_manager_<model>_list`:

```graphql
{
  netbox_peering_manager_peering_session_list {
    id
    service_reference
    relationship { name }
    peering_network { name fabric { name } }
  }
}
```

Available model names: `relationship`, `peer_asn`, `peering_session`,
`peering_fabric_type`, `peering_fabric`, `peering_network`,
`peering_connection`, `irr_source`, `irr_prefix_list_config`. See the
[NetBox GraphQL documentation](https://netboxlabs.com/docs/netbox/integrations/graphql-api/)
for querying and filtering conventions.
