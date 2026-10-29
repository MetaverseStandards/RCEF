# SPDX-License-Identifier: MIT
"""The maps between the canonical expression set and each expression set: structure, losses, evidence, assumptions.

Every translation runs source -> canonical -> target. These tests check the
hop maps against the rules in docs/canonical-set.md and the definitions audit
(docs/canonical-set-audit.md), and against today's direct maps, frozen in
tests/fixtures/baseline-dea1713.pack.json:

- names, directions and groups: one canonical group per map, a whole group
  per in-map;
- sides and direction suffixes agree at both ends of every mapping;
- split losses only on fan-outs and means; the endpoint clause matches the
  operator; the audit loss keys sit exactly on the hops the audit names;
- evidence: each A1 output keeps its evidence on the route (M2c); a withdrawn
  transfer names a loss; the FACS crosswalk is cited on ARKit hops only;
- every assumption and every loss of today's maps has a home on the route (M4b), and a route adds
  only the audit keys that the audit lists for its pair;
- the composed hop weights equal today's weights (M1s);
- which canonical groups other sets could fill (the capability matrix).

The META viseme maps are not in the pack yet. Today's viseme map
(visemes.to_vrm) is therefore left out of the route checks; VISEME_PENDING
counts the assumptions it leaves out; that count becomes 0 when those maps join.
"""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'examples'), str(ROOT / 'tests'), str(ROOT)]
import ab_compare  # noqa: E402
import build_canonical  # noqa: E402
import rcef_route  # noqa: E402
import rcef_translate  # noqa: E402

PREFIX = 'rcef.canonical_expression.'
INTERMEDIATE = 'rcef.intermediate.'
PROFILES = {'arkit': 'arkit.coefficient', 'fb2': 'openxr.fb2', 'vrcft_artist': 'vrcft.artist.base', 'vrm': 'vrm.preset'}
IN_MAP = re.compile(r'^(arkit|fb2|vrcft_artist|vrm)_([a-z_]+)\.to_rcef$')
OUT_MAP = re.compile(r'^rcef_([a-z_]+)\.to_(arkit|fb2|vrcft_artist|vrm)$')
# Mappings per set: (in-maps, out-maps). The FB2 gaze out-map has 4 internal steps.
COUNTS = {'arkit': (60, 52), 'fb2': (60, 64), 'vrcft_artist': (0, 68), 'vrm': (0, 2)}
MAPS = 46
# Pairs of a rule's two ends whose sides may differ although neither is shared. None today.
SIDE_EXCEPTIONS = []
# Operators allowed on a hop: today's operator census, with power-of-two weights.
OPERATORS = [{'id': 'affine', 'scale': 1.0, 'offset': 0.0}, {'id': 'weighted_sum', 'weights': [0.5, 0.5]},
             {'id': 'weighted_sum', 'weights': [0.25, 0.25, 0.25, 0.25]},
             {'id': 'weighted_sum', 'weights': [1.0, -1.0]},
             {'id': 'piecewise_linear', 'knots': [[-1.0, 0.0], [0.0, 0.0], [1.0, 1.0]]},
             {'id': 'piecewise_linear', 'knots': [[-1.0, 1.0], [0.0, 0.0], [1.0, 0.0]]}]
KEYS = {'correspondence', 'endpoints', 'transfer.provider', 'transfer.withdrawn', 'transfer.facs_crosswalk',
        'fan_out.vrcft_ue', 'net.fb2_gaze', 'gaze.fb2_exclusive', 'mean.arkit', 'evidence.vrcft_tables_not_cited',
        'evidence.godot_only_mouth_shift', 'vrm.downstream_effects', 'vrm.side_caveat', 'vrm.definitional_only',
        'lips_toward.jaw_not_compensated'}
A1_PAIRS = {'fb2.to_arkit': 'FB2 -> ARKit', 'fb2_gaze.to_arkit': 'FB2 -> ARKit', 'arkit.to_fb2': 'ARKit -> FB2',
            'arkit_gaze.to_fb2': 'ARKit -> FB2', 'arkit.to_vrcft_artist': 'ARKit -> VRCFT UE',
            'fb2.to_vrm': 'FB2 -> VRM blink'}
VISEME_PAIR = 'META -> VRM'
# Today's assumption templates (docs/canonical-set-audit.md, assumption catalogue): a pattern for each, and the
# hop assumption keys its home needs on the route. None means superseded by the canonical definition.
TEMPLATES = [
    ('a01', r"^ARKit neutral \(0\) and maximum \(1\) are taken to equal the Unified Expressions shape", ['endpoints']),
    ('a02', r"^Both name sides from the subject's own face \(ARKit coefficients are face-relative; Unified", None),
    ('a03', r'^ARKit neutral \(0\) and maximum \(1\) are taken to equal FB2 weight', ['endpoints']),
    ('a04', r"^Both providers name sides from the subject's own face \(ARKit coefficients", None),
    ('a05', r'^FB2 weight 0 \(not active\) and 1 \(fully active\) are taken to equal ARKit', ['endpoints']),
    ('a06', r"^Both providers name sides from the subject's own face \(FB2 describes", None),
    ('a07', r'^FB2 \w+ corresponds to ARKit \w+\.$', ['correspondence', 'transfer']),
    ('a08', r'^ARKit \w+ corresponds to Unified Expressions \w+ \(VRCFaceTracking ARKit table', ['correspondence', 'transfer']),
    ('a09', r'^ARKit \w+ corresponds to FB2 \w+; this is the FB2 -> ARKit rule read back\.$', ['correspondence']),
    ('a10', r'blended Unified Expressions shape; .* computes the blended shape as the mean of these parts', ['fan_out.vrcft_ue']),
    ('a11', r'^ARKit \w+ is one coefficient; FB2 \w+ is set to it', ['endpoints']),
    ('a12', r'^A one-sided split is exactly zero', ['net.fb2_gaze']),
    ('a13', r'blended Unified Expressions shape; .* defines the blended shape as', ['fan_out.vrcft_ue']),
    ('a14', r"^VRCFaceTracking's tables are not cited: .* not an OpenXR name", ['evidence.vrcft_tables_not_cited']),
    ('a15', r'^VRM isBinary and override effects', ['vrm.downstream_effects']),
    ('a16', r'^META viseme \w+ corresponds to VRM preset', None),
    ('a17', r'^META viseme probability', None),
    ('a18', r'^Phoneme-label correspondence only', None),
    ('a19', r'read back, taking \w+ minus \w+ where it is above zero\.$', ['net.fb2_gaze', 'correspondence']),
    ('a20', r'read back, taking how far \w+ minus \w+ is below zero\.$', ['net.fb2_gaze', 'correspondence']),
    ('a21', r'blended Unified Expressions shape; .* Godot builds the blended shape', ['fan_out.vrcft_ue']),
    ('a22', r'are opposing directions of one eye', ['net.fb2_gaze']),
    ('a23', r'^FB2 says only one of two opposing gaze directions', ['gaze.fb2_exclusive']),
    ('a24', r"^FLAGGED: VRCFaceTracking's ARKit table has no", ['evidence.godot_only_mouth_shift']),
    ('a25', r'^ARKit \w+ is one coefficient; it is the mean of FB2 ', ['mean.arkit']),
    ('a26', r"^Both name sides from the subject's own face\. FLAGGED: VRM", ['vrm.side_caveat']),
    ('a27', r'^FB2 \w+ \(lowers the top eyelid', ['correspondence', 'vrm.definitional_only']),
    ('a28', r'^FB2 weight \(0 to 1\) is used directly as the VRM', ['endpoints']),
    ('a29', r'^FLAGGED: only Godot names ARKit \w+ for this channel \(its face-modifier alias\)',
     ['evidence.godot_only_mouth_shift']),
    ('a30', r'^FLAGGED: only Godot names ARKit \w+ for this channel; see', ['evidence.godot_only_mouth_shift']),
    ('a31', r"^VRCFaceTracking's tables are not cited: .* a misspelling", ['evidence.vrcft_tables_not_cited']),
    ('a32', r'is one coefficient for both sides; it is the mean of FB2 .*, as VRCFaceTracking computes', ['mean.arkit']),
    ('a33', r'is one coefficient for both sides; it is the mean of FB2 .*, as the Godot OpenXR vendors plugin computes',
     ['mean.arkit']),
    ('a34', r'^ARKit \w+ is one coefficient; it is the mean of the four quarters', ['mean.arkit']),
    ('a35', r'^FB2 closes the lips regardless of the jaw position', ['lips_toward.jaw_not_compensated']),
]
# a10 on these Unified Expressions parts is superseded: the canonical set holds the parts, so the out-hop copies.
A10_SUPERSEDED = re.compile(r'\.(BrowInnerUp|CheekPuff|LipFunnel|LipSuck)\w+$')
# Where each loss of today's maps lives on the route (docs/canonical-set-audit.md, mapping today's losses to keys):
# a pattern for the loss reason, and the audit keys or the exact non-audit losses the route must hold. None:
# the viseme map's losses, whose route joins with the canonical visemes.
LOSS_HOMES = [
    (r'^provider gain and full-activation pose are not published', ['gain']),
    (r'^Unified Expressions splits this shape into parts', ['split']),
    (r'^FB2 maximum gaze angle is unspecified$', ['fb2_gaze_max_angle_unspecified']),
    (r'^asymmetry unknown: symmetry is invented$', ['asymmetry unknown: symmetry is invented']),
    (r'^FB2 allows only one of two opposing gaze directions', ['netting']),
    (r'^ARKit describes eyelid movement consistent with the gaze; FB2', ['arkit_gaze_eyelid', 'fb2_gaze_rotation']),
    (r'^FB2 describes eye rotation; ARKit describes eyelid', ['fb2_gaze_rotation', 'arkit_gaze_eyelid']),
    (r'^FB2 opposing directions are mutually exclusive', ['fb2_gaze_exclusive']),
    (r'^ARKit and Unified Expressions both describe eyelid', ['arkit_gaze_eyelid', 'vrcft_ue_gaze_no_angle']),
    (r'^asymmetry irrecoverable$', ['asymmetry irrecoverable']),
    (r'^consonant visemes are dropped', None),
    (r'^a viseme probability becomes', None),
    (r'^vowel quality differs', None),
    (r'^both are extension shapes with no stated length$', ['the tongue extension has no stated length']),
    (r'^FB2 also pulls the corner back and laterally', ['arkit_mouthsmile_upward']),
    (r'^an FB2 weight becomes an asset-authored expression weight$',
     ['a canonical value becomes an asset-authored expression weight']),
    (r'^VRM blink \(both eyes\) is left unset', ['same']),
    (r'^a model may mark the preset isBinary', ['same']),
    (r'^jaw-relative versus jaw-independent lip closure$', ['arkit_mouthclose_jaw_unresolved']),
    (r'^FB2 describes upward (lip motion induced by the chin raiser|chin and lower-lip motion)',
     ['arkit_mouthshrug_outward']),
]
# Audit keys that a route may add to today's losses for the same pair (keys added on today's pairs).
ARKIT_ADDED = {'arkit_browdown_outer', 'arkit_eyesquint_face', 'arkit_cheeksquint_cheek', 'arkit_mouthpress_lower_lip',
               'arkit_mouthpucker_compression', 'arkit_mouthstretchright_text_side', 'ict_au33_cheek_blow',
               'ict_au45_blink'}
ADDED = {
    'FB2 -> ARKit': ARKIT_ADDED,
    'ARKit -> FB2': ARKIT_ADDED | {'arkit_mouthsmile_upward', 'arkit_mouthshrug_outward', 'arkit_mouthclose_jaw_unresolved'},
    'ARKit -> VRCFT UE': ARKIT_ADDED | {'arkit_mouthsmile_upward', 'arkit_mouthshrug_outward',
                                        'arkit_mouthclose_jaw_unresolved', 'vrcft_ue_eyesquint_socket',
                                        'vrcft_ue_cheeksquint_cheek', 'vrcft_ue_mouthstretch_down',
                                        'vrcft_ue_mouthclosed_jaw_relative',
                                        'vrcft_ue_mouthlowerdown_direction_unresolved'},
    'FB2 -> VRM blink': {'vrm_blink_side_unresolved'},
}
# The template entries of the viseme map, whose route joins with the canonical visemes.
VISEME_PENDING = 20
# Names in other sets that the capability matrix reads as a canonical name (the planned reading of
# XR_ML_facial_expression's single chin raiser, as for FACS 17).
ALIASES = {'XR_ML_facial_expression': {'CHIN_RAISER': 'CHIN_RAISER_B'}}
CAPABILITY = {
    'FACS': ['face', 'cheek_puff', 'jaw_thrust', 'jaw_sideways', 'blink', 'tongue_out'],
    'FB v1': ['face', 'cheek_puff', 'jaw_thrust', 'jaw_sideways', 'mouth_shift', 'chin_raise_upper_lip', 'blink',
              'gaze'],
    'XR_ANDROID_face_tracking': ['face', 'cheek_puff', 'jaw_thrust', 'jaw_sideways', 'mouth_shift',
                                 'chin_raise_upper_lip', 'blink', 'gaze', 'tongue_out'],
    'XR_ML_facial_expression': ['face', 'blink', 'tongue_out'],
}


def keys_of(rule: dict) -> set[str]:
    return {a.split(':', 1)[0] for a in rule['assumptions']}


def loss_keys(rule: dict, audit_keys) -> set[str]:
    return {l['reason'].split(':', 1)[0] for l in rule['loss_annotations'] if l['reason'].split(':', 1)[0] in audit_keys}


class PivotStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        cls.a1 = json.loads((ROOT / build_canonical.A1_FIXTURE).read_text(encoding='utf-8'))
        cls.signals = {s['id']: s for s in cls.pack['signals']}
        cls.members = {p['id']: set(p['signal_ids']) for p in cls.pack['profiles']}
        cls.docs = build_canonical.read_documents(ROOT)
        cls.hops = []  # (map, direction, set, group, rules)
        for mapping in cls.pack['mappings']:
            if m := IN_MAP.match(mapping['id']):
                cls.hops.append((mapping['id'], 'in', m.group(1), m.group(2), mapping['rules']))
            elif m := OUT_MAP.match(mapping['id']):
                cls.hops.append((mapping['id'], 'out', m.group(2), m.group(1), mapping['rules']))
        cls.group = {sid: s['metadata']['group'] for sid, s in cls.signals.items() if sid.startswith(PREFIX)}
        cls.pairs = ab_compare.b_pairs(cls.pack)
        cls.aligned = build_canonical.Builder(ROOT).aligned
        cls.groups = next(p['metadata']['groups'] for p in cls.pack['profiles'] if p['id'] == 'rcef.canonical_expression')

    def hop_rules(self):
        for map_id, direction, key, group, rules in self.hops:
            for rule in rules:
                yield map_id, direction, key, group, rule

    def canonical(self, rule):
        """The canonical signals a rule reads or writes; a netting step's, through the helper it reads."""
        if rule['operator']['id'] == 'piecewise_linear':
            return [PREFIX + s for s in self.aligned['fb2'][rule['outputs'][0]]]
        return [s for s in rule['inputs'] + rule['outputs'] if s.startswith(PREFIX)]

    def provider(self, key, rule):
        return [s for s in rule['inputs'] + rule['outputs'] if s in self.members[PROFILES[key]]]

    def test_generated_data_is_current(self):
        for path, content in build_canonical.render(ROOT).items():
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_text(encoding='utf-8'), content,
                                 'run scripts/build_canonical.py --write')

    def test_every_map_with_a_canonical_signal_is_a_named_hop(self):
        named = {h[0] for h in self.hops}
        for mapping in self.pack['mappings']:
            if any(s.startswith(PREFIX) for r in mapping['rules'] for s in r['inputs'] + r['outputs']):
                self.assertIn(mapping['id'], named)
        self.assertEqual(len(self.hops), MAPS)
        counts = {key: [0, 0] for key in COUNTS}
        for _, direction, key, _, rules in self.hops:
            counts[key][direction == 'out'] += len(rules)
        self.assertEqual({k: tuple(v) for k, v in counts.items()}, COUNTS)

    def test_each_map_reads_and_writes_one_group(self):
        whole = {}
        for sid, group in self.group.items():
            whole.setdefault(group, set()).add(sid)
        for map_id, direction, key, group, rules in self.hops:
            inputs, outputs = rcef_route.map_ends(rules)
            computed = {o for r in rules for o in r['outputs']} - set(outputs)
            with self.subTest(map=map_id):
                self.assertLessEqual(computed, self.members['rcef.intermediate'])
                if direction == 'in':
                    self.assertLessEqual(set(inputs), self.members[PROFILES[key]])
                    self.assertEqual(set(outputs), whole[group])
                else:
                    self.assertLessEqual(set(inputs), whole[group])
                    self.assertLessEqual(set(outputs), self.members[PROFILES[key]])

    def test_out_maps_read_only_what_every_in_map_of_their_group_writes(self):
        written = {(key, group): set(rcef_route.map_ends(rules)[1])
                   for _, direction, key, group, rules in self.hops if direction == 'in'}
        for map_id, direction, _, group, rules in self.hops:
            if direction != 'out':
                continue
            for (source, g), canonical in written.items():
                if g == group:
                    self.assertLessEqual(set(rcef_route.map_ends(rules)[0]), canonical, (map_id, source))

    def test_hop_fields_operators_and_assumption_keys(self):
        for map_id, _, _, _, rule in self.hop_rules():
            with self.subTest(rule=rule['id']):
                self.assertEqual((rule['disposition'], rule['mapping_quality'], rule['evidence_status']),
                                 ('mapped', 'approximate', 'proposed'))
                self.assertIn(rule['operator'], OPERATORS)
                self.assertGreaterEqual(len(rule['evidence']), 2)
                self.assertEqual(rule['evidence'][-1], 'rcef_canonical_v1')
                self.assertLessEqual(keys_of(rule), KEYS)
                self.assertTrue(rule['loss_annotations'])

    def test_sides_agree_at_both_ends(self):
        for _, _, _, _, rule in self.hop_rules():
            for a in rule['inputs']:
                for b in rule['outputs']:
                    sides = {self.signals[a]['side'], self.signals[b]['side']}
                    if len(sides) > 1 and 'shared' not in sides:
                        self.assertIn((a, b), SIDE_EXCEPTIONS, rule['id'])

    def test_direction_suffixes_keep_their_direction(self):
        for map_id, _, key, _, rule in self.hop_rules():
            for c in self.canonical(rule):
                if self.group[c] not in ('jaw_sideways', 'mouth_shift'):
                    continue
                side = c.rsplit('_', 1)[1]
                other = 'right' if side == 'left' else 'left'
                for sid in self.provider(key, rule):
                    native = sid.rsplit('.', 1)[1].lower()
                    with self.subTest(rule=rule['id'], signal=sid):
                        self.assertIn(side, native)
                        self.assertNotIn(other, native)

    def kind(self, direction, key, rule, rules):
        """in_copy, in_fan, out_copy, out_fan, out_mean, out_net or net_step, from the operator and the fan."""
        output = rule['outputs'][0]
        if output.startswith(INTERMEDIATE):
            return 'net_step'
        if rule['operator']['id'] == 'piecewise_linear':
            return 'out_net'
        if rule['operator']['id'] == 'weighted_sum':
            return 'out_mean'
        readers = [r for r in rules if r['inputs'] == rule['inputs']]
        if len(readers) > 1:
            return f'{direction}_fan'
        return f'{direction}_copy'

    def test_split_losses_only_on_fan_outs_and_means(self):
        audit = self.docs['keys']
        for map_id, direction, key, _, rules in self.hops:
            for rule in rules:
                kind = self.kind(direction, key, rule, rules)
                reasons = [l['reason'] for l in rule['loss_annotations']]
                with self.subTest(rule=rule['id'], kind=kind):
                    self.assertEqual(build_canonical.SYMMETRY in reasons, kind == 'in_fan')
                    self.assertEqual(build_canonical.ASYMMETRY in reasons, kind == 'out_mean')
                    split = f'{build_canonical.SPLIT_KEY}: {audit[build_canonical.SPLIT_KEY]}' in reasons
                    self.assertEqual(split, kind == 'out_fan')
                    self.assertEqual(build_canonical.NETTING in reasons, kind in ('out_net', 'net_step'))

    def test_endpoint_clause_matches_the_operator(self):
        for map_id, direction, key, _, rules in self.hops:
            name = build_canonical.PROVIDERS[key]['name']
            for rule in rules:
                kind = self.kind(direction, key, rule, rules)
                endpoints = [a for a in rule['assumptions'] if a.startswith('endpoints: ')]
                with self.subTest(rule=rule['id'], kind=kind):
                    if kind == 'net_step':
                        self.assertEqual(endpoints, [])
                        self.assertEqual(keys_of(rule), {'net.fb2_gaze', 'gaze.fb2_exclusive'})
                        continue
                    self.assertEqual(len(endpoints), 1)
                    text = endpoints[0]
                    opening = build_canonical.OPENING.format(build_canonical.possessive(name))
                    clause = build_canonical.CLAUSES[kind].format(name=name)
                    self.assertTrue(text.startswith(f'endpoints: {opening}; {clause}'), text)
                    shorts = [c[len(PREFIX):] for c in self.canonical(rule)]
                    differs = any(self.docs['audit'][key][s]['verdict'] != 'same' for s in shorts)
                    self.assertEqual('the endpoints are assumed equal although' in text, differs)

    def test_audit_loss_keys_sit_on_the_hops_the_audit_names(self):
        audit = self.docs['audit']
        for map_id, direction, key, _, rules in self.hops:
            for rule in rules:
                shorts = [c[len(PREFIX):] for c in self.canonical(rule)]
                if rule['outputs'][0].startswith(INTERMEDIATE):
                    shorts = []
                expected = {k for s in shorts for k in audit[key][s]['keys']}
                expected |= {k for s in shorts for k in build_canonical.HOP_KEYS.get((key, direction, self.group[PREFIX + s]), [])}
                if key == 'arkit':
                    expected |= {k for s in shorts for k in self.docs['ict'].get(s, {}).get('keys', [])}
                self.assertEqual(loss_keys(rule, self.docs['keys']), expected, rule['id'])

    def test_hop_loss_keys_are_the_ones_the_audit_gives_a_whole_hop(self):
        owners = {r['Key'].strip('`'): r['Owning hops']
                  for r in build_canonical.table((ROOT / build_canonical.AUDIT_DOC).read_text(encoding='utf-8'),
                                                 '## Loss keys')}
        self.assertEqual(build_canonical.HOP_KEYS, {('fb2', 'in', 'gaze'): ['fb2_gaze_exclusive']})
        self.assertEqual(owners['fb2_gaze_exclusive'], 'FB2 gaze in')
        rules = [r for m, d, k, g, rs in self.hops if (k, d, g) == ('fb2', 'in', 'gaze') for r in rs]
        self.assertEqual(len(rules), 8)
        for rule in rules:
            self.assertIn('fb2_gaze_exclusive', loss_keys(rule, self.docs['keys']))

    def test_each_a1_output_keeps_its_evidence_on_the_route(self):
        for map_id, pair in A1_PAIRS.items():
            with self.subTest(pair=pair):
                counts, failures = ab_compare.m2c(self.a1, self.pack, pair, self.pairs[pair])
                self.assertGreater(counts['outputs'], 0)
                self.assertEqual(failures, [])
        for map_id, _, key, _, rule in self.hop_rules():
            if not rule['outputs'][0].startswith(INTERMEDIATE):
                self.assertEqual(rule['evidence'][:len(build_canonical.PROVIDERS[key]['records'])],
                                 build_canonical.PROVIDERS[key]['records'], rule['id'])

    def test_a_withdrawn_transfer_names_a_loss_on_the_route_of_its_signal(self):
        keys = self.docs['keys']
        on_signal = {}
        for _, _, _, _, rule in self.hop_rules():
            for c in self.canonical(rule):
                on_signal.setdefault(c, set()).update(loss_keys(rule, keys))
        withdrawn = 0
        for _, _, _, _, rule in self.hop_rules():
            for text in rule['assumptions']:
                if not text.startswith('transfer.withdrawn: '):
                    continue
                withdrawn += 1
                named = re.search(r'; see loss(?:es)? (.+)\.$', text).group(1).replace(' and ', ', ').split(', ')
                with self.subTest(rule=rule['id'], text=text):
                    self.assertLessEqual(set(named), set(keys))
                    near = set().union(*(on_signal[c] for c in self.canonical(rule)))
                    self.assertLessEqual(set(named), near)
        self.assertGreater(withdrawn, 0)

    def test_the_facs_crosswalk_is_cited_on_arkit_hops_only(self):
        for map_id, _, key, _, rule in self.hop_rules():
            cites = 'ict_facekit' in rule['evidence']
            texts = [a for a in rule['assumptions'] if 'ict_facekit' in a]
            with self.subTest(rule=rule['id']):
                if key != 'arkit':
                    self.assertFalse(cites)
                    continue
                self.assertEqual(bool(texts), cites)
                gaze = all(self.group[c] == 'gaze' for c in self.canonical(rule))
                for text in texts:
                    self.assertEqual('no FACS transfer claimed' in text, gaze, text)

    def a1_route(self, map_id, rule):
        """The hop rules on the pivot route of one of today's rules."""
        pair = self.pairs[A1_PAIRS[map_id]]
        out_rules = ab_compare.rules_by_output(self.pack, [h[0] for h in pair['out_hops']])
        in_rules = ab_compare.rules_by_output(self.pack, [h[0] for h in pair['in_hops']])
        output = rule['outputs'][0]
        if found := build_canonical.OLD_HELPER.match(output):
            output = build_canonical.new_helper(output)
        rules, leaves = ab_compare.upstream(out_rules, output)
        for leaf in leaves:
            rules += ab_compare.upstream(in_rules, leaf)[0]
        sources = {i for r in rules for i in r['inputs'] if not i.startswith((PREFIX, INTERMEDIATE))}
        if not rule['inputs'][0].startswith(INTERMEDIATE):
            self.assertLessEqual(set(rule['inputs']), sources, rule['id'])
        return rules

    def test_every_assumption_of_today_has_a_home_on_the_route(self):
        documented = {r['ID']: int(r['Strings'])
                      for r in build_canonical.table((ROOT / build_canonical.AUDIT_DOC).read_text(encoding='utf-8'),
                                                     '## Assumption catalogue')}
        found = dict.fromkeys(documented, 0)
        superseded = pending = 0
        records = {k: set(v['records']) for k, v in build_canonical.PROVIDERS.items()}
        for mapping in self.a1['mappings']:
            if mapping['id'] not in build_canonical.A1_MAPS:
                continue
            for rule in mapping['rules']:
                for text in rule['assumptions']:
                    hits = [(t, need) for t, pattern, need in TEMPLATES if re.search(pattern, text)]
                    self.assertEqual(len(hits), 1, text)
                    template, need = hits[0]
                    found[template] += 1
                    if mapping['id'] == 'visemes.to_vrm':
                        pending += 1
                        continue
                    if need is None or (template == 'a10' and A10_SUPERSEDED.search(rule['outputs'][0])):
                        superseded += 1
                        continue
                    present = set()
                    for hop in self.a1_route(mapping['id'], rule):
                        present |= keys_of(hop)
                    present |= {'transfer'} if present & {'transfer.provider', 'transfer.withdrawn'} else set()
                    ends = {build_canonical.provider_of(s) for s in rule['inputs'] + rule['outputs']} - {None}
                    own = set().union(*(records[e] for e in ends))
                    wanted = set(need)
                    if 'transfer' in wanted and not set(rule['evidence']) - own - {'ict_facekit'}:
                        wanted.discard('transfer')
                    with self.subTest(rule=rule['id'], template=template):
                        self.assertLessEqual(wanted, present)
        self.assertEqual(found, documented)
        self.assertEqual(superseded, 178)
        self.assertEqual(pending, VISEME_PENDING)

    def test_every_loss_of_today_has_a_home_on_the_route(self):
        keys = self.docs['keys']
        documented = {r['A1 loss reason'] for r in build_canonical.table(
            (ROOT / build_canonical.AUDIT_DOC).read_text(encoding='utf-8'), "## Mapping today's losses to keys")}
        reasons, pending = set(), 0
        for mapping in self.a1['mappings']:
            if mapping['id'] not in build_canonical.A1_MAPS:
                continue
            for rule in mapping['rules']:
                route = [] if mapping['id'] == 'visemes.to_vrm' else self.a1_route(mapping['id'], rule)
                held = {l['reason'] for hop in route for l in hop['loss_annotations']}
                held_keys = {r.split(':', 1)[0] for r in held} & set(keys)
                covered = set()
                for loss in rule['loss_annotations']:
                    reason = loss['reason']
                    reasons.add(reason)
                    homes = [h for pattern, h in LOSS_HOMES if re.search(pattern, reason)]
                    self.assertEqual(len(homes), 1, reason)
                    if homes[0] is None:
                        pending += 1
                        continue
                    with self.subTest(rule=rule['id'], reason=reason):
                        for home in homes[0]:
                            if home == 'gain':
                                gains = [h for h in route if any('gain and full-activation pose not published' in l['reason']
                                                                 for l in h['loss_annotations'])]
                                self.assertGreaterEqual(len(gains), 1)
                            elif home == 'split':
                                split = A10_SUPERSEDED.search(rule['outputs'][0])
                                self.assertIn(build_canonical.SYMMETRY if split else
                                              f'{build_canonical.SPLIT_KEY}: {keys[build_canonical.SPLIT_KEY]}', held)
                                covered |= set() if split else {build_canonical.SPLIT_KEY}
                            elif home == 'netting':
                                self.assertIn(build_canonical.NETTING, held)
                            elif home == 'same':
                                self.assertIn(reason, held)
                            elif home in keys:
                                self.assertIn(home, held_keys)
                                covered.add(home)
                            else:
                                self.assertIn(home, held)
                # Today's internal gaze steps write no output of the pair; the splits that read them carry its keys.
                if mapping['id'] == 'visemes.to_vrm' or rule['outputs'][0].startswith(INTERMEDIATE):
                    continue
                pair = A1_PAIRS[mapping['id']]
                with self.subTest(rule=rule['id'], added=pair):
                    self.assertLessEqual(held_keys - covered, ADDED[pair])
        self.assertEqual(len(reasons), 21)
        self.assertEqual(len(documented), 21)
        self.assertGreater(pending, 0)

    def test_composed_hop_weights_equal_todays_weights(self):
        for pair in sorted(set(A1_PAIRS.values())):
            with self.subTest(pair=pair):
                counts, failures = ab_compare.m1s(self.a1, self.pack, pair, self.pairs[pair])
                self.assertGreater(counts['linear_outputs'], 0)
                self.assertEqual(failures, [])
        self.assertNotIn(VISEME_PAIR, self.pairs)

    def test_todays_direct_maps_are_unchanged(self):
        baseline = {m['id']: m for m in self.a1['mappings'] if m['id'] in build_canonical.A1_MAPS}
        current = {m['id']: m for m in self.pack['mappings'] if m['id'] in build_canonical.A1_MAPS}
        self.assertEqual(current, baseline)
        a1_signals = {s['id']: s for s in self.a1['signals']}
        a1_records = {e['id']: e for e in self.a1['evidence']}
        records = {e['id']: e for e in self.pack['evidence']}
        for mapping in baseline.values():
            for rule in mapping['rules']:
                for sid in rule['inputs'] + rule['outputs']:
                    self.assertEqual(self.signals[sid], a1_signals[sid], sid)
                for eid in rule['evidence']:
                    self.assertEqual(records[eid], a1_records[eid], eid)

    def capability(self, names, aliases=None, facs=False):
        """The canonical groups that a set with these names can fill completely."""
        aliases = aliases or {}
        native = {}
        for sid, shorts in self.aligned['fb2'].items():
            for short in shorts:
                native[PREFIX + short] = sid.removeprefix('openxr.fb2.XR_FACE_EXPRESSION2_').removesuffix('_FB')
        have = {aliases.get(n, n) for n in names}
        filled = set()
        for group in self.groups:
            members = [s for s, g in self.group.items() if g == group]
            if facs:
                ok = all(self.signals[s]['metadata']['facs_au'] in have for s in members)
            else:
                ok = all(native[s] in have for s in members)
            if ok:
                filled.add(group)
        return [g for g in self.groups if g in filled]

    def test_capability_matrix_of_other_sets(self):
        fixture = json.loads((ROOT / 'tests/fixtures/capability_sets.json').read_text(encoding='utf-8'))
        records = {e['id']: e for e in self.pack['evidence']}
        matrix = {}
        for entry in fixture['sets']:
            self.assertEqual(entry['sha256'], records[entry['record']]['sha256'], entry['set'])
            matrix[entry['set']] = self.capability(entry['names'], ALIASES.get(entry['set']), entry['set'] == 'FACS')
        self.assertEqual(matrix, CAPABILITY)
        self.assertIn('face', matrix['XR_ML_facial_expression'])
        # A synthetic source with every FB2 name but one face name fills every group except face.
        fb2 = [s.removeprefix('openxr.fb2.XR_FACE_EXPRESSION2_').removesuffix('_FB')
               for s in self.members['openxr.fb2']]
        partial = self.capability([n for n in fb2 if n != 'BROW_LOWERER_L'])
        self.assertEqual(partial, [g for g in self.groups if g != 'face'])

    def test_a_missing_face_input_refuses_only_the_face_outputs(self):
        pack = rcef_translate.load_pack(self.pack)
        route = rcef_route.Route('arkit.coefficient', 'openxr.fb2', pack=pack)
        values = {s: 0.25 for s in self.members['arkit.coefficient'] if s in route.kept}
        del values['arkit.coefficient.browDownLeft']
        result, = route.translate([{'time': 0.0, 'values': values, 'flags': {}}])
        face = set(rcef_route.map_ends(next(r for m, _, k, g, r in self.hops if m == 'rcef_face.to_fb2'))[1])
        self.assertEqual(set(result['labels']), face)
        self.assertEqual(set(result['labels'].values()), {'refused upstream at arkit_face.to_rcef'})
        self.assertEqual(set(result['values']), set(route.outputs) - face)
        self.assertIn('openxr.fb2.XR_FACE_EXPRESSION2_MOUTH_LEFT_FB', result['values'])


if __name__ == '__main__':
    unittest.main()
