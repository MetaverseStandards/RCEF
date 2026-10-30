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
- every other channel that the FB2 -> ARKit maps read (RULE_INPUTS), alone and
  briefly;
- tongue: a channel with no RCEF mapping (TONGUE_TIP_ALVEOLAR), with the jaw half open.

All values are multiples of 1/16, so sums and halves are exact in binary.
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent / 'data'
FPS = 15
# The channel lists are fixed, so the frames do not change when the pack does. They are the FB2 and META channels
# that the pack of data 0.3.0 listed (count sentinels left out: they are inventory records, not weights), and the
# FB2 channels that its FB2 -> ARKit maps read, in the order of the FB2 profile.
FB2_CHANNELS = (
    'BROW_LOWERER_L', 'BROW_LOWERER_R', 'CHEEK_PUFF_L', 'CHEEK_PUFF_R', 'CHEEK_RAISER_L', 'CHEEK_RAISER_R',
    'CHEEK_SUCK_L', 'CHEEK_SUCK_R', 'CHIN_RAISER_B', 'CHIN_RAISER_T', 'DIMPLER_L', 'DIMPLER_R', 'EYES_CLOSED_L',
    'EYES_CLOSED_R', 'EYES_LOOK_DOWN_L', 'EYES_LOOK_DOWN_R', 'EYES_LOOK_LEFT_L', 'EYES_LOOK_LEFT_R',
    'EYES_LOOK_RIGHT_L', 'EYES_LOOK_RIGHT_R', 'EYES_LOOK_UP_L', 'EYES_LOOK_UP_R', 'INNER_BROW_RAISER_L',
    'INNER_BROW_RAISER_R', 'JAW_DROP', 'JAW_SIDEWAYS_LEFT', 'JAW_SIDEWAYS_RIGHT', 'JAW_THRUST', 'LID_TIGHTENER_L',
    'LID_TIGHTENER_R', 'LIP_CORNER_DEPRESSOR_L', 'LIP_CORNER_DEPRESSOR_R', 'LIP_CORNER_PULLER_L',
    'LIP_CORNER_PULLER_R', 'LIP_FUNNELER_LB', 'LIP_FUNNELER_LT', 'LIP_FUNNELER_RB', 'LIP_FUNNELER_RT',
    'LIP_PRESSOR_L', 'LIP_PRESSOR_R', 'LIP_PUCKER_L', 'LIP_PUCKER_R', 'LIP_STRETCHER_L', 'LIP_STRETCHER_R',
    'LIP_SUCK_LB', 'LIP_SUCK_LT', 'LIP_SUCK_RB', 'LIP_SUCK_RT', 'LIP_TIGHTENER_L', 'LIP_TIGHTENER_R', 'LIPS_TOWARD',
    'LOWER_LIP_DEPRESSOR_L', 'LOWER_LIP_DEPRESSOR_R', 'MOUTH_LEFT', 'MOUTH_RIGHT', 'NOSE_WRINKLER_L',
    'NOSE_WRINKLER_R', 'OUTER_BROW_RAISER_L', 'OUTER_BROW_RAISER_R', 'UPPER_LID_RAISER_L', 'UPPER_LID_RAISER_R',
    'UPPER_LIP_RAISER_L', 'UPPER_LIP_RAISER_R', 'TONGUE_TIP_INTERDENTAL', 'TONGUE_TIP_ALVEOLAR',
    'TONGUE_FRONT_DORSAL_PALATE', 'TONGUE_MID_DORSAL_PALATE', 'TONGUE_BACK_DORSAL_VELAR', 'TONGUE_OUT',
    'TONGUE_RETREAT')
VISEME_CHANNELS = ('SIL', 'PP', 'FF', 'TH', 'DD', 'KK', 'CH', 'SS', 'NN', 'RR', 'AA', 'E', 'IH', 'OH', 'OU')
NOT_READ = {'CHEEK_SUCK_L', 'CHEEK_SUCK_R', 'LIP_TIGHTENER_L', 'LIP_TIGHTENER_R', 'TONGUE_TIP_INTERDENTAL',
            'TONGUE_TIP_ALVEOLAR', 'TONGUE_FRONT_DORSAL_PALATE', 'TONGUE_MID_DORSAL_PALATE',
            'TONGUE_BACK_DORSAL_VELAR', 'TONGUE_RETREAT'}
RULE_INPUTS = tuple(c for c in FB2_CHANNELS if c not in NOT_READ)


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
    for channel in RULE_INPUTS:
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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=DATA, help='output directory (default: examples/data)')
    out = parser.parse_args(argv).out
    out.mkdir(exist_ok=True)
    count = write(out / 'fb2_demo_frames.csv', FB2_CHANNELS, ['isValid', 'isEyeFollowingBlendshapesValid'], fb2_frames())
    print(f'{out / "fb2_demo_frames.csv"}: {count} frames')
    count = write(out / 'viseme_demo_frames.csv', VISEME_CHANNELS, ['isValid'], viseme_frames())
    print(f'{out / "viseme_demo_frames.csv"}: {count} frames')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
