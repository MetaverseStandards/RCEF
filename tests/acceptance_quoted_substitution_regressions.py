# SPDX-License-Identifier: MIT
"""Independent quote ownership controls; recipe strings are never executed."""
import unittest
import acceptance_substitution_regressions as boundaries


class QuotedSubstitutionOwnership(unittest.TestCase):
    def test_inner_quotes_cannot_hide_later_active_runner(self):
        script = r"""echo "$(printf "x'")"#$(python "scripts/run_accep""tance.py" --tools-path ../.ci-tools)\'"""
        boundaries.SubstitutionBoundaries.check_all(self, script, True)

    def test_inner_quotes_cannot_hide_unquoted_heredoc_header(self):
        script = "cat \"$(printf \"x'\")\"# <<DATA\necho '$(python scripts/run_acceptance.py --tools-path ../.ci-tools)'\nDATA"
        boundaries.SubstitutionBoundaries.check_all(self, script, True)

    def test_real_outer_comment_after_quoted_substitution_stays_literal(self):
        script = r"""echo "$(printf "x'")" #$(python "scripts/run_accep""tance.py" --tools-path ../.ci-tools)\'"""
        boundaries.SubstitutionBoundaries.check_all(self, script, False)


if __name__ == '__main__':
    unittest.main(verbosity=2)
