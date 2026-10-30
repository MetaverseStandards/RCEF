# SPDX-License-Identifier: MIT
"""The facs.code profile and its maps, checked against the FACS section of docs/canonical-set.md.

The expected code lists are written out here, apart from the generator and
from examples/data/facs_codes.json: 92 rows (49 mapped, 25 unresolved, 18
excluded), the ID and notation rules, the calibration strings, the side note,
the Rocketbox names, the 16 maps with 102 mappings and their losses, and a
FACS -> canonical -> FACS round trip that gives every value back exactly.
"""
import json
from pathlib import Path
import random
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'examples')]
import facs_codec  # noqa: E402
import rcef_route  # noqa: E402
import rcef_translate  # noqa: E402
import rigs  # noqa: E402

PROFILE = 'facs.code'
PREFIX = 'rcef.canonical_expression.'
SIDED = ('1', '2', '4', '5', '6', '7', '9', '10', '12', '14', '15', '16', '18', '20', '22', '23', '24', '28', '34',
         '35', '43')
SHARED = ('8', '17', '19', '26', '29')
UNRESOLVED = ('11', '13', '21', '25', '27', '31', '32', '33', '36', '37', '38', '39', '40', '41', '42', '44', '45',
              '46', '61', '62', '63', '64', '65', '66', '69')
EXCLUDED = ('50', '51', '52', '53', '54', '55', '56', '57', '58', '80', '81', '82', '84', '85', '91', '92', '97*',
            '98*')
GROSS = ('29', '30', '34', '35', '43')
HAGER = ('41', '42', '43', '44')
# The upper and lower canonical parts of the two FACS codes with no upper/lower split.
PARTS = {'22': ('lip_funnel_upper', 'lip_funnel_lower'), '28': ('lip_suck_upper', 'lip_suck_lower')}
COPY = {'id': 'affine', 'scale': 1.0, 'offset': 0.0}
MEAN = {'id': 'weighted_sum', 'weights': [0.5, 0.5]}


def local(sid: str) -> str:
    return sid[len(PROFILE) + 1:]


# One map per direction between FACS codes and the canonical expression set.
IN_MAP, OUT_MAP = 'facs.to_rcef_expression', 'rcef_expression.to_facs'

class FacsProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        cls.signals = {s['id']: s for s in cls.pack['signals']}
        profile = next(p for p in cls.pack['profiles'] if p['id'] == PROFILE)
        cls.profile = profile
        cls.rows = [cls.signals[s] for s in profile['signal_ids']]
        cls.mapped = [s for s in cls.rows if s['disposition'] == 'mapped']
        cls.maps = {m['id']: m['rules'] for m in cls.pack['mappings'] if m['id'] in (IN_MAP, OUT_MAP)}
        cls.hops = [(m, r) for m, rules in cls.maps.items() for r in rules]
        cls.doc = (ROOT / 'docs/canonical-set.md').read_text(encoding='utf-8')
        cls.keys = {}
        audit = (ROOT / 'docs/canonical-set-audit.md').read_text(encoding='utf-8')
        for key, text in re.findall(r'^\| `(facs_\w+)` \| \w+ \| [^|]+ \| (.+) \|$', audit, re.M):
            cls.keys[key] = text

    def code(self, signal):
        return re.fullmatch(r'[LR]?(\d+\*?)', signal['native_id']).group(1)

    def facs_end(self, rule):
        return next(s for s in rule['inputs'] + rule['outputs'] if s.startswith(PROFILE + '.'))

    def canonical_ends(self, rule):
        return [s[len(PREFIX):] for s in rule['inputs'] + rule['outputs'] if s.startswith(PREFIX)]

    def test_92_rows_with_their_dispositions(self):
        self.assertEqual(len(self.rows), 92)
        by = {}
        for s in self.rows:
            by.setdefault(s['disposition'], []).append(self.code(s))
        self.assertEqual(len(by['mapped']), 49)
        self.assertEqual(sorted(set(by['mapped']), key=lambda c: int(c)), sorted(SIDED + SHARED + ('30',), key=int))
        self.assertEqual(by['unresolved'], list(UNRESOLVED))
        self.assertEqual(sorted(by['excluded']), sorted(EXCLUDED))
        codes = [self.code(s) for s in self.rows]
        for absent in ('0', '70', '71', '72', '73', '74'):
            self.assertNotIn(absent, codes)
        self.assertFalse([s for s in self.rows if 'M' in s['native_id']])

    def test_ids_notation_labels_and_sides(self):
        names = {c: e['name'] for c, e in facs_codec.table()['codes'].items()}
        for s in self.rows:
            code = self.code(s)
            found = re.fullmatch(r'facs\.code\.au(\d\d)(?:_(left|right))?', s['id'])
            with self.subTest(signal=s['id']):
                self.assertIsNotNone(found)
                self.assertEqual(int(found.group(1)), int(code.rstrip('*')))
                side = found.group(2)
                sided = s['disposition'] == 'mapped' and code in SIDED + ('30',)
                self.assertEqual(bool(side), sided)
                self.assertEqual(s['native_id'], {'left': 'L', 'right': 'R', None: ''}[side] + code)
                self.assertEqual(s['side'], side if code in SIDED and side else 'shared')
                suffix = '' if not side else f', toward the {side}' if code == '30' else f', {side}'
                self.assertEqual(s['label'], f'AU {code} {names[code]}{suffix}')
                self.assertEqual((s['surface'], s['value_type'], s['evidence_status']), (PROFILE, 'scalar', 'proposed'))

    def test_calibration_strings_and_side_notes(self):
        main = re.search(r'Main codes: `(rcef\.facs\.v1:au<NN>: [^`]+)`', self.doc).group(1)
        gross = re.search(r'Gross codes 29, 30, 34, 35 and 43: `(rcef\.facs\.v1:au<NN>: [^`]+)`', self.doc).group(1)
        self.assertIn('1 = intensity E, the maximum possible for the individual person', main)
        self.assertIn('1 = the action at its fullest, as RCEF assumes', gross)
        note = re.search(r'\*\*Side note\*\* on every sided row: "([^"]+)"', self.doc).group(1).replace('`', '')
        for s in self.rows:
            with self.subTest(signal=s['id']):
                if s['disposition'] != 'mapped':
                    self.assertNotIn('neutral', s)
                    self.assertTrue(s['metadata']['reason'])
                    continue
                form = gross if self.code(s) in GROSS else main
                self.assertEqual(s['calibration'], form.replace('au<NN>', local(s['id'])))
                self.assertEqual((s['units'], s['domain'], s['neutral']), ('1', {'min': 0.0, 'max': 1.0}, 0.0))
                self.assertEqual(s['metadata'].get('side_note'), note if s['native_id'][0] in 'LR' else None)

    def test_each_canonical_facs_table_agrees_with_its_facs_rows(self):
        # The FACS column of the signal table, read here without the generator: "43 (`gross_behavior`)".
        table = re.search(r'^### Expression signals\n(.*?)\n### ', self.doc, re.M | re.S).group(1)
        documented = {}
        for line in table.splitlines():
            cells = [c.strip() for c in line.strip('|').split(' | ')]
            if line.startswith('| `') and (found := re.match(r'(\d+)\b.*\(`(main|gross_behavior)`\)$', cells[6])):
                documented[cells[0].strip('`')] = found.groups()
        self.assertEqual(len(documented), 53)
        main = re.search(r'Main codes: `(rcef\.facs\.v1:au<NN>: [^`]+)`', self.doc).group(1)
        for short, (code, table_name) in documented.items():
            signal = self.signals[PREFIX + short]
            rows = [s for s in self.mapped if self.code(s) == code]
            with self.subTest(signal=short):
                self.assertEqual((signal['metadata']['facs_au'], signal['metadata']['facs_table']), (code, table_name))
                self.assertTrue(rows)
                for row in rows:
                    self.assertEqual(row['metadata']['facs_table'], table_name)
                    gross = row['calibration'] != main.replace('au<NN>', local(row['id']))
                    self.assertEqual(gross, table_name == 'gross_behavior')
                    self.assertEqual(table_name == 'gross_behavior', code in GROSS)

    def test_evidence_and_rocketbox_names(self):
        fixture = json.loads((ROOT / 'tests/fixtures/rocketbox_au_names.json').read_text(encoding='utf-8'))
        self.assertEqual(len(fixture['names']), 48)
        self.assertEqual(fixture['commit'], rigs.ROCKETBOX_COMMIT)
        for name, digest in fixture['files'].items():
            self.assertEqual(digest, rigs.ROCKETBOX_SHA256[name.removesuffix('_facial.fbx')])
        used = []
        for s in self.rows:
            names = s['metadata'].get('aligned_names', {}).get('rocketbox_avatars', [])
            used += names
            code = self.code(s)
            with self.subTest(signal=s['id']):
                expected = ['facs_wikipedia'] + (['rocketbox_avatars'] if names else [])
                self.assertEqual(s['evidence'], expected + (['facs_hager_2002'] if code in HAGER else []))
                for name in names:
                    found = re.fullmatch(r'AU_(\d\d)_(?:([LR])_)?\w+', name)
                    self.assertEqual(int(found.group(1)), int(code.rstrip('*')))
                    if s['side'] in ('left', 'right'):
                        self.assertIn(found.group(2), (None, s['side'][0].upper()))
        self.assertEqual(set(used), set(fixture['names']))

    def test_profile_metadata(self):
        meta = self.profile['metadata']
        self.assertEqual((meta['vocabulary_version'], meta['vocabulary_status']), ('1.0', 'draft'))
        self.assertIn('not FACS coding', meta['scope'])
        self.assertIn('values are not FACS scores', meta['scope'])
        self.assertEqual(sorted(meta['groups']), sorted(['face', 'cheek_puff', 'jaw_thrust', 'jaw_sideways', 'blink',
                                                         'cheek_suck', 'lip_tighten', 'tongue_out']))

    def test_the_codec_reads_exactly_the_mapped_rows(self):
        self.assertEqual(facs_codec.signals(), [s['id'] for s in self.mapped])
        for code, entry in facs_codec.table()['codes'].items():
            rows = [s['disposition'] for s in self.rows if self.code(s) == code]
            self.assertEqual(set(rows) or {'none'}, {entry['disposition']}, code)

    def test_2_maps_with_102_mappings_and_their_operators(self):
        self.assertEqual(list(self.maps), [IN_MAP, OUT_MAP])
        ins = [r for m, r in self.hops if m == IN_MAP]
        outs = [r for m, r in self.hops if m == OUT_MAP]
        self.assertEqual((len(ins), len(outs)), (53, 49))
        self.assertTrue(all(r['operator'] == COPY for r in ins))
        means = [r for r in outs if r['operator'] == MEAN]
        self.assertEqual(sorted(local(r['outputs'][0]) for r in means),
                         ['au22_left', 'au22_right', 'au28_left', 'au28_right'])
        self.assertTrue(all(r['operator'] == COPY for r in outs if r not in means))
        for rule in means:
            code, side = re.fullmatch(r'au(\d\d)_(\w+)', local(rule['outputs'][0])).groups()
            self.assertEqual(rule['inputs'], [f'{PREFIX}{p}_{side}' for p in PARTS[code]])
        fans = [r for r in ins if sum(x['inputs'] == r['inputs'] for x in ins) == 2]
        self.assertEqual(len(fans), 8)
        for map_id, rule in self.hops:
            self.assertEqual((rule['disposition'], rule['mapping_quality'], rule['evidence_status']),
                             ('mapped', 'approximate', 'proposed'), rule['id'])

    def test_facs_au_agrees_with_the_maps_both_ways(self):
        written = {}
        for map_id, rule in self.hops:
            if map_id == IN_MAP:
                written[rule['outputs'][0]] = self.code(self.signals[rule['inputs'][0]])
        canonical = [s for s in self.pack['signals'] if s['id'].startswith(PREFIX)]
        for s in canonical:
            with self.subTest(signal=s['id']):
                self.assertEqual(written.get(s['id'], ''), s['metadata']['facs_au'])
        for s in self.mapped:
            readers = [self.canonical_ends(r) for m, r in self.hops
                       if m == OUT_MAP and r['outputs'] == [s['id']]]
            self.assertEqual(len(readers), 1, s['id'])
            for short in readers[0]:
                self.assertEqual(self.signals[PREFIX + short]['metadata']['facs_au'], self.code(s), s['id'])

    def test_openings_evidence_and_losses_of_every_hop(self):
        found = re.search(r'FACS hops start with their own assumption instead: "(.+?)"\. On the hops of the gross '
                          r'behaviour codes \(29, 30, 34, 35 and 43\) it reads: "(.+?)"\.', self.doc)
        link = '[facs-intensity.md](facs-intensity.md)'
        main, gross = (g.replace(link, 'docs/facs-intensity.md') for g in found.groups())
        counts = {'gross': 0, 'symmetry': 0, 'asymmetry': 0, 'length': 0}
        for map_id, rule in self.hops:
            signal = self.signals[self.facs_end(rule)]
            code = self.code(signal)
            shorts = self.canonical_ends(rule)
            reasons = [l['reason'] for l in rule['loss_annotations']]
            keys = {r.split(':', 1)[0] for r in reasons} & set(self.keys)
            endpoints = [a for a in rule['assumptions'] if a.startswith('endpoints: ')]
            with self.subTest(rule=rule['id']):
                self.assertEqual(rule['evidence'], ['facs_wikipedia'] + (['facs_hager_2002'] if code == '43' else [])
                                 + ['rcef_canonical_v1'])
                self.assertEqual(len(endpoints), 1)
                self.assertTrue(endpoints[0].startswith('endpoints: ' + (gross if code in GROSS else main) + '; '))
                self.assertEqual({a.split(':', 1)[0] for a in rule['assumptions']}, {'correspondence', 'endpoints'})
                expected = {'facs_ordinal_intensity'}
                if signal['native_id'][0] in 'LR':
                    expected.add('facs_side_frame_unresolved')
                expected |= {'facs_au30_direction_unresolved'} if code == '30' else set()
                expected |= {'facs_au17_no_split'} if code == '17' else set()
                expected |= {'facs_mouth_opening_split'} if code == '26' else set()
                expected |= {'facs_eyelid_events'} if code == '43' else set()
                expected |= {'facs_gross_code_no_intensity'} if code in GROSS else set()
                self.assertEqual(keys, expected)
                for key in keys:
                    self.assertIn(f'{key}: {self.keys[key]}', reasons)
                fan = map_id == IN_MAP and code in PARTS
                mean = rule['operator'] == MEAN
                self.assertEqual('asymmetry unknown: symmetry is invented' in reasons, fan)
                self.assertEqual('asymmetry irrecoverable' in reasons, mean)
                self.assertEqual(any('no stated length' in r for r in reasons), shorts == ['tongue_out'])
                self.assertFalse([r for r in reasons if 'gain and full-activation pose' in r])
            counts['gross'] += code in GROSS
            counts['symmetry'] += fan
            counts['asymmetry'] += mean
            counts['length'] += shorts == ['tongue_out']
        self.assertEqual(counts, {'gross': 18, 'symmetry': 8, 'asymmetry': 4, 'length': 2})

    def test_facs_to_canonical_to_facs_gives_every_value_back_exactly(self):
        pack = rcef_translate.load_pack(self.pack)
        route = rcef_route.Route(PROFILE, PROFILE, pack=pack)
        self.assertEqual(sorted(route.outputs), sorted(s['id'] for s in self.mapped))
        rng = random.Random(12)
        frames = [dict.fromkeys(route.outputs, 0.0), dict.fromkeys(route.outputs, 1.0)]
        frames += [{s: rng.random() for s in route.outputs} for _ in range(500)]
        frames += [{s: rng.choice(list(facs_codec.table()['letters'].values()) + [0.0]) for s in route.outputs}
                   for _ in range(500)]
        results = route.translate([{'time': n / 60, 'values': v, 'flags': {}} for n, v in enumerate(frames)])
        for values, result in zip(frames, results):
            self.assertEqual(result['labels'], {})
            self.assertEqual(result['values'], values)

    def test_what_facs_fills_in_arkit_and_fb2(self):
        pack = rcef_translate.load_pack(self.pack)
        for target, written, total in (('arkit.coefficient', 41, 52), ('openxr.fb2', 53, 70)):
            route = rcef_route.Route(PROFILE, target, pack=pack)
            frame = {s['id']: 0.5 for s in self.mapped}
            result, = route.translate([{'time': 0.0, 'values': frame, 'flags': {}}])
            with self.subTest(target=target):
                self.assertEqual((len(result['values']), len(route.outputs)), (written, total))
                self.assertEqual(set(result['labels'].values()), {rcef_route.NOT_AVAILABLE})


if __name__ == '__main__':
    unittest.main()
