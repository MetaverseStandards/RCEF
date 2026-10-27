#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write the synthetic demo input frames in examples/data/.

The frames are original synthetic data (no device capture). Each segment
tests one behaviour of the translation:

- neutral: everything at rest;
- jaw sweep: one channel 0 -> 1 -> 0 through a one-to-one mapping;
- gaze: both eyes look left, then right, one direction at a time; then each
  eye alone in each direction, so a rule reading the wrong eye shows up;
- asymmetric brows and cheeks: left and right differ, through the averaged mappings
  (the cheeks both ways round, so each side drives its own half);
- lips closed, jaw closed: LIPS_TOWARD with the jaw explicitly at rest;
- smile, chin raiser and blink: each channel alone (left and right separately),
  so every mapping is the only thing moving in some frame;
- eye following lost: the face stays valid while the gaze weights are invalid
  (FB2 then reports them as zero), during a blink;
- face lost: the whole frame is invalid;
- every other channel an RCEF FB2 mapping reads, alone and briefly;
- tongue: a channel with no RCEF mapping (TONGUE_TIP_ALVEOLAR), with the jaw half open.

All values are multiples of 1/16, so sums and halves are exact in binary.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).resolve().parent / 'data'
FPS = 15
FB2_PREFIX, FB2_SUFFIX = 'openxr.fb2.XR_FACE_EXPRESSION2_', '_FB'
VIS_PREFIX, VIS_SUFFIX = 'openxr.visemes.XR_FACE_TRACKING_VISEME_', '_META'


def names(profile, prefix, suffix):
    pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
    signals = {s['id']: s for s in pack['signals']}
    members = next(p['signal_ids'] for p in pack['profiles'] if p['id'] == profile)
    # Count sentinels are inventory records, not weights a runtime reports.
    return [sid[len(prefix):-len(suffix)] for sid in members if signals[sid]['disposition'] != 'excluded']


def rule_inputs():
    """The FB2 channels RCEF's FB2 -> ARKit mappings read, in profile order."""
    pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
    read = {i for m in pack['mappings'] if m['id'] in ('fb2.to_arkit', 'fb2_gaze.to_arkit')
            for r in m['rules'] for i in r['inputs']}
    order = next(p['signal_ids'] for p in pack['profiles'] if p['id'] == 'openxr.fb2')
    return [sid[len(FB2_PREFIX):-len(FB2_SUFFIX)] for sid in order if sid in read]


def ramp(steps):
    """0 -> 1 -> 0 in steps of 1/16, `steps` frames up and the same down."""
    up = [round(16 * i / steps) / 16 for i in range(steps + 1)]
    return up + up[-2::-1]


def fb2_frames():
    segments = [('neutral', [{}] * 4, True, True)]
    segments.append(('jaw sweep', [{'JAW_DROP': v} for v in ramp(8)], True, True))
    segments.append(('gaze left', [{'EYES_LOOK_LEFT_L': v, 'EYES_LOOK_LEFT_R': v} for v in ramp(6)], True, True))
    segments.append(('gaze right', [{'EYES_LOOK_RIGHT_L': v, 'EYES_LOOK_RIGHT_R': v} for v in ramp(6)], True, True))
    for eye, side in (('left', 'L'), ('right', 'R')):
        for direction in ('left', 'right'):
            segments.append((f'{eye} eye looks {direction}',
                             [{f'EYES_LOOK_{direction.upper()}_{side}': v} for v in ramp(4)], True, True))
    segments.append(('asymmetric brows', [{'INNER_BROW_RAISER_L': v, 'INNER_BROW_RAISER_R': 0.25} for v in ramp(6)], True, True))
    segments.append(('asymmetric cheeks', [{'CHEEK_PUFF_L': v, 'CHEEK_PUFF_R': 0.0} for v in ramp(6)], True, True))
    segments.append(('asymmetric cheeks, mirrored', [{'CHEEK_PUFF_L': 0.0, 'CHEEK_PUFF_R': v} for v in ramp(6)], True, True))
    segments.append(('lips closed, jaw closed', [{'LIPS_TOWARD': v, 'JAW_DROP': 0.0} for v in ramp(4)], True, True))
    for label, channel in (('smile left', 'LIP_CORNER_PULLER_L'), ('smile right', 'LIP_CORNER_PULLER_R'),
                           ('chin raiser top', 'CHIN_RAISER_T'), ('chin raiser bottom', 'CHIN_RAISER_B'),
                           ('blink left', 'EYES_CLOSED_L'), ('blink right', 'EYES_CLOSED_R')):
        segments.append((label, [{channel: v} for v in ramp(4)], True, True))
    # Every other channel an RCEF FB2 mapping reads, alone, so each mapping is the only one moving somewhere.
    alone = {[k for k, v in f.items() if v][0] for _, frames, *_ in segments for f in frames
             if len([v for v in f.values() if v]) == 1}
    for channel in rule_inputs():
        if channel not in alone:
            segments.append((f'{channel} alone', [{channel: v} for v in ramp(2)], True, True))
    segments.append(('eye following lost', [{'EYES_CLOSED_L': v, 'EYES_CLOSED_R': v} for v in ramp(5)], True, False))
    segments.append(('face lost', [{'JAW_DROP': 0.5}] * 5, False, False))
    segments.append(('tongue', [{'JAW_DROP': 0.5, 'TONGUE_TIP_ALVEOLAR': v} for v in ramp(5)], True, True))
    segments.append(('neutral', [{}] * 4, True, True))
    return segments


def viseme_frames():
    def vowel(name, share):
        # A valid META frame sums to 1; the rest of the mass sits on silence.
        return {name: share, 'SIL': 1.0 - share} if share < 1 else {name: 1.0}
    segments = [('silence', [{'SIL': 1.0}] * 3, True)]
    for name in ('AA', 'E', 'IH', 'OH', 'OU'):
        segments.append((f'vowel {name}', [vowel(name, v) for v in ramp(4)], True))
    segments.append(('consonant PP', [{'PP': 0.75, 'AA': 0.25}] * 3, True))
    segments.append(('invalid', [{}] * 3, False))
    segments.append(('silence', [{'SIL': 1.0}] * 3, True))
    return segments


def write(path, channels, flags, segments):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['time', 'segment', *channels, *flags])
        frame = 0
        for segment in segments:
            label, values, *valid = segment
            for value in values:
                writer.writerow([f'{frame / FPS:.6f}', label, *(f'{value.get(c, 0.0):g}' for c in channels),
                                 *(int(v) for v in valid)])
                frame += 1
    return frame


def main() -> int:
    DATA.mkdir(exist_ok=True)
    count = write(DATA / 'fb2_demo_frames.csv', names('openxr.fb2', FB2_PREFIX, FB2_SUFFIX),
                  ['isValid', 'isEyeFollowingBlendshapesValid'], fb2_frames())
    print(f'examples/data/fb2_demo_frames.csv: {count} frames')
    count = write(DATA / 'viseme_demo_frames.csv', names('openxr.visemes', VIS_PREFIX, VIS_SUFFIX),
                  ['isValid'], viseme_frames())
    print(f'examples/data/viseme_demo_frames.csv: {count} frames')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
