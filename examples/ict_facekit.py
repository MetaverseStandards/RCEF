# SPDX-License-Identifier: MIT
"""Fetch the ICT-FaceKit Light face model and convert part of it to a glTF binary.

ICT-FaceKit (USC Institute for Creative Technologies, MIT license) ships a
neutral head and ARKit-named expression shapes as OBJ files, with browInnerUp
and cheekPuff split into left and right halves. The files are fetched into a
cache outside the repository and checked against the SHA-256 values below;
they are never committed.

Only the shapes the RCEF FB2 -> ARKit rules can drive are converted. All 53
expression shapes plus the neutral would need about 4.3 million position
components, more than msf-tools' 4 million decoded-component budget, and
sparse accessors do not help because msf-tools counts them at full size.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import struct
from urllib.request import Request, urlopen

REPOSITORY = 'https://github.com/ICT-VGL/ICT-FaceKit'
COMMIT = 'da5f95a607f5e6b37755b38d3385d7f2853732e5'
RAW = f'https://raw.githubusercontent.com/ICT-VGL/ICT-FaceKit/{COMMIT}/'
NEUTRAL = 'generic_neutral_mesh'
FILES = {
    'LICENSE': 'b20a78d8fc51657e14f3e00c8abb538d786ad00aa63210328c22565e583167e1',
    'FaceXModel/generic_neutral_mesh.obj': 'eedbc2576d8e5ea57f55255b8f98263213a1efb5431d8bfceed1d7aef10271f9',
    'FaceXModel/eyeBlink_L.obj': 'f5ed1c3072a400083b7d4f7f5cb3d73882b7ebb95c3232f957394db8cf7fe19e',
    'FaceXModel/eyeBlink_R.obj': 'd281ad0af03e89a70abf1214d52c295b3a279c9b35f6795938c4487f467ca003',
    'FaceXModel/jawOpen.obj': '8d84355e10f48b05550980cee385bcd426f4797090da76a20de0535bb2f99f4a',
    'FaceXModel/mouthClose.obj': '4a44b94c269407cf1171483d87d99d2cbdea9c66242aabf2ad0f57cb785aa193',
    'FaceXModel/eyeLookIn_L.obj': '1e037332bc059a95d05fcb24728ae297a2d4d268ff0cf623d3647d2a4f86bd31',
    'FaceXModel/eyeLookIn_R.obj': '3d64db0e51ad28e76eff56217da401c5ee563b5e76a207cb192046465bbab14a',
    'FaceXModel/eyeLookOut_L.obj': '235739695136c40b7a2c3239a100ff75b7bfc271ae195aeb55330848c999c9c8',
    'FaceXModel/eyeLookOut_R.obj': 'ac10dfa83ccaca7fd76fe96d74f8cbc80582e2ef914d1092827b54f88125650e',
    'FaceXModel/browInnerUp_L.obj': '81fb1625794ea36fb13303234ce06cef798acfdbc489077e22ae195a705bc92e',
    'FaceXModel/browInnerUp_R.obj': '5e66b46cdad89fd1237273db2b885511688cf37636cedfdde432a4844c9109e7',
    'FaceXModel/cheekPuff_L.obj': 'f53fd2bdeb8e26d0db8a684ab9c095c6bb113b74575dec329facae2799ff18c6',
    'FaceXModel/cheekPuff_R.obj': 'cd5b5d0f3a653a1fa31abeb65daf8fd6ffdf83a4d1bf22333a469b13b96fa801',
    'FaceXModel/mouthSmile_L.obj': '91794e73cef330f1c7d1f4541723544708536b39d5dd6ed35fd8f83f676b7af4',
    'FaceXModel/mouthSmile_R.obj': '3fb3de3da9f8358edbb933a65ce6e44c25a2501f30dcb240daea725b68adac84',
    'FaceXModel/mouthShrugUpper.obj': '2bd3e3f1568366f2fd84717f0f63aee9f56eed4c303fc4f234aadd81d430032c',
    'FaceXModel/mouthShrugLower.obj': '1eedd7831b0408bdcbc9aefe23b11803c54f81da5fc9be1fe81fc7a5117c0b88',
}
SHAPES = [Path(name).stem for name in FILES if name.endswith('.obj') and NEUTRAL not in name]


def fetch(cache: Path) -> None:
    """Download any missing file into `cache` and verify every file's SHA-256."""
    cache.mkdir(parents=True, exist_ok=True)
    for name, digest in FILES.items():
        path = cache / Path(name).name
        if not path.exists():
            with urlopen(Request(RAW + name, headers={'User-Agent': 'RCEF-example/0.2'}), timeout=120) as response:
                path.write_bytes(response.read())
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit(f'{path}: SHA-256 differs from the pinned ICT-FaceKit file')


def read_obj(path: Path) -> tuple[list[tuple[float, float, float]], list[list[int]]]:
    positions, faces = [], []
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('v '):
            x, y, z = line.split()[1:4]
            positions.append((float(x), float(y), float(z)))
        elif line.startswith('f '):
            faces.append([int(corner.split('/')[0]) - 1 for corner in line.split()[1:]])
    return positions, faces


def triangles(faces: list[list[int]]) -> list[int]:
    """Fan-triangulate each polygon; ICT faces are triangles and convex quads."""
    out = []
    for face in faces:
        for k in range(1, len(face) - 1):
            out += [face[0], face[k], face[k + 1]]
    return out


def build_glb(cache: Path) -> tuple[bytes, list[str], list[int]]:
    """A one-mesh GLB: the neutral positions, triangle indices and one morph target per shape.

    Each target stores the shape's positions minus the neutral positions, so a
    weight of 1 reproduces the ICT shape. Returns the GLB bytes, the target
    names in order and the triangle indices.
    """
    neutral, faces = read_obj(cache / f'{NEUTRAL}.obj')
    indices = triangles(faces)
    blobs, views, accessors = [], [], []

    def add(data: bytes, accessor: dict, target: int | None) -> int:
        offset = sum(len(b) for b in blobs)
        blobs.append(data + b'\0' * (-len(data) % 4))
        views.append({'buffer': 0, 'byteOffset': offset, 'byteLength': len(data),
                      **({'target': target} if target else {})})
        accessors.append({'bufferView': len(views) - 1, **accessor})
        return len(accessors) - 1

    def vec3(points):
        flat = [c for p in points for c in p]
        data = struct.pack(f'<{len(flat)}f', *flat)
        floats = struct.unpack(f'<{len(flat)}f', data)  # bounds of the stored float32 values
        return data, [min(floats[k::3]) for k in range(3)], [max(floats[k::3]) for k in range(3)]

    data, low, high = vec3(neutral)
    position = add(data, {'componentType': 5126, 'count': len(neutral), 'type': 'VEC3', 'min': low, 'max': high}, 34962)
    index = add(struct.pack(f'<{len(indices)}I', *indices),
                {'componentType': 5125, 'count': len(indices), 'type': 'SCALAR'}, 34963)
    targets = []
    for name in SHAPES:
        shape, shape_faces = read_obj(cache / f'{name}.obj')
        if len(shape) != len(neutral) or shape_faces != faces:
            raise SystemExit(f'{name}.obj does not share the neutral topology')
        delta = [(s[0] - n[0], s[1] - n[1], s[2] - n[2]) for s, n in zip(shape, neutral)]
        data, low, high = vec3(delta)
        targets.append({'POSITION': add(data, {'componentType': 5126, 'count': len(delta), 'type': 'VEC3',
                                                'min': low, 'max': high}, 34962)})
    binary = b''.join(blobs)
    document = {
        'asset': {'version': '2.0', 'generator': 'RCEF examples/ict_facekit.py',
                  'copyright': 'ICT-FaceKit (c) 2020 USC Institute for Creative Technologies, MIT license'},
        'scene': 0, 'scenes': [{'nodes': [0]}],
        'nodes': [{'mesh': 0, 'name': 'ICT-FaceKit'}],
        'meshes': [{'name': 'ICT-FaceKit', 'primitives': [{'attributes': {'POSITION': position}, 'indices': index,
                                                           'targets': targets}],
                    'weights': [0.0] * len(targets), 'extras': {'targetNames': SHAPES}}],
        'buffers': [{'byteLength': len(binary)}], 'bufferViews': views, 'accessors': accessors,
    }
    text = json.dumps(document, separators=(',', ':')).encode('utf-8')
    text += b' ' * (-len(text) % 4)
    glb = (struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(text) + 8 + len(binary))
           + struct.pack('<II', len(text), 0x4E4F534A) + text
           + struct.pack('<II', len(binary), 0x004E4942) + binary)
    return glb, SHAPES, indices
