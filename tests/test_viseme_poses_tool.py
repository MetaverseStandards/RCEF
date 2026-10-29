# SPDX-License-Identifier: MIT
"""The pure parts of the viseme pose tool: the bounded fit, the held-out conditions, the clamped sum and the cells."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/calibration'))
import viseme_poses as vp  # noqa: E402


def least_squares(columns, target):
    g = vp.gram(columns)
    return vp.bounded_least_squares(g, [vp.dot(c, target) for c in columns])


class Fit(unittest.TestCase):
    def test_an_interior_combination_is_recovered(self):
        a, b = [1.0, 0.0, 1.0], [0.0, 1.0, 1.0]
        u = least_squares([a, b], [0.3 * x + 0.6 * y for x, y in zip(a, b)])
        self.assertAlmostEqual(u[0], 0.3, places=10)
        self.assertAlmostEqual(u[1], 0.6, places=10)

    def test_weights_are_clipped_to_zero_and_one(self):
        a, b = [1.0, 0.0], [0.0, 1.0]
        self.assertEqual(least_squares([a, b], [2.0, -1.0]), [1.0, 0.0])

    def test_a_clipped_weight_lets_the_others_take_up_the_rest(self):
        # Unbounded, the best fit is -0.5 a + b; bounded, a is 0 and b alone gives its projection, 0.7.
        a, b = [1.0, 1.0], [1.0, 2.0]
        u = least_squares([a, b], [0.5, 1.5])
        self.assertEqual(u[0], 0.0)
        self.assertAlmostEqual(u[1], 0.7, places=10)

    def test_left_and_right_share_one_weight(self):
        self.assertEqual(vp.pair('mouthSmileLeft'), 'mouthSmile')
        self.assertEqual(vp.pair('mouthSmileRight'), 'mouthSmile')
        self.assertEqual(vp.pair('jawOpen'), 'jawOpen')


class HeldOut(unittest.TestCase):
    seeds = list(range(1000, 1024))

    def test_conditions_are_the_class_at_a_seeded_weight_and_half_blend_with_rest(self):
        channel = 'rcef.canonical_viseme.bilabial'
        frames = vp.conditions(self.seeds, channel)
        self.assertEqual(frames, vp.conditions(self.seeds, channel))
        self.assertEqual(len(frames), 24)
        for frame in frames:
            self.assertTrue(0.2 <= frame[channel] <= 1.0)
            self.assertLessEqual(set(frame), {channel, vp.REST})
            self.assertAlmostEqual(sum(frame.values()), 1.0 if vp.REST in frame else frame[channel], places=6)
        self.assertTrue(4 <= sum(vp.REST in f for f in frames) <= 20)
        self.assertNotEqual(frames, vp.conditions(self.seeds, 'rcef.canonical_viseme.dental'))
        self.assertTrue(all(set(f) == {vp.REST} for f in vp.conditions(self.seeds, vp.REST)))

    def test_the_bridge_is_a_clamped_sum_of_poses(self):
        poses = {'a': {'x': 0.5, 'y': 0.0}, 'b': {'x': 0.75, 'y': 0.25}}
        self.assertEqual(vp.bridge(poses, {'a': 0.5, 'b': 0.5}), {'x': 0.625, 'y': 0.125})
        self.assertEqual(vp.bridge(poses, {'a': 1.0, 'b': 1.0}), {'x': 1.0, 'y': 0.25})

    def test_the_error_is_a_ratio_and_motion_without_a_target_is_a_failure(self):
        self.assertEqual(vp.ratio(1.0, 4.0), (0.5, False))
        self.assertEqual(vp.ratio(0.0, 0.0), (0.0, False))
        self.assertEqual(vp.ratio(1e-9, 0.0), (1.0, True))
        self.assertEqual(vp.ratio(-1e-18, 4.0), (0.0, False))

    def test_cells_use_the_median_and_the_nearest_rank_p95(self):
        errors = [i / 100 for i in range(1, 25)]
        result = vp.cell(errors, 1, 0.0)
        self.assertEqual((result['failures'], result['median'], result['p95']), (1, 0.125, 0.23))


class Pack(unittest.TestCase):
    def test_the_fit_reads_15_classes_and_37_arkit_shapes_through_copies(self):
        document = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        classes, arkit, signals = vp.correspondences(document)
        self.assertEqual(len(classes), 15)
        self.assertNotIn('rcef.canonical_viseme.alveolar_floor', classes.values())
        self.assertEqual(len(arkit), 37)
        self.assertEqual(len({vp.pair(a) for a in arkit}), 24)
        self.assertEqual(len(signals), 45)
        self.assertFalse({'tongueOut', 'jawLeft', 'mouthLeft', 'eyeBlinkLeft', 'eyeLookInLeft'} & set(arkit))


if __name__ == '__main__':
    unittest.main()
