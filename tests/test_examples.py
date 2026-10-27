# SPDX-License-Identifier: MIT
"""The translation examples on the committed demo frames, run in process on the shared pack."""
import copy
import csv
import json
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
import face_pipeline  # noqa: E402
import ict_facekit  # noqa: E402
import rcef_translate  # noqa: E402


def compiled():
    """The example mappings, compiled once from the shared pack."""
    return {m: shared_pack.mapping(m, s, t) for m, s, t in (('fb2.to_arkit', 'openxr.fb2', 'arkit.coefficient'),
                                                          ('fb2_gaze.to_arkit', 'openxr.fb2', 'arkit.coefficient'),
                                                          ('visemes.to_vrm', 'openxr.visemes', 'vrm.preset'))}


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
        cls.rows = translate(rcef_translate.fb2_to_arkit(pack=shared_pack.pack(), compiled=compiled()), source)

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


def fb2_arkit_document(pack, mapping_ids):
    """The pack cut down to some FB2 -> ARKit mappings and the records they use.

    msf-tools rechecks the whole pack on every call, so the many changed copies
    the oracle tests build stay fast only when the pack is small.
    """
    mappings = [m for m in pack['mappings'] if m['id'] in mapping_ids]
    members = {sid for m in mappings for r in m['rules'] for sid in r['inputs'] + r['outputs']}
    profiles = [{**p, 'signal_ids': [sid for sid in p['signal_ids'] if sid in members]}
                for p in pack['profiles'] if p['id'] in ('openxr.fb2', 'arkit.coefficient')]
    signals = [s for s in pack['signals'] if s['id'] in members]
    cited = {e for record in profiles + signals + [r for m in mappings for r in m['rules']]
             for e in record.get('evidence', [])}
    return {**pack, 'profiles': profiles, 'signals': signals, 'mappings': mappings,
            'evidence': [e for e in pack['evidence'] if e['id'] in cited]}


class Fb2Oracles(unittest.TestCase):
    """The face pipeline's weight oracles catch a wrong FB2 rule on the demo frames."""
    MAPPINGS = ('fb2.to_arkit', 'fb2_gaze.to_arkit')

    @classmethod
    def setUpClass(cls):
        pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        cls.translator = rcef_translate.fb2_to_arkit(
            pack=rcef_translate.load_pack(fb2_arkit_document(pack, cls.MAPPINGS)))
        # A refused frame has no weights to compare, so only fully valid frames
        # can show a wrong rule; each mapping then needs one evaluation. The
        # ramps go up and back down, so each pose is kept once.
        poses = {}
        for frame in cls.translator.read(ROOT / 'examples/data/fb2_demo_frames.csv'):
            if frame['flags']['isValid'] and frame['flags']['isEyeFollowingBlendshapesValid']:
                poses.setdefault(tuple(frame['values'].values()), frame)
        cls.frames = list(poses.values())
        cls.results = cls.translator.translate(cls.frames)
        cls.documents = {m: fb2_arkit_document(pack, (m,)) for m in cls.MAPPINGS}
        cls.mapping_of = {r['id']: m['id'] for m in pack['mappings'] if m['id'] in cls.MAPPINGS for r in m['rules']}

    def failing_frames(self, results):
        return [n for n, (frame, result) in enumerate(zip(self.frames, results))
                if not all(c['passes'] for c in face_pipeline.check_channels(self.translator, frame, result,
                                                                            ict_facekit.SHAPES))]

    def failing_frames_after(self, rule_id, change):
        """Change the mapping that holds `rule_id`; the other mapping keeps its published output."""
        mapping = self.mapping_of[rule_id]
        document = copy.deepcopy(self.documents[mapping])
        change({r['id']: r for r in document['mappings'][0]['rules']})
        changed = rcef_translate.Translator('openxr.fb2', 'arkit.coefficient', [mapping], self.translator.prefix,
                                            self.translator.suffix, pack=rcef_translate.load_pack(document))
        return self.failing_frames([{**r, 'values': {**r['values'], **c['values']}}
                                    for r, c in zip(self.results, changed.translate(self.frames))])

    def test_the_published_rules_pass(self):
        self.assertEqual(self.failing_frames(self.results), [])

    def test_halving_any_rule_fails(self):
        self.assertEqual(len(self.mapping_of), 14)

        def halve(rule_id):
            def change(rules):
                operator = rules[rule_id]['operator']
                if operator['id'] == 'affine':
                    operator['scale'] *= 0.5
                else:
                    operator['weights'] = [w * 0.5 for w in operator['weights']]
            return change
        for rule_id in self.mapping_of:
            with self.subTest(rule_id):
                self.assertTrue(self.failing_frames_after(rule_id, halve(rule_id)))

    def test_swapping_left_and_right_fails(self):
        def swap(first, second):
            def change(rules):
                rules[first]['inputs'], rules[second]['inputs'] = rules[second]['inputs'], rules[first]['inputs']
            return change
        for pair in (('eyeBlinkLeft', 'eyeBlinkRight'), ('mouthSmileLeft', 'mouthSmileRight'),
                     ('eyeLookOutLeft', 'eyeLookInRight'), ('eyeLookInLeft', 'eyeLookOutRight')):
            first, second = (f'fb2_arkit.{name}' for name in pair)
            with self.subTest(pair):
                self.assertTrue(self.failing_frames_after(first, swap(first, second)))


class VisemeExample(unittest.TestCase):
    def test_vowels_pass_through_and_consonants_are_dropped(self):
        source = ROOT / 'examples/data/viseme_demo_frames.csv'
        inputs = read(source)
        rows = translate(rcef_translate.visemes_to_vrm(pack=shared_pack.pack(), compiled=compiled()), source)
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
