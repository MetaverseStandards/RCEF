# SPDX-License-Identifier: MIT
"""The code and record behind the published calibration results have not changed since they were frozen.

test_calibration_provenance.py tests provenance.code_problem on a temporary
repository; this test runs it on the real protected files of this checkout.
"""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/calibration'))
import provenance  # noqa: E402

# The last commit that changed the calibration code, and the one that published the rig-gains results. The code
# changed after the rig-gains and MediaPipe records (code_commit 7cd8ff9) when check.py learnt geometry-only records
# and pose sums, and viseme_poses.py was added; those two records are reproduced from their freeze commit, dd9ecd2.
CODE_COMMIT = 'a03affe90c15fed693ded9a746ab78af79badd55'
RECORD_COMMIT = '2fa1be4'
CODE = ['check.py', 'examples/rig_gains.py', 'examples/rigs.py', 'examples/ict_facekit.py', 'examples/rcef_translate.py',
        'examples/data/rig_landmarks.json', 'tools/calibration/ict_files.json', 'tools/render/']
RECORD = ['calibration/rig-gains.ict-rocketbox-female.cal']
# The commit that published the viseme-poses results.
POSES_COMMIT = 'e43a0ca'
POSES = ['calibration/viseme-poses.rocketbox-female.cal']


def has_history():
    return subprocess.run(['git', 'cat-file', '-e', f'{CODE_COMMIT}^{{commit}}'], cwd=ROOT,
                          capture_output=True).returncode == 0


@unittest.skipUnless(has_history(), 'no Git history for the calibration commits')
class Protected(unittest.TestCase):
    def test_the_calibration_code_is_unchanged(self):
        tools = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'tools/calibration').glob('*.py'))
        self.assertIn('tools/calibration/k4_record.py', tools)
        self.assertIsNone(provenance.code_problem(ROOT, CODE_COMMIT, CODE + tools))

    def test_the_rig_gains_record_is_unchanged(self):
        self.assertIsNone(provenance.code_problem(ROOT, RECORD_COMMIT, RECORD))

    def test_the_viseme_poses_record_is_unchanged(self):
        self.assertIsNone(provenance.code_problem(ROOT, POSES_COMMIT, POSES))


if __name__ == '__main__':
    unittest.main()
