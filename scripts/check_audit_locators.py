#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check the source locators of the audit's table of crosswalks of the FB2-only signals against cached bytes.

Each row names an FB2 weight, a Unified Expressions shape and line numbers in
four sources. The script reads the sources from a cache filled by
`scripts/verify_sources.py --cache DIR` (outside the repository), checks each
file against its SHA-256 in evidence/sources.toml, and checks that every cited
line says what the row needs:

- vrcft_docs_movement: the line pairs the Unified Expressions name with the FB2 name;
- godot_vendors_fb2: the line copies the FB2 weight to one Godot shape;
- godot_enum: lines 38-40 are the sentence that says the shapes are based on
  Unified Expressions, and the row's other line declares that Godot shape;
- godot_face_modifier: lines 48-54 end the comment that says the first name of
  each entry is the Unified Expressions name, and the row's pair of lines gives
  that Godot shape with the Unified Expressions name first.

The tests cannot read the cache, so this is a script check. It exits 1 and
lists the problems when a locator is wrong.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_canonical  # noqa: E402

HEADING = '## Crosswalks of the FB2-only signals'
RECORDS = ('vrcft_docs_movement', 'godot_vendors_fb2', 'godot_enum', 'godot_face_modifier')


def lines_of(cell: str, record: str) -> list[list[int]]:
    """The line numbers or ranges that a cell gives after a record name, as [first, last] pairs."""
    found = re.search(rf'`{record}` lines? ([\d\-, and]+)', cell)
    if not found:
        return []
    spans = []
    for part in re.split(r', | and ', found.group(1).strip(' ,')):
        first, _, last = part.partition('-')
        spans.append([int(first), int(last or first)])
    return spans


def rows(text: str) -> list[dict]:
    out = []
    for row in build_canonical.table(text, HEADING):
        out.append({'signal': build_canonical.ticks(row['Signal'])[0], 'fb2': row['FB2'],
                    'ue': row['Unified Expressions'], 'one_step': lines_of(row['One step'], 'vrcft_docs_movement'),
                    'to_godot': lines_of(row['FB2 to Godot'], 'godot_vendors_fb2'),
                    'enum': lines_of(row['Godot to Unified Expressions'], 'godot_enum'),
                    'modifier': lines_of(row['Godot to Unified Expressions'], 'godot_face_modifier')})
    return out


def check(row: dict, sources: dict[str, list[str]]) -> list[str]:
    def line(record, n):
        return sources[record][n - 1]
    problems, name = [], row['signal']
    [[n, _]] = row['one_step']
    if f"['{row['ue']}', '{row['fb2']}']" not in line('vrcft_docs_movement', n):
        problems.append(f'{name}: vrcft_docs_movement line {n} does not pair {row["ue"]} with {row["fb2"]}')
    [[n, _]] = row['to_godot']
    found = re.search(rf'xr_weights\[XRFaceTracker::(FT_\w+)\] = fb_weights\[XR_FACE_EXPRESSION2_{row["fb2"]}_FB\]',
                      line('godot_vendors_fb2', n))
    if not found:
        return problems + [f'{name}: godot_vendors_fb2 line {n} does not copy {row["fb2"]} to a Godot shape']
    shape = found.group(1)
    based, own = row['enum']
    span = [s.strip() for s in sources['godot_enum'][based[0] - 1:based[1]]]
    if not (span[0].startswith('The supported blend shapes are based on the Unified Expressions')
            and span[-1].endswith('standards.')):
        problems.append(f'{name}: godot_enum lines {based[0]}-{based[1]} are not the sentence on Unified Expressions')
    if not line('godot_enum', own[0]).strip().startswith(f'{shape},'):
        problems.append(f'{name}: godot_enum line {own[0]} does not declare {shape}')
    header, entry = row['modifier']
    span = sources['godot_face_modifier'][header[0] - 1:header[1]]
    if '- The Unified Expression blend shape name.' not in ' '.join(span) or 'Meta blend shape name' not in span[-1]:
        problems.append(f'{name}: godot_face_modifier lines {header[0]}-{header[1]} do not put Unified Expressions '
                        'first')
    first, second = line('godot_face_modifier', entry[0]), line('godot_face_modifier', entry[1])
    names = re.findall(r'"(\w+)"', second)
    if f'XRFaceTracker::{shape},' not in first or not names or names[0] != row['ue'].lower():
        problems.append(f'{name}: godot_face_modifier lines {entry[0]}-{entry[1]} do not give {shape} the name '
                        f'{row["ue"].lower()} first')
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n', 1)[0])
    parser.add_argument('--cache', type=Path, required=True, help='directory filled by verify_sources.py --cache')
    args = parser.parse_args()
    records = {r['id']: r for r in tomllib.loads((ROOT / 'evidence/sources.toml').read_text())['evidence']}
    sources = {}
    for record in RECORDS:
        data = (args.cache / record).read_bytes()
        if hashlib.sha256(data).hexdigest() != records[record]['sha256']:
            raise SystemExit(f'{record}: cached bytes do not match evidence/sources.toml')
        sources[record] = data.decode('utf-8').splitlines()
    found = rows((ROOT / build_canonical.AUDIT_DOC).read_text(encoding='utf-8'))
    problems = [p for row in found for p in check(row, sources)]
    print('\n'.join(problems) or f'{len(found)} rows: every locator checked')
    return bool(problems)


if __name__ == '__main__':
    raise SystemExit(main())
