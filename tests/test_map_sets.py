# SPDX-License-Identifier: MIT
"""docs/map-sets/: one page per map set, current with the pack, and what each page states, read from the pack here.

A map set is one map between an expression set and a canonical set in one direction, or the viseme pose bridge.
scripts/export_map_sets.py writes the pages; these tests check that they are current, and check the counts that
the pages show against the pack without the script: the mappings of each part, the parts the map does not have,
and the evidence records.
"""
import contextlib
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import export_map_sets  # noqa: E402

CANONICAL = ('rcef.canonical_expression', 'rcef.canonical_viseme')


class MapSetPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        cls.signals = {s['id']: s for s in cls.pack['signals']}
        cls.members = {p['id']: p['signal_ids'] for p in cls.pack['profiles']}
        cls.groups = {s: cls.signals[s]['metadata']['group'] for c in CANONICAL for s in cls.members[c]}
        cls.pages = {p.stem: p.read_text(encoding='utf-8') for p in (ROOT / 'docs/map-sets').glob('*.md')}
        cls.files = [f'docs/map-sets/{name}.md' for name in cls.pages]

    def test_the_pages_are_current(self):
        rendered = export_map_sets.render(ROOT)
        self.assertEqual(set(rendered), {f'docs/map-sets/{name}.md' for name in self.pages},
                         'run scripts/export_map_sets.py --write')
        for path, content in rendered.items():
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_text(encoding='utf-8'), content,
                                 'run scripts/export_map_sets.py --write')

    def test_one_page_for_each_map_with_a_canonical_signal(self):
        expected = {m['id'] for m in self.pack['mappings']
                    if any(r['disposition'] == 'mapped' for r in m['rules'])
                    and any(s in self.groups for r in m['rules'] for s in r['inputs'] + r['outputs'])}
        self.assertEqual(set(self.pages), expected)
        self.assertEqual(len(expected), 16)

    def test_each_part_lists_its_mappings_and_together_they_are_the_map(self):
        for mapping in self.pack['mappings']:
            text = self.pages.get(mapping['id'])
            if text is None:
                continue
            with self.subTest(map=mapping['id']):
                section = text[text.index('## Mappings by part'):text.index('## Evidence')]
                listed = {}
                for group, ids in re.findall(r'^- `(\w+)`: (.+)\.$', section, re.M):
                    listed[group] = re.findall(r'`([^`]+)`', ids)
                every = [r for ids in listed.values() for r in ids]
                self.assertEqual(sorted(every), sorted(r['id'] for r in mapping['rules']))
                self.assertEqual(len(every), len(set(every)))
                rules = {r['id']: r for r in mapping['rules']}
                for group, ids in listed.items():
                    # A part's mappings read or write its group, or reach it through intermediate values.
                    direct = [i for i in ids if group in {self.groups.get(s) for s in rules[i]['inputs'] +
                                                          rules[i]['outputs']}]
                    self.assertTrue(direct, group)
                table = text[text.index('## Parts\n'):text.index('## Mappings by part')]
                counts = {g: int(n) for g, n in re.findall(r'^\| `(\w+)` \| \d+ of \d+ \| (\d+) \|', table, re.M)}
                self.assertEqual(counts, {g: len(ids) for g, ids in listed.items()})
                self.assertIn(f'- Mappings: {len(rules)}, in {len(listed)} parts.', text)

    def test_the_parts_a_map_does_not_have_are_the_groups_it_never_touches(self):
        for mapping in self.pack['mappings']:
            text = self.pages.get(mapping['id'])
            if text is None:
                continue
            touched = {s for r in mapping['rules'] for s in r['inputs'] + r['outputs']}
            canonical = [c for c in CANONICAL if touched & set(self.members[c])]
            # The bridge reads the viseme set and writes the expression set; its missing parts are expression groups.
            target = 'rcef.canonical_expression' if len(canonical) == 2 else canonical[0]
            have = {self.groups[s] for s in touched if s in self.members[target]}
            groups = next(p['metadata']['groups'] for p in self.pack['profiles'] if p['id'] == target)
            with self.subTest(map=mapping['id']):
                section = text[text.index('## Parts this map does not have'):]
                listed = re.findall(r'^- `(\w+)` \((\d+)\)', section, re.M)
                self.assertEqual([g for g, _ in listed], [g for g in groups if g not in have])
                for group, n in listed:
                    self.assertEqual(int(n), sum(self.groups[s] == group for s in self.members[target]))
                if not listed:
                    self.assertIn('None:', section)

    def test_the_evidence_table_counts_the_mappings_that_cite_each_record(self):
        for mapping in self.pack['mappings']:
            text = self.pages.get(mapping['id'])
            if text is None:
                continue
            with self.subTest(map=mapping['id']):
                rows = dict(re.findall(r'^\| \[`([^`]+)`\]\(\.\./\.\./references\.md#[\w-]+\) \| (\d+) \|', text, re.M))
                expected = {}
                for rule in mapping['rules']:
                    for record in rule['evidence']:
                        expected[record] = expected.get(record, 0) + 1
                self.assertEqual({k: int(v) for k, v in rows.items()}, expected)

    def test_a_split_map_is_two_pages_and_a_stale_page_is_reported_and_removed(self):
        document = json.loads(json.dumps(self.pack))
        mapping = next(m for m in document['mappings'] if m['id'] == 'fb2.to_rcef_expression')
        gaze = [r for r in mapping['rules'] if self.groups.get(r['outputs'][0]) == 'gaze']
        mapping['rules'] = [r for r in mapping['rules'] if r not in gaze]
        document['mappings'].append({'id': 'fb2_gaze.to_rcef_expression', 'rules': gaze})
        sets = {e['id'] for e in export_map_sets.map_sets(document)}
        self.assertIn('fb2_gaze.to_rcef_expression', sets)
        self.assertEqual(len(sets), 17)
        # A page with no map behind it is reported as out of date, and --write removes it.
        with tempfile.TemporaryDirectory(prefix='rcef-map-sets-') as temp:
            root = Path(temp)
            for path in ('generated/rcef.pack.json', 'docs/canonical-set-audit.md', *self.files):
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / path).write_bytes((ROOT / path).read_bytes())
            stale = root / 'docs/map-sets/fb2_face.to_rcef.md'
            stale.write_text('old page\n', encoding='utf-8')
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(export_map_sets.main([], root), 1)
            self.assertIn('docs/map-sets/fb2_face.to_rcef.md out of date', out.getvalue())
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(export_map_sets.main(['--write'], root), 0)
            self.assertFalse(stale.exists())
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(export_map_sets.main([], root), 0)


if __name__ == '__main__':
    unittest.main()
