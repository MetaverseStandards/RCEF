# SPDX-License-Identifier: MIT
"""docs/retired-ids.csv: one tombstone for each ID that the pack no longer has, and no other.

The IDs are those of the A1 baseline and of the B pack of every committed A/B registration, so an ID added
after the baseline and removed later needs a tombstone too.
"""
import csv
import json
from pathlib import Path
import unittest

try:
    import shared_pack
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import shared_pack

ROOT = Path(__file__).resolve().parents[1]


def ids(document):
    """Every ID in a pack document, with its kind."""
    found = {}
    for mapping in document['mappings']:
        found[mapping['id']] = 'map'
        found.update({rule['id']: 'mapping' for rule in mapping['rules']})
    found.update({p['id']: 'profile' for p in document['profiles']})
    found.update({s['id']: 'signal' for s in document['signals']})
    found.update({e['id']: 'evidence' for e in document['evidence']})
    return found


class RetiredIds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'docs/retired-ids.csv').open(encoding='utf-8', newline='') as handle:
            cls.rows = list(csv.DictReader(handle))
        cls.live = ids(shared_pack.document())
        cls.baseline = ids(json.loads((ROOT / 'tests/fixtures/baseline-dea1713.pack.json').read_text(encoding='utf-8')))
        cls.registered = {}
        for path in sorted((ROOT / 'ab').glob('*.abreg')):
            document = shared_pack.registered_pack(path.relative_to(ROOT).as_posix())
            if document is not None:
                cls.registered[path.name] = ids(document)
        cls.known = {**cls.baseline}
        for found in cls.registered.values():
            for key, kind in found.items():
                if cls.known.setdefault(key, kind) != kind:
                    raise AssertionError(f'{key} is a {kind} in one pack and a {cls.known[key]} in another')

    def test_every_missing_baseline_id_has_exactly_one_tombstone(self):
        tombstones = [r['id'] for r in self.rows]
        self.assertEqual(len(tombstones), len(set(tombstones)))
        self.assertEqual(set(tombstones), {i for i in self.known if i not in self.live})
        for row in self.rows:
            with self.subTest(row['id']):
                self.assertEqual(row['kind'], self.known[row['id']])
                self.assertTrue(row['retired_in'] and row['note'])

    def test_the_registered_b_packs_are_read(self):
        if not self.registered:
            self.skipTest('no Git history for the registered packs')
        self.assertIn('ab.pivot-v1.abreg', self.registered)
        for name, found in self.registered.items():
            with self.subTest(name):
                retired = {r['id'] for r in self.rows}
                self.assertEqual({i for i in found if i not in self.live} - retired, set())

    def test_no_retired_id_is_used_again(self):
        self.assertEqual({r['id'] for r in self.rows} & set(self.live), set())

    def test_a_replacement_exists_where_one_is_named(self):
        for row in self.rows:
            if row['replaced_by'] and not row['replaced_by'].startswith('route '):
                self.assertIn(row['replaced_by'], self.live, row['id'])

    def test_what_was_retired(self):
        kinds = {}
        for row in self.rows:
            kinds[row['kind']] = kinds.get(row['kind'], 0) + 1
        # 7 direct maps and 3 identity maps; their 191 + 21 mappings and the old survey.ambiguous rule; the old
        # canonical profile, its 21 signals and the 4 intermediate values of the old ARKit -> FB2 gaze map. Then the
        # 84 maps of one canonical group each, whose mappings moved unchanged into the 15 maps of one set pair and
        # direction, and the old ID of the viseme pose bridge.
        self.assertEqual(kinds, {'map': 95, 'mapping': 213, 'profile': 1, 'signal': 25})
        merged = [r for r in self.rows if r['kind'] == 'map' and r['replaced_by'] and not r['replaced_by'].startswith('route ')]
        self.assertEqual((len(merged), len({r['replaced_by'] for r in merged})), (85, 16))


if __name__ == '__main__':
    unittest.main()
