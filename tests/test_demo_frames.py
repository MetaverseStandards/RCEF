# SPDX-License-Identifier: MIT
"""examples/make_demo_frames.py writes the committed demo frames byte for byte, from channel lists fixed in the code.

The lists are those of the A1 pack at dea1713 (tests/fixtures/baseline-dea1713.pack.json).
"""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import make_demo_frames  # noqa: E402

FB2 = ('openxr.fb2.XR_FACE_EXPRESSION2_', '_FB')
VISEMES = ('openxr.visemes.XR_FACE_TRACKING_VISEME_', '_META')


class DemoFrames(unittest.TestCase):
    def test_the_committed_frames_are_written_byte_for_byte(self):
        with tempfile.TemporaryDirectory(prefix='rcef-demo-') as tmp, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(make_demo_frames.main(['--out', tmp]), 0)
            for name in ('fb2_demo_frames.csv', 'viseme_demo_frames.csv'):
                with self.subTest(name):
                    self.assertEqual((Path(tmp) / name).read_bytes(), (ROOT / 'examples/data' / name).read_bytes())

    def test_the_channel_lists_are_those_of_the_a1_pack(self):
        pack = json.loads((ROOT / 'tests/fixtures/baseline-dea1713.pack.json').read_text(encoding='utf-8'))
        signals = {s['id']: s for s in pack['signals']}

        def members(profile, affixes):
            ids = next(p['signal_ids'] for p in pack['profiles'] if p['id'] == profile)
            return tuple(sid[len(affixes[0]):-len(affixes[1])] for sid in ids
                         if signals[sid]['disposition'] != 'excluded')
        self.assertEqual(make_demo_frames.FB2_CHANNELS, members('openxr.fb2', FB2))
        self.assertEqual(make_demo_frames.VISEME_CHANNELS, members('openxr.visemes', VISEMES))
        read = {i for m in pack['mappings'] if m['id'] in ('fb2.to_arkit', 'fb2_gaze.to_arkit')
                for r in m['rules'] for i in r['inputs']}
        self.assertEqual(make_demo_frames.RULE_INPUTS, tuple(c for c in members('openxr.fb2', FB2)
                                                             if FB2[0] + c + FB2[1] in read))


if __name__ == '__main__':
    unittest.main()
