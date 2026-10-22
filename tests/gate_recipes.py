# SPDX-License-Identifier: MIT
"""Restricted offline recipes for the published RCEF gate controls."""
from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import stat
import sys

GATE_ID = 'test_gate.Gate.test_published_gates_reject_coherent_wrong_metadata'
SHELL_BLANKS = ' \t'


def _recipe_lines(text):
    # Shell/YAML physical lines end at LF. Unicode separators and CR are
    # literal characters, not extra lines or implicit CRLF normalization.
    lines = text.split('\n')
    return lines[:-1] if lines[-1] == '' else lines


def subset_script(script):
    """Adapt standalone runner commands; preserve literals and heredoc bodies."""
    return _runner_script(script, subset=True)


def _runner_script(script, *, subset):
    def substitution_end(text, index, depth=0, *, allow_and=False):
        # An admitted active $() is one outer word fragment. Inspect its
        # balanced simple command separately so its spaces/closing parenthesis
        # cannot invent an outer comment or hide an actual heredoc header.
        # Inner comments, operators, heredocs, arithmetic and backticks are
        # outside this subset and refuse before any append. Quoted exports
        # retain their existing grammar and the protected-reference guard.
        if depth >= 32:
            raise ValueError('unquoted recipe substitution nesting exceeds supported grammar')
        index += 2
        quote = None
        while index < len(text):
            char = text[index]
            if char == '\\' and quote != "'" and index + 1 < len(text):
                index += 2
                continue
            if quote == "'":
                if char == "'":
                    quote = None
            elif char == '"':
                quote = None if quote == '"' else '"'
            elif char == "'" and quote is None:
                quote = "'"
            elif text.startswith('$(', index):
                index = substitution_end(text, index, depth + 1, allow_and=quote == '"')
                continue
            elif char == '`':
                raise ValueError('unsupported unquoted recipe substitution grammar')
            elif quote is None:
                if char == ')':
                    return index + 1
                # Retain the published quoted cd/pwd exports. Other compound
                # syntax remains outside this bounded substitution grammar.
                if allow_and and text.startswith('&&', index):
                    index += 2
                    continue
                if char in '#;&|(<>`\n':
                    raise ValueError('unsupported unquoted recipe substitution grammar')
            index += 1
        raise ValueError('unterminated unquoted recipe substitution')

    def backtick_end(text, index):
        # Only simple backtick commands belong to this recipe subset. Refuse
        # inner quoting/escapes or compound syntax before outer state can change.
        index += 1
        while index < len(text):
            char = text[index]
            if char == '`':
                return index + 1
            if char in "'\"\\$#;&|()<>\n":
                raise ValueError('unsupported recipe backtick grammar')
            index += 1
        raise ValueError('unterminated recipe backtick substitution')

    def active_context(text, *, body=False):
        # Inspection only: retain original output bytes. In an unquoted body,
        # quotes and hashes are ordinary text; only shell body escapes apply.
        active = []
        heredocs = []
        substitution_spans = []
        comment_end = len(text)
        in_word = False
        quote = None
        index = 0
        while index < len(text):
            char = text[index]
            if not body and quote == "'":
                if char == "'":
                    quote = None
                else:
                    active.append('\0' if char in '$`' else char)
                index += 1
                continue
            if char == '\\' and index + 1 < len(text):
                following = text[index + 1]
                if following == '\n':
                    index += 2
                    continue
                special = '\\$`' if body else '\\$`"'
                if (not body and quote is None) or following in special:
                    active.append('\0' if following in '$`' else following)
                    in_word = True
                    index += 2
                    continue
            if not body:
                if char == '`':
                    end = backtick_end(text, index)
                    active.append(text[index:end])
                    substitution_spans.append((index, end))
                    in_word = True
                    index = end
                    continue
                if text.startswith('$(', index):
                    end = substitution_end(text, index, allow_and=quote == '"')
                    inspected, _, _, _ = active_context(text[index + 2:end - 1])
                    active.append('$(' + inspected + ')')
                    substitution_spans.append((index, end))
                    in_word = True
                    index = end
                    continue
                if char == '"':
                    in_word = True
                    quote = None if quote == '"' else '"'
                    index += 1
                    continue
                if char == "'" and quote is None:
                    in_word = True
                    quote = "'"
                    index += 1
                    continue
                if quote is None:
                    # Quotes (including empty fragments) and escaped separators
                    # belong to a word. Only a real boundary starts a comment.
                    if char == '#' and not in_word:
                        comment_end = index
                        break
                    if text.startswith('<<', index):
                        # The same quote/escape/comment state owns recognition.
                        # Admit only one supported, complete named delimiter.
                        match = re.match(
                            r"<<[ \t]*(?P<quote>['\"]?)(?P<delimiter>[A-Za-z_]\w*)(?P=quote)(?=$|[ \t;&|()<>])",
                            text[index:])
                        if not match:
                            raise ValueError('unsupported recipe heredoc delimiter')
                        heredocs.append((match['delimiter'], bool(match['quote'])))
                    in_word = not (char in SHELL_BLANKS or char in ';&|()<>')
            active.append(char)
            index += 1
        return ''.join(active), heredocs, comment_end, substitution_spans

    def reject_substitution(active, *, body=False):
        # Unquoted bodies expand even inside ordinary quote text. Refuse
        # every active marker there, including harmless substitutions; outside
        # bodies keep the conservative protected-reference co-occurrence guard.
        # This does not qualify general shell grammar or indirect runner aliases.
        if (re.search(r'\$\(|`', active)
                and (body or re.search(
                    r'run_acceptance\.py|\$(?:RUNNER\b|\{RUNNER\})', active))):
            raise ValueError('runner command substitution is unsupported')

    output = []
    delimiter = None
    quoted_body = False
    body = []
    for line in _recipe_lines(script):
        if delimiter is not None:
            output.append(line)
            if line == delimiter:
                if not quoted_body:
                    active, _, _, _ = active_context('\n'.join(body), body=True)
                    reject_substitution(active, body=True)
                delimiter = None
                body = []
            else:
                body.append(line)
            continue
        # All append/adaptation paths use this lexical inspection first.
        active, heredocs, comment_end, substitution_spans = active_context(line)
        if len(heredocs) > 1:
            raise ValueError('multiple recipe heredocs are unsupported')
        if heredocs:
            delimiter, quoted_body = heredocs[0]
        reject_substitution(active)
        if not line.strip(SHELL_BLANKS) or line.lstrip(SHELL_BLANKS).startswith('#'):
            output.append(line)
            continue
        # Inspect substitution interiors above, then tokenize only the outer
        # grammar. shlex cannot isolate the inner quote state itself. The inert
        # placeholder retains each outer word fragment; returned bytes are original.
        lexical_line = line[:comment_end]
        for start, end in reversed(substitution_spans):
            lexical_line = lexical_line[:start] + 'RCEF_SUBSTITUTION' + lexical_line[end:]
        lexer = shlex.shlex(lexical_line, posix=True, punctuation_chars=True)
        lexer.commenters = ''
        lexer.whitespace = SHELL_BLANKS
        lexer.whitespace_split = True
        tokens = list(lexer)
        runner = 'scripts/run_acceptance.py'
        python = tokens and tokens[0] in {'python', 'python3'}
        if python and re.search(r'\$(?:RUNNER\b|\{RUNNER\})', active):
            raise ValueError('variable runner commands are unsupported')
        if tokens and tokens[0] == 'echo' and len(tokens) == 2:
            output.append(line)
            continue
        if any(token.rsplit('/', 1)[-1] == 'run_acceptance.py'
               and token != runner for token in tokens):
            raise ValueError('unsupported runner script pathname')
        if runner not in tokens:
            output.append(line)
            continue
        if (not python or tokens.count(runner) != 1
                or tokens.index(runner) not in {1, 2}
                or (tokens.index(runner) == 2 and tokens[1] != '-B')
                or any(token in {';', '&&', '||', '|', '&', '>', '>>', '<', '(', ')'}
                       for token in tokens)
                or any(token in {'--qualification-only', '--observe-gate-control'}
                       for token in tokens)):
            raise ValueError('copied runner must be a standalone default command')
        # Locate the script token, preserving all original quoting and arguments.
        spans = list(re.finditer(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"|[^ \t]+", line))
        position = tokens.index(runner)
        if shlex.split(spans[position][0]) != [runner]:
            raise ValueError('unsupported runner command token syntax')
        end = spans[position].end()
        output.append(line[:end] + (' --qualification-only' if subset else '') + line[end:])
    if delimiter is not None:
        raise ValueError('unterminated recipe heredoc')
    return '\n'.join(output)


def workflow_recipe(text, workspace, base_environment, *, subset):
    """Consume every run step in the current named/literal YAML subset."""
    lines = _recipe_lines(text)
    if lines.count('    steps:') != 1:
        raise ValueError('workflow must declare exactly one supported steps block')
    top_keys = set()
    for line in lines:
        if (not line.strip(SHELL_BLANKS) or line.lstrip(SHELL_BLANKS).startswith('#')
                or line[0] in SHELL_BLANKS):
            continue
        match = re.fullmatch(r'([A-Za-z_]\w*):(?: .*)?', line)
        if (not match or match[1] not in {'name', 'on', 'permissions', 'jobs'}
                or match[1] in top_keys):
            raise ValueError('unsupported or duplicate workflow header')
        top_keys.add(match[1])
    job_keys = set()
    job_names = []
    for line in lines[lines.index('jobs:') + 1:lines.index('    steps:') + 1]:
        if not line.strip(SHELL_BLANKS) or line.lstrip(SHELL_BLANKS).startswith('#'):
            continue
        if line.startswith('  ') and not line.startswith('   '):
            if not re.fullmatch(r'  [A-Za-z_]\w*:', line):
                raise ValueError('unsupported job declaration')
            job_names.append(line)
        if line.startswith('    ') and not line.startswith('     '):
            match = re.fullmatch(r'    ([a-z][a-z-]*):(?: .*)?', line)
            if (not match or match[1] not in {'runs-on', 'env', 'strategy', 'steps'}
                    or match[1] in job_keys):
                raise ValueError('unsupported or duplicate job header')
            job_keys.add(match[1])
    if len(job_names) != 1:
        raise ValueError('workflow must declare one supported job')
    if any(re.match(r'    (?:defaults|if|continue-on-error|container|services):', line)
           for line in lines):
        raise ValueError('unsupported job execution semantics')
    environment = dict(base_environment)
    env_blocks = [index for index, line in enumerate(lines) if line == '    env:']
    if len(env_blocks) != 1:
        raise ValueError('workflow must declare one job environment')
    seen = set()
    index = env_blocks[0] + 1
    while index < len(lines) and lines[index].startswith('      '):
        match = re.fullmatch(r'      ([A-Za-z_]\w*): (.+)', lines[index])
        if not match or match[1] in seen:
            raise ValueError('unsupported or duplicate job environment value')
        seen.add(match[1])
        value = match[2].replace('${{ github.workspace }}', str(workspace))
        if '${{' in value or '\n' in value or value.startswith(('|', '>')):
            raise ValueError('unresolved job environment expression')
        environment[match[1]] = value
        index += 1

    scripts = []
    index = lines.index('    steps:') + 1
    while index < len(lines):
        if not lines[index].strip(SHELL_BLANKS):
            index += 1
            continue
        head = re.fullmatch(r'      - (name|uses|run): (.+)', lines[index])
        if not head:
            raise ValueError('unsupported workflow step or trailing job')
        step = {head[1]: head[2]}
        index += 1
        if head[1] == 'run' and head[2] == '|':
            block = []
            while index < len(lines) and (lines[index].startswith('          ') or not lines[index].strip(SHELL_BLANKS)):
                block.append(lines[index][10:] if lines[index].strip(SHELL_BLANKS) else '')
                index += 1
            step['run'] = '\n'.join(block).rstrip('\n')
        while index < len(lines) and lines[index].startswith('        '):
            match = re.fullmatch(r'        ([a-z][a-z-]*):(?: (.+))?', lines[index])
            if not match or match[1] in step:
                raise ValueError('unsupported or duplicate step field')
            key, value = match[1], match[2]
            step[key] = value
            index += 1
            if key == 'run' and value == '|':
                block = []
                while index < len(lines) and (lines[index].startswith('          ') or not lines[index].strip(SHELL_BLANKS)):
                    block.append(lines[index][10:] if lines[index].strip(SHELL_BLANKS) else '')
                    index += 1
                step[key] = '\n'.join(block).rstrip('\n')
            elif key == 'with' and 'uses' in step:
                with_keys = set()
                while index < len(lines) and lines[index].startswith('          '):
                    declaration = re.fullmatch(
                        r'          (path|repository|ref|token|python-version): .+', lines[index])
                    if not declaration or declaration[1] in with_keys:
                        raise ValueError('unsupported or duplicate checkout/setup declaration')
                    with_keys.add(declaration[1])
                    index += 1
        if 'uses' in step:
            if set(step) - {'uses', 'name', 'with'} or 'run' in step:
                raise ValueError('unsupported executable uses step')
            if step['uses'] not in {'actions/checkout@v4', 'actions/setup-python@v5'}:
                raise ValueError('unsupported offline action declaration')
            continue
        if (set(step) - {'name', 'run', 'working-directory', 'shell'}
                or step.get('working-directory') != 'RCEF'
                or step.get('shell', 'sh') != 'sh'
                or not step.get('run') or step['run'].startswith(('>', '|'))):
            raise ValueError('unsupported run step semantics')
        if '${{' in step['run'] or '--write' in step['run']:
            raise ValueError('acceptance run must be resolved and nonwriting')
        scripts.append(step['run'])
    if not scripts:
        raise ValueError('workflow has no executable acceptance steps')
    script = _runner_script('\n'.join(scripts), subset=subset)
    return {'script': script, 'cwd': workspace / 'RCEF', 'env': environment}


def document_recipe(text, *, subset):
    """Require a single marked acceptance region containing only sh fences."""
    regions = {}
    for role in ('GENERATE', 'ACCEPTANCE'):
        begin, end = (f'<!-- RCEF:{part} {role} -->' for part in ('BEGIN', 'END'))
        if text.count(begin) != text.count(end) or text.count(begin) > 1:
            raise ValueError('duplicate or mismatched document recipe markers')
        if begin in text:
            left, right = text.index(begin), text.index(end)
            if left >= right:
                raise ValueError('reversed document recipe markers')
            regions[role] = (left + len(begin), right)
    if 'ACCEPTANCE' not in regions:
        raise ValueError('document must mark one acceptance recipe')
    if 'GENERATE' in regions:
        a, b = regions['GENERATE'], regions['ACCEPTANCE']
        if not (a[1] < b[0] or b[1] < a[0]):
            raise ValueError('overlapping document recipes')
    left, right = regions['ACCEPTANCE']
    region = text[left:right]
    fences = list(re.finditer(r'```sh\n(.*?)```', region, re.DOTALL))
    if not fences or re.sub(r'```sh\n.*?```', '', region, flags=re.DOTALL).strip():
        raise ValueError('unsupported content in acceptance recipe')
    script = '\n'.join(match[1].strip('\n') for match in fences)
    if '--write' in script:
        raise ValueError('acceptance recipe may not generate outputs')
    return _runner_script(script, subset=subset)


def gate_record(output, exit_code, selected_ids):
    """Validate the last record of this invocation, including refusal records."""
    records = []
    for line in output.splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if isinstance(record, dict):
            records.append(record)
    expected = Counter(selected_ids)
    if not records or not expected or any(count != 1 for count in expected.values()):
        raise ValueError('missing gate-control invocation record')
    record = records[-1]
    if (record.get('scope') != 'gate-control'
            or record.get('original_required_methods') != [GATE_ID]
            or record.get('selected_methods') != sorted(selected_ids)
            or record.get('tests_run') != len(selected_ids)
            or Counter(record.get('executed_methods', [])) != expected
            or record.get('qualification') == 'PASS' or record.get('native_qualified') is True
            or record.get('observation') not in {'PASS', 'REFUSE'}
            or (exit_code == 0) != (record.get('observation') == 'PASS')):
        raise ValueError('incomplete or mismatched gate-control invocation')
    return record


def gate_observation(output, exit_code, selected_ids):
    record = gate_record(output, exit_code, selected_ids)
    if (exit_code != 0 or record['observation'] != 'PASS'
            or any(record.get(key) != 0 for key in ('failures', 'errors'))
            or record.get('skips') != [] or record.get('incomplete_methods')):
        raise ValueError('gate-control invocation did not succeed')
    return record


def _copy_source(source, destination):
    """Admit a bounded FD, then validate all source bytes before writing."""
    source, destination = Path(source), Path(destination)
    descriptor = os.open(source, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > 16 * 1024 * 1024:
            raise ValueError(f'fixture source is not a bounded regular file: {source}')
        chunks, consumed = [], 0
        # Never follow growth beyond the admitted size, even before endpoint
        # checks. A changed size or a premature EOF refuses the entire copy.
        while consumed < before.st_size:
            chunk = os.read(descriptor, min(1024 * 1024, before.st_size - consumed))
            if not chunk:
                break
            consumed += len(chunk)
            chunks.append(chunk)
        after = os.fstat(descriptor)
        endpoint = source.lstat()
        signature = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if (consumed != before.st_size or signature(before) != signature(after)
                or signature(after) != signature(endpoint)):
            raise ValueError(f'fixture source changed during reading: {source}')
        destination.write_bytes(b''.join(chunks))
        destination.chmod(stat.S_IMODE(before.st_mode))
    finally:
        os.close(descriptor)


def source_complete_fixture(root, workspace):
    """Copy the public fixture sources; leaf recipes exclude gate execution."""
    checkout = workspace / 'RCEF'
    checkout.mkdir()
    for name in ('pack.toml', 'check.py', 'data', 'profiles', 'mappings', 'evidence',
                 'fixtures', 'generated', 'reports', 'docs', 'scripts', 'tests',
                 'README.md', 'CONTRIBUTING.md', '.github'):
        source = root / name
        if source.is_dir():
            shutil.copytree(source, checkout / name, copy_function=_copy_source,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        else:
            _copy_source(source, checkout / name)
    tools = Path(os.environ['MSF_TOOLS_PATH']).resolve(strict=True)
    for name in ('msf-tools', '.ci-tools'):
        (workspace / name).symlink_to(tools, target_is_directory=True)
    binaries = workspace / 'bin'
    binaries.mkdir()
    for name in ('python', 'python3'):
        (binaries / name).symlink_to(sys.executable)
    environment = os.environ.copy()
    environment.pop('PYTHONPATH', None)
    environment['PATH'] = str(binaries) + os.pathsep + environment['PATH']
    environment['PYTHONDONTWRITEBYTECODE'] = '1'
    return checkout, environment
