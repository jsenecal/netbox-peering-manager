# Contributing

Contributions are welcome through pull requests against
[jsenecal/netbox-peering-manager](https://github.com/jsenecal/netbox-peering-manager).
This page covers what a change needs in order to pass review and CI.

## Development environment

The repository ships a VS Code devcontainer with NetBox, netbox-routing,
and this plugin installed in editable mode. Setup steps and the full list
of `make` targets are in the
[README](https://github.com/jsenecal/netbox-peering-manager#development).

Changes that would require modifying netbox-routing belong upstream in
[netbox-routing](https://github.com/DanSheps/netbox-routing). This plugin
builds on its models and does not patch them.

## Project layout

| Path | Contents |
|------|----------|
| `netbox_peering_manager/models.py` | All models. |
| `netbox_peering_manager/services/` | PeeringDB client, PeeringDB sync, configuration context builder. |
| `netbox_peering_manager/irr_client.py`, `jobs.py` | fastbgpq4 client and the IRR sync jobs. |
| `netbox_peering_manager/jinja2_filters.py` | Template filters. |
| `netbox_peering_manager/api/`, `graphql/` | REST and GraphQL surfaces. |
| `netbox_peering_manager/forms.py`, `tables.py`, `views.py`, `filtersets.py`, `navigation.py` | UI. |
| `netbox_peering_manager/management/commands/` | `manage.py` commands. |
| `netbox_peering_manager/tests/` | Test suite. |
| `docs/` | This site. |

## Running the tests

Tests need a working NetBox checkout with PostgreSQL and Redis, which the
devcontainer provides. CI runs them with pytest:

```bash
cd /path/to/netbox-peering-manager
export PYTHONPATH=/opt/netbox/netbox
export DJANGO_SETTINGS_MODULE=netbox.settings
pytest netbox_peering_manager/tests/
```

`make test` is the shorter equivalent inside the devcontainer. It first
verifies that no migration is missing, then runs the suite through
`manage.py test`.

Run one file or one test while iterating:

```bash
pytest netbox_peering_manager/tests/test_jobs.py
pytest netbox_peering_manager/tests/test_jobs.py -k replaces_existing
```

## What CI checks

Every pull request that touches code runs:

| Check | Requirement |
|-------|-------------|
| Lint | `ruff check` and `ruff format --check` pass. |
| Tests | The suite passes on Python 3.12, 3.13, and 3.14 against NetBox 4.5, 4.6, and 4.7. |
| Migrations | `makemigrations --check` reports no missing migration. |
| System check | `manage.py check` passes. |
| Build | The package builds. |
| Coverage | Reported to Codecov. New and changed lines are expected to be covered. |
| PR title | Follows Conventional Commits. |

Pull requests that touch only documentation run the docs build instead.

## Test layout

| File | Covers |
|------|--------|
| `test_models.py` | Model validation, constraints, computed properties. |
| `test_validators.py` | Community string validation. |
| `test_peeringdb.py` | PeeringDB client and sync service. |
| `test_irr_client.py` | fastbgpq4 client, including deferred jobs and polling. |
| `test_jobs.py` | IRR sync jobs. |
| `test_config_renderer.py` | Template context building. |
| `test_jinja2_filters.py` | Template filters. |
| `test_forms.py`, `test_views.py`, `test_api.py` | UI and API behavior, built on NetBox's test case classes. |

Aim tests at the plugin's own logic: validation, sync mapping, context
building, filters, jobs. A test that only proves NetBox, Django, or DRF
still works adds runtime without protecting anything.

A bug fix needs a regression test that fails before the fix.

## Mocking external services

No test may reach PeeringDB or a fastbgpq4 instance. The suite isolates
them at three seams:

**PeeringDB HTTP.** Patch the `requests.Session` class used by the client
and hand back canned JSON:

```python
from unittest.mock import MagicMock, patch

@patch("netbox_peering_manager.services.peeringdb.requests.Session")
def test_get_ix(self, mock_session_class):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"data": [{"id": 123, "name": "AMS-IX"}]}
    mock_session_class.return_value.get.return_value = response

    client = PeeringDBClient(base_url="https://peeringdb.example.com/api", rate_limit=0)
    assert client.get_ix(123)["name"] == "AMS-IX"
```

Pass `rate_limit=0` so the client does not sleep between requests.

**PeeringDB sync.** Sync tests leave the service untouched and patch the
client methods it calls, for example
`@patch.object(PeeringDBClient, "get_ixlans")`, then set return values for
`get_ix`, `get_ixlans`, `get_ixlan_prefixes`, and `get_netixlans_batch`.

**fastbgpq4.** For client tests, patch
`netbox_peering_manager.irr_client.httpx.Client`, and patch
`netbox_peering_manager.irr_client.time.sleep` when exercising polling.
For job tests, patch `netbox_peering_manager.jobs.IRRClient` and set
`fetch_prefixes.return_value` to a list of prefix strings.

## Query-count baselines

`netbox_peering_manager/tests/query_counts.json` records how many database
queries each list view and API list endpoint issues. NetBox's test case
classes compare against it on NetBox 4.6 and later, which catches N+1
regressions.

If a change legitimately alters a count, regenerate the file and commit
it with the change:

```bash
UPDATE_QUERY_COUNTS=1 pytest netbox_peering_manager/tests/
```

Review the diff: a count that goes up needs a reason.

## Code style

- `ruff check --fix` and `ruff format`. Line length is 120.
- `pre-commit install` sets up the hooks that run both on commit.
- Model changes need a migration (`make migrations`).

## Commits and pull requests

- PR titles follow [Conventional Commits](https://www.conventionalcommits.org/):
  `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`, `perf`,
  `build`, or `revert`, an optional scope, and a summary that starts with
  a lowercase letter. Example: `fix(peeringdb): skip peers without an address`.
- The title determines the label and the release-notes section, so choose
  the type that describes the user-visible effect.
- Add a line under `[Unreleased]` in `CHANGELOG.md` for anything a user
  would notice.
- Keep one logical change per pull request.

## Documentation

The site is built with [Zensical](https://zensical.org/) from the `docs/`
directory.

```bash
pip install zensical
cd docs
zensical serve            # live preview
zensical build --strict   # what CI runs; fails on broken links
```

Every page must be listed in the `nav` table of `docs/zensical.toml`, and
every `nav` entry must point at an existing file. CI verifies the second
half with:

```bash
python .github/scripts/check-docs-nav.py docs/zensical.toml
```

When a change is user-visible, update the relevant page here along with
the README and the changelog.
