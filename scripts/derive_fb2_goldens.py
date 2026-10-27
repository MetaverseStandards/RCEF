#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Derive FB2 -> ARKit and META viseme -> VRM expectations from pinned source bytes.

The expectations used by the translation tests must not come from the person
who wrote RCEF's rules, or from RCEF's mapping data. This script reads only
public source files from a cache filled by `scripts/verify_sources.py --cache`.
It checks each file against the SHA-256 in evidence/sources.toml and never
reads mappings/, profiles/ or data/.

Outputs:
- tests/fixtures/godot_fb2_rules.csv: every ARKit coefficient the sources can
  express as a linear combination of FB2 weights, with the route and lines.
- tests/fixtures/fb2_goldens.json: input frames and expected outputs, with
  the source lines behind every expectation and the SHA-256 of each source.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('godot_vendors_fb2', 'godot_face_modifier', 'vrcft_docs_arkit', 'vrcft_code_parameters',
           'apple_blendshapes', 'xr_visemes', 'vrm_expressions')
FB2 = 'openxr.fb2.XR_FACE_EXPRESSION2_{}_FB'
ARKIT = 'arkit.coefficient.{}'
VISEME = 'openxr.visemes.XR_FACE_TRACKING_VISEME_{}_META'
VRM = 'vrm.preset.{}'
# Values with exact binary representations, so sums and halves compare exactly.
LEVELS = (0.25, 1.0)
PAIRS = ((0.25, 0.75), (1.0, 0.0), (0.0, 1.0), (0.5, 0.5), (0.125, 0.875))


def load_sources(cache: Path) -> tuple[dict[str, list[str]], dict[str, str]]:
    records = {r['id']: r for r in tomllib.loads((ROOT / 'evidence/sources.toml').read_text())['evidence']}
    texts, digests = {}, {}
    for name in SOURCES:
        data = (cache / name).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != records[name]['sha256']:
            raise SystemExit(f'{name}: cached bytes do not match evidence/sources.toml')
        texts[name] = data.decode('utf-8').splitlines()
        digests[name] = digest
    return texts, digests


def godot_weights(lines: list[str]) -> dict[str, tuple[dict[str, float], list[int]]]:
    """FT shape -> (FB2 weight per input, source lines), from the vendors plugin."""
    assign = re.compile(r'xr_weights\[XRFaceTracker::(FT_\w+)\]\s*=\s*(.+);')
    direct = re.compile(r'fb_weights\[XR_FACE_EXPRESSION2_(\w+)_FB\]$')
    mean = re.compile(r'average\(xr_weights\[XRFaceTracker::(FT_\w+)\],\s*xr_weights\[XRFaceTracker::(FT_\w+)\]\)$')
    shapes: dict[str, tuple[dict[str, float], list[int]]] = {}
    for number, line in enumerate(lines, 1):
        found = assign.search(line)
        if not found:
            continue
        shape, value = found.group(1), found.group(2).strip()
        if m := direct.match(value):
            shapes[shape] = ({m.group(1): 1.0}, [number])
        elif m := mean.match(value):
            combined: dict[str, float] = {}
            used = [number]
            for part in m.groups():
                weights, part_lines = shapes.get(part, ({}, []))
                used += part_lines
                for name, weight in weights.items():
                    combined[name] = combined.get(name, 0.0) + weight / 2
            shapes[shape] = ({k: v for k, v in combined.items() if v}, used)
        else:
            shapes[shape] = ({}, [number])  # A constant such as 0.0f: not tracked.
    return shapes


def godot_names(lines: list[str]) -> dict[str, tuple[list[str], int]]:
    """FT shape -> (lower-case names, line) from the face modifier's name table."""
    text = '\n'.join(lines)
    entry = re.compile(r'\{\s*XRFaceTracker::(FT_\w+),\s*\{\s*((?:"[a-z0-9]+",?\s*)+)\}\s*\}')
    names = {}
    for found in entry.finditer(text):
        names[found.group(1)] = (re.findall(r'"([a-z0-9]+)"', found.group(2)),
                                 text.count('\n', 0, found.start()) + 1)
    return names


def arkit_names(lines: list[str]) -> list[str]:
    document = json.loads('\n'.join(lines))
    prefix = '/documentation/arkit/arfaceanchor/blendshapelocation/'
    return sorted(r['title'] for r in document['references'].values()
                  if r.get('url', '').startswith(prefix) and r.get('kind') == 'symbol')


def vrcft_arkit(lines: list[str]) -> dict[str, tuple[str, int]]:
    """ARKit name -> (Unified Expressions name, line) from the VRCFT ARKit table."""
    row = re.compile(r"\[\s*(?:<b>)?(\w+)(?:</b>)?'?\s*,\s*'(\w+)'\s*\]")
    table = {}
    for number, line in enumerate(lines, 1):
        found = row.search(line.replace("['", '[').replace("'<b>", '<b>'))
        if found:
            table[found.group(2)] = (found.group(1), number)
    return table


def vrcft_means(lines: list[str]) -> dict[str, tuple[tuple[str, str], list[int]]]:
    """Unified parameter -> (two Unified shapes it averages, lines)."""
    head = re.compile(r'new EParam\("v2/(\w+)"')
    body = re.compile(r'^\s*\(exp\.Shapes\[\(int\)UnifiedExpressions\.(\w+)\]\.Weight \+ '
                      r'exp\.Shapes\[\(int\)UnifiedExpressions\.(\w+)\]\.Weight\) / 2\.0f\),?$')
    means = {}
    for number, line in enumerate(lines, 1):
        found = head.search(line)
        if found and number < len(lines) and (m := body.match(lines[number])):
            means[found.group(1)] = ((m.group(1), m.group(2)), [number, number + 1])
    return means


def fb2_routes(texts):
    weights = godot_weights(texts['godot_vendors_fb2'])
    names = godot_names(texts['godot_face_modifier'])
    by_name = {}
    for shape, (labels, line) in names.items():
        for label in labels:
            by_name.setdefault(label, []).append((shape, line))
    unified = {labels[0]: shape for shape, (labels, _) in names.items()}
    table = vrcft_arkit(texts['vrcft_docs_arkit'])
    means = vrcft_means(texts['vrcft_code_parameters'])
    routes = []
    for arkit in arkit_names(texts['apple_blendshapes']):
        matches = by_name.get(arkit.lower(), [])
        if len(matches) > 1:
            raise SystemExit(f'{arkit} names more than one Godot shape')
        if matches:
            shape, name_line = matches[0]
            combination, lines = weights.get(shape, ({}, []))
            if combination:
                routes.append({'arkit': arkit, 'inputs': combination, 'route': 'godot',
                               'cites': [('godot_face_modifier', name_line)]
                               + [('godot_vendors_fb2', n) for n in sorted(set(lines))]})
                continue
        if arkit in table and table[arkit][0] in means:
            ue, table_line = table[arkit]
            (left, right), mean_lines = means[ue]
            combination: dict[str, float] = {}
            cites = [('vrcft_docs_arkit', table_line)] + [('vrcft_code_parameters', n) for n in mean_lines]
            for part in (left, right):
                shape = unified.get(part.lower())
                part_weights, part_lines = weights.get(shape, ({}, []))
                if not part_weights:
                    combination = {}
                    break
                cites += [('godot_face_modifier', names[shape][1])] + [('godot_vendors_fb2', n) for n in part_lines]
                for name, weight in part_weights.items():
                    combination[name] = combination.get(name, 0.0) + weight / 2
            if combination:
                routes.append({'arkit': arkit, 'inputs': combination, 'route': 'vrcft mean via godot names',
                               'cites': cites})
    return routes


def viseme_pairs(texts):
    vis, vrm = texts['xr_visemes'], texts['vrm_expressions']
    visemes = {}
    for number, line in enumerate(vis, 1):
        if m := re.match(r'^\|(\w+) \(ename:XR_FACE_TRACKING_VISEME_(\w+)_META\)$', line):
            visemes[m.group(2)] = (number, vis[number].lstrip('|'), vis[number + 1].lstrip('|'))
    start = next(i for i, line in enumerate(vrm) if line.startswith('### Lip Sync Procedural'))
    presets = {}
    for number in range(start + 1, len(vrm)):
        if vrm[number].startswith('###'):
            break
        if m := re.match(r'^\| ([a-z]+)\s+\| (\w+)\s+\|$', vrm[number]):
            presets[m.group(1)] = (number + 1, m.group(2))
    pairs = []
    for preset, (line, remark) in presets.items():
        if preset.upper() in visemes:
            viseme = preset.upper()
            basis = 'same name'
        elif preset == 'ee' and remark == 'eh' and visemes.get('E', (0, ''))[1] == 'e':
            # The one pairing that is not a name match: VRM's remark "eh" and META's
            # phoneme "e" (as in "bed") name the same vowel.
            viseme = 'E'
            basis = 'VRM remark "eh" and META phoneme "e"'
        else:
            raise SystemExit(f'no META viseme for VRM preset {preset}')
        pairs.append({'vrm': preset, 'viseme': viseme, 'basis': basis,
                      'cites': [('vrm_expressions', line), ('xr_visemes', visemes[viseme][0])]})
    return pairs, sorted(visemes)


def cite(cites):
    """Source lines as "id:Lnn"; the SHA-256 of each source is in the file's "sources"."""
    return [f'{name}:L{line}' for name, line in cites]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--cache', type=Path, required=True, help='directory filled by verify_sources.py --cache')
    args = parser.parse_args()
    texts, digests = load_sources(args.cache)
    routes = fb2_routes(texts)
    pairs, visemes = viseme_pairs(texts)

    table = io.StringIO()
    writer = csv.writer(table, lineterminator='\n')
    writer.writerow(['arkit', 'fb2_inputs', 'route', 'sources'])
    for r in routes:
        writer.writerow([r['arkit'], ';'.join(f'{k}*{v:g}' for k, v in sorted(r['inputs'].items())),
                         r['route'], ';'.join(f'{n}:L{line}' for n, line in r['cites'])])
    (ROOT / 'tests/fixtures/godot_fb2_rules.csv').write_text(table.getvalue(), encoding='utf-8')

    cases = []
    for r in routes:
        inputs = sorted(r['inputs'])
        if len(inputs) == 1:
            values = [(level,) for level in LEVELS]
        else:
            values = [pair for pair in PAIRS] if len(inputs) == 2 else []
        for value in values:
            frame = {FB2.format(name): v for name, v in zip(inputs, value)}
            expected = sum(r['inputs'][name] * v for name, v in zip(inputs, value))
            cases.append({'mapping_kind': 'fb2_to_arkit', 'inputs': frame,
                          'expected': {ARKIT.format(r['arkit']): expected},
                          'sources': cite(r['cites'])})
    # One valid viseme frame (values sum to 1, as the META spec requires), with
    # mass on every paired vowel and on a consonant that no VRM preset receives.
    frame = {VISEME.format(v): 0.0 for v in visemes}
    shares = (0.25, 0.1875, 0.125, 0.0625, 0.03125)  # distinct, so a swapped pair shows
    for pair, share in zip(sorted(pairs, key=lambda p: p['viseme']), shares):
        frame[VISEME.format(pair['viseme'])] = share
    frame[VISEME.format('SS')] = 1.0 - sum(shares)
    cases.append({'mapping_kind': 'visemes_to_vrm', 'inputs': frame,
                  'expected': {VRM.format(p['vrm']): frame[VISEME.format(p['viseme'])] for p in pairs},
                  'sources': cite([c for p in pairs for c in p['cites']])})
    output = {'generated_by': 'scripts/derive_fb2_goldens.py',
              'sources': {name: digests[name] for name in SOURCES},
              'viseme_pairs': [{k: v for k, v in p.items() if k != 'cites'} | {'sources': cite(p['cites'])}
                               for p in pairs],
              'cases': cases}
    (ROOT / 'tests/fixtures/fb2_goldens.json').write_text(json.dumps(output, indent=1, sort_keys=True) + '\n',
                                                          encoding='utf-8')
    print(f'{len(routes)} ARKit routes, {len(pairs)} viseme pairs, {len(cases)} cases')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
