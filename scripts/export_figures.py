#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write the two data figures of the documents: docs/routes.svg and docs/ab-coverage.svg.

- routes.svg: which canonical groups each expression set fills (in-maps) and
  reads back (out-maps), and what the viseme pose bridge reads and writes.
  It reads generated/rcef.pack.json.
- ab-coverage.svg: the A/B result for each route of the latest registered
  run: the external reference, the frames, the frames that B refuses, and the
  routes that run the pose bridge. It reads ab/FREEZES, the registration and
  ab/results/v<N>/.

It uses only the Python standard library. Without --write it checks the two
files and exits 1 if one is out of date.
"""
from __future__ import annotations
import argparse
import collections
import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = 'system-ui, -apple-system, Segoe UI, sans-serif'
INK, MUTED, LINE, PAPER, CARD = '#182b29', '#415b57', '#c8d5cc', '#f4f5ef', '#ffffff'
GREEN, BLUE, AMBER, GREY = '#17614c', '#155576', '#75500e', '#7d8b87'
GREEN_T, BLUE_T, AMBER_T, GREY_T = '#d7eadf', '#d6e6ef', '#f1e3c8', '#eceee9'
EXPRESSION, VISEME = 'rcef.canonical_expression', 'rcef.canonical_viseme'
SETS = (('arkit.coefficient', 'ARKit'), ('openxr.fb2', 'FB2'), ('facs.code', 'FACS'),
        ('vrcft.artist.base', 'VRCFT UE'), ('vrcft.eye', 'VRCFT eye'), ('vrm.preset', 'VRM'),
        ('openxr.visemes', 'META'))
LICENCE = '<!-- SPDX-License-Identifier: CC-BY-SA-4.0; RCEF contributors (2026). Written by scripts/export_figures.py. -->'


class Svg:
    def __init__(self, width: int, height: int, title: str, desc: str):
        self.width, self.height, self.title, self.desc, self.parts = width, height, title, desc, []

    def text(self, x, y, s, size=12, fill=INK, weight='normal', anchor='start'):
        self.parts.append(f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
                          f'text-anchor="{anchor}">{html.escape(str(s))}</text>')

    def rect(self, x, y, w, h, fill, stroke=None, dash=None, width=1, rx=4):
        extra = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ''
        extra += f' stroke-dasharray="{dash}"' if dash else ''
        self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx}" fill="{fill}"{extra}/>')

    def render(self) -> str:
        return '\n'.join([
            LICENCE,
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" '
            f'height="{self.height}" role="img" aria-labelledby="title desc" font-family="{FONT}">',
            f'<title id="title">{html.escape(self.title)}</title>',
            f'<desc id="desc">{html.escape(self.desc)}</desc>',
            f'<rect width="{self.width}" height="{self.height}" fill="{PAPER}"/>',
            *self.parts, '</svg>', ''])


def routes_figure(pack: dict) -> str:
    homes = collections.defaultdict(set)
    for profile in pack['profiles']:
        for sid in profile['signal_ids']:
            homes[sid].add(profile['id'])
    group = {s['id']: s['metadata']['group'] for s in pack['signals'] if s['id'].startswith('rcef.canonical_')}
    size = collections.Counter((sid.split('.')[1], g) for sid, g in group.items())  # signals per group
    order = []
    for s in pack['signals']:
        if s['id'] in group and (s['id'].split('.')[1], group[s['id']]) not in order:
            order.append((s['id'].split('.')[1], group[s['id']]))
    fills = collections.defaultdict(set)  # (group, set) -> {'in', 'out'}; set 'bridge' for the pose bridge
    for mapping in pack['mappings']:
        rules = [r for r in mapping['rules'] if r['disposition'] == 'mapped']
        outs = {o for r in rules for o in r['outputs']}
        ins = {i for r in rules for i in r['inputs']} - outs
        in_groups = {group[i] for i in ins if i in group}
        out_groups = {group[o] for o in outs if o in group}
        sources = set.intersection(*(homes[i] for i in ins)) if ins else set()
        targets = set.intersection(*(homes[o] for o in outs if o in group or not o.startswith('rcef.'))) \
            if outs else set()
        if in_groups and out_groups:
            for g in in_groups:
                fills[g, 'bridge'].add('read')
            for g in out_groups:
                fills[g, 'bridge'].add('written')
            continue
        for profile, _ in SETS:
            if profile in sources and out_groups:
                for g in out_groups:
                    fills[g, profile].add('in')
            if profile in targets and in_groups:
                for g in in_groups:
                    fills[g, profile].add('out')
    columns = [*SETS, ('bridge', 'Pose bridge')]
    cw, ch, x0, top = 92, 24, 214, 104
    width = x0 + cw * len(columns) + 24
    height = top + ch * (len(order) + 2) + 74
    svg = Svg(width, height, 'Which canonical groups each expression set fills',
              'One row per group of the canonical expression and viseme sets, with its number of signals, one column '
              'per expression set. '
              '"in" means an in-map writes the group from the set; "out" means an out-map writes the set from '
              'the group. The last column shows the groups that the viseme pose bridge reads and writes.')
    svg.text(24, 32, 'Which canonical groups each expression set fills', size=17, weight='600')
    svg.text(24, 52, f'Data {pack["data_version"]}. "in": an in-map writes the group from the set. "out": an out-map '
             'writes the set from the group. A route needs both ends.', fill=MUTED)
    svg.text(24, 70, 'Both canonical sets are drafts (vocabulary status "draft").', fill=MUTED)
    for j, (_, label) in enumerate(columns):
        svg.text(x0 + j * cw + cw / 2, top - 8, label, weight='600', anchor='middle')
    y = top
    current = None
    for profile, g in order:
        if profile != current:
            current = profile
            total = sum(n for (p, _), n in size.items() if p == profile)
            name = 'Canonical expression set' if profile == 'canonical_expression' else 'Canonical viseme set'
            svg.text(24, y + 17, f'{name} ({total} signals)', size=12, fill=MUTED, weight='600')
            y += ch
        svg.text(36, y + 16, f"{g.replace('_', ' ')} ({size[profile, g]})")
        for j, (column, _) in enumerate(columns):
            state = fills.get((g, column), set())
            x = x0 + j * cw
            if column == 'bridge':
                label = ' and '.join(sorted(state))
                fill, ink = (BLUE_T, BLUE) if state else (CARD, MUTED)
            else:
                label = {frozenset({'in', 'out'}): 'in + out', frozenset({'in'}): 'in',
                         frozenset({'out'}): 'out'}.get(frozenset(state), '')
                fill, ink = {'in + out': (GREEN_T, GREEN), 'in': (BLUE_T, BLUE),
                             'out': (AMBER_T, AMBER)}.get(label, (CARD, MUTED))
            svg.rect(x + 2, y + 2, cw - 4, ch - 4, fill, stroke=LINE)
            if label:
                svg.text(x + cw / 2, y + 16, label, size=11, fill=ink, weight='600', anchor='middle')
        y += ch
    svg.text(24, y + 24, 'The bridge reads only the viseme classes that passed its calibration record; it maps no '
             'expression back to visemes.', fill=MUTED)
    svg.text(24, y + 42, 'Source: generated/rcef.pack.json. README "Routes" lists every route.', fill=MUTED)
    return svg.render()


def rows(path: Path) -> list[dict]:
    with path.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def ab_figure() -> str:
    ledger = [line.split() for line in (ROOT / 'ab/FREEZES').read_text(encoding='utf-8').splitlines()
              if line and not line.startswith('#')]
    run_id, version = ledger[-1][0], ledger[-1][1]
    results = ROOT / 'ab/results' / version
    manifest = json.loads((results / 'manifest.json').read_text(encoding='utf-8'))
    abreg = json.loads((ROOT / f'ab/{run_id}-{version}.abreg').read_text(encoding='utf-8'))
    reference = {}
    for line in (results / 'scoreboard.md').read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip('|').split('|')]
        if line.startswith('| ') and len(cells) == 5 and ' -> ' in cells[0]:
            reference[cells[0]] = cells[4]
    frames = collections.Counter()
    for row in rows(results / 'b_equals_o.csv'):
        frames[row['pair']] += int(row['frames'])
    refused = collections.defaultdict(set)
    for row in rows(results / 'refusals.csv'):
        refused[row['arm'], row['pair']].add((row['family'], row['frame']))
    bridged = {p for p, v in abreg['pairs'].items() if v['bridges']}
    names = {profile: label for profile, label in SETS}
    pair_of = {(names[v['source']], names[v['target']]): p for p, v in abreg['pairs'].items()}
    sources = [label for _, label in SETS if any(s == label for s, _ in pair_of)]
    targets = [label for _, label in SETS if any(t == label for _, t in pair_of)]
    style = {'A1': (BLUE, BLUE_T), 'A2': (AMBER, AMBER_T), 'A3': (GREEN, GREEN_T),
             'no external reference': (GREY, GREY_T)}
    cw, ch, x0, top = 118, 64, 110, 128
    width = x0 + cw * len(targets) + 24
    height = top + ch * len(sources) + 112
    passed = 'every gate passes' if manifest['passed'] else 'NOT every gate passes'
    svg = Svg(width, height, f'A/B comparison {run_id} {version}: the result for each route',
              'One cell per source and target set. The colour and the first line give the external reference; '
              'the cell gives the frames and the frames that B refuses. A dashed border marks a route through the '
              'viseme pose bridge.')
    svg.text(24, 32, f'A/B comparison {run_id} {version} ({manifest["kind"]}): {passed}', size=17, weight='600')
    svg.text(24, 52, f'B (the route through the canonical sets) runs on {len(pair_of)} routes and '
             f'{sum(frames.values()):,} frames, and gives the oracle\'s values on every frame.', fill=MUTED)
    svg.text(24, 70, 'A1: the retired direct map. A2: two retired direct maps in turn. A3: the expression '
             'library\'s FACS table. On each A1 route, B equals A1.', fill=MUTED)
    svg.text(24, 88, 'Most routes have no external reference: they are checked against the oracle only.', fill=MUTED)
    svg.text(x0 + cw * len(targets) / 2, top - 26, 'Target set', fill=MUTED, weight='600', anchor='middle')
    svg.text(24, top - 8, 'Source set', fill=MUTED, weight='600')
    for j, label in enumerate(targets):
        svg.text(x0 + j * cw + cw / 2, top - 8, label, weight='600', anchor='middle')
    for i, source in enumerate(sources):
        y = top + i * ch
        svg.text(24, y + ch / 2 + 4, source, weight='600')
        for j, target in enumerate(targets):
            x = x0 + j * cw
            pair = pair_of.get((source, target))
            if pair is None:
                svg.rect(x + 2, y + 2, cw - 4, ch - 4, CARD, stroke=LINE)
                svg.text(x + cw / 2, y + ch / 2 + 4, 'no route', size=11, fill=MUTED, anchor='middle')
                continue
            ref = reference[pair]
            hue, tint = style['A3' if ref.startswith('A3') else ref]
            dashed = pair in bridged
            svg.rect(x + 2, y + 2, cw - 4, ch - 4, tint, stroke=INK if dashed else None,
                     dash='5 3' if dashed else None, width=1.5)
            svg.rect(x + 2, y + 2, 5, ch - 4, hue, rx=2)
            label = 'A3, then A1' if ref == 'A3' and pair in {'FACS -> ARKit'} else (
                'no ext. ref.' if ref == 'no external reference' else ref)
            svg.text(x + 13, y + 19, label, size=11, weight='600')
            svg.text(x + 13, y + 35, f'{frames[pair]:,} frames', size=11)
            svg.text(x + 13, y + 51, f'B refuses {len(refused["B", pair]):,}', size=11, fill=MUTED)
    y = top + len(sources) * ch + 26
    svg.rect(24, y - 12, 18, 14, CARD, stroke=INK, dash='5 3', width=1.5)
    svg.text(48, y, 'Dashed border: the route runs the viseme pose bridge.', fill=MUTED)
    svg.text(24, y + 20, '"B refuses" counts frames on which at least one map refuses. Refusals are expected: the '
             'frames include planted faults (values out of range,', fill=MUTED)
    svg.text(24, y + 38, 'missing or invalid channels, non-finite edge values). On each A1 route, A1 refuses the same '
             'frames as B.', fill=MUTED)
    svg.text(24, y + 58, f'Source: ab/results/{version}/ (scoreboard.md, b_equals_o.csv, refusals.csv, '
             'manifest.json) and the registration.', fill=MUTED)
    return svg.render()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write the figures instead of checking them')
    args = parser.parse_args()
    pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
    figures = {'docs/routes.svg': routes_figure(pack), 'docs/ab-coverage.svg': ab_figure()}
    stale = []
    for name, text in figures.items():
        path = ROOT / name
        if args.write:
            path.write_text(text, encoding='utf-8')
        elif not path.exists() or path.read_text(encoding='utf-8') != text:
            stale.append(name)
    for name in stale:
        print(f'{name} is out of date; run scripts/export_figures.py --write')
    return 1 if stale else 0


if __name__ == '__main__':
    raise SystemExit(main())
