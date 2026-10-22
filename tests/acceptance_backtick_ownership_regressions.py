# SPDX-License-Identifier: MIT
"""Inert backtick quote ownership controls; no returned text execution."""
import unittest

import acceptance_substitution_regressions as boundaries


class BacktickOwnership(unittest.TestCase):
    def test_inner_quotes_cannot_hide_backtick_runner(self):
        script = r"""echo "`printf "x'"`"#`python "scripts/run_accep""tance.py" --tools-path ../.ci-tools`\'"""
        boundaries.SubstitutionBoundaries.check_all(self, script, True)

    def test_single_quoted_backtick_word_stays_literal(self):
        script = "echo '`printf x`#`python scripts/run_acceptance.py`'"
        boundaries.SubstitutionBoundaries.check_all(self, script, False)


    def test_simple_active_backtick_word_stays_admitted(self):
        script = "echo `printf x`#safe"
        boundaries.SubstitutionBoundaries.check_all(self, script, False)


if __name__ == '__main__':
    unittest.main(verbosity=2)
