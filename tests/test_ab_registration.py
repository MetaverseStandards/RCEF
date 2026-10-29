# SPDX-License-Identifier: MIT
"""The A/B ledger, registrations and results follow the rules in ab/README.md.

The real ab/ folder is checked with check.read_ledger and
ab_compare.registration_problems. Synthetic folders in temporary Git
repositories check that each rule is enforced.
"""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import ab_compare  # noqa: E402
import ab_frames  # noqa: E402
import check  # noqa: E402

PINS = {'a1_sha256': ab_compare.A1_SHA256, 'b_pack_sha256': '0' * 64, 'code': {'generator': '1' * 64},
        'runtime': {'python': '3.12.15'}}


def registration(version=1, kind='first', identity='ab.pivot', **fields):
    abreg = {'format': ab_compare.FORMAT, 'id': identity, 'version': version, 'kind': kind, 'date': '2026-11-01',
             'sources': {}, 'families': [], 'perturbations': [], 'pairs': {},
             'metrics': {'M1': 'B equals A1'}, 'lists': {'intended_differences': []}, 'acceptance': {},
             'changes': [], 'pins': deepcopy(PINS), **fields}
    abreg['seed_root'] = ab_compare.seed_root(abreg)
    return abreg


class RealFolder(unittest.TestCase):
    def test_the_ledger_is_well_formed(self):
        entries, problems = check.read_ledger(ROOT / ab_compare.LEDGER)
        self.assertEqual(problems, [])
        self.assertEqual(len(entries), len(list((ROOT / 'ab').glob('*.abreg'))))

    def test_the_folder_follows_the_rules(self):
        self.assertEqual(ab_compare.registration_problems(ROOT), [])


class Rules(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='rcef-ab-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / 'ab').mkdir()
        self.ledger = ['# id version abreg_sha256 date [reason]']

    def git(self, *args):
        return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=self.root,
                              check=True, capture_output=True, text=True).stdout.strip()

    def commit(self, message):
        subprocess.run(f'git add -A && git -c user.name=t -c user.email=t@t commit -q -m "{message}"', shell=True,
                       cwd=self.root, check=True, capture_output=True)

    def add(self, abreg, line=True, reason=''):
        path = self.root / 'ab' / f'{abreg["id"]}-v{abreg["version"]}.abreg'
        path.write_text(json.dumps(abreg, indent=1), encoding='utf-8')
        if line:
            self.ledger.append(f'{abreg["id"]} v{abreg["version"]} {ab_compare.abreg_sha256(abreg)} '
                               f'{abreg["date"]} {reason}'.rstrip())
        (self.root / 'ab/FREEZES').write_text('\n'.join(self.ledger) + '\n', encoding='utf-8')

    def results(self, abreg, passed=True, folder=None, **fields):
        folder = self.root / ab_compare.RESULTS / (folder or f'v{abreg["version"]}')
        folder.mkdir(parents=True)
        manifest = {'id': abreg['id'], 'version': abreg['version'], 'kind': abreg['kind'],
                    'abreg_sha256': ab_compare.abreg_sha256(abreg), 'passed': passed, 'dry_run': False, **fields}
        (folder / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')

    def problems(self):
        return ab_compare.registration_problems(self.root, recompute=False, history=(self.root / '.git').exists())

    def assertProblem(self, text):
        problems = self.problems()
        self.assertTrue(any(text in p for p in problems), problems)

    def test_a_registered_first_freeze_passes(self):
        self.add(registration())
        self.assertEqual(self.problems(), [])

    def test_a_registration_without_a_ledger_line_is_refused(self):
        self.add(registration(), line=False)
        self.assertProblem('has no line in ab/FREEZES')

    def test_a_ledger_line_without_its_registration_is_refused(self):
        abreg = registration()
        self.add(abreg)
        (self.root / 'ab/ab.pivot-v1.abreg').unlink()
        self.assertProblem('registrations are never removed')

    def test_an_abandoned_registration_keeps_its_line_and_the_next_version_needs_a_reason(self):
        self.add(registration())
        self.add(registration(2, 'fix', changes=['the oracle']), reason='fix')
        self.assertProblem('needs a reason for re-freezing')

    def test_seed_root_is_the_hash_of_the_registration_without_it(self):
        abreg = registration()
        abreg['seed_root'] = 'f' * 64
        self.add(abreg)
        self.assertProblem('seed_root must be')

    def test_kind_and_version_must_agree(self):
        self.add(registration(kind='fix'))
        self.assertProblem('v1 is a "first" freeze')
        other = registration(identity='ab.pivot2', kind='first')
        self.add(other)
        self.assertProblem('a new A/B needs a new id')

    def test_thresholds_never_change_inside_an_id(self):
        self.add(registration())
        self.add(registration(2, 'fix', metrics={'M1': 'looser'}), reason='the oracle had a bug')
        self.assertProblem('thresholds must equal')

    def test_a_new_ab_sets_its_own_thresholds(self):
        self.add(registration())
        self.add(registration(identity='ab.pivot2', kind='new', metrics={'M1': 'other'}))
        self.assertEqual(self.problems(), [])

    def test_a_changed_list_needs_the_release_owners_acceptance(self):
        self.add(registration())
        lists = {'intended_differences': ['signed gaze']}
        self.add(registration(2, 'fix', lists=lists), reason='a hop bug in the gaze out-map')
        self.assertProblem("list intended_differences changed without the release owners' acceptance")
        accepted = registration(3, 'fix', lists=lists, acceptance={
            'intended_differences': 'accepted by the project\'s release owners on 2026-11-02'})
        self.add(accepted, reason='same list, now with the acceptance recorded')
        problems = self.problems()
        self.assertEqual([p for p in problems if 'v3' in p], [])

    def test_a_revise_freeze_lists_its_changes_and_their_acceptance(self):
        self.add(registration())
        self.results(registration())
        self.add(registration(2, 'revise'), reason='working group renames of two maps')
        self.assertProblem('a "revise" freeze lists each change')

    def test_a_reproduce_freeze_names_a_passing_freeze_and_copies_its_seeds(self):
        first = registration()
        self.add(first)
        reproduce = {**registration(2, 'reproduce'), 'reproduces': {'id': 'ab.pivot', 'version': 1}}
        reproduce['seed_root'] = first['seed_root']
        self.add(reproduce, reason='re-run after the direct maps are retired')
        self.assertProblem('whose results passed')
        self.results(first, passed=True)
        self.assertEqual(self.problems(), [])
        changed = {**reproduce, 'seed_root': 'e' * 64}
        self.add(changed, line=False)
        self.ledger[-1] = self.ledger[-1].replace(ab_compare.abreg_sha256(reproduce), ab_compare.abreg_sha256(changed))
        self.add(changed, line=False)
        self.assertProblem('copies the seed_root')

    def test_the_results_manifest_names_the_registration_hash_version_and_kind(self):
        abreg = registration()
        self.add(abreg)
        self.results(abreg, abreg_sha256='0' * 64)
        self.assertProblem('must name the registration hash')

    def test_results_go_in_the_folder_of_their_version(self):
        abreg = registration()
        self.add(abreg)
        self.results(abreg, folder='v7')
        self.assertProblem('must be in ab/results/v1/')

    def test_the_ledger_line_is_committed_before_the_results(self):
        self.git('init', '-q')
        first, second = registration(), registration(identity='ab.pivot2', kind='new')
        for abreg in (first, second):
            self.add(abreg, line=False)
        self.commit('register both')
        self.add(first)
        self.commit('ledger line')
        self.results(first)
        self.commit('results after the ledger line')
        self.add(second)
        self.results(second, folder='ab.pivot2-v1')
        self.commit('ledger line and results together')
        late = 'ab/results/ab.pivot2-v1/manifest.json was committed before, or with, its line in ab/FREEZES'
        self.assertEqual([p for p in self.problems() if 'was committed' in p], [late])


class A1Figures(unittest.TestCase):
    def test_no_a1_figure_depends_on_seed_root(self):
        document = ab_compare.load_a1()
        sources = {p: ab_frames.pinned_source(document, p) for p in ab_compare.A1_SOURCES}
        # The figures come from a registration that has no seed_root at all, so they cannot read it.
        figures = ab_compare.a1_figures({'families': [], 'sources': sources}, document)
        self.assertEqual(figures['observed_loss'], dict.fromkeys(ab_compare.A1_PAIRS, []))
        # 0.5 * 5e-324 underflows, so A1 refuses FB2 -> ARKit on the edge frames that hold it.
        refused = figures['edge_refusals']['FB2 -> ARKit']
        self.assertTrue(refused)
        self.assertEqual({codes for r in refused.values() for codes in map(tuple, r.values())}, {('E_NONFINITE',)})


if __name__ == '__main__':
    unittest.main()
