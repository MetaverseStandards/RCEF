#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Drive ARKit faces with META viseme frames through RCEF's viseme pose bridge, and compare with a Rocketbox rig.

Usage: python examples/viseme_bridge.py [--frames CSV] [--rig RIG] [--rig-cache DIR] [--ict-cache DIR] [--out DIR]

The frames default to "bed car toe book" (examples/data/viseme_talk_frames.csv). Route carries them from META
visemes through the canonical viseme set, the pose bridge and the canonical expression set to ARKit weights
(bridge_arkit.csv). The ARKit weights then pose two faces that have ARKit shapes:

- a Rocketbox rig (default rocketbox-female-09, Female_Adult_09, one of the 4 rigs that the bridge's calibration
  record held out; the others are rocketbox-female-15, rocketbox-male-08 and rocketbox-male-15). Its own META
  viseme shapes, driven by the same frames by name, are the comparison ("direct"). Per frame, the error is
  |bridged - direct| / |direct| over every vertex except the tongue (the vertices its tongueOut moves), as in the calibration record, and the
  RMS vertex distance in millimetres over the vertices that either face moves.
- ICT-FaceKit, which has no viseme shapes, from its OBJ files (all 53 expression shapes; the cache of
  tools/calibration/k4_mediapipe.py). Its ARKit weights are in Rocketbox units, so the geometry is only indicative
  (record rig-gains.ict-rocketbox-female).

It also prints one line per META viseme at weight 1: on the Rocketbox rig the error ratio and the RMS distance
between the bridged and the direct face; on ICT the RMS distance between the bridged face and its neutral face, the
signed lip opening on the mid line, and how differently the two sides move (the largest difference between a Left
and a Right ARKit weight, and the RMS difference between each vertex's motion and the mirrored motion of its mirror
vertex).

Positions go to OUT/mesh/RIG/PANEL/NNNN.f32 (little-endian float32 xyz), with OUT/frames.json, so the frames can be
rendered later. Rig files go to ~/.cache/rcef-face-rigs and ~/.cache/rcef-ict-full, outputs to
~/.cache/rcef-examples/viseme-bridge ($XDG_CACHE_HOME instead of ~/.cache when it is set).
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import struct

import msf_character_tools as msf

import face_pipeline
import ict_facekit
import rcef_route
import rcef_translate
import rigs

HERE = Path(__file__).resolve().parent
ARKIT = 'arkit.coefficient.'
CAPTION = ("ARKit weights from META visemes through RCEF's viseme pose bridge: poses fitted to 18 Rocketbox rigs, held "
           'out on 4 others by their shape or their visible mouth features; classes that failed both are not read.')
HELD_OUT = ['rocketbox-female-09', 'rocketbox-female-15', 'rocketbox-male-08', 'rocketbox-male-15']


def arguments(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--frames', type=Path, default=HERE / 'data/viseme_talk_frames.csv')
    names = sorted(rigs.rocketbox_name(*avatar.split('_Adult_')) for avatar in rigs.ROCKETBOX_SHA256)
    parser.add_argument('--rig', choices=names, default=HELD_OUT[0],
                        help=f'the Rocketbox rig to compare with (default {HELD_OUT[0]}; held out: '
                             f'{", ".join(HELD_OUT)})')
    parser.add_argument('--rig-cache', type=Path, help='Rocketbox files (default: ~/.cache/rcef-face-rigs)')
    parser.add_argument('--ict-cache', type=Path, help='ICT-FaceKit OBJ files (default: ~/.cache/rcef-ict-full)')
    parser.add_argument('--out', type=Path, help='output directory (default: ~/.cache/rcef-examples/viseme-bridge)')
    args = parser.parse_args(argv)
    home = rcef_translate.cache_home()
    args.rig_cache = args.rig_cache or home / 'rcef-face-rigs'
    args.ict_cache = args.ict_cache or home / 'rcef-ict-full'
    args.out = args.out or home / 'rcef-examples/viseme-bridge'
    return args


class Rocketbox:
    def __init__(self, cache: Path, name: str):
        self.rig = rigs.load(name, cache)
        self.arkit = {a: i for i, a, _ in self.rig.shapes}
        self.rest = self.positions({})
        moved = [math.dist(p, q) for p, q in zip(self.positions({self.arkit['tongueOut']: 1.0}), self.rest)]
        self.keep = [v for v, m in enumerate(moved) if m <= 0.01 * max(moved)]

    def positions(self, weights: dict[int, float]) -> list[tuple[float, float, float]]:
        vector = [weights.get(i, 0.0) for i in range(len(self.rig.targets))]
        geometry = rigs.require(msf.evaluate_geometry(self.rig.snapshot, morph_weights={self.rig.node: vector}))
        return [tuple(p) for instance in geometry.instances for primitive in instance['primitives']
                for p in primitive['positions']]


class ICT:
    """ICT-FaceKit from its OBJ files: neutral plus each ARKit-named shape's offsets, loaded when first used."""

    def __init__(self, cache: Path):
        ict_facekit.fetch(cache, ict_facekit.CALIBRATION_FILES)
        self.cache = cache
        self.rest, faces = ict_facekit.read_obj(cache / f'{ict_facekit.NEUTRAL}.obj')
        self.indices = ict_facekit.triangles(faces)
        names = list(ict_facekit.EXPRESSIONS)
        self.parts = {}  # ARKit name -> ICT shapes; ICT splits browInnerUp and cheekPuff into halves
        for (_, arkit, _), name in zip(rigs.ict_shapes(names), names):
            self.parts.setdefault(arkit, []).append(name)
        self.offsets = {}

    def offset(self, name: str) -> list[tuple[float, float, float]]:
        if name not in self.offsets:
            shape, _ = ict_facekit.read_obj(self.cache / f'{name}.obj')
            self.offsets[name] = [(s[0] - r[0], s[1] - r[1], s[2] - r[2]) for s, r in zip(shape, self.rest)]
        return self.offsets[name]

    def mouth(self) -> None:
        """Mid-line lip landmarks (ICT: x across, y up, z forward, centimetres), close to the rule of the calibration
        tool's Mouth: lips are what mouthFunnel moves by more than 0.2 of its largest move, within 1 cm of the height
        of the vertex mouthFunnel moves most (on ICT jawOpen moves the chin most, not the lips); upper lip under 0.3
        of jawOpen's largest move, lower lip over 0.6; mid line |x| <= 0.3 cm. Also each vertex's mirror vertex (x
        negated), where one exists."""
        def moved(name):
            values = [math.hypot(*d) for d in self.offset(self.parts[name][0])]
            top = max(values)
            return [x / top for x in values]
        jaw, funnel = moved('jawOpen'), moved('mouthFunnel')
        centre = self.rest[max(range(len(funnel)), key=funnel.__getitem__)]
        mid = [v for v, f in enumerate(funnel) if f > 0.2 and abs(self.rest[v][1] - centre[1]) <= 1.0
               and abs(self.rest[v][0]) <= 0.3]
        self.upper, self.lower = [v for v in mid if jaw[v] < 0.3], [v for v in mid if jaw[v] > 0.6]
        index = {tuple(round(c, 2) for c in p): v for v, p in enumerate(self.rest)}
        self.mirror = {v: index.get((round(-p[0], 2), round(p[1], 2), round(p[2], 2))) for v, p in enumerate(self.rest)}

    def lip_opening_mm(self, positions) -> float:
        return 10 * (min(positions[v][1] for v in self.upper) - max(positions[v][1] for v in self.lower))

    def asymmetry_mm(self, positions) -> float:
        """RMS of |d(v) - mirrored d(mirror(v))| over the vertices that move, in mm."""
        d = [tuple(a - b for a, b in zip(p, r)) for p, r in zip(positions, self.rest)]
        diffs = [math.dist(d[v], (-d[m][0], d[m][1], d[m][2])) for v, m in self.mirror.items()
                 if m is not None and math.hypot(*d[v]) > 1e-2]
        return 10 * math.sqrt(math.fsum(x * x for x in diffs) / len(diffs)) if diffs else 0.0

    def positions(self, arkit: dict[str, float]) -> list[tuple[float, float, float]]:
        out = [list(p) for p in self.rest]
        for name, w in arkit.items():
            for part in self.parts.get(name, []) if w else []:
                for p, d in zip(out, self.offset(part)):
                    p[0] += w * d[0]
                    p[1] += w * d[1]
                    p[2] += w * d[2]
        return [tuple(p) for p in out]


def compare(rb: Rocketbox, bridged, direct) -> dict:
    """|bridged - direct| / |direct - rest| over the non-tongue vertices; RMS distance in mm where either moves."""
    error = math.fsum(math.dist(bridged[v], direct[v]) ** 2 for v in rb.keep)
    motion = math.fsum(math.dist(direct[v], rb.rest[v]) ** 2 for v in rb.keep)
    moved = [v for v in rb.keep if math.dist(direct[v], rb.rest[v]) > 1e-4 or math.dist(bridged[v], rb.rest[v]) > 1e-4]
    rms = math.sqrt(math.fsum(math.dist(bridged[v], direct[v]) ** 2 for v in moved) / len(moved)) if moved else 0.0
    return {'ratio': math.sqrt(error / motion) if motion else (0.0 if error == 0 else None), 'rms_mm': 1000 * rms}


def main(argv=None) -> int:
    args = arguments(argv)
    reader = rcef_translate.visemes_to_vrm()
    frames = reader.read(args.frames)
    route = rcef_route.Route('openxr.visemes', 'arkit.coefficient')
    results = route.translate(frames)
    columns = [o[len(ARKIT):] for o in route.outputs]
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / 'bridge_arkit.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['time', 'segment', *columns, 'labels', 'dropped'])
        for r in results:
            labels = sorted(set(r['labels'].values()) | {f'refused at {m}' for m in r['refused']})
            writer.writerow([f'{r["time"]:.6f}', r['segment'],
                             *(repr(r['values'][ARKIT + c]) if ARKIT + c in r['values'] else '' for c in columns),
                             '; '.join(labels), ' '.join(reader.short(s) for s in r['dropped'])])
    rb, ict = Rocketbox(args.rig_cache, args.rig), ICT(args.ict_cache)
    name = args.rig
    panels = {f'{name}/bridged', f'{name}/direct', f'{name}/difference', 'ict/bridged'}
    for panel in panels:
        (args.out / 'mesh' / panel).mkdir(parents=True, exist_ok=True)
    for panel, indices in ((name, rb.rig.indices()), ('ict', ict.indices)):
        (args.out / 'mesh' / panel / 'indices.u32').write_bytes(struct.pack(f'<{len(indices)}I', *indices))
    manifest = []
    for number, (frame, result) in enumerate(zip(frames, results)):
        stem = f'{number:04d}.f32'
        arkit = {o[len(ARKIT):]: v for o, v in result['values'].items()}
        bridged = rb.positions({rb.arkit[a]: w for a, w in arkit.items() if a in rb.arkit})
        direct = rb.positions({rb.rig.visemes[reader.short(s)]: w for s, w in frame['values'].items()}
                              if all(frame['flags'].values()) else {})
        entry = {'frame': number, 'time': frame['time'], 'segment': frame['segment'],
                 'viseme': frame['labels'].get('viseme', ''), 'refused': sorted(result['refused']),
                 'dropped': [reader.short(s) for s in result['dropped']], **compare(rb, bridged, direct)}
        face_pipeline.write_f32(args.out / 'mesh' / name / 'bridged' / stem, bridged)
        face_pipeline.write_f32(args.out / 'mesh' / name / 'direct' / stem, direct)
        face_pipeline.write_f32(args.out / 'mesh' / name / 'difference' / stem,
                                (face_pipeline.heat(math.dist(p, q), 0.004) for p, q in zip(bridged, direct)))
        face_pipeline.write_f32(args.out / 'mesh/ict/bridged' / stem, ict.positions(arkit))
        manifest.append(entry)
    (args.out / 'frames.json').write_text(json.dumps({
        'caption': CAPTION, 'frames_csv': str(args.frames.name), 'panels': sorted(panels),
        'credits': [rb.rig.credit, 'ICT-FaceKit (c) 2020 USC Institute for Creative Technologies, MIT license'],
        'positions_format': 'little-endian float32 xyz per vertex, rig units (Rocketbox metres, ICT centimetres)',
        'difference_colors_format': 'little-endian float32 RGB per vertex; blue = 0, red >= 4 mm',
        'error': f'|bridged - direct| / |direct - rest| over {name} vertices except the tongue; rms_mm over the '
                 'vertices either face moves', 'frames': manifest}, indent=1), encoding='utf-8')
    ratios = [m['ratio'] for m in manifest if m['ratio'] is not None]
    print(f'{len(frames)} frames -> {args.out}')
    median = sorted(ratios)[len(ratios) // 2]
    print(f'{name}, bridged against its own visemes: error ratio median {median:.3f}, max {max(ratios):.3f}; '
          f'RMS distance max {max(m["rms_mm"] for m in manifest):.2f} mm')
    ict.mouth()
    neutral = ict.lip_opening_mm(ict.rest)
    print(f'Each META viseme at weight 1 ({name}: error ratio and RMS mm against its own viseme; ICT: RMS mm from '
          f'neutral over the vertices that move, lip opening mm on the mid line (neutral {neutral:.2f}), largest '
          'Left - Right ARKit weight difference, mirror RMS mm):')
    for meta in rigs.META_VISEME_ORDER:
        values = {f'{reader.prefix}{n}{reader.suffix}': float(n == meta) for n in rigs.META_VISEME_ORDER}
        result, = route.translate([{'time': 0.0, 'values': values, 'flags': {'isValid': True}}])
        arkit = {o[len(ARKIT):]: v for o, v in result['values'].items()}
        found = compare(rb, rb.positions({rb.arkit[a]: w for a, w in arkit.items() if a in rb.arkit}),
                        rb.positions({rb.rig.visemes[meta]: 1.0}))
        posed = ict.positions(arkit)
        moved = [math.dist(p, q) for p, q in zip(posed, ict.rest) if math.dist(p, q) > 1e-2]
        ict_mm = 10 * math.sqrt(math.fsum(d * d for d in moved) / len(moved)) if moved else 0.0
        ratio = 'n/a' if found['ratio'] is None else f'{found["ratio"]:.3f}'
        sides = max((abs(w - arkit.get(a.removesuffix('Left') + 'Right', 0.0)) for a, w in arkit.items()
                     if a.endswith('Left')), default=0.0)
        print(f'  {meta:4} {"read" if not result["dropped"] else "dropped":7} ratio {ratio:6} '
              f'RMS {found["rms_mm"]:5.2f} mm   ICT RMS {ict_mm:5.2f} mm, lip opening '
              f'{ict.lip_opening_mm(posed):6.2f} mm, Left - Right {sides:.3f}, '
              f'mirror RMS {ict.asymmetry_mm(posed):.2f} mm')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
