#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Derive translation expectations (FB2, ARKit, Unified Expressions, VRM) from pinned source bytes.

The expectations used by the translation tests must not come from the person
who wrote RCEF's rules, or from RCEF's mapping data. This script reads only
public source files from a cache filled by `scripts/verify_sources.py --cache`.
It checks each file against the SHA-256 in evidence/sources.toml and never
reads mappings/, profiles/ or data/.

Outputs:
- tests/fixtures/godot_fb2_rules.csv: every ARKit coefficient the sources can
  express as a linear combination of FB2 weights, with the route and lines.
- tests/fixtures/fb2_goldens.json: input frames and expected outputs, with
  the source lines behind every expectation and the SHA-256 of each source:
  FB2 -> ARKit, ARKit -> FB2 (the same routes read back, each composite copied
  to its parts), ARKit -> Unified Expressions base shapes, FB2 -> VRM blink and
  META visemes -> VRM. Each direction also gets frames in which every input
  has its own value, so a halved or wrong-input rule cannot hide.
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
SOURCES = ('godot_vendors_fb2', 'godot_face_modifier', 'vrcft_docs_arkit', 'vrcft_docs_movement',
           'vrcft_code_parameters', 'vrcft_simple_expressions', 'ict_facekit', 'apple_blendshapes', 'xr_fb2',
           'xr_registry', 'xr_visemes', 'vrm_expressions')
FB2 = 'openxr.fb2.XR_FACE_EXPRESSION2_{}_FB'
ARKIT = 'arkit.coefficient.{}'
VISEME = 'openxr.visemes.XR_FACE_TRACKING_VISEME_{}_META'
VRM = 'vrm.preset.{}'
UE = 'vrcft.artist.base.{}'
# Values with exact binary representations, so sums and halves compare exactly.
LEVELS = (0.25, 1.0)
PAIRS = ((0.25, 0.75), (1.0, 0.0), (0.0, 1.0), (0.5, 0.5), (0.125, 0.875))
QUADS = ((0.125, 0.25, 0.5, 1.0), (1.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.75, 0.25))


def load_sources(cache: Path) -> tuple[dict[str, list[str]], dict[str, str]]:
    records = {r['id']: r for r in tomllib.loads((ROOT / 'evidence/sources.toml').read_text())['evidence']}
    texts, digests = {}, {}
    for name in SOURCES:
        data = (cache / name).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != records[name]['sha256']:
            raise SystemExit(f'{name}: cached bytes do not match evidence/sources.toml')
        texts[name] = data.decode('utf-8-sig').splitlines()
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


def vrcft_table(lines: list[str]) -> list[tuple[list[str], str, int, bool]]:
    """Rows of a VRCFT comparison table: (Unified names, other name, line, blended)."""
    rows = []
    for number, line in enumerate(lines, 1):
        if m := re.match(r"\s*\[(.*),\s*'(\w+)'\],?\s*$", line):
            left = m.group(1)
            names = re.findall(r'[A-Z][A-Za-z]+', re.sub(r'</?b>|<br/>|<>|</>', ' ', left))
            rows.append((names, m.group(2), number, '<b>' in left))
    return rows


def registry_fb_names(lines: list[str]) -> set[str]:
    """XrFaceExpressionFB and XrFaceExpression2FB channel names in the pinned xr.xml."""
    return set(re.findall(r'name="XR_FACE_EXPRESSION2?_(\w+?)_FB"', '\n'.join(lines)))


def ict_units(lines: list[str]) -> dict[str, tuple[int, str, int]]:
    """ICT shape (eyeSquint_L style) -> (AU number, AU name, line) from its FACS table."""
    units = {}
    for number, line in enumerate(lines, 1):
        if m := re.match(r'\|\s*AU(\d+) ([^|]+?)\s*\|\s*([^|]+?)\s*\|', line):
            for shape in m.group(3).split('+'):
                units[shape.strip()] = (int(m.group(1)), m.group(2), number)
    return units


def ict_name(arkit: str) -> str:
    for side, suffix in (('Left', '_L'), ('Right', '_R')):
        if arkit.endswith(side):
            return arkit[:-len(side)] + suffix
    return arkit


def second_sources(routes, texts) -> dict[str, dict]:
    """For each FB2 -> ARKit route, the evidence beyond Godot: VRCFT's two tables, or ICT's FACS table.

    VRCFT's Movement table labels some eye rows with names that are in neither
    FB registry enum (EYES_LOOK_IN/OUT, EYES_SQUINT, EYES_WIDEN); those rows and
    rows with a misspelt or wrong-side name are not counted. ICT's mouthUpperUp
    row names AU 11, not the AU 10 that FB2's UPPER_LIP_RAISER is named after,
    so it is recorded as a disagreement.
    """
    ue_of = {other: (names, line, blended) for names, other, line, blended in vrcft_table(texts['vrcft_docs_arkit'])}
    fb_of = {name: (other, line) for names, other, line, _ in vrcft_table(texts['vrcft_docs_movement'])
             for name in names}
    means = vrcft_part_means(texts['vrcft_code_parameters'])
    registry = registry_fb_names(texts['xr_registry'])
    ict = ict_units(texts['ict_facekit'])
    out = {}
    for r in routes:
        arkit, channels = r['arkit'], set(r['inputs'])
        counted, notes, cites = [], [], []
        if arkit in ue_of:
            names, line, blended = ue_of[arkit]
            mean = means.get(names[0]) or means.get(names[0] + 'Suck (first term)')
            if blended and mean:
                # A blended Unified shape is the mean of its parts; each part maps to an FB name.
                parts, mean_lines = mean
                weights, part_lines = {}, []
                for part in parts:
                    if part in fb_of:
                        weights[fb_of[part][0]] = weights.get(fb_of[part][0], 0.0) + 1 / len(parts)
                        part_lines.append(fb_of[part][1])
                if set(weights) - registry:
                    notes.append(f'vrcft label {"/".join(sorted(set(weights) - registry))} not in the registry; '
                                 'not counted')
                elif weights == r['inputs']:
                    counted.append('vrcft mean')
                    cites += ([('vrcft_docs_arkit', line)] + [('vrcft_code_parameters', n) for n in mean_lines]
                              + [('vrcft_docs_movement', n) for n in sorted(set(part_lines))])
                else:
                    notes.append(f'vrcft mean gives {weights}; not counted')
            else:
                fbs = [fb_of[n] for n in names if n in fb_of]
                labels = {f for f, _ in fbs}
                if labels - registry:
                    notes.append(f'vrcft label {"/".join(sorted(labels - registry))} not in the registry; not counted')
                elif fbs and labels == channels:
                    counted.append('vrcft')
                    cites += [('vrcft_docs_arkit', line)] + [('vrcft_docs_movement', fl) for _, fl in fbs]
                elif fbs:
                    notes.append(f'vrcft names {"/".join(sorted(labels))}; not counted')
        elif arkit.lower() in ('mouthleft', 'mouthright'):
            unified = 'Mouth' + arkit[5:]
            if unified in fb_of and fb_of[unified][0] in channels:
                notes.append(f'single project for the ARKit name (Godot); vrcft pairs {fb_of[unified][0]} with its '
                             f'blended {unified} (vrcft_docs_movement:L{fb_of[unified][1]})')
        if r['route'] != 'godot' and 'vrcft mean' in counted:
            counted.remove('vrcft mean')
            cites = [c for c in cites if not c[0].startswith('vrcft')]
            notes.append('the route itself comes from vrcft; not counted again')
        # ICT splits browInnerUp and cheekPuff into halves, listed under one AU.
        unit = ict.get(ict_name(arkit)) or ict.get(arkit + '_L')
        if unit:
            number, name, line = unit
            if arkit.startswith('mouthUpperUp'):
                notes.append(f'ict names AU{number} ({name}), not AU10; a disagreement, not a source')
            else:
                counted.append('ict')
                cites.append(('ict_facekit', line))
        out[arkit] = {'counted': counted, 'notes': notes, 'cites': cites}
    return out


def ft_to_unified(ft: str) -> str:
    return ''.join(part.capitalize() for part in ft[len('FT_'):].split('_'))


def godot_unified(lines: list[str]) -> dict[str, tuple[list[str], int]]:
    """Blended FT shape -> (its FT parts, line), from the face modifier's unified table."""
    text = '\n'.join(lines)
    start = text.index('unified_blends[] = {')
    end = text.index('};', start)
    table = {}
    for m in re.finditer(r'\{\s*XRFaceTracker::(FT_\w+),\s*\{([^}]*)\}\s*\}', text[start:end]):
        parts = re.findall(r'XRFaceTracker::(FT_\w+)', m.group(2))
        table[m.group(1)] = (parts, text.count('\n', 0, start + m.start()) + 1)
    return table


def vrcft_splits(lines: list[str]) -> dict[str, tuple[dict[str, float], list[int]]]:
    """VRCFT simple expression -> ({Unified part: weight}, lines), e.g. BrowDownRight."""
    splits = {}
    for number, line in enumerate(lines, 1):
        if m := re.search(r'\{ UnifiedSimpleExpressions\.(\w+), exp =>', line):
            body = lines[number]
            parts = re.findall(r'UnifiedExpressions\.(\w+)\]\.Weight \* (\.\d+)f', body)
            if parts and ' ? ' not in body:
                splits[m.group(1)] = ({p: float(w) for p, w in parts}, [number, number + 1])
    return splits


def vrcft_part_means(lines: list[str]) -> dict[str, tuple[list[str], list[int]]]:
    """Unified parameter -> (the parts it averages, lines), for two- and four-part means."""
    means = {}
    for number, line in enumerate(lines, 1):
        if m := re.search(r'new EParam\("v2/(\w+)"', line):
            body, used = line, [number]
            k = number
            while not body.rstrip().endswith('),') and k < len(lines) and k - number < 4:
                body += lines[k]
                k += 1
                used.append(k)
            parts = re.findall(r'UnifiedExpressions\.(\w+)\]\.Weight', body)
            if re.search(r'/ (2|4)\.0f\)', body) and len(parts) in (2, 4) and '-' not in body.split('=>', 1)[1]:
                means[m.group(1)] = (parts, used)
            elif lead := re.search(r'=>\s*\(exp\.Shapes\[\(int\)UnifiedExpressions\.(\w+)\]\.Weight \+ '
                                   r'exp\.Shapes\[\(int\)UnifiedExpressions\.(\w+)\]\.Weight\) / 2\.0f -', body):
                # v2/CheekPuffSuck: the mean of the two puff shapes, minus the mean of the two suck shapes.
                means[m.group(1) + ' (first term)'] = ([lead.group(1), lead.group(2)], used)
    return means


def ue_routes(texts) -> list[dict]:
    """ARKit -> Unified Expressions base shapes; a blended Unified shape is filled by copying into its parts."""
    rows = vrcft_table(texts['vrcft_docs_arkit'])
    unified = godot_unified(texts['godot_face_modifier'])
    names = godot_names(texts['godot_face_modifier'])
    splits = vrcft_splits(texts['vrcft_simple_expressions'])
    means = vrcft_part_means(texts['vrcft_code_parameters'])
    alias = {label: (shape, line) for shape, (labels, line) in names.items() for label in labels}
    routes = []
    covered = set()
    for ue_names, arkit, line, blended in rows:
        ue = ue_names[0]
        cites = [('vrcft_docs_arkit', line)]
        if arkit.lower() in alias:
            cites.append(('godot_face_modifier', alias[arkit.lower()][1]))
        if not blended:
            routes.append({'arkit': arkit, 'outputs': [ue], 'basis': 'one to one', 'cites': cites})
        elif ue in splits:
            parts, lines = splits[ue]
            routes.append({'arkit': arkit, 'outputs': sorted(parts), 'basis': 'copied into both parts of a weighted '
                           f'split ({", ".join(f"{p} {w:g}" for p, w in sorted(parts.items()))}, sum 1)',
                           'cites': cites + [('vrcft_simple_expressions', n) for n in lines]})
        else:
            ft = 'FT_' + re.sub(r'(?<!^)(?=[A-Z])', '_', ue).upper()
            if ft in unified:
                parts, uline = unified[ft]
                outputs = [ft_to_unified(p) for p in parts]
                cites.append(('godot_face_modifier', uline))
            elif ue in means:
                outputs, mlines = means[ue]
                cites += [('vrcft_code_parameters', n) for n in mlines]
            else:
                raise SystemExit(f'no parts for blended {ue}')
            if ue in means:
                if sorted(means[ue][0]) != sorted(outputs):
                    raise SystemExit(f'{ue}: VRCFT and Godot disagree on its parts')
                cites += [('vrcft_code_parameters', n) for n in means[ue][1] if ('vrcft_code_parameters', n) not in cites]
            routes.append({'arkit': arkit, 'outputs': sorted(outputs), 'basis': 'copied into the parts of a mean',
                           'cites': cites})
        covered.add(arkit)
    # ARKit names VRCFT's table leaves out but Godot's alias table carries (mouthLeft/Right).
    for arkit in arkit_names(texts['apple_blendshapes']):
        if arkit in covered or arkit.lower() not in alias:
            continue
        shape, line = alias[arkit.lower()]
        if shape in unified:
            parts, uline = unified[shape]
            routes.append({'arkit': arkit, 'outputs': sorted(ft_to_unified(p) for p in parts),
                           'basis': 'Godot alias only; copied into the parts of a blended shape',
                           'cites': [('godot_face_modifier', line), ('godot_face_modifier', uline)]})
    return routes


def vrm_blinks(texts) -> list[dict]:
    """FB2 EYES_CLOSED_L/R -> VRM blinkLeft/Right, by the side each text names."""
    xr, vrm = texts['xr_fb2'], texts['vrm_expressions']
    closed = {}
    for number, line in enumerate(xr, 1):
        if m := re.match(r'ename:XR_FACE_EXPRESSION2_(EYES_CLOSED_([LR]))_FB lowers the top eyelid to cover$', line):
            if re.match(rf'the {"left" if m.group(2) == "L" else "right"} eye\.$', xr[number]):
                closed[m.group(2)] = (m.group(1), number)
    pairs = []
    for number, line in enumerate(vrm, 1):
        if m := re.match(r'^\| (blink(Left|Right))\s+\| Close (?:the )?(left|right) eyelid\s*\|$', line):
            side = 'L' if m.group(3) == 'left' else 'R'
            channel, xline = closed[side]
            pairs.append({'fb2': channel, 'vrm': m.group(1),
                          'cites': [('xr_fb2', xline), ('vrm_expressions', number)]})
    return pairs


def exclusive_line(lines: list[str]) -> int:
    """The line of the FB2 spec saying only one of two opposing gaze directions is non-zero."""
    found = [n for n, line in enumerate(lines, 1) if 'only one of the pair' in line]
    if len(found) != 1:
        raise SystemExit('the FB2 spec no longer states gaze exclusivity on one line')
    return found[0]


def distinct(names: list[str], flip: bool = False) -> dict[str, float]:
    """A different exact value for every input (k/128), so no two inputs can be confused."""
    return {n: (1.0 - (k + 1) / 128 if flip else (k + 1) / 128) for k, n in enumerate(sorted(names))}


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
    seconds = second_sources(routes, texts)
    unified_routes = ue_routes(texts)
    blinks = vrm_blinks(texts)

    table = io.StringIO()
    writer = csv.writer(table, lineterminator='\n')
    writer.writerow(['arkit', 'fb2_inputs', 'route', 'sources', 'second_sources', 'second_source_lines', 'notes'])
    for r in routes:
        second = seconds[r['arkit']]
        writer.writerow([r['arkit'], ';'.join(f'{k}*{v:g}' for k, v in sorted(r['inputs'].items())),
                         r['route'], ';'.join(f'{n}:L{line}' for n, line in r['cites']),
                         ';'.join(second['counted']), ';'.join(f'{n}:L{line}' for n, line in second['cites']),
                         '; '.join(second['notes'])])
    (ROOT / 'tests/fixtures/godot_fb2_rules.csv').write_text(table.getvalue(), encoding='utf-8')

    cases = []
    for r in routes:
        inputs = sorted(r['inputs'])
        if len(inputs) == 1:
            values = [(level,) for level in LEVELS]
        else:
            values = [pair for pair in PAIRS] if len(inputs) == 2 else list(QUADS) if len(inputs) == 4 else []
        for value in values:
            frame = {FB2.format(name): v for name, v in zip(inputs, value)}
            expected = sum(r['inputs'][name] * v for name, v in zip(inputs, value))
            cases.append({'mapping_kind': 'fb2_to_arkit', 'inputs': frame,
                          'expected': {ARKIT.format(r['arkit']): expected},
                          'sources': cite(r['cites'])})
    # Every input at once, each with its own value, in both directions of the
    # route table: a halved rule or a rule reading the wrong input changes its
    # own output and cannot be hidden by another rule.
    fb2_inputs = sorted({name for r in routes for name in r['inputs']})
    owner = {}
    for r in routes:
        for name in r['inputs']:
            if name in owner:
                raise SystemExit(f'{name} is read by two routes, so its inverse is ambiguous')
            owner[name] = r['arkit']
    for flip in (False, True):
        values = distinct(fb2_inputs, flip)
        cases.append({'mapping_kind': 'fb2_to_arkit', 'inputs': {FB2.format(n): v for n, v in values.items()},
                      'expected': {ARKIT.format(r['arkit']): sum(w * values[n] for n, w in r['inputs'].items())
                                   for r in routes},
                      'sources': cite([c for r in routes for c in r['cites']])})
        arkit_values = distinct([r['arkit'] for r in routes], flip)
        # FB2 allows only one of two opposing gaze directions to be non-zero, so
        # each frame sets one ARKit direction of each pair, the other frame the other.
        for side in 'LR':
            for pair in (('LEFT', 'RIGHT'), ('UP', 'DOWN')):
                arkit_values[owner[f'EYES_LOOK_{pair[0 if flip else 1]}_{side}']] = 0.0
        cases.append({'mapping_kind': 'arkit_to_fb2', 'inputs': {ARKIT.format(a): v for a, v in arkit_values.items()},
                      'expected': {FB2.format(n): arkit_values[owner[n]] for n in fb2_inputs},
                      'sources': cite([c for r in routes for c in r['cites']] + [('xr_fb2', exclusive_line(texts['xr_fb2']))])})
        ue_values = distinct([r['arkit'] for r in unified_routes], flip)
        cases.append({'mapping_kind': 'arkit_to_ue', 'inputs': {ARKIT.format(a): v for a, v in ue_values.items()},
                      'expected': {UE.format(o): ue_values[r['arkit']] for r in unified_routes for o in r['outputs']},
                      'sources': cite([c for r in unified_routes for c in r['cites']])})
        blink_values = distinct([p['fb2'] for p in blinks], flip)
        cases.append({'mapping_kind': 'fb2_to_vrm', 'inputs': {FB2.format(p['fb2']): blink_values[p['fb2']] for p in blinks},
                      'expected': {VRM.format(p['vrm']): blink_values[p['fb2']] for p in blinks},
                      'sources': cite([c for p in blinks for c in p['cites']])})
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
              'unified_routes': [{k: v for k, v in r.items() if k != 'cites'} | {'sources': cite(r['cites'])}
                                 for r in unified_routes],
              'blink_pairs': [{k: v for k, v in p.items() if k != 'cites'} | {'sources': cite(p['cites'])}
                              for p in blinks],
              # The FB or ARKit name on each row of VRCFT's two tables, exactly as written,
              # so a rule citing a table can be checked to name a signal it really lists.
              'vrcft_labels': {name: sorted({other for _, other, _, _ in vrcft_table(texts[name])})
                               for name in ('vrcft_docs_arkit', 'vrcft_docs_movement')},
              'cases': cases}
    (ROOT / 'tests/fixtures/fb2_goldens.json').write_text(json.dumps(output, indent=1, sort_keys=True) + '\n',
                                                          encoding='utf-8')
    print(f'{len(routes)} ARKit routes, {len(unified_routes)} Unified routes '
          f'({sum(len(r["outputs"]) for r in unified_routes)} outputs), {len(blinks)} blink pairs, '
          f'{len(pairs)} viseme pairs, {len(cases)} cases')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
