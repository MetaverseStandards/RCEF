#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write the canonical expression profile and the maps between it and each expression set.

The output is data. The script only reads:

- docs/canonical-set.md: the signal table (short names, labels, sides,
  regions, groups, definitions and FACS codes) and the calibration strings;
- docs/canonical-set-audit.md: the audit table of each source (its names,
  verdicts and loss keys), the ICT-FaceKit table and the loss-key texts;
- tests/fixtures/baseline-dea1713.pack.json: today's direct maps. They give
  the operators, weight order and knots of the ARKit and FB2 out-maps, the
  crosswalk evidence each hop takes over, and the assumptions that the
  assumption catalogue carries over.

It writes data/canonical_expression.toml and mappings/canonical_<set>.toml.
With --write it rewrites them; without it, it exits non-zero if any of them
is out of date. Each output section is made per profile and per map, so a new
profile (such as the canonical visemes) or a new group adds its own section.
"""
from __future__ import annotations
import argparse
import difflib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SIGNAL_DOC = 'docs/canonical-set.md'
AUDIT_DOC = 'docs/canonical-set-audit.md'
A1_FIXTURE = 'tests/fixtures/baseline-dea1713.pack.json'
PROFILE = 'rcef.canonical_expression'
OWN = 'rcef_canonical_v1'
FACS_RECORD = 'facs_wikipedia'
# Groups of the signal table that are not in the pack yet: the FB2-only signals (cheek_suck, lip_tighten,
# tongue_place) and the VRCFaceTracking pupils (pupil_mm) come with their own in-maps.
LATER_GROUPS = ('cheek_suck', 'lip_tighten', 'tongue_place', 'pupil_mm')
# Today's direct maps (A1). The viseme map is read only for its source signals.
A1_MAPS = ('arkit.to_fb2', 'arkit_gaze.to_fb2', 'fb2.to_arkit', 'fb2_gaze.to_arkit', 'arkit.to_vrcft_artist',
           'fb2.to_vrm', 'visemes.to_vrm')
OLD_HELPER = re.compile(r'^rcef\.intermediate\.arkit_gaze_(in_minus_out|up_minus_down)_([LR])$')
INTERMEDIATE = 'rcef.intermediate.'

# One entry per expression set that has hops. `audit` is the heading of its table in the audit; `records` are
# its own definition records, which every hop of the set cites first; `maps` names the directions it has.
PROVIDERS = {
    'arkit': {'name': 'ARKit', 'audit': 'ARKit', 'id': 'arkit.coefficient.{}', 'records': ['apple_blendshapes'],
              'maps': ('in', 'out')},
    'fb2': {'name': 'FB2', 'audit': 'FB2', 'id': 'openxr.fb2.XR_FACE_EXPRESSION2_{}_FB', 'records': ['xr_fb2'],
            'maps': ('in', 'out')},
    'vrcft_artist': {'name': 'Unified Expressions', 'audit': 'VRCFaceTracking Unified Expressions',
                     'id': 'vrcft.artist.base.{}', 'records': ['vrcft_artist', 'vrcft_docs_shapes'], 'maps': ('out',)},
    'vrm': {'name': 'VRM', 'audit': 'VRM', 'id': 'vrm.preset.{}', 'records': ['vrm_expressions'], 'maps': ('out',)},
}
FILES = {'arkit': 'mappings/canonical_arkit.toml', 'fb2': 'mappings/canonical_fb2.toml',
         'vrcft_artist': 'mappings/canonical_vrcft_artist.toml', 'vrm': 'mappings/canonical_vrm.toml'}
REGION = {'Brows': 'brow', 'Eyes and eyelids': 'eyelid', 'Gaze': 'gaze', 'Cheeks': 'cheek', 'Nose': 'nose',
          'Jaw': 'jaw', 'Mouth': 'mouth', 'Lips': 'mouth', 'Tongue': 'tongue', 'Pupils': 'pupil'}
AUDIT_ANCHORS = {'FB2': 'fb2', 'ARKit': 'arkit', 'VRCFaceTracking Unified Expressions':
                 'vrcfacetracking-unified-expressions', 'VRCFaceTracking eye': 'vrcfacetracking-eye', 'VRM': 'vrm',
                 'FACS': 'facs', 'FACS crosswalk: ICT-FaceKit': 'facs-crosswalk-ict-facekit'}

# Loss texts that are not audit keys. Tests match the first three exactly or by phrase.
SYMMETRY = 'asymmetry unknown: symmetry is invented'
ASYMMETRY = 'asymmetry irrecoverable'
NETTING = ('FB2 allows only one of two opposing gaze directions to be non-zero; when both canonical directions of a '
           'pair are non-zero, only their difference is kept, as the larger direction reduced by the smaller')
ROUNDING = ('outputs below 0.5 on the negative knot segment may change by up to 2⁻⁵⁴ in rounding; values at or '
            'below 2⁻⁵⁴ become 0')
GAIN = '{} gain and full-activation pose not published'
NO_LENGTH = 'the tongue extension has no stated length'
SPLIT_KEY = 'vrcft_ue_set_equal'
# Audit loss keys that belong to a whole hop, not to one signal's audit row: (set, direction, group) -> keys.
HOP_KEYS = {('fb2', 'in', 'gaze'): ['fb2_gaze_exclusive']}
OPENING = ("{} 0 and 1 for this shape are assumed to be canonical 0 and 1, and values between are assumed to "
           'correspond as the operator passes them; no evidence supports this, and no response curve is measured')
CLAUSES = {'in_copy': 'the value is carried over unchanged',
           'in_fan': 'the one {name} value is copied into each part',
           'out_copy': 'the value is carried over unchanged',
           'out_fan': 'the one canonical value is copied into each {name} part',
           'out_mean': 'the {name} value is the mean of the canonical parts',
           'out_net': 'the larger of two opposing directions is reduced by the smaller; only the difference is kept'}
DIFFERS = 'the endpoints are assumed equal although the defined actions differ or are unresolved; see {}'


# ---------------------------------------------------------------- reading the documents

def split_cells(line: str) -> list[str]:
    cells = re.split(r'(?<!\\)\|', line.strip().strip('|'))
    return [c.strip().replace('\\|', '|') for c in cells]


def table(text: str, heading: str) -> list[dict]:
    """The first Markdown table after a heading line, as one dict per row keyed by the header cells."""
    lines = text.splitlines()
    start = lines.index(heading)
    rows, header = [], None
    for line in lines[start + 1:]:
        if line.startswith('#'):
            break
        if not line.startswith('|'):
            if header:
                break
            continue
        cells = split_cells(line)
        if header is None:
            header = cells
        elif not set(line) <= set('|-: '):
            rows.append(dict(zip(header, cells)))
    if not rows:
        raise SystemExit(f'{heading}: no table')
    return rows


def plain(text: str) -> str:
    """Document text for a data string: no code marks, and a link to a section names the section and its file."""
    text = re.sub(r'\[([^\]]+)\]\(#[^)]+\)', rf'\1 in {SIGNAL_DOC}', text)
    return text.replace('`', '')


def ticks(cell: str) -> list[str]:
    return re.findall(r'`([^`]+)`', cell)


def read_documents(root: Path) -> dict:
    signal_doc = (root / SIGNAL_DOC).read_text(encoding='utf-8')
    audit_doc = (root / AUDIT_DOC).read_text(encoding='utf-8')
    calibration = {}
    for kind, label in (('face', 'Expression signals'), ('gaze', 'Gaze')):
        found = re.search(rf'^- \*\*{label}:\*\* `(rcef\.canonical\.v1:<short_name>: [^`]+)`$', signal_doc, re.M)
        calibration[kind] = found.group(1)
    groups = [ticks(r['Group'])[0] for r in table(signal_doc, '### Groups')]
    signals = []
    for row in table(signal_doc, '### Expression signals'):
        facs = re.match(r'(\d+)\b.*\(`(main|gross_behavior)`\)$', row['FACS code (table)'])
        signals.append({'short': ticks(row['Short name'])[0], 'label': row['Label'], 'side': row['Side'],
                        'region': REGION[row['Region']], 'group': row['Group'], 'definition': plain(row['Definition']),
                        'facs_au': facs.group(1) if facs else '', 'facs_table': facs.group(2) if facs else ''})
    keys = {}
    for row in table(audit_doc, '## Loss keys'):
        text = re.sub(r' \(the wording of [^)]*\)$', '', row['Loss text'])
        keys[ticks(row['Key'])[0]] = text
    audit = {}
    for key, spec in PROVIDERS.items():
        rows = {}
        for row in table(audit_doc, '## ' + spec['audit']):
            short = ticks(row['Signal'])[0]
            names = ticks(row['Source name']) or row['Source name'].split(' and ')
            rows[short] = {'names': [spec['id'].format(n) for n in names], 'verdict': row['Verdict'],
                           'keys': [k for k in ticks(row['Owning hop, key']) if k in keys]}
        audit[key] = rows
    ict = {}
    for row in table(audit_doc, '## FACS crosswalk: ICT-FaceKit'):
        ict[ticks(row['Signal'])[0]] = {'code': re.match(r'AU(\d+)', row['ICT FACS unit']).group(1),
                                        'verdict': row['Verdict'],
                                        'keys': [k for k in ticks(row['Owning hop, key']) if k in keys]}
    facs = {ticks(r['Signal'])[0] for r in table(audit_doc, '## FACS')}
    return {'calibration': calibration, 'groups': groups, 'signals': signals, 'keys': keys, 'audit': audit,
            'ict': ict, 'facs_rows': facs}


# ---------------------------------------------------------------- today's direct maps

def provider_of(sid: str) -> str | None:
    for key, spec in PROVIDERS.items():
        prefix = spec['id'].split('{')[0]
        if sid.startswith(prefix):
            return key
    return None


def read_a1(root: Path) -> dict:
    """Each final rule of today's direct maps as a chain: the rules behind its output and the inputs they read."""
    document = json.loads((root / A1_FIXTURE).read_text(encoding='utf-8'))
    maps = {m['id']: m['rules'] for m in document['mappings']}
    chains = []
    for map_id in A1_MAPS:
        by_output = {r['outputs'][0]: r for r in maps[map_id]}
        for rule in maps[map_id]:
            output = rule['outputs'][0]
            if output.startswith(INTERMEDIATE):
                continue
            found, leaves, todo = [], [], [output]
            while todo:
                current = todo.pop(0)
                if current in by_output:
                    found.append(by_output[current])
                    todo += by_output[current]['inputs']
                elif current not in leaves:
                    leaves.append(current)
            evidence = list(dict.fromkeys(e for r in found for e in r['evidence']))
            assumptions = list(dict.fromkeys(a for r in found for a in r['assumptions']))
            chains.append({'map': map_id, 'rule': rule, 'rules': found, 'inputs': leaves, 'output': output,
                           'evidence': evidence, 'assumptions': assumptions})
    return {'maps': maps, 'chains': chains}


# ---------------------------------------------------------------- the data model

class Builder:
    def __init__(self, root: Path = ROOT):
        self.docs = read_documents(root)
        self.a1 = read_a1(root)
        self.groups = [g for g in self.docs['groups']
                       if g not in LATER_GROUPS and any(s['group'] == g for s in self.docs['signals'])]
        self.signals = [s for s in self.docs['signals'] if s['group'] in self.groups]
        self.by_short = {s['short']: s for s in self.signals}
        self.audit = self.docs['audit']
        # Provider signal -> the canonical signals it is aligned with, per set (from the audit tables).
        self.aligned = {key: {} for key in PROVIDERS}
        for key, rows in self.audit.items():
            for short, row in rows.items():
                if short in self.by_short:
                    for sid in row['names']:
                        self.aligned[key].setdefault(sid, []).append(short)

    # -- names
    def cid(self, short: str) -> str:
        return f'{PROFILE}.{short}'

    def native(self, key: str, sid: str) -> str:
        prefix, suffix = PROVIDERS[key]['id'].split('{}')
        return sid[len(prefix):len(sid) - len(suffix) if suffix else None]

    def names(self, key: str, shorts: list[str]) -> list[str]:
        return list(dict.fromkeys(self.native(key, n) for s in shorts for n in self.audit[key][s]['names']))

    # -- evidence
    def crosswalks(self, key: str, sid: str) -> dict[str, list[str]]:
        """Per other set: the records of today's chains that link `sid` to that set, less both sets' own records."""
        found: dict[str, list[str]] = {}
        for chain in self.a1['chains']:
            if sid in chain['inputs']:
                others = [chain['output']]
            elif sid == chain['output']:
                others = chain['inputs']
            else:
                continue
            for other in others:
                other_key = provider_of(other)
                if other_key is None or other_key == key:
                    continue
                own = PROVIDERS[key]['records'] + PROVIDERS[other_key]['records']
                records = found.setdefault(other_key, [])
                records += [e for e in chain['evidence'] if e not in own and e not in records]
        return found

    def evidence(self, key: str, sid: str) -> list[str]:
        records = list(PROVIDERS[key]['records'])
        for found in self.crosswalks(key, sid).values():
            records += [e for e in found if e not in records and (e != 'ict_facekit' or key == 'arkit')]
        return records + [OWN]

    # -- assumptions
    def correspondence(self, key: str, kind: str, sid: str, shorts: list[str]) -> str:
        name = PROVIDERS[key]['name']
        native = self.native(key, sid)
        if kind == 'in_fan':
            every = self.aligned[key][sid]
            return (f'correspondence: {name} {native} is one value for canonical {join(every)}; this mapping '
                    f'writes {shorts[0]}.')
        if kind == 'out_fan':
            return (f'correspondence: {name} {join(self.names(key, shorts))} together correspond to canonical '
                    f'{shorts[0]}; this mapping writes {native}.')
        return f'correspondence: {name} {native} corresponds to canonical {join(shorts)}.'

    def endpoints(self, key: str, kind: str, shorts: list[str]) -> str:
        name = PROVIDERS[key]['name']
        text = f'endpoints: {OPENING.format(possessive(name))}; {CLAUSES[kind].format(name=name)}'
        keys = list(dict.fromkeys(k for s in shorts if self.audit[key][s]['verdict'] != 'same'
                                  for k in self.audit[key][s]['keys']))
        if keys:
            text += '; ' + DIFFERS.format(('losses ' if len(keys) > 1 else 'loss ') + join(keys))
        return text + '.'

    def transfers(self, key: str, sid: str, shorts: list[str]) -> list[str]:
        name, native = PROVIDERS[key]['name'], self.native(key, sid)
        out = []
        crosswalks = self.crosswalks(key, sid)
        for other in PROVIDERS:
            records = [e for e in crosswalks.get(other, []) if e != 'ict_facekit']
            if not records:
                continue
            other_name = PROVIDERS[other]['name']
            other_names = self.names(other, [s for s in shorts if s in self.audit[other]])
            head = f'correspondence evidence is {other_name}↔{name} ({", ".join(records)})'
            # Withdrawn when either set's audit row for the canonical signal is not `same`: the other set's or its own.
            reasons, keys = [], []
            for short in shorts:
                for who in (other, key):
                    row = self.audit[who].get(short)
                    if not row or row['verdict'] == 'same':
                        continue
                    who_names = self.names(who, [short])
                    verb = (('differ from', 'are unresolved against') if len(who_names) > 1 else
                            ('differs from', 'is unresolved against'))[row['verdict'] != 'differs']
                    reason = f'{PROVIDERS[who]["name"]} {join(who_names)} {verb} canonical {short}'
                    if reason not in reasons:
                        reasons.append(reason)
                    keys += row['keys']
            if reasons:
                keys = list(dict.fromkeys(keys))
                out.append(f'transfer.withdrawn: {head}; it does not carry over for the defined action, because the '
                           f'audit finds that {"; and that ".join(reasons)}; see {"losses" if len(keys) > 1 else "loss"} '
                           f'{join(keys)}.')
            else:
                verb = 'are' if len(shorts) > 1 else 'is'
                out.append(f'transfer.provider: {head}; it carries over because canonical {join(shorts)} {verb} '
                           f'defined to match {other_name} {join(other_names)}.')
        if key == 'arkit' and any('ict_facekit' in r for r in crosswalks.values()):
            out += self.ict_transfer(native, shorts)
        return out

    def ict_transfer(self, native: str, shorts: list[str]) -> list[str]:
        if all(self.by_short[s]['group'] == 'gaze' for s in shorts):
            return [f'transfer.facs_crosswalk: ict_facekit names ARKit {native} for an eye movement code; no FACS '
                    f'transfer claimed; canonical gaze has no FACS code.']
        rows = [self.docs['ict'][s] for s in shorts]
        code, canonical = rows[0]['code'], self.by_short[shorts[0]]['facs_au']
        have = 'have' if len(shorts) > 1 else 'has'
        if rows[0]['verdict'] == 'same':
            return [f'transfer.facs_crosswalk: ict_facekit relates FACS code {code} to ARKit {native}; it carries '
                    f'over because canonical {join(shorts)} {have} facs_au {canonical}.']
        return [f'transfer.withdrawn: ict_facekit relates FACS code {code} to ARKit {native}; it does not carry over '
                f'for the FACS code, because canonical {join(shorts)} {have} facs_au {canonical}; see loss '
                f'{join(rows[0]["keys"])}.']

    def a1_strings(self, sid: str, end: str, pattern: str, maps=None) -> list[str]:
        """Today's assumptions matching `pattern` on the chains that `sid` starts (end 'in') or ends (end 'out')."""
        found = []
        for chain in self.a1['chains']:
            if maps and chain['map'] not in maps:
                continue
            if (end == 'in' and sid in chain['inputs']) or (end == 'out' and sid == chain['output']):
                found += [a for a in chain['assumptions'] if re.match(pattern, a) and a not in found]
        return found

    def extras(self, key: str, kind: str, end: str, sid: str, shorts: list[str]) -> list[str]:
        out = []
        if key == 'fb2':
            out += ['evidence.vrcft_tables_not_cited: ' + a
                    for a in self.a1_strings(sid, end, r"VRCFaceTracking's tables are not cited")]
        godot_maps = ('arkit.to_fb2', 'fb2.to_arkit') + (('arkit.to_vrcft_artist',) if end == 'out' else ())
        for text in self.a1_strings(sid, end, r'FLAGGED: (only Godot names|VRCFaceTracking\'s ARKit table)', godot_maps):
            if found := re.search(r' for this channel; see fb2_arkit\.(\w+)\.$', text):
                full = self.a1_strings(PROVIDERS['arkit']['id'].format(found.group(1)), 'out',
                                       r'FLAGGED: only Godot names ARKit \w+ for this channel \(', ('fb2.to_arkit',))
                text = full[0]
            out.append('evidence.godot_only_mouth_shift: ' + text)
        if kind == 'out_mean':
            for text in self.a1_strings(sid, 'out', r'ARKit \w+ is one coefficient'):
                for fb2_sid, short in self.fb2_to_short().items():
                    text = re.sub(rf'\b{self.native("fb2", fb2_sid)}\b', short, text)
                text = text.replace('of the four quarters of FB2 ', 'of the four canonical quarters ')
                out.append('mean.arkit: ' + text.replace(' of FB2 ', ' of canonical '))
        if kind == 'out_fan':
            native = self.native(key, sid)
            parts = [self.native(key, n) for n, s in self.aligned[key].items() if s == shorts and n != sid]
            for text in self.a1_strings(sid, 'out', r'ARKit \w+ is a blended Unified Expressions shape'):
                listed = re.match(r'^ARKit \w+ is a blended Unified Expressions shape; (\w+) is set to the ARKit '
                                  r'value, as is ([\w, ]+)\. (.*)$', text)
                every = [listed.group(1), *listed.group(2).split(', ')]
                head = (f'canonical {shorts[0]} is one whole action, which Unified Expressions splits into parts; '
                        f'{native} is set to the canonical value, as is {join(parts)}. ')
                if sorted(every) == sorted([native, *parts]):
                    tail = listed.group(3).replace('the ARKit value', 'the canonical value')
                else:
                    others = [n for n in self.aligned[key] if self.native(key, n) in every
                              and self.aligned[key][n] != shorts]
                    other = self.aligned[key][others[0]][0]
                    tail = (f'VRCFaceTracking computes the blended shape as the mean of {join(every)}. The canonical '
                            f'set holds the two sides apart: {other} goes to {join(self.native(key, n) for n in others)}, '
                            f'so the blended shape is the mean of canonical {shorts[0]} and {other}.')
                out.append('fan_out.vrcft_ue: ' + head + tail)
        if 'lips_toward' in shorts and end == 'out' and key == 'arkit':
            out.append('lips_toward.jaw_not_compensated: the value is copied without compensating for the jaw. '
                       'Canonical lips_toward follows FB2 LIPS_TOWARD, which closes the lips whatever the jaw does; '
                       'the audit rows are FB2 same, ARKit unresolved and Unified Expressions differs.')
        if key == 'vrm':
            side = self.by_short[shorts[0]]['side']
            out += [f'vrm.definitional_only: canonical {shorts[0]} (the upper lid of the {side} eye lowers until it '
                    f'covers the eye) corresponds to VRM preset {self.native(key, sid)} (closes the {side} eyelid); '
                    'definitional only: the definitions agree, but no published table maps FB2 or the canonical set '
                    'to VRM.']
            for text in self.a1_strings(sid, 'out', r'Both name sides from the subject\'s own face\. FLAGGED: '):
                out.append('vrm.side_caveat: ' + text.split('FLAGGED: ', 1)[1])
            out += ['vrm.downstream_effects: ' + a for a in self.a1_strings(sid, 'out', r'VRM isBinary and override')]
        return out

    def fb2_to_short(self) -> dict[str, str]:
        return {sid: shorts[0] for sid, shorts in self.aligned['fb2'].items() if len(shorts) == 1}

    # -- losses
    def losses(self, key: str, kind: str, shorts: list[str], negative: bool = False) -> list[str]:
        name = PROVIDERS[key]['name']
        out = {'in_fan': [SYMMETRY], 'out_mean': [ASYMMETRY], 'out_net': [NETTING]}.get(kind, [])
        if negative:
            out.append(ROUNDING)
        if key == 'vrm':
            out += [r.replace('an FB2 weight', 'a canonical value') for r in self.vrm_losses()]
        else:
            out.append(GAIN.format(name))
        for short in shorts:
            out += [f'{k}: {self.docs["keys"][k]}' for k in self.audit[key][short]['keys']
                    if f'{k}: {self.docs["keys"][k]}' not in out]
            if key == 'arkit' and short in self.docs['ict']:
                out += [f'{k}: {self.docs["keys"][k]}' for k in self.docs['ict'][short]['keys']
                        if f'{k}: {self.docs["keys"][k]}' not in out]
        groups = {s['group'] for s in self.signals if s['short'] in shorts}
        for group in groups:
            out += [f'{k}: {self.docs["keys"][k]}' for k in HOP_KEYS.get((key, kind.split('_')[0], group), [])]
        if 'tongue_out' in shorts:
            out.append(NO_LENGTH)
        return out

    def vrm_losses(self) -> list[str]:
        rule = self.a1['maps']['fb2.to_vrm'][0]
        return [loss['reason'] for loss in rule['loss_annotations']]

    # -- rules
    def rule(self, rid, inputs, outputs, operator, assumptions, losses, evidence) -> dict:
        refs = inputs + outputs
        return {'id': rid, 'inputs': inputs, 'outputs': outputs, 'operator': operator, 'disposition': 'mapped',
                'mapping_quality': 'approximate', 'evidence_status': 'proposed', 'assumptions': assumptions,
                'evidence': evidence,
                'loss_annotations': [{'category': 'signal', 'effect': 'approximated', 'reason': r, 'refs': refs,
                                      'units': '1'} for r in losses]}

    def hop(self, key, kind, end, rid, sid, shorts, inputs, outputs, operator, negative=False) -> dict:
        assumptions = [self.correspondence(key, kind, sid, shorts), self.endpoints(key, kind, shorts),
                       *self.transfers(key, sid, shorts), *self.extras(key, kind, end, sid, shorts)]
        return self.rule(rid, inputs, outputs, operator, assumptions, self.losses(key, kind, shorts, negative),
                         self.evidence(key, sid))

    def in_maps(self, key: str) -> list[dict]:
        maps = []
        for group in self.groups:
            rules = []
            for s in self.signals:
                if s['group'] != group or s['short'] not in self.audit[key]:
                    continue
                names = self.audit[key][s['short']]['names']
                if len(names) != 1:
                    raise SystemExit(f'{key} in-map: {s["short"]} needs one source name, not {names}')
                sid = names[0]
                kind = 'in_fan' if len(self.aligned[key][sid]) > 1 else 'in_copy'
                rules.append(self.hop(key, kind, 'in', f'{key}_rcef.{s["short"]}', sid, [s['short']], [sid],
                                      [self.cid(s['short'])], copy()))
            if rules:
                written = {r['outputs'][0] for r in rules}
                if written != {self.cid(s['short']) for s in self.signals if s['group'] == group}:
                    raise SystemExit(f'{key}_{group}.to_rcef does not write its whole group')
                maps.append({'id': f'{key}_{group}.to_rcef', 'rules': rules})
        return maps

    def out_rules(self, key: str) -> list[tuple[str, dict]]:
        """(group, rule) for every out-map rule of a set, in the order of today's map into that set."""
        found = []
        if key == 'arkit':
            fb2 = self.fb2_to_short()
            for map_id in ('fb2.to_arkit', 'fb2_gaze.to_arkit'):
                for a1 in self.a1['maps'][map_id]:
                    sid = a1['outputs'][0]
                    shorts = [fb2[i] for i in a1['inputs']]
                    if sorted(shorts) != sorted(self.aligned['arkit'][sid]):
                        raise SystemExit(f'{sid}: today\'s inputs disagree with the ARKit audit rows')
                    kind = 'out_mean' if a1['operator']['id'] == 'weighted_sum' else 'out_copy'
                    found.append((self.group(shorts), self.hop(key, kind, 'out', f'rcef_arkit.{self.native(key, sid)}',
                                                              sid, shorts, [self.cid(s) for s in shorts], [sid],
                                                              operator(a1['operator']))))
        elif key == 'fb2':
            for a1 in self.a1['maps']['arkit.to_fb2']:
                sid = a1['outputs'][0]
                shorts = self.aligned['fb2'][sid]
                found.append((self.group(shorts), self.hop(key, 'out_copy', 'out', f'rcef_fb2.{self.native(key, sid)}',
                                                          sid, shorts, [self.cid(shorts[0])], [sid], copy())))
            arkit = {sid: shorts[0] for sid, shorts in self.aligned['arkit'].items()}
            for a1 in self.a1['maps']['arkit_gaze.to_fb2']:
                output = a1['outputs'][0]
                if OLD_HELPER.match(output):
                    shorts = [arkit[i] for i in a1['inputs']]
                    helper = new_helper(output)
                    found.append(('gaze', self.rule(
                        f'rcef_fb2.{helper[len(INTERMEDIATE):]}', [self.cid(s) for s in shorts], [helper],
                        operator(a1['operator']), [self.net_pair(shorts), GAZE_EXCLUSIVE], [NETTING], ['xr_fb2', OWN])))
                    continue
                helper = new_helper(a1['inputs'][0])
                shorts = self.aligned['fb2'][output]
                knots = a1['operator']['knots']
                negative = knots[0][1] == 1.0
                rule = self.hop(key, 'out_net', 'out', f'rcef_fb2.{self.native(key, output)}', output, shorts,
                                [helper], [output], operator(a1['operator']), negative)
                rule['assumptions'].insert(2, self.net_split(output, shorts[0], helper, negative))
                found.append(('gaze', rule))
        elif key == 'vrcft_artist':
            for a1 in self.a1['maps']['arkit.to_vrcft_artist']:
                sid = a1['outputs'][0]
                shorts = self.aligned[key][sid]
                kind = 'out_fan' if len(self.audit[key][shorts[0]]['names']) > 1 else 'out_copy'
                found.append((self.group(shorts), self.hop(key, kind, 'out', f'rcef_vrcft_artist.{self.native(key, sid)}',
                                                          sid, shorts, [self.cid(shorts[0])], [sid], copy())))
        elif key == 'vrm':
            for a1 in self.a1['maps']['fb2.to_vrm']:
                sid = a1['outputs'][0]
                shorts = self.aligned[key][sid]
                found.append((self.group(shorts), self.hop(key, 'out_copy', 'out', f'rcef_vrm.{self.native(key, sid)}',
                                                          sid, shorts, [self.cid(shorts[0])], [sid], copy())))
        return found

    def net_pair(self, shorts: list[str]) -> str:
        return (f'net.fb2_gaze: canonical {shorts[0]} and {shorts[1]} are opposing directions of one eye; their '
                'difference, from -1 to 1, carries both.')

    def net_split(self, output: str, short: str, helper: str, negative: bool) -> str:
        name = helper[len(INTERMEDIATE):]
        part = f'how far {name} is below zero' if negative else f'{name} where it is above zero'
        return (f'net.fb2_gaze: FB2 {self.native("fb2", output)} is {part}; a one-sided split is exactly zero on its '
                'flat side, so the two FB2 directions of a pair are never both non-zero.')

    def group(self, shorts: list[str]) -> str:
        groups = {self.by_short[s]['group'] for s in shorts}
        if len(groups) != 1:
            raise SystemExit(f'{shorts} span groups {groups}')
        return groups.pop()

    def out_maps(self, key: str) -> list[dict]:
        rules = self.out_rules(key)
        maps = []
        for group in self.groups:
            mine = [r for g, r in rules if g == group]
            if mine:
                maps.append({'id': f'rcef_{group}.to_{key}', 'rules': mine})
        return maps

    def maps(self, key: str) -> list[dict]:
        spec = PROVIDERS[key]
        return (self.in_maps(key) if 'in' in spec['maps'] else []) + (self.out_maps(key) if 'out' in spec['maps'] else [])

    # -- signals
    def canonical_signals(self) -> list[dict]:
        out = []
        for s in self.signals:
            gaze = s['group'] == 'gaze'
            evidence = [OWN] + ([FACS_RECORD] if s['facs_au'] else [])
            if s['group'] in ('jaw_sideways', 'mouth_shift'):
                evidence += ['xr_fb2', 'xr_fb2_fig_eyes_closed_l', 'xr_fb2_fig_eyes_look_left_l',
                             'xr_fb2_fig_mouth_left', 'apple_blendshapes']
            aligned = {profile_of(k): self.names(k, [s['short']]) for k in PROVIDERS if s['short'] in self.audit[k]}
            anchors = [f'docs/canonical-set-audit.md#{AUDIT_ANCHORS[PROVIDERS[k]["audit"]]}'
                       for k in PROVIDERS if s['short'] in self.audit[k]]
            if s['short'] in self.docs['facs_rows']:
                anchors.append(f'docs/canonical-set-audit.md#{AUDIT_ANCHORS["FACS"]}')
            if s['short'] in self.docs['ict']:
                anchors.append(f'docs/canonical-set-audit.md#{AUDIT_ANCHORS["FACS crosswalk: ICT-FaceKit"]}')
            metadata = {
                'definition': s['definition'],
                'zero': ('the eye does not look in this direction' if gaze else
                         'the neutral face: relaxed, lids open and relaxed, eyes ahead, lips together, jaw closed, '
                         'tongue at rest'),
                'one': ("the source's maximum gaze in this direction" if gaze else
                        'full activation of the action, as the definition describes it'),
                'facs_au': s['facs_au'], 'facs_table': s['facs_table'], 'group': s['group'],
                'aligned_names': aligned, 'audit': anchors}
            out.append({'id': self.cid(s['short']), 'label': s['label'], 'value_type': 'scalar', 'units': '1',
                        'domain': {'min': 0.0, 'max': 1.0},
                        'calibration': self.docs['calibration']['gaze' if gaze else 'face'].replace(
                            '<short_name>', s['short']),
                        'disposition': 'mapped', 'evidence': evidence, 'evidence_status': 'proposed',
                        'side': s['side'], 'neutral': 0.0, 'metadata': metadata, 'region': s['region']})
        return out

    def profile(self) -> dict:
        return {'id': PROFILE, 'label': 'RCEF canonical expression set (draft)',
                'signal_ids': [self.cid(s['short']) for s in self.signals], 'evidence': [OWN],
                'metadata': {'vocabulary_version': '1.0', 'vocabulary_status': 'draft',
                             'scope': 'a pivot for translating between expression sets; each signal has a declared '
                                      'meaning, but no shared or measured gain',
                             'groups': self.groups}}


GAZE_EXCLUSIVE = 'gaze.fb2_exclusive: FB2 says only one of two opposing gaze directions is non-zero at a time (xr_fb2 lines 648-649).'


def profile_of(key: str) -> str:
    return {'arkit': 'arkit.coefficient', 'fb2': 'openxr.fb2', 'vrcft_artist': 'vrcft.artist.base',
            'vrm': 'vrm.preset'}[key]


def new_helper(old: str) -> str:
    found = OLD_HELPER.match(old)
    return f'{INTERMEDIATE}gaze_{found.group(1)}_{"left" if found.group(2) == "L" else "right"}'


def possessive(name: str) -> str:
    return name + ("'" if name.endswith('s') else "'s")


def operator(op: dict) -> dict:
    """An operator with its keys in the order the TOML files use."""
    order = ('id', 'scale', 'offset', 'weights', 'knots')
    return {k: op[k] for k in sorted(op, key=order.index)}


def copy() -> dict:
    return {'id': 'affine', 'scale': 1.0, 'offset': 0.0}


def join(items: list[str]) -> str:
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


# ---------------------------------------------------------------- TOML

def value(v) -> str:
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (int, float)):
        return repr(float(v)) if isinstance(v, float) else str(v)
    if isinstance(v, list):
        return '[' + ', '.join(value(x) for x in v) + ']'
    if isinstance(v, dict):
        return '{ ' + ', '.join(f'{json.dumps(k)} = {value(x)}' for k, x in v.items()) + ' }'
    raise TypeError(v)


HEADER = '''# SPDX-License-Identifier: CC-BY-SA-4.0
# Original RCEF data; attributed source identifiers are factual inventories.
# Written by scripts/build_canonical.py from docs/canonical-set.md,
# docs/canonical-set-audit.md and today's direct maps
# (tests/fixtures/baseline-dea1713.pack.json). Edit those, then run the script.
'''


def signals_toml(signals: list[dict], profile: dict) -> str:
    parts = [HEADER, '# The canonical expression set, vocabulary version 1.0 (draft). See docs/canonical-set.md.\n']
    for s in signals:
        parts.append('\n[[signals]]\n' + ''.join(f'{k} = {value(v)}\n' for k, v in s.items()))
    parts.append('\n[[profiles]]\n' + ''.join(f'{k} = {value(v)}\n' for k, v in profile.items()))
    return ''.join(parts)


def maps_toml(name: str, maps: list[dict]) -> str:
    parts = [HEADER, f'# The maps between the canonical expression set and {name}: one map per canonical group and\n'
                     '# direction. In-maps are <set>_<group>.to_rcef; out-maps are rcef_<group>.to_<set>.\n']
    for m in maps:
        parts.append(f'\n[[mappings]]\nid = {value(m["id"])}\n')
        for r in m['rules']:
            parts.append('\n[[mappings.rules]]\n')
            for k, v in r.items():
                if k in ('assumptions', 'loss_annotations'):
                    parts.append(f'{k} = [\n' + ''.join(f'  {value(x)},\n' for x in v) + ']\n')
                else:
                    parts.append(f'{k} = {value(v)}\n')
    return ''.join(parts)


def render(root: Path = ROOT) -> dict[str, str]:
    builder = Builder(root)
    files = {'data/canonical_expression.toml': signals_toml(builder.canonical_signals(), builder.profile())}
    for key, path in FILES.items():
        files[path] = maps_toml(PROVIDERS[key]['name'], builder.maps(key))
    return files


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n', 1)[0])
    parser.add_argument('--write', action='store_true', help='rewrite the output files')
    args = parser.parse_args(argv)
    stale = []
    for path, content in render().items():
        target = ROOT / path
        current = target.read_text(encoding='utf-8') if target.exists() else ''
        if current == content:
            continue
        if args.write:
            target.write_text(content, encoding='utf-8', newline='\n')
        else:
            stale.append(path)
            print(''.join(difflib.unified_diff(current.splitlines(True), content.splitlines(True), path, 'generated')),
                  end='')
    if stale:
        print(f'{", ".join(stale)} out of date; run scripts/build_canonical.py --write')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
