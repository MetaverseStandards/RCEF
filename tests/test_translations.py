# SPDX-License-Identifier: MIT
"""Cross-provider translations through the canonical sets, checked against expectations derived from public sources.

The expected values come from tests/fixtures/fb2_goldens.json, which
scripts/derive_fb2_goldens.py derives from the pinned Godot, VRCFT, META and
VRM sources without reading RCEF's mapping data. Each translation runs as the
examples run it: examples/rcef_route.py's Route, source -> canonical -> target.
A mutation changes the maps of one hop: the in-maps (source -> canonical) or
the out-maps (canonical -> target).
"""
from copy import deepcopy
import csv
from functools import cache
import json
import os
from pathlib import Path
import re
import sys
import unittest

import msf_character_tools as msf

try:
    import shared_pack
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import shared_pack

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import rcef_frames  # noqa: E402
import rcef_route  # noqa: E402

KIND = {'fb2_to_arkit': ('openxr.fb2', 'arkit.coefficient'), 'visemes_to_vrm': ('openxr.visemes', 'vrm.preset'),
        'arkit_to_fb2': ('arkit.coefficient', 'openxr.fb2'), 'arkit_to_ue': ('arkit.coefficient', 'vrcft.artist.base'),
        'fb2_to_vrm': ('openxr.fb2', 'vrm.preset')}
FLAGS = {'isValid': True, 'isEyeFollowingBlendshapesValid': True}
SIDED = ('Left', 'Right', '_L_FB', '_R_FB')
SLOW = os.environ.get('RCEF_SLOW_TESTS') == '1'


def halve(rules):
    for rule in rules:
        operator = rule['operator']
        if operator['id'] == 'affine':
            operator['scale'] *= 0.5
        elif operator['id'] == 'piecewise_linear':
            operator['knots'] = [[x, y * 0.5] for x, y in operator['knots']]
        else:
            operator['weights'] = [w * 0.5 for w in operator['weights']]


@cache
def frames(kind):
    """The route of `kind` on the shared pack, with its writable outputs and its inputs."""
    return rcef_frames.Frames(*KIND[kind], '', '', pack=shared_pack.pack())


class Translations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = shared_pack.document()
        cls.signals = {s['id']: s for s in cls.document['signals']}
        cls.goldens = json.loads((ROOT / 'tests/fixtures/fb2_goldens.json').read_text())

    def rules(self, mapping):
        return next(m['rules'] for m in self.document['mappings'] if m['id'] == mapping)

    def part(self, mapping, group):
        """The rules of a map that read or write a canonical signal of one group (a netting step counts)."""
        def touches(rule):
            return any(self.signals[s].get('metadata', {}).get('group') == group for s in rule['inputs'] + rule['outputs']
                       if s.startswith('rcef.canonical_expression.'))
        rules = self.rules(mapping)
        steps = {r['outputs'][0] for r in rules if touches(r)}
        return [r for r in rules if touches(r) or set(r['inputs']) & steps]

    def hop(self, kind, hop):
        """The in-maps of the route, or the out-maps that the source can feed (those that write its outputs)."""
        route = frames(kind).route
        if hop == 'in':
            return route.in_maps
        return [m for m in route.out_maps if any(all(i in route.writer for i in route.mappings[m].output_inputs[o])
                                                 for o in route.mappings[m].output_ids)]

    def inputs(self, kind):
        return frames(kind).inputs

    def outputs(self, kind):
        return set(frames(kind).outputs)

    def evaluate(self, kind, values_list, translator=None):
        """Output values for each frame; a frame holds every input of the route, zero unless given.

        msf-character-tools rechecks the whole pack on every call, so the frames, which are
        independent, go through Route together.
        """
        zero = dict.fromkeys(self.inputs(kind), 0.0)
        for values in values_list:
            self.assertLessEqual(set(values), set(zero))
        results = (translator or frames(kind)).route.translate(
            [{'time': 0.0, 'values': {**zero, **values}, 'flags': FLAGS} for values in values_list])
        for result in results:
            self.assertEqual(result['refused'], {})
        return [result['values'] for result in results]

    def test_fb2_rules_match_source_derived_vectors(self):
        everything = [c for c in self.goldens['cases'] if c['mapping_kind'] == 'fb2_to_arkit']
        cases = [c for c in everything if len(c['expected']) == 1]  # the whole frames are checked below
        for case in cases:
            self.assertLessEqual(set(case['inputs']), self.inputs('fb2_to_arkit'),
                                 f'RCEF and the sources use different inputs ({case["sources"]})')
        checked = set()
        for case, values in zip(cases, self.evaluate('fb2_to_arkit', [c['inputs'] for c in cases])):
            (target, expected), = case['expected'].items()
            with self.subTest(target=target, inputs=case['inputs']):
                self.assertEqual(values[target], expected, case['sources'])
                checked.add(target)
        expected = {o for c in everything for o in c['expected']}
        self.assertEqual(checked, expected, 'every coefficient the sources route needs a rule, and only those')
        self.assertEqual(self.outputs('fb2_to_arkit'), expected)

    def whole_frames(self, kind):
        """The golden frames that set every input at once, each to its own value."""
        frames_ = [c for c in self.goldens['cases'] if c['mapping_kind'] == kind and len(c['inputs']) > 4
                   or c['mapping_kind'] == kind == 'fb2_to_vrm']
        self.assertEqual(len(frames_), 2, kind)
        return frames_

    def check_whole_frames(self, kind, translator=None):
        """Per output: True if it matches the golden value in every whole frame."""
        frames_ = self.whole_frames(kind)
        inputs = self.inputs(kind)
        results = self.evaluate(kind, [{k: v for k, v in f['inputs'].items() if k in inputs} for f in frames_],
                                translator)
        matches = {}
        for frame, values in zip(frames_, results):
            for output in self.outputs(kind):
                matches[output] = matches.get(output, True) and values.get(output) == frame['expected'][output]
        return matches

    def test_whole_frames_match_the_sources(self):
        for kind in KIND:
            if kind == 'visemes_to_vrm':
                continue
            with self.subTest(kind):
                matches = self.check_whole_frames(kind)
                expected = set(self.whole_frames(kind)[0]['expected'])
                self.assertEqual(set(matches), expected)
                self.assertEqual([o for o, ok in matches.items() if not ok], [])

    def changed_copy(self, kind, change, hop='out', only=None):
        """The route of `kind` on a small copy of the pack in which `change` has edited the rules of one hop (or of
        the map `only`). The other maps keep their compiled form from the shared pack."""
        route = frames(kind).route
        changed = [only] if only else self.hop(kind, hop)
        document = shared_pack.cut(self.document, route.in_maps + route.out_maps, [KIND[kind][0]])
        document['mappings'] = deepcopy(document['mappings'])
        for mapping in document['mappings']:
            if mapping['id'] in changed:
                change(mapping['rules'])
        pack = rcef_frames.load_pack(document)
        kept = {m: c for m, c in route.mappings.items() if m not in changed}
        return rcef_frames.Frames(*KIND[kind], '', '', pack=pack, compiled=kept)

    def test_halving_every_rule_changes_every_output(self):
        # Each mapping writes one output, and only the gaze splits read another
        # mapping's output (one difference each). So halving all the mappings of a hop
        # at once and checking each output stands in for halving one at a time. The
        # slow tier also halves them one at a time.
        for kind in KIND:
            if kind == 'visemes_to_vrm':
                continue
            for hop in ('in', 'out'):
                with self.subTest(kind=kind, hop=hop):
                    matches = self.check_whole_frames(kind, self.changed_copy(kind, halve, hop))
                    self.assertEqual([o for o, ok in matches.items() if ok], [])

    @unittest.skipUnless(SLOW, 'slow tier: set RCEF_SLOW_TESTS=1')
    def test_halving_any_one_rule_changes_its_output_and_no_other(self):
        for kind in KIND:
            if kind == 'visemes_to_vrm':
                continue
            outputs = self.outputs(kind)
            out_maps = self.hop(kind, 'out')
            for hop in ('in', 'out'):
                for mapping in self.hop(kind, hop):
                    for rule in self.rules(mapping):
                        with self.subTest(rule=rule['id']):
                            def change(rules, target=rule['id']):
                                halve([r for r in rules if r['id'] == target])
                            matches = self.check_whole_frames(kind, self.changed_copy(kind, change, only=mapping))
                            failing = {o for o, ok in matches.items() if not ok}
                            # A changed value shows in the target outputs computed from it.
                            reached = {o for m in (out_maps if hop == 'in' else [mapping]) for i in rule['outputs']
                                       for o in rcef_route.reaches(self.rules(m), i)} | set(rule['outputs'])
                            if hop == 'out' or not reached & outputs:
                                # A part of the in-map that the target does not read changes nothing.
                                self.assertEqual(sorted(failing), sorted(reached & outputs))
                            else:
                                # A gaze split keeps only the larger of two directions, so a halved
                                # direction shows only on the side where it is the larger one.
                                # Each difference is split into a pair of opposing FB2 directions.
                                net = self.part('rcef_expression.to_fb2', 'gaze')
                                pairs = [sorted(o for r in net if r['inputs'] == d['outputs'] for o in r['outputs'])
                                         for d in net if d['outputs'][0].startswith('rcef.intermediate.')]
                                self.assertTrue(failing)
                                self.assertLessEqual(failing, reached & outputs)
                                for pair in pairs:
                                    if set(pair) <= reached:
                                        self.assertEqual(len(set(pair) & failing), 1, pair)
                                self.assertLessEqual((reached & outputs) - failing, {o for p in pairs for o in p})

    def test_swapping_every_left_and_right_rule_changes_both_outputs(self):
        def side_free(sid):
            return re.sub(r'(Left|Right)$|_[LR](?=[TB]?_FB$)|_(LEFT|RIGHT)(?=_FB$)', '#', sid)

        def swap(rules):
            by_key = {}
            for rule in rules:
                by_key.setdefault(side_free(rule['outputs'][0]), []).append(rule)
            for pair in by_key.values():
                if len(pair) == 2:
                    pair[0]['inputs'], pair[1]['inputs'] = pair[1]['inputs'], pair[0]['inputs']
        for kind in KIND:
            if kind == 'visemes_to_vrm':
                continue
            with self.subTest(kind):
                # The source inputs behind each canonical signal, through the in-maps.
                behind = {r['outputs'][0]: r['inputs'] for m in self.hop(kind, 'in') for r in self.rules(m)}
                swapped = set()
                for mapping in self.hop(kind, 'out'):
                    pairs = {}
                    for rule in self.rules(mapping):
                        pairs.setdefault(side_free(rule['outputs'][0]), []).append(rule)
                    # A copied composite feeds both sides from one source input; swapping changes nothing there.
                    swapped |= {r['outputs'][0] for pair in pairs.values() if len(pair) == 2
                                and [behind.get(i, [i]) for i in pair[0]['inputs']]
                                != [behind.get(i, [i]) for i in pair[1]['inputs']] for r in pair}
                swapped &= self.outputs(kind)
                self.assertTrue(swapped)
                matches = self.check_whole_frames(kind, self.changed_copy(kind, swap))
                self.assertEqual(sorted(o for o in swapped if matches[o]), [])

    def test_swapping_every_left_and_right_in_map_rule_changes_what_is_computed_from_it(self):
        # From ARKit, the in-maps copy each sided coefficient to its canonical side; swapping the inputs of each
        # left/right pair must change every target output computed from a swapped canonical signal, and no other.
        def swap(rules):
            pairs = {}
            for rule in rules:
                pairs.setdefault(re.sub(r'_(left|right)$', '#', rule['outputs'][0]), []).append(rule)
            for pair in pairs.values():
                if len(pair) == 2:
                    pair[0]['inputs'], pair[1]['inputs'] = pair[1]['inputs'], pair[0]['inputs']
        for kind in ('arkit_to_fb2', 'arkit_to_ue'):
            with self.subTest(kind):
                swapped = set()
                for mapping in self.hop(kind, 'in'):
                    pairs = {}
                    for rule in self.rules(mapping):
                        pairs.setdefault(re.sub(r'_(left|right)$', '#', rule['outputs'][0]), []).append(rule)
                    # A fan-out feeds both sides from one coefficient; swapping changes nothing there.
                    swapped |= {r['outputs'][0] for pair in pairs.values() if len(pair) == 2
                                and pair[0]['inputs'] != pair[1]['inputs'] for r in pair}
                self.assertTrue(swapped)
                expected = {o for m in self.hop(kind, 'out') for c in swapped
                            for o in rcef_route.reaches(self.rules(m), c)} & self.outputs(kind)
                matches = self.check_whole_frames(kind, self.changed_copy(kind, swap, 'in'))
                self.assertEqual(sorted(o for o, ok in matches.items() if not ok), sorted(expected))

    def test_fb2_to_arkit_after_arkit_to_fb2_returns_every_coefficient(self):
        for frame in self.whole_frames('arkit_to_fb2'):
            fb2, = self.evaluate('arkit_to_fb2', [frame['inputs']])
            arkit, = self.evaluate('fb2_to_arkit', [{k: v for k, v in fb2.items() if k in self.inputs('fb2_to_arkit')}])
            self.assertEqual(arkit, frame['inputs'])

    def test_inverse_gaze_never_sets_both_opposing_fb2_directions(self):
        # FB2 allows only one of two opposing gaze directions to be non-zero
        # (xr_fb2 lines 648-649). Each pair comes from one signed difference split
        # into its two sides, so when ARKit sets both directions only the net is kept.
        fb2 = 'openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_{}_{}_FB'.format
        ak = 'arkit.coefficient.eyeLook{}{}'.format
        pairs = [(ak('In', 'Left'), ak('Out', 'Left'), fb2('RIGHT', 'L'), fb2('LEFT', 'L')),
                 (ak('In', 'Right'), ak('Out', 'Right'), fb2('LEFT', 'R'), fb2('RIGHT', 'R')),
                 (ak('Up', 'Left'), ak('Down', 'Left'), fb2('UP', 'L'), fb2('DOWN', 'L')),
                 (ak('Up', 'Right'), ak('Down', 'Right'), fb2('UP', 'R'), fb2('DOWN', 'R'))]
        steps = [k / 8 for k in range(9)]
        frames_ = [{a: x, b: y} for a, b, _, _ in pairs for x in steps for y in steps]
        for frame, values in zip(frames_, self.evaluate('arkit_to_fb2', frames_)):
            for a, b, toward_a, toward_b in pairs:
                if a in frame:
                    with self.subTest(frame=frame):
                        self.assertFalse(values[toward_a] and values[toward_b])
                        self.assertEqual((values[toward_a], values[toward_b]),
                                         (max(frame[a] - frame[b], 0.0), max(frame[b] - frame[a], 0.0)))
        gaze_rules = self.part('rcef_expression.to_fb2', 'gaze')
        self.assertEqual(len(gaze_rules), 12)
        for rule in gaze_rules:
            with self.subTest(rule['id']):
                self.assertTrue(any('only their difference is kept' in loss['reason']
                                    for loss in rule['loss_annotations']))
        gaze, face = (set(rcef_route.map_ends(self.part('arkit.to_rcef_expression', g))[0]) for g in ('gaze', 'face'))
        self.assertTrue(gaze and face)
        self.assertFalse(gaze & face)

    def test_vrcft_composites_of_the_copied_parts_return_the_arkit_value(self):
        # VRCFT's BrowDown is 0.75 BrowLowerer + 0.25 BrowPinch and its MouthSmile 0.8
        # CornerPull + 0.2 CornerSlant; its other blended shapes are means of their parts.
        frame = self.whole_frames('arkit_to_ue')[0]
        values, = self.evaluate('arkit_to_ue', [frame['inputs']])
        ue = 'vrcft.artist.base.{}'.format
        for side in ('Left', 'Right'):
            down = 0.75 * values[ue(f'BrowLowerer{side}')] + 0.25 * values[ue(f'BrowPinch{side}')]
            smile = 0.8 * values[ue(f'MouthCornerPull{side}')] + 0.2 * values[ue(f'MouthCornerSlant{side}')]
            self.assertAlmostEqual(down, frame['inputs'][f'arkit.coefficient.browDown{side}'], places=12)
            self.assertAlmostEqual(smile, frame['inputs'][f'arkit.coefficient.mouthSmile{side}'], places=12)
        funnel = sum(values[ue(f'LipFunnel{p}')] for p in ('UpperLeft', 'UpperRight', 'LowerLeft', 'LowerRight')) / 4
        self.assertEqual(funnel, frame['inputs']['arkit.coefficient.mouthFunnel'])

    def test_fb2_to_vrm_drives_each_blink_side_but_not_both_eyes_blink(self):
        # A VRM model may bind blink as well as blinkLeft and blinkRight; writing all
        # three would close the eyes twice over.
        inputs = sorted(self.inputs('fb2_to_vrm'))
        driven = {i.split('EXPRESSION2_')[1]: [o for o, v in values.items() if v]
                  for i, values in zip(inputs, self.evaluate('fb2_to_vrm', [{i: 0.5} for i in inputs]))}
        self.assertEqual(driven, {'EYES_CLOSED_L_FB': ['vrm.preset.blinkLeft'],
                                  'EYES_CLOSED_R_FB': ['vrm.preset.blinkRight']})
        self.assertEqual(self.outputs('fb2_to_vrm'), {'vrm.preset.blinkLeft', 'vrm.preset.blinkRight'})

    def counterparts(self, rule, rules, profile):
        """The signals of `profile` that a hop rule names: its own, or else those its canonical signals align with.

        A split of a computed difference names the canonical signals of the difference: the first input on the
        rising side, the second on the falling side.
        """
        signals = [s for s in rule['inputs'] + rule['outputs'] if s.startswith(profile + '.')]
        if signals:
            return {s[len(profile) + 1:] for s in signals}
        canonical = [s for s in rule['inputs'] + rule['outputs'] if s.startswith('rcef.canonical_expression.')]
        if not canonical:
            maker = next(r for r in rules if r['outputs'] == rule['inputs'])
            rising = rule['operator']['knots'][-1][1] > rule['operator']['knots'][0][1]
            canonical = [maker['inputs'][0 if rising else 1]]
        return {n for s in canonical for n in self.signals[s]['metadata']['aligned_names'].get(profile, [])}

    def test_vrcft_tables_are_cited_only_where_they_name_the_rules_own_signals(self):
        # VRCFT's Movement table writes some FB names that OpenXR does not define
        # (EYES_SQUINT_R on the LID_TIGHTENER_L row) or misspells them; such a row is
        # not evidence, and without it VRCFT's ARKit table does not reach FB2 either.
        # A hop names its FB2 <-> ARKit evidence in a transfer clause; the VRCFT tables
        # it lists there must name the FB2 and ARKit signals the hop stands for.
        labels = self.goldens['vrcft_labels']
        arkit_names = {n[0].lower() + n[1:] for n in labels['vrcft_docs_arkit']}
        with (ROOT / 'tests/fixtures/godot_fb2_rules.csv').open(encoding='utf-8', newline='') as handle:
            derived = {r['arkit']: r['sources'] + ';' + r['second_source_lines'] for r in csv.DictReader(handle)}
        clause = re.compile(r'correspondence evidence is (?:FB2↔ARKit|ARKit↔FB2) \(([^)]*)\)')
        cited = set()
        for kind in ('fb2_to_arkit', 'arkit_to_fb2'):
            for mapping in self.hop(kind, 'in') + self.hop(kind, 'out'):
                rules = self.rules(mapping)
                for rule in rules:
                    evidence = {e for a in rule['assumptions'] for m in clause.finditer(a) for e in m[1].split(', ')}
                    self.assertLessEqual(evidence, set(rule['evidence']), rule['id'])
                    if not evidence & {'vrcft_docs_movement', 'vrcft_docs_arkit'}:
                        continue
                    fb2 = {re.sub(r'^XR_FACE_EXPRESSION2_|_FB$', '', n)
                           for n in self.counterparts(rule, rules, 'openxr.fb2')}
                    arkit = self.counterparts(rule, rules, 'arkit.coefficient')
                    with self.subTest(rule=rule['id']):
                        self.assertTrue(fb2 and arkit)
                        if 'vrcft_docs_movement' in evidence:
                            cited.add('vrcft_docs_movement')
                            self.assertLessEqual(fb2, set(labels['vrcft_docs_movement']))
                        if 'vrcft_docs_arkit' in evidence:
                            cited.add('vrcft_docs_arkit')
                            arkit, = arkit
                            self.assertIn(arkit, arkit_names)
                            self.assertIn('vrcft_docs_arkit:', derived[arkit], 'the derivation does not count this row')
        self.assertEqual(cited, {'vrcft_docs_movement', 'vrcft_docs_arkit'})

    def test_viseme_rules_match_source_derived_vectors_and_drop_consonants(self):
        case, = (c for c in self.goldens['cases'] if c['mapping_kind'] == 'visemes_to_vrm')
        result, = frames('visemes_to_vrm').route.translate([{'time': 0.0, 'values': case['inputs'], 'flags': FLAGS}])
        self.assertEqual(result['refused'], {})
        dropped = sum(case['inputs'][s] for s in result['dropped'])
        self.assertEqual(sum(case['inputs'].values()), 1.0)  # a valid META frame
        self.assertGreater(dropped, 0.0)
        self.assertEqual(dict(result['values']), case['expected'])
        self.assertEqual(sum(result['values'].values()) + dropped, 1.0, 'the probability lost is the consonant mass')

    def test_averaged_pairs_lose_exactly_half_the_difference(self):
        route = frames('fb2_to_arkit').route
        averaged = {r['outputs'][0]: (m, r) for m in route.out_maps for r in self.rules(m)
                    if r['operator']['id'] == 'weighted_sum'}
        self.assertEqual(sorted(averaged),
                         [f'arkit.coefficient.{n}' for n in ('browInnerUp', 'cheekPuff', 'mouthFunnel', 'mouthPucker',
                                                             'mouthRollLower', 'mouthRollUpper')])
        funnel, = (r for _, r in averaged.values() if len(r['inputs']) == 4)
        self.assertEqual(funnel['operator']['weights'], [0.25] * 4)
        # The FB2 channel that each canonical input copies.
        source = {r['outputs'][0]: r['inputs'] for m in route.in_maps for r in self.rules(m)}
        levels = (0.0, 0.25, 0.5, 0.75, 1.0)
        for output, (mapping, rule) in averaged.items():
            if len(rule['inputs']) != 2:
                continue
            (left,), (right,) = (source[i] for i in rule['inputs'])
            pairs = [(a, b) for a in levels for b in levels]
            results = self.evaluate('fb2_to_arkit', [{left: a, right: b} for a, b in pairs])
            for (a, b), values in zip(pairs, results):
                with self.subTest(output=output, left=a, right=b):
                    # Driving both halves with the one value misses each by |L - R| / 2.
                    self.assertEqual(abs(values[output] - a), abs(a - b) / 2)
                    self.assertEqual(abs(values[output] - b), abs(a - b) / 2)
            losses = [loss.to_dict() for loss in route.mappings[mapping].losses]
            self.assertTrue(any(loss['reason'] == 'asymmetry irrecoverable'
                                and set(loss['refs']) == {*rule['inputs'], output} for loss in losses), output)

    def test_face_valid_gaze_invalid_frame_keeps_face_outputs(self):
        # FB2 may report the face valid while eye following is not; the eight gaze
        # weights are then zero and their validity false.
        route = frames('fb2_to_arkit').route
        gaze = set(rcef_route.map_ends(self.part('fb2.to_rcef_expression', 'gaze'))[0])
        face = self.inputs('fb2_to_arkit') - gaze
        self.assertTrue(gaze and face)
        values = {**dict.fromkeys(face, 0.5), **dict.fromkeys(gaze, 0.0)}
        result, = route.translate([{'time': 0.0, 'values': values,
                                    'flags': {'isValid': True, 'isEyeFollowingBlendshapesValid': False}}])
        gaze_outputs = set(rcef_route.map_ends(self.part('rcef_expression.to_arkit', 'gaze'))[1])
        self.assertEqual(set(result['values']), self.outputs('fb2_to_arkit') - gaze_outputs)
        self.assertEqual(result['values']['arkit.coefficient.eyeBlinkLeft'], 0.5)
        self.assertEqual({m: r['codes'] for m, r in result['refused'].items()},
                         {'fb2.to_rcef_expression': ['E_INVALID_SAMPLE']})
        self.assertEqual(result['labels'], dict.fromkeys(gaze_outputs, 'refused upstream at fb2.to_rcef_expression'))
        # Whole-map evaluation refuses the whole frame for one invalid input; partial evaluation, which Route uses,
        # refuses only the outputs that read the invalid inputs.
        compiled = route.mappings['fb2.to_rcef_expression']
        given = {s: values.get(s, 0.0) for s in compiled.required_inputs}
        sample = {'timestamp': 0.0, 'values': given, 'validity': {s: s not in gaze for s in given}}
        outcome = msf.evaluate_mapping(compiled, [sample])
        self.assertIsNone(outcome.value)
        self.assertEqual({d.code for d in outcome.report.diagnostics}, {'E_INVALID_SAMPLE'})
        self.assertEqual({d.ref.rsplit('/', 1)[-1] for d in outcome.report.diagnostics}, gaze)
        partial = msf.evaluate_mapping(compiled, [sample], partial=True)
        refused = {r['output'] for r in partial.value.refusals}
        self.assertEqual(refused, {o for o in compiled.output_ids if set(compiled.output_inputs[o]) & gaze})
        self.assertEqual(len(refused), 8)
        self.assertEqual(set(partial.value.samples[0]['values']), set(compiled.output_ids) - refused)

    def hop_maps(self):
        """Every map of every route here, with its source and target profile."""
        return {m: (s, t) for kind in KIND for m, s, t in frames(kind).route.hops}

    def test_translations_need_the_approximation_opt_in(self):
        for mapping, (source, target) in self.hop_maps().items():
            with self.subTest(mapping=mapping):
                result = msf.compile_mapping(shared_pack.pack(), shared_pack.snapshot(source),
                                             shared_pack.snapshot(target), mapping)
                self.assertIsNone(result.value)
                self.assertIn('E_APPROXIMATION', {d.code for d in result.report.diagnostics})

    def test_every_rule_is_proposed_with_two_sources_assumptions_and_losses(self):
        for mapping in self.hop_maps():
            rules = self.rules(mapping)
            for rule in rules:
                with self.subTest(rule=rule['id']):
                    self.assertEqual((rule['evidence_status'], rule['mapping_quality'], rule['disposition']),
                                     ('proposed', 'approximate', 'mapped'))
                    self.assertGreaterEqual(len(set(rule['evidence'])), 2)
                    self.assertTrue(rule['assumptions'])
                    self.assertTrue(rule['loss_annotations'])
                    if any(s in sid for sid in (*rule['inputs'], *rule['outputs']) for s in SIDED):
                        # The side convention is the canonical signal's side field (the subject's own face).
                        makers = [r for r in rules if r['outputs'] == rule['inputs']]
                        canonical = [s for r in [rule, *makers] for s in (*r['inputs'], *r['outputs'])
                                     if s.startswith('rcef.canonical_')]
                        self.assertTrue(canonical)
                        # A shared signal (jaw or mouth shift) names a direction: _left is toward the subject's
                        # own left.
                        sides = [(self.signals[s].get('side'), s.endswith(('_left', '_right'))) for s in canonical]
                        self.assertTrue(all(side in ('left', 'right') or side == 'shared' and suffix
                                            for side, suffix in sides), 'left/right rules state the side convention')


if __name__ == '__main__':
    unittest.main()
