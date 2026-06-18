# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- NetBox 4.6 support: CI now tests against NetBox 4.6.3 (alongside 4.5.10) and
  `max_version` is raised to 4.6.99.

### Changed

- GraphQL: expose conventional `<Model>Filter` aliases so NetBox 4.6's filter
  auto-discovery resolves each model's filter. The canonical `NetBoxBGP*` filter
  classes (and the GraphQL schema input-type names) are unchanged.

## [0.2.2] - 2026-04-28

First release on the canonical toolkit. Behaviour and plugin code unchanged.

### Added

- Canonical 5 GHA workflows: `ci.yml`, `publish.yml`, `docs.yml`, `release-drafter.yml`, `pr-title.yml`. Plus `.github/release-drafter.yml`.
- `commit-msg` pre-commit stage that rejects AI / Claude attribution lines.
- `.git-template/hooks/commit-msg` (canonical hook tracked in-tree).
- `docs/zensical.toml` + scaffold (no docs site existed before).
- `CHANGELOG.md` (this file).
- `[docs]` extra in `pyproject.toml` (zensical).
- `bumpver` configuration with vMAJOR.MINOR.PATCH tags and `CHANGELOG.md` Unreleased promotion.

### Removed

- `setup.py` (replaced by `[project]` section in `pyproject.toml` with dynamic version sourced from `netbox_peering_manager.version.__version__`).

### Changed

- CI: switched from `manage.py test` to `pytest` (matches the rest of the toolkit). Matrix expanded to Python 3.12-3.14 x NetBox 4.5.5/4.5.8. Switched dependency installation to `uv` with caching. Activates the workspace `.venv` via `GITHUB_PATH` so plain `python` works from `/opt/netbox/netbox`. Added Codecov OIDC upload, `manage.py check`, and `makemigrations --check`.
- `publish.yml`: build switched to `uv build`; `actions/upload-artifact` and `actions/download-artifact` pinned to v4.
- `pyproject.toml`: gained the full `[project]` section, switched build to setuptools, expanded ruff selectors with `A` and `S`; ignored `N806`, `S101`, `DJ001`. Added test per-file ignores for `E402`, `F841`, `B017`.
- `.pre-commit-config.yaml`: added `pre-commit-hooks` (whitespace, EOF, YAML/TOML, merge-conflict, line-endings) and the local `commit-msg` stage.

### Fixed

- CI tests on Python 3.14 / NetBox 4.5.5 / 4.5.8 now pass: defined `API_TOKEN_PEPPERS` in the test configuration so v2 API tests can run, and patched `get_netixlans_batch` in the PeeringDB sync tests so they no longer hit the live PeeringDB API and timeout under pytest collection order.
