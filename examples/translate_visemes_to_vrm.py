#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Translate a CSV of frames with RCEF's META viseme -> VRM mappings into VRM weights.

Usage: python examples/translate_visemes_to_vrm.py [INPUT.csv [OUTPUT.csv]]

OUTPUT defaults to ~/.cache/rcef-examples/visemes_to_vrm.csv ($XDG_CACHE_HOME instead of
~/.cache when it is set), outside the checkout.

Input columns: time, segment (a free label), one column per provider channel
and one 0/1 column per provider validity flag. Output columns: time, segment,
one column per translated VRM weight (empty when refused), "refused"
(which mapping refused the frame and why) and "dropped" (non-zero inputs that
no RCEF rule reads).
"""
from pathlib import Path
import sys

import rcef_translate

HERE = Path(__file__).resolve().parent


def main(argv: list[str]) -> int:
    source = Path(argv[0]) if argv else HERE / 'data/viseme_demo_frames.csv'
    target = Path(argv[1]) if len(argv) > 1 else rcef_translate.cache_home() / 'rcef-examples/visemes_to_vrm.csv'
    target.parent.mkdir(parents=True, exist_ok=True)
    translator = rcef_translate.visemes_to_vrm()
    results = translator.translate(translator.read(source))
    translator.write(results, target)
    refused = sum(bool(r['refused']) for r in results)
    print(f'{len(results)} frames -> {target} ({refused} with a refusal)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
