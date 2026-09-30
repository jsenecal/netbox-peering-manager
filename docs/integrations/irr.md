# IRR / fastbgpq4

The plugin does not query Internet Routing Registries itself. It delegates
to [fastbgpq4](https://github.com/jsenecal/fastbgpq4), a REST service
wrapping [bgpq4](https://github.com/bgp/bgpq4). This page describes that
contract. For the operator workflow, see
[IRR prefix lists](../user-guide/irr-prefix-lists.md).

## Why a separate service

bgpq4 is a command-line tool, not a library. Running it behind a small
HTTP service keeps bgpq4 off the NetBox hosts, adds result caching, lets
large AS-SET expansions run asynchronously, and centralizes IRR queries in
one place.

## Deployment requirements

- fastbgpq4 must be reachable over HTTP from the **NetBox RQ worker**.
  The web process never calls it.
- The plugin sends no credentials. Put fastbgpq4 on a private network or
  behind a gateway that restricts access by source address.
- Each `IRRSource` row holds the base URL of one fastbgpq4 instance. A
  trailing slash is ignored.

## Request

For each address family, the client issues:

```
GET <irr_source.url>/api/v1/as-set/expand
```

| Query parameter | Value |
|-----------------|-------|
| `target` | The config's source AS-SET. |
| `format` | `json` |
| `protocol` | `4` or `6`. |
| `sources` | The source's registry list, only when set. |
| `cache_ttl` | The source's cache TTL, only when set. |

The address family comes from the netbox-routing prefix list being
synced, so one sync of one prefix list is one expansion request.

## Response

fastbgpq4 can answer in two ways, and the client handles both.

**Immediate (HTTP 200).** The prefixes are in the body:

```json
{"data": {"nn": ["192.0.2.0/24", "198.51.100.0/24"]}}
```

**Deferred (HTTP 202).** The body carries a `job_id`. The client then
polls:

```
GET <irr_source.url>/api/v1/jobs/<job_id>
```

until the job reports `status` of `completed` (prefixes under `data`) or
`failed` (message under `error`), or until the poll limit below is
reached.

## Timeouts and retries

| Setting | Value |
|---------|-------|
| HTTP timeout | 30 seconds per request |
| Retries | Up to 3 attempts on connection errors and timeouts, with exponential backoff between 1 and 10 seconds |
| Poll interval | 2 seconds |
| Poll limit | 150 polls, about five minutes |

These are fixed in `netbox_peering_manager.irr_client` and are not
configurable through plugin settings.

## Failure behavior

Any failure aborts the sync of that prefix list **before** its entries are
touched, so a failed sync never leaves a prefix list half written.

| Situation | Result |
|-----------|--------|
| Connection refused, DNS failure, timeout | Retried, then the job fails. |
| HTTP 4xx or 5xx from fastbgpq4 | The job fails. |
| Deferred job reports `failed` | The job fails with the fastbgpq4 error message. |
| Deferred job never completes | The job fails after the poll limit. |
| AS-SET expands to nothing | The job succeeds and the prefix list ends up empty. |

The last row deserves attention. An AS-SET that was deleted from the
registry, or a typo in its name, can legitimately expand to zero prefixes,
and the prefix list is emptied accordingly. If a managed prefix list is
used as an inbound filter, review job results after changing an AS-SET
name.

## What is written to netbox-routing

The returned prefixes replace the entries of the managed prefix list. The
details are under
[netbox-routing integration](netbox-routing.md#objects-written).
