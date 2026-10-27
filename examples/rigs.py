# SPDX-License-Identifier: MIT
"""The face rigs the examples drive: two Rocketbox avatars, ICT-FaceKit and a VRM sample.

Every rig is fetched into a cache outside the repository, checked against a
pinned SHA-256 and loaded with msf_tools.inspect_asset; none is committed.

- Microsoft Rocketbox (MIT): Female_Adult_01 and Male_Adult_01 "facial" FBX
  files, with Apple's 52 ARKit shapes (AK_*), the 15 Oculus visemes (AA_VI_*)
  and FACS action-unit shapes (AU_*), authored independently of ICT-FaceKit.
- ICT-FaceKit Light (MIT): the 16 ARKit-named shapes RCEF's rules drove first.
- VRM1_Constraint_Twist_Sample (VRM Public License 1.0, redistribution and
  modification allowed, credit not required): VRM 1.0 expression presets.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
from pathlib import Path
import re
import struct
from urllib.request import Request, urlopen

import msf_tools as msf

import ict_facekit

ROCKETBOX_COMMIT = '0943055db6ec570bcef9f2c8b41c9e5467c808f9'
ROCKETBOX_RAW = f'https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/{ROCKETBOX_COMMIT}/'
VRM_COMMIT = '94e82dd346fa6cf0337c4421728640e5252dd38e'
VRM_RAW = f'https://raw.githubusercontent.com/vrm-c/vrm-specification/{VRM_COMMIT}/'
FILES = {
    'Female_Adult_01_facial.fbx': (
        ROCKETBOX_RAW + 'Assets/Avatars/Adults/Female_Adult_01/Export/Female_Adult_01_facial.fbx',
        '2e6ba71fb83a6899e3d4dd35da07fb5b078eef0c4d593f73d70cfc05dc4644cb'),
    'Male_Adult_01_facial.fbx': (
        ROCKETBOX_RAW + 'Assets/Avatars/Adults/Male_Adult_01/Export/Male_Adult_01_facial.fbx',
        '55771cbbcffb8204dcfe450784c8439ee27bfa48efffc48d325b55ee4bd04388'),
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


def load_rocketbox(cache: Path, which: str) -> Rig:
    name = f'{which}_Adult_01_facial.fbx'
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
    return Rig(f'rocketbox-{which.lower()}', f'{ROCKETBOX_CREDIT} ({which}_Adult_01)', snapshot, node, targets,
               shapes=[(i, a, None) for i, a in arkit.items()], visemes=rocketbox_visemes(targets),
               facs={t: i for i, t in enumerate(targets) if t.startswith('AU_')})


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
    return load_rocketbox(cache, {'rocketbox-female': 'Female', 'rocketbox-male': 'Male'}[name])


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
