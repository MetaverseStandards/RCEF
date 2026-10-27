# SPDX-License-Identifier: MIT
"""RCEF's FB2 -> ARKit mappings against the routes in the Godot and VRCFT sources."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('compare_godot', ROOT / 'scripts/compare_godot.py')
compare_godot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compare_godot)


class GodotComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        cls.routes = (ROOT / 'tests/fixtures/godot_fb2_rules.csv').read_text(encoding='utf-8')

    def test_committed_comparison_is_current(self):
        self.assertEqual((ROOT / 'docs/godot_comparison.md').read_text(encoding='utf-8'),
                         compare_godot.render(self.pack, self.routes))

    def test_only_brow_inner_up_departs_from_godot(self):
        rows = [r for r in compare_godot.compare(self.pack, self.routes) if r['mapping'] != '—']
        self.assertEqual(len(rows), 52)
        results = {r['arkit']: r['result'] for r in rows}
        self.assertEqual(results.pop('browInnerUp'), "Godot has no route; RCEF follows VRCFT's average")
        self.assertEqual(set(results.values()), {'agrees with Godot'})

    def test_a_changed_weight_is_reported(self):
        pack = json.loads(json.dumps(self.pack))
        rule = next(r for m in pack['mappings'] if m['id'] == 'fb2.to_arkit' for r in m['rules']
                    if r['outputs'] == ['arkit.coefficient.cheekPuff'])
        rule['operator']['weights'] = [0.75, 0.25]
        row = next(r for r in compare_godot.compare(pack, self.routes) if r['arkit'] == 'cheekPuff')
        self.assertEqual(row['result'], 'DISAGREES with Godot')


if __name__ == '__main__':
    unittest.main()
