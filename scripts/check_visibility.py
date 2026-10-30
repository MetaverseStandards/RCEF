#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check that the documents claim public access only for what a visitor with no GitHub account can reach.

The script finds every https://github.com/MetaverseStandards/... link in the
tracked Markdown files and the GitHub workflow, and requests each one with no
login or token. Then it lists each sentence of the Markdown files that says
that a repository or release is public, or that something works with no login
or token. A sentence that sets a condition on the visibility ("When the
release is public, ...", "... until the release is public") is not a claim.
The condition must be in the same sentence as the claim.

It exits 1 when a link cannot be reached without a login and a claim exists.
Run it before a release, and again after the release owners change the
visibility. It needs network access; tests/test_public_sources.py runs the
claim scan offline.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from test_unresolved_claims import units  # noqa: E402

LINK = re.compile(r'https://github\.com/MetaverseStandards/[A-Za-z0-9_.-]+(?:/releases/tag/v[0-9.]+)?')
CLAIM = re.compile(r'\b(?:is|are) (?:now )?public\b|\bpublic (?:repository|release)\b|\bpublicly\b(?! listed)|'
                   r'\banonymous(?:ly)?\b|needs? no (?:login|token)|\bno token\b|without (?:a )?(?:login|token)|'
                   r'without signing in|\bto everyone\b|\banyone can (?:download|read|clone|install|reach|access)\b|no (?:GitHub )?account|open to all', re.I)
# The condition is a clause of the same sentence that names the visibility: "when the release is public".
CONDITION = re.compile(r'\b(?:when|once|until|after|if)\b[^,.;]*\b(?:is|are|becomes?) public\b', re.I)
SENTENCE = re.compile(r'(?<=[.!?])\s+(?=[A-Z`*\[(])')


def claims(texts: dict[str, str]) -> list[dict]:
    """Every sentence that claims public access with no condition on the visibility in the same sentence."""
    found = []
    for name, text in texts.items():
        if name.startswith('.github/'):
            continue
        for unit in units(text):
            for sentence in SENTENCE.split(' '.join(unit.split())):
                if CLAIM.search(sentence) and not CONDITION.search(sentence):
                    found.append({'file': name, 'text': sentence[:200]})
    return found


def tracked_texts() -> dict[str, str]:
    result = subprocess.run(['git', 'ls-files', '*.md', '.github/*'], cwd=ROOT, capture_output=True, text=True,
                            check=False)
    names = result.stdout.split() if result.returncode == 0 else []
    if not names:
        names = [str(p.relative_to(ROOT)) for p in sorted(ROOT.rglob('*.md'))
                 if not any(part.startswith('.') for part in p.relative_to(ROOT).parts)]
    return {name: (ROOT / name).read_text(encoding='utf-8') for name in names}


def status(url: str) -> int:
    request = Request(url, method='HEAD', headers={'User-Agent': 'RCEF-visibility/0.1'})
    try:
        with urlopen(request, timeout=25) as response:
            return response.status
    except HTTPError as exc:
        return exc.code
    except (URLError, OSError):
        return 0


def main() -> int:
    texts = tracked_texts()
    links = sorted({m.rstrip('.') for text in texts.values() for m in LINK.findall(text)})
    reach = {url: status(url) for url in links}
    found = claims(texts)
    private = [url for url, code in reach.items() if code != 200]
    print(json.dumps({'links': reach, 'claims': found, 'not_public': private}, indent=1, sort_keys=True))
    return 1 if private and found else 0


if __name__ == '__main__':
    raise SystemExit(main())
