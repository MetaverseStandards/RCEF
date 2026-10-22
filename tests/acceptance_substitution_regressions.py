# SPDX-License-Identifier: MIT
"""Inert closed-substitution and actual-header cases through recipe ingress."""
from pathlib import Path
import unittest

from gate_recipes import _runner_script, subset_script, document_recipe, workflow_recipe

DIRECT = 'echo x$(printf x)#$(python scripts/run_acceptance.py --tools-path ../.ci-tools)'
HEADER = "cat $(printf x)# <<DATA\necho '$(python scripts/run_acceptance.py --tools-path ../.ci-tools)'\nDATA"
DIRECT_COMMENT = 'echo x$(printf x) #$(python scripts/run_acceptance.py --tools-path ../.ci-tools)'
HEADER_COMMENT = "cat $(printf x) # <<DATA\necho '$(python scripts/run_acceptance.py --tools-path ../.ci-tools)'\nDATA"
EVENTS = []

def document(script):
    return '<!-- RCEF:BEGIN ACCEPTANCE -->\n```sh\n' + script + '\n```\n<!-- RCEF:END ACCEPTANCE -->\n'

def workflow(script):
    return ('name: Construction control\non:\n  workflow_dispatch:\njobs:\n  parity:\n'
            '    runs-on: ubuntu-latest\n    env:\n'
            '      MSF_TOOLS_PATH: ${{ github.workspace }}/.ci-tools\n'
            '      PYTHONPATH: ${{ github.workspace }}/.ci-tools\n'
            '    steps:\n      - run: |\n' +
            '\n'.join('          ' + line for line in script.split('\n')) +
            '\n        working-directory: RCEF\n')

class SubstitutionBoundaries(unittest.TestCase):
    def check_all(self, script, refusal):
        variants = [('_runner_script', True), ('_runner_script', False), ('subset_script', True),
                    ('document_recipe', True), ('document_recipe', False),
                    ('workflow_recipe', True), ('workflow_recipe', False)]
        for entry, subset in variants:
            with self.subTest(entry=entry, subset=subset):
                source = document(script) if entry == 'document_recipe' else workflow(script) if entry == 'workflow_recipe' else script
                event = {'id': self.id(), 'entry': entry, 'subset': subset, 'source': source,
                         'expected': 'REFUSE' if refusal else 'ACCEPT_EXACT'}
                EVENTS.append(event)
                try:
                    if entry == '_runner_script': value = _runner_script(source, subset=subset)
                    elif entry == 'subset_script': value = subset_script(source)
                    elif entry == 'document_recipe': value = document_recipe(source, subset=subset)
                    else: value = workflow_recipe(source, Path('/rcef-control-workspace'), {'PATH':'/usr/bin:/bin'}, subset=subset)
                except ValueError as error:
                    event.update(actual='REFUSE', exception_type='ValueError', message=str(error))
                    self.assertTrue(refusal, 'genuine comment or literal refused')
                else:
                    output = value['script'] if isinstance(value, dict) else value
                    event.update(actual='ACCEPT', output=output)
                    self.assertFalse(refusal, 'active runner substitution or actual heredoc header accepted')
                    self.assertEqual(output, script)

    def test_closed_substitution_keeps_adjacent_hash_in_word(self):
        self.check_all(DIRECT, True)

    def test_closed_substitution_cannot_hide_actual_unquoted_heredoc(self):
        self.check_all(HEADER, True)

    def test_blank_after_closed_substitution_starts_real_comment(self):
        self.check_all(DIRECT_COMMENT, False)

    def test_real_comment_hides_header_and_keeps_next_line_literal(self):
        self.check_all(HEADER_COMMENT, False)

    def test_quoted_substitution_is_literal(self):
        self.check_all("echo 'x$(printf x)#$(python scripts/run_acceptance.py)'", False)

    def test_quoted_heredoc_remains_literal_after_substitution_word(self):
        self.check_all("cat $(printf x)# <<'DATA'\n$(python scripts/run_acceptance.py)\nDATA", False)

if __name__ == '__main__':
    unittest.main(verbosity=2)
