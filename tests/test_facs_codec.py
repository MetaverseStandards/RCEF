# SPDX-License-Identifier: MIT
"""examples/facs_codec.py: FACS notation read into facs.code values, with every rule of its data file."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import facs_codec  # noqa: E402

try:
    import ab_a3
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import ab_a3

AU = 'facs.code.au{:02d}'


def sided(code, value):
    return {f'{AU.format(code)}_left': value, f'{AU.format(code)}_right': value}


class Table(unittest.TestCase):
    def setUp(self):
        self.data = facs_codec.table()

    def test_49_mapped_signals_from_27_codes(self):
        signals = facs_codec.signals()
        self.assertEqual(len(signals), 49)
        self.assertEqual(len(set(signals)), 49)
        rows = [e['disposition'] for e in self.data['codes'].values()]
        self.assertEqual((rows.count('mapped'), rows.count('unresolved'), rows.count('excluded')), (27, 25, 18))
        self.assertIn('facs.code.au30_left', signals)
        self.assertIn('facs.code.au17', signals)
        self.assertNotIn('facs.code.au17_left', signals)

    def test_the_letters_are_the_expression_library_table(self):
        library = json.loads((ROOT / 'examples/data/expressions.json').read_text(encoding='utf-8'))
        self.assertEqual(self.data['letters'], library['intensity'])
        self.assertEqual(self.data['letters'], {'A': 0.2, 'B': 0.4, 'C': 0.6, 'D': 0.8, 'E': 1.0})

    def test_every_visibility_region_holds_only_mapped_codes_and_together_all_of_them(self):
        mapped = {c for c, e in self.data['codes'].items() if e['disposition'] == 'mapped'}
        regions = [set(v['leave_out']) for c, v in self.data['visibility'].items() if v['leave_out'] != 'all']
        self.assertEqual(set().union(*regions), mapped)
        self.assertEqual(sum(map(len, regions)), len(mapped))


class Read(unittest.TestCase):
    def values(self, notation):
        reading = facs_codec.read(notation)
        self.assertIsNotNone(reading.values, reading.refused)
        return reading

    def nonzero(self, notation):
        return {k: v for k, v in self.values(notation).values.items() if v}

    def test_letters_and_a_letterless_code(self):
        self.assertEqual(self.nonzero('1A+2B+4C+5D+7E'),
                         {**sided(1, 0.2), **sided(2, 0.4), **sided(4, 0.6), **sided(5, 0.8), **sided(7, 1.0)})
        for notation, expected in (('1', sided(1, 0.6)), ('27', {AU.format(26): 0.6}), ('45', sided(43, 0.6)),
                                   ('L46', {f'{AU.format(43)}_left': 0.6})):
            with self.subTest(notation):
                self.assertEqual(self.nonzero(notation), expected)

    def test_library_numbers_are_taken_as_is(self):
        self.assertEqual(self.nonzero({'1': 0.8, 'R12': 'A', 'L46': 1.0, '17': 0.3}),
                         {**sided(1, 0.8), f'{AU.format(12)}_right': 0.2, f'{AU.format(43)}_left': 1.0,
                          AU.format(17): 0.3})

    def test_sides_and_directions(self):
        self.assertEqual(self.nonzero('L12B+R6'), {f'{AU.format(12)}_left': 0.4, f'{AU.format(6)}_right': 0.6})
        self.assertEqual(self.nonzero('L30D'), {f'{AU.format(30)}_left': 0.8})
        self.assertEqual(self.nonzero('17C+26'), {AU.format(17): 0.6, AU.format(26): 0.6})

    def test_absent_codes_are_zero_and_every_mapped_signal_has_a_value(self):
        reading = self.values('')
        self.assertEqual(reading.values, dict.fromkeys(facs_codec.signals(), 0.0))
        self.assertEqual(len(self.values('12C').values), 49)

    def test_refusals_name_the_codes(self):
        for notation, code in (('U12', 'U12'), ('A12C', 'A12C'), ('30', '30'), ('46', '46'), ('L17', 'L17'),
                               ('L26', 'L26'), ('L27', 'L27'), ('L37', 'L37'), ('R37B', 'R37B'), ('1+1B', '1B'),
                               ('L12+L12', 'L12'), ('26+27', '27'),
                               ('43+45', '45'), ('45+L46', 'L46'), ('L43+L46', 'L46'), ('12+L12', 'L12'),
                               ('L70', 'L70'), ('3', '3'), ('M7', 'M7'), ('97', '97'), ('12F', '12F'),
                               ('1++2', '(empty)'),
                               ({'12': 'F'}, '12'), ({'12': True}, '12'), ({'X12': 'C'}, 'X12')):
            with self.subTest(notation):
                reading = facs_codec.read(notation)
                self.assertIsNone(reading.values)
                self.assertTrue(any(code in r for r in reading.refused), reading.refused)

    def test_codes_read_as_another_code(self):
        self.assertEqual(self.nonzero('1+2+5B+27'), {**sided(1, 0.6), **sided(2, 0.6), **sided(5, 0.4),
                                                     AU.format(26): 0.6})
        self.assertEqual(self.nonzero('45E'), sided(43, 1.0))
        self.assertEqual(self.nonzero('R46B'), {f'{AU.format(43)}_right': 0.4})
        self.assertEqual(self.nonzero('L46+R46'), sided(43, 0.6))

    def test_codes_scored_instead_of_a_mapped_code_leave_its_signals_out_never_zero(self):
        for notation, left_out in (('33', sided(34, 0)), ('37', {AU.format(19): 0}), ('41', sided(43, 0)),
                                   ('42', sided(43, 0)), ('44', {**sided(43, 0), **sided(7, 0)}),
                                   ('L44', {f'{AU.format(43)}_left': 0, f'{AU.format(7)}_left': 0}),
                                   ('R33', {f'{AU.format(34)}_right': 0}), ('L41', {f'{AU.format(43)}_left': 0}),
                                   ('R42', {f'{AU.format(43)}_right': 0}),
                                   ('43E+41', sided(43, 0)), ('7C+44', {**sided(43, 0), **sided(7, 0)})):
            with self.subTest(notation):
                reading = self.values(notation)
                self.assertEqual(set(reading.left_out), set(left_out))
                self.assertFalse(set(left_out) & set(reading.values))
                self.assertEqual(len(reading.values) + len(left_out), 49)

    def test_visibility_codes_leave_their_region_out(self):
        self.assertEqual(set(self.values('70').left_out), {**sided(1, 0), **sided(2, 0), **sided(4, 0)}.keys())
        self.assertEqual(len(self.values('71').left_out), 8)
        self.assertEqual(len(self.values('72').left_out), 49 - 6 - 8)
        for code in ('73', '74'):
            self.assertEqual(self.values(f'12C+{code}').values, {})

    def test_codes_with_no_signal_are_listed_as_not_read(self):
        reading = self.values('11+13B+25+61+62+63+64+M61+M55C+51+21+0+97*C+12C')
        self.assertEqual(reading.not_read, ('11', '13B', '25', '61', '62', '63', '64', 'M61', 'M55C', '51', '21', '0',
                                            '97*C'))
        self.assertEqual(self.nonzero('11+13B+25+61+62+63+64+M61+M55C+51+21+0+12C'), sided(12, 0.6))

    def test_decode_thresholds_and_the_letter_round_trip(self):
        for value, shown in ((0.0, ''), (0.09999999999999999, ''), (0.1, 'A'), (0.29, 'A'), (0.3, 'B'), (0.5, 'C'),
                             (0.7, 'D'), (0.9, 'E'), (1.0, 'E')):
            self.assertEqual(facs_codec.letter(value), shown, value)
        for name in 'ABCDE':
            reading = self.values(f'12{name}')
            self.assertEqual(facs_codec.letter(reading.values[f'{AU.format(12)}_left']), name)
        with self.assertRaises(ValueError):
            facs_codec.letter(1.5)


class Library(unittest.TestCase):
    def test_all_22_library_expressions_convert_to_what_a3_gives_b(self):
        lib = ab_a3.library()
        rows = ab_a3.expression_rows(lib, ab_a3.channels())
        b = ab_a3.b_inputs(facs_codec)
        held = {row['segment']: b[n] for n, row in enumerate(rows) if row['phase'] == 'hold'}
        self.assertEqual(len(lib['expressions']), 22)
        for expression in lib['expressions']:
            with self.subTest(expression['name']):
                reading = facs_codec.read(expression['aus'])
                self.assertIsNotNone(reading.values, reading.refused)
                self.assertEqual(reading, held[expression['name']])


if __name__ == '__main__':
    unittest.main()
