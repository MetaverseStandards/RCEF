#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Drive a face rig with FB2 frames, directly and through RCEF, and compare.

Usage: python examples/face_pipeline.py [--rig RIG] [--cache DIR] [--out DIR] [--frames CSV]

RIG is rocketbox-female (the default), rocketbox-male or ict. Rig files go to a
cache (~/.cache/rcef-face-rigs, or ~/.cache/rcef-ict-facekit for ict) and the
outputs to ~/.cache/rcef-examples/face/RIG ($XDG_CACHE_HOME instead of ~/.cache
when it is set), so nothing is written into the checkout unless asked. The
frames default to the expression library (examples/data/fb2_expression_frames.csv).

For every frame this builds morph weights for the rig's ARKit shapes twice and
evaluates both with msf_tools.evaluate_geometry:

- direct: the FB2 values routed to ARKit names as the Godot and VRCFT sources
  route them (tests/fixtures/godot_fb2_rules.csv, derived from the pinned
  source bytes). ICT splits browInnerUp and cheekPuff into halves, so on ICT
  each half takes its own FB2 side.
- translated: the ARKit weights RCEF's proposed mappings produce. A shape that
  no RCEF mapping writes yet stays at rest here and is labelled. This is not an
  oracle failure, but its whole direct movement counts towards the mesh bound.

On the Rocketbox rigs a third render drives Rocketbox's own FACS action-unit
shapes with the expression's AUs. It is a labelled semantic comparison
between two independently authored shape sets, not an oracle.

It writes, under --out: the sidecar binding each ARKit shape, the translated
weights, per-frame vertex positions (float32 xyz), one shared triangle index
file (uint32), per-vertex difference colours (float32 RGB), frames.json
describing every frame, and a residual report as CSV and Markdown.

This shows that names and meanings correspond on one rig. It says nothing
about calibration: neither provider publishes its gain, so equal weights are
assumed to mean equal expressions.
"""
from __future__ import annotations
import argparse
import csv
from functools import cache
import json
import math
from pathlib import Path
import struct

import msf_tools as msf

import make_expression_frames
import rcef_translate
import rigs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ARKIT = 'arkit.coefficient.'
EXACT_TOLERANCE = 1e-9
CAPTION = ('Name and meaning correspondence on one rig, not calibration: the providers do not publish their gains, '
           'so equal weights are assumed to mean equal expressions.')
FACS_CAPTION = ('Semantic difference between two authored shape sets (Rocketbox FACS action units against RCEF-translated '
                'ARKit shapes); not an error measure.')
UNCOVERED = 'no RCEF rule yet (direct only)'


@cache
def source_routes() -> dict[str, dict[str, float]]:
    """ARKit name -> {FB2 channel: weight}, as derived from the pinned sources."""
    with (ROOT / 'tests/fixtures/godot_fb2_rules.csv').open(encoding='utf-8', newline='') as handle:
        return {row['arkit']: {name: float(weight) for name, weight in
                               (part.split('*') for part in row['fb2_inputs'].split(';'))}
                for row in csv.DictReader(handle)}


def face_targets(shapes: list[tuple[int, str, str | None]], names: list[str]) -> list[dict]:
    """For each (target index, ARKit name, half side): what drives it directly and how it is checked.

    A whole ARKit shape takes the source route, weights included. A half of a
    split shape takes its own FB2 side; the translated value, one coefficient
    for both halves, is checked against half the L/R difference.
    """
    routes = source_routes()
    targets = []
    for index, arkit, side in shapes:
        route = routes[arkit]
        pair = None
        if side:
            pair = (next(n for n in route if n.endswith('_L')), next(n for n in route if n.endswith('_R')))
            # Both providers name sides from the subject's own face.
            route = {pair[0 if side == 'L' else 1]: 1.0}
        targets.append({'index': index, 'name': names[index], 'arkit': arkit, 'route': route, 'pair': pair})
    return targets


def check_channels(translator, frame: dict, result: dict, targets: list[dict]) -> list[dict]:
    """The weight oracles for one frame, one entry per target.

    Each entry has the direct and translated weights (None when invalid,
    refused or not written by any rule), the residual, its bound, a status and
    whether the oracle passes.
    """
    channels = []
    for t in targets:
        signal = ARKIT + t['arkit']
        sids = {name: translator.signal_id(name) for name in t['route']}
        valid = all(translator.valid(sid, frame['flags']) for sid in sids.values())
        direct = sum(w * frame['values'][sids[n]] for n, w in t['route'].items()) if valid else None
        value = result['values'].get(signal)
        passes, residual, bound = True, '', ''
        if signal not in translator.outputs:
            status = UNCOVERED if direct != 0 else 'at rest in both paths'
        elif value is None:
            status = 'refused'
        elif direct is None:
            status = 'direct input invalid'
        else:
            residual = abs(value - direct)
            if t['pair']:
                left, right = (frame['values'][translator.signal_id(n)] for n in t['pair'])
                bound = abs(left - right) / 2
                passes = residual <= bound + EXACT_TOLERANCE
                status = ('averaged pair, within half the L/R difference' if passes
                          else 'averaged pair, OVER half the L/R difference')
            else:
                bound = EXACT_TOLERANCE
                passes = residual <= bound
                status = 'exact (moving)' if passes else 'exact rule, RESIDUAL OVER 1e-9'
            if direct == 0 and value == 0:
                status = 'at rest in both paths'
        channels.append({'index': t['index'], 'target': t['name'], 'arkit': t['arkit'],
                         'fb2': ';'.join(f'{n}*{w:g}' for n, w in t['route'].items()), 'direct': direct,
                         'translated': value, 'residual': residual, 'bound': bound, 'status': status,
                         'passes': passes})
    return channels


def facs_weights(rig, expression: dict | None, amount: float, library: dict) -> tuple[dict[int, float], list[str]]:
    """Rocketbox AU-shape weights for an expression at `amount`, and notes on AUs it has no shape for."""
    if expression is None or amount == 0:
        return {}, []
    weights, notes = {}, []
    for key, value in expression['aus'].items():
        found = rigs.facs_targets(rig.targets, key)
        side, au = (key[0], key[1:]) if key[0] in 'LR' else ('', key)
        if found is None and au == '46':
            # A wink is one eye closing; Rocketbox has one-sided AU 43 shapes but no AU 46.
            found = rigs.facs_targets(rig.targets, side + '43')
            if found:
                notes.append(f'FACS panel: Rocketbox has no AU 46 (wink) shape; AU {key} is shown as AU 43 '
                             '(eyes closed) on that side')
        if found is None:
            notes.append(f'FACS panel: Rocketbox has no AU {key} shape')
            continue
        for index in found:
            weights[index] = make_expression_frames.intensity(value, library) * amount
    return weights, notes


def bind(rig, translator) -> msf.Sidecar:
    """Bind each ARKit shape to its ARKit signal, as "<signal>:<target>"."""
    bindings = []
    for index, arkit, _ in rig.shapes:
        signal = translator.signals[ARKIT + arkit]
        target = rig.targets[index]
        bindings.append(rigs.require(msf.morph_binding(rig.snapshot, {**signal, 'id': f'{signal["id"]}:{target}'},
                                                       rig.node, index)))
    return rigs.require(msf.annotate_asset(rig.snapshot, {'bindings': bindings, 'metadata': {
        'note': 'Rig shape driven by an ARKit coefficient; both halves of a split shape share one coefficient.'}}))


def heat(delta: float, scale: float) -> tuple[float, float, float]:
    """Blue at zero, through green, to red at `scale` and above."""
    x = min(delta / scale, 1.0) if scale > 0 else 0.0
    return (min(1.0, 2 * x), 1.0 - abs(2 * x - 1.0), max(0.0, 1.0 - 2 * x))


def write_f32(path: Path, values) -> None:
    flat = [c for v in values for c in v]
    path.write_bytes(struct.pack(f'<{len(flat)}f', *flat))


def arguments(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--rig', choices=['rocketbox-female', 'rocketbox-male', 'ict'], default='rocketbox-female')
    parser.add_argument('--cache', type=Path, help='directory for the rig files (default: a per-rig cache)')
    parser.add_argument('--out', type=Path, help='output directory (default: ~/.cache/rcef-examples/face/RIG)')
    parser.add_argument('--frames', type=Path, default=HERE / 'data/fb2_expression_frames.csv')
    args = parser.parse_args(argv)
    home = rcef_translate.cache_home()
    args.cache = args.cache or home / ('rcef-ict-facekit' if args.rig == 'ict' else 'rcef-face-rigs')
    args.out = args.out or home / 'rcef-examples/face' / args.rig
    return args


def main(argv=None) -> int:
    args = arguments(argv)
    out = args.out
    panels = ['direct', 'translated', 'difference']
    rig = rigs.load(args.rig, args.cache)
    if rig.facs:
        panels += ['facs', 'facs_difference']
    for panel in panels:
        (out / 'mesh' / panel).mkdir(parents=True, exist_ok=True)
    library = make_expression_frames.library()
    expressions = {e['name']: e for e in library['expressions']}

    translator = rcef_translate.fb2_to_arkit()
    frames = translator.read(args.frames)
    translated = translator.translate(frames)
    translator.write(translated, out / 'fb2_to_arkit.csv')
    (out / 'sidecar.json').write_bytes(msf.canonical_json(bind(rig, translator).document))
    targets = face_targets(rig.shapes, rig.targets)

    indices = rig.indices()
    (out / 'mesh/indices.u32').write_bytes(struct.pack(f'<{len(indices)}I', *indices))
    evaluated, norms = {}, {}

    def positions(weights: dict[int, float]):
        vector = [0.0] * len(rig.targets)
        for index, w in weights.items():
            vector[index] = w
        key = tuple(vector)
        if key not in evaluated:
            geometry = rigs.require(msf.evaluate_geometry(rig.snapshot, morph_weights={rig.node: vector}))
            evaluated[key] = [p for instance in geometry.instances for primitive in instance['primitives']
                              for p in primitive['positions']]
        return evaluated[key]

    neutral = positions({})

    def norm(index: int) -> float:
        """The largest vertex move of one shape at full weight; morphs are linear, so this bounds its effect."""
        if index not in norms:
            norms[index] = max(math.dist(p, q) for p, q in zip(positions({index: 1.0}), neutral))
        return norms[index]

    low = [min(p[k] for p in neutral) for k in range(3)]
    high = [max(p[k] for p in neutral) for k in range(3)]
    heat_scale = None
    residual_rows, manifest = [], []
    for number, (frame, result) in enumerate(zip(frames, translated)):
        channels = check_channels(translator, frame, result, targets)
        direct_w = {c['index']: c['direct'] for c in channels if c['direct']}
        translated_w = {c['index']: c['translated'] for c in channels if c['translated']}
        oracle_ok = all(c['passes'] for c in channels)
        mesh_bound = sum(c['residual'] * norm(c['index']) for c in channels if c['residual'])
        mesh_bound += sum(abs(c['direct']) * norm(c['index']) for c in channels if c['status'] == UNCOVERED and c['direct'])
        direct_p, translated_p = positions(direct_w), positions(translated_w)
        deltas = [math.dist(p, q) for p, q in zip(direct_p, translated_p)]
        if heat_scale is None:
            # A tenth of the largest move of the rig's jaw: visible on any face size.
            heat_scale = 0.1 * norm(next(t['index'] for t in targets if t['arkit'] == 'jawOpen'))
        max_delta = max(deltas)
        oracle_ok &= max_delta <= mesh_bound + EXACT_TOLERANCE
        stem = f'{number:04d}.f32'
        write_f32(out / 'mesh/direct' / stem, direct_p)
        write_f32(out / 'mesh/translated' / stem, translated_p)
        write_f32(out / 'mesh/difference' / stem, (heat(d, heat_scale) for d in deltas))
        labels = [f'refused by {r}' for r in result['refused']]
        labels += [f'{d}: no RCEF rule; not in the translated weights' for d in result['dropped']]
        uncovered = [c['arkit'] for c in channels if c['status'] == UNCOVERED and c['direct']]
        if uncovered:
            labels.append(f'no RCEF rule yet, direct render only: {", ".join(uncovered)}')
        if frame['labels'].get('note'):
            labels.append(frame['labels']['note'])
        entry = {'frame': number, 'time': frame['time'], 'segment': frame['segment'],
                 'phase': frame['labels'].get('phase', ''), 'amount': float(frame['labels'].get('amount') or 0),
                 **{panel: f'mesh/{panel}/{stem}' for panel in ('direct', 'translated')},
                 'difference_colors': f'mesh/difference/{stem}', 'labels': labels,
                 'max_vertex_difference': max_delta, 'vertex_difference_bound': mesh_bound, 'oracles_pass': oracle_ok}
        if rig.facs:
            weights, notes = facs_weights(rig, expressions.get(frame['segment']), entry['amount'], library)
            facs_p = positions(weights)
            write_f32(out / 'mesh/facs' / stem, facs_p)
            write_f32(out / 'mesh/facs_difference' / stem,
                      (heat(math.dist(p, q), heat_scale) for p, q in zip(facs_p, translated_p)))
            entry.update({'facs': f'mesh/facs/{stem}', 'facs_difference_colors': f'mesh/facs_difference/{stem}',
                          'facs_labels': notes})
        manifest.append(entry)
        for c in channels:
            residual_rows.append({'frame': number, 'time': f'{frame["time"]:.6f}', 'segment': frame['segment'], **c})

    (out / 'frames.json').write_text(json.dumps({
        'rig': rig.name, 'credit': rig.credit, 'caption': CAPTION,
        **({'facs_caption': FACS_CAPTION} if rig.facs else {}),
        'panels': panels, 'indices': 'mesh/indices.u32', 'vertex_count': len(neutral),
        'positions_format': 'little-endian float32 xyz per vertex, every mesh of the rig in node order, rig units',
        'difference_colors_format': 'little-endian float32 RGB per vertex; blue = 0, red >= heat_scale',
        'heat_scale': heat_scale, 'bounds': {'min': low, 'max': high},
        'targets': [t['name'] for t in targets], 'frames': manifest}, indent=1), encoding='utf-8')
    write_report(out, rig, residual_rows, manifest, targets)
    failed = [m['frame'] for m in manifest if not m['oracles_pass']]
    print(f'{rig.name}: {len(frames)} frames, {len(evaluated)} geometry evaluations -> {out}')
    print('all oracles pass' if not failed else f'oracles FAIL on frames {failed}')
    return 1 if failed else 0


def write_report(out: Path, rig, rows: list[dict], manifest: list[dict], targets: list[dict]) -> None:
    columns = ['frame', 'time', 'segment', 'target', 'arkit', 'fb2', 'direct', 'translated', 'residual', 'bound', 'status']
    with (out / 'residuals.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, columns, lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        writer.writerows({k: ('' if r[k] is None else r[k]) for k in columns} for r in rows)
    statuses = {}
    for r in rows:
        statuses[r['status']] = statuses.get(r['status'], 0) + 1
    worst_exact = max((r['residual'] for r in rows if r['status'] == 'exact (moving)'), default=0.0)
    moving = {t['name']: 0 for t in targets}
    for r in rows:
        moving[r['target']] += bool(r['direct'])
    drives = {r['target']: (r['arkit'], r['fb2'], r['status'] == UNCOVERED) for r in rows}
    lines = [f'# RCEF FB2 → ARKit on {rig.name}: residual report', '', f'**{CAPTION}**', '', f'Rig: {rig.credit}.', '',
             f'{len(manifest)} frames, {len(targets)} ARKit shapes. Direct weights come from the Godot and VRCFT '
             'source routes; translated weights from RCEF\'s proposed rules.', '',
             '## Oracles', '',
             f'- Exact rules: residual ≤ 1e-9. Largest residual seen: {worst_exact:g}.',
             '- Averaged pairs on a rig that splits them (ICT browInnerUp, cheekPuff): each half within |L − R| / 2 '
             'of its own side.',
             '- Mesh: largest vertex difference ≤ Σ residual × the largest vertex move of that shape, plus the whole '
             'direct movement of shapes no RCEF rule writes yet.',
             '- Refused channels are labelled on their frame (the mesh shows them at rest, with the label, never as a '
             'silent zero); dropped channels and shapes without a rule are listed.', '',
             f'Frames where every oracle passes: {sum(m["oracles_pass"] for m in manifest)} of {len(manifest)}.', '',
             '| Channel status | Count |', '|---|---|']
    lines += [f'| {s} | {n} |' for s, n in sorted(statuses.items())]
    lines += ['', '"At rest in both paths" counts channels that are zero in both the direct and the translated '
              f'weights. They cannot fail, so they are not counted as exact. "{UNCOVERED}" counts shapes that no RCEF '
              'rule writes yet; they are shown in the direct render only.', '',
              '## Frames in which each shape moves', '',
              'Frames in which the FB2 input that drives the shape directly is not zero. A rule is only tested '
              'where its shape moves.', '',
              '| Rig shape | ARKit | FB2 (direct) | RCEF rule | Frames moving |', '|---|---|---|---|---|']
    lines += [f'| {t} | {drives[t][0]} | {drives[t][1]} | {"none yet" if drives[t][2] else "yes"} | {moving[t]} |'
              for t in moving]
    lines += ['', '## Per frame', '',
              '| Frame | Time | Segment | Phase | Max vertex difference | Bound | Oracles | Labels |',
              '|---|---|---|---|---|---|---|---|']
    for m in manifest:
        lines.append(f'| {m["frame"]} | {m["time"]:.3f} | {m["segment"]} | {m["phase"]} | '
                     f'{m["max_vertex_difference"]:.3g} | {m["vertex_difference_bound"]:.3g} | '
                     f'{"pass" if m["oracles_pass"] else "FAIL"} | {"; ".join(m["labels"])} |')
    lines += ['', 'Per-channel values are in residuals.csv.', '']
    (out / 'residuals.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    raise SystemExit(main())
