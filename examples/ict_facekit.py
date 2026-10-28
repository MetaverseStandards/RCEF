# SPDX-License-Identifier: MIT
"""Fetch the ICT-FaceKit Light face model and convert part of it to a glTF binary.

ICT-FaceKit (USC Institute for Creative Technologies, MIT license) ships a
neutral head and ARKit-named expression shapes as OBJ files, with browInnerUp
and cheekPuff split into left and right halves. The files are fetched into a
cache outside the repository and checked against the SHA-256 values below;
they are never committed.

Only the shapes the RCEF FB2 -> ARKit mappings can drive are converted. All 53
expression shapes plus the neutral would need about 4.3 million position
components, more than msf-character-tools' 4 million decoded-component budget,
and sparse accessors do not help because msf-character-tools counts them at full
size.
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
# All 53 expression shapes and the first ten identity modes, for the rig-gain fit (rig_gains.py). The identity
# modes are principal components of light-stage scans of real people; they are used only as geometry.
CALIBRATION_FILES = {
    'LICENSE': FILES['LICENSE'],
    f'FaceXModel/{NEUTRAL}.obj': FILES[f'FaceXModel/{NEUTRAL}.obj'],
    'FaceXModel/browDown_L.obj': 'd1dcd14fc085a9e258dec62a4bfe4a31d592cce5d8918a3892c20f480653f4c1',
    'FaceXModel/browDown_R.obj': '66a2c72ab64999af168795f27182d011f52b90958c402d719d3ec8ff7d1c8939',
    'FaceXModel/browInnerUp_L.obj': '81fb1625794ea36fb13303234ce06cef798acfdbc489077e22ae195a705bc92e',
    'FaceXModel/browInnerUp_R.obj': '5e66b46cdad89fd1237273db2b885511688cf37636cedfdde432a4844c9109e7',
    'FaceXModel/browOuterUp_L.obj': '022d5342687e51351f4cad6dd1abd42c3bb1b752d0b235bdc7fc588ab0d79c90',
    'FaceXModel/browOuterUp_R.obj': '1e4722060538b274ed49ed872525d770b5bfd9262b7bce1b6310f49356f5b531',
    'FaceXModel/cheekPuff_L.obj': 'f53fd2bdeb8e26d0db8a684ab9c095c6bb113b74575dec329facae2799ff18c6',
    'FaceXModel/cheekPuff_R.obj': 'cd5b5d0f3a653a1fa31abeb65daf8fd6ffdf83a4d1bf22333a469b13b96fa801',
    'FaceXModel/cheekSquint_L.obj': '572fe87f2e0cdd0a7ff868b9173d0ff08ee2bc73bf94c17b603f6e5d5b8fbe26',
    'FaceXModel/cheekSquint_R.obj': 'a9afa0aac432159e89eb54dbbb3139864b8cc1c4208c3c0e9c420d0d8050b99a',
    'FaceXModel/eyeBlink_L.obj': 'f5ed1c3072a400083b7d4f7f5cb3d73882b7ebb95c3232f957394db8cf7fe19e',
    'FaceXModel/eyeBlink_R.obj': 'd281ad0af03e89a70abf1214d52c295b3a279c9b35f6795938c4487f467ca003',
    'FaceXModel/eyeLookDown_L.obj': 'e7da4fa6509af5da25fab1a34255889a68f06b90fd37f65c6c05e5bdbbe2f755',
    'FaceXModel/eyeLookDown_R.obj': 'ac466de6decf619701f3ee7f80fa7371020d325084b41ad7f4b2840e232abf83',
    'FaceXModel/eyeLookIn_L.obj': '1e037332bc059a95d05fcb24728ae297a2d4d268ff0cf623d3647d2a4f86bd31',
    'FaceXModel/eyeLookIn_R.obj': '3d64db0e51ad28e76eff56217da401c5ee563b5e76a207cb192046465bbab14a',
    'FaceXModel/eyeLookOut_L.obj': '235739695136c40b7a2c3239a100ff75b7bfc271ae195aeb55330848c999c9c8',
    'FaceXModel/eyeLookOut_R.obj': 'ac10dfa83ccaca7fd76fe96d74f8cbc80582e2ef914d1092827b54f88125650e',
    'FaceXModel/eyeLookUp_L.obj': '72ed342df43489a76e9d468df3ca7f48328f41c924af0c03d88fde9905d82848',
    'FaceXModel/eyeLookUp_R.obj': 'd8ade1cab9f7f0c4ef6ec007f33e9c9df90a58c666b9aac5a784192cd389e899',
    'FaceXModel/eyeSquint_L.obj': 'ecb8244f083cf55fa9f0277427b8213315176a624d9ac3a09b533c7fbc68917e',
    'FaceXModel/eyeSquint_R.obj': '0dffbbc651b9cdbc346ead32ba102051200c72ed8a93e7b33f07149e18390b8a',
    'FaceXModel/eyeWide_L.obj': '015a995b0f09783683f5575af7e4c939cd758d194d7ca2e8ffacb9ddbabf0078',
    'FaceXModel/eyeWide_R.obj': '4b8207f6013a751ae35affba62cc70bd6b53e046bbe48e8fd5a150450a7789ed',
    'FaceXModel/jawForward.obj': 'a0126b2926b69540f478e4c48f05e370868050e6c33718e53c2f17e190a3b239',
    'FaceXModel/jawLeft.obj': '5af90cd941660fb0116948866414e4321035de754b7ebec787f8144445d2d9e9',
    'FaceXModel/jawOpen.obj': '8d84355e10f48b05550980cee385bcd426f4797090da76a20de0535bb2f99f4a',
    'FaceXModel/jawRight.obj': 'd719335ad69a8f18797501d4728910c7a467aecbbae260923192b1bf242eec97',
    'FaceXModel/mouthClose.obj': '4a44b94c269407cf1171483d87d99d2cbdea9c66242aabf2ad0f57cb785aa193',
    'FaceXModel/mouthDimple_L.obj': '189f6e01adbf1e13147fe4d505d1f3006e5ce4590ae150064b810274093d29b0',
    'FaceXModel/mouthDimple_R.obj': '4cf674b98d6d34a16fab462fbd9ecb2cb5e39ccaf3f50459b9ac7d59fbd6a215',
    'FaceXModel/mouthFrown_L.obj': '1bfd720ad024e5805ac8472df170c2c96c09e817e02b66f916057d6e2d31ee9b',
    'FaceXModel/mouthFrown_R.obj': 'ae3da92fa1dc70010c6bec810338d740287c71b8730694c97876cab5af241f74',
    'FaceXModel/mouthFunnel.obj': 'd4f1dba04c1af5fc37452c88cc54a72f1133296c26d9abe0f8adb74dc5c2577f',
    'FaceXModel/mouthLeft.obj': '01fb69aa8ac07c5762719c9bb2eec5372652c9f1e73509a63d01e7e60e28b885',
    'FaceXModel/mouthLowerDown_L.obj': '8847660d51e2a72f2bce6ce9add7d58abab1cef967420db83056891291c0b2de',
    'FaceXModel/mouthLowerDown_R.obj': 'b5143ed50d41c91d80ddc8b565f6274eaf514509ec6f895797db34ca92a85b68',
    'FaceXModel/mouthPress_L.obj': 'de2bdaf2fa7199294ff7a281cd8f6647bf5ca9a6f84588bd7f7779fff4c61396',
    'FaceXModel/mouthPress_R.obj': 'ca8d9973b3231e51b8b76d3e7af7f7f3432959b7c37148fc25e7c643252847b6',
    'FaceXModel/mouthPucker.obj': '9929c31025667683809f70df7dce612f72e3acfc7f9e8acb939f6636509dbc5c',
    'FaceXModel/mouthRight.obj': 'e3faaf5ed51715e77122d76e8187d5ba83ea9f54e15e29c52e64f26c52e66bda',
    'FaceXModel/mouthRollLower.obj': '1f577e1129eef4f9e9dc26aa739c6d0f15b27253dee89af3428db6816666e910',
    'FaceXModel/mouthRollUpper.obj': 'a69ec7407adfd6a5f4c818179bb4604d9e506c07671976f75ac33ef8f54a1bb0',
    'FaceXModel/mouthShrugLower.obj': '1eedd7831b0408bdcbc9aefe23b11803c54f81da5fc9be1fe81fc7a5117c0b88',
    'FaceXModel/mouthShrugUpper.obj': '2bd3e3f1568366f2fd84717f0f63aee9f56eed4c303fc4f234aadd81d430032c',
    'FaceXModel/mouthSmile_L.obj': '91794e73cef330f1c7d1f4541723544708536b39d5dd6ed35fd8f83f676b7af4',
    'FaceXModel/mouthSmile_R.obj': '3fb3de3da9f8358edbb933a65ce6e44c25a2501f30dcb240daea725b68adac84',
    'FaceXModel/mouthStretch_L.obj': '9187105730bad43023c63e2a91c979091b9289dd8fc1b587885412b8f7a3d2b7',
    'FaceXModel/mouthStretch_R.obj': 'd985452085a19d6b3da397ca2cd2f938d8e08761d2e684e87640f3639bdf5f6d',
    'FaceXModel/mouthUpperUp_L.obj': 'd49483aca6cbbb7a559edf4865aec62970560ddf3a0d34e5b208488bff59f722',
    'FaceXModel/mouthUpperUp_R.obj': '299e3da0f36ca80c0c74e51900b67bfe6bb5b0101aaf46ce30075064c26a7f02',
    'FaceXModel/noseSneer_L.obj': '47c5d66ddc1ba146480f0e43b1084f439e0e7d2af31bcec3e6a3bffc420ffa4d',
    'FaceXModel/noseSneer_R.obj': 'c384c41331124b9cd4b99c1bbe8aef56318cae2b8db6ff0f573a7347ebbe8caa',
    'FaceXModel/identity000.obj': '918160cf82d541336b4c367cf93199c9827832bde02511b8fbdf9019d6f1a773',
    'FaceXModel/identity001.obj': '325115059deb6691cb2d55da07ae38bb08ce36e4ea146982f294a17513155b3b',
    'FaceXModel/identity002.obj': 'e140e8305cd5232def3b94331d08450a13f312e525130fca8eeaa653231decc3',
    'FaceXModel/identity003.obj': 'be3481a6bed8953a6d9dd7f811a04bc6d2ab94d1bd76ecfaa6d4cae87a450f9d',
    'FaceXModel/identity004.obj': 'a2f411cc763e881cff250eb23c04fe8375b63a05a7dfa0492422e3b943e8a01d',
    'FaceXModel/identity005.obj': '274178eb33e33c555e6024535a51a62ee50050abd4f7014bbc7a4dc90a638c65',
    'FaceXModel/identity006.obj': 'c9ae0426ab88b49065c852148f7bcff8cb09253fbee068b78955bd76c19a3e0f',
    'FaceXModel/identity007.obj': 'ba38037151277b94e2b6b9b9800275d92d2c0aa8d61057b0718c9d7b90fffc44',
    'FaceXModel/identity008.obj': 'b03543b783a15c1d28c5a384cd93657eda915227756780f682bc7370cd94ce1d',
    'FaceXModel/identity009.obj': '0cbb5ca5db9c61fa91df8d1c04b9b383b40d797032ca3f5a28a234d495e31b54',
}
EXPRESSIONS = [Path(n).stem for n in CALIBRATION_FILES if n.endswith('.obj') and 'identity' not in n and NEUTRAL not in n]
IDENTITY_MODES = [Path(n).stem for n in CALIBRATION_FILES if Path(n).stem.startswith('identity')]


def fetch(cache: Path, files: dict[str, str] = FILES) -> None:
    """Download any missing file into `cache` and verify every file's SHA-256."""
    cache.mkdir(parents=True, exist_ok=True)
    for name, digest in files.items():
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
