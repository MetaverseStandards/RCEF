#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render references.md from evidence/sources.toml; check it is current by default."""
from __future__ import annotations
import argparse
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'references.md'
HEADER = '''# Public source references

SPDX-License-Identifier: CC-BY-SA-4.0

Generated from [evidence/sources.toml](evidence/sources.toml) by `scripts/export_references.py`; edit the TOML, not this file. Each entry gives the exact bytes RCEF verified: the URL, the revision (or `retrieval-digest` for mutable documentation pages), the retrieval date and the SHA-256. `scripts/verify_sources.py` re-fetches them. Provider names and enums are extracted as facts with attribution; source prose, figures and algorithms are not bundled.
'''


def render(records: list[dict]) -> str:
    parts = [HEADER]
    for r in records:
        lines = [f'## {r["id"]}', '', r['claim'], '']
        if 'url' in r:
            lines.append(f'- Source: [{r["id"]}]({r["url"]})')
            if 'revision' in r:
                lines.append(f'- Revision: `{r["revision"]}`')
            if 'retrieved' in r:
                lines.append(f'- Retrieved: {r["retrieved"]}')
            if 'sha256' in r:
                lines.append(f'- SHA-256: `{r["sha256"]}`')
        if 'authorship' in r:
            lines.append(f'- Original authorship: {r["authorship"]}')
        if 'license' in r:
            lines.append(f'- License or terms: {r["license"]}')
        if 'locator' in r:
            lines.append(f'- Locator: {r["locator"]}')
        parts.append('\n'.join(lines) + '\n')
    return '\n'.join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='rewrite references.md')
    args = parser.parse_args()
    content = render(tomllib.loads((ROOT / 'evidence/sources.toml').read_text(encoding='utf-8'))['evidence'])
    if args.write:
        OUTPUT.write_text(content, encoding='utf-8')
        return 0
    if OUTPUT.read_text(encoding='utf-8') != content:
        print('references.md is out of date; run scripts/export_references.py --write')
        return 1
    print('references.md matches evidence/sources.toml.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
