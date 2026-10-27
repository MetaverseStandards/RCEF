# SPDX-License-Identifier: MIT
"""The pure parts of the MediaPipe calibration tool: fitting, inverting and scoring cells (no rendering)."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/calibration'))
import k4_mediapipe as k  # noqa: E402
import k4_record  # noqa: E402
import check  # noqa: E402


def sweeps(response, conditions=24, missing=()):
    return {i: {w: None if (i, w) in missing else response(w) for w in k.WEIGHTS} for i in range(conditions)}


class Fit(unittest.TestCase):
    def test_isotonic_pools_any_fall(self):
        self.assertEqual(k.isotonic([0.0, 0.3, 0.2, 0.5, 0.4, 0.6]), [0.0, 0.25, 0.25, 0.45, 0.45, 0.6])
        self.assertEqual(k.isotonic([0.1, 0.2, 0.3]), [0.1, 0.2, 0.3])

    def test_a_linear_response_inverts_to_the_weight(self):
        knots, why = k.fit_channel(sweeps(lambda w: 0.1 + 0.6 * w))
        self.assertEqual(why, 'fitted')
        self.assertEqual((knots[0], knots[-1]), ([0.0, 0.0], [1.0, 1.0]))
        xs = [x for x, _ in knots]
        self.assertTrue(all(b > a for a, b in zip(xs, xs[1:])))
        for w in k.WEIGHTS:
            self.assertAlmostEqual(k.inverse(knots, 0.1 + 0.6 * w), w, places=6)
        self.assertEqual(k.inverse(knots, 0.05), 0.0)
        self.assertEqual(k.inverse(knots, 0.9), 1.0)

    def test_a_flat_or_undetected_response_is_not_fitted(self):
        self.assertIn('rises only', k.fit_channel(sweeps(lambda w: 0.3 + 0.05 * w))[1])
        missing = {(i, 1.0) for i in range(13)}
        self.assertIn('no face', k.fit_channel(sweeps(lambda w: w, missing=missing))[1])

    def test_a_plateau_keeps_its_lowest_weight(self):
        knots, _ = k.fit_channel(sweeps(lambda w: min(w, 0.6)))
        self.assertEqual([y for x, y in knots if 0 < x < 1], [0.2, 0.4, 0.6])

    def test_cells_count_missed_faces_as_failures_and_measure_errors(self):
        knots, _ = k.fit_channel(sweeps(lambda w: 0.1 + 0.6 * w))
        result = k.cell(knots, sweeps(lambda w: 0.1 + 0.6 * w, 20, missing={(3, 0.4)}), 20)
        self.assertEqual(result['failures'], 1)
        self.assertLess(result['p95'], 1e-6)
        result = k.cell(knots, sweeps(lambda w: 0.1 + 0.3 * w, 20), 20)
        self.assertGreater(result['p95'], 0.15)
        self.assertEqual(result['neutral'], 0.0)


class Tool(unittest.TestCase):
    def test_every_channel_has_its_ict_shapes_pinned(self):
        pinned = {Path(name).stem for name in k.ICT_FILES}
        for channel in k.CHANNELS:
            with self.subTest(channel):
                self.assertLessEqual(set(k.ict_names(channel)), pinned)
        self.assertEqual(len(k.CHANNELS), 51)

    def test_conditions_are_reproducible(self):
        self.assertEqual(k.training_conditions(), k.training_conditions())
        self.assertEqual(k.held_out_conditions([7, 8], True), k.held_out_conditions([7, 8], True))
        self.assertNotIn('identity', k.held_out_conditions([7], False)[0])

    def test_pending_rules_use_the_records_frozen_knots(self):
        self.assertEqual(check.calibration_problems(ROOT / 'calibration', k4_record.read_rules()), [])


if __name__ == '__main__':
    unittest.main()
