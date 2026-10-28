#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render docs/toml-index.csv from the TOML authoring files, or by default check that it is current."""
from __future__ import annotations
import argparse
import csv
import difflib
import hashlib
import io
import os
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs/toml-index.csv'
COLUMNS = ['path', 'role', 'table_kinds', 'signals', 'profiles', 'membership_rows', 'mappings', 'rules',
           'evidence', 'canonical_signals', 'bytes', 'sha256', 'license']
ARRAYS = ('signals', 'profiles', 'mappings', 'evidence')


def authoring_files(root: Path = ROOT) -> list[Path]:
    """The files msf-character-tools discovery reads: every *.toml, skipping hidden names and generated/."""
    files = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'generated']
        files += [Path(directory) / n for n in names if not n.startswith('.') and n.endswith('.toml')]
    return sorted(files)


def role(path: str, document: dict) -> str:
    if path == 'pack.toml':
        return 'pack metadata'
    if path == 'data/canonical.toml':
        return 'canonical signals and profile'
    if path == 'data/intermediate.toml':
        return 'intermediate signals and profile'
    if 'evidence' in document:
        return 'source evidence'
    if 'mappings' in document:
        return 'directional maps'
    return 'signal inventory and profiles'


def render(root: Path = ROOT) -> str:
    files = authoring_files(root)
    documents = {f: tomllib.loads(f.read_text(encoding='utf-8')) for f in files}
    canonical = {s for d in documents.values() for p in d.get('profiles', [])
                 if p['id'] == 'rcef.canonical' for s in p['signal_ids']}
    out = io.StringIO()
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(COLUMNS)
    for f in files:
        d, raw, path = documents[f], f.read_bytes(), f.relative_to(root).as_posix()
        signals, profiles, maps = d.get('signals', []), d.get('profiles', []), d.get('mappings', [])
        kinds = '; '.join(f'[[{k}]]' for k in ARRAYS if k in d) or 'root scalar keys'
        licence = re.search(rb'SPDX-License-Identifier:\s*(\S+)', raw)
        writer.writerow([path, role(path, d), kinds, len(signals), len(profiles),
                         sum(len(p['signal_ids']) for p in profiles), len(maps),
                         sum(len(m['rules']) for m in maps), len(d.get('evidence', [])),
                         sum(1 for s in signals if s['id'] in canonical), len(raw),
                         hashlib.sha256(raw).hexdigest(), licence.group(1).decode() if licence else ''])
    return out.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='rewrite docs/toml-index.csv')
    args = parser.parse_args()
    content = render()
    if args.write:
        OUTPUT.write_text(content, encoding='utf-8', newline='\n')
        return 0
    current = OUTPUT.read_text(encoding='utf-8') if OUTPUT.exists() else ''
    if current != content:
        print(''.join(difflib.unified_diff(current.splitlines(True), content.splitlines(True),
                                           'docs/toml-index.csv', 'from the TOML files')), end='')
        print('docs/toml-index.csv is out of date; run scripts/export_toml_index.py --write')
        return 1
    print('docs/toml-index.csv matches the TOML authoring files.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
