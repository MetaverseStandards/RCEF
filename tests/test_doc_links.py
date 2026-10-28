# SPDX-License-Identifier: MIT
"""Relative links in the Markdown files resolve, and their #anchors name a heading in the target."""
from functools import cache
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^)\s]+)\)')
FENCE = re.compile(r'^```.*?^```', re.S | re.M)


def markdown_files():
    return sorted(p for p in ROOT.rglob('*.md')
                  if not any(part.startswith('.') or part == 'out' for part in p.relative_to(ROOT).parts))


@cache
def anchors(path):
    """GitHub heading anchors: lowercase, punctuation dropped, spaces to hyphens, -N for repeats."""
    seen, found = {}, set()
    for line in FENCE.sub('', path.read_text(encoding='utf-8')).splitlines():
        heading = re.match(r'#{1,6} (.*)', line)
        if heading:
            text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', heading.group(1).replace('`', '')).strip().lower()
            slug = re.sub(r'[^\w\- ]', '', text).replace(' ', '-')
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            found.add(slug if count == 0 else f'{slug}-{count}')
    return frozenset(found)


class DocLinks(unittest.TestCase):
    def test_relative_links_and_anchors_resolve(self):
        for path in markdown_files():
            for link in LINK.findall(FENCE.sub('', path.read_text(encoding='utf-8'))):
                if re.match(r'[a-z]+:', link):
                    continue
                target, _, fragment = link.partition('#')
                resolved = (path.parent / target).resolve() if target else path
                if not resolved.is_relative_to(ROOT):
                    continue  # links to a sibling msf_character_tools checkout
                with self.subTest(file=str(path.relative_to(ROOT)), link=link):
                    self.assertTrue(resolved.exists())
                    if fragment and resolved.suffix == '.md':
                        self.assertIn(fragment, anchors(resolved))


if __name__ == '__main__':
    unittest.main()
