#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write the signal names of expression sets that have no profile yet, for the capability test.

tests/test_pivot_structure.py checks which canonical groups each of these
sets could fill. The names come only from pinned public source bytes in a
cache filled by `scripts/verify_sources.py --cache DIR`; each file is checked
against its SHA-256 in evidence/sources.toml. The script never reads
mappings/, profiles/ or data/.

Output: tests/fixtures/capability_sets.json, with each set's names, its
evidence record and the locator of the names in the source.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'tests/fixtures/capability_sets.json'
# (set, evidence record, enum name in xr.xml, prefix, suffix)
ENUMS = (('FB v1', 'xr_registry', 'XrFaceExpressionFB', 'XR_FACE_EXPRESSION_', '_FB'),
         ('XR_ANDROID_face_tracking', 'xr_registry', 'XrFaceParameterIndicesANDROID', 'XR_FACE_PARAMETER_INDICES_',
          '_ANDROID'),
         ('XR_ML_facial_expression', 'xr_registry', 'XrFacialBlendShapeML', 'XR_FACIAL_BLEND_SHAPE_', '_ML'))
# The FACS tables whose codes a FACS source can score as face actions: main codes and gross behavior codes.
FACS_TABLES = (('main codes', '==== Main codes ===='), ('gross behavior codes', '==== Gross behavior codes ===='))


def source(cache: Path, name: str, records: dict) -> list[str]:
    data = (cache / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != records[name]['sha256']:
        raise SystemExit(f'{name}: cached bytes do not match evidence/sources.toml')
    return data.decode('utf-8').splitlines()


def enum_names(lines: list[str], enum: str, prefix: str, suffix: str) -> tuple[list[str], str]:
    start = next(i for i, line in enumerate(lines) if f'<enums name="{enum}"' in line)
    end = next(i for i in range(start, len(lines)) if '</enums>' in lines[i])
    names = []
    for line in lines[start + 1:end]:
        found = re.search(r'name="([A-Z0-9_]+)"', line)
        if found and not found.group(1).endswith('_COUNT' + suffix):
            name = found.group(1)
            if not (name.startswith(prefix) and name.endswith(suffix)):
                raise SystemExit(f'{enum}: unexpected name {name}')
            names.append(name[len(prefix):-len(suffix)])
    return names, f'xr.xml lines {start + 1}-{end + 1} ({enum}), without the COUNT entry'


def facs_codes(lines: list[str]) -> tuple[list[str], str]:
    codes, parts = [], []
    for label, heading in FACS_TABLES:
        start = lines.index(heading)
        end = next(i for i in range(start, len(lines)) if lines[i].startswith('|}'))
        for line in lines[start:end]:
            found = re.match(r'^\| (\d+)\*? \|\|', line)
            if found and found.group(1) != '0':
                codes.append(found.group(1))
        parts.append(f'{start + 1}-{end + 1} ({label})')
    return codes, 'raw wikitext lines ' + ' and '.join(parts) + '; code 0 (neutral face) left out'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n', 1)[0])
    parser.add_argument('--cache', type=Path, required=True, help='directory filled by verify_sources.py --cache')
    args = parser.parse_args()
    records = {r['id']: r for r in tomllib.loads((ROOT / 'evidence/sources.toml').read_text())['evidence']}
    sets = []
    codes, locator = facs_codes(source(args.cache, 'facs_wikipedia', records))
    sets.append({'set': 'FACS', 'record': 'facs_wikipedia', 'sha256': records['facs_wikipedia']['sha256'],
                 'locator': locator, 'names': codes,
                 'note': 'any code may take an L or R side prefix (raw line 78); L30 and R30 are read as directions'})
    registry = source(args.cache, 'xr_registry', records)
    for name, record, enum, prefix, suffix in ENUMS:
        names, locator = enum_names(registry, enum, prefix, suffix)
        sets.append({'set': name, 'record': record, 'sha256': records[record]['sha256'], 'locator': locator,
                     'names': names, 'note': f'names without the {prefix} prefix and the {suffix} suffix'})
    OUTPUT.write_text(json.dumps({'sets': sets}, indent=1) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
