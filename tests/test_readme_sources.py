# SPDX-License-Identifier: MIT
"""The README's pivot sentence, routes, mapping and expression-set tables, and docs/expression-sets.md agree with the data."""
import json
from pathlib import Path
import re
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
PIVOT = ('RCEF is a pivot for translating between expression sets. It is not a set that everyone must adopt. '
         'Each canonical signal has a declared meaning, but no shared or measured gain.')
THROUGH = {'canonical expression set': 'expression', 'canonical viseme set': 'viseme',
           'canonical viseme set, viseme pose bridge, canonical expression set': 'bridge'}
LINK = re.compile(r'\[[^\]]*\]\(([^)]+)\)')


def table_rows(text, start, end):
    section = text[text.index(start):text.index(end, text.index(start))]
    return [[cell.strip() for cell in line.strip('|').split(' | ')]
            for line in section.splitlines() if line.startswith('| [')]


class ReadmeSources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        cls.mappings = table_rows(readme, '### Mappings', '### Expression sets')
        overview = readme[readme.index('### Expression sets'):readme.index('## Getting started')]
        cls.overview = [[cell.strip() for cell in line.strip('|').split(' | ')]
                        for line in overview.splitlines()[1:] if line.startswith('| ') and '---' not in line][1:]
        # docs/expression-sets.md links up one level; read its links as paths from the checkout root.
        sets_doc = (ROOT / 'docs/expression-sets.md').read_text(encoding='utf-8').replace('](../', '](')
        cls.sets = table_rows(sets_doc, '## Where each set comes from', '## Signal counts')
        cls.evidence = {r['id']: r for r in
                        tomllib.loads((ROOT / 'evidence/sources.toml').read_text(encoding='utf-8'))['evidence']}
        cls.files = {p.name: tomllib.loads(p.read_text(encoding='utf-8')) for p in (ROOT / 'profiles').glob('*.toml')}
        cls.pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        cls.members = {p['id']: set(p['signal_ids']) for p in cls.pack['profiles']}
        cls.file_of = {p['id']: name for name, data in cls.files.items() for p in data.get('profiles', [])}

    def row_for(self, name):
        return next(r for r in self.sets if r[0].startswith(f'[`profiles/{name}`]'))

    def test_every_profile_file_has_one_row(self):
        names = [re.match(r'\[`profiles/([^`]+)`\]\(profiles/\1\)', r[0]).group(1) for r in self.sets]
        self.assertEqual(sorted(names), sorted(self.files))
        self.assertTrue(all(len(r) == 7 for r in self.sets))

    def test_signal_counts_match_the_profile_files(self):
        for name, data in self.files.items():
            with self.subTest(profile=name):
                self.assertEqual(int(self.row_for(name)[2]), len(data['signals']))

    def test_pinned_sources_are_the_evidence_the_signals_cite(self):
        for name, data in self.files.items():
            with self.subTest(profile=name):
                row = self.row_for(name)
                pinned = LINK.findall(row[5])
                self.assertTrue(all(link.startswith('references.md#') for link in pinned), pinned)
                ids = {link.split('#', 1)[1] for link in pinned}
                self.assertLessEqual(ids, set(self.evidence))
                self.assertEqual(ids, {e for s in data['signals'] for e in s.get('evidence', [])})
                # Revisions and retrieval dates quoted in the description are the pinned ones.
                for short in re.findall(r'`([0-9a-f]{7})`', row[1]):
                    self.assertTrue(any(self.evidence[i].get('revision', '').startswith(short) for i in ids), short)
                for date in re.findall(r'retrieved (\d{4}-\d{2}-\d{2})', row[1]):
                    self.assertTrue(any(self.evidence[i].get('retrieved') == date for i in ids), date)

    def test_documentation_links_are_web_pages_not_data_endpoints(self):
        for row in self.sets:
            for link in LINK.findall(row[4]):
                with self.subTest(link=link):
                    if link.startswith('http'):
                        self.assertNotIn('raw.githubusercontent.com', link)
                        self.assertFalse(link.endswith('.json'))
                    else:
                        self.assertTrue((ROOT / link).exists(), link)

    def test_roles_follow_the_executable_mappings(self):
        read, written = set(), set()
        signal_file = {sid: self.file_of[pid] for pid, sids in self.members.items()
                       if pid in self.file_of for sid in sids}
        for mapping in self.pack['mappings']:
            for rule in mapping['rules']:
                if rule['disposition'] == 'mapped':
                    read |= {signal_file[s] for s in rule['inputs'] if s in signal_file}
                    written |= {signal_file[s] for s in rule['outputs'] if s in signal_file}
        for name in self.files:
            with self.subTest(profile=name):
                expected = ('source and target' if name in read and name in written else 'source' if name in read
                            else 'target' if name in written else 'inventory only')
                role = self.row_for(name)[3]
                self.assertTrue(role == expected or role.startswith(expected + ' ('), (role, expected))

    def test_readme_overview_lists_each_profile_file_once_in_its_role_column(self):
        names = {Path(name).stem for name in self.files}
        columns = {}
        for row in self.overview:
            self.assertEqual(len(row), 3, row)
            for column in (1, 2):
                for token in re.findall(r'`([^`]+)`', row[column]):
                    if token in names:
                        self.assertNotIn(token, columns)
                        columns[token] = column
                    else:
                        self.assertIn(token, self.members)
        self.assertEqual(set(columns), names)
        for name in self.files:
            with self.subTest(profile=name):
                inventory_only = self.row_for(name)[3].startswith('inventory only')
                self.assertEqual(columns[Path(name).stem], 2 if inventory_only else 1)

    def test_mapping_table_lists_each_map_set_once_with_its_page(self):
        listed = {}
        for row in self.mappings:
            found = re.match(r'\[`([^`]+)`\]\(docs/map-sets/([^)]+)\.md\)$', row[0])
            self.assertIsNotNone(found, row[0])
            self.assertEqual(found.group(1), found.group(2))
            self.assertTrue((ROOT / f'docs/map-sets/{found.group(1)}.md').is_file(), found.group(1))
            source, target = re.match(r'`([^`]+)` → `([^`]+)`', row[1]).groups()
            listed[found.group(1)] = (source, target, int(row[2]), int(row[3]), set(row[4].split(', ')))
        self.assertEqual(len(listed), len(self.mappings))
        # Synthetic test maps and unresolved maps are left out of the table.
        fixture = self.members['fixture.source'] | self.members['fixture.target']
        shown = [m for m in self.pack['mappings']
                 if any(r['disposition'] == 'mapped' for r in m['rules'])
                 and not {s for r in m['rules'] for s in r['inputs'] + r['outputs']} <= fixture]
        self.assertEqual(set(listed), {m['id'] for m in shown})
        signals = {s['id']: s for s in self.pack['signals']}
        canonical = self.members['rcef.canonical_expression'] | self.members['rcef.canonical_viseme']
        seen = set()
        for mapping in shown:
            with self.subTest(mapping=mapping['id']):
                source, target, count, parts, statuses = listed[mapping['id']]
                rules = mapping['rules']
                self.assertEqual(count, len(rules))
                self.assertEqual(statuses, {r['evidence_status'] for r in rules})
                # Values a map computes for its own later rules are RCEF intermediates.
                computed = {s for r in rules for s in r['outputs']} & {s for r in rules for s in r['inputs']}
                self.assertLessEqual(computed, self.members.get('rcef.intermediate', set()))
                self.assertLessEqual({s for r in rules for s in r['inputs']} - computed, self.members[source])
                self.assertLessEqual({s for r in rules for s in r['outputs']} - computed, self.members[target])
                # One map per set pair and direction, named <from>.to_<to>.
                self.assertNotIn((source, target), seen)
                seen.add((source, target))
                keys = {'rcef.canonical_expression': 'rcef_expression', 'rcef.canonical_viseme': 'rcef_viseme'}
                start, end = mapping['id'].split('.to_')
                self.assertEqual(keys.get(source, start) == start and keys.get(target, end) == end, True)
                # Its parts: the canonical groups that its mappings read or write directly.
                groups = {signals[s]['metadata']['group'] for r in rules for s in r['inputs'] + r['outputs']
                          if s in canonical}
                self.assertEqual(parts, len(groups))


class ReadmeRoutes(unittest.TestCase):
    """The README states the pivot sentence, and its Routes table lists every route Route can run."""

    @classmethod
    def setUpClass(cls):
        cls.readme = (ROOT / 'README.md').read_text(encoding='utf-8')

    def test_pivot_sentence(self):
        purpose = self.readme[self.readme.index('## Purpose'):self.readme.index('## Contents')]
        self.assertIn(PIVOT, ' '.join(purpose.split()))

    def test_routes_table_matches_route(self):
        import sys
        sys.path.insert(0, str(ROOT / 'examples'))
        from rcef_route import Route
        from rcef_translate import load_pack
        section = self.readme[self.readme.index('### Routes'):self.readme.index('### Mappings')]
        listed = set()
        for line in section.splitlines():
            if line.startswith('| `'):
                source, through, targets = [c.strip() for c in line.strip('|').split(' | ')]
                for target in re.findall(r'`([^`]+)`', targets):
                    listed.add((source.strip('`'), THROUGH[through], target))
        pack = load_pack(json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8')))
        sets = [p['id'] for p in pack.document['profiles'] if not p['id'].startswith(('rcef.', 'fixture'))]
        found, compiled = set(), {}
        for source in sets:
            for target in sets:
                route = Route(source, target, pack=pack, compiled=compiled)
                compiled.update(route.mappings)
                if not route.in_maps:
                    continue
                into = {m: dst for m, _, dst in route.hops}
                out_of = {m: src for m, src, _ in route.hops}
                if any(into[m] == 'rcef.canonical_expression' for m in route.in_maps):
                    found.add((source, 'expression', target))
                if (any(into[m] == 'rcef.canonical_viseme' for m in route.in_maps)
                        and any(out_of[m] == 'rcef.canonical_viseme' for m in route.out_maps)):
                    found.add((source, 'viseme', target))
                if route.bridges:
                    found.add((source, 'bridge', target))
        self.assertEqual(listed, found)
        self.assertIn(f'the {len({(s, t) for s, _, t in found})} routes', section)


if __name__ == '__main__':
    unittest.main()
