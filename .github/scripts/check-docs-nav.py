#!/usr/bin/env python3
"""Fail when the zensical nav points at pages that do not exist.

`zensical build --strict` aborts on broken links inside page bodies, but it
silently accepts nav entries whose target file is missing and renders them
as dead links on every page. This check closes that gap.
"""

import sys
import tomllib
from pathlib import Path


def nav_targets(node):
    """Yield every page path referenced by a (possibly nested) nav node."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, list):
        for item in node:
            yield from nav_targets(item)
    elif isinstance(node, dict):
        for value in node.values():
            yield from nav_targets(value)


def main(config_path="docs/zensical.toml"):
    config = Path(config_path)
    project = tomllib.loads(config.read_text())["project"]
    docs_dir = config.parent / project.get("docs_dir", "docs")
    missing = [
        target
        for target in nav_targets(project.get("nav", []))
        if "://" not in target and not (docs_dir / target).is_file()
    ]
    for target in missing:
        print(f"{config}: nav entry points at a missing page: {target}", file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
