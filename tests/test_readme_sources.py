# SPDX-License-Identifier: MIT
"""The README's expression-set and mapping tables agree with the data they describe."""
import json
from pathlib import Path
import re
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
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
        cls.sets = table_rows(readme, '### Expression sets', '## Generate and check')
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

    def test_mapping_table_matches_the_pack(self):
        listed = {}
        for row in self.mappings:
            mapping_id = re.match(r'\[`([^`]+)`\]\(reports/mappings\.md#([^)]+)\)', row[0])
            self.assertEqual(mapping_id.group(2), mapping_id.group(1).replace('.', ''))
            source, target = re.match(r'`([^`]+)` → `([^`]+)`', row[1]).groups()
            listed[mapping_id.group(1)] = (source, target, int(row[2]), row[3].split(' (')[0])
        self.assertEqual(set(listed), {m['id'] for m in self.pack['mappings']})
        for mapping in self.pack['mappings']:
            with self.subTest(mapping=mapping['id']):
                source, target, count, status = listed[mapping['id']]
                rules = mapping['rules']
                self.assertEqual(count, len(rules))
                self.assertEqual({status}, {r['evidence_status'] for r in rules})
                self.assertLessEqual({s for r in rules for s in r['inputs']}, self.members[source])
                self.assertLessEqual({s for r in rules for s in r['outputs']}, self.members[target])


if __name__ == '__main__':
    unittest.main()
