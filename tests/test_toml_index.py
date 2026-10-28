# SPDX-License-Identifier: MIT
"""docs/toml-index.csv lists every TOML authoring file with its current counts and hash."""
import csv
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('export_toml_index', ROOT / 'scripts/export_toml_index.py')
export_toml_index = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export_toml_index)


class TomlIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / 'docs/toml-index.csv').read_text(encoding='utf-8')
        cls.rows = list(csv.DictReader(cls.text.splitlines()))
        cls.pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))

    def test_index_is_generated_from_the_tree(self):
        self.assertEqual(self.text, export_toml_index.render(),
                         'docs/toml-index.csv is out of date; run scripts/export_toml_index.py --write')

    def test_one_row_per_authoring_file(self):
        self.assertEqual([r['path'] for r in self.rows],
                         [f.relative_to(ROOT).as_posix() for f in export_toml_index.authoring_files()])

    def test_totals_match_the_pack(self):
        total = {c: sum(int(r[c]) for r in self.rows) for c in ('signals', 'profiles', 'mappings', 'evidence')}
        self.assertEqual(total, {k: len(self.pack[k]) for k in total})
        self.assertEqual(sum(int(r['rules']) for r in self.rows),
                         sum(len(m['rules']) for m in self.pack['mappings']))
        self.assertEqual(sum(int(r['membership_rows']) for r in self.rows),
                         sum(len(p['signal_ids']) for p in self.pack['profiles']))


if __name__ == '__main__':
    unittest.main()
