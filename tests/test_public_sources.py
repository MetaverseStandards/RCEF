# SPDX-License-Identifier: MIT
"""Every source that RCEF cites is public and pinned.

- No tracked text file names a local home directory, a path under a home
  directory (`~/` or `$HOME/`), localhost, a private IP address or a
  `.corp` or `.internal` host. The one exemption is the XDG default
  directories (`~/.cache`, `$HOME/.cache` and `$HOME/.local/share` as the
  fallback of `$XDG_DATA_HOME`): the examples and the local CI name them as
  defaults, and they hold nothing of anyone's own. More hosts can be listed,
  one per line, in an untracked file: `.private-hosts` in the checkout, or the
  file that `RCEF_PRIVATE_HOSTS` names.
- Every raw.githubusercontent.com URL, and every github.com URL to a file or
  folder, names a full commit hash (or the commit constant of the code that
  builds it).
- Every evidence record with a URL has a SHA-256, a revision or a retrieval
  date, and a locator. When the URL holds a commit hash, the record's
  revision is that commit. Every Wikipedia record names a revision (`oldid`).
- The claim scan of `scripts/check_visibility.py` finds no claim of public
  access. The script itself also requests the links, so it needs the network;
  this test runs only the scan.

`scripts/verify_sources.py` checks the digests against the live sources; this
test checks only the text, so it runs offline. Outside a git checkout it reads
every file under the checkout instead of the tracked files.
"""
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
GENERIC = (r'/Users/[A-Za-z]|/home/[a-z]|[A-Z]:\\Users\\|(?:~|\$HOME|\$\{HOME\})/|\blocalhost\b|'
           r'\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b|'
           r'\b[a-z0-9-]+\.(?:corp|internal)\b')
XDG_DEFAULTS = re.compile(r'(?:~|\$HOME)/\.cache\b|\$\{XDG_DATA_HOME:-\$HOME/\.local/share\}')
URL = re.compile(r'https?://[^\s)>"\'`\]]+')
COMMIT = re.compile(r'/[0-9a-f]{40}(?:/|$)|\{[A-Z_]*COMMIT\}')
TEXT = ('.md', '.py', '.toml', '.json', '.csv', '.sh', '.yml', '.cal', '.abreg', '.swift', '.txt', '.html', '.svg', '')
SELF = 'tests/test_public_sources.py'


def private_pattern():
    hosts = []
    for name in (os.environ.get('RCEF_PRIVATE_HOSTS'), ROOT / '.private-hosts'):
        if name and Path(name).is_file():
            hosts += [h.strip() for h in Path(name).read_text(encoding='utf-8').splitlines()
                      if h.strip() and not h.startswith('#')]
    return re.compile('|'.join([GENERIC] + [re.escape(h) for h in hosts]), re.I)


def tracked():
    result = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True, check=False)
    names = result.stdout.split() if result.returncode == 0 else []
    if not names:
        names = [str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()
                 and not any(part.startswith('.') or part == '__pycache__' for part in p.relative_to(ROOT).parts)]
    for name in names:
        if name == SELF:
            continue  # its own patterns
        path = ROOT / name
        if path.suffix in TEXT and path.is_file() and path.stat().st_size < 20_000_000:
            yield name, path.read_text(encoding='utf-8', errors='replace')


class PublicSources(unittest.TestCase):
    def test_no_private_paths_or_hosts(self):
        pattern = private_pattern()
        for name, text in tracked():
            with self.subTest(file=name):
                found = pattern.search(XDG_DEFAULTS.sub('', text))
                self.assertIsNone(found, found and found.group(0))

    def test_the_pattern_finds_planted_paths(self):
        pattern = private_pattern()
        for text, found in (('see ~/.local/share/work', True), ('MSF=$HOME/work', True), ('/Users/someone/x', True),
                            ('http://localhost:8000', True), ('host 192.168.1.20', True), ('wiki.corp', True),
                            ('outputs go to ~/.cache/rcef-examples', False),
                            ('${XDG_DATA_HOME:-$HOME/.local/share}/rcef/venvs', False), ('version 10.2.3', False)):
            with self.subTest(text=text):
                self.assertEqual(bool(pattern.search(XDG_DEFAULTS.sub('', text))), found)

    def test_github_file_urls_name_a_commit(self):
        for name, text in tracked():
            for url in URL.findall(text):
                raw = url.startswith(('https://raw.githubusercontent.com/', 'http://raw.githubusercontent.com/'))
                blob = re.match(r'https?://github\.com/[^/]+/[^/]+/(?:blob|tree|raw)/', url)
                if raw or blob:
                    with self.subTest(file=name, url=url):
                        self.assertRegex(url, COMMIT)

    def test_evidence_records_are_pinned(self):
        records = tomllib.loads((ROOT / 'evidence/sources.toml').read_text(encoding='utf-8'))['evidence']
        for record in records:
            if 'url' not in record:
                continue
            with self.subTest(record=record['id']):
                self.assertRegex(record['sha256'], r'^[0-9a-f]{64}$')
                self.assertTrue(record.get('revision') or record.get('retrieved'))
                self.assertTrue(record.get('locator'))
                commit = re.search(r'/([0-9a-f]{40})(?:/|$)', record['url'])
                if commit:
                    self.assertEqual(record.get('revision'), commit.group(1))
                if 'wikipedia.org' in record['url']:
                    self.assertIn('oldid=', record['url'])

    def test_no_claim_of_public_access(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        import check_visibility
        self.assertEqual(check_visibility.claims(check_visibility.tracked_texts()), [])

    def test_visibility_scan_tells_claims_from_conditions(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        import check_visibility
        for text, claim in (('The release is public, so the download needs no token.', True),
                            ('When the release is public, the download needs no login or token.', False),
                            ('It works once the release is public, with no token.', False),
                            ('RCEF is a public repository.', True),
                            ('Anyone can download it anonymously.', True),
                            ('The wheel is publicly available to everyone.', True),
                            ('Anyone can download the wheel.', True), ('Anyone can recompute the hash.', False),
                            ('It needs no GitHub account.', True),
                            ('It lists 124 publicly listed parameters.', False),
                            ('When GitHub Actions is on, it downloads the public release with no token.', True)):
            with self.subTest(text=text):
                self.assertEqual(bool(check_visibility.claims({'x.md': text})), claim)


if __name__ == '__main__':
    unittest.main()
