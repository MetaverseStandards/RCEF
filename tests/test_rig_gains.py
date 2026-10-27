# SPDX-License-Identifier: MIT
"""Rig intensity normalisation (examples/rig_gains.py): its pieces, its landmarks and, once frozen, its record."""
import ast
from fractions import Fraction
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import ict_facekit  # noqa: E402
import rig_gains  # noqa: E402
import rigs  # noqa: E402

LANDMARKS = json.loads((ROOT / 'examples/data/rig_landmarks.json').read_text(encoding='utf-8'))
MULTI_PIE = [1225, 1888, 1052, 367, 1719, 1722, 2199, 1447, 966, 3661, 4390, 3927, 3924, 2608, 3272, 4088, 3443, 268,
             493, 1914, 2044, 1401, 3615, 4240, 4114, 2734, 2509, 978, 4527, 4942, 4857, 1140, 2075, 1147, 4269, 3360,
             1507, 1542, 1537, 1528, 1518, 1511, 3742, 3751, 3756, 3721, 3725, 3732, 5708, 5695, 2081, 0, 4275, 6200,
             6213, 6346, 6461, 5518, 5957, 5841, 5702, 5711, 5533, 6216, 6207, 6470, 5517, 5966]  # ICT README


def png(rows, filters):
    """An 8-bit RGBA PNG of `rows` (lists of (r, g, b, a)), each row filtered with the given PNG filter type."""
    raw, prev = b'', bytes(4 * len(rows[0]))
    for row, kind in zip(rows, filters):
        line = bytes(c for px in row for c in px)
        out = bytearray()
        for x in range(len(line)):
            a = line[x - 4] if x >= 4 else 0
            b, c = prev[x], prev[x - 4] if x >= 4 else 0
            p = a + b - c
            pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
            predictor = [0, a, b, (a + b) // 2, a if pa <= pb and pa <= pc else b if pb <= pc else c][kind]
            out.append((line[x] - predictor) & 255)
        raw += bytes([kind]) + bytes(out)
        prev = line

    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))
    header = struct.pack('>IIBBBBB', len(rows[0]), len(rows), 8, 6, 0, 0, 0)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')


class Pieces(unittest.TestCase):
    def test_every_ict_expression_maps_to_one_arkit_channel(self):
        found = rig_gains.channels()
        self.assertEqual(len(found), 51)  # the 52 ARKit shapes but tongueOut, which ICT does not have
        self.assertNotIn('tongueOut', found)
        self.assertEqual(found['browInnerUp'], ['browInnerUp_L', 'browInnerUp_R'])
        self.assertEqual(found['eyeBlinkLeft'], ['eyeBlink_L'])
        self.assertEqual(sorted(s for v in found.values() for s in v), sorted(ict_facekit.EXPRESSIONS))

    def test_regions_and_sides(self):
        self.assertEqual(rig_gains.region('eyeLookUpLeft'), 'gaze')
        self.assertEqual(rig_gains.region('eyeBlinkLeft'), 'eyes')
        self.assertEqual(rig_gains.region('mouthClose'), 'mouth')
        self.assertEqual(rig_gains.side('jawOpen'), 'none')
        self.assertEqual(rig_gains.side('noseSneerRight'), 'right')

    def test_the_png_reader_undoes_every_filter(self):
        rows = [[((x * 37 + y * 11) % 256, (x * y) % 256, (200 - 3 * x) % 256, 255) for x in range(7)] for y in range(5)]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'f.png'
            path.write_bytes(png(rows, [0, 1, 2, 3, 4]))
            w, h, bpp, out = rig_gains.read_png(str(path))
        self.assertEqual((w, h, bpp), (7, 5, 4))
        self.assertEqual([list(r) for r in out], [[c for px in row for c in px] for row in rows])

    def test_marker_centroid_and_weight(self):
        rows = [[(0, 0, 0, 255)] * 9 for _ in range(9)]
        rows[4][6] = (200, 0, 0, 255)
        rows[5][6] = (100, 0, 0, 255)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'm.png'
            path.write_bytes(png(rows, [4] * 9))
            found = rig_gains.measure((str(path), [('m', 0, 5.0, 5.0, 3.0), ('g', 1, 5.0, 5.0, 3.0)]))
        x, y, weight = found['m']
        self.assertEqual(weight, 300)
        self.assertAlmostEqual(x, 6.5)
        self.assertAlmostEqual(y, (200 * 4.5 + 100 * 5.5) / 300)
        self.assertEqual(found['g'][2], 0)

    def test_pool_adjacent_violators(self):
        for values, expected in (([0.2, 0.5, 0.4, 0.9], [0.2, 0.45, 0.45, 0.9]), ([0.3, 0.2, 0.1], [0.2, 0.2, 0.2]),
                                 ([0.1, 0.2], [0.1, 0.2])):
            for got, want in zip(rig_gains.pava(values), expected, strict=True):
                self.assertAlmostEqual(got, want)

    def test_best_weight_interpolates_between_grid_renders(self):
        grid = {u: {'a': (0.02 * u, 0.0), 'b': (0.0, -0.01 * u)} for u in rig_gains.GRID}
        u, residual = rig_gains.best_weight({'a': (0.0062, 0.0), 'b': (0.0, -0.0031)}, grid)
        self.assertAlmostEqual(u, 0.31)
        self.assertAlmostEqual(residual, 0.0)
        u, _ = rig_gains.best_weight({'a': (0.05, 0.0), 'b': (0.0, -0.025)}, grid)
        self.assertEqual(u, 1.0)  # beyond Rocketbox's reach: held at 1, which analyse() reports as a failure
        u, _ = rig_gains.best_weight({'a': (-0.01, 0.0), 'b': (0.0, 0.01)}, grid)
        self.assertEqual(u, 0.0)

    def test_conditions_are_derived_deterministically_within_their_ranges(self):
        a = rig_gains.camera_params('rcef.k3.heldout:123:jawOpen', with_weight=True)
        self.assertEqual(a, rig_gains.camera_params('rcef.k3.heldout:123:jawOpen', with_weight=True))
        self.assertNotEqual(a, rig_gains.camera_params('rcef.k3.heldout:124:jawOpen', with_weight=True))
        self.assertTrue(-rig_gains.YAW <= a['yaw'] <= rig_gains.YAW)
        self.assertTrue(rig_gains.HELD_OUT_WEIGHTS[0] <= a['weight'] <= rig_gains.HELD_OUT_WEIGHTS[1])
        deviates = [rig_gains.normal_deviate(f'rcef.k3.identity:0:{i}') for i in range(200)]
        self.assertLess(abs(sum(deviates) / 200), 0.25)

    def test_the_float_curve_matches_the_exact_fraction_oracle(self):
        knots = [[0.0, 0.0], [0.25, 0.164103], [0.5, 0.321478], [0.75, 0.48384], [1.0, 0.659608]]
        for k in range(-20, 241):
            x = k / 200 + 1e-7 * (k % 3)
            exact = rig_gains.curve_value(knots, x)
            self.assertLessEqual(abs(Fraction(rigs.piecewise_linear(knots, x)) - exact), Fraction(1, 2 ** 52))
        self.assertEqual(rig_gains.curve_value(knots, 2.0), Fraction(0.659608))
        self.assertEqual(rig_gains.curve_value(knots, -1.0), 0)


class Landmarks(unittest.TestCase):
    def test_regions_use_defined_landmarks_on_both_rigs(self):
        marks = LANDMARKS['landmarks']
        for name, members in LANDMARKS['regions'].items():
            for m in members:
                self.assertIn(m, marks, name)
        for m, v in marks.items():
            self.assertEqual(sorted(v), ['ict', 'provenance', 'rocketbox_female'], m)
            self.assertEqual(sorted(v['provenance']), ['ict', 'rocketbox_female'], m)
        self.assertEqual(set(rig_gains.region(a) for a in rig_gains.channels()), set(LANDMARKS['regions']))

    def test_ict_multi_pie_landmarks_are_the_readme_indices(self):
        marks = LANDMARKS['landmarks']
        for name, v in marks.items():
            text = v['provenance']['ict']
            if text.startswith('Multi-PIE 68 #'):
                number = int(text.split('#')[1].split()[0])
                self.assertEqual(v['ict'], MULTI_PIE[number], name)

    def test_left_and_right_landmarks_are_mirrored_by_name(self):
        marks = LANDMARKS['landmarks']
        for name in marks:
            if name.endswith('_R'):
                self.assertIn(name[:-1] + 'L', marks)


class ReservedRig(unittest.TestCase):
    def test_the_fit_never_loads_rocketbox_male(self):
        source = (ROOT / 'examples/rig_gains.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and getattr(node.func, 'attr', None) == 'load_rocketbox']
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].args[1].value, 'Female')
        self.assertNotIn("'Male'", source)
        self.assertNotIn('rocketbox-male', source)
        self.assertNotIn('Male_Adult', json.dumps(LANDMARKS))


if __name__ == '__main__':
    unittest.main()
