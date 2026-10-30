#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Metric M7 of the A/B comparison: plant each registered fault in a copy of the B pack and see what catches it.

A registration lists its mutations in lists.m7_mutations. Each names one
change to the B pack document and the checks that must catch it. A check
catches a mutation when it fails on the changed pack:

- M1 and M2: B against A1 on the five A1 pairs, on the fixed impulse frames,
  the goldens and the example CSVs (values and sign of zero; refusal scope);
- M3 exact: every round trip on the fixed impulse frames;
- M10: FACS to FB2 against arm A3 on the 221 library frames;
- M4 keys and M4b: the registration's frozen tables on the changed pack;
- the side test, the direction-suffix test, the one-group test and the audit
  loss-key test of tests/test_pivot_structure.py, and the weight and chain
  tests of tests/test_pose_bridge.py, run on the changed pack;
- the calibration check of check.py: each rule that cites a calibration
  record holds exactly the record's frozen values.

The unchanged pack must pass every check first. A test class that cannot even
be set up on a changed pack catches nothing: the row counts it as a setup
error, which fails M7. The changes are data in the registration, so a run
plants exactly what was registered.

Usage: python scripts/ab_mutations.py   (prints the mutation set a draft registers)
"""
from __future__ import annotations
from copy import deepcopy
import importlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
# Check name: (test module, test class, test method). Each class reads its pack through load_pack().
TEST_CHECKS = {
    'side test': ('test_pivot_structure', 'PivotStructure', 'test_sides_agree_at_both_ends'),
    'direction-suffix test': ('test_pivot_structure', 'PivotStructure', 'test_direction_suffixes_keep_their_direction'),
    'one-group test': ('test_pivot_structure', 'PivotStructure', 'test_each_map_reads_and_writes_one_group'),
    'audit loss-key test': ('test_pivot_structure', 'PivotStructure',
                            'test_audit_loss_keys_sit_on_the_hops_the_audit_names'),
    'pose-bridge weight test': ('test_pose_bridge', 'PoseBridge', 'test_each_weight_is_the_frozen_pose_of_the_record'),
    'pose-bridge chain test': ('test_pose_bridge', 'PoseBridge', 'test_the_chain_is_copy_then_sum_then_clamp'),
}
CHECKS = ('M1', 'M2', 'M3 exact', 'M10', 'M4 keys', 'M4b', *TEST_CHECKS, 'calibration check')
# The registered mutation set: the faults of the A/B design, each with the checks that must catch it.
MUTATIONS = [
    {'id': 'halve one hop', 'caught_by': ['M1'],
     'change': {'op': 'operator', 'rule': 'fb2_rcef.brow_lower_left',
                'operator': {'id': 'affine', 'scale': 0.5, 'offset': 0.0}}},
    {'id': 'swap left and right in one hop', 'caught_by': ['side test', 'M1'],
     'change': {'op': 'swap_outputs', 'pairs': [['arkit_rcef.brow_lower_left', 'arkit_rcef.brow_lower_right']]}},
    {'id': 'drop an averaged input', 'caught_by': ['M1'],
     'change': {'op': 'drop_input', 'rule': 'rcef_arkit.browInnerUp',
                'input': 'rcef.canonical_expression.brow_inner_raise_right'}},
    {'id': 'merge two in-maps', 'caught_by': ['M2', 'one-group test'],
     'change': {'op': 'merge_maps', 'maps': ['fb2_face.to_rcef', 'fb2_gaze.to_rcef']}},
    {'id': 'swap left and right in both VRCFaceTracking eye blink hops', 'caught_by': ['side test'],
     'change': {'op': 'swap_outputs', 'pairs': [
         ['vrcft_eye_rcef.eye_close_left', 'vrcft_eye_rcef.eye_close_right'],
         ['rcef_vrcft_eye.Left.Openness', 'rcef_vrcft_eye.Right.Openness']]}},
    {'id': 'swap jaw_sideways_left and jaw_sideways_right in one hop', 'caught_by': ['direction-suffix test', 'M1'],
     'change': {'op': 'swap_outputs', 'pairs': [['arkit_rcef.jaw_sideways_left', 'arkit_rcef.jaw_sideways_right']]}},
    {'id': 'delete one assumption from one hop', 'caught_by': ['M4b'],
     'change': {'op': 'delete_assumption', 'rule': 'rcef_arkit.eyeBlinkLeft', 'key': 'correspondence'}},
    {'id': 'swap left and right in one FACS hop', 'caught_by': ['side test'],
     'change': {'op': 'swap_outputs', 'pairs': [['facs_rcef.brow_inner_raise_left',
                                                  'facs_rcef.brow_inner_raise_right']]}},
    {'id': 'swap au30_left and au30_right in one FACS hop', 'caught_by': ['direction-suffix test'],
     'change': {'op': 'swap_outputs', 'pairs': [['facs_rcef.jaw_sideways_left', 'facs_rcef.jaw_sideways_right']]}},
    {'id': 'delete facs_ordinal_intensity from one FACS hop', 'caught_by': ['audit loss-key test'],
     'change': {'op': 'delete_loss', 'rule': 'facs_rcef.brow_lower_left', 'key': 'facs_ordinal_intensity'}},
    {'id': 'change one pose weight of the viseme bridge', 'caught_by': ['pose-bridge weight test', 'calibration check'],
     'change': {'op': 'weight', 'rule': 'rcef_viseme_pose.jaw_drop_sum', 'index': 1, 'weight': 0.5}},
    {'id': 'move one clamp knot of the viseme bridge', 'caught_by': ['pose-bridge chain test'],
     'change': {'op': 'operator', 'rule': 'rcef_viseme_pose.jaw_drop',
                'operator': {'id': 'piecewise_linear', 'knots': [[0.0, 0.0], [0.5, 1.0], [11.0, 1.0]]}}},
]


def rule_of(document: dict, rule_id: str) -> dict:
    found = [r for m in document['mappings'] for r in m['rules'] if r['id'] == rule_id]
    if len(found) != 1:
        raise SystemExit(f'mutation: rule {rule_id} found {len(found)} times')
    return found[0]


def map_of(document: dict, map_id: str) -> dict:
    found = [m for m in document['mappings'] if m['id'] == map_id]
    if len(found) != 1:
        raise SystemExit(f'mutation: map {map_id} found {len(found)} times')
    return found[0]


def mutate(document: dict, change: dict) -> dict:
    """A copy of a pack document with one registered change applied."""
    out = deepcopy(document)
    op = change['op']
    if op == 'operator':
        rule_of(out, change['rule'])['operator'] = change['operator']
    elif op == 'weight':
        rule_of(out, change['rule'])['operator']['weights'][change['index']] = change['weight']
    elif op == 'swap_outputs':
        for a, b in change['pairs']:
            ra, rb = rule_of(out, a), rule_of(out, b)
            ra['outputs'], rb['outputs'] = rb['outputs'], ra['outputs']
    elif op == 'drop_input':
        rule = rule_of(out, change['rule'])
        if change['input'] not in rule['inputs']:
            raise SystemExit(f'mutation: {change["rule"]} does not read {change["input"]}')
        n = rule['inputs'].index(change['input'])
        del rule['inputs'][n]
        del rule['operator']['weights'][n]
    elif op == 'merge_maps':
        keep, gone = change['maps']
        map_of(out, keep)['rules'] += map_of(out, gone)['rules']
        out['mappings'] = [m for m in out['mappings'] if m['id'] != gone]
    elif op == 'delete_assumption':
        rule = rule_of(out, change['rule'])
        rule['assumptions'] = [a for a in rule['assumptions'] if a.split(':', 1)[0] != change['key']]
    elif op == 'delete_loss':
        rule = rule_of(out, change['rule'])
        rule['loss_annotations'] = [x for x in rule['loss_annotations']
                                    if x['reason'].split(':', 1)[0] != change['key']]
    else:
        raise SystemExit(f'mutation: unknown change {op}')
    if out == document:
        raise SystemExit(f'mutation: {change} changes nothing')
    return out


def test_failures(document: dict, names: list[str]) -> tuple[set[str], set[str]]:
    """The test checks (by name) that fail on a pack document, and those whose test class could not be set up."""
    if str(ROOT / 'tests') not in sys.path:
        sys.path.insert(0, str(ROOT / 'tests'))
    failed, errors = set(), set()
    for module_name, class_name in dict.fromkeys(TEST_CHECKS[n][:2] for n in names):
        base = getattr(importlib.import_module(module_name), class_name)
        changed = type(f'Changed{class_name}', (base,), {'load_pack': classmethod(lambda cls: document)})
        mine = [n for n in names if TEST_CHECKS[n][:2] == (module_name, class_name)]
        suite = unittest.TestSuite(changed(TEST_CHECKS[n][2]) for n in mine)
        try:
            result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
        except SystemExit:  # msf-character-tools refused the pack while the class was set up
            errors.update(mine)
            continue
        if any(not hasattr(test, '_testMethodName') for test, _ in result.errors):
            errors.update(mine)  # the class could not be set up on this pack: no test ran, so none caught it
            continue
        # A failure inside a subTest is reported on the subtest, which names its test case.
        methods = {getattr(test, 'test_case', test)._testMethodName for test, _ in result.failures + result.errors}
        failed.update(n for n in mine if TEST_CHECKS[n][2] in methods)
    return failed, errors


def calibration_fails(document: dict) -> bool:
    """check.py's calibration check on the pack's rules: a rule that cites a record must hold its frozen values."""
    spec = importlib.util.spec_from_file_location('rcef_check', ROOT / 'check.py')
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    return bool(check.calibration_problems(ROOT / 'calibration', [r for m in document['mappings'] for r in m['rules']]))


def metric_failures(abreg: dict, document: dict, a1_document: dict, families: dict) -> set[str]:
    """The value and table metrics that fail on a pack document, with its pairs as Route now selects them."""
    import ab_a3
    import ab_compare
    failed, compiled = set(), {}
    pack, a1_pack = (ab_compare.rcef_translate.load_pack(d) for d in (document, a1_document))

    def route(source, target):
        """B's route on the changed pack, sharing the maps already compiled for other pairs."""
        found = ab_compare.rcef_route.Route(source, target, pack=pack, compiled=compiled)
        compiled.update(found.mappings)
        return found

    pairs = {}
    for name, (source, target, maps) in ab_compare.A1_PAIRS.items():
        b_route = route(source, target)
        if b_route.in_maps and b_route.out_maps:
            pairs[name] = {'source': source, 'target': target, **ab_compare.route_hops(b_route)}
        a1_route = ab_compare.rcef_route.Route(source, target, pack=a1_pack, maps=maps)
        names = [f'impulse:{source}', f'goldens:{source}', *(f for f in families if f.startswith(f'csv:{source}:'))]
        for family in (f for f in names if f in families):
            a1, b = (ab_compare.run_route(r, families[family]) for r in (a1_route, b_route))
            counts, _ = ab_compare.m1(a1, b)
            if counts['value_differences'] or counts['sign_differences']:
                failed.add('M1')
            if ab_compare.m2(a1, b)[0]['violations']:
                failed.add('M2')
    for pair in abreg['pairs'].values():
        if pair['source'] == pair['target']:
            impulse = families[f'impulse:{pair["source"]}']
            back = ab_compare.run_route(route(pair['source'], pair['target']), impulse)
            counts, _ = ab_compare.m3_exact(impulse, back, abreg['sources'][pair['source']])
            if counts['errors'] or counts['over_bound']:
                failed.add('M3 exact')
    if 'FACS -> FB2' in abreg['pairs']:
        frames = ab_compare.facs_values([{'family': 'facs_library', 'label': str(n), 'keys': keys}
                                         for n, keys in enumerate(ab_a3.b_keys())])
        fb2 = [f'{ab_compare.FB2[0]}{c}{ab_compare.FB2[1]}' for c in ab_a3.channels()]
        expected = [dict(zip(fb2, f.values())) for f in ab_a3.a3_frames()]
        counts, _ = ab_compare.facs_compare(ab_compare.run_route(route('facs.code', 'openxr.fb2'), frames), expected,
                                            abreg['lists']['m10_not_available'])
        if counts['value_differences'] or counts['coverage_violations'] or counts['b_refusals']:
            failed.add('M10')
    changed = {**abreg, 'pairs': {**abreg['pairs'], **pairs}}
    rows, _ = ab_compare.m4_keys(changed, a1_document, document)
    if any(r['shortfall'] or r['unlisted_added'] for r in rows):
        failed.add('M4 keys')
    rows, _, _ = ab_compare.m4b(changed, a1_document, document)
    if any(r['shortfall'] for r in rows):
        failed.add('M4b')
    return failed


def caught(abreg: dict, document: dict, a1_document: dict, families: dict) -> tuple[set[str], set[str]]:
    """The checks that fail on a pack document, and the test checks that could not run on it."""
    failed, errors = test_failures(document, list(TEST_CHECKS))
    failed |= metric_failures(abreg, document, a1_document, families)
    if calibration_fails(document):
        failed.add('calibration check')
    return failed, errors


def m7(abreg: dict, document: dict, a1_document: dict, families: dict) -> tuple[list, list]:
    """One row per registered mutation: the checks that caught it and how many required ones missed it.

    A last row holds the checks that fail on the unchanged pack: there must be none, or no catch means anything.
    """
    rows, failures = [], []
    for mutation in abreg['lists']['m7_mutations']:
        try:
            changed = mutate(document, mutation['change'])
        except SystemExit as problem:  # the B pack lacks a rule the mutation names: nothing can catch it
            rows.append({'mutation': mutation['id'], 'required': ' '.join(mutation['caught_by']), 'caught_by': '',
                         'missed': len(mutation['caught_by']), 'setup_errors': 0})
            failures.append([mutation['id'], ' '.join(mutation['caught_by']), str(problem)])
            continue
        found, errors = caught(abreg, changed, a1_document, families)
        missed = sorted(set(mutation['caught_by']) - found)
        rows.append({'mutation': mutation['id'], 'required': ' '.join(mutation['caught_by']),
                     'caught_by': ' '.join(c for c in CHECKS if c in found), 'missed': len(missed),
                     'setup_errors': len(errors)})
        if missed:
            failures.append([mutation['id'], ' '.join(missed), 'a required check did not catch it'])
        if errors:
            failures.append([mutation['id'], ' '.join(sorted(errors)), 'the test class could not be set up'])
    baseline, errors = caught(abreg, document, a1_document, families)
    rows.append({'mutation': 'unchanged pack', 'required': '',
                 'caught_by': ' '.join(c for c in CHECKS if c in baseline), 'missed': len(baseline),
                 'setup_errors': len(errors)})
    if baseline or errors:
        failures.append(['unchanged pack', ' '.join(sorted(baseline | errors)),
                         'fails or cannot run before any mutation'])
    return rows, failures


if __name__ == '__main__':
    print(json.dumps(MUTATIONS, indent=1))
