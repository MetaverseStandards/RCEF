# SPDX-License-Identifier: MIT
"""The translation examples on the committed demo frames, run in process on the shared pack.

The examples translate through the canonical sets (examples/rcef_frames.py), so a refusal names a hop map.
"""
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
import rcef_frames  # noqa: E402
import rigs  # noqa: E402
import translate_visemes_to_vrm  # noqa: E402

ICT = face_pipeline.face_targets(rigs.ict_shapes(ict_facekit.SHAPES), ict_facekit.SHAPES)
ARKIT_52 = list(face_pipeline.source_routes())
FULL = face_pipeline.face_targets([(i, a, None) for i, a in enumerate(ARKIT_52)], ARKIT_52)


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
        cls.rows = translate(shared_pack.frames('fb2_to_arkit'), source)

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
            # The whole cell: the hop map, its code and the refused inputs by the provider's own names.
            self.assertEqual(output['refused'],
                             'fb2_gaze.to_rcef: E_INVALID_SAMPLE on 8 inputs (EYES_LOOK_DOWN_L, EYES_LOOK_DOWN_R, '
                             'EYES_LOOK_LEFT_L, EYES_LOOK_LEFT_R, EYES_LOOK_RIGHT_L, EYES_LOOK_RIGHT_R, EYES_LOOK_UP_L, '
                             'EYES_LOOK_UP_R)')

    def test_lost_face_refuses_everything(self):
        for _, output in self.frames('face lost'):
            self.assertEqual(output['jawOpen'], '')
            self.assertIn('fb2_face.to_rcef', output['refused'])
            self.assertIn('fb2_gaze.to_rcef', output['refused'])

    def test_unmapped_tongue_is_listed_as_dropped(self):
        frames = [(s, o) for s, o in self.frames('tongue') if float(s['TONGUE_TIP_ALVEOLAR']) > 0]
        self.assertTrue(frames)
        for _, output in frames:
            self.assertIn('TONGUE_TIP_ALVEOLAR', output['dropped'])
            self.assertEqual(float(output['jawOpen']), 0.5)


class ReadFrames(unittest.TestCase):
    def test_label_columns_are_kept_and_are_not_validity_flags(self):
        translator = shared_pack.frames('fb2_to_arkit')
        with tempfile.TemporaryDirectory(prefix='rcef-frames-') as tmp:
            path = Path(tmp) / 'frames.csv'
            path.write_text('time,segment,phase,amount,JAW_DROP,isValid,isEyeFollowingBlendshapesValid\n'
                            '0.0,anger,hold,1,0.5,1,0\n', encoding='utf-8')
            frame, = translator.read(path)
        self.assertEqual(frame['flags'], {'isValid': True, 'isEyeFollowingBlendshapesValid': False})
        self.assertEqual(frame['labels'], {'phase': 'hold', 'amount': '1'})
        self.assertEqual(frame['values'], {FB2('JAW_DROP'): 0.5})


def side_free(sid):
    """The ID without its side: ARKit names end in Left or Right, canonical names in _left or _right."""
    return re.sub(r'(Left|Right|_left|_right)$', '#', sid)


class ArkitToFb2(unittest.TestCase):
    def test_opposing_gaze_is_netted_so_fb2_exclusivity_holds(self):
        translator = shared_pack.frames('arkit_to_fb2')
        zero = dict.fromkeys(translator.inputs, 0.0)
        frames = [{'time': 0.0, 'segment': 'both ways', 'flags': {}, 'labels': {},
                   'values': {**zero, 'arkit.coefficient.eyeLookInLeft': 0.5, 'arkit.coefficient.eyeLookOutLeft': 0.25,
                              'arkit.coefficient.jawOpen': 0.75}},
                  {'time': 0.1, 'segment': 'one way', 'flags': {}, 'labels': {},
                   'values': {**zero, 'arkit.coefficient.eyeLookInLeft': 0.5}}]
        both, one = translator.translate(frames)
        self.assertEqual(both['values'][FB2('JAW_DROP')], 0.75)
        self.assertEqual((both['values'][FB2('EYES_LOOK_RIGHT_L')], both['values'][FB2('EYES_LOOK_LEFT_L')]), (0.25, 0.0))
        self.assertEqual(one['values'][FB2('EYES_LOOK_RIGHT_L')], 0.5)
        self.assertEqual(both['refused'] + one['refused'], [])
        self.assertFalse(any(o.startswith('rcef.intermediate.') for o in translator.outputs))


class Fb2Oracles(unittest.TestCase):
    """The face pipeline's weight oracles catch every wrong mapping of the FB2 -> ARKit route on the demo frames.

    The route has two hops: the in-maps (FB2 -> canonical) and the out-maps
    (canonical -> ARKit). Each mutation changes the maps of one hop. Each
    mapping writes one signal, and none reads another mapping's output, so
    changing every mapping of a hop at once and asking which shapes fail is the
    same as changing them one at a time. Every shape's own input moves alone in
    some demo frame, so no change can hide behind another.
    """

    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        route = shared_pack.frames('fb2_to_arkit').route
        cls.hops = {'in': route.in_maps, 'out': route.out_maps}
        cls.document = shared_pack.cut(cls.pack, route.in_maps + route.out_maps)
        cls.translator = cls.translator_for(cls.document)
        # A refused frame has no weights to compare, so only fully valid frames
        # can show a wrong mapping, and each map then needs one evaluation. The
        # ramps go up and back down, so each pose is kept once.
        poses = {}
        for frame in cls.translator.read(ROOT / 'examples/data/fb2_demo_frames.csv'):
            if frame['flags']['isValid'] and frame['flags']['isEyeFollowingBlendshapesValid']:
                poses.setdefault(tuple(frame['values'].values()), frame)
        cls.frames = list(poses.values())
        cls.results = cls.translator.translate(cls.frames)

    @staticmethod
    def translator_for(document):
        return rcef_frames.fb2_to_arkit(pack=rcef_frames.load_pack(document))

    def failing_shapes(self, results, targets=FULL):
        return {c['arkit'] for frame, result in zip(self.frames, results)
                for c in face_pipeline.check_channels(self.translator, frame, result, targets) if not c['passes']}

    def after(self, change, hop):
        """Translate the demo frames with a copy of the route in which `change` has edited the rules of one hop."""
        document = copy.deepcopy(self.document)
        for mapping in document['mappings']:
            if mapping['id'] in self.hops[hop]:
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
        for hop in self.hops:
            with self.subTest(hop=hop):
                self.assertEqual(self.failing_shapes(self.after(halve, hop)), {t['arkit'] for t in FULL})

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
        for hop in self.hops:
            with self.subTest(hop=hop):
                self.assertEqual(sided - self.failing_shapes(self.after(swap, hop)), set())

    def test_dropping_any_input_of_an_averaged_rule_fails(self):
        # Only the out-maps average: every in-map mapping copies one FB2 weight.
        averaged = {r['outputs'][0][len('arkit.coefficient.'):]: len(r['inputs'])
                    for m in self.document['mappings'] if m['id'] in self.hops['out'] for r in m['rules']
                    if r['operator']['id'] == 'weighted_sum'}
        self.assertEqual(len(averaged), 6)
        self.assertFalse([r for m in self.document['mappings'] if m['id'] in self.hops['in'] for r in m['rules']
                          if len(r['inputs']) > 1])
        for position in range(4):
            def drop(rules):
                for rule in rules:
                    if rule['operator']['id'] == 'weighted_sum' and position < len(rule['inputs']):
                        rule['operator']['weights'][position] = 0.0
            with self.subTest(position=position):
                expected = {name for name, count in averaged.items() if position < count}
                self.assertEqual(expected - self.failing_shapes(self.after(drop, 'out')), set())


class VisemeExample(unittest.TestCase):
    def test_vowels_pass_through_and_consonants_are_dropped(self):
        source = ROOT / 'examples/data/viseme_demo_frames.csv'
        inputs = read(source)
        rows = translate(shared_pack.frames('visemes_to_vrm'), source)
        self.assertEqual(len(rows), len(inputs))
        for source_row, output in zip(inputs, rows):
            if source_row['isValid'] == '0':
                self.assertEqual(output['refused'],
                                 'visemes_vowel.to_rcef: E_INVALID_SAMPLE on 5 inputs (AA, E, IH, OH, OU)')
                continue
            for viseme, preset in (('AA', 'aa'), ('E', 'ee'), ('IH', 'ih'), ('OH', 'oh'), ('OU', 'ou')):
                self.assertEqual(float(output[preset]), float(source_row[viseme]))
            if float(source_row['PP']) > 0:
                self.assertIn('PP', output['dropped'])


class Columns(unittest.TestCase):
    def test_the_output_columns_keep_the_order_of_the_a1_maps(self):
        # The published example outputs must not change, so each CSV keeps the column order that the direct maps
        # gave it, read here from the A1 pack at dea1713 (tests/fixtures/baseline-dea1713.pack.json).
        pack = json.loads((ROOT / 'tests/fixtures/baseline-dea1713.pack.json').read_text(encoding='utf-8'))
        rules = {m['id']: m['rules'] for m in pack['mappings']}
        for kind, maps in (('fb2_to_arkit', ('fb2.to_arkit', 'fb2_gaze.to_arkit')),
                           ('visemes_to_vrm', ('visemes.to_vrm',)), ('fb2_to_vrm', ('fb2.to_vrm',))):
            with self.subTest(kind):
                computed = {i for m in maps for r in rules[m] for i in r['inputs']}
                expected = [o.rsplit('.', 1)[1] for m in maps for r in rules[m] for o in r['outputs']
                            if o not in computed]
                translator = shared_pack.frames(kind)
                with tempfile.TemporaryDirectory(prefix='rcef-columns-') as tmp:
                    out = Path(tmp) / 'out.csv'
                    translator.write([], out)
                    header = out.read_text(encoding='utf-8').splitlines()[0].split(',')
                self.assertEqual(header, ['time', 'segment', *expected, 'refused', 'dropped'])


class DefaultOutputs(unittest.TestCase):
    def test_examples_write_outside_the_checkout_by_default(self):
        shared = shared_pack.frames('visemes_to_vrm')
        with tempfile.TemporaryDirectory(prefix='rcef-cache-') as tmp, \
                mock.patch.dict(os.environ, {'XDG_CACHE_HOME': tmp}), \
                mock.patch.object(rcef_frames, 'visemes_to_vrm', lambda: shared), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(translate_visemes_to_vrm.main([]), 0)
            self.assertTrue((Path(tmp) / 'rcef-examples/visemes_to_vrm.csv').is_file())
            args = face_pipeline.arguments([])
            self.assertEqual((args.rig, args.out), ('rocketbox-female', Path(tmp) / 'rcef-examples/face/rocketbox-female'))
            self.assertEqual(args.cache, Path(tmp) / 'rcef-face-rigs')
            self.assertEqual(face_pipeline.arguments(['--rig', 'ict']).cache, Path(tmp) / 'rcef-ict-facekit')


if __name__ == '__main__':
    unittest.main()
