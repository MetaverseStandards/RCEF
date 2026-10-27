#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Translate a CSV of frames with RCEF's FB2 -> ARKit mappings into ARKit weights.

Usage: python examples/translate_fb2_to_arkit.py [INPUT.csv [OUTPUT.csv]]

Input columns: time, segment (a free label), one column per provider channel
and one 0/1 column per provider validity flag. Output columns: time, segment,
one column per translated ARKit weight (empty when refused), "refused"
(which mapping refused the frame and why) and "dropped" (non-zero inputs that
no RCEF rule reads).
"""
from pathlib import Path
import sys

import rcef_translate

HERE = Path(__file__).resolve().parent


def main(argv: list[str]) -> int:
    source = Path(argv[0]) if argv else HERE / 'data/fb2_demo_frames.csv'
    target = Path(argv[1]) if len(argv) > 1 else Path('fb2_to_arkit.csv')
    translator = rcef_translate.fb2_to_arkit()
    results = translator.translate(translator.read(source))
    translator.write(results, target)
    refused = sum(bool(r['refused']) for r in results)
    print(f'{len(results)} frames -> {target} ({refused} with a refusal)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
