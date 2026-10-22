# SPDX-License-Identifier: MIT
"""Preserve refusal of quote-assembled protected paths inside substitution words."""
import unittest
from acceptance_substitution_regressions import SubstitutionBoundaries

class SubstitutionGrammar(unittest.TestCase):
    def test_quote_assembled_runner_path_stays_visible_to_inspection(self):
        SubstitutionBoundaries.check_all(self,
            'echo x$(python "scripts/run_accep""tance.py" --tools-path ../.ci-tools)', True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
