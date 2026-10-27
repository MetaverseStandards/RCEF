# SPDX-License-Identifier: MIT
"""The translation examples on the committed demo frames, run in process on the shared pack."""
import contextlib
import copy
import csv
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock

try:
    import shared_pack
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import shared_pack

ROOT = Path(__file__).resolve().parents[1]
FB2 = 'openxr.fb2.XR_FACE_EXPRESSION2_{}_FB'.format
sys.path.insert(0, str(ROOT / 'examples'))
import face_pipeline  # noqa: E402
import ict_facekit  # noqa: E402
import rcef_translate  # noqa: E402
import rigs  # noqa: E402
import translate_visemes_to_vrm  # noqa: E402

ICT = face_pipeline.face_targets(rigs.ict_shapes(ict_facekit.SHAPES), ict_facekit.SHAPES)
ARKIT_52 = list(face_pipeline.source_routes())
FULL = face_pipeline.face_targets([(i, a, None) for i, a in enumerate(ARKIT_52)], ARKIT_52)


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
        frames = [(s, o) for s, o in self.frames('tongue') if float(s['TONGUE_TIP_ALVEOLAR']) > 0]
        self.assertTrue(frames)
        for _, output in frames:
            self.assertIn('TONGUE_TIP_ALVEOLAR', output['dropped'])
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


class ReadFrames(unittest.TestCase):
    def test_label_columns_are_kept_and_are_not_validity_flags(self):
        translator = rcef_translate.fb2_to_arkit(pack=shared_pack.pack(), compiled=compiled())
        with tempfile.TemporaryDirectory(prefix='rcef-frames-') as tmp:
            path = Path(tmp) / 'frames.csv'
            path.write_text('time,segment,phase,amount,JAW_DROP,isValid,isEyeFollowingBlendshapesValid\n'
                            '0.0,anger,hold,1,0.5,1,0\n', encoding='utf-8')
            frame, = translator.read(path)
        self.assertEqual(frame['flags'], {'isValid': True, 'isEyeFollowingBlendshapesValid': False})
        self.assertEqual(frame['labels'], {'phase': 'hold', 'amount': '1'})
        self.assertEqual(frame['values'], {FB2('JAW_DROP'): 0.5})


def side_free(sid):
    return re.sub(r'(Left|Right)$', '#', sid)


class Fb2Oracles(unittest.TestCase):
    """The face pipeline's weight oracles catch every wrong FB2 rule on the demo frames.

    Each rule writes one coefficient and none reads another rule's output, so
    changing every rule at once and asking which shapes fail is the same as
    changing the rules one at a time. Every shape's own input moves alone in
    some demo frame, so no change can hide behind another.
    """
    MAPPINGS = ('fb2.to_arkit', 'fb2_gaze.to_arkit')

    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        cls.translator = cls.translator_for(fb2_arkit_document(cls.pack, cls.MAPPINGS))
        # A refused frame has no weights to compare, so only fully valid frames
        # can show a wrong rule; each mapping then needs one evaluation. The
        # ramps go up and back down, so each pose is kept once.
        poses = {}
        for frame in cls.translator.read(ROOT / 'examples/data/fb2_demo_frames.csv'):
            if frame['flags']['isValid'] and frame['flags']['isEyeFollowingBlendshapesValid']:
                poses.setdefault(tuple(frame['values'].values()), frame)
        cls.frames = list(poses.values())
        cls.results = cls.translator.translate(cls.frames)

    @staticmethod
    def translator_for(document):
        return rcef_translate.fb2_to_arkit(pack=rcef_translate.load_pack(document))

    def failing_shapes(self, results, targets=FULL):
        return {c['arkit'] for frame, result in zip(self.frames, results)
                for c in face_pipeline.check_channels(self.translator, frame, result, targets) if not c['passes']}

    def after(self, change):
        """Translate the demo frames with a copy of both mappings in which `change` has edited the rules."""
        document = fb2_arkit_document(self.pack, self.MAPPINGS)
        document['mappings'] = copy.deepcopy(document['mappings'])
        for mapping in document['mappings']:
            change(mapping['rules'])
        return self.translator_for(document).translate(self.frames)

    def test_the_published_rules_pass(self):
        self.assertEqual(self.failing_shapes(self.results, ICT), set())
        self.assertEqual(self.failing_shapes(self.results), set())

    def test_channels_at_rest_are_counted_apart_from_exact_ones(self):
        statuses = {}
        for frame, result in zip(self.frames, self.results):
            for c in face_pipeline.check_channels(self.translator, frame, result, ICT):
                statuses.setdefault(c['status'], []).append(c)
        self.assertNotIn('exact', set(statuses))
        self.assertTrue(statuses['at rest in both paths'])
        self.assertTrue(all(c['direct'] == 0 == c['translated'] for c in statuses['at rest in both paths']))
        self.assertTrue(statuses['exact (moving)'])
        self.assertTrue(all(c['direct'] or c['translated'] for c in statuses['exact (moving)']))

    def test_every_shape_has_a_frame_where_its_own_input_moves(self):
        for targets in (ICT, FULL):
            still = {t['name'] for t in targets}
            for frame, result in zip(self.frames, self.results):
                still -= {c['target'] for c in face_pipeline.check_channels(self.translator, frame, result, targets)
                          if c['direct']}
            self.assertEqual(still, set())

    def test_halving_every_rule_fails_every_shape(self):
        def halve(rules):
            for rule in rules:
                operator = rule['operator']
                if operator['id'] == 'affine':
                    operator['scale'] *= 0.5
                else:
                    operator['weights'] = [w * 0.5 for w in operator['weights']]
        self.assertEqual(self.failing_shapes(self.after(halve)), {t['arkit'] for t in FULL})

    def test_swapping_every_left_and_right_rule_fails_both_shapes(self):
        def swap(rules):
            pairs = {}
            for rule in rules:
                pairs.setdefault(side_free(rule['outputs'][0]), []).append(rule)
            for pair in pairs.values():
                if len(pair) == 2:
                    pair[0]['inputs'], pair[1]['inputs'] = pair[1]['inputs'], pair[0]['inputs']
        sided = {t['arkit'] for t in FULL if side_free(t['arkit']) != t['arkit']}
        self.assertEqual(len(sided), 40)
        self.assertEqual(sided - self.failing_shapes(self.after(swap)), set())

    def test_dropping_any_input_of_an_averaged_rule_fails(self):
        averaged = {r['outputs'][0][len('arkit.coefficient.'):]: len(r['inputs'])
                    for m in self.pack['mappings'] if m['id'] in self.MAPPINGS for r in m['rules']
                    if r['operator']['id'] == 'weighted_sum'}
        self.assertEqual(len(averaged), 6)
        for position in range(4):
            def drop(rules):
                for rule in rules:
                    if rule['operator']['id'] == 'weighted_sum' and position < len(rule['inputs']):
                        rule['operator']['weights'][position] = 0.0
            with self.subTest(position=position):
                expected = {name for name, count in averaged.items() if position < count}
                self.assertEqual(expected - self.failing_shapes(self.after(drop)), set())


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


class DefaultOutputs(unittest.TestCase):
    def test_examples_write_outside_the_checkout_by_default(self):
        shared = rcef_translate.visemes_to_vrm(pack=shared_pack.pack(), compiled=compiled())
        with tempfile.TemporaryDirectory(prefix='rcef-cache-') as tmp, \
                mock.patch.dict(os.environ, {'XDG_CACHE_HOME': tmp}), \
                mock.patch.object(rcef_translate, 'visemes_to_vrm', lambda: shared), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(translate_visemes_to_vrm.main([]), 0)
            self.assertTrue((Path(tmp) / 'rcef-examples/visemes_to_vrm.csv').is_file())
            args = face_pipeline.arguments([])
            self.assertEqual((args.rig, args.out), ('rocketbox-female', Path(tmp) / 'rcef-examples/face/rocketbox-female'))
            self.assertEqual(args.cache, Path(tmp) / 'rcef-face-rigs')
            self.assertEqual(face_pipeline.arguments(['--rig', 'ict']).cache, Path(tmp) / 'rcef-ict-facekit')


if __name__ == '__main__':
    unittest.main()
