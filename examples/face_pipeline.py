#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Drive the ICT-FaceKit face with FB2 frames, directly and through RCEF, and compare.

Usage: python examples/face_pipeline.py [--cache DIR] [--out DIR] [--frames CSV]

The ICT-FaceKit files go to ~/.cache/rcef-ict-facekit and the outputs to
~/.cache/rcef-examples/face ($XDG_CACHE_HOME instead of ~/.cache when it is
set), so nothing is written into the checkout unless asked.

For every frame of the FB2 input this builds two sets of ICT-FaceKit morph
weights and evaluates both with msf_tools.evaluate_geometry:

- direct: the FB2 values routed to ARKit-named shapes as the Godot and VRCFT
  sources route them (tests/fixtures/godot_fb2_rules.csv, derived from the
  pinned source bytes). ICT splits browInnerUp and cheekPuff into halves, so
  each half gets its own FB2 side here.
- translated: the ARKit weights RCEF's proposed rules produce. Both halves of
  a split shape get the one translated value.

It writes, under --out: the GLB and sidecar it built, the translated weights,
per-frame vertex positions (float32 xyz), one shared triangle index file
(uint32), per-vertex difference colours (float32 RGB), frames.json describing
every frame, and a residual report as CSV and Markdown.

This shows name and meaning correspondence on one rig. It says nothing about
calibration: neither provider publishes its gain, so equal weights are assumed
to mean equal expressions.
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

import ict_facekit
import rcef_translate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ARKIT = 'arkit.coefficient.'
EXACT_TOLERANCE = 1e-9
CAPTION = ('Name and meaning correspondence on one rig (ICT-FaceKit), not calibration: the providers do not '
           'publish their gains, so equal weights are assumed to mean equal expressions.')
# ICT-FaceKit splits these ARKit coefficients into left and right halves (its README, line 150).
SPLIT = {'browInnerUp': ('browInnerUp_L', 'browInnerUp_R'), 'cheekPuff': ('cheekPuff_L', 'cheekPuff_R')}


def ict_name(arkit: str) -> str:
    for side, suffix in (('Left', '_L'), ('Right', '_R')):
        if arkit.endswith(side):
            return arkit[:-len(side)] + suffix
    return arkit


@cache
def source_routes() -> dict[str, dict[str, float]]:
    """ARKit name -> {FB2 channel: weight}, as derived from the pinned sources."""
    with (ROOT / 'tests/fixtures/godot_fb2_rules.csv').open(encoding='utf-8', newline='') as handle:
        return {row['arkit']: {name: float(weight) for name, weight in
                               (part.split('*') for part in row['fb2_inputs'].split(';'))}
                for row in csv.DictReader(handle)}


def direct_inputs(targets: list[str]) -> dict[str, str]:
    """ICT target -> the FB2 channel that drives it directly."""
    routes = source_routes()
    driven = {}
    for arkit, route in routes.items():
        if arkit in SPLIT:
            left, right = SPLIT[arkit]
            # Both providers name sides from the subject's own face.
            driven[left] = next(n for n in route if n.endswith('_L'))
            driven[right] = next(n for n in route if n.endswith('_R'))
        elif len(route) == 1 and next(iter(route.values())) == 1.0:
            driven[ict_name(arkit)] = next(iter(route))
    missing = [t for t in targets if t not in driven]
    if missing:
        raise SystemExit(f'no source route drives {missing}')
    return {t: driven[t] for t in targets}


def require(result):
    if not result.ok:
        raise SystemExit(result.report.to_dict())
    return result.value


def target_signals(translator, targets: list[str]) -> dict[str, str]:
    """ICT target -> the ARKit signal that drives it; both halves of a split shape share one."""
    by_target = {ict_name(o[len(ARKIT):]): o for o in translator.outputs}
    for arkit, halves in SPLIT.items():
        for half in halves:
            by_target[half] = ARKIT + arkit
    return {t: by_target[t] for t in targets}


def bind(snapshot, translator, targets) -> msf.Sidecar:
    """Bind each ICT target to the ARKit signal that drives it, as "<signal>:<target>"."""
    bindings = []
    for index, (target, sid) in enumerate(target_signals(translator, targets).items()):
        signal = translator.signals[sid]
        bindings.append(require(msf.morph_binding(snapshot, {**signal, 'id': f'{signal["id"]}:{target}'}, 0, index)))
    return require(msf.annotate_asset(snapshot, {'bindings': bindings, 'metadata': {
        'note': 'ICT-FaceKit target driven by an ARKit coefficient; both halves of a split shape share one coefficient.'}}))


def check_channels(translator, frame: dict, result: dict, targets: list[str]) -> list[dict]:
    """The weight oracles for one frame, per ICT target, in target order.

    Each entry has the direct and translated weights (None when invalid or
    refused), the residual, its bound, a status and whether the oracle passes.
    """
    drives = direct_inputs(targets)
    channels = []
    for target, signal in target_signals(translator, targets).items():
        fb2 = translator.signal_id(drives[target])
        direct = frame['values'][fb2] if translator.valid(fb2, frame['flags']) else None
        value = result['values'].get(signal)
        arkit = signal[len(ARKIT):]
        passes = True
        if value is None:
            status, residual, bound = 'refused', '', ''
        elif direct is None:
            status, residual, bound = 'direct input invalid', '', ''
        else:
            residual = abs(value - direct)
            if arkit in SPLIT:
                left, right = (frame['values'][translator.signal_id(drives[h])] for h in SPLIT[arkit])
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
        channels.append({'target': target, 'arkit': arkit, 'fb2': drives[target], 'direct': direct,
                         'translated': value, 'residual': residual, 'bound': bound, 'status': status,
                         'passes': passes})
    return channels


def heat(delta: float, scale: float) -> tuple[float, float, float]:
    """Blue at zero, through green, to red at `scale` and above."""
    x = min(delta / scale, 1.0) if scale > 0 else 0.0
    return (min(1.0, 2 * x), 1.0 - abs(2 * x - 1.0), max(0.0, 1.0 - 2 * x))


def write_f32(path: Path, values) -> None:
    flat = [c for v in values for c in v]
    path.write_bytes(struct.pack(f'<{len(flat)}f', *flat))


def arguments(argv=None) -> argparse.Namespace:
    cache = rcef_translate.cache_home()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--cache', type=Path, default=cache / 'rcef-ict-facekit',
                        help='directory for the ICT-FaceKit files (default: %(default)s)')
    parser.add_argument('--out', type=Path, default=cache / 'rcef-examples/face',
                        help='output directory (default: %(default)s)')
    parser.add_argument('--frames', type=Path, default=HERE / 'data/fb2_demo_frames.csv')
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = arguments(argv)
    out = args.out
    for sub in ('mesh/direct', 'mesh/translated', 'mesh/difference'):
        (out / sub).mkdir(parents=True, exist_ok=True)

    ict_facekit.fetch(args.cache)
    glb, targets, indices = ict_facekit.build_glb(args.cache)
    (out / 'ict_facekit_subset.glb').write_bytes(glb)
    snapshot = require(msf.inspect_asset(glb, 'glb'))

    translator = rcef_translate.fb2_to_arkit()
    frames = translator.read(args.frames)
    translated = translator.translate(frames)
    translator.write(translated, out / 'fb2_to_arkit.csv')
    sidecar = bind(snapshot, translator, targets)
    (out / 'ict_facekit_subset.sidecar.json').write_bytes(msf.canonical_json(sidecar.document))

    (out / 'mesh/indices.u32').write_bytes(struct.pack(f'<{len(indices)}I', *indices))
    evaluated = {}

    def positions(weights):
        key = tuple(weights)
        if key not in evaluated:
            geometry = require(msf.evaluate_geometry(snapshot, morph_weights={0: list(weights)}))
            evaluated[key] = geometry.instances[0]['primitives'][0]['positions']
        return evaluated[key]

    neutral = positions([0.0] * len(targets))
    target_norms = []
    for index in range(len(targets)):
        unit = [0.0] * len(targets)
        unit[index] = 1.0
        target_norms.append(max(math.dist(p, q) for p, q in zip(positions(unit), neutral)))
    low = [min(p[k] for p in neutral) for k in range(3)]
    high = [max(p[k] for p in neutral) for k in range(3)]
    heat_scale = 0.1 * max(target_norms)

    residual_rows, manifest = [], []
    for number, (frame, result) in enumerate(zip(frames, translated)):
        channels = check_channels(translator, frame, result, targets)
        direct_w = [c['direct'] or 0.0 for c in channels]
        translated_w = [c['translated'] or 0.0 for c in channels]
        oracle_ok = all(c['passes'] for c in channels)
        mesh_bound = sum(c['residual'] * norm for c, norm in zip(channels, target_norms) if c['residual'] != '')
        direct_p, translated_p = positions(direct_w), positions(translated_w)
        deltas = [math.dist(p, q) for p, q in zip(direct_p, translated_p)]
        max_delta = max(deltas)
        mesh_ok = max_delta <= mesh_bound + EXACT_TOLERANCE
        oracle_ok &= mesh_ok
        stem = f'{number:04d}.f32'
        write_f32(out / 'mesh/direct' / stem, direct_p)
        write_f32(out / 'mesh/translated' / stem, translated_p)
        write_f32(out / 'mesh/difference' / stem, (heat(d, heat_scale) for d in deltas))
        labels = [f'refused by {r}' for r in result['refused']]
        labels += [f'{d}: no RCEF rule (and no ICT-FaceKit shape); not shown' for d in result['dropped']]
        manifest.append({'frame': number, 'time': frame['time'], 'segment': frame['segment'],
                         'direct': f'mesh/direct/{stem}', 'translated': f'mesh/translated/{stem}',
                         'difference_colors': f'mesh/difference/{stem}', 'labels': labels,
                         'max_vertex_difference': max_delta, 'vertex_difference_bound': mesh_bound,
                         'oracles_pass': oracle_ok})
        for c in channels:
            residual_rows.append({'frame': number, 'time': f'{frame["time"]:.6f}', 'segment': frame['segment'], **c})

    (out / 'frames.json').write_text(json.dumps({
        'caption': CAPTION, 'indices': 'mesh/indices.u32', 'vertex_count': len(neutral),
        'positions_format': 'little-endian float32 xyz per vertex, mesh-local, in ICT-FaceKit model units',
        'difference_colors_format': 'little-endian float32 RGB per vertex; blue = 0, red >= heat_scale',
        'heat_scale': heat_scale, 'bounds': {'min': low, 'max': high},
        'targets': targets, 'frames': manifest}, indent=1), encoding='utf-8')
    write_report(out, residual_rows, manifest, targets)
    failed = [m['frame'] for m in manifest if not m['oracles_pass']]
    print(f'{len(frames)} frames, {len(evaluated)} geometry evaluations -> {out}')
    print('all oracles pass' if not failed else f'oracles FAIL on frames {failed}')
    return 1 if failed else 0


def write_report(out: Path, rows: list[dict], manifest: list[dict], targets: list[str]) -> None:
    columns = ['frame', 'time', 'segment', 'target', 'arkit', 'fb2', 'direct', 'translated', 'residual', 'bound', 'status']
    with (out / 'residuals.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, columns, lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        writer.writerows({k: ('' if r[k] is None else r[k]) for k in columns} for r in rows)
    statuses = {}
    for r in rows:
        statuses.setdefault(r['status'], 0)
        statuses[r['status']] += 1
    worst_exact = max((r['residual'] for r in rows if r['status'] == 'exact (moving)'), default=0.0)
    moving = {t: 0 for t in targets}
    for r in rows:
        moving[r['target']] += bool(r['direct'])
    drives = {r['target']: (r['arkit'], r['fb2']) for r in rows}
    lines = ['# RCEF FB2 → ARKit on ICT-FaceKit: residual report', '', f'**{CAPTION}**', '',
             f'{len(manifest)} frames, {len(targets)} ICT-FaceKit shapes. Direct weights come from the Godot and VRCFT '
             'source routes; translated weights from RCEF\'s proposed rules.', '',
             '## Oracles', '',
             f'- Exact rules: residual ≤ 1e-9. Largest residual seen: {worst_exact:g}.',
             '- Averaged pairs (browInnerUp, cheekPuff): each half within |L − R| / 2 of its own side.',
             '- Mesh: largest vertex difference ≤ Σ residual × the largest vertex move of that shape.',
             '- Refused channels are labelled on their frame (the mesh shows them at rest, with the label, never as a '
             'silent zero); dropped channels are listed.', '',
             f'Frames where every oracle passes: {sum(m["oracles_pass"] for m in manifest)} of {len(manifest)}.', '',
             '| Channel status | Count |', '|---|---|']
    lines += [f'| {s} | {n} |' for s, n in sorted(statuses.items())]
    lines += ['', '"At rest in both paths" counts channels that are zero in both the direct and the translated '
              'weights. They cannot fail, so they are not counted as exact.', '',
              '## Frames in which each shape moves', '',
              'Frames in which the FB2 input that drives the shape directly is not zero. A rule is only tested '
              'where its shape moves; every shape should move in some frame.', '',
              '| ICT-FaceKit shape | ARKit | FB2 (direct) | Frames moving |', '|---|---|---|---|']
    lines += [f'| {t} | {drives[t][0]} | {drives[t][1]} | {moving[t]} |' for t in targets]
    lines += ['', '## Per frame', '', '| Frame | Time | Segment | Max vertex difference | Bound | Oracles | Labels |',
              '|---|---|---|---|---|---|---|']
    for m in manifest:
        lines.append(f'| {m["frame"]} | {m["time"]:.3f} | {m["segment"]} | {m["max_vertex_difference"]:.3g} | '
                     f'{m["vertex_difference_bound"]:.3g} | {"pass" if m["oracles_pass"] else "FAIL"} | '
                     f'{"; ".join(m["labels"])} |')
    lines += ['', 'Per-channel values are in residuals.csv.', '']
    (out / 'residuals.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    raise SystemExit(main())
