# SPDX-License-Identifier: MIT
"""The canonical viseme set in the pack against docs/canonical-set.md and the IPA chart.

- the profile, its groups and the fields of each signal;
- every symbol of the IPA chart (tests/fixtures/ipa_chart_symbols.json) is in exactly one partition class,
  written in NFC, and the document's appendix lists the same assignment;
- the IPA rules (tests/ipa_classes.py) on the rule cases, on the examples in each class's `ipa_rules`, and on
  the provider labels; a symbol with no rule raises;
- each reserved refinement lies inside one class; each aggregate is a union of whole classes of one group;
- the partition classes are coupled as a simplex, and the aggregate is outside it.
"""
import json
from pathlib import Path
import re
import sys
import unicodedata
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tests')]
import build_canonical  # noqa: E402
import ipa_classes  # noqa: E402

PROFILE = 'rcef.canonical_viseme'
PREFIX = PROFILE + '.'
GROUPS = {'viseme_vowel': 5, 'viseme_consonant': 9, 'viseme_rest': 1, 'viseme_aggregate': 1}
EVIDENCE = ['rcef_canonical_v1', 'ipa_chart_doulos_2020']
SECTIONS = {'Pulmonic consonants': 59, 'Non-pulmonic consonants': 10, 'Other symbols': 10, 'Vowels': 28}
RULE_CASES = {
    # rhoticity
    'ɚ': 'rhotic', 'ɝ': 'rhotic', 'a˞': 'vowel_open', 'ə˞': 'rhotic', 'ɜ˞': 'rhotic', 'ɘ˞': 'vowel_mid_spread',
    'o˞': 'vowel_mid_rounded',
    # labialisation and compression
    'kʷ': 'vowel_close_rounded', 'ɡʷ': 'vowel_close_rounded', 'tʷ': 'vowel_close_rounded',
    'dʷ': 'vowel_close_rounded', 'xʷ': 'vowel_close_rounded', 'hʷ': 'vowel_close_rounded',
    't͡ɕᶣ': 'postalveolar', 'pʷ': 'bilabial', 'ɹʷ': 'rhotic', 'sʷ': 'postalveolar', 'zʷ': 'postalveolar',
    't͡sʷ': 'postalveolar', 'θʷ': 'dental', 'ɯʷ': 'vowel_close_rounded', 'eʷ': 'vowel_mid_rounded',
    'jʷ': 'vowel_close_rounded', 'ɰʷ': 'vowel_close_rounded', 'eᵝ': 'vowel_mid_rounded',
    'ɯᵝ': 'vowel_close_rounded', 'ɨᵝ': 'vowel_close_rounded', 'uᵝ': 'vowel_close_rounded',
    'kᵝ': 'vowel_close_rounded',
    # marks that keep the class
    'ɫ': 'coronal_nasal_lateral', 'β̞': 'bilabial', 'ɹ̝': 'rhotic', 'tʲ': 'coronal_stop', 'tˠ': 'coronal_stop',
    'tˤ': 'coronal_stop', 'dⁿ': 'coronal_stop', 'dˡ': 'coronal_stop', 'ẽ': 'vowel_mid_spread',
    'n̩': 'coronal_nasal_lateral', 'ɔ̹': 'vowel_mid_rounded', 'ɔ̜': 'vowel_mid_rounded',
    # ejectives, affricates and double articulations
    'pʼ': 'bilabial', 'tʼ': 'coronal_stop', 'kʼ': 'dorsal', 'sʼ': 'alveolar_sibilant',
    't͡s': 'alveolar_sibilant', 't͡ʃ': 'postalveolar', 'd͡ʒ': 'postalveolar', 'p͡f': 'labiodental',
    't͡ɬ': 'coronal_nasal_lateral', 'k͡x': 'dorsal', 'k͡p': 'bilabial', 'ɡ͡b': 'bilabial', 'ŋ͡m': 'bilabial',
    # the dental mark or the advanced mark alone keeps the coronal class
    't̪': 'coronal_stop', 'd̪': 'coronal_stop', 'n̪': 'coronal_nasal_lateral', 'l̪': 'coronal_nasal_lateral',
    'ǀ': 'coronal_stop', 'ǃ': 'coronal_stop', 't̟': 'coronal_stop', 'n̟': 'coronal_nasal_lateral',
    'l̟': 'coronal_nasal_lateral',
    # interdental by symbols; not on a sibilant
    'θ̟': 'dental', 'ð̟': 'dental', 't̪̟': 'dental', 'd̪̟': 'dental', 'n̪̟': 'dental', 'l̪̟': 'dental',
    'ɹ̪̟': 'dental', 'n̪͆': 'dental', 'ð̪͆': 'dental', 't̺͆': 'dental', 'l̻͆': 'dental', 's̪͆': 'dental',
    's̪̟': 'alveolar_sibilant', 'z̪̟': 'alveolar_sibilant',
    # linguolabial on alveolar, dental, labial and rhotic letters; the apico-labial notation
    't̼': 'dental', 'θ̼': 'dental', 'ð̼': 'dental', 'p̼': 'dental', 'b̼': 'dental', 'm̼': 'dental',
    'f̼': 'dental', 'v̼': 'dental', 'r̼': 'dental', 'ɾ̼': 'dental', 'p̺': 'dental', 'm̺': 'dental',
    # leading superscripts
    'ᵐb': 'bilabial', 'ⁿd': 'coronal_stop', 'ᵑɡ': 'dorsal', 'ʰt': 'coronal_stop',
    # conventions for single chart letters
    'ɸ': 'bilabial', 'β': 'bilabial', 'ɧ': 'postalveolar', 'ɺ': 'coronal_nasal_lateral',
    'ɬ': 'coronal_nasal_lateral', 'ɮ': 'coronal_nasal_lateral', 'h': 'dorsal', 'ʔ': 'dorsal',
    'j': 'vowel_close_spread', 'ɰ': 'vowel_close_spread', 'ʝ': 'dorsal', 'ç': 'dorsal', 'ɣ': 'dorsal',
    'ɥ': 'vowel_close_rounded', 'ǁ': 'coronal_nasal_lateral', 'ɒ': 'vowel_mid_rounded',
    'ʉ': 'vowel_close_rounded', 'ɵ': 'vowel_mid_rounded', 'ɞ': 'vowel_mid_rounded',
}
NO_RULE = ['f͆', 'θ͆', 'k̼']
# Every reading of each provider label that the audit considers (META's cells and examples, VRM's remarks).
READINGS = {
    'openxr.visemes': {'PP': 'p b m', 'FF': 'f v', 'TH': 'θ ð', 'DD': 't d', 'KK': 'k ɡ', 'CH': 't͡ʃ d͡ʒ ʃ',
                       'SS': 's z', 'NN': 'n l', 'RR': 'r ɹ', 'AA': 'ɑ', 'E': 'e ɛ', 'IH': 'ɪ', 'OH': 'o',
                       'OU': 'ʊ'},
    'vrm.preset': {'aa': 'a ɑ', 'ih': 'i', 'ou': 'u ɯᵝ', 'ee': 'e ɛ', 'oh': 'o'},
}


class CanonicalVisemes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        cls.profile = next(p for p in pack['profiles'] if p['id'] == PROFILE)
        signals = {s['id']: s for s in pack['signals']}
        cls.signals = {sid[len(PREFIX):]: signals[sid] for sid in cls.profile['signal_ids']}
        cls.classes = {k: s for k, s in cls.signals.items() if s['coupling'] == 'probability_simplex'}
        cls.symbols = json.loads((ROOT / build_canonical.IPA_FIXTURE).read_text(encoding='utf-8'))['symbols']
        cls.doc = (ROOT / build_canonical.SIGNAL_DOC).read_text(encoding='utf-8')

    def test_profile_groups_and_fields(self):
        meta = self.profile['metadata']
        self.assertEqual(meta['groups'], list(GROUPS))
        self.assertEqual((meta['vocabulary_version'], meta['vocabulary_status']), ('1.0', 'draft'))
        self.assertEqual(self.profile['evidence'], EVIDENCE)
        sizes = {g: [s['metadata']['group'] for s in self.signals.values()].count(g) for g in GROUPS}
        self.assertEqual(sizes, GROUPS)
        for short, s in self.signals.items():
            with self.subTest(signal=short):
                self.assertRegex(short, r'^[a-z][a-z_]*[a-z]$')
                self.assertEqual((s['units'], s['domain'], s['side'], s['region']),
                                 ('probability', {'min': 0.0, 'max': 1.0}, 'shared', 'mouth'))
                self.assertNotIn('neutral', s)
                self.assertEqual(s['evidence'], EVIDENCE)
                self.assertEqual((s['evidence_status'], s['disposition']), ('proposed', 'mapped'))
                self.assertTrue(s['metadata']['definition'])

    def test_the_group_follows_the_class(self):
        for short, s in self.signals.items():
            group = s['metadata']['group']
            with self.subTest(signal=short):
                if s['coupling'] != 'probability_simplex':
                    self.assertEqual(group, 'viseme_aggregate')
                elif short == 'sil':
                    self.assertEqual(group, 'viseme_rest')
                else:
                    self.assertEqual(group, 'viseme_vowel' if short.startswith('vowel_') else 'viseme_consonant')
                    self.assertTrue(s['metadata']['shape_class'])
        # So the VRM vowels and META's vowels share one group, and no consonant or sil is in it.
        vowels = {k for k, s in self.signals.items() if s['metadata']['group'] == 'viseme_vowel'}
        self.assertEqual(vowels, {k for k, s in self.signals.items() if 'vrm.preset' in s['metadata']['aligned_names']})

    def test_every_chart_symbol_is_in_exactly_one_class(self):
        chart = [s['symbol'] for s in self.symbols]
        self.assertEqual(len(chart), 107)
        self.assertEqual(len(set(chart)), len(chart))
        self.assertEqual({k: sum(s['section'] == k for s in self.symbols) for k in SECTIONS}, SECTIONS)
        homes = {}
        for short, s in self.classes.items():
            for symbol in s['metadata']['ipa_members']:
                homes.setdefault(symbol, []).append(short)
        self.assertEqual(sorted(homes), sorted(chart))
        for entry in self.symbols:
            with self.subTest(symbol=entry['symbol']):
                self.assertEqual(homes[entry['symbol']], [entry['class']])
                self.assertEqual(ipa_classes.classify(entry['symbol']), entry['class'])
                assumed = entry['symbol'] in self.classes[entry['class']]['metadata']['ipa_members_assumed']
                self.assertEqual(assumed, entry['evidence'].startswith('A'))
        self.assertEqual(self.classes['sil']['metadata']['ipa_members'], [])

    def test_symbols_are_nfc_and_match_their_code_points(self):
        for entry in self.symbols:
            symbol = entry['symbol']
            with self.subTest(symbol=symbol):
                self.assertEqual(unicodedata.normalize('NFC', symbol), symbol)
                self.assertEqual(entry['code_points'], ' '.join(f'U+{ord(c):04X}' for c in symbol))
        members = [m for s in self.signals.values() for m in s['metadata']['ipa_members']]
        self.assertIn('ɡ', members)  # U+0261, the IPA letter, not the ASCII g
        self.assertNotIn('g', members)

    def test_the_document_appendix_lists_the_fixture(self):
        rows = build_canonical.table(self.doc, '## IPA chart assignment')
        listed = [(r['Symbol'], r['Code points'], r['Chart section'], r['Cell'], r['Class'].strip('`'), r['Evidence'])
                  for r in rows]
        expected = [(s['symbol'], s['code_points'], s['section'], s['cell'], s['class'], s['evidence'])
                    for s in self.symbols]
        self.assertEqual(listed, expected)

    def test_rule_cases(self):
        self.assertEqual((len(RULE_CASES), len(NO_RULE)), (112, 3))
        for symbol, expected in RULE_CASES.items():
            with self.subTest(symbol=symbol):
                self.assertEqual(ipa_classes.classify(symbol), expected)
        for symbol in NO_RULE:
            with self.subTest(symbol=symbol), self.assertRaises(ValueError):
                ipa_classes.classify(symbol)

    def test_the_rule_examples_of_each_class_are_in_that_class(self):
        examples = 0
        for short, s in self.classes.items():
            for token in re.split(r'[\s;,()]+', s['metadata']['ipa_rules']):
                if token and not token.isascii():
                    examples += 1
                    with self.subTest(signal=short, example=token):
                        self.assertEqual(ipa_classes.classify(token), short)
        self.assertGreater(examples, 30)

    def test_each_provider_label_reads_into_its_class_alone(self):
        for profile, labels in READINGS.items():
            for label, reading in labels.items():
                with self.subTest(label=label):
                    homes = {ipa_classes.classify(symbol) for symbol in reading.split()}
                    aligned = [k for k, s in self.classes.items()
                               if label in s['metadata']['aligned_names'].get(profile, [])]
                    self.assertEqual(sorted(homes), aligned)
        meta = READINGS['openxr.visemes']
        homes = [ipa_classes.classify(meta[label].split()[0]) for label in meta]
        self.assertEqual(len(set(homes)), 14)

    def test_each_refinement_lies_inside_one_class(self):
        rows = build_canonical.table(self.doc, '### Viseme refinements')
        self.assertEqual(len(rows), 10)
        for row in rows:
            name, parent = row['Reserved refinement'].strip('`'), row['Refines'].strip('`')
            members = row['Members'].split(';')[0].split('(')[0].split()
            with self.subTest(refinement=name):
                self.assertNotIn(name, self.signals)
                self.assertEqual({ipa_classes.classify(m) for m in members}, {parent})
        self.assertEqual(ipa_classes.classify('β̞'), 'bilabial')

    def test_each_aggregate_is_a_union_of_whole_classes_of_one_group(self):
        reserved = {r['Reserved aggregate'].strip('`'): re.findall(r'`([a-z_]+)`', r['Classes'])
                    for r in build_canonical.table(self.doc, '### Viseme aggregates')}
        aggregates = {k: s for k, s in self.signals.items() if s['coupling'] != 'probability_simplex'}
        self.assertEqual(list(aggregates), ['alveolar_floor'])
        for short, s in aggregates.items():
            parts = s['metadata']['aggregates']
            self.assertEqual(s['coupling'], 'aggregate_of_simplex_classes')
            self.assertNotIn('shape_class', s['metadata'])
            union = [m for p in parts for m in self.classes[p]['metadata']['ipa_members']]
            self.assertEqual(sorted(s['metadata']['ipa_members']), sorted(union))
            self.assertEqual(len(union), 23)
            reserved[short] = parts
        for name, parts in reserved.items():
            with self.subTest(aggregate=name):
                self.assertGreaterEqual(len(parts), 2)
                self.assertEqual(len(set(parts)), len(parts))
                self.assertLessEqual(set(parts), set(self.classes))
                self.assertEqual(len({self.classes[p]['metadata']['group'] for p in parts}), 1)

    def test_the_partition_classes_are_coupled_as_a_simplex(self):
        partition = [k for k, s in self.signals.items() if s['metadata']['group'] != 'viseme_aggregate']
        self.assertEqual(sorted(self.classes), sorted(partition))
        self.assertEqual(len(self.classes), 15)
        self.assertEqual(sorted(ipa_classes.partition()), sorted(self.classes))


if __name__ == '__main__':
    unittest.main()
