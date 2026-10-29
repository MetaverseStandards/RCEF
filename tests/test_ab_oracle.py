# SPDX-License-Identifier: MIT
"""The A/B oracle (tests/ab_oracle.py) against msf-character-tools on today's direct maps.

The oracle must give the same values, bit for bit, and the same refusals as
msf-character-tools on the A1 baseline for every edge input and for 1,000
random frames per source set, including gaze pairs that break FB2's
exclusivity. On the fixed impulse frames, the outputs it says change must be
the outputs that change in A1.
"""
from copy import deepcopy
import json
from pathlib import Path
import random
import struct
import sys
import unittest

import msf_character_tools as msf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
sys.path.insert(0, str(ROOT / 'scripts'))
import ab_frames  # noqa: E402
import rcef_route  # noqa: E402
import rcef_translate  # noqa: E402

try:
    import ab_oracle
    import test_route_runner
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import ab_oracle, test_route_runner

FIXTURE = ROOT / 'tests/fixtures/baseline-dea1713.pack.json'
MAPS = {'fb2.to_arkit': ('openxr.fb2', 'arkit.coefficient'), 'fb2_gaze.to_arkit': ('openxr.fb2', 'arkit.coefficient'),
        'arkit.to_fb2': ('arkit.coefficient', 'openxr.fb2'), 'arkit_gaze.to_fb2': ('arkit.coefficient', 'openxr.fb2'),
        'arkit.to_vrcft_artist': ('arkit.coefficient', 'vrcft.artist.base'), 'fb2.to_vrm': ('openxr.fb2', 'vrm.preset'),
        'visemes.to_vrm': ('openxr.visemes', 'vrm.preset')}
PAIRS = {'FB2 -> ARKit': ['fb2.to_arkit', 'fb2_gaze.to_arkit'], 'ARKit -> FB2': ['arkit.to_fb2', 'arkit_gaze.to_fb2'],
         'ARKit -> VRCFT UE': ['arkit.to_vrcft_artist'], 'FB2 -> VRM blink': ['fb2.to_vrm'],
         'META -> VRM': ['visemes.to_vrm']}
RANDOM_FRAMES = 1000
ARKIT, FB2 = 'arkit.coefficient.{}', 'openxr.fb2.XR_FACE_EXPRESSION2_{}_FB'


def bits(values):
    return {k: struct.pack('>d', v) for k, v in values.items()}


class OracleMatchesMsf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(FIXTURE.read_text(encoding='utf-8'))
        cls.pack = rcef_translate.load_pack(cls.document)
        cls.oracle = ab_oracle.Oracle(cls.document)
        cls.sources = {p: ab_frames.pinned_source(cls.document, p)
                       for p in ('openxr.fb2', 'arkit.coefficient', 'openxr.visemes')}
        cls.compiled = {}
        for mapping, (source, target) in MAPS.items():
            snapshots = [msf.profile_snapshot(cls.pack, p).value for p in (source, target)]
            cls.compiled[mapping] = msf.compile_mapping(cls.pack, *snapshots, mapping, True).value

    def msf_results(self, mapping, samples):
        """Per sample: (values, []) or (None, sorted (code, ref) pairs), from batched calls."""
        outcome = msf.evaluate_mapping(self.compiled[mapping], samples)
        results = [None] * len(samples)
        if not outcome.ok:
            refused = {}
            for d in outcome.report.diagnostics:
                refused.setdefault(int(d.ref.split('/')[2]), []).append((d.code, d.ref))
            for n, diagnostics in refused.items():
                results[n] = (None, sorted(diagnostics))
            rest = [n for n in range(len(samples)) if n not in refused]
            if rest:
                again = msf.evaluate_mapping(self.compiled[mapping], [samples[n] for n in rest])
                self.assertTrue(again.ok, again.report.to_dict())
                for n, sample in zip(rest, again.value.samples):
                    results[n] = (dict(sample['values']), [])
        else:
            results = [(dict(s['values']), []) for s in outcome.value.samples]
        return results

    def compare(self, mapping, frames):
        source, target = MAPS[mapping]
        required = self.compiled[mapping].required_inputs
        samples = [{'timestamp': 0.0, 'values': {s: f['values'][s] for s in required},
                    'validity': {s: self.oracle.valid(s, f['flags']) for s in required}} for f in frames]
        expected = self.msf_results(mapping, samples)
        mismatches, refused = [], 0
        for n, (sample, (values, diagnostics)) in enumerate(zip(samples, expected)):
            got, got_diagnostics = self.oracle.frame(mapping, source, target, sample['values'], sample['validity'], n)
            refused += values is None
            if (got is None) != (values is None) or got_diagnostics != diagnostics or (
                    got is not None and bits(got) != bits(values)):
                mismatches.append((frames[n]['label'], diagnostics, got_diagnostics))
        self.assertEqual(mismatches[:3], [], f'{mapping}: {len(mismatches)} frames differ')
        return refused

    def test_every_edge_input_on_every_a1_map(self):
        refused = {}
        for mapping, (source, _) in MAPS.items():
            with self.subTest(mapping):
                refused[mapping] = self.compare(mapping, ab_frames.edge_family('edge', self.sources[source]))
        # Products such as 0.5 * 5e-324 underflow, so the edge set is refused somewhere on every map that averages.
        self.assertGreater(refused['fb2.to_arkit'], 0)

    def test_random_frames_on_every_a1_map(self):
        for mapping, (source, _) in MAPS.items():
            with self.subTest(mapping):
                rng = random.Random(f'ab_oracle {mapping}')
                spec = {'name': 'random', 'count': RANDOM_FRAMES, 'range': [0.0, 1.0]}
                self.compare(mapping, ab_frames.uniform_family(spec, self.sources[source], rng))

    def test_gaze_pairs_that_break_exclusivity_keep_only_the_difference(self):
        def look(**values):
            frame = {**dict.fromkeys(self.compiled['arkit_gaze.to_fb2'].required_inputs, 0.0),
                     **{ARKIT.format(k): v for k, v in values.items()}}
            return self.oracle.frame('arkit_gaze.to_fb2', *MAPS['arkit_gaze.to_fb2'], frame, dict.fromkeys(frame, True))
        cases = {(0.3, 0.1): {'EYES_LOOK_RIGHT_L': 0.19999999999999998},
                 (0.1, 0.3): {'EYES_LOOK_LEFT_L': 0.19999999999999996},
                 (0.3, 0.3): {}, (1.0, 1.0): {}, (0.3, 0.0): {'EYES_LOOK_RIGHT_L': 0.3}}
        for (inward, outward), written in cases.items():
            with self.subTest(inward=inward, outward=outward):
                values, diagnostics = look(eyeLookInLeft=inward, eyeLookOutLeft=outward)
                self.assertEqual(diagnostics, [])
                self.assertEqual({k: v for k, v in values.items() if v}, {FB2.format(k): v for k, v in written.items()})
        frames = [f for f in ab_frames.edge_family('edge', self.sources['arkit.coefficient'])
                  if ', ' in f['label']]
        self.assertEqual(len(frames), 4 * 4)
        self.compare('arkit_gaze.to_fb2', frames)


class Refusals(unittest.TestCase):
    """Every refusal the oracle reproduces, against msf-character-tools on the synthetic route pack.

    Codes and references are compared in full, so one check cannot hide
    another: an out-of-range input that the oracle failed to refuse would show
    up as a rule's output E_DOMAIN with a different reference.
    """

    @classmethod
    def setUpClass(cls):
        document = test_route_runner.synthetic_document()
        rule = deepcopy(document['mappings'][1]['rules'][0])
        extra = {'src_big.to_tgt': (['src.brow_l', 'src.brow_r'], 'tgt.big', {'id': 'weighted_sum',
                                                                             'weights': [1e308, 1e308]}),
                 'src_knee.to_tgt': (['src.jaw'], 'tgt.knee', {'id': 'piecewise_linear', 'knots': [
                     [0.0, 1.0], [0.2, 0.68], [0.88, 0.08], [1.0, 0.0]]})}
        for mapping, (inputs, output, operator) in extra.items():
            document['mappings'].append({'id': mapping, 'rules': [{
                **rule, 'id': mapping, 'inputs': inputs, 'outputs': [output], 'operator': operator,
                'loss_annotations': [{**rule['loss_annotations'][0], 'refs': inputs + [output]}]}]})
        tgt = next(p for p in document['profiles'] if p['id'] == 'tgt')
        for sid, domain in (('tgt.big', {}), ('tgt.knee', {'min': 0.0, 'max': 1.0})):
            document['signals'].append({**document['signals'][-1], 'id': sid, 'label': sid, 'domain': domain})
            tgt['signal_ids'].append(sid)
        cls.oracle = ab_oracle.Oracle(document)
        cls.pack = rcef_translate.load_pack(document)

    def check(self, mapping, source, target, values, validity):
        snapshots = [msf.profile_snapshot(self.pack, p).value for p in (source, target)]
        compiled = msf.compile_mapping(self.pack, *snapshots, mapping, True).value
        outcome = msf.evaluate_mapping(compiled, [{'timestamp': 0.0, 'values': values, 'validity': validity}])
        expected = (dict(outcome.value.samples[0]['values']), []) if outcome.ok else (
            None, sorted((d.code, d.ref) for d in outcome.report.diagnostics))
        got = self.oracle.frame(mapping, source, target, values, validity)
        self.assertEqual(got[1], expected[1])
        self.assertEqual(got[0] is None, expected[0] is None)
        if got[0] is not None:
            self.assertEqual(bits(got[0]), bits(expected[0]))
        return expected

    def test_each_refusal_and_the_clamp_match_msf(self):
        c = 'rcef.canonical_expression.'
        cases = {
            'cleared flag': ('src_eye.to_rcef', 'src', 'rcef.canonical_expression', {'src.eye': 0.5},
                             {'src.eye': False}, 'E_INVALID_SAMPLE'),
            'missing input': ('src_brow.to_rcef', 'src', 'rcef.canonical_expression', {'src.brow_l': 0.5},
                              {'src.brow_l': True}, 'E_MISSING_SAMPLE'),
            'input above its domain': ('src_jaw.to_rcef', 'src', 'rcef.canonical_expression', {'src.jaw': 1.5},
                                       {'src.jaw': True}, 'E_DOMAIN'),
            'output above its domain': ('rcef_jaw.to_tgt', 'rcef.canonical_expression', 'tgt', {c + 'jaw': 0.75},
                                        {c + 'jaw': True}, 'E_DOMAIN'),
            'out-of-range input of an out-map': ('rcef_jaw.to_tgt', 'rcef.canonical_expression', 'tgt',
                                                 {c + 'jaw': 1.5}, {c + 'jaw': True}, 'E_DOMAIN'),
            'cleared flag and out of range': ('src_eye.to_rcef', 'src', 'rcef.canonical_expression',
                                              {'src.eye': 1.5}, {'src.eye': False}, 'E_DOMAIN'),
            'sum overflows': ('src_big.to_tgt', 'src', 'tgt', {'src.brow_l': 1.0, 'src.brow_r': 1.0},
                              {'src.brow_l': True, 'src.brow_r': True}, 'E_NONFINITE'),
        }
        for name, (mapping, source, target, values, validity, code) in cases.items():
            with self.subTest(name):
                _, diagnostics = self.check(mapping, source, target, values, validity)
                self.assertEqual({d[0] for d in diagnostics}, {code})
        # t rounds to 1 on the segment [0.2, 0.88], so ya + t * (yb - ya) is just below yb until it is clamped.
        values, _ = self.check('src_knee.to_tgt', 'src', 'tgt', {'src.jaw': 0.8799999999999999},
                               {'src.jaw': True})
        self.assertEqual(values, {'tgt.knee': 0.08})

    def test_route_refusals_and_labels_match_the_oracle_route(self):
        route = rcef_route.Route('src', 'tgt', pack=self.pack)
        in_hops = [(m, d) for m, _, d in route.hops if m in route.in_maps]
        out_hops = [(m, s) for m, s, _ in route.hops if m in route.out_maps]
        base = {'src.brow_l': 0.25, 'src.brow_r': 0.75, 'src.jaw': 0.25, 'src.eye': 0.5}
        flags = {'isValid': True, 'isEyeValid': True}
        frames = [(base, {**flags, 'isEyeValid': False}), ({k: v for k, v in base.items() if k != 'src.jaw'}, flags),
                  ({**base, 'src.jaw': 1.5}, flags), ({**base, 'src.jaw': 0.75}, flags),
                  ({**base, 'src.eye': 1.5}, {**flags, 'isEyeValid': False})]
        results = route.translate([{'time': 0.0, 'values': v, 'flags': f} for v, f in frames])
        for (values, frame_flags), result in zip(frames, results):
            expected = self.oracle.route('src', 'tgt', in_hops, out_hops, values, frame_flags)
            self.assertEqual(result['refused'], expected['refused'])
            self.assertEqual(result['labels'], expected['labels'])
            self.assertEqual(bits(result['values']), bits(expected['values']))
        self.assertEqual(results[2]['refused'], {'src_jaw.to_rcef': {'codes': ['E_DOMAIN'], 'refs': ['src.jaw']}})


class ImpulseLinks(unittest.TestCase):
    """O's changed-output sets on the impulse frames equal A1's, run through Route's one-hop mode."""

    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(FIXTURE.read_text(encoding='utf-8'))
        cls.pack = rcef_translate.load_pack(cls.document)
        cls.oracle = ab_oracle.Oracle(cls.document)

    def test_changed_outputs_match_on_every_a1_pair(self):
        links = {}
        for pair, maps in PAIRS.items():
            source, target = MAPS[maps[0]]
            frames = ab_frames.impulse_family('impulse', ab_frames.pinned_source(self.document, source))
            route = rcef_route.Route(source, target, pack=self.pack, maps=maps)
            actual = route.translate([{**f, 'time': 0.0} for f in frames])
            expected = [self.oracle.route(source, target, [], [(m, None) for m in maps], f['values'], f['flags'])
                        for f in frames]
            with self.subTest(pair):
                for frame, a, e in zip(frames, actual, expected):
                    self.assertEqual(bits(a['values']), bits(e['values']), frame['label'])
                    self.assertEqual(a['refused'], e['refused'], frame['label'])
                for frame, a in zip(frames[1:], actual[1:]):
                    links[pair, frame['label']] = ab_oracle.changed(actual[0], a)
                    self.assertEqual(links[pair, frame['label']], ab_oracle.changed(expected[0], self.oracle.route(
                        source, target, [], [(m, None) for m in maps], frame['values'], frame['flags'])))
        # The weight-linked LOOK_RIGHT_L stays 0: eyeLookOutLeft enters its knots on the flat side.
        self.assertEqual(links['ARKit -> FB2', f'{ARKIT.format("eyeLookOutLeft")} 1.0'],
                         {FB2.format('EYES_LOOK_LEFT_L')})


if __name__ == '__main__':
    unittest.main()
