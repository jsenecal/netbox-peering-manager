# Jinja2 filters

The plugin registers five filters with NetBox's Jinja2 environment when it
loads. They are available in Config Templates and in any other template
NetBox renders, not only in requests made through the plugin's
render endpoint.

| Filter | Purpose |
|--------|---------|
| [`as_path_regex`](#as_path_regex) | AS number to an AS-path regular expression. |
| [`ip_network`](#ip_network) | CIDR string to network address, prefix length, and netmask. |
| [`group_by`](#group_by) | Group a list by an attribute, keeping input order. |
| [`to_community_list`](#to_community_list) | Community value to a community list statement. |
| [`to_prefix_set`](#to_prefix_set) | Prefix entries to a prefix list block. |

Filters that produce device syntax take a `vendor` argument. Two values
are recognized: `"cisco"` (the default) and `"junos"`. **Any other value
falls back to Cisco syntax**, so pass the vendor explicitly rather than
feeding a platform slug straight in.

## as_path_regex

```
as_path_regex(asn, vendor="cisco")
```

Returns a regular expression matching AS paths that start with `asn`.

| Input | Output |
|-------|--------|
| `{{ 64512 | as_path_regex }}` | `^64512_` |
| `{{ 64512 | as_path_regex("junos") }}` | `^64512 ` (with a trailing space) |

## ip_network

```
ip_network(prefix)
```

Parses a CIDR string and returns a dict with `network`, `prefix_length`,
and `netmask`. Host bits are allowed and ignored.

| Input | Output |
|-------|--------|
| `{{ "198.51.100.17/24" | ip_network }}` | `{"network": "198.51.100.0", "prefix_length": 24, "netmask": "255.255.255.0"}` |
| `{{ ("2001:db8::1/48" | ip_network).prefix_length }}` | `48` |

Useful for platforms that want an address and mask instead of CIDR:

```jinja
{% set net = "198.51.100.0/24" | ip_network %}
network {{ net.network }} mask {{ net.netmask }}
```

An invalid prefix raises an error and fails the render.

## group_by

```
group_by(items, attr)
```

Groups a list of dicts or objects by a key or attribute and yields
`(value, items)` pairs. Groups appear in the order their value is first
seen, unlike Jinja's built-in `groupby`, which sorts. Items missing the
attribute are grouped under `None`.

```jinja
{% for relationship, group in sessions | group_by("relationship") %}
! {{ relationship or "unclassified" }}: {{ group | length }} sessions
{% endfor %}
```

## to_community_list

```
to_community_list(value, name, vendor="cisco")
```

Renders one community value as a named community list.

`{{ "64500:100" | to_community_list("CL-PEERS") }}`:

```
ip community-list standard CL-PEERS permit 64500:100
```

`{{ "64500:100" | to_community_list("CL-PEERS", "junos") }}`:

```
policy-options {
    community CL-PEERS members 64500:100;
}
```

The Cisco form always emits a `standard` list with a `permit` action. The
value is inserted as given and is not validated.

## to_prefix_set

```
to_prefix_set(prefixes, name, vendor="cisco")
```

Renders a list of prefix entries as a named prefix list. Each entry is a
dict with a `prefix` key and optional `ge` and `le` keys. An empty list
returns an empty string.

Given:

```jinja
{% set entries = [
  {"prefix": "192.0.2.0/24"},
  {"prefix": "198.51.100.0/22", "le": 24},
  {"prefix": "203.0.113.0/24", "ge": 25, "le": 28},
] %}
```

`{{ entries | to_prefix_set("PL-AS64512") }}`:

```
ip prefix-list PL-AS64512 seq 10 permit 192.0.2.0/24
ip prefix-list PL-AS64512 seq 20 permit 198.51.100.0/22 le 24
ip prefix-list PL-AS64512 seq 30 permit 203.0.113.0/24 ge 25 le 28
```

`{{ entries | to_prefix_set("PL-AS64512", "junos") }}`:

```
policy-options {
    prefix-list PL-AS64512 {
        192.0.2.0/24;
        198.51.100.0/22 upto /24;
        203.0.113.0/24 prefix-length-range /25-/28;
    }
}
```

Limitations to be aware of:

- The Cisco form always emits `ip prefix-list` with `permit` entries,
  numbered in steps of 10. It does not switch to `ipv6 prefix-list` for
  IPv6 prefixes.
- In the Junos form, an entry with `ge` but no `le` is rendered with an
  upper bound of `/32`. For IPv6 prefixes always give an explicit `le`.
- The render context does not include prefix list entries (see
  [Configuration templating](../user-guide/configuration-templating.md#the-context)),
  so the input list has to come from elsewhere in your template or
  context data.

## Overriding a filter

On NetBox 4.7 and later the filters are registered through NetBox's plugin
filter registry, which ranks below the instance-level `JINJA_FILTERS`
setting. Defining a filter of the same name there replaces the plugin's
version. On NetBox 4.5 and 4.6 the plugin writes its filters into the
filter setting directly at startup and takes precedence.
