# Configuration templating

The plugin turns your peering data into device configuration by combining
two things:

- A NetBox **Config Template** that you write in Jinja2.
- A **context** the plugin builds for one device: every peering session on
  it, flattened into plain dictionaries that are easy to loop over.

Templates are stored in core NetBox (**Provisioning &rarr; Config
Templates**), so they get NetBox's change logging, data source sync, and
permissions. The plugin adds the context builder, a rendering endpoint,
and a few [Jinja2 filters](../reference/jinja2-filters.md).

## Quick start

1. Create a Config Template. Start from one of the
   [example templates](https://github.com/jsenecal/netbox-peering-manager/tree/main/docs/examples/templates)
   for Junos, IOS-XR, EOS, or SR OS and paste it into the template body.
2. Note the template ID and the device ID.
3. Render:

```bash
curl -X POST https://netbox.example.com/api/plugins/bgp/render-config/ \
  -H "Authorization: Token $NETBOX_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: text/plain" \
  -d '{"template": 7, "device": 42}'
```

With `Accept: text/plain` the response body is the rendered configuration
and nothing else, ready to pipe into a file or a deployment tool.

Rendering is available through the REST API only; there is no render
button in the UI. The JSON response format, errors, and access control
are in the [REST API reference](../reference/rest-api.md#render-config).

## Which sessions are rendered

| Request | Sessions in the context |
|---------|-------------------------|
| `device` only | Every peering session whose BGP peer belongs to a BGP router assigned to that device. |
| `sessions` only | Exactly the listed peering sessions. `device` in the context is null. |
| Both | Exactly the listed sessions, with the device details filled in. |

Only BGP peers wrapped in a `PeeringSession` are included. A netbox-routing
peer without a peering session is invisible to this renderer.

## The context

A template receives these top-level variables:

| Variable | Type | Content |
|----------|------|---------|
| `device` | dict or null | `id`, `name`, `platform` (`name`, `slug`), `site` (`name`, `slug`). `platform` and `site` are null when unset. |
| `sessions` | list | One dict per peering session, described below. |
| `peer_groups` | list | Each distinct peer template used by the sessions: `id`, `name`. |
| `route_maps` | list | Each distinct route map used by the sessions' address families: `id`, `name`. |
| `prefix_lists` | list | Always empty. Reserved. |
| `communities` | list | Always empty. Reserved. |

Each entry of `sessions`:

| Field | Type | Source |
|-------|------|--------|
| `id` | int | Peering session ID. |
| `name`, `description` | str | BGP peer. |
| `status` | str | BGP peer status. |
| `enabled` | bool | BGP peer. |
| `local_asn`, `peer_asn` | int or null | AS numbers of the peer's local and remote AS. |
| `local_ip`, `remote_ip` | str or null | Source and peer address, without the mask. |
| `password` | str | BGP peer password, empty string when unset. |
| `ttl` | int or null | BGP peer TTL. |
| `relationship` | str or null | Relationship name. |
| `service_reference` | str | Peering session. |
| `peer_name` | str or null | From the remote AS: its description, or `AS<number>`. |
| `irr_as_set` | str or null | From the remote AS's `PeerASN`. Null when there is none. |
| `ipv4_max_prefixes`, `ipv6_max_prefixes` | int or null | From the remote AS's `PeerASN`. Null when there is none. |
| `bfd_profile` | dict or null | `name`, `minimum_interval`, `minimum_rx_interval`, `multiplier`, `hold`. |
| `peer_group` | dict or null | `id`, `name` of the peer template. |
| `peering_network` | dict or null | `id`, `name`, `fabric` (the fabric name). |
| `address_families` | list | One dict per peer address family: `afi`, plus `route_map_in`, `route_map_out`, `prefix_list_in`, `prefix_list_out` when set, each as `{"name": ...}`. |
| `afi_safis` | list | `["ipv4-unicast"]` or `["ipv6-unicast"]`, derived from the local address version. Empty when the peer has no source address. |

Three behaviors to design templates around:

- **Policy objects are referenced by name only.** Route map and prefix
  list contents are not in the context. A template emits
  `import-policy {{ af.route_map_in.name }}` and relies on the policy
  being defined elsewhere in the device configuration.
- **Max-prefix and AS-SET come from `PeerASN`.** Create a `PeerASN` for the
  remote AS, or those fields are null.
- **Disabled peers are included.** Filter on `session.enabled` in the
  template if you do not want them rendered.

## Seeing the context

Add `?include_context=true` to a JSON request and the response carries the
exact context the template saw. This is the fastest way to find out why a
template prints nothing: check whether `sessions` is empty before
debugging the Jinja.

## A minimal template

```jinja
{% for session in sessions if session.enabled %}
neighbor {{ session.remote_ip }}
  remote-as {{ session.peer_asn }}
  description {{ session.peer_name }} [{{ session.relationship or "unclassified" }}]
{%- if session.ipv4_max_prefixes and "ipv4-unicast" in session.afi_safis %}
  maximum-prefix {{ session.ipv4_max_prefixes }}
{%- endif %}
{%- for af in session.address_families if af.prefix_list_in %}
  prefix-list {{ af.prefix_list_in.name }} in
{%- endfor %}
{% endfor %}
```

The example templates in the repository show complete per-vendor
structure, including BFD, peer groups, and authentication.

## Handling secrets

The `password` field holds the BGP password in clear text, so rendered
output is sensitive. Who can call the endpoint is covered under
[access control](../reference/rest-api.md#access-control).

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| `session_count` is 0 for a device | The device has no netbox-routing BGP router, or its peers have no peering sessions. |
| A plugin filter is reported as unknown | The plugin is not loaded in the process that rendered. |

HTTP error responses are listed in the
[REST API reference](../reference/rest-api.md#errors).
