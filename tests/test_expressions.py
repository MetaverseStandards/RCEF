# SPDX-License-Identifier: MIT
"""The example expression library and the frames generated from it."""
import csv
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import make_demo_frames  # noqa: E402
import make_expression_frames as gen  # noqa: E402

FB2 = list(make_demo_frames.FB2_CHANNELS)
VISEMES = list(make_demo_frames.VISEME_CHANNELS)


def read(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


class Library(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library = gen.library()

    def test_eighteen_expressions_and_a_four_way_gaze_sweep(self):
        names = [e['name'] for e in self.library['expressions']]
        self.assertEqual(len(names), 22)
        self.assertEqual(names[-4:], ['look left', 'look right', 'look up', 'look down'])
        self.assertEqual(len(set(names)), len(names))

    def test_every_expression_cites_a_source_and_flags_chosen_weights(self):
        for expression in self.library['expressions']:
            with self.subTest(expression['name']):
                self.assertTrue(expression['sources'])
                for source in expression['sources']:
                    self.assertIn(source.split(':')[0], self.library['sources'])
                if any(not isinstance(v, str) for v in expression['aus'].values()):
                    self.assertTrue(expression.get('assumptions'), 'a weight not from a FACS letter needs a reason')

    def test_aus_resolve_to_existing_fb2_channels(self):
        for expression in self.library['expressions']:
            with self.subTest(expression['name']):
                weights = gen.fb2_weights(expression, self.library, FB2)
                self.assertTrue(weights)
                self.assertLessEqual(set(weights), set(FB2))
                self.assertTrue(all(0 < w <= 1 for w in weights.values()))

    def test_examples_of_the_correspondence(self):
        by_name = {e['name']: e for e in self.library['expressions']}
        self.assertEqual(gen.fb2_weights(by_name['happiness'], self.library, FB2),
                         {'CHEEK_RAISER_L': 0.6, 'CHEEK_RAISER_R': 0.6,
                          'LIP_CORNER_PULLER_L': 0.6, 'LIP_CORNER_PULLER_R': 0.6})
        self.assertEqual(gen.fb2_weights(by_name['contempt'], self.library, FB2),
                         {'LIP_CORNER_PULLER_R': 0.2, 'DIMPLER_R': 0.2})
        self.assertEqual(gen.fb2_weights(by_name['jaw sideways left'], self.library, FB2), {'JAW_SIDEWAYS_LEFT': 0.6})
        pucker = gen.fb2_weights(by_name['pucker'], self.library, FB2)
        self.assertEqual({k for k in pucker if k.startswith('LIP_FUNNELER')},
                         {'LIP_FUNNELER_LB', 'LIP_FUNNELER_LT', 'LIP_FUNNELER_RB', 'LIP_FUNNELER_RT'})
        self.assertEqual(gen.missing_aus(by_name['surprise'], self.library), ['AU 25 (lips part): no FB2 channel'])


class Frames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library = gen.library()
        cls.fb2 = read(ROOT / 'examples/data/fb2_expression_frames.csv')
        cls.talk = read(ROOT / 'examples/data/viseme_talk_frames.csv')

    def test_committed_frames_match_the_generator(self):
        with tempfile.TemporaryDirectory(prefix='rcef-expr-') as tmp:
            gen.write_all(Path(tmp))
            for name in ('fb2_expression_frames.csv', 'viseme_talk_frames.csv'):
                self.assertEqual((Path(tmp) / name).read_bytes(), (ROOT / 'examples/data' / name).read_bytes(), name)

    def test_each_expression_ramps_in_holds_and_ramps_out(self):
        for expression in self.library['expressions']:
            with self.subTest(expression['name']):
                rows = [r for r in self.fb2 if r['segment'] == expression['name']]
                self.assertEqual([r['phase'] for r in rows],
                                 ['in'] * gen.RAMP + ['hold'] * gen.HOLD + ['out'] * gen.RAMP)
                weights = gen.fb2_weights(expression, self.library, FB2)
                for row in rows:
                    amount = float(row['amount'])
                    self.assertEqual({c: float(row[c]) for c in FB2 if float(row[c])},
                                     {c: w * amount for c, w in weights.items()})
                self.assertEqual(float(rows[gen.RAMP]['amount']), 1.0)

    def test_frames_are_valid_and_never_set_opposing_gaze_together(self):
        for row in self.fb2:
            self.assertEqual((row['isValid'], row['isEyeFollowingBlendshapesValid']), ('1', '1'))
            for side in 'LR':
                for a, b in (('LEFT', 'RIGHT'), ('UP', 'DOWN')):
                    self.assertFalse(float(row[f'EYES_LOOK_{a}_{side}']) and float(row[f'EYES_LOOK_{b}_{side}']))

    def test_missing_aus_are_noted_on_their_frames(self):
        for row in self.fb2:
            if row['segment'] in ('surprise', 'happily surprised') and row['phase']:
                self.assertEqual(row['note'], 'AU 25 (lips part): no FB2 channel')

    def test_talking_frames_sum_to_one_and_hold_each_viseme(self):
        self.assertEqual({r['segment'] for r in self.talk}, {'', 'bed', 'car', 'toe', 'book'})
        for row in self.talk:
            self.assertEqual(sum(float(row[v]) for v in VISEMES), 1.0)
            self.assertEqual(row['isValid'], '1')
        held = [r['viseme'] for r in self.talk if r['phase'] == 'hold']
        sequence = [v for _, v in self.library['talk']['sequence']]
        self.assertEqual(held[::gen.TALK_HOLD], sequence)
        self.assertEqual(len(held), gen.TALK_HOLD * len(sequence))


if __name__ == '__main__':
    unittest.main()
