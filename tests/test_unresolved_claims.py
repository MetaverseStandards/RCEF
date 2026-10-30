# SPDX-License-Identifier: MIT
"""The documents do not state as fact what the definitions audit leaves `unresolved`.

Each rule names an `unresolved` loss key of docs/canonical-set-audit.md, the
words that name its subject and the words of a claim about it (a side frame,
a jaw relation, a neutral value, a direction). When one sentence (or table
cell) of a paragraph, list item or table row has both, the unit must also
say, in words, that the point is open (the hedge may be in any sentence of
the unit, so hedges are checked per paragraph, list item or table row): "RCEF
reads", "read as", "assumption", "not stated" and the like, or end with a
question. Identifiers do not count: the hedge test ignores text in backticks
and snake_case names such as loss keys, so naming a key is not enough. The
check reads every tracked Markdown file, the generated reports included.
"""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SIDE_FRAME = r"subject'?s|viewer'?s|own (?:left|right|side)|mirror|camera'?s"
# (loss key, subject, claim, a planted claim that the rule must find)
RULES = (
    ('vrm_blink_side_unresolved', r'\b(?:VRM|blinkLeft|blinkRight)\b', SIDE_FRAME,
     "VRM blinkLeft closes the subject's own left eye."),
    ('facs_side_frame_unresolved', r'\b(?:FACS|facs\.code|L30|R30|AU30)\b', SIDE_FRAME,
     "FACS L and R name the subject's own sides (`facs_side_frame_unresolved`)."),
    ('facs_au30_direction_unresolved', r'\b(?:L30|R30|AU30)\b',
     r"\bdirections?\b|\btoward\b|\bto the (?:subject's )?(?:own )?(?:left|right)\b",
     '`L30` and `R30` are directions: the jaw moves left or right. Loss key `facs_au30_direction_unresolved`.'),
    ('arkit_mouthclose_jaw_unresolved', r'(?<![\w.])mouthClose\b', r'\bjaw',
     'ARKit mouthClose closes the lips whatever the jaw does.'),
    ('vrcft_eye_openness_neutral_unresolved', r'\bOpenness\b', r'\b(?:neutral|relaxed)\b',
     'VRCFaceTracking Openness 1 is the relaxed open eye.'),
    ('vrcft_ue_mouthlowerdown_direction_unresolved', r'\bMouthLowerDown', r'\b(?:drops?|lowers?|rises?|raises?)\b',
     'MouthLowerDownLeft lowers the left half of the bottom lip.'),
    ('arkit_mouthstretchright_text_side', r'\bmouthStretchRight\b',
     r'\b(?:Apple|abstract)\b.*\bright (?:lip )?corner\b',
     "Apple's abstract says mouthStretchRight pulls the right corner."),
    ('meta_viseme_class_scope', r'\bMETA\b', r"\bMETA(?:'s)? (?:assigns|classifies|puts)\b",
     'META classifies every IPA sound into its 15 visemes.'),
)
# Not claims: "the 2 AU30 directions" counts mappings; the audit's corrections list says which key covers a loss.
NOT_CLAIMS = re.compile(r'the 2 AU30 directions|`mouthClose` jaw loss is covered by')
# More planted claims, as (rule index, text).
PLANTED = ((3, 'ARKit mouthClose closes the lips while the jaw stays open.'),
           (3, 'ARKit mouthClose is a jaw corrective: it closes the lips against jawOpen.'))
IDENTIFIERS = re.compile(r'`[^`\s]*`|\b[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+\b')
SENTENCE = re.compile(r'(?<=[.!?;])\s+|\s\|\s?')
HEDGE = re.compile(r'\bRCEF reads?\b|\bread as\b|\bunresolved\b|\bassum|not stated|does not (?:say|state|define)|'
                   r'\btaken (?:as|from)\b|\bcaveat|\bconflict|\bno normative\b|\bno neutral\b|\bnot treat|\?\s*\|?\s*$', re.I)


def units(text):
    """Paragraphs, list items and table rows, each as one string."""
    found = []
    for block in re.split(r'\n\s*\n', re.sub(r'^```.*?^```', '', text, flags=re.S | re.M)):
        current = []
        for line in block.splitlines():
            if line.startswith('|') or re.match(r'\s*(?:[-*]|\d+\.) ', line):
                if current:
                    found.append(' '.join(current))
                current = [line]
            else:
                current.append(line)
        if current:
            found.append(' '.join(current))
    return found


def flagged(unit, subject, claim):
    """True when the unit makes the claim and says nothing, in words, that leaves it open."""
    text = NOT_CLAIMS.sub('', unit)
    claimed = any(re.search(subject, sentence) and re.search(claim, sentence, re.I)
                  for sentence in SENTENCE.split(text))
    return claimed and not HEDGE.search(IDENTIFIERS.sub('', text))


def markdown_files():
    result = subprocess.run(['git', 'ls-files', '*.md'], cwd=ROOT, capture_output=True, text=True, check=False)
    names = result.stdout.split() if result.returncode == 0 else []
    paths = [ROOT / n for n in names] if names else sorted(ROOT.rglob('*.md'))
    return [p for p in paths if not any(part.startswith('.') for part in p.relative_to(ROOT).parts)]


class UnresolvedClaims(unittest.TestCase):
    def test_audit_keys_are_unresolved(self):
        audit = (ROOT / 'docs/canonical-set-audit.md').read_text(encoding='utf-8')
        for key, *_ in RULES:
            with self.subTest(key=key):
                self.assertRegex(audit, rf'\| `{key}` \| unresolved \|')

    def test_documents_do_not_state_unresolved_points_as_fact(self):
        for path in markdown_files():
            for unit in units(path.read_text(encoding='utf-8')):
                for key, subject, claim, _ in RULES:
                    with self.subTest(file=str(path.relative_to(ROOT)), key=key, text=unit[:160]):
                        self.assertFalse(flagged(unit, subject, claim))

    def test_each_rule_finds_its_planted_claim(self):
        for key, subject, claim, planted in RULES:
            with self.subTest(key=key):
                self.assertTrue(flagged(f'- {planted}', subject, claim))
                self.assertFalse(flagged(f'- RCEF reads it this way, as an assumption: {planted}', subject, claim))
        for index, planted in PLANTED:
            _, subject, claim, _ = RULES[index]
            with self.subTest(planted=planted):
                self.assertTrue(flagged(f'- {planted}', subject, claim))

    def test_a_question_at_the_end_is_not_a_claim(self):
        _, subject, claim, _ = RULES[3]
        self.assertFalse(flagged('- Does ARKit mouthClose depend on the jaw?', subject, claim))
        self.assertTrue(flagged('- Does it? ARKit mouthClose works whatever the jaw does.', subject, claim))


if __name__ == '__main__':
    unittest.main()
