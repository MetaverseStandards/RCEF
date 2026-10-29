# SPDX-License-Identifier: MIT
"""examples/rcef_route.py: the source -> canonical -> target runner, and its anchor to today's Translator.

The anchor runs Route's one-hop mode and rcef_translate.Translator on the A1
baseline pack (tests/fixtures/baseline-dea1713.pack.json) and requires the
same bits and the same refused frames per map, so a runner bug cannot hide in
both arms of the A/B comparison. The synthetic pack checks what only the
two-hop mode does.
"""
from copy import copy
import json
from pathlib import Path
import struct
import sys
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import rcef_route  # noqa: E402
import rcef_translate  # noqa: E402

FIXTURE = ROOT / 'tests/fixtures/baseline-dea1713.pack.json'
DATA = ROOT / 'examples/data'
# Refused frames per map, measured on the baseline pack: the gaze map refuses the
# 16 FB2 demo frames whose eye-following flag is cleared or whose face is lost,
# the face maps the 5 face-lost frames, and the viseme map the 3 invalid frames.
REFUSED = {
    ('fb2_to_arkit', 'fb2_demo_frames.csv'): {'fb2_gaze.to_arkit': 16, 'fb2.to_arkit': 5},
    ('fb2_to_arkit', 'fb2_expression_frames.csv'): {},
    ('fb2_to_vrm', 'fb2_demo_frames.csv'): {'fb2.to_vrm': 5},
    ('fb2_to_vrm', 'fb2_expression_frames.csv'): {},
    ('visemes_to_vrm', 'viseme_demo_frames.csv'): {'visemes.to_vrm': 3},
    ('visemes_to_vrm', 'viseme_talk_frames.csv'): {},
}
PROFILES = {'fb2_to_arkit': ('openxr.fb2', 'arkit.coefficient'), 'fb2_to_vrm': ('openxr.fb2', 'vrm.preset'),
            'visemes_to_vrm': ('openxr.visemes', 'vrm.preset'), 'arkit_to_fb2': ('arkit.coefficient', 'openxr.fb2')}


def bits(values):
    return {k: struct.pack('>d', v) for k, v in values.items()}


def differences(translator, expected, actual):
    """Every way Route's results differ from Translator's: values (bit for bit), refused maps and dropped inputs."""
    found = []
    for i, (a, b) in enumerate(zip(expected, actual, strict=True)):
        if bits(a['values']) != bits(b['values']):
            found.append(f'frame {i}: values differ')
        if sorted(r.split(':', 1)[0] for r in a['refused']) != sorted(b['refused']):
            found.append(f'frame {i}: refused maps differ')
        if sorted(translator.signal_id(s) for s in a['dropped']) != b['dropped']:
            found.append(f'frame {i}: dropped inputs differ')
    return found


def refused_counts(results):
    counts = {}
    for result in results:
        for mapping in result['refused']:
            counts[mapping] = counts.get(mapping, 0) + 1
    return counts


class TranslatorAnchor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = rcef_translate.load_pack(json.loads(FIXTURE.read_text(encoding='utf-8')))
        cls.translators = {kind: getattr(rcef_translate, kind)(pack=cls.pack) for kind in PROFILES}
        cls.complete = None

    def route(self, kind):
        return rcef_route.Route(*PROFILES[kind], pack=self.pack, maps=list(self.translators[kind].mappings))

    def check(self, translator, route, frames, expected_refusals):
        expected, actual = translator.translate(frames), route.translate(frames)
        self.assertEqual(differences(translator, expected, actual), [])
        self.assertEqual(refused_counts(actual), expected_refusals)
        return actual

    def frames(self, kind, name):
        return self.translators[kind].read(DATA / name)

    def test_1_fb2_to_arkit_on_both_fb2_csvs(self):
        for name, full in (('fb2_demo_frames.csv', 425), ('fb2_expression_frames.csv', 221)):
            with self.subTest(name):
                frames = self.frames('fb2_to_arkit', name)
                results = self.check(self.translators['fb2_to_arkit'], self.route('fb2_to_arkit'), frames,
                                     REFUSED['fb2_to_arkit', name])
                complete = [r for r in results if len(r['values']) == 52]
                self.assertEqual(len(complete), full)

    def test_2_fb2_to_vrm_on_both_fb2_csvs(self):
        for name in ('fb2_demo_frames.csv', 'fb2_expression_frames.csv'):
            with self.subTest(name):
                self.check(self.translators['fb2_to_vrm'], self.route('fb2_to_vrm'), self.frames('fb2_to_vrm', name),
                           REFUSED['fb2_to_vrm', name])

    def test_3_visemes_to_vrm_on_both_viseme_csvs(self):
        for name in ('viseme_demo_frames.csv', 'viseme_talk_frames.csv'):
            with self.subTest(name):
                self.check(self.translators['visemes_to_vrm'], self.route('visemes_to_vrm'),
                           self.frames('visemes_to_vrm', name), REFUSED['visemes_to_vrm', name])

    def arkit_frames(self):
        """The ARKit frames of case 1 that have all 52 outputs: Translator raises KeyError on a partial frame."""
        if self.complete is None:
            frames = []
            for name in ('fb2_demo_frames.csv', 'fb2_expression_frames.csv'):
                results = self.translators['fb2_to_arkit'].translate(self.frames('fb2_to_arkit', name))
                frames += [{'time': r['time'], 'segment': r['segment'], 'values': r['values'], 'flags': {}}
                           for r in results if len(r['values']) == 52]
            type(self).complete = frames
        self.assertEqual(len(self.complete), 425 + 221)
        return self.complete

    def test_4_arkit_to_fb2_on_the_complete_arkit_frames(self):
        self.check(self.translators['arkit_to_fb2'], self.route('arkit_to_fb2'), self.arkit_frames(), {})

    def test_5_arkit_to_vrcft_ue_on_the_complete_arkit_frames(self):
        translator = rcef_translate.Translator('arkit.coefficient', 'vrcft.artist.base', ['arkit.to_vrcft_artist'],
                                               'arkit.coefficient.', '', pack=self.pack)
        route = rcef_route.Route('arkit.coefficient', 'vrcft.artist.base', pack=self.pack,
                                 maps=['arkit.to_vrcft_artist'])
        self.assertEqual((len(translator.inputs), len(translator.outputs)), (52, 68))
        self.assertEqual(route.outputs, translator.outputs)
        self.check(translator, route, self.arkit_frames(), {})

    def test_a_planted_fault_in_the_runner_is_found(self):
        translator = self.translators['fb2_to_arkit']
        frames = self.frames('fb2_to_arkit', 'fb2_demo_frames.csv')
        expected = translator.translate(frames)

        class IgnoresFlags(rcef_route.Route):
            def valid(self, sid, flags):
                return True
        faulty = IgnoresFlags(*PROFILES['fb2_to_arkit'], pack=self.pack, maps=list(translator.mappings))
        self.assertNotEqual(differences(translator, expected, faulty.translate(frames)), [])

    def test_a_planted_fault_in_one_rule_is_found(self):
        document = json.loads(FIXTURE.read_text(encoding='utf-8'))
        rule = next(r for m in document['mappings'] if m['id'] == 'fb2.to_arkit' for r in m['rules']
                    if r['operator']['id'] == 'affine')
        rule['operator']['scale'] = 0.5
        changed = rcef_translate.load_pack(document)
        translator = self.translators['fb2_to_arkit']
        route = rcef_route.Route(*PROFILES['fb2_to_arkit'], pack=changed, maps=list(translator.mappings))
        frames = self.frames('fb2_to_arkit', 'fb2_demo_frames.csv')
        self.assertNotEqual(differences(translator, translator.translate(frames), route.translate(frames)), [])

    def test_one_hop_refuses_a_frame_with_a_missing_input(self):
        route = self.route('arkit_to_fb2')
        frame = dict(self.arkit_frames()[0])
        frame['values'] = {k: v for k, v in frame['values'].items() if k != 'arkit.coefficient.jawOpen'}
        result, = route.translate([frame])
        self.assertEqual(result['refused'], {'arkit.to_fb2': {'codes': ['E_MISSING_SAMPLE'],
                                                              'refs': ['arkit.coefficient.jawOpen']}})
        self.assertEqual(len(result['values']), 8)
        self.assertEqual(set(result['labels'].values()), {'refused at arkit.to_fb2'})


def synthetic_document():
    """A small pack with one source set, the canonical expression set, a second source and one target set.

    Canonical groups: brow (2), jaw, eye, tongue and cheek. No out-map reads
    tongue, so its in-map must not run; only the second source writes cheek.
    """
    base = json.loads(FIXTURE.read_text(encoding='utf-8'))
    unit = {'min': 0.0, 'max': 1.0}

    def signal(sid, validity=None):
        record = {'id': sid, 'label': sid, 'value_type': 'scalar', 'units': '1', 'domain': unit,
                  'calibration': f'{sid.split(".")[0]}.v1', 'disposition': 'mapped', 'evidence': ['rcef_definitions'],
                  'evidence_status': 'proposed', 'side': 'shared'}
        return {**record, 'validity': validity} if validity else record

    def rule(rid, inputs, output, operator):
        return {'id': rid, 'inputs': inputs, 'outputs': [output], 'operator': operator, 'disposition': 'mapped',
                'mapping_quality': 'approximate', 'evidence_status': 'proposed', 'evidence': ['rcef_definitions'],
                'assumptions': ['synthetic'], 'loss_annotations': [
                    {'category': 'signal', 'effect': 'approximated', 'reason': 'synthetic', 'refs': inputs + [output],
                     'units': '1'}]}

    copy = {'id': 'affine', 'scale': 1.0, 'offset': 0.0}
    src = ['src.brow_l', 'src.brow_r', 'src.jaw', 'src.tongue', 'src.extra']
    canonical = [f'rcef.canonical_expression.{n}' for n in ('brow_left', 'brow_right', 'jaw', 'eye', 'tongue', 'cheek')]
    c = {sid.rsplit('.', 1)[1]: sid for sid in canonical}
    target = ['tgt.brow', 'tgt.jaw', 'tgt.jaw_double', 'tgt.eye', 'tgt.cheek']
    signals = ([signal(s, 'isValid') for s in src] + [signal('src.eye', 'isValid AND isEyeValid')]
               + [signal(s) for s in ['other.cheek'] + canonical + target])
    profiles = [{'id': 'src', 'label': 'source', 'signal_ids': src + ['src.eye']},
                {'id': 'other', 'label': 'second source', 'signal_ids': ['other.cheek']},
                {'id': 'rcef.canonical_expression', 'label': 'canonical', 'signal_ids': canonical},
                {'id': 'tgt', 'label': 'target', 'signal_ids': target}]
    mappings = [
        {'id': 'src_brow.to_rcef', 'rules': [rule('in.brow_l', ['src.brow_l'], c['brow_left'], copy),
                                             rule('in.brow_r', ['src.brow_r'], c['brow_right'], copy)]},
        {'id': 'src_jaw.to_rcef', 'rules': [rule('in.jaw', ['src.jaw'], c['jaw'], copy)]},
        {'id': 'src_eye.to_rcef', 'rules': [rule('in.eye', ['src.eye'], c['eye'], copy)]},
        {'id': 'src_tongue.to_rcef', 'rules': [rule('in.tongue', ['src.tongue'], c['tongue'], copy)]},
        {'id': 'other_cheek.to_rcef', 'rules': [rule('in.cheek', ['other.cheek'], c['cheek'], copy)]},
        {'id': 'rcef_brow.to_tgt', 'rules': [rule('out.brow', [c['brow_left'], c['brow_right']], 'tgt.brow',
                                                  {'id': 'weighted_sum', 'weights': [0.5, 0.5]})]},
        {'id': 'rcef_jaw.to_tgt', 'rules': [rule('out.jaw', [c['jaw']], 'tgt.jaw', copy),
                                            rule('out.jaw_double', [c['jaw']], 'tgt.jaw_double',
                                                 {'id': 'affine', 'scale': 2.0, 'offset': 0.0})]},
        {'id': 'rcef_eye.to_tgt', 'rules': [rule('out.eye', [c['eye']], 'tgt.eye', copy)]},
        {'id': 'rcef_cheek.to_tgt', 'rules': [rule('out.cheek', [c['cheek']], 'tgt.cheek', copy)]},
    ]
    evidence = [e for e in base['evidence'] if e['id'] == 'rcef_definitions']
    return {**{k: base[k] for k in ('schema_version', 'data_version', 'operator_version', 'license')},
            'id': 'synthetic.route', 'signals': signals, 'profiles': profiles, 'mappings': mappings,
            'evidence': evidence}


def synthetic_pack():
    return rcef_translate.load_pack(synthetic_document())


class TwoHop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = rcef_route.Route('src', 'tgt', pack=synthetic_pack())

    def frame(self, flags=None, **values):
        base = {'brow_l': 0.25, 'brow_r': 0.75, 'jaw': 0.25, 'eye': 0.5, 'tongue': 0.0, 'extra': 0.0}
        base.update(values)
        return {'time': 0.0, 'values': {f'src.{k}': v for k, v in base.items() if v is not None},
                'flags': {'isValid': True, 'isEyeValid': True, **(flags or {})}}

    def test_maps_are_found_by_profile_and_unselected_in_maps_are_not_compiled(self):
        self.assertEqual(self.route.in_maps, ['src_brow.to_rcef', 'src_jaw.to_rcef', 'src_eye.to_rcef'])
        self.assertEqual(self.route.out_maps, ['rcef_brow.to_tgt', 'rcef_jaw.to_tgt', 'rcef_eye.to_tgt',
                                               'rcef_cheek.to_tgt'])
        self.assertNotIn('src_tongue.to_rcef', self.route.mappings)
        self.assertNotIn('other_cheek.to_rcef', self.route.mappings)

    def test_values_pass_through_both_hops(self):
        result, = self.route.translate([self.frame()])
        self.assertEqual(result['values'], {'tgt.brow': 0.5, 'tgt.jaw': 0.25, 'tgt.jaw_double': 0.5, 'tgt.eye': 0.5})
        self.assertEqual(result['refused'], {})

    def test_a_group_no_selected_in_map_writes_is_not_available_and_not_a_refusal(self):
        result, = self.route.translate([self.frame()])
        self.assertEqual(result['labels'], {'tgt.cheek': rcef_route.NOT_AVAILABLE})
        self.assertNotIn('rcef_cheek.to_tgt', result['refused'])

    def test_an_invalid_input_refuses_only_its_group_and_labels_the_outputs(self):
        result, = self.route.translate([self.frame({'isEyeValid': False})])
        self.assertEqual(result['refused'], {'src_eye.to_rcef': {'codes': ['E_INVALID_SAMPLE'], 'refs': ['src.eye']}})
        self.assertEqual(result['labels']['tgt.eye'], 'refused upstream at src_eye.to_rcef')
        self.assertEqual(set(result['values']), {'tgt.brow', 'tgt.jaw', 'tgt.jaw_double'})

    def test_bad_values_that_no_selected_in_map_reads_are_never_sent(self):
        result, = self.route.translate([self.frame(tongue=-1.0, extra=5.0)])
        self.assertEqual(result['refused'], {})
        self.assertEqual(result['dropped'], ['src.extra', 'src.tongue'])

    def test_a_missing_input_is_left_out_so_its_in_map_refuses_the_frame(self):
        results = self.route.translate([self.frame(jaw=None), self.frame()])
        self.assertEqual(results[0]['refused'], {'src_jaw.to_rcef': {'codes': ['E_MISSING_SAMPLE'],
                                                                     'refs': ['src.jaw']}})
        self.assertEqual(results[0]['labels']['tgt.jaw'], 'refused upstream at src_jaw.to_rcef')
        self.assertEqual(results[1]['values']['tgt.jaw'], 0.25)

    def test_an_out_map_refusal_is_labelled_with_the_out_map(self):
        results = self.route.translate([self.frame(jaw=0.75), self.frame()])
        self.assertEqual(results[0]['refused'], {'rcef_jaw.to_tgt': {'codes': ['E_DOMAIN'],
                                                                     'refs': ['rules/out.jaw_double']}})
        self.assertEqual(results[0]['labels']['tgt.jaw'], 'refused at rcef_jaw.to_tgt')
        self.assertEqual(results[1]['values']['tgt.jaw_double'], 0.5)

    def test_a_failed_call_with_no_error_diagnostic_stops_instead_of_retrying(self):
        class Report:
            diagnostics = (SimpleNamespace(severity='warning', ref='/samples/0/src.jaw', code='W'),)

            def to_dict(self):
                return {'diagnostics': ['W']}
        failed = SimpleNamespace(ok=False, report=Report())
        with mock.patch.object(rcef_route.msf, 'evaluate_mapping', return_value=failed), \
                self.assertRaises(SystemExit):
            self.route.translate([self.frame()])

    def test_meta_validity_is_never_asserted_for_another_source(self):
        route = copy(self.route)
        route.target = rcef_route.META
        result, = route.translate([self.frame()])
        self.assertEqual(result['notes'], [rcef_route.META_NOT_ASSERTED])


if __name__ == '__main__':
    unittest.main()
