# SPDX-License-Identifier: MIT
"""The canonical viseme class of an IPA segment, by the IPA rules of docs/canonical-set.md.

A chart letter takes the class whose `ipa_members` list it in data/canonical_viseme.toml. A segment
written with diacritics, a tie bar or a leading superscript takes the class that the rules give.
`classify` raises ValueError where no rule applies; it never guesses.
"""
from pathlib import Path
import tomllib
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/canonical_viseme.toml'
PARTITION = 'probability_simplex'

NO_LIP_TARGET = {'coronal_stop', 'coronal_nasal_lateral', 'dorsal'}  # the laryngeals are in dorsal
CORONAL_LIKE = {'coronal_stop', 'coronal_nasal_lateral', 'alveolar_sibilant', 'rhotic', 'dental'}
ADVANCED_DENTAL = CORONAL_LIKE - {'alveolar_sibilant'}  # sibilants are not interdental
ROUNDED_OF = {'vowel_close_spread': 'vowel_close_rounded', 'vowel_mid_spread': 'vowel_mid_rounded',
              'vowel_open': 'vowel_mid_rounded'}
LABIALISED = ('ʷ', 'ᶣ')
COMPRESSED = ('ᵝ', 'ᶹ')
RHOTICITY = '˞'
RHOTIC_VOWEL_BASES = ('ə', 'ɜ')  # ə˞ = ɚ and ɜ˞ = ɝ; NFC does not unify the two spellings
DENTAL, ADVANCED, APICAL, LAMINAL, BRIDGE_ABOVE = '̪', '̟', '̺', '̻', '͆'
KEEP = set('ʲˠˤʰⁿˡ̥̬̤̰̃ːˑ̹̜̟̠̝̞̘̙̩̯̪̺̻̈̽̚ʼ') | {'̴'}  # alone, each keeps the base class
LINGUOLABIAL = '̼'
LINGUOLABIAL_BASES = {'bilabial', 'labiodental', 'dental', 'coronal_stop', 'coronal_nasal_lateral', 'rhotic',
                      'alveolar_sibilant'}
LABIAL = {'bilabial', 'labiodental'}
LEADING = set('ᵐⁿᵑᶬᶯᶮʰ')  # prenasalisation and preaspiration, written before the letter
TIE = ('͡', '͜')
WHOLE = {'ɫ': 'coronal_nasal_lateral', 'ɚ': 'rhotic', 'ɝ': 'rhotic'}  # chart examples written as one letter


def partition() -> dict[str, list[str]]:
    """The chart letters of each partition class, as data/canonical_viseme.toml lists them."""
    signals = tomllib.loads(DATA.read_text(encoding='utf-8'))['signals']
    return {s['id'].rsplit('.', 1)[1]: s['metadata']['ipa_members'] for s in signals if s['coupling'] == PARTITION}


def owners() -> dict[str, str]:
    owner = {}
    for cls, members in partition().items():
        for symbol in members:
            if symbol in owner:
                raise ValueError(f'{symbol} is in {owner[symbol]} and {cls}')
            owner[symbol] = cls
    return owner


OWNER = owners()


def classify(symbol: str) -> str:
    s = unicodedata.normalize('NFC', symbol)
    if s in OWNER:
        return OWNER[s]
    if s in WHOLE:
        return WHOLE[s]
    for tie in TIE:
        if tie in s:
            a, b = (classify(part) for part in s.split(tie, 1))
            # A double articulation shows its lip closure; an affricate takes the class of its release.
            if 'bilabial' in (a, b) and {a, b} <= NO_LIP_TARGET | {'bilabial'}:
                return 'bilabial'
            return b
    if len(s) > 1 and s[0] in LEADING:
        return classify(s[1:])
    decomposed = unicodedata.normalize('NFD', s)
    base, marks = decomposed[0], decomposed[1:]
    if base not in OWNER:
        raise ValueError(f'no chart letter {base!r} in {symbol}')
    cls = OWNER[base]
    if RHOTICITY in marks and base in RHOTIC_VOWEL_BASES:
        cls, marks = 'rhotic', marks.replace(RHOTICITY, '')
    if BRIDGE_ABOVE in marks:
        if cls not in CORONAL_LIKE or not any(m in marks for m in (DENTAL, APICAL, LAMINAL)):
            raise ValueError(f'no rule for the extIPA bridge in {symbol}')
        cls, marks = 'dental', marks.replace(BRIDGE_ABOVE, '')
    elif cls in ADVANCED_DENTAL and DENTAL in marks and ADVANCED in marks:
        cls = 'dental'
    if LINGUOLABIAL in marks:
        if cls not in LINGUOLABIAL_BASES:
            raise ValueError(f'no rule for the linguolabial mark on {base!r} in {symbol}')
        cls, marks = 'dental', marks.replace(LINGUOLABIAL, '')
    elif APICAL in marks and cls in LABIAL:  # the older apico-labial notation
        cls = 'dental'
    for m in marks:
        rounding = m in LABIALISED or m in COMPRESSED
        if rounding and cls in NO_LIP_TARGET:
            cls = 'vowel_close_rounded'
        elif m in LABIALISED and cls == 'alveolar_sibilant':
            cls = 'postalveolar'
        elif rounding and cls in ROUNDED_OF:
            cls = ROUNDED_OF[cls]
        elif not (rounding or m == RHOTICITY or m in KEEP):
            raise ValueError(f'no rule for the mark U+{ord(m):04X} in {symbol}')
    return cls
