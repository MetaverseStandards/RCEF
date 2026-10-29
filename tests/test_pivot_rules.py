# SPDX-License-Identifier: MIT
"""The hop maps against the rules of docs/canonical-set.md and its audit, without the generator.

tests/test_pivot_structure.py compares the data with what scripts/build_canonical.py writes. These tests do
not import the generator: they read the pack, the audit document and the frozen direct maps, and state each
rule on its own, so that a fault in the generator fails here even when the data agrees with the generator.

- every hop states its gain loss, so every route states it twice (VRM out-hops state the weight loss);
- each tongue_out hop states that the tongue extension has no stated length;
- exactly the 4 FB2 gaze outputs on a negative knot segment state the 2⁻⁵⁴ rounding loss;
- each hop cites exactly its evidence: its set's own records, every crosswalk record that today's direct maps
  cite on a rule that links its provider signal to another set (ict_facekit on ARKit hops only), and
  rcef_canonical_v1;
- a hop withdraws a crosswalk transfer exactly when its own audit row or the other set's audit row for the
  canonical signal is `differs` or `unresolved`, and names those rows' loss keys;
- a Unified Expressions fan-out names only the parts that its canonical value goes to;
- the jaw caveat of today's FB2 -> ARKit mouthClose rule is on the ARKit out-hop only.
"""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'rcef.canonical_expression.'
INTERMEDIATE = 'rcef.intermediate.'
OWN = 'rcef_canonical_v1'
SETS = {'arkit': ('arkit.coefficient', 'ARKit', ['apple_blendshapes']),
        'fb2': ('openxr.fb2', 'FB2', ['xr_fb2']),
        'vrcft_artist': ('vrcft.artist.base', 'Unified Expressions', ['vrcft_artist', 'vrcft_docs_shapes']),
        'vrm': ('vrm.preset', 'VRM', ['vrm_expressions'])}
AUDIT_SECTIONS = {'## FB2': 'fb2', '## ARKit': 'arkit', '## VRCFaceTracking Unified Expressions': 'vrcft_artist',
                  '## VRM': 'vrm'}
HOP = re.compile(r'^(?:(arkit|fb2|vrcft_artist|vrm)_\w+\.to_rcef|rcef_\w+\.to_(arkit|fb2|vrcft_artist|vrm))$')
DIRECT = ('arkit.to_fb2', 'arkit_gaze.to_fb2', 'fb2.to_arkit', 'fb2_gaze.to_arkit', 'arkit.to_vrcft_artist',
          'fb2.to_vrm')
VRM_WEIGHT = 'a canonical value becomes an asset-authored expression weight'
NO_LENGTH = 'no stated length'
ROUNDED = {f'openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_{d}_FB' for d in ('LEFT_L', 'DOWN_L', 'RIGHT_R', 'DOWN_R')}
RANK = {'same': 0, 'differs': 1, 'unresolved': 2}


def set_of(sid: str) -> str | None:
    return next((key for key, (profile, _, _) in SETS.items() if sid.startswith(profile + '.')), None)


class PivotRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        cls.signals = {s['id']: s for s in cls.pack['signals']}
        cls.hops = []  # (set, rule)
        for mapping in cls.pack['mappings']:
            if found := HOP.match(mapping['id']):
                cls.hops += [(found.group(1) or found.group(2), rule) for rule in mapping['rules']]
        cls.steps = [r for _, r in cls.hops if r['outputs'][0].startswith(INTERMEDIATE)]
        cls.rules = [(k, r) for k, r in cls.hops if not r['outputs'][0].startswith(INTERMEDIATE)]
        # Audit rows: the worst verdict per (set, canonical short name), and the keys of the rows.
        cls.audit = {key: {} for key in SETS}
        text = (ROOT / 'docs/canonical-set-audit.md').read_text(encoding='utf-8')
        section = None
        for line in text.splitlines():
            if line.startswith('## '):
                section = AUDIT_SECTIONS.get(line)
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
        shorts = [s[len(PREFIX):] for s in rule['inputs'] + rule['outputs'] if s.startswith(PREFIX)]
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
            expected = VRM_WEIGHT if key == 'vrm' else f'{name} gain and full-activation pose not published'
            with self.subTest(rule=rule['id']):
                self.assertIn(expected, self.reasons(rule))
        for rule in self.steps:
            self.assertFalse([r for r in self.reasons(rule) if 'gain' in r], rule['id'])
        # So every route from an in-hop to an out-hop states it on both hops.
        ins = [r for k, r in self.rules if any(i.startswith(SETS[k][0] + '.') for i in r['inputs'])]
        outs = [r for k, r in self.rules if r not in ins]
        self.assertEqual((len(ins), len(outs)), (120, 182))

    def test_each_tongue_out_hop_states_the_missing_length(self):
        tongue = [(k, r) for k, r in self.rules if 'tongue_out' in self.canonical(k, r)]
        self.assertEqual(sorted(k for k, _ in tongue), ['arkit', 'arkit', 'fb2', 'fb2', 'vrcft_artist'])
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
            expected = set(own) | {OWN}
            for sid in [s for s in rule['inputs'] + rule['outputs'] if set_of(s) == key]:
                for inputs, output, evidence in self.chains:
                    others = [output] if sid in inputs else inputs if sid == output else []
                    for other in {set_of(o) for o in others} - {None, key}:
                        expected |= set(evidence) - set(own) - set(SETS[other][2])
            if key != 'arkit':
                expected.discard('ict_facekit')
            with self.subTest(rule=rule['id']):
                self.assertEqual(set(rule['evidence']), expected)
                self.assertEqual(len(rule['evidence']), len(expected))
                self.assertEqual(rule['evidence'][:len(own)], own)
                self.assertEqual(rule['evidence'][-1], OWN)

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


if __name__ == '__main__':
    unittest.main()
