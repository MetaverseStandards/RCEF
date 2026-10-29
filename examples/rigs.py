# SPDX-License-Identifier: MIT
"""The face rigs the examples drive: two Rocketbox avatars, ICT-FaceKit and a VRM sample.

Every rig is fetched into a cache outside the repository, checked against a
pinned SHA-256 and loaded with msf_character_tools.inspect_asset; none is committed.

- Microsoft Rocketbox (MIT): Female_Adult_01 and Male_Adult_01 "facial" FBX
  files, with Apple's 52 ARKit shapes (AK_*), the 15 Oculus visemes (AA_VI_*)
  and FACS action-unit shapes (AU_*), authored independently of ICT-FaceKit.
  The viseme pose tool also reads 12 more Rocketbox adults (ROCKETBOX_SHA256),
  as rocketbox-female-NN and rocketbox-male-NN.
- ICT-FaceKit Light (MIT): the 16 ARKit-named shapes RCEF's mappings drove first.
- VRM1_Constraint_Twist_Sample (VRM Public License 1.0, redistribution and
  modification allowed, credit not required): VRM 1.0 expression presets.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import struct
from urllib.request import Request, urlopen

import msf_character_tools as msf

import ict_facekit

ROCKETBOX_COMMIT = '0943055db6ec570bcef9f2c8b41c9e5467c808f9'
ROCKETBOX_RAW = f'https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/{ROCKETBOX_COMMIT}/'
VRM_COMMIT = '94e82dd346fa6cf0337c4421728640e5252dd38e'
VRM_RAW = f'https://raw.githubusercontent.com/vrm-c/vrm-specification/{VRM_COMMIT}/'
# The Rocketbox facial FBX files the examples and tools read, by avatar.
ROCKETBOX_SHA256 = {
    'Female_Adult_01': '2e6ba71fb83a6899e3d4dd35da07fb5b078eef0c4d593f73d70cfc05dc4644cb',
    'Male_Adult_01': '55771cbbcffb8204dcfe450784c8439ee27bfa48efffc48d325b55ee4bd04388',
    'Female_Adult_04': 'ce83b428828314ef675d1a64ca17d8c3d2178cc4f8b3e80273483f83f08748fb',
    'Female_Adult_08': 'a98436064305b968d8bbf8a84632c746dbf5674c572f1916264f13ce53e7422d',
    'Female_Adult_10': '7b7208b23688af2f884570a4aaa47ef803442fba2bdb2433f196bb977459e4b5',
    'Female_Adult_12': '0dd67a4fd3f9d9b3a73d17e0862742ebb3197016387915b41f4815d50308c7ef',
    'Female_Adult_13': 'fd3aabfd6e34ada38d3d7137075e4955701234cfc0f40613eae07f3750a36983',
    'Female_Adult_14': '8fcaa34c4ed5c3ea5f6b9add7e9a39ac0184d11232688102ef0811ef8cf2914c',
    'Male_Adult_03': '88aedb2f47ce68dab7ddaf1f53f6357290dc4edb69fc26e3d5fa27d18ee0785a',
    'Male_Adult_05': '2ae6474a98d477d3c46553cb93ea3d452179afa4756db18c23e8aec97982a161',
    'Male_Adult_10': 'e62c3c1345150d4cfebf454fbcb906d3cc8f4c846f4ee63e06d6928438b409a3',
    'Male_Adult_11': '7c58b696c6f570a13dc6cb4d22f71d7ea82884eca095549fe2122c94a7f0b857',
    'Male_Adult_13': 'acf0693228d3c3bca085f724aae2965c904b38d768bc0a71ba8a4606ab806549',
    'Male_Adult_17': 'e779639155a145c027c54f7f6d91a2a82ad4be862bebee64337ef08245cb86b2',
}
FILES = {
    **{f'{avatar}_facial.fbx': (ROCKETBOX_RAW + f'Assets/Avatars/Adults/{avatar}/Export/{avatar}_facial.fbx', digest)
       for avatar, digest in ROCKETBOX_SHA256.items()},
    'ROCKETBOX_LICENSE.md': (ROCKETBOX_RAW + 'LICENSE.md',
                             '17474e386e0b9e1a700cc3d06b2b0882a2c376d9c6b49c7f8274409b8f8d2352'),
    'VRM1_Constraint_Twist_Sample.vrm': (
        VRM_RAW + 'samples/VRM1_Constraint_Twist_Sample/vrm/VRM1_Constraint_Twist_Sample.vrm',
        '12c2b97e95e700783a6a550dc0eee2d7880aeedccef9ae67bc4c5a2f0f2631a2'),
}
ROCKETBOX_CREDIT = 'Microsoft Rocketbox avatar library (c) 2020 Microsoft, MIT license; ARKit shapes by Fang Ma and Matias Volonte'
# Rocketbox numbers its visemes in the order of the Oculus Lipsync set, which is
# also the order of XR_META_face_tracking_visemes; only three names are spelled
# differently (I, O, U for IH, OH, OU).
ROCKETBOX_VISEMES = {'Sil': 'SIL', 'PP': 'PP', 'FF': 'FF', 'TH': 'TH', 'DD': 'DD', 'KK': 'KK', 'CH': 'CH',
                     'SS': 'SS', 'nn': 'NN', 'RR': 'RR', 'aa': 'AA', 'E': 'E', 'I': 'IH', 'O': 'OH', 'U': 'OU'}
META_VISEME_ORDER = ['SIL', 'PP', 'FF', 'TH', 'DD', 'KK', 'CH', 'SS', 'NN', 'RR', 'AA', 'E', 'IH', 'OH', 'OU']
# Rig gains (rig_gains.py, calibration record rig-gains.ict-rocketbox-female): a rendering correction, not pack data.
GAINS = Path(__file__).resolve().parent / 'data/rig_gains.json'


@dataclass
class Rig:
    name: str
    credit: str
    snapshot: object
    node: int
    targets: list[str]
    shapes: list[tuple[int, str, str | None]] = field(default_factory=list)  # (index, ARKit name, half side)
    visemes: dict[str, int] = field(default_factory=dict)  # META viseme -> index
    facs: dict[str, int] = field(default_factory=dict)  # Rocketbox AU target name -> index

    def indices(self) -> list[int]:
        return triangle_indices(self.snapshot)


def fetch(cache: Path, name: str) -> Path:
    """Download `name` into `cache` if missing, and check its SHA-256."""
    url, digest = FILES[name]
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / name
    if not path.exists():
        with urlopen(Request(url, headers={'User-Agent': 'RCEF-example/0.3'}), timeout=300) as response:
            path.write_bytes(response.read())
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit(f'{path}: SHA-256 differs from the pinned file')
    return path


def require(result):
    if not result.ok:
        raise SystemExit(result.report.to_dict())
    return result.value


def lower_first(name: str) -> str:
    return name[:1].lower() + name[1:]


def rocketbox_arkit(targets: list[str]) -> dict[int, str]:
    """Target index -> ARKit name, from names like AK_09_EyeBlinkLeft."""
    return {i: lower_first(m.group(1)) for i, t in enumerate(targets) if (m := re.fullmatch(r'AK_\d\d_(\w+)', t))}


def rocketbox_visemes(targets: list[str]) -> dict[str, int]:
    """META viseme -> target index, from names like AA_VI_10_aa."""
    found = {}
    for i, t in enumerate(targets):
        if m := re.fullmatch(r'AA_VI_(\d\d)_(\w+)', t):
            meta = ROCKETBOX_VISEMES[m.group(2)]
            if META_VISEME_ORDER.index(meta) != int(m.group(1)):
                raise SystemExit(f'{t}: numbered out of the META viseme order')
            found[meta] = i
    return found


def facs_targets(targets: list[str], au_key: str) -> list[int] | None:
    """Rocketbox AU shapes for an AU key such as '12', 'L12' or 'R12'; None if there is none."""
    side, au = (au_key[0], au_key[1:]) if au_key[0] in 'LR' else ('', au_key)
    both, sided = [], {'L': [], 'R': []}
    for i, t in enumerate(targets):
        if m := re.fullmatch(r'AU_(\d\d)_(?:([LR])_)?\w+', t):
            if int(m.group(1)) == int(au):
                (sided[m.group(2)] if m.group(2) else both).append(i)
    if side:
        return sided[side] or None
    return both or (sided['L'] + sided['R']) or None


def load_rocketbox(cache: Path, which: str, number: str = '01') -> Rig:
    name = f'{which}_Adult_{number}_facial.fbx'
    fetch(cache, 'ROCKETBOX_LICENSE.md')
    snapshot = require(msf.inspect_asset(fetch(cache, name).read_bytes(), 'fbx'))
    keys = snapshot.to_dict()['source']['target_keys']
    if len(keys) != 1:
        raise SystemExit(f'{name}: expected one mesh with morph targets')
    targets = [k.split('.', 1)[1] for k in keys[0]]
    node = next(i for i, n in enumerate(snapshot.document['nodes']) if 'mesh' in n)
    arkit = rocketbox_arkit(targets)
    if len(arkit) != 52:
        raise SystemExit(f'{name}: expected 52 ARKit shapes, found {len(arkit)}')
    return Rig(rocketbox_name(which, number), f'{ROCKETBOX_CREDIT} ({which}_Adult_{number})', snapshot, node, targets,
               shapes=[(i, a, None) for i, a in arkit.items()], visemes=rocketbox_visemes(targets),
               facs={t: i for i, t in enumerate(targets) if t.startswith('AU_')})


def rocketbox_name(which: str, number: str) -> str:
    """The rig name of a Rocketbox adult: rocketbox-female for Female_Adult_01, rocketbox-male-05 for Male_Adult_05."""
    return f'rocketbox-{which.lower()}' + ('' if number == '01' else f'-{number}')


def rocketbox_avatar(name: str) -> tuple[str, str] | None:
    """('Female', '04') for the rig name rocketbox-female-04, ('Male', '01') for rocketbox-male; None otherwise."""
    if m := re.fullmatch(r'rocketbox-(female|male)(?:-(\d\d))?', name):
        return m.group(1).capitalize(), m.group(2) or '01'
    return None


def ict_shapes(targets: list[str]) -> list[tuple[int, str, str | None]]:
    """(index, ARKit name, half side) for ICT target names such as eyeBlink_L or browInnerUp_R."""
    shapes = []
    for i, t in enumerate(targets):
        base, _, side = t.rpartition('_')
        if not base:
            shapes.append((i, t, None))
        elif base in ('browInnerUp', 'cheekPuff'):
            # ICT splits these one-coefficient ARKit shapes into halves (its README, line 150).
            shapes.append((i, base, side))
        else:
            shapes.append((i, base + {'L': 'Left', 'R': 'Right'}[side], None))
    return shapes


def load_ict(cache: Path) -> Rig:
    ict_facekit.fetch(cache)
    glb, targets, _ = ict_facekit.build_glb(cache)
    snapshot = require(msf.inspect_asset(glb, 'glb'))
    return Rig('ict', 'ICT-FaceKit (c) 2020 USC Institute for Creative Technologies, MIT license', snapshot, 0,
               targets, shapes=ict_shapes(targets))


def load_vrm(cache: Path) -> Rig:
    snapshot = require(msf.inspect_asset(fetch(cache, 'VRM1_Constraint_Twist_Sample.vrm').read_bytes(), 'glb'))
    meta = snapshot.to_dict()['document']['extensions']['VRMC_vrm']['meta']
    return Rig('vrm-twist', f'{meta["name"]} {meta["copyrightInformation"]}, VRM Public License 1.0 ({meta["licenseUrl"]})',
               snapshot, -1, [])


def load(name: str, cache: Path) -> Rig:
    if name == 'ict':
        return load_ict(cache)
    if name == 'vrm-twist':
        return load_vrm(cache)
    avatar = rocketbox_avatar(name)
    if avatar is None or f'{avatar[0]}_Adult_{avatar[1]}' not in ROCKETBOX_SHA256:
        raise SystemExit(f'unknown rig {name}')
    return load_rocketbox(cache, *avatar)


def triangle_indices(snapshot) -> list[int]:
    """Triangle indices of every mesh primitive, in evaluate_geometry's order, offset into one vertex list."""
    document = snapshot.to_dict()['document']
    data = {r.id: r.data for r in snapshot.resources}
    widths = {5121: 'B', 5123: 'H', 5125: 'I'}
    out, base = [], 0
    for node in document['nodes']:
        if 'mesh' not in node:
            continue
        for primitive in document['meshes'][node['mesh']]['primitives']:
            if primitive.get('mode', 4) != 4:
                raise SystemExit('only triangle primitives are supported')
            count = document['accessors'][primitive['attributes']['POSITION']]['count']
            if 'indices' in primitive:
                accessor = document['accessors'][primitive['indices']]
                view = document['bufferViews'][accessor['bufferView']]
                start = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
                code = widths[accessor['componentType']]
                values = struct.unpack_from(f'<{accessor["count"]}{code}', data[f'/buffers/{view["buffer"]}'], start)
            else:
                values = range(count)
            out += [base + v for v in values]
            base += count
    return out


def piecewise_linear(knots: list[list[float]], x: float) -> float:
    """The piecewise-linear curve through `knots` ([input, output] pairs, increasing inputs) at x, held at the end
    knots' outputs outside their range."""
    if x <= knots[0][0]:
        return knots[0][1]
    for (x0, y0), (x1, y1) in zip(knots, knots[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * ((x - x0) / (x1 - x0))
    return knots[-1][1]


def normalised(weights: dict[str, float], path: Path = GAINS) -> dict[str, float]:
    """ARKit weights for Rocketbox Female such that each shape moves her face about as much as the same weight moves
    ICT-FaceKit's, where the held-out evaluation passed; other shapes are returned unchanged. A rendering correction
    between two example rigs, not a statement about any tracker or provider."""
    curves = json.loads(path.read_text(encoding='utf-8'))['curves']
    return {name: piecewise_linear(curves[name], w) if name in curves else w for name, w in weights.items()}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Pose a rig with ARKit weights and write its positions '
                                                 '(little-endian float32 xyz) and triangle indices (uint32).')
    parser.add_argument('--rig', required=True, choices=['ict', 'rocketbox-female', 'rocketbox-male'])
    parser.add_argument('--cache', type=Path, required=True, help='directory for the rig files')
    parser.add_argument('--set', action='append', default=[], metavar='NAME=WEIGHT', help='an ARKit weight, repeatable')
    parser.add_argument('--normalise', action='store_true',
                        help=f'map the weights through {GAINS.name} first (rocketbox-female only)')
    parser.add_argument('--out', type=Path, required=True, help='output stem: writes STEM.f32 and STEM.u32')
    args = parser.parse_args(argv)
    weights = {name: float(value) for name, value in (item.split('=', 1) for item in args.set)}
    if args.normalise:
        if args.rig != 'rocketbox-female':
            parser.error('rig gains exist only for rocketbox-female (reference: ict)')
        weights = normalised(weights)
    rig = load(args.rig, args.cache)
    by_name = {}
    for index, name, half in rig.shapes:
        by_name.setdefault(name, []).append(index)
    unknown = sorted(set(weights) - set(by_name))
    if unknown:
        parser.error(f'{args.rig} has no ARKit shape {", ".join(unknown)}')
    vector = [0.0] * len(rig.targets)
    for name, w in weights.items():
        for index in by_name[name]:
            vector[index] = w
    geometry = require(msf.evaluate_geometry(rig.snapshot, morph_weights={rig.node: vector}))
    positions = [c for instance in geometry.instances for primitive in instance['primitives']
                 for p in primitive['positions'] for c in p]
    args.out.with_suffix('.f32').write_bytes(struct.pack(f'<{len(positions)}f', *positions))
    indices = rig.indices()
    args.out.with_suffix('.u32').write_bytes(struct.pack(f'<{len(indices)}I', *indices))
    print(json.dumps({'rig': args.rig, 'weights': weights, 'normalised': args.normalise}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
