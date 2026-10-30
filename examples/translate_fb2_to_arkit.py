#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Translate a CSV of FB2 frames into ARKit weights through RCEF's canonical expression set.

Usage: python examples/translate_fb2_to_arkit.py [INPUT.csv [OUTPUT.csv]]

OUTPUT defaults to ~/.cache/rcef-examples/fb2_to_arkit.csv ($XDG_CACHE_HOME instead of
~/.cache when it is set), outside the checkout.

Input columns: time, segment (a free label), one column per provider channel
and one 0/1 column per provider validity flag. Output columns: time, segment,
one column per translated ARKit weight (empty when refused), "refused"
(which hop map refused the frame and why) and "dropped" (non-zero inputs that
do not reach the target).
"""
from pathlib import Path
import sys

import rcef_frames

HERE = Path(__file__).resolve().parent


def main(argv: list[str]) -> int:
    source = Path(argv[0]) if argv else HERE / 'data/fb2_demo_frames.csv'
    target = Path(argv[1]) if len(argv) > 1 else rcef_frames.cache_home() / 'rcef-examples/fb2_to_arkit.csv'
    target.parent.mkdir(parents=True, exist_ok=True)
    translator = rcef_frames.fb2_to_arkit()
    results = translator.translate(translator.read(source))
    translator.write(results, target)
    refused = sum(bool(r['refused']) for r in results)
    print(f'{len(results)} frames -> {target} ({refused} with a refusal)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
