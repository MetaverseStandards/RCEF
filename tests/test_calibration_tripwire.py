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
# check.py changed again (16a698f) after viseme-poses.rocketbox-female (code_commit d7e0f50), which is reproduced from
# its freeze commit, a0381b2. viseme_poses.py then learnt the multi-rig fit (c0b8b8b; viseme-poses.rocketbox-multi v1,
# code_commit ce56bb6, reproduced from its freeze commit d53567c), and then the tied Left and Right fit and the lips
# step (05b8b0e), the code of viseme-poses.rocketbox-multi v2 (reproduced from its freeze commit 8354daf). check.py
# then learnt the perceptual gate, and viseme_poses.py the features (295f4d7), the code of
# viseme-poses.rocketbox-features. check.py then required the whole-face guard of every gated channel
# (8d10950). viseme_poses.py then read the poses through the one map per set pair and direction (b826a59);
# the correspondences and ARKit weights it computes are unchanged, so no record is fitted again.
CODE_COMMIT = 'b826a5929c8060c42c46eff1f6d7daa4d8d7e8cd'
RECORD_COMMIT = '2fa1be4'
CODE = ['check.py', 'examples/rig_gains.py', 'examples/rigs.py', 'examples/ict_facekit.py', 'examples/rcef_translate.py',
        'examples/data/rig_landmarks.json', 'tools/calibration/ict_files.json', 'tools/calibration/viseme_rigs.json',
        'tools/render/']
RECORD = ['calibration/rig-gains.ict-rocketbox-female.cal']
# The commits that published the results of the two viseme-poses records.
POSES_COMMIT = 'e43a0ca'
POSES = ['calibration/viseme-poses.rocketbox-female.cal']
# Version 1 of viseme-poses.rocketbox-multi, replaced in the checkout by version 2, is kept in the history.
MULTI_V1_COMMIT = '5b25c8d'
MULTI = 'calibration/viseme-poses.rocketbox-multi.cal'
# The commit that published the results of version 2.
MULTI_COMMIT = '29a5223'
# The commit that published the results of the perceptual record.
FEATURES_COMMIT = '68e0f1e'
FEATURES = ['calibration/viseme-poses.rocketbox-features.cal']


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

    def test_the_multi_rig_viseme_poses_record_is_unchanged(self):
        self.assertIsNone(provenance.code_problem(ROOT, MULTI_COMMIT, [MULTI]))

    def test_the_perceptual_viseme_poses_record_is_unchanged(self):
        self.assertIsNone(provenance.code_problem(ROOT, FEATURES_COMMIT, FEATURES))

    def test_version_1_of_the_multi_rig_record_is_kept_in_the_history(self):
        text = subprocess.run(['git', 'show', f'{MULTI_V1_COMMIT}:{MULTI}'], cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout
        self.assertIn('version = 1\n', text)
        self.assertIn('[[cells]]', text)
        frozen = text.split('frozen_sha256 = "', 1)[1][:64]
        ledger = (ROOT / 'calibration/FREEZES').read_text(encoding='utf-8')
        self.assertIn(f'viseme-poses.rocketbox-multi v1 {frozen} ', ledger)


if __name__ == '__main__':
    unittest.main()
