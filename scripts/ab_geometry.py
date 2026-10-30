#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Metric M6 of the A/B comparison (report only): B and the arm it is compared with, posed on face rigs.

For the pairs with an ARKit target (FB2 -> ARKit against A1, and FACS -> ARKit
against A3 then A1), the ARKit outputs of each frame pose a rig with
msf_character_tools.evaluate_geometry, once with each arm's values, and the
vertex positions are compared bit for bit. Only the outputs that both arms
write pose the rig; every other shape stays at rest. So M6 should be 0
wherever M1 (or M10b) passes, and a non-zero M6 there is a harness problem.

The rigs come from examples/rigs.py: fetched into caches outside the
repository and checked against their pinned SHA-256. Before any comparison
the harness checks itself on each rig (its oracles):

- rest: all-zero weights give the positions of the rig with no weights;
- bindings: each bound ARKit shape at weight 1 moves at least one vertex;
- repeatable: the same weights give the same positions twice.
"""
from __future__ import annotations
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'examples')]
import ict_facekit  # noqa: E402
import msf_character_tools as msf  # noqa: E402
import rigs  # noqa: E402

RIGS = ('rocketbox-female', 'ict')
ARKIT = 'arkit.coefficient.'


def rig_pins() -> dict:
    """The SHA-256 of every file each rig is built from, as examples/rigs.py and ict_facekit.py pin them."""
    return {'rocketbox-female': {'Female_Adult_01_facial.fbx': rigs.ROCKETBOX_SHA256['Female_Adult_01']},
            'ict': dict(sorted(ict_facekit.FILES.items()))}


def positions(rig, weights: dict[str, float]) -> bytes:
    """Vertex positions (binary64, packed) of a rig posed with ARKit weights by signal ID; a split ICT shape takes
    its coefficient on both halves."""
    vector = [0.0] * len(rig.targets)
    for index, name, _ in rig.shapes:
        vector[index] = weights.get(ARKIT + name, 0.0)
    geometry = rigs.require(msf.evaluate_geometry(rig.snapshot, morph_weights={rig.node: vector}))
    values = [c for instance in geometry.instances for primitive in instance['primitives']
              for p in primitive['positions'] for c in p]
    return struct.pack(f'>{len(values)}d', *values)


def oracle_problems(rig) -> list[str]:
    """The harness oracles on one rig: rest, live bindings and repeatability."""
    problems = []
    plain = rigs.require(msf.evaluate_geometry(rig.snapshot))
    rest = [c for instance in plain.instances for primitive in instance['primitives']
            for p in primitive['positions'] for c in p]
    zero = positions(rig, {})
    if zero != struct.pack(f'>{len(rest)}d', *rest):
        problems.append(f'{rig.name}: all-zero weights do not give the rest positions')
    for name in sorted({shape for _, shape, _ in rig.shapes}):
        if positions(rig, {ARKIT + name: 1.0}) == zero:
            problems.append(f'{rig.name}: {name} at 1 moves no vertex')
    probe = {ARKIT + name: 0.5 for _, name, _ in rig.shapes}
    if positions(rig, probe) != positions(rig, probe):
        problems.append(f'{rig.name}: the same weights gave different positions')
    return problems


def load(caches: dict[str, Path]) -> dict:
    return {name: rigs.load(name, caches[name]) for name in RIGS if name in caches}


def vertex_difference(rig, a: list[dict], b: list[dict]) -> dict:
    """Pose the rig with each arm's values on the outputs both write; the largest coordinate difference."""
    counts = {'frames': len(a), 'posed': 0, 'frames_with_difference': 0, 'max_vertex_difference': 0.0}
    for x, y in zip(a, b, strict=True):
        common = x['values'].keys() & y['values'].keys()
        if not any(o.startswith(ARKIT) for o in common):
            continue
        counts['posed'] += 1
        p, q = (positions(rig, {o: r['values'][o] for o in common}) for r in (x, y))
        if p != q:
            counts['frames_with_difference'] += 1
            n = len(p) // 8
            difference = max(abs(u - v) for u, v in zip(struct.unpack(f'>{n}d', p), struct.unpack(f'>{n}d', q)))
            counts['max_vertex_difference'] = max(counts['max_vertex_difference'], difference)
    return counts
