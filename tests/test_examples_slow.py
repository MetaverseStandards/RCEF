# SPDX-License-Identifier: MIT
"""Slow tier: run the ICT-FaceKit face pipeline end to end and check its report.

Skipped unless RCEF_SLOW_TESTS=1. Set RCEF_ICT_CACHE to a directory outside
the repository for the ICT-FaceKit files (fetched on first use, about 46 MB).
It takes about a minute.
"""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SLOW = os.environ.get('RCEF_SLOW_TESTS') == '1'


@unittest.skipUnless(SLOW and os.environ.get('RCEF_ICT_CACHE'), 'slow tier: set RCEF_SLOW_TESTS=1 and RCEF_ICT_CACHE')
class FacePipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='rcef-face-')
        cls.out = Path(cls.temp.name)
        cls.process = subprocess.run([sys.executable, '-B', str(ROOT / 'examples/face_pipeline.py'),
                                  '--cache', os.environ['RCEF_ICT_CACHE'], '--out', str(cls.out)],
                                 capture_output=True, text=True, timeout=1200)
        with (ROOT / 'examples/data/fb2_demo_frames.csv').open(encoding='utf-8', newline='') as handle:
            cls.inputs = list(csv.DictReader(handle))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_pipeline_succeeds_and_every_oracle_passes(self):
        self.assertEqual(self.process.returncode, 0, self.process.stdout + self.process.stderr)
        manifest = json.loads((self.out / 'frames.json').read_text())
        self.assertEqual(len(manifest['frames']), len(self.inputs))
        self.assertTrue(all(f['oracles_pass'] for f in manifest['frames']))
        self.assertIn('not calibration', manifest['caption'])
        report = (self.out / 'residuals.md').read_text()
        self.assertIn(f'Frames where every oracle passes: {len(self.inputs)} of {len(self.inputs)}.', report)
        self.assertIn('not calibration', report)

    def test_residuals_follow_the_rules(self):
        with (self.out / 'residuals.csv').open(encoding='utf-8', newline='') as handle:
            rows = list(csv.DictReader(handle))
        exact = [r for r in rows if r['status'] == 'exact (moving)']
        averaged = [r for r in rows if r['status'].startswith('averaged pair')]
        self.assertTrue(exact and averaged)
        self.assertTrue(all(float(r['direct'] or 0) or float(r['translated'] or 0) for r in exact))
        at_rest = [r for r in rows if r['status'] == 'at rest in both paths']
        self.assertTrue(at_rest)
        self.assertTrue(all(float(r['direct']) == 0 == float(r['translated']) for r in at_rest))
        self.assertTrue(all(float(r['residual']) <= 1e-9 for r in exact))
        self.assertTrue(all(float(r['residual']) <= float(r['bound']) + 1e-9 for r in averaged))
        self.assertTrue(any(float(r['residual']) > 0 for r in averaged), 'the asymmetric frames must show a loss')

    def test_every_shape_moves_in_some_frame(self):
        with (self.out / 'residuals.csv').open(encoding='utf-8', newline='') as handle:
            rows = list(csv.DictReader(handle))
        moving = {r['target'] for r in rows if r['status'] == 'exact (moving)' or r['status'].startswith('averaged')}
        manifest = json.loads((self.out / 'frames.json').read_text())
        self.assertEqual(moving, set(manifest['targets']))
        self.assertIn('## Frames in which each shape moves', (self.out / 'residuals.md').read_text())

    def test_refusals_and_dropped_channels_are_labelled(self):
        manifest = json.loads((self.out / 'frames.json').read_text())
        by_segment = {}
        for frame in manifest['frames']:
            by_segment.setdefault(frame['segment'], []).append(frame)
        for frame in by_segment['eye following lost']:
            self.assertTrue(any('fb2_gaze.to_arkit' in label for label in frame['labels']))
            self.assertFalse(any('fb2.to_arkit:' in label for label in frame['labels']))
        for frame in by_segment['face lost']:
            self.assertTrue(any('fb2.to_arkit:' in label for label in frame['labels']))
        self.assertTrue(any('TONGUE_OUT' in label for f in by_segment['tongue'] for label in f['labels']))

    def test_renderer_files_have_the_declared_sizes(self):
        manifest = json.loads((self.out / 'frames.json').read_text())
        vertices = manifest['vertex_count']
        self.assertEqual((self.out / manifest['indices']).stat().st_size % 12, 0)
        for frame in manifest['frames'][::17]:
            for key in ('direct', 'translated', 'difference_colors'):
                self.assertEqual((self.out / frame[key]).stat().st_size, vertices * 12, (frame['frame'], key))


if __name__ == '__main__':
    unittest.main()
