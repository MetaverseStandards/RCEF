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
# check.py changed again (c4ff122) after viseme-poses.rocketbox-female (code_commit 703ee7c), which is reproduced from
# its freeze commit, 605c4f9. viseme_poses.py then learnt the multi-rig fit (0d3ee83; viseme-poses.rocketbox-multi v1,
# code_commit 6624079, reproduced from its freeze commit 6417863), and then the tied Left and Right fit and the lips
# step (1f77cdd), the code of viseme-poses.rocketbox-multi v2 (reproduced from its freeze commit 61660f1). check.py
# then learnt the perceptual gate, and viseme_poses.py the features (333d928), the code of
# viseme-poses.rocketbox-features. check.py then required the whole-face guard of every gated channel
# (fd07416). viseme_poses.py then read the poses through the one map per set pair and direction (aa43116);
# the correspondences and ARKit weights it computes are unchanged, so no record is fitted again. The history was then
# rewritten for publication, and the three viseme-poses records were frozen again as new versions that name the new
# hashes of their code commits. Each new version was frozen and held out on a branch from the freeze commit of the
# version before it, where the code is as at its code_commit, and that branch was merged.
CODE_COMMIT = 'aa4311623f6cafe201446a57abafd914a6fa5ca3'
RECORD_COMMIT = '2fa1be4'
CODE = ['check.py', 'examples/rig_gains.py', 'examples/rigs.py', 'examples/ict_facekit.py', 'examples/rcef_translate.py',
        'examples/data/rig_landmarks.json', 'tools/calibration/ict_files.json', 'tools/calibration/viseme_rigs.json',
        'tools/render/']
RECORD = ['calibration/rig-gains.ict-rocketbox-female.cal']
# The commits that published the results of the versions in the checkout: viseme-poses.rocketbox-female v2,
# viseme-poses.rocketbox-multi v3 and viseme-poses.rocketbox-features v2.
POSES_COMMIT = '303d8a2'
POSES = ['calibration/viseme-poses.rocketbox-female.cal']
MULTI = 'calibration/viseme-poses.rocketbox-multi.cal'
MULTI_COMMIT = 'b299b62'
FEATURES_COMMIT = '24a4af1'
FEATURES = ['calibration/viseme-poses.rocketbox-features.cal']
# The earlier versions, replaced in the checkout, are kept in the history: (results commit, record, version).
EARLIER = [('ba58c88', POSES[0], 1), ('f166568', MULTI, 1), ('7873008', MULTI, 2), ('43a5735', FEATURES[0], 1)]


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

    def test_the_earlier_versions_are_kept_in_the_history(self):
        ledger = (ROOT / 'calibration/FREEZES').read_text(encoding='utf-8')
        for commit, path, version in EARLIER:
            with self.subTest(commit=commit):
                text = subprocess.run(['git', 'show', f'{commit}:{path}'], cwd=ROOT, check=True,
                                      capture_output=True, text=True).stdout
                self.assertIn(f'version = {version}\n', text)
                self.assertIn('[[cells]]', text)
                frozen = text.split('frozen_sha256 = "', 1)[1][:64]
                record_id = path.removeprefix('calibration/').removesuffix('.cal')
                self.assertIn(f'{record_id} v{version} {frozen} ', ledger)

if __name__ == '__main__':
    unittest.main()
