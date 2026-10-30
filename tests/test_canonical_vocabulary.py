# SPDX-License-Identifier: MIT
"""The canonical expression set in the pack against its documents: fields, groups, evidence and audit rows.

docs/canonical-set.md is the meaning source; docs/canonical-set-audit.md holds
one audit row for each pair of canonical signal and source that maps it. The
pack holds the groups that have maps today; the groups listed in
scripts/build_canonical.py LATER_GROUPS come later, and each adds its own
expectations here when it joins the pack. The canonical viseme profile has its
own tests in tests/test_canonical_visemes.py.
"""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_canonical  # noqa: E402

EXPRESSION = 'rcef.canonical_expression'
PREFIX = EXPRESSION + '.'
# Group sizes in the pack, after the face splits. Update with each new group.
GROUPS = {'face': 41, 'cheek_puff': 2, 'jaw_thrust': 1, 'jaw_sideways': 2, 'mouth_shift': 2,
          'chin_raise_upper_lip': 1, 'blink': 2, 'gaze': 8, 'tongue_out': 1, 'cheek_suck': 2, 'lip_tighten': 2,
          'tongue_place': 6, 'pupil_mm': 2}
METADATA = {'definition', 'zero', 'one', 'facs_au', 'facs_table', 'group', 'aligned_names', 'audit'}
PUPILS = {PREFIX + 'pupil_diameter_mm_left', PREFIX + 'pupil_diameter_mm_right'}
DIRECTION_EVIDENCE = {'xr_fb2', 'xr_fb2_fig_eyes_closed_l', 'xr_fb2_fig_eyes_look_left_l', 'xr_fb2_fig_mouth_left',
                      'apple_blendshapes'}
# The provider whose hops cite a record, by the profile its signals belong to.
SOURCES = {'arkit.coefficient': 'arkit', 'openxr.fb2': 'fb2', 'vrcft.artist.base': 'vrcft_artist', 'vrm.preset': 'vrm',
           'vrcft.eye': 'vrcft_eye'}


class CanonicalVocabulary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        cls.signals = {s['id']: s for s in cls.pack['signals']}
        cls.profiles = {p['id']: p for p in cls.pack['profiles']}
        cls.docs = build_canonical.read_documents(ROOT)
        cls.expression = [cls.signals[s] for s in cls.profiles[EXPRESSION]['signal_ids']]

    def canonical_profiles(self):
        return [p for p in self.profiles.values() if p['id'].startswith('rcef.canonical_')]

    def test_short_names_are_unique_across_the_canonical_profiles(self):
        shorts = [sid.split('.', 2)[2] for p in self.canonical_profiles() for sid in p['signal_ids']]
        self.assertEqual(len(shorts), len(set(shorts)))
        for p in self.canonical_profiles():
            self.assertTrue(all(sid.startswith(p['id'] + '.') for sid in p['signal_ids']), p['id'])

    def test_every_canonical_profile_has_a_draft_vocabulary_version(self):
        for p in self.canonical_profiles():
            with self.subTest(profile=p['id']):
                self.assertEqual(p['metadata']['vocabulary_version'], '1.0')
                self.assertEqual(p['metadata']['vocabulary_status'], 'draft')

    def test_signals_follow_the_signal_table(self):
        table = {s['short']: s for s in self.docs['signals']}
        for signal in self.expression:
            short = signal['id'][len(PREFIX):]
            row = table[short]
            with self.subTest(signal=short):
                self.assertEqual((signal['label'], signal['side'], signal['region']),
                                 (row['label'], row['side'], row['region']))
                self.assertEqual(signal['metadata']['definition'], build_canonical.plain(row['definition']))
                self.assertEqual((signal['metadata']['group'], signal['metadata']['facs_au'],
                                  signal['metadata']['facs_table']), (row['group'], row['facs_au'], row['facs_table']))
        later = {s['short'] for s in self.docs['signals'] if s['group'] in build_canonical.LATER_GROUPS}
        self.assertEqual({s['id'][len(PREFIX):] for s in self.expression}, set(table) - later)

    def test_unitless_signals_have_neutral_zero_a_unit_range_and_the_metadata_fields(self):
        for signal in self.expression:
            if signal['id'] in PUPILS:
                continue
            with self.subTest(signal=signal['id']):
                self.assertEqual((signal['value_type'], signal['units'], signal['domain'], signal['neutral']),
                                 ('scalar', '1', {'min': 0.0, 'max': 1.0}, 0.0))
                self.assertEqual(set(signal['metadata']), METADATA)
                self.assertNotIn('coupling', signal)
                self.assertEqual(signal['disposition'], 'mapped')

    def test_calibration_strings_follow_the_signal_class(self):
        for signal in self.expression:
            short = signal['id'][len(PREFIX):]
            kind = {'gaze': 'gaze', 'pupil_mm': 'pupil'}.get(signal['metadata']['group'], 'face')
            with self.subTest(signal=short):
                self.assertEqual(signal['calibration'],
                                 self.docs['calibration'][kind].replace('<short_name>', short))
                self.assertTrue(signal['calibration'].startswith(f'rcef.canonical.v1:{short}: '))

    def test_only_the_pupils_are_verified_current(self):
        verified = {s['id'] for s in self.expression if s['evidence_status'] == 'verified_current'}
        self.assertEqual(verified, PUPILS)
        records = {e['id']: e for e in self.pack['evidence']}
        for sid in PUPILS:
            signal = self.signals[sid]
            self.assertEqual((signal['units'], signal['domain'], 'neutral' in signal), ('mm', {}, False))
            self.assertEqual(signal['evidence'], ['rcef_canonical_v1', 'vrcft_data'])
            self.assertTrue(all(records[e]['status'] == 'verified_current' for e in signal['evidence']))
        for signal in self.expression:
            if signal['id'] not in PUPILS:
                self.assertEqual(signal['evidence_status'], 'proposed', signal['id'])

    def test_evidence_of_each_signal(self):
        for signal in self.expression:
            meta = signal['metadata']
            with self.subTest(signal=signal['id']):
                self.assertEqual(signal['evidence'][0], 'rcef_canonical_v1')
                self.assertEqual('facs_wikipedia' in signal['evidence'], bool(meta['facs_au']))
                self.assertEqual(bool(meta['facs_au']), meta['facs_table'] in ('main', 'gross_behavior'))
                if meta['group'] == 'gaze':
                    self.assertEqual((meta['facs_au'], meta['facs_table']), ('', ''))
                if meta['group'] in ('jaw_sideways', 'mouth_shift'):
                    self.assertLessEqual(DIRECTION_EVIDENCE, set(signal['evidence']))

    def test_groups_partition_the_profile(self):
        groups = {}
        for signal in self.expression:
            groups.setdefault(signal['metadata']['group'], []).append(signal['id'])
        self.assertEqual({g: len(s) for g, s in groups.items()}, GROUPS)
        self.assertEqual(self.profiles[EXPRESSION]['metadata']['groups'], list(GROUPS))
        documented = {build_canonical.ticks(r['Group'])[0]: int(r['Signals'])
                      for r in build_canonical.table((ROOT / build_canonical.SIGNAL_DOC).read_text(encoding='utf-8'),
                                                     '### Groups')}
        for group, size in GROUPS.items():
            self.assertEqual(documented[group], size, group)

    def test_aligned_names_are_the_names_the_hops_read_and_write(self):
        hop_names = {}
        for mapping in self.pack['mappings']:
            for rule in mapping['rules']:
                ends = rule['inputs'] + rule['outputs']
                for canonical in (s for s in ends if s.startswith(PREFIX)):
                    for sid in ends:
                        profile = next((p for p in SOURCES if sid.startswith(p + '.')), None)
                        if profile:
                            hop_names.setdefault((canonical, profile), set()).add(sid[len(profile) + 1:])
        for signal in self.expression:
            aligned = signal['metadata']['aligned_names']
            for profile, names in aligned.items():
                with self.subTest(signal=signal['id'], profile=profile):
                    hop = hop_names.get((signal['id'], profile), set())
                    if profile == 'openxr.fb2':
                        hop = {n.removeprefix('XR_FACE_EXPRESSION2_').removesuffix('_FB') for n in hop}
                    self.assertEqual(set(names), hop)
            self.assertEqual(set(aligned), {p for c, p in hop_names if c == signal['id']}, signal['id'])

    def test_every_mapped_pair_and_every_cited_facs_crosswalk_has_an_audit_row(self):
        audit = self.docs['audit']
        for mapping in self.pack['mappings']:
            for rule in mapping['rules']:
                ends = rule['inputs'] + rule['outputs']
                canonical = [s[len(PREFIX):] for s in ends if s.startswith(PREFIX)]
                provider = next((SOURCES[p] for p in SOURCES for s in ends if s.startswith(p + '.')), None)
                for short in canonical:
                    with self.subTest(rule=rule['id'], signal=short):
                        if provider:
                            self.assertIn(short, audit[provider])
                        if 'ict_facekit' in rule['evidence'] and self.signals[PREFIX + short]['metadata']['facs_au']:
                            self.assertIn(short, self.docs['ict'])
        for signal in self.expression:
            short = signal['id'][len(PREFIX):]
            if signal['metadata']['facs_au']:
                self.assertIn(short, self.docs['facs_rows'], short)
            for anchor in signal['metadata']['audit']:
                self.assertTrue(anchor.startswith('docs/canonical-set-audit.md#'), anchor)

    def test_intermediate_gaze_differences(self):
        helpers = [f'rcef.intermediate.gaze_{d}_{s}' for s in ('left', 'right') for d in ('in_minus_out', 'up_minus_down')]
        users = {}
        for mapping in self.pack['mappings']:
            for rule in mapping['rules']:
                for sid in rule['inputs'] + rule['outputs']:
                    if sid in helpers:
                        users.setdefault(sid, set()).add(mapping['id'])
        for sid in helpers:
            with self.subTest(signal=sid):
                self.assertIn(sid, self.profiles['rcef.intermediate']['signal_ids'])
                self.assertEqual(self.signals[sid]['domain'], {'min': -1.0, 'max': 1.0})
                self.assertEqual(users[sid], {'rcef_expression.to_fb2'})


if __name__ == '__main__':
    unittest.main()
