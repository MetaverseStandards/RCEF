# SPDX-License-Identifier: MIT
"""The A1 arm of the A/B comparison: today's direct maps, frozen as a committed copy of the dea1713 pack."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/baseline-dea1713.pack.json'
SHA256 = '630d37a5b01e4983f8e5cbcbd54d8268abeffb09248ea793d4842bd2df5cd4f7'
COMMIT = 'dea171370bba25dda3aa6b9846a346b5fca43aa5'
DIRECT = ('fb2.to_arkit', 'fb2_gaze.to_arkit', 'arkit.to_fb2', 'arkit_gaze.to_fb2', 'arkit.to_vrcft_artist',
          'fb2.to_vrm', 'visemes.to_vrm')


def git_copy():
    """The pack at dea1713 from Git, or None when the checkout has no such history."""
    result = subprocess.run(['git', 'show', f'{COMMIT}:generated/rcef.pack.json'], cwd=ROOT, capture_output=True)
    return result.stdout if result.returncode == 0 else None


class Baseline(unittest.TestCase):
    def test_the_fixture_has_the_pinned_hash(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), SHA256)

    def test_the_fixture_is_the_pack_at_dea1713(self):
        copy = git_copy()
        if copy is None:
            self.skipTest('no Git history for dea1713')
        self.assertEqual(copy, FIXTURE.read_bytes())

    def test_the_fixture_holds_the_seven_direct_maps(self):
        document = json.loads(FIXTURE.read_text(encoding='utf-8'))
        self.assertEqual(document['data_version'], '0.4.0')
        self.assertLessEqual(set(DIRECT), {m['id'] for m in document['mappings']})


if __name__ == '__main__':
    unittest.main()
