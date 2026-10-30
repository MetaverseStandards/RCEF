# SPDX-License-Identifier: MIT
"""The hop maps against the rules of docs/canonical-set.md and its audit, without the generator.

tests/test_pivot_structure.py compares the data with what scripts/build_canonical.py writes. These tests do
not import the generator: they read the pack, the audit document and the frozen direct maps, and state each
rule on its own, so that a fault in the generator fails here even when the data agrees with the generator.

- every hop states its gain loss, so every route states it twice (VRM blink out-hops state the weight loss,
  VRM vowel hops the asset-weight key, FACS hops the ordinal-intensity key, which says no gain is measured);
- each tongue_out hop states that the tongue extension has no stated length;
- exactly the 4 FB2 gaze outputs on a negative knot segment state the 2⁻⁵⁴ rounding loss;
- each hop cites exactly its evidence: its set's own records, every crosswalk record that today's direct maps
  cite on a rule that links its provider signal to another set (ict_facekit on ARKit hops only), the IPA chart
  on viseme hops, facs_hager_2002 on the FACS AU43 hops, and rcef_canonical_v1;
- each crosswalk set that a hop cites has exactly one transfer assumption, and each transfer assumption names
  a crosswalk set that the hop cites;
- a hop withdraws a crosswalk transfer exactly when its own audit row or the other set's audit row for the
  canonical signal is `differs` or `unresolved`, and names those rows' loss keys;
- the FB2-only signals that Unified Expressions also has take their crosswalks from the audit's table of them:
  their FB2 and Unified Expressions hops cite its one-step record (provider form) and its Godot records (chain
  form), and only the Unified Expressions out-hops state the two-step loss;
- a Unified Expressions fan-out names only the parts that its canonical value goes to;
- the jaw caveat of today's FB2 -> ARKit mouthClose rule is on the ARKit out-hop only;
- every VRM vowel hop, in and out, states the unit change from probability to VRM weight, and no other hop does;
- the META viseme hops copy each META signal to its own canonical class and back, so META -> canonical -> META
  gives every value back.
"""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'rcef.canonical_expression.'
VISEME = 'rcef.canonical_viseme.'
INTERMEDIATE = 'rcef.intermediate.'
SUM = INTERMEDIATE + 'viseme_alveolar_floor_sum'
OWN = 'rcef_canonical_v1'
IPA = 'ipa_chart_doulos_2020'
SETS = {'arkit': ('arkit.coefficient', 'ARKit', ['apple_blendshapes']),
        'fb2': ('openxr.fb2', 'FB2', ['xr_fb2']),
        'vrcft_artist': ('vrcft.artist.base', 'Unified Expressions', ['vrcft_artist', 'vrcft_docs_shapes']),
        'vrm': ('vrm.preset', 'VRM', ['vrm_expressions']),
        'visemes': ('openxr.visemes', 'META', ['xr_visemes', 'xr_registry']),
        'facs': ('facs.code', 'FACS', ['facs_wikipedia'])}
AUDIT_SECTIONS = {'## FB2': 'fb2', '## ARKit': 'arkit', '## VRCFaceTracking Unified Expressions': 'vrcft_artist',
                  '## VRM': 'vrm', '## META visemes': 'visemes', '## FACS': 'facs'}
SET_KEYS = 'arkit|fb2|vrcft_artist|vrm|visemes|facs'
FACS_ORDINAL = 'facs_ordinal_intensity: '
HOP = re.compile(rf'^(?:({SET_KEYS})_\w+\.to_rcef|rcef_\w+\.to_({SET_KEYS}))$')
DIRECT = ('arkit.to_fb2', 'arkit_gaze.to_fb2', 'fb2.to_arkit', 'fb2_gaze.to_arkit', 'arkit.to_vrcft_artist',
          'fb2.to_vrm', 'visemes.to_vrm')
VRM_WEIGHT = 'a canonical value becomes an asset-authored expression weight'
VRM_VOWEL_WEIGHT = 'vrm_vowel_asset_weight: '
TRANSFER = re.compile(r'^transfer\.(?:provider|withdrawn): correspondence evidence is (.+?)↔(.+?) \(([^)]+)\)')
ICT_TRANSFER = re.compile(r'^transfer\.(?:facs_crosswalk|withdrawn): ict_facekit ')
NO_LENGTH = 'no stated length'
CHAIN = re.compile(r'^transfer\.chain: correspondence evidence is FB2↔Godot \((.+?)\) and Godot↔Unified Expressions '
                   r'\((.+?), which give')
CHAIN_LOSS = 'two-step crosswalk through Godot: '
SOURCED = '## Crosswalks of the FB2-only signals'
ROUNDED = {f'openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_{d}_FB' for d in ('LEFT_L', 'DOWN_L', 'RIGHT_R', 'DOWN_R')}
RANK = {'same': 0, 'differs': 1, 'unresolved': 2}


def set_of(sid: str) -> str | None:
    return next((key for key, (profile, _, _) in SETS.items() if sid.startswith(profile + '.')), None)


def is_viseme(rule: dict) -> bool:
    return any(s.startswith(VISEME) or s == SUM for s in rule['inputs'] + rule['outputs'])


class PivotRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        cls.signals = {s['id']: s for s in cls.pack['signals']}
        cls.hops = []  # (set, rule)
        cls.in_rules = []
        for mapping in cls.pack['mappings']:
            if found := HOP.match(mapping['id']):
                cls.hops += [(found.group(1) or found.group(2), rule) for rule in mapping['rules']]
                if found.group(1):
                    cls.in_rules += [rule['id'] for rule in mapping['rules']]
        # Internal steps: the FB2 gaze nets, and the META sum that the aggregate in-hop clamps.
        cls.steps = [r for _, r in cls.hops if r['outputs'][0].startswith(INTERMEDIATE) and r['outputs'] != [SUM]]
        cls.rules = [(k, r) for k, r in cls.hops if r not in cls.steps]
        # Audit rows: the worst verdict per (set, canonical short name), and the keys of the rows.
        cls.audit = {key: {} for key in SETS}
        text = (ROOT / 'docs/canonical-set-audit.md').read_text(encoding='utf-8')
        section, sourced = None, False
        cls.sourced = {}  # canonical short name -> the audit's crosswalk row of an FB2-only signal
        for line in text.splitlines():
            if line.startswith('## '):
                section = AUDIT_SECTIONS.get(line)
                sourced = line == SOURCED
                continue
            if sourced and line.startswith('| `'):
                cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
                cls.sourced[re.findall(r'`([a-z_]+)`', cells[0])[0]] = {
                    'fb2': cells[1], 'vrcft_artist': cells[2], 'one_step': set(re.findall(r'`(\w+)`', cells[3])),
                    'chain': set(re.findall(r'`(\w+)`', cells[4] + cells[5]))}
                continue
            if section is None or not line.startswith('| `'):
                continue
            cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
            verdict, owners = cells[-2], cells[-1]
            for short in re.findall(r'`([a-z_]+)`', cells[0]):
                old = cls.audit[section].get(short, ('same', set()))
                keys = set(re.findall(r'`([a-z0-9_]+)`', owners)) if verdict != 'same' else set()
                cls.audit[section][short] = (max(old[0], verdict, key=RANK.get), old[1] | keys)
        # Today's direct rules as chains from external inputs to one output, with the internal steps folded in.
        baseline = json.loads((ROOT / 'tests/fixtures/baseline-dea1713.pack.json').read_text(encoding='utf-8'))
        cls.chains = []
        for mapping in baseline['mappings']:
            if mapping['id'] not in DIRECT:
                continue
            writers = {r['outputs'][0]: r for r in mapping['rules']}
            for rule in mapping['rules']:
                if rule['outputs'][0].startswith(INTERMEDIATE):
                    continue
                inputs, evidence = [], list(rule['evidence'])
                for sid in rule['inputs']:
                    if sid.startswith(INTERMEDIATE):
                        inputs += writers[sid]['inputs']
                        evidence += writers[sid]['evidence']
                    else:
                        inputs.append(sid)
                cls.chains.append((inputs, rule['outputs'][0], evidence))

    def canonical(self, key, rule):
        """The canonical short names of a rule; a netting split's, through the aligned FB2 name it writes."""
        shorts = [s.rsplit('.', 1)[1] for s in rule['inputs'] + rule['outputs'] if s.startswith((PREFIX, VISEME))]
        if not shorts and rule['outputs'] == [SUM]:
            return [next(r for _, r in self.hops if r['inputs'] == [SUM])['outputs'][0].rsplit('.', 1)[1]]
        if not shorts:
            native = rule['outputs'][0].removeprefix('openxr.fb2.XR_FACE_EXPRESSION2_').removesuffix('_FB')
            shorts = [s[len(PREFIX):] for s, signal in self.signals.items() if s.startswith(PREFIX)
                      and native in signal['metadata']['aligned_names'].get('openxr.fb2', [])]
        return shorts

    def reasons(self, rule):
        return [loss['reason'] for loss in rule['loss_annotations']]

    def test_every_hop_states_its_gain_loss(self):
        self.assertEqual(len(self.steps), 4)
        for key, rule in self.rules:
            name = SETS[key][1]
            with self.subTest(rule=rule['id']):
                if key == 'vrm' and is_viseme(rule):
                    self.assertTrue([r for r in self.reasons(rule) if r.startswith(VRM_VOWEL_WEIGHT)])
                elif key == 'facs':
                    self.assertTrue([r for r in self.reasons(rule) if r.startswith(FACS_ORDINAL)])
                    self.assertFalse([r for r in self.reasons(rule) if 'gain and full-activation pose' in r])
                else:
                    expected = VRM_WEIGHT if key == 'vrm' else f'{name} gain and full-activation pose not published'
                    self.assertIn(expected, self.reasons(rule))
        for rule in self.steps:
            self.assertFalse([r for r in self.reasons(rule) if 'gain' in r], rule['id'])
        # So every route from an in-hop to an out-hop states it on both hops. The META aggregate in-hop states it
        # on its sum and on its clamp.
        ins = [r for k, r in self.rules if r['id'] in self.in_rules]
        outs = [r for k, r in self.rules if r not in ins]
        self.assertEqual((len(ins), len(outs)), (205, 265))

    def test_each_tongue_out_hop_states_the_missing_length(self):
        tongue = [(k, r) for k, r in self.rules if 'tongue_out' in self.canonical(k, r)]
        self.assertEqual(sorted(k for k, _ in tongue), ['arkit', 'arkit', 'facs', 'facs', 'fb2', 'fb2', 'vrcft_artist'])
        for key, rule in self.hops:
            stated = any(NO_LENGTH in r for r in self.reasons(rule))
            self.assertEqual(stated, (key, rule) in tongue, rule['id'])

    def test_only_the_negative_segment_gaze_outputs_state_the_rounding_loss(self):
        rounded = {r['outputs'][0] for _, r in self.hops if any('2⁻⁵⁴' in x for x in self.reasons(r))}
        self.assertEqual(rounded, ROUNDED)
        for _, rule in self.hops:
            if rule['outputs'][0] in ROUNDED:
                self.assertEqual(rule['operator']['knots'], [[-1.0, 1.0], [0.0, 0.0], [1.0, 0.0]], rule['id'])

    def test_each_hop_cites_exactly_its_evidence(self):
        for rule in self.steps:
            self.assertEqual(rule['evidence'], ['xr_fb2', OWN], rule['id'])
        for key, rule in self.rules:
            own = SETS[key][2]
            expected = set(own) | {OWN} | ({IPA} if is_viseme(rule) else set())
            for records in self.crosswalks(key, rule).values():
                expected |= records
            if key == 'arkit':
                expected |= self.ict(key, rule)
            if row := self.sourced_row(key, rule):
                expected |= row['chain']
            if key == 'facs' and self.canonical(key, rule)[0].startswith('eye_close_'):
                expected.add('facs_hager_2002')
            with self.subTest(rule=rule['id']):
                self.assertEqual(set(rule['evidence']), expected)
                self.assertEqual(len(rule['evidence']), len(expected))
                self.assertEqual(rule['evidence'][:len(own)], own)
                self.assertEqual(rule['evidence'][-2:] if is_viseme(rule) else rule['evidence'][-1:],
                                 [IPA, OWN] if is_viseme(rule) else [OWN])

    def linked(self, key, rule):
        """Today's chains that link a provider signal of this hop to another set: (other set, evidence)."""
        for sid in [s for s in rule['inputs'] + rule['outputs'] if set_of(s) == key]:
            for inputs, output, evidence in self.chains:
                others = [output] if sid in inputs else inputs if sid == output else []
                for other in {set_of(o) for o in others} - {None, key}:
                    yield other, set(evidence)

    def crosswalks(self, key, rule):
        """The crosswalk records per other set: today's evidence on the linking chains, less both sets' own, and
        the one-step record of an FB2-only signal's row in the audit."""
        found = {}
        for other, evidence in self.linked(key, rule):
            records = evidence - set(SETS[key][2]) - set(SETS[other][2]) - {'ict_facekit'}
            if records:
                found.setdefault(other, set()).update(records)
        if row := self.sourced_row(key, rule):
            found.setdefault('vrcft_artist' if key == 'fb2' else 'fb2', set()).update(row['one_step'])
        return found

    def sourced_row(self, key, rule):
        """The audit's crosswalk row of an FB2-only signal, on its FB2 and Unified Expressions hops."""
        if key not in ('fb2', 'vrcft_artist') or is_viseme(rule):
            return None
        rows = [self.sourced[s] for s in self.canonical(key, rule) if s in self.sourced]
        return rows[0] if rows else None

    def ict(self, key, rule):
        return {'ict_facekit'} & set().union(*(evidence for _, evidence in self.linked(key, rule)))

    def transfer_failures(self, key, rule):
        """Why the transfer assumptions of a hop do not match the crosswalk sets it cites; [] when they do."""
        names = {name: k for k, (_, name, _) in SETS.items()}
        cited = {other: records for other, records in self.crosswalks(key, rule).items()
                 if records <= set(rule['evidence'])}
        stated = {}
        for text in rule['assumptions']:
            if found := TRANSFER.match(text):
                if names.get(found.group(2)) != key:
                    return [f'names {found.group(2)}, not this hop\'s set: {text}']
                stated.setdefault(names.get(found.group(1)), []).append(set(found.group(3).split(', ')))
        failures = [f'{other}: {len(stated.get(other, []))} transfer assumptions' for other in cited
                    if len(stated.get(other, [])) != 1]
        failures += [f'{other}: a transfer assumption for a set the hop does not cite' for other in stated
                     if other not in cited]
        failures += [f'{other}: records {texts[0]} are not {cited[other]}' for other, texts in stated.items()
                     if other in cited and len(texts) == 1 and texts[0] != cited[other]]
        ict = [text for text in rule['assumptions'] if ICT_TRANSFER.match(text)]
        if len(ict) != ('ict_facekit' in rule['evidence']):
            failures.append(f'ict_facekit: {len(ict)} transfer assumptions')
        row = self.sourced_row(key, rule)
        chains = [text for text in rule['assumptions'] if text.startswith('transfer.chain: ')]
        if len(chains) != (row is not None):
            failures.append(f'{len(chains)} chain transfers')
        elif row and not (found := CHAIN.match(chains[0])):
            failures.append(f'a chain transfer not through Godot: {chains[0]}')
        elif row and set(re.findall(r'\b(godot_\w+)', found.group(1) + ' ' + found.group(2))) != row['chain']:
            failures.append(f'the chain transfer names other records than {sorted(row["chain"])}: {chains[0]}')
        return failures

    def test_each_crosswalk_set_cited_has_exactly_one_transfer_assumption(self):
        mutants = 0
        for key, rule in self.rules:
            with self.subTest(rule=rule['id']):
                self.assertEqual(self.transfer_failures(key, rule), [])
            # A hop that drops any one of its transfer assumptions fails.
            for n, text in enumerate(rule['assumptions']):
                if text.startswith('transfer.'):
                    mutant = {**rule, 'assumptions': rule['assumptions'][:n] + rule['assumptions'][n + 1:]}
                    self.assertTrue(self.transfer_failures(key, mutant), (rule['id'], text))
                    mutants += 1
        self.assertGreater(mutants, 0)

    def test_a_transfer_is_withdrawn_exactly_where_an_audit_row_is_not_same(self):
        names = {name: key for key, (_, name, _) in SETS.items()}
        counts = {'withdrawn': 0, 'carried': 0}
        for key, rule in self.rules:
            shorts = self.canonical(key, rule)
            for text in rule['assumptions']:
                found = re.match(r'^transfer\.(provider|withdrawn): correspondence evidence is (.+?)↔(.+?) \(', text)
                if not found:
                    continue
                self.assertEqual(names[found.group(3)], key, text)
                rows = [self.audit[who][s] for who in (names[found.group(2)], key) for s in shorts
                        if s in self.audit[who]]
                bad = [row for row in rows if row[0] != 'same']
                with self.subTest(rule=rule['id'], text=text):
                    self.assertEqual(found.group(1) == 'withdrawn', bool(bad))
                    if bad:
                        named = re.search(r'; see loss(?:es)? (.+)\.$', text).group(1).replace(' and ', ', ')
                        self.assertEqual(set(named.split(', ')), set().union(*(row[1] for row in bad)))
                counts['withdrawn' if bad else 'carried'] += 1
        self.assertGreater(counts['withdrawn'], 0)
        self.assertGreater(counts['carried'], 0)


    def test_only_the_unified_out_hops_of_the_fb2_only_signals_state_the_two_step_loss(self):
        self.assertEqual(set(self.sourced), {'cheek_suck_left', 'cheek_suck_right', 'lip_tighten_left',
                                             'lip_tighten_right'})
        stated = {r['id'] for _, r in self.rules if any(x.startswith(CHAIN_LOSS) for x in self.reasons(r))}
        expected = {r['id'] for k, r in self.rules if k == 'vrcft_artist' and self.sourced_row(k, r)}
        self.assertEqual(len(expected), 4)
        self.assertEqual(stated, expected)
        chained = {r['id'] for _, r in self.rules if any(a.startswith('transfer.chain: ') for a in r['assumptions'])}
        self.assertEqual(len(chained), 12)  # 4 FB2 in-hops, 4 FB2 out-hops, 4 Unified Expressions out-hops
        for _, rule in self.rules:
            if rule['id'] in chained:
                name = self.sourced_row(set_of([s for s in rule['inputs'] + rule['outputs'] if set_of(s)][0]), rule)
                self.assertIsNotNone(name, rule['id'])

    def test_a_fan_out_names_only_the_parts_its_canonical_value_goes_to(self):
        fans = 0
        for key, rule in self.rules:
            for text in rule['assumptions']:
                if not text.startswith('fan_out.vrcft_ue: '):
                    continue
                fans += 1
                found = re.search(r'; (\w+) is set to the canonical value, as is ([\w, ]+?)\. ', text)
                written = [found.group(1), *found.group(2).replace(' and ', ', ').split(', ')]
                siblings = [r['outputs'][0].rsplit('.', 1)[1] for k, r in self.rules
                            if k == key and r['inputs'] == rule['inputs']]
                self.assertEqual(sorted(written), sorted(siblings), rule['id'])
        self.assertEqual(fans, 16)

    def test_the_jaw_caveat_is_on_the_arkit_out_hop_only(self):
        found = [r['id'] for _, r in self.rules
                 if any(a.startswith('lips_toward.jaw_not_compensated:') for a in r['assumptions'])]
        self.assertEqual(found, ['rcef_arkit.mouthClose'])

    def test_each_vrm_vowel_hop_states_the_unit_change(self):
        stated = [r['id'] for _, r in self.rules
                  if sum(a.startswith('vrm.probability_as_weight: ') for a in r['assumptions']) == 1]
        vowel_hops = [r['id'] for key, r in self.rules if key == 'vrm' and is_viseme(r)]
        self.assertEqual(len(vowel_hops), 10)
        self.assertEqual(sorted(stated), sorted(vowel_hops))

    def test_meta_to_canonical_to_meta_gives_every_value_back(self):
        copy = {'id': 'affine', 'scale': 1.0, 'offset': 0.0}
        into, back = {}, {}
        for key, rule in self.rules:
            if key != 'visemes' or rule['outputs'] == [SUM] or rule['inputs'] == [SUM]:
                continue
            [source], [target] = rule['inputs'], rule['outputs']
            self.assertEqual(rule['operator'], copy, rule['id'])
            if rule['id'] in self.in_rules:
                into[source] = target
            else:
                back[source] = target
        self.assertEqual(len(into), 15)
        self.assertEqual(len(set(into.values())), 15)
        self.assertEqual({c: m for m, c in into.items()}, back)


if __name__ == '__main__':
    unittest.main()
