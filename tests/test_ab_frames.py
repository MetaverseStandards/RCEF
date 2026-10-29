# SPDX-License-Identifier: MIT
"""scripts/ab_frames.py: the A/B input families, their seeds and their value mix."""
import json
import math
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import ab_frames  # noqa: E402

FIXTURE = ROOT / 'tests/fixtures/baseline-dea1713.pack.json'


def registration(seed_root):
    document = json.loads(FIXTURE.read_text(encoding='utf-8'))
    sources = {p: ab_frames.pinned_source(document, p) for p in ('openxr.fb2', 'arkit.coefficient', 'openxr.visemes')}
    letters = [f'facs.code.au{n:02d}_{s}' for n in (1, 12) for s in ('left', 'right')] + ['facs.code.au17']
    return {'seed_root': seed_root, 'sources': sources,
            'families': [{'name': 'fb2_contract', 'kind': 'fb2_contract', 'source': 'openxr.fb2', 'count': 20},
                         {'name': 'arkit_uniform', 'kind': 'uniform', 'source': 'arkit.coefficient', 'count': 20},
                         {'name': 'viseme_simplex', 'kind': 'simplex', 'source': 'openxr.visemes', 'count': 10},
                         {'name': 'facs_letters', 'kind': 'facs_letters', 'count': 10, 'channels': letters}],
            'perturbations': [{'family': 'arkit_uniform', 'bases': 2}]}


class Families(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first, cls.second = registration('a' * 64), registration('b' * 64)

    def test_the_pinned_sources_come_from_the_baseline_pack(self):
        fb2 = self.first['sources']['openxr.fb2']
        self.assertEqual(len(fb2['channels']), 70)
        self.assertEqual(fb2['flags'], ['isEyeFollowingBlendshapesValid', 'isValid'])
        self.assertEqual(len(fb2['gaze_pairs']), 4)
        self.assertEqual(len(self.first['sources']['arkit.coefficient']['gaze_pairs']), 4)

    def test_fixed_families_do_not_depend_on_seed_root(self):
        self.assertEqual(ab_frames.fixed_families(self.first), ab_frames.fixed_families(self.second))

    def test_seeded_families_repeat_for_a_seed_root_and_change_with_it(self):
        first = ab_frames.seeded_families(self.first)
        self.assertEqual(first, ab_frames.seeded_families(registration('a' * 64)))
        second = ab_frames.seeded_families(self.second)
        self.assertTrue(all(first[name] != second[name] for name in first))

    def test_full_mantissa_values_fill_the_mantissa_and_stay_below_one(self):
        rng = random.Random(1)
        values = [ab_frames.full_mantissa(rng) for _ in range(4000)]
        self.assertTrue(all(0 <= v < 1 for v in values))
        self.assertGreater(sum(math.frexp(v)[0] * 2 ** 53 % 2 == 1 for v in values), 1800)
        self.assertLess(abs(sum(v < 0.5 for v in values) - 2000), 200)
        self.assertTrue(all(float(f'{v:.6f}') == v for v in (ab_frames.decimal6(rng) for _ in range(1000))))

    def test_seeded_families_mix_full_mantissa_and_six_decimal_values(self):
        values = [v for f in ab_frames.seeded_families(self.first)['arkit_uniform'] for v in f['values'].values()]
        decimal = [v for v in values if float(f'{v:.6f}') == v]
        self.assertTrue(0.3 < len(decimal) / len(values) < 0.7)

    def test_contract_frames_set_at_most_one_direction_of_each_gaze_pair(self):
        source = self.first['sources']['openxr.fb2']
        for frame in ab_frames.seeded_families(self.first)['fb2_contract']:
            for a, b in source['gaze_pairs']:
                self.assertFalse(frame['values'][a] and frame['values'][b])

    def test_letter_frames_are_library_keys_with_letter_values(self):
        for frame in ab_frames.seeded_families(self.first)['facs_letters']:
            self.assertLessEqual(set(frame['keys']), {'L1', 'R1', 'L12', 'R12', '17'})
            self.assertTrue(all(v in ab_frames.LETTER_VALUES[1:] for v in frame['keys'].values()))

    def test_perturbations_leave_out_raise_lower_and_clear(self):
        frames = ab_frames.seeded_families(self.first)['perturb:arkit_uniform']
        self.assertEqual(len(frames), 2 * 52 * 3)
        self.assertEqual(len(frames[0]['values']), 51)
        self.assertEqual(sorted(set(frames[1]['values'].values()) - set(frames[0]['values'].values())), [1.5])

    def test_the_edge_set_holds_the_gaze_pairs_and_near_subnormal_values(self):
        frames = ab_frames.edge_family('edge', self.first['sources']['arkit.coefficient'])
        self.assertEqual(len(frames), len(ab_frames.EDGE_VALUES) * 53 + 4 * 4)
        self.assertIn(5e-324, ab_frames.EDGE_VALUES)
        self.assertIn(math.copysign(0.0, -1), [math.copysign(0.0, v) for v in ab_frames.EDGE_VALUES if v == 0])

    def test_files_and_sums_are_written_with_every_bit(self):
        families = {'edge:x': [{'family': 'edge:x', 'label': 'z', 'values': {'a': -0.0, 'b': 5e-324}, 'flags': {}}]}
        with tempfile.TemporaryDirectory(prefix='rcef-ab-') as tmp:
            sums = ab_frames.write(families, Path(tmp))
            text = (Path(tmp) / 'frames/edge__x.jsonl').read_text(encoding='utf-8')
            self.assertIn('"a":-0.0', text)
            self.assertEqual(json.loads(text)['values']['b'], 5e-324)
            self.assertIn(sums['frames/edge__x.jsonl'], (Path(tmp) / 'SHA256SUMS').read_text(encoding='utf-8'))

    def test_facs_keys_use_the_library_notation(self):
        self.assertEqual([ab_frames.facs_key(s) for s in ('facs.code.au01_left', 'facs.code.au17',
                                                           'facs.code.au30_right')], ['L1', '17', 'R30'])
        frames = ab_frames.facs_key_impulses('k', ['1'], ['17'], ['L30', 'R30'])
        self.assertEqual([f['label'] for f in frames[:4]], ['1 1.0', '1 0.5', 'L1 1.0', 'L1 0.5'])
        self.assertEqual(len(frames), 2 * 6)


if __name__ == '__main__':
    unittest.main()
