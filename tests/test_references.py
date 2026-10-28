# SPDX-License-Identifier: MIT
"""references.md agrees with evidence/sources.toml."""
import importlib.util
from pathlib import Path
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('export_references', ROOT / 'scripts/export_references.py')
export_references = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export_references)


class References(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = tomllib.loads((ROOT / 'evidence/sources.toml').read_text(encoding='utf-8'))['evidence']

    def test_references_md_is_generated_from_sources_toml(self):
        self.assertEqual((ROOT / 'references.md').read_text(encoding='utf-8'),
                         export_references.render(self.records))


if __name__ == '__main__':
    unittest.main()
