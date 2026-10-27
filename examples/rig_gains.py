# SPDX-License-Identifier: MIT
"""Rig intensity normalisation, ICT-FaceKit -> Rocketbox Female: one monotone curve per ARKit shape.

The same ARKit name moves two independently authored rigs by different amounts. For each shape both rigs have,
this fits a curve from an ICT-FaceKit weight to the Rocketbox Female weight whose motion matches best, measured
on rendered stimuli, and evaluates it on a held-out ICT identity. It calibrates how two example rigs render
ARKit names; it says nothing about any tracker, and the result is a rendering correction for RCEF's face
examples, not a provider claim and not pack data. Rocketbox Male is reserved for a later method and is never
loaded here.

Measurement, per condition (a rig pose seen by one jittered camera):
- Every landmark of the shape's region (examples/data/rig_landmarks.json) is painted as a small marker: vertex
  colour falling linearly from 1 at the landmark to 0 at MARKER_RADIUS (IOD units), in one of three colour
  channels, on an otherwise black mesh, rendered unlit on black with tools/render/meshrender. Markers that share
  a channel are at least SEPARATION apart; regions that need more markers than fit use several renders (passes).
- A marker's position is the centroid of its channel's pixel values in a window around its projected landmark;
  its weight is their sum. A marker is visible if its weight is at least MIN_WEIGHT at rest and at least
  VISIBLE_FRACTION of that when posed. Occluded markers (lips rolled in, a lid over the iris) drop out.
- Both rigs are framed by their own IOD, so marker displacements (pixels / image height) are comparable.
- The best Rocketbox weight u* for an ICT pose is the u in [0, 1] whose displacements, linearly interpolated
  between renders at GRID, are nearest (least squares over the markers visible in every render of the
  condition) to ICT's. Rocketbox's morph targets are linear, and it is skinned at its bind pose, so its
  positions at u are its positions at 0 plus u times (positions at 1 minus positions at 0).

Fit: training identities 1-8, TRAIN_CAMERAS jittered cameras each, ICT weights TRAIN_WEIGHTS. The knot at each
weight is the median u* over the conditions, made non-decreasing (pool-adjacent-violators) and rounded to six
decimals, with [0, 0] first.

Held-out evaluation: ICT identity 0, one condition per held-out seed of the calibration record (camera and an
ICT weight in HELD_OUT_WEIGHTS derived from the seed and the channel). The error is |curve(w) - u*|, in Rocketbox
weight. A condition is a failure (the expected response was not detected) if fewer than half the region's
markers, or fewer than 3, are visible in all its renders; if ICT's own motion is below MIN_MOTION_PX; if
Rocketbox at u* explains less than MIN_QUALITY of ICT's motion (1 - residual^2 / |ICT motion|^2), meaning the
shapes move differently; or if u* = 1 and ICT's motion is more than SATURATION times Rocketbox's best reach,
meaning Rocketbox cannot produce the motion at all. A condition with too few visible markers has no u*; its error
counts as 1.

Usage:
  rig_gains.py fit --ict-cache DIR --rig-cache DIR --renderer BIN --work DIR --out fit.json
  rig_gains.py evaluate --record calibration/ID.cal --ict-cache DIR --rig-cache DIR --renderer BIN --work DIR --out cells.json
  rig_gains.py export --record calibration/ID.cal --out examples/data/rig_gains.json
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from multiprocessing import get_context
import os
from pathlib import Path
import statistics
import struct
import subprocess
import zlib

import ict_facekit

ROOT = Path(__file__).resolve().parents[1]
LANDMARKS = ROOT / 'examples/data/rig_landmarks.json'
RECORD_ID = 'rig-gains.ict-rocketbox-female'
TARGET = 'rocketbox_female'

IMAGE = 384
MARKER_RADIUS = 0.08
SEPARATION = 0.28
PIXEL_THRESHOLD = 8
MIN_WEIGHT = 5 * 255
VISIBLE_FRACTION = 0.4
MIN_MOTION_PX = 0.5
MIN_QUALITY = 0.5
SATURATION = 1.05
FRAME_HALF_HEIGHT = 0.9  # IOD
YAW, PITCH = 30.0, 15.0  # degrees, uniform in +-
DISTANCE = (0.92, 1.08)
FOV = (26.0, 34.0)
OFFSET = 0.05  # IOD, uniform in +- along left and up
TRAIN_IDENTITIES = range(1, 9)
HELD_OUT_IDENTITY = 0
TRAIN_CAMERAS = 3
TRAIN_WEIGHTS = (0.25, 0.5, 0.75, 1.0)
HELD_OUT_WEIGHTS = (0.2, 1.0)
GRID = tuple(i / 8 for i in range(9))
# ICT's eyeballs and the polygons rendered (face to right eyeball; lacrimal fluid, eye blend and occlusion
# shells and eyelashes are left out, since an opaque renderer would draw them over the eyes). ICT README.
ICT_EYEBALLS = {'L': range(21451, 23021), 'R': range(23021, 24591)}
ICT_POLYGONS = 24692


def arkit_name(ict: str) -> str:
    base, _, side = ict.rpartition('_')
    if not base:
        return ict
    if base in ('browInnerUp', 'cheekPuff'):  # ICT splits these one-coefficient shapes into halves
        return base
    return base + {'L': 'Left', 'R': 'Right'}[side]


def channels() -> dict[str, list[str]]:
    """ARKit name -> the ICT shapes that make it, for every ARKit shape ICT has (all but tongueOut)."""
    out: dict[str, list[str]] = {}
    for shape in ict_facekit.EXPRESSIONS:
        out.setdefault(arkit_name(shape), []).append(shape)
    return dict(sorted(out.items()))


def region(arkit: str) -> str:
    for prefix, name in (('brow', 'brows'), ('eyeLook', 'gaze'), ('eye', 'eyes'), ('cheek', 'cheeks'),
                         ('nose', 'nose'), ('jaw', 'jaw')):
        if arkit.startswith(prefix):
            return name
    return 'mouth'


def side(arkit: str) -> str:
    return 'left' if arkit.endswith('Left') else 'right' if arkit.endswith('Right') else 'none'


def signal(arkit: str) -> str:
    return f'arkit.coefficient.{arkit}'


# ---------------------------------------------------------------------------------------------- vectors

def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def scale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def unit(a):
    return scale(a, 1 / math.sqrt(dot(a, a)))


def point(flat, i):
    return (flat[3 * i], flat[3 * i + 1], flat[3 * i + 2])


def mean(points):
    points = list(points)
    return scale((sum(p[0] for p in points), sum(p[1] for p in points), sum(p[2] for p in points)), 1 / len(points))


# ---------------------------------------------------------------------------------------------- rigs

class Rig:
    """A rig's rest positions, triangles, face frame (left, up, forward), eyeballs and landmarks."""

    def __init__(self, name, rest, triangles, frame, eyeballs, landmarks):
        self.name, self.rest, self.triangles = name, rest, triangles
        self.left, self.up, self.forward = frame
        self.eyeballs, self.landmarks = eyeballs, landmarks

    def iod(self, positions) -> float:
        left, right = (mean(point(positions, i) for i in self.eyeballs[s]) for s in 'LR')
        return abs(dot(sub(left, right), self.left))


class ICT(Rig):
    def __init__(self, cache: Path, landmarks: dict):
        ict_facekit.fetch(cache, ict_facekit.CALIBRATION_FILES)
        self.cache = cache
        rest, faces = ict_facekit.read_obj(cache / f'{ict_facekit.NEUTRAL}.obj')
        super().__init__('ict', [c for p in rest for c in p], ict_facekit.triangles(faces[:ICT_POLYGONS]),
                         ((1, 0, 0), (0, 1, 0), (0, 0, 1)), ICT_EYEBALLS, {n: v['ict'] for n, v in landmarks.items()})
        self._deltas: dict[str, list[float]] = {}

    def _shape(self, name: str) -> list[float]:
        if name not in self._deltas:
            shape, _ = ict_facekit.read_obj(self.cache / f'{name}.obj')
            self._deltas[name] = [c - r for c, r in zip((c for p in shape for c in p), self.rest)]
        return self._deltas[name]

    def identity(self, j: int) -> list[float]:
        """ICT's generic neutral plus its first ten identity modes, with standard-normal coefficients derived from j."""
        out = list(self.rest)
        for i, mode in enumerate(ict_facekit.IDENTITY_MODES):
            c = normal_deviate(f'rcef.k3.identity:{j}:{i}')
            out = [o + c * x for o, x in zip(out, self._shape(mode))]
        return out

    def delta(self, arkit: str) -> list[float]:
        total = [0.0] * len(self.rest)
        for s in channels()[arkit]:
            total = [t + x for t, x in zip(total, self._shape(s))]
        return total


class Rocketbox(Rig):
    def __init__(self, cache: Path, landmarks: dict):
        import msf_tools as msf
        import rigs
        self.msf, self.rigs = msf, rigs
        self.rig = rigs.load_rocketbox(cache, 'Female')
        self.arkit = {a: i for i, a, _ in self.rig.shapes}
        rest = self._evaluate({})
        triangles = self.rig.indices()
        names = {n: v[TARGET] for n, v in landmarks.items()}
        eyeballs = {s: sorted(component(triangles, names[f'iris_{s}'])) for s in 'LR'}
        super().__init__(TARGET, rest, triangles, ((1, 0, 0), (0, 0, 1), (0, -1, 0)), eyeballs, names)
        self._deltas: dict[str, list[float]] = {}

    def _evaluate(self, weights: dict[int, float]) -> list[float]:
        vector = [0.0] * len(self.rig.targets)
        for k, w in weights.items():
            vector[k] = w
        geometry = self.rigs.require(self.msf.evaluate_geometry(self.rig.snapshot, morph_weights={self.rig.node: vector}))
        return [c for instance in geometry.instances for primitive in instance['primitives']
                for p in primitive['positions'] for c in p]

    def target(self, arkit: str) -> str:
        return self.rig.targets[self.arkit[arkit]]

    def delta(self, arkit: str) -> list[float]:
        if arkit not in self._deltas:
            one = self._evaluate({self.arkit[arkit]: 1.0})
            self._deltas[arkit] = [a - b for a, b in zip(one, self.rest)]
        return self._deltas[arkit]


def component(triangles: list[int], seed: int) -> set[int]:
    """The vertices connected to `seed` through triangle edges."""
    neighbours: dict[int, set[int]] = {}
    for t in range(0, len(triangles), 3):
        a, b, c = triangles[t:t + 3]
        for u, v in ((a, b), (b, c), (c, a)):
            neighbours.setdefault(u, set()).add(v)
            neighbours.setdefault(v, set()).add(u)
    seen, stack = {seed}, [seed]
    while stack:
        for u in neighbours.get(stack.pop(), ()):
            if u not in seen:
                seen.add(u)
                stack.append(u)
    return seen


def posed(base: list[float], delta: list[float], w: float) -> list[float]:
    return [b + w * d for b, d in zip(base, delta)] if w else list(base)


# ---------------------------------------------------------------------------------------------- conditions

def uniforms(text: str, count: int) -> list[float]:
    """`count` numbers in [0, 1) from the SHA-256 of `text` (4 bytes each, big-endian)."""
    digest = hashlib.sha256(text.encode()).digest()
    return [int.from_bytes(digest[4 * i:4 * i + 4], 'big') / 2 ** 32 for i in range(count)]


def normal_deviate(text: str) -> float:
    """A standard normal deviate from the SHA-256 of `text` (Box-Muller on its first two 8-byte words)."""
    a, b = (int.from_bytes(hashlib.sha256(text.encode()).digest()[k:k + 8], 'big') for k in (0, 8))
    u1, u2 = (a + 0.5) / 2 ** 64, (b + 0.5) / 2 ** 64
    return math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)


def camera_params(text: str, with_weight: bool = False) -> dict:
    u = uniforms(text, 7)
    lerp = lambda lo, hi, t: lo + (hi - lo) * t  # noqa: E731
    params = {'yaw': lerp(-YAW, YAW, u[0]), 'pitch': lerp(-PITCH, PITCH, u[1]), 'distance': lerp(*DISTANCE, u[2]),
              'fov': lerp(*FOV, u[3]), 'offset_left': lerp(-OFFSET, OFFSET, u[4]), 'offset_up': lerp(-OFFSET, OFFSET, u[5])}
    if with_weight:
        params['weight'] = lerp(*HELD_OUT_WEIGHTS, u[6])
    return params


def camera(rig: Rig, base: list[float], names: list[str], params: dict) -> dict:
    """Aim at the region's landmark centroid from a jittered direction, framing FRAME_HALF_HEIGHT IODs."""
    iod = rig.iod(base)
    centre = mean(point(base, rig.landmarks[n]) for n in names)
    target = add(centre, scale(add(scale(rig.left, params['offset_left']), scale(rig.up, params['offset_up'])), iod))
    yaw, pitch = math.radians(params['yaw']), math.radians(params['pitch'])
    flat = add(scale(rig.forward, math.cos(yaw)), scale(rig.left, math.sin(yaw)))
    direction = add(scale(flat, math.cos(pitch)), scale(rig.up, math.sin(pitch)))
    distance = FRAME_HALF_HEIGHT * iod / math.tan(math.radians(params['fov']) / 2) * params['distance']
    return {'position': list(add(target, scale(direction, distance))), 'target': list(target), 'up': list(rig.up),
            'yfov': params['fov'], 'iod': iod}


def project(cam: dict, p) -> tuple[float, float, float]:
    """Pixel position and depth of a point, as SceneKit's camera with a vertical field of view draws it."""
    f = unit(sub(cam['target'], cam['position']))
    r = unit(cross(f, cam['up']))
    u = cross(r, f)
    d = sub(p, cam['position'])
    z = dot(d, f)
    t = math.tan(math.radians(cam['yfov']) / 2)
    return (dot(d, r) / (z * t) + 1) / 2 * IMAGE, (1 - dot(d, u) / (z * t)) / 2 * IMAGE, z


# ---------------------------------------------------------------------------------------------- markers

def passes(rigs_: list[Rig], names: list[str]) -> list[list[tuple[str, int]]]:
    """Assign each marker a (pass, colour channel) so that markers sharing one are SEPARATION apart on every rig."""
    slots: list[list[list[str]]] = []

    def apart(a: str, b: str) -> bool:
        return all(math.dist(point(r.rest, r.landmarks[a]), point(r.rest, r.landmarks[b])) / r.iod(r.rest) >= SEPARATION
                   for r in rigs_)
    for name in names:
        for colours in slots + [[[], [], []]]:
            free = [c for c in range(3) if all(apart(name, m) for m in colours[c])]
            if free:
                if colours not in slots:
                    slots.append(colours)
                colours[free[0]].append(name)
                break
    return [[(n, c) for c, members in enumerate(colours) for n in members] for colours in slots]


def marker_colours(rig: Rig, assignment: list[tuple[str, int]]) -> list[float]:
    radius = MARKER_RADIUS * rig.iod(rig.rest)
    count = len(rig.rest) // 3
    colours = [0.0] * (3 * count)
    for name, channel in assignment:
        centre = point(rig.rest, rig.landmarks[name])
        for i in range(count):
            d = math.dist(point(rig.rest, i), centre)
            if d < radius:
                colours[3 * i + channel] = max(colours[3 * i + channel], 1 - d / radius)
    return colours


def write_f32(path: Path, values) -> str:
    if not path.exists():
        path.write_bytes(struct.pack(f'<{len(values)}f', *values))
    return str(path)


def write_u32(path: Path, values) -> str:
    if not path.exists():
        path.write_bytes(struct.pack(f'<{len(values)}I', *values))
    return str(path)


# ---------------------------------------------------------------------------------------------- PNG

def read_png(path: str) -> tuple[int, int, int, list[bytearray]]:
    """Width, height, bytes per pixel and unfiltered rows of an 8-bit RGB or RGBA PNG (the renderer's output)."""
    data = Path(path).read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'{path}: not a PNG')
    pos, chunks, header = 8, [], None
    while pos < len(data):
        length, kind = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if kind == b'IHDR':
            header = struct.unpack('>IIBBBBB', body)
        elif kind == b'IDAT':
            chunks.append(body)
        pos += 12 + length
    w, h, depth, colour, _, _, interlace = header
    if depth != 8 or colour not in (2, 6) or interlace:
        raise ValueError(f'{path}: only 8-bit, non-interlaced RGB(A) PNGs are read')
    bpp = 4 if colour == 6 else 3
    raw = zlib.decompress(b''.join(chunks))
    stride, rows, prev, i = w * bpp, [], bytearray(w * bpp), 0
    for _ in range(h):
        kind, line = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        if kind == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 255
        elif kind == 2:
            line = bytearray((a + b) & 255 for a, b in zip(line, prev))
        elif kind == 3:
            for x in range(stride):
                line[x] = (line[x] + ((line[x - bpp] if x >= bpp else 0) + prev[x]) // 2) & 255
        elif kind == 4 and (any(line) or any(prev)):
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(line)
        prev = line
    return w, h, bpp, rows


def measure(job: tuple[str, list[tuple[str, int, float, float, float]]]) -> dict[str, tuple[float, float, float]]:
    """Weighted centroid and weight of each marker's channel within its window."""
    path, markers = job
    w, h, bpp, rows = read_png(path)
    out = {}
    for name, channel, px, py, radius in markers:
        sx = sy = total = 0.0
        y0, y1 = max(0, int(py - radius)), min(h - 1, int(py + radius) + 1)
        x0, x1 = max(0, int(px - radius)), min(w - 1, int(px + radius) + 1)
        r2 = radius * radius
        for y in range(y0, y1 + 1):
            row = rows[y]
            dy2 = (y + 0.5 - py) ** 2
            for x in range(x0, x1 + 1):
                v = row[x * bpp + channel]
                if v > PIXEL_THRESHOLD and (x + 0.5 - px) ** 2 + dy2 <= r2:
                    sx += v * (x + 0.5)
                    sy += v * (y + 0.5)
                    total += v
        out[name] = (sx / total, sy / total, total) if total else (px, py, 0.0)
    return out


# ---------------------------------------------------------------------------------------------- one channel

class Session:
    """Renders and measures the conditions of one channel."""

    def __init__(self, ict: ICT, rocketbox: Rocketbox, renderer: str, work: Path, workers: int):
        self.ict, self.rb, self.renderer, self.work, self.workers = ict, rocketbox, renderer, work, workers
        self.landmarks = json.loads(LANDMARKS.read_text(encoding='utf-8'))
        work.mkdir(parents=True, exist_ok=True)
        self.indices = {r.name: write_u32(work / f'{r.name}.u32', r.triangles) for r in (ict, rocketbox)}
        self.identities: dict[int, list[float]] = {}
        self.keep_images = False

    def identity(self, j: int) -> list[float]:
        if j not in self.identities:
            self.identities[j] = self.ict.identity(j)
        return self.identities[j]

    def run(self, arkit: str, conditions: list[dict]) -> list[dict]:
        """Render and measure each condition ({'identity', 'params', 'ict_weights', 'rb_weights'}); adds
        'cameras' and 'measured' ({rig: {weight: {marker: (x, y, weight)}}}) to each."""
        names = self.landmarks['regions'][region(arkit)]
        plan = passes([self.ict, self.rb], names)
        folder = self.work / arkit
        folder.mkdir(exist_ok=True)
        colours = {(r.name, k): write_f32(folder / f'{r.name}.pass{k}.colours.f32', marker_colours(r, a))
                   for r in (self.ict, self.rb) for k, a in enumerate(plan)}
        deltas = {'ict': self.ict.delta(arkit), TARGET: self.rb.delta(arkit)}
        jobs, wanted = [], []
        for n, cond in enumerate(conditions):
            bases = {'ict': self.identity(cond['identity']), TARGET: self.rb.rest}
            cond['cameras'] = {}
            for rig, weights in ((self.ict, cond['ict_weights']), (self.rb, cond['rb_weights'])):
                base = bases[rig.name]
                cam = camera(rig, base, names, cond['params'])
                cond['cameras'][rig.name] = cam
                ident = f'id{cond["identity"]}' if rig is self.ict else 'rest'
                for w in weights:
                    positions = posed(base, deltas[rig.name], w)
                    geometry = write_f32(folder / f'{rig.name}.{ident}.{w!r}.f32', positions)
                    radius_world = MARKER_RADIUS * cam['iod']
                    for k, assignment in enumerate(plan):
                        out = str(folder / f'c{n}.{rig.name}.{w!r}.p{k}.png')
                        markers = []
                        for name, channel in assignment:
                            px, py, z = project(cam, point(positions, rig.landmarks[name]))
                            r_px = radius_world / (z * math.tan(math.radians(cam['yfov']) / 2)) * IMAGE / 2
                            markers.append((name, channel, px, py, max(6.0, 1.6 * r_px)))
                        jobs.append({'positions': geometry, 'indices': self.indices[rig.name],
                                     'colors': colours[(rig.name, k)], 'lit': False, 'background': [0, 0, 0],
                                     'camera': {kk: cam[kk] for kk in ('position', 'target', 'up', 'yfov')}, 'out': out})
                        wanted.append((n, rig.name, w, (out, markers)))
        self.render(folder, jobs)
        with get_context('spawn').Pool(self.workers) as pool:
            results = pool.map(measure, [job for *_, job in wanted], chunksize=4)
        for cond in conditions:
            cond['measured'] = {'ict': {}, TARGET: {}}
        for (n, rig, w, _), found in zip(wanted, results):
            conditions[n]['measured'][rig].setdefault(w, {}).update(found)
        if not self.keep_images:
            for job in jobs:
                Path(job['out']).unlink()
        return conditions

    def render(self, folder: Path, jobs: list[dict]) -> None:
        processes = []
        for i in range(4):
            chunk = jobs[i::4]
            if chunk:
                batch = folder / f'jobs{i}.json'
                batch.write_text(json.dumps({'width': IMAGE, 'height': IMAGE, 'jobs': chunk}))
                processes.append(subprocess.Popen([self.renderer, str(batch)], stdout=subprocess.DEVNULL))
        if any(p.wait() for p in processes):
            raise SystemExit(f'{self.renderer} failed')


# ---------------------------------------------------------------------------------------------- analysis

def displacements(measured: dict, w: float, names: list[str]) -> dict[str, tuple[float, float]]:
    rest = measured[0.0]
    return {n: ((measured[w][n][0] - rest[n][0]) / IMAGE, (measured[w][n][1] - rest[n][1]) / IMAGE) for n in names}


def visible(measured: dict, weights, names: list[str]) -> list[str]:
    rest = measured[0.0]
    return [n for n in names if rest[n][2] >= MIN_WEIGHT
            and all(measured[w][n][2] >= VISIBLE_FRACTION * rest[n][2] for w in weights)]


def norm2(d: dict) -> float:
    return sum(x * x + y * y for x, y in d.values())


def best_weight(target: dict, grid: dict[float, dict]) -> tuple[float, float]:
    """The u in [0, 1] nearest to `target` with Rocketbox's displacements interpolated linearly between GRID
    renders, and the squared residual there. Ties go to the smaller u."""
    best = (0.0, norm2(target))
    for lo, hi in zip(GRID, GRID[1:]):
        a, b = grid[lo], grid[hi]
        step = {n: (b[n][0] - a[n][0], b[n][1] - a[n][1]) for n in target}
        off = {n: (target[n][0] - a[n][0], target[n][1] - a[n][1]) for n in target}
        length = norm2(step)
        t = 0.0 if length == 0 else min(1.0, max(0.0, sum(off[n][0] * step[n][0] + off[n][1] * step[n][1]
                                                          for n in target) / length))
        residual = sum((off[n][0] - t * step[n][0]) ** 2 + (off[n][1] - t * step[n][1]) ** 2 for n in target)
        if residual < best[1] - 1e-18:
            best = (lo + t * (hi - lo), residual)
    return best


def analyse(cond: dict, w: float, region_names: list[str]) -> dict:
    """u*, match quality and failure reason (if any) for ICT weight w in one condition."""
    ict, rb = cond['measured']['ict'], cond['measured'][TARGET]
    seen = [n for n in visible(ict, [w], region_names) if n in visible(rb, GRID[1:], region_names)]
    result = {'weight': w, 'visible': len(seen), 'markers': len(region_names), 'u': None}
    if len(seen) < max(3, math.ceil(len(region_names) / 2)):
        return {**result, 'failure': 'too few markers visible'}
    target = displacements(ict, w, seen)
    grid = {u: displacements(rb, u, seen) for u in GRID}
    motion = math.sqrt(norm2(target)) * IMAGE
    u, residual = best_weight(target, grid)
    quality = 1 - residual / norm2(target) if norm2(target) else 0.0
    reach = grid[1.0]
    stretch = (sum(target[n][0] * reach[n][0] + target[n][1] * reach[n][1] for n in seen) / norm2(reach)
               if norm2(reach) else math.inf)
    result.update(u=u, quality=quality, motion_px=motion, stretch=stretch)
    if motion < MIN_MOTION_PX:
        result['failure'] = 'reference motion below detection'
    elif quality < MIN_QUALITY:
        result['failure'] = 'Rocketbox explains too little of the reference motion (the shapes move differently)'
    elif u >= 1.0 and stretch > SATURATION:
        result['failure'] = 'Rocketbox cannot reach the reference motion at weight 1'
    return result


def pava(values: list[float]) -> list[float]:
    """Pool-adjacent-violators: the non-decreasing sequence nearest (least squares) to `values`."""
    blocks = [[v, 1] for v in values]
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][0] > blocks[i + 1][0]:
            count = blocks[i][1] + blocks[i + 1][1]
            blocks[i:i + 2] = [[(blocks[i][0] * blocks[i][1] + blocks[i + 1][0] * blocks[i + 1][1]) / count, count]]
            i = max(i - 1, 0)
        else:
            i += 1
    return [v for v, c in blocks for _ in range(c)]


def curve_value(knots: list[list[float]], x) -> Fraction:
    """The piecewise-linear curve through `knots` at x, exactly; not extrapolated past the end knots."""
    x = Fraction(x)
    pts = [(Fraction(a), Fraction(b)) for a, b in knots]
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def p95(values: list[float]) -> float:
    """The nearest-rank 95th percentile."""
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


# ---------------------------------------------------------------------------------------------- commands

def load_rigs(args) -> tuple[ICT, Rocketbox]:
    landmarks = json.loads(LANDMARKS.read_text(encoding='utf-8'))['landmarks']
    return ICT(Path(args.ict_cache), landmarks), Rocketbox(Path(args.rig_cache), landmarks)


def selected(args) -> list[str]:
    wanted = args.channels.split(',') if args.channels else None
    return [n for n in channels() if wanted is None or n in wanted]


def fit(args) -> int:
    ict, rb = load_rigs(args)
    session = Session(ict, rb, args.renderer, Path(args.work), args.workers)
    out = {'record': RECORD_ID, 'channels': {}}
    for arkit in selected(args):
        names = session.landmarks['regions'][region(arkit)]
        conditions = [{'identity': j, 'params': camera_params(f'rcef.k3.train:{arkit}:{j}:{k}'),
                       'ict_weights': (0.0,) + TRAIN_WEIGHTS, 'rb_weights': GRID}
                      for j in TRAIN_IDENTITIES for k in range(TRAIN_CAMERAS)]
        session.run(arkit, conditions)
        rows = [[analyse(c, w, names) for w in TRAIN_WEIGHTS] for c in conditions]
        medians = []
        for k, w in enumerate(TRAIN_WEIGHTS):
            us = [r[k]['u'] for r in rows if r[k]['u'] is not None]
            medians.append(statistics.median(us) if us else w)
        knots = [[0.0, 0.0]] + [[w, round(min(1.0, max(0.0, m)), 6)] for w, m in zip(TRAIN_WEIGHTS, pava(medians))]
        for i in range(1, len(knots)):
            knots[i][1] = max(knots[i][1], knots[i - 1][1])
        failures = sum('failure' in x for r in rows for x in r)
        out['channels'][arkit] = {'knots': knots, 'medians': medians, 'target': rb.target(arkit),
                                  'training_failures': failures, 'training_cases': len(rows) * len(TRAIN_WEIGHTS),
                                  'markers': len(names), 'passes': len(passes([ict, rb], names)), 'rows': rows}
        print(f'{arkit}: knots {knots} (training failures {failures}/{len(rows) * len(TRAIN_WEIGHTS)})', flush=True)
        Path(args.out).write_text(json.dumps(out, indent=1))
    return 0


def load_check():
    spec = importlib.util.spec_from_file_location('rcef_check', ROOT / 'check.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate(args) -> int:
    check = load_check()
    record = check.load_record(Path(args.record))
    seeds = check.held_out_seeds(record)
    curves = {c['input']: c['knots'] for c in record['curves']}
    ict, rb = load_rigs(args)
    session = Session(ict, rb, args.renderer, Path(args.work), args.workers)
    out = {'record': record['id'], 'frozen_sha256': record['held_out']['frozen_sha256'], 'cells': [], 'conditions': {}}
    for arkit in selected(args):
        knots = curves[signal(arkit)]
        names = session.landmarks['regions'][region(arkit)]
        conditions = []
        for s in seeds:
            params = camera_params(f'rcef.k3.heldout:{s}:{arkit}', with_weight=True)
            conditions.append({'identity': args.identity, 'params': params,
                               'ict_weights': (0.0, params['weight']), 'rb_weights': GRID})
        session.run(arkit, conditions)
        details = []
        for c in conditions:
            w = c['params']['weight']
            r = analyse(c, w, names)
            r['curve'] = float(curve_value(knots, w))
            r['error'] = 1.0 if r['u'] is None else abs(r['curve'] - r['u'])
            r['error_uncalibrated'] = 1.0 if r['u'] is None else abs(w - r['u'])
            details.append(r)
        errors = [r['error'] for r in details]
        before = [r['error_uncalibrated'] for r in details]
        cell = {'channel': signal(arkit), 'side': side(arkit),
                'stimulus': f'ICT weight in [{HELD_OUT_WEIGHTS[0]}, {HELD_OUT_WEIGHTS[1]}], jittered camera',
                'identity': f'ICT identity {args.identity}' + (' (held out)' if args.identity == HELD_OUT_IDENTITY else ''),
                'conditions': len(conditions),
                'failures': sum('failure' in r for r in details), 'median': round(statistics.median(errors), 6),
                'p95': round(p95(errors), 6), 'neutral': round(abs(float(curve_value(knots, 0))), 6)}
        out['cells'].append(cell)
        out['conditions'][arkit] = {'details': details, 'median_uncalibrated': statistics.median(before),
                                    'p95_uncalibrated': p95(before)}
        print(f'{arkit}: failures {cell["failures"]}/{len(conditions)} median {cell["median"]} p95 {cell["p95"]} '
              f'(uncalibrated median {statistics.median(before):.4f})', flush=True)
        Path(args.out).write_text(json.dumps(out, indent=1))
    return 0


def export(args) -> int:
    check = load_check()
    record = check.load_record(Path(args.record))
    passed: dict[str, list] = {}
    failed: dict[str, str] = {}
    for curve in record['curves']:
        cells = [c for c in record['cells'] if c['channel'] == curve['input']]
        arkit = curve['input'].rsplit('.', 1)[1]
        bad = [c for c in cells if not check.cell_passes(record, c)]
        if cells and not bad:
            passed[arkit] = curve['knots']
        else:
            failed[arkit] = (f'held-out cell failed: {bad[0]["failures"]} of {bad[0]["conditions"]} conditions not '
                             f'detected, median error {bad[0]["median"]}, p95 {bad[0]["p95"]}' if bad else 'no held-out cell')
    data = {
        'format': 'rcef.example.rig_gains/1',
        'note': ("A rendering correction for RCEF's face examples: maps an ARKit weight as ICT-FaceKit renders it to the "
                 'Rocketbox Female weight that moves her face about as much. It calibrates how two example rigs render '
                 'ARKit names, not any tracker; it is not a provider claim and not pack data. Shapes under '
                 'not_normalised failed their held-out evaluation and are left unchanged.'),
        'record': f'calibration/{record["id"]}.cal',
        'frozen_sha256': record['held_out']['frozen_sha256'],
        'reference_rig': 'ict', 'rig': 'rocketbox-female',
        'curves': dict(sorted(passed.items())),
        'not_normalised': dict(sorted(failed.items())),
    }
    Path(args.out).write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8')
    print(f'{len(passed)} curves, {len(failed)} shapes not normalised -> {args.out}')
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('fit', 'evaluate'):
        p = commands.add_parser(name)
        p.add_argument('--ict-cache', required=True)
        p.add_argument('--rig-cache', required=True)
        p.add_argument('--renderer', required=True, help='a meshrender binary built from tools/render/meshrender.swift')
        p.add_argument('--work', required=True)
        p.add_argument('--out', required=True)
        p.add_argument('--channels', help='comma-separated ARKit names (default: all)')
        p.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 2))
        if name == 'evaluate':
            p.add_argument('--record', required=True)
            p.add_argument('--identity', type=int, default=HELD_OUT_IDENTITY,
                           help='ICT identity to evaluate on (default: the held-out one); others are for dry runs')
    p = commands.add_parser('export')
    p.add_argument('--record', required=True)
    p.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    return {'fit': fit, 'evaluate': evaluate, 'export': export}[args.command](args)


if __name__ == '__main__':
    raise SystemExit(main())
