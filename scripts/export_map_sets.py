#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write one page per map set, docs/map-sets/<map id>.md, from the pack, or by default check that they are current.

A map set is one map between an expression set and a canonical set, in one direction, or the viseme pose bridge
between the two canonical sets. Its page shows the map's parts (its mappings split by the canonical group they read
or write), the mappings, operators, evidence and loss keys of each part, and the groups of the canonical set that
the map does not have, with the reason. It reads only generated/rcef.pack.json.
"""
from __future__ import annotations
import argparse
import difflib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = 'docs/map-sets'
CANONICAL = {'rcef.canonical_expression': 'canonical expression set', 'rcef.canonical_viseme': 'canonical viseme set'}
INTERMEDIATE = 'rcef.intermediate'
# The definitions audit section of each expression set (docs/canonical-set-audit.md).
AUDIT = {'arkit.coefficient': ('ARKit', 'arkit'), 'openxr.fb2': ('FB2', 'fb2'),
         'vrcft.artist.base': ('VRCFaceTracking Unified Expressions', 'vrcfacetracking-unified-expressions'),
         'vrcft.eye': ('VRCFaceTracking eye', 'vrcfacetracking-eye'), 'vrm.preset': ('VRM', 'vrm'),
         'openxr.visemes': ('META visemes', 'meta-visemes'), 'facs.code': ('FACS', 'facs')}
HEADER = ('<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->\n'
          '<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->\n')


def anchor(heading: str) -> str:
    """The GitHub anchor of a Markdown heading: lowercase, punctuation dropped, spaces to hyphens."""
    return re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')


def ends(rules: list[dict]) -> tuple[list[str], list[str]]:
    """A map's source signals and target signals, leaving out values it computes for its own later rules."""
    written = {o for r in rules for o in r['outputs']}
    read = {i for r in rules for i in r['inputs']}
    return ([s for s in dict.fromkeys(i for r in rules for i in r['inputs']) if s not in written],
            [s for s in dict.fromkeys(o for r in rules for o in r['outputs']) if s not in read])


def map_sets(document: dict) -> list[dict]:
    """Every map set of the pack: {id, source, target, rules}, in pack order."""
    profiles = {p['id']: set(p['signal_ids']) for p in document['profiles']}

    def home(sids):
        found = [p for p, members in profiles.items() if p != INTERMEDIATE and not p.startswith('fixture')
                 and set(sids) <= members and (p in CANONICAL or not p.startswith('rcef.'))]
        return found[0] if len(found) == 1 else None

    out = []
    for mapping in document['mappings']:
        if all(r['disposition'] == 'unresolved' for r in mapping['rules']):
            continue
        source, target = (home(sids) for sids in ends(mapping['rules']))
        if source and target and (source in CANONICAL or target in CANONICAL):
            out.append({'id': mapping['id'], 'source': source, 'target': target, 'rules': mapping['rules']})
    return out


def parts(rules: list[dict], groups: dict[str, str]) -> dict[str, list[dict]]:
    """The map's rules by part: the canonical group a rule reads or writes. A rule between intermediate values
    takes the part of the rules that read what it writes, or else of the rules that write what it reads."""
    part = {}
    for rule in rules:
        found = {groups[s] for s in rule['inputs'] + rule['outputs'] if s in groups}
        if len(found) == 1:
            part[rule['id']] = found.pop()
    for downstream in (True, False):
        changed = True
        while changed:
            changed = False
            for rule in rules:
                if rule['id'] in part:
                    continue
                joined = [part[r['id']] for r in rules if r['id'] in part and (
                    set(r['inputs']) & set(rule['outputs']) if downstream else set(r['outputs']) & set(rule['inputs']))]
                if joined:
                    part[rule['id']] = joined[0]
                    changed = True
    missing = [r['id'] for r in rules if r['id'] not in part]
    if missing:
        raise SystemExit(f'mappings with no canonical group: {missing}')
    out = {}
    for rule in rules:
        out.setdefault(part[rule['id']], []).append(rule)
    return out


def operator_name(operator: dict) -> str:
    kind = operator['id']
    if kind == 'affine':
        if (operator['scale'], operator['offset']) == (1.0, 0.0):
            return 'copy (affine 1, 0)'
        return f'affine {operator["scale"]:g}, {operator["offset"]:g}'
    if kind == 'weighted_sum':
        weights = operator['weights']
        if len(set(weights)) == 1 and weights[0] * len(weights) == 1.0:
            return f'mean of {len(weights)} (weighted_sum)'
        if len(weights) > 4:
            return f'weighted_sum of {len(weights)}'
        return 'weighted_sum ' + ', '.join(f'{w:g}' for w in weights)
    if kind == 'piecewise_linear':
        return 'piecewise_linear ' + ' '.join(f'({x:g}, {y:g})' for x, y in operator['knots'])
    return kind


def counted(items) -> str:
    totals = {}
    for item in items:
        totals[item] = totals.get(item, 0) + 1
    return ', '.join(f'{name} ({n})' if n > 1 else name for name, n in totals.items())


def page(entry: dict, document: dict, keys: set[str], siblings: list[dict]) -> str:
    signals = {s['id']: s for s in document['signals']}
    profiles = {p['id']: p for p in document['profiles']}
    groups = {s: signals[s]['metadata']['group'] for c in CANONICAL for s in profiles[c]['signal_ids']}
    canonical = entry['target'] if entry['target'] in CANONICAL else entry['source']
    provider = entry['source'] if entry['target'] in CANONICAL else entry['target']
    bridge = entry['source'] in CANONICAL and entry['target'] in CANONICAL
    rules, found = entry['rules'], parts(entry['rules'], groups)
    statuses = counted(r['evidence_status'] for r in rules)
    lines = [HEADER, f'# Map set `{entry["id"]}`', '']
    direction = 'into' if entry['target'] in CANONICAL and not bridge else 'out of'
    if bridge:
        lines.append(f'The viseme pose bridge: one map from the {CANONICAL[entry["source"]]} (`{entry["source"]}`) '
                     f'to the {CANONICAL[entry["target"]]} (`{entry["target"]}`).')
    else:
        lines.append(f'One map {direction} the {CANONICAL[canonical]} (`{canonical}`): from `{entry["source"]}` to '
                     f'`{entry["target"]}`.')
    lines += ['', f'- Mappings: {len(rules)}, in {len(found)} parts.',
              f'- Evidence status of its mappings: {statuses}.',
              f'- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#'
              f'{anchor(entry["id"])}).', '',
              'A part is the mappings of the map that read or write one group of a canonical set. The groups are '
              'metadata of the canonical signals (`metadata.group`); they document the parts of the set. The map runs '
              'as one whole: a bad or missing input stops only the outputs that read it '
              '([examples/rcef_route.py](../../examples/rcef_route.py)).', '', '## Parts', '',
              '| Part (canonical group) | Canonical signals | Mappings | Operators | Evidence status |',
              '|---|---|---|---|---|']
    for group, members in found.items():
        set_of = next(c for c in CANONICAL for s in profiles[c]['signal_ids'] if groups[s] == group)
        size = sum(groups[s] == group for s in profiles[set_of]['signal_ids'])
        touched = sorted({s for r in members for s in r['inputs'] + r['outputs'] if groups.get(s) == group})
        lines.append(f'| `{group}` | {len(touched)} of {size} | {len(members)} | '
                     f'{counted(operator_name(r["operator"]) for r in members)} | '
                     f'{counted(r["evidence_status"] for r in members)} |')
    lines += ['', '## Mappings by part', '']
    for group, members in found.items():
        lines.append(f'- `{group}`: ' + ', '.join(f'`{r["id"]}`' for r in members) + '.')
    helpers = sorted({s for r in rules for s in r['inputs'] + r['outputs']} & set(profiles[INTERMEDIATE]['signal_ids']))
    if helpers:
        lines += ['', f'{len(helpers)} intermediate values (`{INTERMEDIATE}`) are computed inside the map and read '
                      'only by its own later mappings.']
    lines += ['', '## Evidence', '', '| Evidence record | Mappings that cite it |', '|---|---|']
    cited = {}
    for rule in rules:
        for record in rule['evidence']:
            cited[record] = cited.get(record, 0) + 1
    for record, n in cited.items():
        lines.append(f'| [`{record}`](../../references.md#{anchor(record)}) | {n} |')
    losses = {}
    for rule in rules:
        for loss in rule['loss_annotations']:
            key = loss['reason'].split(':', 1)[0]
            if key in keys:
                losses[key] = losses.get(key, 0) + 1
    if losses:
        lines += ['', '## Loss keys', '', 'Loss keys of the [definitions audit](../canonical-set-audit.md#loss-keys) '
                  'that its mappings state, with the number of mappings:', '']
        lines += [f'- `{key}`: {n}' for key, n in losses.items()]
    side = 'inputs' if direction == 'out of' and not bridge else 'outputs'
    written = {groups[s] for r in rules for s in r[side] if s in groups and s in profiles[canonical]['signal_ids']}
    absent = [g for g in profiles[canonical]['metadata']['groups'] if g not in written]
    lines += ['', '## Parts this map does not have', '']
    if not absent:
        lines.append(f'None: the map {"reads" if side == "inputs" else "writes"} every group of the '
                     f'{CANONICAL[canonical]}.')
    else:
        name, section = AUDIT.get(provider, (provider, None))
        verb = 'reads' if side == 'inputs' else 'writes'
        where = f'the [{name} section](../canonical-set-audit.md#{section}) of the definitions audit' if section else \
            'the definitions audit'
        if bridge:
            lines.append('The bridge writes only the groups of a mouth pose. Teeth, tongue, blink, gaze, the sideways '
                         'jaw and the mouth shifts are not represented ([canonical-set.md]'
                         '(../canonical-set.md#viseme-pose-bridge)):')
        else:
            lines.append(f'{where[0].upper()}{where[1:]} names no `{provider}` signal for the canonical signals of '
                         f'these groups, so no mapping {verb} them. A route labels the outputs that need them "not available from '
                         'source", which is not a refusal.')
        lines.append('')
        for group in absent:
            members = [s.rsplit('.', 1)[1] for s in profiles[canonical]['signal_ids'] if groups[s] == group]
            lines.append(f'- `{group}` ({len(members)}): ' + ', '.join(f'`{m}`' for m in members))
    if siblings:
        lines += ['', f'## Other map sets {direction} the {CANONICAL[canonical]}', '',
                  '| Map set | Parts | Mappings |', '|---|---|---|']
        for other in siblings:
            lines.append(f'| [`{other["id"]}`]({other["id"]}.md) | {len(parts(other["rules"], groups))} | '
                         f'{len(other["rules"])} |')
    return '\n'.join(lines) + '\n'


def audit_keys(root: Path = ROOT) -> set[str]:
    text = (root / 'docs/canonical-set-audit.md').read_text(encoding='utf-8')
    section = text[text.index('\n## Loss keys'):]
    section = section[:section.index('\n## ', 5)]
    return {line.split('`')[1] for line in section.splitlines() if line.startswith('| `')}


def render(root: Path = ROOT) -> dict[str, str]:
    document = json.loads((root / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
    sets, keys = map_sets(document), audit_keys(root)

    def side(entry):
        return ('bridge' if entry['source'] in CANONICAL and entry['target'] in CANONICAL else
                ('in', entry['target']) if entry['target'] in CANONICAL else ('out', entry['source']))
    return {f'{OUTPUT}/{e["id"]}.md': page(e, document, keys, [o for o in sets if o is not e and side(o) == side(e)
                                                                and side(e) != 'bridge'])
            for e in sets}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n', 1)[0])
    parser.add_argument('--write', action='store_true', help='rewrite the pages')
    args = parser.parse_args(argv)
    pages, stale = render(), []
    folder = ROOT / OUTPUT
    extra = sorted(p.relative_to(ROOT).as_posix() for p in folder.glob('*.md')) if folder.exists() else []
    extra = [p for p in extra if p not in pages]
    for path, content in pages.items():
        target = ROOT / path
        current = target.read_text(encoding='utf-8') if target.exists() else ''
        if current == content:
            continue
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding='utf-8', newline='\n')
        else:
            stale.append(path)
            print(''.join(difflib.unified_diff(current.splitlines(True), content.splitlines(True), path, 'generated')),
                  end='')
    for path in extra:
        if args.write:
            (ROOT / path).unlink()
        else:
            stale.append(path)
    if stale:
        print(f'{", ".join(stale)} out of date; run scripts/export_map_sets.py --write')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
