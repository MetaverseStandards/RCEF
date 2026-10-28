#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render META viseme frames on a face: directly on Rocketbox, and through RCEF on a VRM model.

Usage: python examples/viseme_pipeline.py [--rig RIG] [--cache DIR] [--out DIR] [--frames CSV]

RIG is rocketbox-female (the default), rocketbox-male or vrm-twist. The frames
default to "bed car toe book" (examples/data/viseme_talk_frames.csv). Rig
files go to ~/.cache/rcef-face-rigs and outputs to
~/.cache/rcef-examples/visemes/RIG ($XDG_CACHE_HOME instead of ~/.cache when
it is set).

- Rocketbox has its own shapes for all 15 META visemes, so the frames drive
  them directly, by name. No translation is involved.
- The VRM sample has the five vowel presets. RCEF's visemes.to_vrm map
  translates the frames, and vrm_presets.py turns the presets into morph
  weights through the model's own binds ("translated"). The same binds driven
  through the vowel pairs scripts/derive_fb2_goldens.py read from the pinned
  sources (tests/fixtures/fb2_goldens.json) give "direct", independent of
  RCEF's mappings. The two morph weight vectors must agree within 1e-9.
  Consonants have no VRM preset and are labelled as dropped.
- The VRM path then shows the two winks from the expression library
  (examples/data/fb2_expression_frames.csv): RCEF's fb2.to_vrm map against
  the blink pairs read from the same sources, with the same check.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import struct

import msf_character_tools as msf

import face_pipeline
import rcef_translate
import rigs
import vrm_presets

HERE = Path(__file__).resolve().parent
TOLERANCE = 1e-9
GOLDENS = HERE.parent / 'tests/fixtures/fb2_goldens.json'
EXPRESSIONS = HERE / 'data/fb2_expression_frames.csv'


def vowel_presets(path: Path = GOLDENS) -> dict[str, str]:
    """META vowel -> VRM preset, as scripts/derive_fb2_goldens.py read them from the pinned VRM and META texts."""
    return {p['viseme']: p['vrm'] for p in json.loads(path.read_text(encoding='utf-8'))['viseme_pairs']}


def blink_presets(path: Path = GOLDENS) -> dict[str, str]:
    """FB2 eye closure -> VRM blink preset, as scripts/derive_fb2_goldens.py read them from the pinned texts."""
    return {p['fb2']: p['vrm'] for p in json.loads(path.read_text(encoding='utf-8'))['blink_pairs']}


def wink_frames(translator: rcef_translate.Translator, path: Path = EXPRESSIONS) -> list[dict]:
    return [f for f in translator.read(path) if f['segment'].startswith('wink')]


CAPTION = ('Phoneme-label correspondence, not calibration: no published table maps META visemes to VRM presets, and '
           'each model authors its own shapes.')


def arguments(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--rig', choices=['rocketbox-female', 'rocketbox-male', 'vrm-twist'], default='rocketbox-female')
    parser.add_argument('--cache', type=Path, help='directory for the rig files (default: ~/.cache/rcef-face-rigs)')
    parser.add_argument('--out', type=Path, help='output directory (default: ~/.cache/rcef-examples/visemes/RIG)')
    parser.add_argument('--frames', type=Path, default=HERE / 'data/viseme_talk_frames.csv')
    args = parser.parse_args(argv)
    home = rcef_translate.cache_home()
    args.cache = args.cache or home / 'rcef-face-rigs'
    args.out = args.out or home / 'rcef-examples/visemes' / args.rig
    return args


def vectors(snapshot, weights: dict[int, dict[int, float]]) -> dict[int, list[float]]:
    """Full morph weight vectors for the nodes that have weights."""
    document = snapshot.document
    out = {}
    for node, values in weights.items():
        count = len(document['meshes'][document['nodes'][node]['mesh']]['primitives'][0]['targets'])
        vector = [0.0] * count
        for index, w in values.items():
            vector[index] = w
        out[node] = vector
    return out


def max_difference(a: dict[int, dict[int, float]], b: dict[int, dict[int, float]]) -> float:
    keys = {(n, i) for w in (a, b) for n in w for i in w[n]}
    return max((abs(a.get(n, {}).get(i, 0.0) - b.get(n, {}).get(i, 0.0)) for n, i in keys), default=0.0)


def main(argv=None) -> int:
    args = arguments(argv)
    out = args.out
    rig = rigs.load(args.rig, args.cache)
    vrm = args.rig == 'vrm-twist'
    panels = ['direct', 'translated', 'difference'] if vrm else ['direct']
    for panel in panels:
        (out / 'mesh' / panel).mkdir(parents=True, exist_ok=True)
    translator = rcef_translate.visemes_to_vrm()
    frames = translator.read(args.frames)
    translated = translator.translate(frames) if vrm else [None] * len(frames)
    if translated[0] is not None:
        translator.write(translated, out / 'visemes_to_vrm.csv')
    jobs = [(translator, vowel_presets(), frame, result) for frame, result in zip(frames, translated)]
    if vrm:
        blinker = rcef_translate.fb2_to_vrm()
        winks = wink_frames(blinker)
        # The winks follow the talk without a gap.
        shift = frames[-1]['time'] + (winks[1]['time'] - winks[0]['time']) - winks[0]['time']
        for frame in winks:
            frame['time'] = round(frame['time'] + shift, 6)
        blinked = blinker.translate(winks)
        blinker.write(blinked, out / 'fb2_to_vrm.csv')
        jobs += [(blinker, blink_presets(), frame, result) for frame, result in zip(winks, blinked)]
    expressions = vrm_presets.presets(rig.snapshot.to_dict()['document']) if vrm else {}
    if not vrm and len(rig.visemes) != len(rigs.META_VISEME_ORDER):
        raise SystemExit(f'{rig.name}: expected a shape for each of the 15 META visemes')
    indices = rig.indices()
    (out / 'mesh/indices.u32').write_bytes(struct.pack(f'<{len(indices)}I', *indices))
    evaluated = {}

    def positions(weights: dict[int, dict[int, float]]):
        full = vectors(rig.snapshot, weights) if vrm else {rig.node: [weights.get(rig.node, {}).get(i, 0.0)
                                                                       for i in range(len(rig.targets))]}
        key = json.dumps(full, sort_keys=True)
        if key not in evaluated:
            geometry = rigs.require(msf.evaluate_geometry(rig.snapshot, morph_weights=full))
            evaluated[key] = [p for instance in geometry.instances for primitive in instance['primitives']
                              for p in primitive['positions']]
        return evaluated[key]

    neutral = positions({})
    low = [min(p[k] for p in neutral) for k in range(3)]
    high = [max(p[k] for p in neutral) for k in range(3)]
    if vrm:
        reference = vrm_presets.morph_weights(expressions, {'aa': 1.0})[0]
    else:
        reference = {rig.node: {rig.visemes['AA']: 1.0}}
    heat_scale = 0.1 * max(math.dist(p, q) for p, q in zip(positions(reference), neutral))
    manifest = []
    for number, (translator, pairs, frame, result) in enumerate(jobs):
        values = {translator.short(sid): v for sid, v in frame['values'].items()}
        stem = f'{number:04d}.f32'
        labels, ok = [], True
        if vrm:
            valid = all(translator.valid(sid, frame['flags']) for sid in frame['values'])
            direct_w, _ = vrm_presets.morph_weights(
                expressions, {pairs[v]: w for v, w in values.items() if v in pairs and valid})
            translated_w, labels = vrm_presets.morph_weights(
                expressions, {translator.short(sid): w for sid, w in result['values'].items()})
            difference = max_difference(direct_w, translated_w)
            ok = difference <= TOLERANCE
            labels = [f'refused by {r}' for r in result['refused']] + labels
            labels += [f'{d}: no VRM preset; not shown' for d in result['dropped']]
            direct_p, translated_p = positions(direct_w), positions(translated_w)
            write_f32 = face_pipeline.write_f32
            write_f32(out / 'mesh/direct' / stem, direct_p)
            write_f32(out / 'mesh/translated' / stem, translated_p)
            write_f32(out / 'mesh/difference' / stem,
                      (face_pipeline.heat(math.dist(p, q), heat_scale) for p, q in zip(direct_p, translated_p)))
            entry = {'direct': f'mesh/direct/{stem}', 'translated': f'mesh/translated/{stem}',
                     'difference_colors': f'mesh/difference/{stem}', 'max_morph_weight_difference': difference}
        else:
            weights = {rig.node: {rig.visemes[v]: w for v, w in values.items() if w}}
            face_pipeline.write_f32(out / 'mesh/direct' / stem, positions(weights))
            entry = {'direct': f'mesh/direct/{stem}'}
        manifest.append({'frame': number, 'time': frame['time'], 'segment': frame['segment'],
                         'phase': frame['labels'].get('phase', ''), 'viseme': frame['labels'].get('viseme', ''),
                         **entry, 'labels': labels, 'oracles_pass': ok})

    (out / 'frames.json').write_text(json.dumps({
        'rig': rig.name, 'credit': rig.credit, 'caption': CAPTION if vrm else
        'META visemes on the rig\'s own viseme shapes, by name; no translation.',
        'panels': panels, 'indices': 'mesh/indices.u32', 'vertex_count': len(neutral),
        'positions_format': 'little-endian float32 xyz per vertex, every mesh of the rig in node order, rig units',
        'difference_colors_format': 'little-endian float32 RGB per vertex; blue = 0, red >= heat_scale',
        'heat_scale': heat_scale, 'bounds': {'min': low, 'max': high}, 'frames': manifest}, indent=1),
        encoding='utf-8')
    failed = [m['frame'] for m in manifest if not m['oracles_pass']]
    print(f'{rig.name}: {len(jobs)} frames, {len(evaluated)} geometry evaluations -> {out}')
    print('all oracles pass' if not failed else f'oracles FAIL on frames {failed}')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
