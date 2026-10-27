# SPDX-License-Identifier: MIT
"""Slow tier: run the face and viseme pipelines end to end and check their reports.

Skipped unless RCEF_SLOW_TESTS=1. Set RCEF_ICT_CACHE (ICT-FaceKit, about 46 MB)
and RCEF_RIG_CACHE (Rocketbox and the VRM sample, about 15 MB) to directories
outside the repository; the files are fetched on first use. Each class is
skipped if its cache variable is unset. All of it takes about ten minutes.
"""
import csv
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SLOW = os.environ.get('RCEF_SLOW_TESTS') == '1'
RIG_CACHE = os.environ.get('RCEF_RIG_CACHE')


def run(script, *args):
    return subprocess.run([sys.executable, '-B', str(ROOT / 'examples' / script), *args],
                          capture_output=True, text=True, timeout=1800)


def read(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


@unittest.skipUnless(SLOW and os.environ.get('RCEF_ICT_CACHE'), 'slow tier: set RCEF_SLOW_TESTS=1 and RCEF_ICT_CACHE')
class FacePipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='rcef-face-')
        cls.out = Path(cls.temp.name)
        cls.process = run('face_pipeline.py', '--rig', 'ict', '--frames', str(ROOT / 'examples/data/fb2_demo_frames.csv'),
                          '--cache', os.environ['RCEF_ICT_CACHE'], '--out', str(cls.out))
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
        moving = {r['target'] for r in rows if r['direct'] and float(r['direct'])}
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
        self.assertTrue(any('TONGUE_TIP_ALVEOLAR' in label for f in by_segment['tongue'] for label in f['labels']))

    def test_renderer_files_have_the_declared_sizes(self):
        manifest = json.loads((self.out / 'frames.json').read_text())
        vertices = manifest['vertex_count']
        self.assertEqual((self.out / manifest['indices']).stat().st_size % 12, 0)
        for frame in manifest['frames'][::17]:
            for key in ('direct', 'translated', 'difference_colors'):
                self.assertEqual((self.out / frame[key]).stat().st_size, vertices * 12, (frame['frame'], key))


class RocketboxFace:
    """Run once per Rocketbox identity; the subclasses name the rig."""
    RIG = ''

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='rcef-rocketbox-')
        cls.out = Path(cls.temp.name)
        cls.process = run('face_pipeline.py', '--rig', cls.RIG, '--cache', RIG_CACHE, '--out', str(cls.out))
        cls.inputs = read(ROOT / 'examples/data/fb2_expression_frames.csv')
        cls.manifest = json.loads((cls.out / 'frames.json').read_text()) if not cls.process.returncode else None

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_every_oracle_passes_on_every_expression_frame(self):
        self.assertEqual(self.process.returncode, 0, self.process.stdout + self.process.stderr)
        self.assertEqual(len(self.manifest['frames']), len(self.inputs))
        self.assertTrue(all(f['oracles_pass'] for f in self.manifest['frames']))
        self.assertEqual(len(self.manifest['targets']), 52)

    def test_frames_name_their_expression_phase_and_what_is_not_translated(self):
        frames = {(f['segment'], f['phase']) for f in self.manifest['frames']}
        self.assertIn(('anger', 'hold'), frames)
        self.assertIn(('look down', 'out'), frames)
        anger = next(f for f in self.manifest['frames'] if f['segment'] == 'anger' and f['phase'] == 'hold')
        self.assertFalse(any(label.startswith('no RCEF rule yet') for f in self.manifest['frames'] for label in f['labels']))
        self.assertTrue(any('LIP_TIGHTENER_L' in label for label in anger['labels']))
        surprise = next(f for f in self.manifest['frames'] if f['segment'] == 'surprise' and f['phase'] == 'hold')
        self.assertIn('AU 25 (lips part): no FB2 channel', surprise['labels'])

    def test_covered_shapes_are_exact_and_the_facs_panel_is_labelled(self):
        rows = read(self.out / 'residuals.csv')
        exact = [r for r in rows if r['status'] == 'exact (moving)']
        self.assertTrue(exact)
        self.assertTrue(all(float(r['residual']) <= 1e-9 for r in exact))
        self.assertIn('browInnerUp', {r['arkit'] for r in exact})
        self.assertIn('not an error measure', self.manifest['facs_caption'])
        vertices = self.manifest['vertex_count']
        for frame in self.manifest['frames'][::37]:
            for key in ('direct', 'translated', 'facs', 'difference_colors', 'facs_difference_colors'):
                self.assertEqual((self.out / frame[key]).stat().st_size, vertices * 12, (frame['frame'], key))


    def test_a_wink_is_shown_with_the_one_sided_closed_eye_on_the_facs_panel(self):
        wink = next(f for f in self.manifest['frames'] if f['segment'] == 'wink left' and f['phase'] == 'hold')
        self.assertTrue(any('shown as AU 43' in note for note in wink['facs_labels']))


@unittest.skipUnless(SLOW and RIG_CACHE, 'slow tier: set RCEF_SLOW_TESTS=1 and RCEF_RIG_CACHE')
class RocketboxFemaleFace(RocketboxFace, unittest.TestCase):
    RIG = 'rocketbox-female'


@unittest.skipUnless(SLOW and RIG_CACHE, 'slow tier: set RCEF_SLOW_TESTS=1 and RCEF_RIG_CACHE')
class RocketboxMaleFace(RocketboxFace, unittest.TestCase):
    RIG = 'rocketbox-male'


@unittest.skipUnless(SLOW and os.environ.get('RCEF_ICT_CACHE'), 'slow tier: set RCEF_SLOW_TESTS=1 and RCEF_ICT_CACHE')
class IctExpressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='rcef-ict-expr-')
        cls.out = Path(cls.temp.name)
        cls.process = run('face_pipeline.py', '--rig', 'ict', '--cache', os.environ['RCEF_ICT_CACHE'], '--out', str(cls.out))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_every_oracle_passes_on_every_expression_frame(self):
        self.assertEqual(self.process.returncode, 0, self.process.stdout + self.process.stderr)
        manifest = json.loads((self.out / 'frames.json').read_text())
        self.assertEqual(len(manifest['frames']), len(read(ROOT / 'examples/data/fb2_expression_frames.csv')))
        self.assertTrue(all(f['oracles_pass'] for f in manifest['frames']))
        self.assertIn(('happiness', 'hold'), {(f['segment'], f['phase']) for f in manifest['frames']})
        statuses = {r['status'] for r in read(self.out / 'residuals.csv')}
        self.assertIn('averaged pair, within half the L/R difference', statuses)


@unittest.skipUnless(SLOW and RIG_CACHE, 'slow tier: set RCEF_SLOW_TESTS=1 and RCEF_RIG_CACHE')
class Visemes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='rcef-visemes-')
        cls.out = Path(cls.temp.name)
        cls.runs = {rig: run('viseme_pipeline.py', '--rig', rig, '--cache', RIG_CACHE, '--out', str(cls.out / rig))
                    for rig in ('vrm-twist', 'rocketbox-female', 'rocketbox-male')}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_translated_vrm_morph_weights_match_the_direct_ones(self):
        process = self.runs['vrm-twist']
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        manifest = json.loads((self.out / 'vrm-twist/frames.json').read_text())
        self.assertTrue(all(f['max_morph_weight_difference'] <= 1e-9 for f in manifest['frames']))
        self.assertTrue(any('PP: no VRM preset' in label for f in manifest['frames'] for label in f['labels']))
        self.assertIn('not calibration', manifest['caption'])
        winks = [f for f in manifest['frames'] if f['segment'].startswith('wink')]
        self.assertEqual({f['segment'] for f in winks}, {'wink left', 'wink right'})
        self.assertTrue(any(f['max_morph_weight_difference'] == 0 and f['phase'] == 'hold' for f in winks))

    def test_vrm_blink_left_closes_the_eye_on_the_models_own_left(self):
        # VRM does not say whose left blinkLeft is; RCEF assumes the avatar's own,
        # so check it on this model's geometry rather than trusting its axes.
        sys.path.insert(0, str(ROOT / 'examples'))
        import msf_tools as msf
        import rigs
        import viseme_pipeline
        import vrm_presets
        rig = rigs.load('vrm-twist', Path(RIG_CACHE))
        expressions = vrm_presets.presets(rig.snapshot.to_dict()['document'])

        def positions(values):
            weights = viseme_pipeline.vectors(rig.snapshot, vrm_presets.morph_weights(expressions, values)[0])
            geometry = rigs.require(msf.evaluate_geometry(rig.snapshot, morph_weights=weights))
            return [p for instance in geometry.instances for primitive in instance['primitives']
                    for p in primitive['positions']]

        def mean(points, axis):
            return sum(p[axis] for p in points) / len(points)
        neutral = positions({})
        moved = {name: [q for p, q in zip(neutral, positions({name: 1.0})) if math.dist(p, q) > 1e-6]
                 for name in ('blinkLeft', 'blinkRight')}
        eyes = moved['blinkLeft'] + moved['blinkRight']
        # The eyes sit at the front of the head: compare them with everything at or above them.
        head = [p for p in neutral if p[1] >= min(q[1] for q in eyes)]
        facing = 1 if mean(eyes, 2) > mean(head, 2) else -1
        # With y up, the avatar's own left is up x forward: +x when it faces +z.
        left = facing
        self.assertGreater(left * mean(moved['blinkLeft'], 0), 0)
        self.assertLess(left * mean(moved['blinkRight'], 0), 0)

    def test_rocketbox_speaks_with_its_own_viseme_shapes(self):
        for rig in ('rocketbox-female', 'rocketbox-male'):
            with self.subTest(rig):
                process = self.runs[rig]
                self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                manifest = json.loads((self.out / rig / 'frames.json').read_text())
                self.assertEqual({f['segment'] for f in manifest['frames']}, {'', 'bed', 'car', 'toe', 'book'})
                self.assertEqual(manifest['panels'], ['direct'])


if __name__ == '__main__':
    unittest.main()
