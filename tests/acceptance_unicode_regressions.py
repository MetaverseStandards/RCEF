# SPDX-License-Identifier: MIT
"""Independent string-only shell boundary regressions; no recipe execution."""
from pathlib import Path
import unittest

import gate_recipes

EVENTS = []
# These are literal shell word characters, even where Python calls them space
# or a line separator. Each adverse case has quoted and unquoted literal twins.
CHARACTERS = (
    ('nbsp', '\u00a0'), ('ogham', '\u1680'), ('em_space', '\u2003'),
    ('narrow_nbsp', '\u202f'), ('ideographic', '\u3000'),
    ('vertical_tab', '\x0b'), ('form_feed', '\x0c'), ('carriage_return', '\r'),
    ('file_separator', '\x1c'), ('group_separator', '\x1d'),
    ('record_separator', '\x1e'), ('next_line', '\x85'),
    ('line_separator', '\u2028'), ('paragraph_separator', '\u2029'),
)


def workflow(script):
    return ('name: boundary control\non: push\njobs:\n  check:\n'
            '    runs-on: ubuntu-latest\n    env:\n'
            '      MSF_TOOLS_PATH: ${{ github.workspace }}/.ci-tools\n'
            '      PYTHONPATH: ${{ github.workspace }}/.ci-tools\n'
            '    steps:\n      - run: |\n' +
            '\n'.join('          ' + line for line in script.split('\n')) +
            '\n        working-directory: RCEF\n        shell: sh\n')


def document(script):
    return ('<!-- RCEF:BEGIN ACCEPTANCE -->\n```sh\n' + script +
            '\n```\n<!-- RCEF:END ACCEPTANCE -->')


class UnicodeBoundaries(unittest.TestCase):
    def check(self, source, expected, *, entry='runner', script=None):
        for subset in (True, False):
            with self.subTest(entry=entry, subset=subset, source=ascii(source)):
                event = {'test': self.id(), 'entry': entry, 'subset': subset,
                         'source': source, 'expected': expected, 'calls': 1}
                EVENTS.append(event)
                try:
                    if entry == 'runner':
                        value = gate_recipes._runner_script(source, subset=subset)
                    elif entry == 'workflow':
                        value = gate_recipes.workflow_recipe(source, Path('/unicode-control'),
                                                             {'PATH': '/usr/bin:/bin'}, subset=subset)
                    elif entry == 'document':
                        value = gate_recipes.document_recipe(source, subset=subset)
                    else:
                        self.fail('unknown independent entry')
                except ValueError as error:
                    event.update(actual='REFUSE', exception_type='ValueError', message=str(error))
                    self.assertEqual(expected, 'REFUSE', 'literal healthy recipe refused')
                else:
                    event.update(actual='ACCEPT', script=value['script'] if isinstance(value, dict) else value)
                    self.assertEqual(expected, 'ACCEPT', 'active protected substitution accepted')
                    target = source if script is None else script
                    self.assertEqual(event['script'], target, 'literal bytes changed')
                    if entry == 'workflow':
                        self.assertEqual(value['cwd'], Path('/unicode-control/RCEF'))
                        self.assertEqual(value['env'], {'PATH': '/usr/bin:/bin',
                            'MSF_TOOLS_PATH': '/unicode-control/.ci-tools',
                            'PYTHONPATH': '/unicode-control/.ci-tools'})

    def test_ascii_space_comment_healthy(self):
        self.check('echo #$(python3 scripts/run_acceptance.py)', 'ACCEPT')

    def test_ascii_tab_comment_healthy(self):
        self.check('echo\t#$(python3 scripts/run_acceptance.py)', 'ACCEPT')

    def test_ascii_lf_comment_healthy(self):
        self.check('echo harmless\n#$(python3 scripts/run_acceptance.py)', 'ACCEPT')

    def test_workflow_unicode_hash_adverse(self):
        for _, char in CHARACTERS:
            self.check(workflow('echo ' + char + '#$(python3 scripts/run_acceptance.py)'),
                       'REFUSE', entry='workflow')

    def test_workflow_quoted_unicode_healthy(self):
        for _, char in CHARACTERS:
            script = "echo 'left" + char + "#$(python3 scripts/run_acceptance.py)'"
            self.check(workflow(script), 'ACCEPT', entry='workflow', script=script)

    def test_document_unicode_hash_adverse(self):
        for _, char in CHARACTERS:
            self.check(document('echo ' + char + '#$(python3 scripts/run_acceptance.py)'),
                       'REFUSE', entry='document')

    def test_document_quoted_unicode_healthy(self):
        for _, char in CHARACTERS:
            script = "echo 'left" + char + "#$(python3 scripts/run_acceptance.py)'"
            self.check(document(script), 'ACCEPT', entry='document', script=script)

    def test_unicode_heredoc_suffix_refused(self):
        # The delimiter is EOF followed by a literal nonblank. Refusal is the
        # explicit named-ASCII-delimiter limit, before any false body handling.
        for _, char in CHARACTERS:
            self.check('cat <<EOF' + char + '\nbody\nEOF', 'REFUSE')

    def test_quoted_heredoc_unicode_body_healthy(self):
        for _, char in CHARACTERS:
            self.check("cat <<'EOF'\nleft" + char +
                       '#$(python3 scripts/run_acceptance.py)\nEOF', 'ACCEPT')

    def test_unicode_separator_does_not_terminate_heredoc(self):
        for char in ('\x85', '\u2028', '\u2029'):
            self.check("cat <<'EOF'\nbody" + char + 'EOF', 'REFUSE')

    def test_escaped_unicode_before_hash_stays_in_word(self):
        self.check('echo \\\u2003#$(python3 scripts/run_acceptance.py)', 'REFUSE')

    def test_empty_quote_before_unicode_hash_stays_in_word(self):
        self.check("echo ''\u2003#$(python3 scripts/run_acceptance.py)", 'REFUSE')

    def test_double_quoted_unicode_active_substitution_refused(self):
        self.check('echo "\u2003#$(python3 scripts/run_acceptance.py)"', 'REFUSE')

    def test_ascii_runner_with_unicode_argument_healthy(self):
        command = 'python3\t-B\tscripts/run_acceptance.py --label=left\u2003right'
        for subset in (True, False):
            # This control needs different exact outputs for each mode.
            expected = command.replace(' --label', ' --qualification-only --label') if subset else command
            with self.subTest(subset=subset):
                actual = gate_recipes._runner_script(command, subset=subset)
                EVENTS.append({'test': self.id(), 'entry': 'runner', 'subset': subset,
                    'source': command, 'expected': 'ACCEPT', 'actual': 'ACCEPT', 'script': actual, 'calls': 1})
                self.assertEqual(actual, expected)


for name, char in CHARACTERS:
    def adverse(self, char=char):
        self.check('echo ' + char + '#$(python3 scripts/run_acceptance.py)', 'REFUSE')

    def quoted(self, char=char):
        self.check("echo 'left" + char + "#$(python3 scripts/run_acceptance.py)'", 'ACCEPT')

    def literal(self, char=char):
        self.check('echo left' + char + 'right', 'ACCEPT')

    setattr(UnicodeBoundaries, 'test_' + name + '_hash_adverse', adverse)
    setattr(UnicodeBoundaries, 'test_' + name + '_quoted_literal_healthy', quoted)
    setattr(UnicodeBoundaries, 'test_' + name + '_unquoted_literal_healthy', literal)


if __name__ == '__main__':
    unittest.main(verbosity=2)
