#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare RCEF's FB2 -> ARKit translation with the routes the public sources give.

RCEF translates FB2 to ARKit through its canonical expression set: an in-map
(FB2 -> canonical) and an out-map (canonical -> ARKit). For each ARKit
coefficient this composes the two hops exactly, with fractions.Fraction, and
compares the composed FB2 weights with the source route.

Reads generated/rcef.pack.json and tests/fixtures/godot_fb2_rules.csv (written
by scripts/derive_fb2_goldens.py) and renders docs/godot_comparison.md. By
default it checks that the committed file is current; --write rewrites it.
"""
from __future__ import annotations
import argparse
import csv
from fractions import Fraction
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs/godot_comparison.md'
FB2_PREFIX, FB2_SUFFIX = 'openxr.fb2.XR_FACE_EXPRESSION2_', '_FB'
CANONICAL_PREFIX = 'rcef.canonical_expression.'
ARKIT_PREFIX = 'arkit.coefficient.'
# Disagreements about meaning that a weight comparison cannot show. Each was
# found while writing the mappings; the sources are in the evidence records.
SEMANTIC = (
    ('mouthClose', 'FB2 LIPS_TOWARD closes the lips "regardless of the position of the jaw"; VRCFT\'s Unified '
     'Expressions table defines MouthClosed relative to JawOpen (`vrcft_docs_shapes`), and SRanipal requires Jaw_Open '
     'to be inactive. Godot and VRCFT both copy the value directly, as RCEF does. For ARKit, RCEF\'s audit leaves the '
     'jaw relation unresolved: Apple\'s text says that mouthClose does not depend on the jaw, but RCEF\'s own '
     'calibration record reads it together with jawOpen (`arkit_mouthclose_jaw_unresolved`).'),
    ('mouthShrugUpper', 'ICT-FaceKit relates mouthShrugUpper to FACS AU10 (upper lip raiser), while Godot, VRCFT and '
     'RCEF use FB2 CHIN_RAISER_T; FB2 has separate UPPER_LIP_RAISER_L/R weights.'),
    ('jawOpen', 'ICT-FaceKit relates jawOpen to FACS AU27 (mouth stretch); FB2 JAW_DROP is the jaw drop.'),
    ('mouthUpperUpLeft, mouthUpperUpRight', 'ICT-FaceKit relates mouthUpperUp to FACS AU11 (nasolabial deepener); '
     'Godot, VRCFT and RCEF use FB2 UPPER_LIP_RAISER, named after AU10.'),
    ('cheekPuff', 'ICT-FaceKit relates cheekPuff to FACS AU33 (cheek blow); RCEF\'s canonical cheek puff has AU34 '
     '(puff), so the ICT crosswalk does not carry over for the FACS code (`ict_au33_cheek_blow`).'),
    ('eyeBlinkLeft, eyeBlinkRight', 'ICT-FaceKit relates eyeBlink to FACS AU45 (blink); RCEF\'s canonical eye '
     'closure has AU43 (eyes closed), so the ICT crosswalk does not carry over for the FACS code (`ict_au45_blink`).'),
    ('mouthSmileLeft, mouthSmileRight', 'Unified Expressions MouthSmile blends corner pull and corner slant; FB2 has '
     'no slant, and Godot sets it to zero.'),
    ('eyeLookIn/Out', 'VRCFT\'s Meta Movement and overview tables name FB2 weights EYES_LOOK_IN/OUT_*, which do not exist '
     'in the OpenXR registry, so they cannot settle the sides. Godot routes the FB2 values as RCEF does; ICT-FaceKit '
     'names ARKit shapes only; the FB2 figures (`xr_fb2_fig_eyes_look_left_l`) show the subject\'s own side.'),
)


def combination(rule) -> dict[str, Fraction]:
    """A rule's weight on each of its inputs, exactly."""
    operator = rule['operator']
    if operator['id'] == 'affine':
        if operator['offset'] != 0.0:
            raise ValueError(f"{rule['id']}: offsets are not compared")
        weights = [operator['scale']]
    elif operator['id'] == 'weighted_sum':
        weights = operator['weights']
    else:
        weights = [1.0]
    return {i: Fraction(w) for i, w in zip(rule['inputs'], weights)}


def hops(pack: dict) -> dict[str, tuple[list[str], dict[str, Fraction]]]:
    """ARKit name -> (the maps of its two hops, its composed weight on each FB2 channel)."""
    # canonical signal -> (its FB2 -> canonical map, its rule); ARKit signal -> (its canonical -> ARKit map, its rule)
    writers = {}
    for mapping in pack['mappings']:
        for rule in mapping['rules']:
            for start, end in ((FB2_PREFIX, CANONICAL_PREFIX), (CANONICAL_PREFIX, ARKIT_PREFIX)):
                if all(i.startswith(start) for i in rule['inputs']) and rule['outputs'][0].startswith(end):
                    if rule['outputs'][0] in writers:
                        raise ValueError(f'{rule["outputs"][0]}: written by two hop maps')
                    writers[rule['outputs'][0]] = (mapping['id'], rule)
    composed = {}
    for sid, (out_map, rule) in writers.items():
        if not sid.startswith(ARKIT_PREFIX):
            continue
        maps, weights = [], {}
        for canonical, weight in combination(rule).items():
            in_map, in_rule = writers[canonical]
            maps.append(in_map)
            for fb2, w in combination(in_rule).items():
                name = fb2[len(FB2_PREFIX):-len(FB2_SUFFIX)]
                weights[name] = weights.get(name, Fraction(0)) + weight * w
        composed[sid[len(ARKIT_PREFIX):]] = (sorted(set(maps)) + [out_map], weights)
    return composed


def text(weights: dict) -> str:
    return ' + '.join(f'{float(w):g}·{name}' for name, w in sorted(weights.items())) if weights else '—'


def compare(pack: dict, routes_csv: str) -> list[dict]:
    routes = {}
    for row in csv.DictReader(io.StringIO(routes_csv)):
        weights = {}
        for part in row['fb2_inputs'].split(';'):
            name, weight = part.split('*')
            weights[name] = float(weight)
        routes[row['arkit']] = {'weights': weights, 'route': row['route'], 'sources': row['sources']}
    rules = hops(pack)
    rows = []
    for arkit in sorted(set(routes) | set(rules)):
        route = routes.get(arkit)
        maps, ours = rules.get(arkit, (None, {}))
        theirs = route['weights'] if route else {}
        if maps is None:
            result = 'Godot translates it; RCEF does not yet'
        elif route is None:
            result = 'DISAGREES: no source route'
        elif ours != {name: Fraction(w) for name, w in theirs.items()}:
            result = 'DISAGREES with ' + ('Godot' if route['route'] == 'godot' else route['route'])
        elif route['route'] == 'godot':
            result = 'agrees with Godot'
        else:
            result = "Godot has no route; RCEF follows VRCFT's average"
        rows.append({'arkit': arkit, 'mapping': ' → '.join(f'`{m}`' for m in maps) if maps else '—',
                     'ours': text(ours), 'theirs': text(theirs),
                     'result': result, 'sources': route['sources'] if route else '—'})
    return rows


def render(pack: dict, routes_csv: str) -> str:
    rows = compare(pack, routes_csv)
    differences = [r for r in rows if r['mapping'] != '—' and r['result'] != 'agrees with Godot']
    missing = [r['arkit'] for r in rows if r['result'].startswith('Godot translates')]
    lines = [
        '# RCEF FB2 → ARKit translation compared with Godot',
        '',
        'Original documentation: CC-BY-SA-4.0. Generated by `scripts/compare_godot.py` from',
        '`generated/rcef.pack.json` and `tests/fixtures/godot_fb2_rules.csv`; do not edit by hand.',
        '',
        'The source routes come from the Godot OpenXR vendors plugin (FB2 weight → Godot shape, MIT) and Godot\'s',
        'face-modifier name table (Godot shape → ARKit name, MIT). Where Godot has no route, VRCFaceTracking\'s',
        'parameter code is used.',
        '',
        'RCEF translates FB2 to ARKit through its canonical expression set: an in-map (FB2 → canonical) and an',
        'out-map (canonical → ARKit). The two hops are composed exactly, and the composed weights are compared',
        'exactly. The "RCEF maps" column names the two maps.',
        '',
        f'RCEF translates {sum(1 for r in rows if r["mapping"] != "—")} ARKit coefficients from FB2. '
        f'Weight disagreements with Godot: {sum(r["result"].startswith("DISAGREES") for r in rows)}. '
        f'Without a Godot route: {sum(r["result"].startswith("Godot has no route") for r in rows)}. '
        f'Godot translates {len(missing)} more that RCEF does not yet.',
        '',
        '## Every difference from Godot',
        '',
    ]
    for r in differences:
        if r['result'].startswith('Godot has no route'):
            lines.append(f'- **{r["arkit"]}** ({r["mapping"]}): {r["result"]} ({r["ours"]}).')
        else:
            lines.append(f'- **{r["arkit"]}** ({r["mapping"]}): RCEF uses {r["ours"]}; the source route is '
                         f'{r["theirs"]}. {r["result"]}.')
    for arkit, note in SEMANTIC:
        lines.append(f'- **{arkit}** (meaning, not weights): {note}')
    lines += ['', '## RCEF mappings', '', '| ARKit | RCEF maps | RCEF | Source route | Result | Source lines |',
              '|---|---|---|---|---|---|']
    for r in rows:
        if r['mapping'] != '—':
            lines.append(f'| {r["arkit"]} | {r["mapping"]} | {r["ours"]} | {r["theirs"]} | {r["result"]} | {r["sources"]} |')
    lines += ['', '## Coefficients Godot translates and RCEF does not yet', '', ', '.join(missing) + '.', '']
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--write', action='store_true', help='rewrite docs/godot_comparison.md')
    args = parser.parse_args()
    content = render(json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8')),
                     (ROOT / 'tests/fixtures/godot_fb2_rules.csv').read_text(encoding='utf-8'))
    if args.write:
        OUTPUT.write_text(content, encoding='utf-8')
        return 0
    if not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8') != content:
        print('docs/godot_comparison.md is out of date; run scripts/compare_godot.py --write')
        return 1
    print('Godot comparison matches.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
