# SPDX-License-Identifier: MIT
"""Arm A3 (tests/ab_a3.py): the expression library's AU table at dea1713, run without msf-character-tools."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import facs_codec  # noqa: E402

try:
    import ab_a3
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import ab_a3


class Fixture(unittest.TestCase):
    def test_the_fixture_files_have_the_pinned_hashes(self):
        self.assertEqual(ab_a3.fixture_problems(), [])

    def test_the_fixture_files_are_the_files_at_dea1713(self):
        for name in ab_a3.SHA256:
            result = subprocess.run(['git', 'show', f'{ab_a3.COMMIT}:examples/data/{name}'], cwd=ROOT,
                                    capture_output=True)
            if result.returncode:
                self.skipTest('no Git history for dea1713')
            self.assertEqual(result.stdout, (ab_a3.FIXTURE / name).read_bytes(), name)

    def test_fps_and_the_70_channels_are_frozen_from_the_fixture(self):
        fb2 = ab_a3.channels()
        self.assertEqual(len(fb2), 70)
        self.assertEqual((fb2[0], fb2[-1]), ('BROW_LOWERER_L', 'TONGUE_RETREAT'))
        with (ab_a3.FIXTURE / 'fb2_expression_frames.csv').open(encoding='utf-8') as handle:
            second = handle.readlines()[2]
        self.assertTrue(second.startswith(f'{1 / ab_a3.FPS:.6f},'))


class Arm(unittest.TestCase):
    def test_a3_rewrites_the_csv_at_dea1713_byte_for_byte(self):
        with tempfile.TemporaryDirectory(prefix='rcef-a3-') as tmp:
            path = Path(tmp) / 'fb2_expression_frames.csv'
            self.assertEqual(ab_a3.rewrite(path), 221)
            self.assertEqual(path.read_bytes(), (ab_a3.FIXTURE / 'fb2_expression_frames.csv').read_bytes())

    def test_a3_writes_every_channel_and_fills_unset_ones_with_zero(self):
        frames = ab_a3.a3_frames()
        self.assertEqual(len(frames), 221)
        self.assertTrue(all(len(f) == 70 for f in frames))
        self.assertEqual({k: v for k, v in ab_a3.a3_keys({'L1': 0.4, 'R30': 0.6}).items() if v},
                         {'INNER_BROW_RAISER_L': 0.4, 'JAW_SIDEWAYS_RIGHT': 0.6})

    def test_b_reads_the_same_frames_through_the_codec(self):
        readings = ab_a3.b_inputs(facs_codec)
        self.assertEqual(len(readings), 221)
        self.assertTrue(all(r.values is not None and not r.left_out for r in readings))
        lib = ab_a3.library()
        hold = [n for n, row in enumerate(ab_a3.expression_rows(lib, ab_a3.channels())) if row['phase'] == 'hold']
        by_name = {e['name']: readings[i] for e, i in zip(lib['expressions'], hold[::ab_a3.HOLD], strict=True)}
        self.assertEqual(by_name['surprise'].not_read, ('25',))
        self.assertEqual(by_name['look left'].not_read, ('61',))
        self.assertEqual({k: v for k, v in by_name['wink left'].values.items() if v},
                         {'facs.code.au43_left': 1.0, 'facs.code.au06_left': 0.3})


if __name__ == '__main__':
    unittest.main()
