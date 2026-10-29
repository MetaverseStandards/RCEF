#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Drive ARKit faces with META viseme frames through RCEF's viseme pose bridge, and compare with Rocketbox Male.

Usage: python examples/viseme_bridge.py [--frames CSV] [--rig-cache DIR] [--ict-cache DIR] [--out DIR]

The frames default to "bed car toe book" (examples/data/viseme_talk_frames.csv). Route carries them from META
visemes through the canonical viseme set, the pose bridge and the canonical expression set to ARKit weights
(bridge_arkit.csv). The ARKit weights then pose two faces that have ARKit shapes:

- Rocketbox Male_Adult_01, the rig the bridge's calibration record held out. Its own META viseme shapes, driven by
  the same frames by name, are the comparison ("direct"). Per frame, the error is |bridged - direct| / |direct|
  over every vertex except the tongue (the vertices its tongueOut moves), as in the calibration record, and the
  RMS vertex distance in millimetres over the vertices that either face moves.
- ICT-FaceKit, which has no viseme shapes, from its OBJ files (all 53 expression shapes; the cache of
  tools/calibration/k4_mediapipe.py). Its ARKit weights are Rocketbox Female's units, so the geometry is only
  indicative (record rig-gains.ict-rocketbox-female).

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
CAPTION = ("ARKit weights from META visemes through RCEF's viseme pose bridge: poses of Rocketbox Female, held out on "
           'Rocketbox Male; classes that failed their bounds are not read.')


def arguments(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--frames', type=Path, default=HERE / 'data/viseme_talk_frames.csv')
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
    def __init__(self, cache: Path):
        self.rig = rigs.load('rocketbox-male', cache)
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
    rb, ict = Rocketbox(args.rig_cache), ICT(args.ict_cache)
    panels = {'rocketbox-male/bridged', 'rocketbox-male/direct', 'rocketbox-male/difference', 'ict/bridged'}
    for panel in panels:
        (args.out / 'mesh' / panel).mkdir(parents=True, exist_ok=True)
    for name, indices in (('rocketbox-male', rb.rig.indices()), ('ict', ict.indices)):
        (args.out / 'mesh' / name / 'indices.u32').write_bytes(struct.pack(f'<{len(indices)}I', *indices))
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
        face_pipeline.write_f32(args.out / 'mesh/rocketbox-male/bridged' / stem, bridged)
        face_pipeline.write_f32(args.out / 'mesh/rocketbox-male/direct' / stem, direct)
        face_pipeline.write_f32(args.out / 'mesh/rocketbox-male/difference' / stem,
                                (face_pipeline.heat(math.dist(p, q), 0.004) for p, q in zip(bridged, direct)))
        face_pipeline.write_f32(args.out / 'mesh/ict/bridged' / stem, ict.positions(arkit))
        manifest.append(entry)
    (args.out / 'frames.json').write_text(json.dumps({
        'caption': CAPTION, 'frames_csv': str(args.frames.name), 'panels': sorted(panels),
        'credits': [rb.rig.credit, 'ICT-FaceKit (c) 2020 USC Institute for Creative Technologies, MIT license'],
        'positions_format': 'little-endian float32 xyz per vertex, rig units (Rocketbox metres, ICT centimetres)',
        'difference_colors_format': 'little-endian float32 RGB per vertex; blue = 0, red >= 4 mm',
        'error': '|bridged - direct| / |direct - rest| over Rocketbox Male vertices except the tongue; rms_mm over '
                 'the vertices either face moves', 'frames': manifest}, indent=1), encoding='utf-8')
    ratios = [m['ratio'] for m in manifest if m['ratio'] is not None]
    print(f'{len(frames)} frames -> {args.out}')
    median = sorted(ratios)[len(ratios) // 2]
    print(f'Rocketbox Male, bridged against its own visemes: error ratio median {median:.3f}, max {max(ratios):.3f}; '
          f'RMS distance max {max(m["rms_mm"] for m in manifest):.2f} mm')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
