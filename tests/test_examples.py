# SPDX-License-Identifier: MIT
"""The translation examples on the committed demo frames, run in process on the shared pack."""
import csv
from pathlib import Path
import sys
import tempfile
import unittest

try:
    import shared_pack
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import shared_pack

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import rcef_translate  # noqa: E402


def translate(translator, source):
    """Translate a frames CSV and read back the CSV the example writes."""
    results = translator.translate(translator.read(source))
    with tempfile.TemporaryDirectory(prefix='rcef-example-') as tmp:
        out = Path(tmp) / 'out.csv'
        translator.write(results, out)
        with out.open(encoding='utf-8', newline='') as handle:
            return list(csv.DictReader(handle))


def read(source):
    with source.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


class Fb2Example(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = ROOT / 'examples/data/fb2_demo_frames.csv'
        cls.inputs = read(source)
        cls.rows = translate(rcef_translate.fb2_to_arkit(pack=shared_pack.pack()), source)

    def frames(self, segment):
        return [(i, o) for i, o in zip(self.inputs, self.rows) if i['segment'] == segment]

    def test_one_row_per_input_frame(self):
        self.assertEqual([r['time'] for r in self.rows], [r['time'] for r in self.inputs])

    def test_one_to_one_and_averaged_values(self):
        for source, output in self.frames('jaw sweep'):
            self.assertEqual(float(output['jawOpen']), float(source['JAW_DROP']))
        for source, output in self.frames('asymmetric brows'):
            expected = (float(source['INNER_BROW_RAISER_L']) + float(source['INNER_BROW_RAISER_R'])) / 2
            self.assertEqual(float(output['browInnerUp']), expected)
        for source, output in self.frames('gaze left'):
            self.assertEqual(float(output['eyeLookOutLeft']), float(source['EYES_LOOK_LEFT_L']))
            self.assertEqual(float(output['eyeLookInRight']), float(source['EYES_LOOK_LEFT_R']))

    def test_lost_eye_following_keeps_face_and_refuses_gaze(self):
        frames = self.frames('eye following lost')
        self.assertTrue(frames)
        for source, output in frames:
            self.assertEqual(float(output['eyeBlinkLeft']), float(source['EYES_CLOSED_L']))
            self.assertEqual(output['eyeLookOutLeft'], '')
            self.assertIn('fb2_gaze.to_arkit', output['refused'])
            self.assertNotIn('fb2.to_arkit:', output['refused'])

    def test_lost_face_refuses_everything(self):
        for _, output in self.frames('face lost'):
            self.assertEqual(output['jawOpen'], '')
            self.assertIn('fb2.to_arkit', output['refused'])
            self.assertIn('fb2_gaze.to_arkit', output['refused'])

    def test_unmapped_tongue_is_listed_as_dropped(self):
        frames = [(s, o) for s, o in self.frames('tongue') if float(s['TONGUE_OUT']) > 0]
        self.assertTrue(frames)
        for _, output in frames:
            self.assertIn('TONGUE_OUT', output['dropped'])
            self.assertEqual(float(output['jawOpen']), 0.5)


class VisemeExample(unittest.TestCase):
    def test_vowels_pass_through_and_consonants_are_dropped(self):
        source = ROOT / 'examples/data/viseme_demo_frames.csv'
        inputs = read(source)
        rows = translate(rcef_translate.visemes_to_vrm(pack=shared_pack.pack()), source)
        self.assertEqual(len(rows), len(inputs))
        for source_row, output in zip(inputs, rows):
            if source_row['isValid'] == '0':
                self.assertIn('visemes.to_vrm', output['refused'])
                continue
            for viseme, preset in (('AA', 'aa'), ('E', 'ee'), ('IH', 'ih'), ('OH', 'oh'), ('OU', 'ou')):
                self.assertEqual(float(output[preset]), float(source_row[viseme]))
            if float(source_row['PP']) > 0:
                self.assertIn('PP', output['dropped'])


if __name__ == '__main__':
    unittest.main()
