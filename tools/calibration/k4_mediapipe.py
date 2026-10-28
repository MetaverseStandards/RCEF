#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Measure MediaPipe's blendshape response to untextured renders of ICT-FaceKit, and fit curves back to ARKit weights.

Optional tool: needs numpy, mediapipe, msf-character-tools (for the Rocketbox rig) and a
built tools/render/meshrender. RCEF's own code and tests do not use it.

    python tools/calibration/k4_mediapipe.py fetch
    python tools/calibration/k4_mediapipe.py train --renderer PATH     # training renders and scores
    python tools/calibration/k4_mediapipe.py freeze --renderer PATH    # fit; write the record's frozen part
    (to freeze again as a new version, add --reason TEXT; the ledger needs one after v1)
    (commit the record and its calibration/FREEZES line)
    python tools/calibration/k4_mediapipe.py heldout --renderer PATH   # held-out renders and scores
    python tools/calibration/k4_mediapipe.py evaluate                  # cells into the record; rules for passes

A channel is one ARKit coefficient that MediaPipe also scores. A sweep sets
that coefficient alone to each of WEIGHTS on a face under one condition
(identity, head pose, camera, light, grey level) and records MediaPipe's score
for the same name. Training conditions come from fixed seeds on training ICT
identities. Held-out conditions come from the seeds fixed by the record's
frozen hash, on new ICT identities and on Rocketbox Male, a rig never used in
training.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import ssl
import subprocess
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'examples'))
sys.path.insert(0, str(ROOT))

ICT_COMMIT = 'da5f95a607f5e6b37755b38d3385d7f2853732e5'
ICT_RAW = f'https://raw.githubusercontent.com/ICT-VGL/ICT-FaceKit/{ICT_COMMIT}/'
ICT_FILES = json.loads(Path(__file__).with_name('ict_files.json').read_text(encoding='utf-8'))
# Data the harness reads besides its modules; a held-out run checks these with the code.
DATA_FILES = ['tools/calibration/ict_files.json']
TASK_URL = 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task'
TASK_SHA256 = '64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff'
IDENTITY_MODES = 10
WEIGHTS = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
TRAINING_CONDITIONS = 24
SIZE = 512
# MediaPipe's face_blendshapes graph (evidence "mediapipe"): _neutral and 51 ARKit names, without tongueOut.
CHANNELS = [
    'browDownLeft', 'browDownRight', 'browInnerUp', 'browOuterUpLeft', 'browOuterUpRight', 'cheekPuff',
    'cheekSquintLeft', 'cheekSquintRight', 'eyeBlinkLeft', 'eyeBlinkRight', 'eyeLookDownLeft', 'eyeLookDownRight',
    'eyeLookInLeft', 'eyeLookInRight', 'eyeLookOutLeft', 'eyeLookOutRight', 'eyeLookUpLeft', 'eyeLookUpRight',
    'eyeSquintLeft', 'eyeSquintRight', 'eyeWideLeft', 'eyeWideRight', 'jawForward', 'jawLeft', 'jawOpen', 'jawRight',
    'mouthClose', 'mouthDimpleLeft', 'mouthDimpleRight', 'mouthFrownLeft', 'mouthFrownRight', 'mouthFunnel',
    'mouthLeft', 'mouthLowerDownLeft', 'mouthLowerDownRight', 'mouthPressLeft', 'mouthPressRight', 'mouthPucker',
    'mouthRight', 'mouthRollLower', 'mouthRollUpper', 'mouthShrugLower', 'mouthShrugUpper', 'mouthSmileLeft',
    'mouthSmileRight', 'mouthStretchLeft', 'mouthStretchRight', 'mouthUpperUpLeft', 'mouthUpperUpRight',
    'noseSneerLeft', 'noseSneerRight']


def cache_dir(name: str) -> Path:
    return Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / name


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(url: str, path: Path, digest: str) -> Path:
    if not path.exists():
        context = ssl.create_default_context(cafile=os.environ.get('SSL_CERT_FILE'))
        with urlopen(Request(url, headers={'User-Agent': 'RCEF-calibration/0.1'}), timeout=300,
                     context=context) as response:
            path.write_bytes(response.read())
    if sha256(path) != digest:
        raise SystemExit(f'{path}: SHA-256 differs from the pinned value')
    return path


def fetch(cache: Path) -> None:
    """ICT-FaceKit's neutral head, 53 expressions and first identity modes, and MediaPipe's model, all hash-checked."""
    cache.mkdir(parents=True, exist_ok=True)
    for name, digest in ICT_FILES.items():
        download(ICT_RAW + name, cache / Path(name).name, digest)
    download(TASK_URL, cache / 'face_landmarker.task', TASK_SHA256)


# --- rigs -------------------------------------------------------------------

class Rig:
    """Neutral positions, per-channel deltas, triangles, and the head frame (centre, height, up, forward)."""

    def __init__(self, name, neutral, deltas, triangles, centre, height, up, forward, identities=None):
        self.name, self.neutral, self.deltas, self.triangles = name, neutral, deltas, triangles
        self.centre, self.height, self.up, self.forward = centre, height, up, forward
        self.identities = identities  # ICT identity mode deltas

    def positions(self, channel, weight, identity=None):
        import numpy as np
        p = self.neutral.copy()
        if identity is not None and self.identities is not None:
            p += np.tensordot(np.asarray(identity), self.identities, axes=1)
        if weight:
            p += weight * self.deltas[channel]
        return p


def read_obj(path: Path):
    import numpy as np
    vertices, faces = [], []
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('v '):
            vertices.append(line.split()[1:4])
        elif line.startswith('f '):
            faces.append([int(c.split('/')[0]) - 1 for c in line.split()[1:]])
    return np.asarray(vertices, dtype=float), faces


def fan(faces):
    return [i for f in faces for k in range(1, len(f) - 1) for i in (f[0], f[k], f[k + 1])]


def ict_names(channel: str) -> list[str]:
    """ICT shape names for an ARKit name: _L/_R for sides, and both halves of browInnerUp and cheekPuff."""
    if channel in ('browInnerUp', 'cheekPuff'):
        return [channel + '_L', channel + '_R']
    if channel in ('jawLeft', 'jawRight', 'mouthLeft', 'mouthRight'):
        return [channel]  # movements of the whole jaw or mouth, named as ARKit does
    for side, suffix in (('Left', '_L'), ('Right', '_R')):
        if channel.endswith(side):
            return [channel[:-len(side)] + suffix]
    return [channel]


def load_ict(cache: Path) -> Rig:
    import numpy as np
    neutral, faces = read_obj(cache / 'generic_neutral_mesh.obj')
    deltas = {c: sum(read_obj(cache / f'{n}.obj')[0] - neutral for n in ict_names(c)) for c in CHANNELS}
    identities = np.stack([read_obj(cache / f'identity{i:03d}.obj')[0] - neutral for i in range(IDENTITY_MODES)])
    face = neutral[:9409]  # ICT's "Face" geometry, vertices 0-9408
    return Rig('ict', neutral, deltas, fan(faces), (face.min(0) + face.max(0)) / 2, float(np.ptp(face[:, 1])),
               np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0]), identities)


def load_rocketbox_male(cache: Path) -> Rig:
    """Rocketbox Male's ARKit shapes as linear deltas, each measured once with msf-character-tools."""
    import numpy as np
    import msf_character_tools as msf
    import rigs
    rig = rigs.load_rocketbox(cache, 'Male')

    def positions(weights):
        vector = [0.0] * len(rig.targets)
        for index, w in weights.items():
            vector[index] = w
        geometry = rigs.require(msf.evaluate_geometry(rig.snapshot, morph_weights={rig.node: vector}))
        return np.asarray([p for i in geometry.instances for prim in i['primitives'] for p in prim['positions']])
    neutral = positions({})
    index = {name: i for i, name, _ in rig.shapes}
    deltas = {c: positions({index[c]: 1.0}) - neutral for c in CHANNELS}
    head = neutral[(neutral[:, 2] > neutral[:, 2].max() - 0.3) & (np.abs(neutral[:, 0]) < 0.15)]
    # Rocketbox is z up and faces -y; its head region is about 0.3 m tall.
    return Rig('rocketbox-male', neutral, deltas, rig.indices(), (head.min(0) + head.max(0)) / 2, 0.3,
               np.array([0.0, 0.0, 1.0]), np.array([0.0, -1.0, 0.0]))


# --- conditions -------------------------------------------------------------

CONDITION_TEXT = ('head yaw within +-15 degrees, pitch +-10 and roll +-5; camera distance 0.9 to 1.2 of the framing '
                  'distance and vertical field of view 25 to 35 degrees; key light pitch -0.8 to 0.1 rad and yaw '
                  '+-0.8 rad, key 600 to 1100 and ambient 150 to 400; grey level 0.55 to 0.85 on a 0.05 to 0.3 '
                  'background; 512 x 512 renders')


def condition(rng: random.Random) -> dict:
    """One rendering condition: head pose, camera, light and grey levels."""
    return {'yaw': rng.uniform(-15, 15), 'pitch': rng.uniform(-10, 10), 'roll': rng.uniform(-5, 5),
            'distance': rng.uniform(0.9, 1.2), 'yfov': rng.uniform(25, 35),
            'light_pitch': rng.uniform(-0.8, 0.1), 'light_yaw': rng.uniform(-0.8, 0.8),
            'key': rng.uniform(600, 1100), 'ambient': rng.uniform(150, 400),
            'grey': rng.uniform(0.55, 0.85), 'background': rng.uniform(0.05, 0.3)}


def identity(rng: random.Random) -> list[float]:
    """ICT identity weights for the first IDENTITY_MODES modes, each from a standard normal, as ICT's sampler does."""
    return [rng.gauss(0.0, 1.0) for _ in range(IDENTITY_MODES)]


def training_conditions() -> list[dict]:
    out = []
    for i in range(TRAINING_CONDITIONS):
        rng = random.Random(f'rcef.k4.training:{i}')
        out.append({**condition(rng), 'identity': identity(rng)})
    return out


def held_out_conditions(seeds: list[int], ict: bool) -> list[dict]:
    """Condition i from held-out seed i; on ICT it also carries a new identity drawn from the same seed."""
    out = []
    for seed in seeds:
        rng = random.Random(seed)
        c = condition(rng)
        weights = identity(rng)
        out.append({**c, 'identity': weights} if ict else c)
    return out


def rotation(rig: Rig, c: dict):
    import numpy as np
    right = np.cross(rig.forward, rig.up)

    def about(axis, degrees):
        a = math.radians(degrees)
        k = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
        return np.eye(3) + math.sin(a) * k + (1 - math.cos(a)) * k @ k
    return about(rig.up, c['yaw']) @ about(right, c['pitch']) @ about(rig.forward, c['roll'])


def job(rig: Rig, c: dict, positions_path: Path, indices_path: Path, out: Path) -> dict:
    distance = rig.height * 0.75 / math.tan(math.radians(c['yfov']) / 2) * c['distance']
    return {'positions': str(positions_path), 'indices': str(indices_path), 'out': str(out),
            'color': [c['grey']] * 3, 'background': [c['background']] * 3,
            'camera': {'position': [float(v) for v in rig.centre + distance * rig.forward],
                       'target': [float(v) for v in rig.centre], 'up': [float(v) for v in rig.up], 'yfov': c['yfov']},
            'light': {'pitch': c['light_pitch'], 'yaw': c['light_yaw'], 'key': c['key'], 'ambient': c['ambient']}}


# --- render and score -------------------------------------------------------

class Scorer:
    def __init__(self, model: Path):
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions, vision
        self.mp = mp
        options = vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=str(model)), num_faces=1,
                                               output_face_blendshapes=True)
        self.landmarker = vision.FaceLandmarker.create_from_options(options)

    def __call__(self, png: Path) -> dict | None:
        result = self.landmarker.detect(self.mp.Image.create_from_file(str(png)))
        if not result.face_blendshapes:
            return None
        return {c.category_name: c.score for c in result.face_blendshapes[0]}


def sweep_runs(rig: Rig, conditions: list[dict], channels: list[str], renderer: Path, scorer: Scorer, work: Path,
               batch: int = 400) -> list[dict]:
    """Render and score every channel at every weight under every condition; each condition's rest pose is shared."""
    import numpy as np
    indices = work / f'{rig.name}.u32'
    np.asarray(rig.triangles, dtype='<u4').tofile(indices)
    tasks = []
    for k in range(len(conditions)):
        tasks += [(k, None, 0.0)] + [(k, channel, w) for channel in channels for w in WEIGHTS if w]
    results = []
    for start in range(0, len(tasks), batch):
        jobs, chunk = [], tasks[start:start + batch]
        for n, (k, channel, w) in enumerate(chunk):
            c = conditions[k]
            p = rig.positions(channel, w, c.get('identity'))
            p = (p - rig.centre) @ rotation(rig, c).T + rig.centre
            p.astype('<f4').tofile(work / f'p{n}.f32')
            jobs.append(job(rig, c, work / f'p{n}.f32', indices, work / f'i{n}.png'))
        (work / 'jobs.json').write_text(json.dumps({'width': SIZE, 'height': SIZE, 'jobs': jobs}))
        subprocess.run([str(renderer), str(work / 'jobs.json')], check=True, capture_output=True)
        for n, (k, channel, w) in enumerate(chunk):
            results.append({'condition': k, 'channel': channel, 'weight': w, 'scores': scorer(work / f'i{n}.png')})
        print(f'{rig.name}: {min(start + batch, len(tasks))} of {len(tasks)}', file=sys.stderr, flush=True)
    return results


def by_channel(results: list[dict], channels: list[str]) -> dict:
    """{channel: {condition: {weight: score or None}}}; weight 0 is the condition's rest pose."""
    rest = {r['condition']: r['scores'] for r in results if r['channel'] is None}
    out = {c: {k: {0.0: None if s is None else s[c]} for k, s in rest.items()} for c in channels}
    for r in results:
        if r['channel'] in out:
            out[r['channel']][r['condition']][r['weight']] = None if r['scores'] is None else r['scores'][r['channel']]
    return out


# --- fit and evaluate -------------------------------------------------------

MIN_RISE = 0.1  # a median response rising less than this over the sweep cannot be inverted usefully


def isotonic(values: list[float]) -> list[float]:
    """Pool-adjacent-violators: the closest nondecreasing sequence, all points weighted equally."""
    blocks = []
    for v in values:
        blocks.append([v, 1])
        while len(blocks) > 1 and blocks[-2][0] > blocks[-1][0]:
            (a, n), (b, m) = blocks[-2], blocks[-1]
            blocks[-2:] = [[(a * n + b * m) / (n + m), n + m]]
    return [v for v, n in blocks for _ in range(n)]


def fit_channel(sweeps: dict) -> tuple[list[list[float]] | None, str]:
    """Knots of the inverse curve, MediaPipe score -> ARKit weight, from the median score at each weight."""
    medians = []
    for w in WEIGHTS:
        scores = sorted(s[w] for s in sweeps.values() if s.get(w) is not None)
        if len(scores) * 2 < len(sweeps):
            return None, f'no face found in most training renders at weight {w}'
        medians.append(scores[len(scores) // 2])
    response = isotonic(medians)
    if response[-1] - response[0] < MIN_RISE:
        return None, f'the median score rises only {response[-1] - response[0]:.3f} from weight 0 to 1'
    points = []
    for w, r in zip(WEIGHTS, response):
        r = round(r, 6)
        if not points or r > points[-1][0]:
            points.append([r, w])  # in a flat stretch, keep its lowest weight so the inverse stays a function
    knots = ([[0.0, 0.0]] if points[0][0] > 0 else []) + points + ([[1.0, 1.0]] if points[-1][0] < 1 else [])
    knots[0][0], knots[-1][0] = 0.0, 1.0  # the score's domain is exactly [0, 1]
    return knots, 'fitted'


def inverse(knots: list[list[float]], score: float) -> float:
    for (x0, y0), (x1, y1) in zip(knots, knots[1:]):
        if score <= x1:
            return y0 + (score - x0) / (x1 - x0) * (y1 - y0)
    return knots[-1][1]


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)]


def cell(knots, sweeps: dict, conditions: int) -> dict:
    """Errors |inverse(score) - weight| over the first `conditions` conditions; a missed face is a failure."""
    errors, rest, failures = [], [], 0
    for k in sorted(sweeps)[:conditions]:
        sweep = sweeps[k]
        if any(sweep.get(w) is None for w in WEIGHTS):
            failures += 1
            continue
        for w in WEIGHTS:
            errors.append(abs(inverse(knots, sweep[w]) - w))
            if w == 0:
                rest.append(errors[-1])
    if not errors:
        return {'failures': failures, 'median': 1.0, 'p95': 1.0, 'neutral': 1.0}
    return {'failures': failures, 'median': round(quantile(errors, 0.5), 6), 'p95': round(quantile(errors, 0.95), 6),
            'neutral': round(quantile(rest, 0.5), 6)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('command', choices=['fetch', 'train', 'freeze', 'heldout', 'evaluate'])
    parser.add_argument('--cache', type=Path, default=cache_dir('rcef-ict-full'), help='ICT-FaceKit and model cache')
    parser.add_argument('--rig-cache', type=Path, default=cache_dir('rcef-face-rigs'), help='Rocketbox cache')
    parser.add_argument('--renderer', type=Path, help='a meshrender binary built from tools/render')
    parser.add_argument('--out', type=Path, default=cache_dir('rcef-k4'), help='renders and scores (not committed)')
    parser.add_argument('--reason', help='freeze: why the record is frozen again, for a version after v1')
    args = parser.parse_args(argv)
    if args.command == 'fetch':
        fetch(args.cache)
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    import k4_record
    return getattr(k4_record, args.command)(args)


if __name__ == '__main__':
    raise SystemExit(main())
