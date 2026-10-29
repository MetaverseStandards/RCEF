# SPDX-License-Identifier: MIT
"""The A/B oracle (tests/ab_oracle.py) against msf-character-tools on today's direct maps.

The oracle must give the same values, bit for bit, and the same refusals as
msf-character-tools on the A1 baseline for every edge input and for 1,000
random frames per source set, including gaze pairs that break FB2's
exclusivity. On the fixed impulse frames, the outputs it says change must be
the outputs that change in A1.
"""
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
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import ab_oracle

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
                spec = {'name': 'random', 'count': RANDOM_FRAMES}
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
                    self.assertEqual(sorted(a['refused']), sorted(e['refused']), frame['label'])
                for frame, a in zip(frames[1:], actual[1:]):
                    links[pair, frame['label']] = ab_oracle.changed(actual[0], a)
                    self.assertEqual(links[pair, frame['label']], ab_oracle.changed(expected[0], self.oracle.route(
                        source, target, [], [(m, None) for m in maps], frame['values'], frame['flags'])))
        # The weight-linked LOOK_RIGHT_L stays 0: eyeLookOutLeft enters its knots on the flat side.
        self.assertEqual(links['ARKit -> FB2', f'{ARKIT.format("eyeLookOutLeft")} 1.0'], {FB2.format('EYES_LOOK_LEFT_L')})


if __name__ == '__main__':
    unittest.main()
