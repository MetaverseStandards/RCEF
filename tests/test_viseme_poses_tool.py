# SPDX-License-Identifier: MIT
"""The pure parts of the viseme pose tool: the rig sets, the bounded and minimax fits, the held-out conditions, the
clamped sum and the cells."""
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

    def test_a_warm_start_reaches_the_same_weights(self):
        a, b = [1.0, 0.0, 1.0], [0.0, 1.0, 1.0]
        target = [0.3 * x + 0.6 * y for x, y in zip(a, b)]
        g, rhs = vp.gram([a, b]), [vp.dot(a, target), vp.dot(b, target)]
        warm = vp.bounded_least_squares(g, rhs, start=[1.0, 0.0])
        self.assertAlmostEqual(warm[0], 0.3, places=10)
        self.assertAlmostEqual(warm[1], 0.6, places=10)

    def test_minimax_balances_the_largest_relative_error(self):
        # One shape [1, 0]; rig 1 wants it at 1, rig 2 at 0.5. Errors |u - 1| and |u - 0.5| / 0.5 are equal, 1/3,
        # at u = 2/3; the sum of their squares is smallest at u = 0.6.
        g = [[1.0]]
        systems = [(g, [1.0], 1.0), (g, [0.5], 0.25)]
        [u] = vp.minimax(systems)
        self.assertAlmostEqual(u, 2 / 3, places=3)
        self.assertAlmostEqual(vp.error([u], *systems[0]), vp.error([u], *systems[1]), places=3)
        self.assertEqual(vp.minimax(systems, iterations=1), [0.6])

    def test_minimax_leaves_out_rigs_whose_target_does_not_move(self):
        self.assertEqual(vp.minimax([([[1.0]], [0.0], 0.0)]), [0.0])
        self.assertEqual(vp.minimax([([[1.0]], [0.0], 0.0), ([[1.0]], [0.5], 0.25)]), [0.5])

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


class RigSets(unittest.TestCase):
    def test_the_rig_sets_of_every_round_follow_their_rule(self):
        rounds = [(r['training'], r['held_out']) for r in vp.SETS['rounds']]
        self.assertEqual(vp.chosen(vp.SETS), rounds)
        self.assertEqual([len(t) for t, _ in rounds], [10, 10, 18])
        self.assertEqual((vp.TRAINING, vp.HELD_OUT_RIGS), rounds[-1])
        for training, held in rounds:
            self.assertFalse(set(training) & set(held))
            self.assertEqual(sorted(a.split('_')[0] for a in held), ['Female', 'Female', 'Male', 'Male'])

    def test_no_rig_is_ever_held_out_twice(self):
        held = [a for r in vp.SETS['rounds'] for a in r['held_out']]
        self.assertEqual(len(held), len(set(held)))
        self.assertEqual(sorted(vp.TRAINING), sorted(vp.SETS['rounds'][0]['training'] + held[:8]))

    def test_a_replaced_rig_gives_its_place_to_the_next_unused_candidate(self):
        sets = json.loads(json.dumps(vp.SETS))
        first = vp.HELD_OUT_RIGS[0]
        sets['replaced'] = [{'name': first, 'reason': 'synthetic'}]
        rounds = vp.chosen(sets)
        training, held = rounds[-1]
        self.assertNotIn(first, held + training)
        self.assertEqual(held[1:], vp.HELD_OUT_RIGS[1:])
        self.assertEqual(rounds[:2], vp.chosen(vp.SETS)[:2])
        self.assertEqual(held[0].split('_')[0], first.split('_')[0])

    def test_every_rig_file_is_pinned(self):
        text = (ROOT / 'examples/rigs.py').read_text(encoding='utf-8')
        for avatar in vp.TRAINING + vp.HELD_OUT_RIGS:
            self.assertIn(f"'{avatar}': '", text)


class Gate(unittest.TestCase):
    def test_feature_errors(self):
        self.assertEqual(vp.feature_error('difference', None, 1.5, 1.0), 0.5)
        self.assertEqual(vp.feature_error('range', (-2.0, 0.5), 0.2, 9.0), 0.0)
        self.assertAlmostEqual(vp.feature_error('range', (-2.0, 0.5), 0.75, 0.0), 0.25)
        self.assertAlmostEqual(vp.feature_error('range', (-2.0, 0.5), -2.5, 0.0), 0.5)

    def test_the_gated_classes_and_their_features(self):
        self.assertEqual(sorted(c.rsplit('.', 1)[1] for c in vp.FEATURES),
                         ['alveolar_sibilant', 'bilabial', 'vowel_close_rounded', 'vowel_mid_spread'])
        for spec in vp.FEATURES.values():
            self.assertLessEqual(len(spec), 3)
            for feature, kind, span in spec:
                self.assertIn(feature, vp.UNITS)
                self.assertIn(feature, vp.DESCRIPTIONS)
                self.assertEqual(span is None, kind == 'difference')
        self.assertEqual(vp.FEATURES[vp.V + 'bilabial'][0], ('lip_opening_mm', 'range', (-2.0, 0.5)))

    def test_tolerances_are_the_spread_of_the_rigs_own_features_with_a_floor(self):
        class Fake:
            def __init__(self, opening, width):
                self.values = {'lip_opening_mm': opening, 'corner_width_ratio': width}

            def target(self, meta):
                return self.values
        spec = [('lip_opening_mm', 'difference', None), ('corner_width_ratio', 'difference', None)]
        mouths = {n: Fake(o, w) for n, (o, w) in enumerate([(4.0, 0.9), (5.0, 0.905), (7.2, 0.91)])}
        self.assertEqual(vp.tolerances(mouths, 'E', spec), {'lip_opening_mm': 2.2, 'corner_width_ratio': 0.02})
        self.assertEqual(vp.tolerances(mouths, 'E', [vp.GUARD]), {'whole_face_error': 0.0})


class Tied(unittest.TestCase):
    def test_left_and_right_columns_are_summed_into_one(self):
        class Fake:
            basis = [[1.0, 0.0], [0.0, 2.0], [3.0, 3.0]]
        keys, columns = vp.tied(Fake, ['mouthSmileLeft', 'mouthSmileRight', 'jawOpen'])
        self.assertEqual(keys, ['mouthSmile', 'jawOpen'])
        self.assertEqual(columns, [[1.0, 2.0], [3.0, 3.0]])


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
