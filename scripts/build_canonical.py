#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write the canonical expression and viseme profiles and the maps between them and each expression set.

The output is data. The script only reads:

- docs/canonical-set.md: the signal tables (short names, labels, sides,
  regions, groups, definitions and FACS codes; for the visemes also the IPA
  symbols, shapes and floor classes) and the calibration strings;
- docs/canonical-set-audit.md: the audit table of each source (its names,
  verdicts and loss keys), the ICT-FaceKit table and the loss-key texts;
- tests/fixtures/ipa_chart_symbols.json: the IPA chart symbols of each viseme
  class, with their chart cells and evidence levels;
- tests/fixtures/baseline-dea1713.pack.json: the retired A1 direct maps. They
  give the operators, weight order and knots of the ARKit and FB2 out-maps,
  the crosswalk evidence each hop takes over, and the assumptions that the
  assumption catalogue carries over.

It writes data/canonical_expression.toml, data/canonical_viseme.toml and
mappings/canonical_<set>.toml.
With --write it rewrites them; without it, it exits non-zero if any of them
is out of date. Each output section is made per profile and per map, so a new
profile or a new group adds its own section.
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
# Groups of the signal table that are not in the pack yet. None today.
LATER_GROUPS = ()
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
    'vrm': {'name': 'VRM', 'audit': 'VRM', 'id': 'vrm.preset.{}', 'records': ['vrm_expressions'],
            'maps': ('in', 'out')},
    'vrcft_eye': {'name': 'VRCFaceTracking eye', 'audit': 'VRCFaceTracking eye', 'id': 'vrcft.eye.{}',
                  'records': ['vrcft_data'], 'maps': ('in', 'out')},
}
FILES = {'arkit': 'mappings/canonical_arkit.toml', 'fb2': 'mappings/canonical_fb2.toml',
         'vrcft_artist': 'mappings/canonical_vrcft_artist.toml', 'vrm': 'mappings/canonical_vrm.toml',
         'vrcft_eye': 'mappings/canonical_vrcft_eye.toml'}
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
CHAIN_LOSS = ('two-step crosswalk through Godot: Godot links FB2 to its own shape, and its shape to Unified Expressions '
              'by name; neither step alone links FB2 to Unified Expressions')
# The crosswalk records of the FB2-only signals that Unified Expressions also has (the audit's table of them).
SOURCE_CROSSWALKS = ['vrcft_docs_movement', 'godot_vendors_fb2', 'godot_enum', 'godot_face_modifier']
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
           'out_net': 'the larger of two opposing directions is reduced by the smaller; only the difference is kept',
           'in_invert': 'eye_close is 1 − Openness', 'out_invert': 'eye_close is 1 − Openness',
           'in_mm': 'the tracker-reported diameter is carried over unchanged',
           'out_mm': 'the tracker-reported diameter is carried over unchanged'}
# The VRCFaceTracking eye hops: Openness runs the other way from eye_close, and the pupils are a length.
INVERT_OPENING = ("{} Openness 1 and 0 are assumed to be canonical eye_close 0 and 1, and values between are assumed "
                  'to correspond as the operator passes them; no evidence supports this, and no response curve is '
                  'measured')
MM_OPENING = 'both ends are the pupil diameter in millimetres, as the tracker reports it'
OPENNESS_KEY = 'vrcft_eye_openness_neutral_unresolved'
VRM_IN_WEIGHT = 'an asset-authored expression weight becomes a canonical value'
VRM_BLINK_NOT_READ = 'VRM blink (both eyes) not read; when a model drives only blink, eye_close reads open'
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
    for kind, label in (('face', 'Expression signals'), ('gaze', 'Gaze'), ('pupil', 'Pupils')):
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
    sourced = {}
    for row in table(audit_doc, '## Crosswalks of the FB2-only signals'):
        sourced[ticks(row['Signal'])[0]] = {'names': {'fb2': row['FB2'], 'vrcft_artist': row['Unified Expressions']},
                                            'one_step': plain(row['One step']), 'to_godot': plain(row['FB2 to Godot']),
                                            'from_godot': plain(row['Godot to Unified Expressions'])}
    return {'calibration': calibration, 'groups': groups, 'signals': signals, 'keys': keys, 'audit': audit,
            'ict': ict, 'facs_rows': facs, 'sourced': sourced}


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

    def evidence(self, key: str, sid: str, shorts: list[str]) -> list[str]:
        records = list(PROVIDERS[key]['records'])
        for found in self.crosswalks(key, sid).values():
            records += [e for e in found if e not in records and (e != 'ict_facekit' or key == 'arkit')]
        if self.sourced(key, shorts):
            records += [e for e in SOURCE_CROSSWALKS if e not in records]
        return records + [OWN]

    def sourced(self, key: str, shorts: list[str]) -> dict | None:
        """The audit's crosswalk row of an FB2-only signal, on its FB2 and Unified Expressions hops."""
        rows = [self.docs['sourced'][s] for s in shorts if s in self.docs['sourced']]
        return rows[0] if rows and key in rows[0]['names'] else None

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
        opening = {'invert': INVERT_OPENING.format(possessive(name)), 'mm': MM_OPENING}.get(
            kind.split('_')[1], OPENING.format(possessive(name)))
        text = f'endpoints: {opening}; {CLAUSES[kind].format(name=name)}'
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
        if row := self.sourced(key, shorts):
            other = 'vrcft_artist' if key == 'fb2' else 'fb2'
            match = (f'it carries over because canonical {shorts[0]} is defined to match {PROVIDERS[other]["name"]} '
                     f'{row["names"][other]}.')
            out.append(f'transfer.provider: correspondence evidence is {PROVIDERS[other]["name"]}↔{name} '
                       f'(vrcft_docs_movement); {match}')
            out.append(f'transfer.chain: correspondence evidence is FB2↔Godot ({row["to_godot"]}) and Godot↔Unified '
                       f'Expressions ({row["from_godot"]}, which give the Unified Expressions name of each Godot '
                       f'shape); {match}')
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
        if kind.endswith('_invert'):
            out.append(f'vrcft_eye.openness: {self.docs["keys"][OPENNESS_KEY]}.')
        if key == 'vrm':
            side = self.by_short[shorts[0]]['side']
            out += [f'vrm.definitional_only: canonical {shorts[0]} (the upper lid of the {side} eye lowers until it '
                    f'covers the eye) corresponds to VRM preset {self.native(key, sid)} (closes the {side} eyelid); '
                    'definitional only: the definitions agree, but no published table maps FB2 or the canonical set '
                    'to VRM.']
            for text in self.a1_strings(sid, 'out', r'Both name sides from the subject\'s own face\. FLAGGED: '):
                out.append('vrm.side_caveat: ' + text.split('FLAGGED: ', 1)[1])
            if end == 'out':
                out += ['vrm.downstream_effects: ' + a for a in self.a1_strings(sid, 'out', r'VRM isBinary and override')]
        return out

    def fb2_to_short(self) -> dict[str, str]:
        return {sid: shorts[0] for sid, shorts in self.aligned['fb2'].items() if len(shorts) == 1}

    # -- losses
    def losses(self, key: str, kind: str, shorts: list[str], negative: bool = False) -> list[str]:
        name = PROVIDERS[key]['name']
        if kind.endswith('_mm'):
            return []
        out = {'in_fan': [SYMMETRY], 'out_mean': [ASYMMETRY], 'out_net': [NETTING]}.get(kind, [])
        if negative:
            out.append(ROUNDING)
        if key == 'vrm' and kind.startswith('in_'):
            out += [VRM_IN_WEIGHT, VRM_BLINK_NOT_READ]
        elif key == 'vrm':
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
        if key == 'vrcft_artist' and self.sourced(key, shorts):
            out.append(CHAIN_LOSS)
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
        rule = self.rule(rid, inputs, outputs, operator, assumptions, self.losses(key, kind, shorts, negative),
                         self.evidence(key, sid, shorts))
        if kind.endswith('_mm'):
            # The pupil copies restate a verified fact: one field in millimetres at both ends.
            rule.update(mapping_quality='exact', evidence_status='verified_current')
        return rule

    def eye_kind(self, key: str, group: str, end: str) -> tuple[str, dict] | None:
        """The kind and operator of a VRCFaceTracking eye hop: inverted for blink, a copy for the pupils."""
        if key != 'vrcft_eye':
            return None
        return (f'{end}_invert', invert()) if group == 'blink' else (f'{end}_mm', copy())

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
                kind, op = self.eye_kind(key, group, 'in') or (
                    'in_fan' if len(self.aligned[key][sid]) > 1 else 'in_copy', copy())
                rules.append(self.hop(key, kind, 'in', f'{key}_rcef.{s["short"]}', sid, [s['short']], [sid],
                                      [self.cid(s['short'])], op))
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
        elif key == 'vrcft_eye':
            for s in self.signals:
                if s['short'] in self.audit[key]:
                    sid = self.audit[key][s['short']]['names'][0]
                    kind, op = self.eye_kind(key, s['group'], 'out')
                    found.append((s['group'], self.hop(key, kind, 'out', f'rcef_vrcft_eye.{self.native(key, sid)}', sid,
                                                       [s['short']], [self.cid(s['short'])], [sid], op)))
        elif key == 'vrm':
            for a1 in self.a1['maps']['fb2.to_vrm']:
                sid = a1['outputs'][0]
                shorts = self.aligned[key][sid]
                found.append((self.group(shorts), self.hop(key, 'out_copy', 'out', f'rcef_vrm.{self.native(key, sid)}',
                                                          sid, shorts, [self.cid(shorts[0])], [sid], copy())))
        if key in ('fb2', 'vrcft_artist'):
            # Signals that today's map into this set does not write (the FB2-only signals), in signal-table order.
            written = {r['outputs'][0] for _, r in found}
            for s in self.signals:
                row = self.audit[key].get(s['short'])
                if not row or set(row['names']) & written:
                    continue
                if len(row['names']) != 1:
                    raise SystemExit(f'{key} out-map: {s["short"]} needs one target name, not {row["names"]}')
                sid = row['names'][0]
                found.append((s['group'], self.hop(key, 'out_copy', 'out', f'rcef_{key}.{self.native(key, sid)}', sid,
                                                   [s['short']], [self.cid(s['short'])], [sid], copy())))
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
            pupil = s['group'] == 'pupil_mm'
            evidence = [OWN] + ([FACS_RECORD] if s['facs_au'] else []) + (['vrcft_data'] if pupil else [])
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
                         'a reported diameter of 0 mm; the pupils have no neutral value' if pupil else
                         'the neutral face: relaxed, lids open and relaxed, eyes ahead, lips together, jaw closed, '
                         'tongue at rest'),
                'one': ("the source's maximum gaze in this direction" if gaze else
                        'a reported diameter of 1 mm' if pupil else
                        'full activation of the action, as the definition describes it'),
                'facs_au': s['facs_au'], 'facs_table': s['facs_table'], 'group': s['group'],
                'aligned_names': aligned, 'audit': anchors}
            kind = 'gaze' if gaze else 'pupil' if pupil else 'face'
            signal = {'id': self.cid(s['short']), 'label': s['label'], 'value_type': 'scalar',
                      'units': 'mm' if pupil else '1', 'domain': {} if pupil else {'min': 0.0, 'max': 1.0},
                      'calibration': self.docs['calibration'][kind].replace('<short_name>', s['short']),
                      'disposition': 'mapped', 'evidence': evidence,
                      'evidence_status': 'verified_current' if pupil else 'proposed', 'side': s['side'],
                      'neutral': 0.0, 'metadata': metadata, 'region': s['region']}
            if pupil:
                del signal['neutral']
            out.append(signal)
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
            'vrm': 'vrm.preset', 'vrcft_eye': 'vrcft.eye'}[key]


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


def invert() -> dict:
    return {'id': 'affine', 'scale': -1.0, 'offset': 1.0}


def join(items: list[str]) -> str:
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


# ---------------------------------------------------------------- FACS codes

FACS_PROFILE = 'facs.code'
FACS_FILE = 'profiles/facs.code.toml'
FACS_MAPS_FILE = 'mappings/canonical_facs.toml'
FACS_CODES = 'examples/data/facs_codes.json'
ROCKETBOX_FIXTURE = 'tests/fixtures/rocketbox_au_names.json'
HAGER = 'facs_hager_2002'
ROCKETBOX = 'rocketbox_avatars'
FACS_SPEC = {'name': 'FACS', 'records': [FACS_RECORD]}
# The FACS 2002 page backs AU43's scoring and the reasons of the old eye codes it folds into AU43.
HAGER_CODES = ('41', '42', '43', '44')
SIDE_KEY = 'facs_side_frame_unresolved'
FACS_CLAUSES = {'in_copy': 'the value is carried over unchanged',
                'in_fan': 'the one FACS side value is copied into the upper and the lower part',
                'out_copy': 'the value is carried over unchanged',
                'out_mean': 'the FACS side value is the mean of the upper and lower canonical parts'}
FACS_CALIBRATION_UNMAPPED = 'facs.code: no RCEF value of its own; see metadata.reason'
FACS_HEADER = '''# SPDX-License-Identifier: CC-BY-SA-4.0
# Original RCEF data; FACS code numbers and names are facts from a public list
# (record facs_wikipedia). This is not FACS coding, and the values are not FACS
# scores. Written by scripts/build_canonical.py from docs/canonical-set.md,
# docs/canonical-set-audit.md, examples/data/facs_codes.json and
# tests/fixtures/rocketbox_au_names.json. Edit those, then run the script.
'''


def section_tables(text: str, heading: str) -> list[list[dict]]:
    """Every Markdown table in the section under a heading line, in order."""
    lines = text.splitlines()
    start = lines.index(heading)
    end = next((n for n in range(start + 1, len(lines)) if lines[n].startswith('#')), len(lines))
    found, n = [], start + 1
    while n < end:
        if lines[n].startswith('|'):
            found.append(table('\n'.join([heading, *lines[n:end]]), heading))
            while n < end and lines[n].startswith('|'):
                n += 1
        n += 1
    return found


def file_links(text: str) -> str:
    """A Markdown link to another document becomes the document's path."""
    return re.sub(r'\[[^\]]+\]\(([\w-]+\.md)\)', r'docs/\1', text)


class FacsBuilder:
    """The facs.code profile and its maps: codes from the FACS data file, rows and texts from the documents."""

    def __init__(self, root: Path, builder: Builder):
        self.b = builder
        doc = (root / SIGNAL_DOC).read_text(encoding='utf-8')
        audit_doc = (root / AUDIT_DOC).read_text(encoding='utf-8')
        self.codes = json.loads((root / FACS_CODES).read_text(encoding='utf-8'))['codes']
        self.rocketbox = json.loads((root / ROCKETBOX_FIXTURE).read_text(encoding='utf-8'))['names']
        found = re.search(r'FACS hops start with their own assumption instead: "(.+?)"\. On the hops of the gross '
                          r'behaviour codes \([^)]*\) it reads: "(.+?)"\.', doc)
        self.opening = {'main': file_links(found.group(1)), 'gross_behavior': file_links(found.group(2))}
        self.calibration = {
            'main': re.search(r'Main codes: `(rcef\.facs\.v1:au<NN>: [^`]+)`', doc).group(1),
            'gross_behavior': re.search(r'Gross codes [\d, and]+: `(rcef\.facs\.v1:au<NN>: [^`]+)`', doc).group(1)}
        self.side_note = plain(re.search(r'\*\*Side note\*\* on every sided row: "([^"]+)"', doc).group(1))
        self.scope = re.search(r'`vocabulary_status = "draft"`, and the text "([^"]+)"', doc).group(1)
        self.unmapped = {}
        for row in table_after(doc, '## FACS', '**Rows that are not mapped.**'):
            for code in row['Codes'].replace('\\*', '*').split(', '):
                self.unmapped[code] = {'disposition': row['Disposition'], 'region': row['Region'],
                                       'reason': plain(row['Reason'])}
        rows, extra = section_tables(audit_doc, '## FACS')
        self.audit, self.aligned = {}, {}
        for row in rows:
            short = ticks(row['Signal'])[0]
            fid = ticks(row['FACS code (`facs.code` ID)'])[0]
            self.audit[short] = {'id': fid, 'verdict': row['Verdict'],
                                 'keys': [k for k in ticks(row['Owning hop, key']) if k in builder.docs['keys']]}
            self.aligned.setdefault(fid, []).append(short)
        # Encoding rows: keys for the hops of the signals named, or of every FACS hop when the row names none.
        self.encoding = []
        for row in extra:
            patterns = [t for t in ticks(row['Canonical signals']) if not t.startswith(FACS_PROFILE)]
            shorts = {s for s in self.audit if any(re.fullmatch(p.replace('*', r'\w+'), s) for p in patterns)}
            self.encoding.append((shorts or set(self.audit),
                                  [k for k in ticks(row['Owning hop, key']) if k in builder.docs['keys']]))
        for code, entry in self.codes.items():
            if entry['disposition'] in ('mapped', 'none'):
                continue
            if self.unmapped.get(code, {}).get('disposition') != entry['disposition']:
                raise SystemExit(f'FACS {code}: {FACS_CODES} and the rows that are not mapped disagree')

    # -- names
    def local(self, fid: str) -> str:
        return fid[len(FACS_PROFILE) + 1:]

    def code_of(self, fid: str) -> str:
        return next(c for c in self.codes if f'au{int(c.rstrip("*")):02d}' == self.local(fid).split('_')[0])

    def notation(self, fid: str) -> str:
        local = self.local(fid)
        side = local.split('_')[1] if '_' in local else ''
        return {'left': 'L', 'right': 'R', '': ''}[side] + self.code_of(fid)

    def shorts(self, fid: str) -> list[str]:
        return [s['short'] for s in self.b.signals if s['short'] in self.aligned.get(fid, [])]

    def rocketbox_names(self, code: str, side: str | None) -> list[str]:
        """The Rocketbox shapes of a code that act on the row's side: that side's shape and the both-sides shape."""
        found = []
        for name in self.rocketbox:
            match = re.fullmatch(r'AU_(\d\d)_(?:([LR])_)?\w+', name)
            if code.rstrip('*').isdigit() and int(match.group(1)) == int(code.rstrip('*')):
                if side is None or match.group(2) in (None, {'left': 'L', 'right': 'R'}[side]):
                    found.append(name)
        return found

    # -- signals
    def rows(self) -> list[dict]:
        """(fid, code, side, mapped) for every row, in code order, left before right."""
        out = []
        for code, entry in self.codes.items():
            if entry['disposition'] == 'none':
                continue
            base = f'{FACS_PROFILE}.au{int(code.rstrip("*")):02d}'
            if entry['disposition'] != 'mapped':
                out.append((base, code, None))
            elif entry['read'] == 'shared':
                out.append((base, code, None))
            else:
                out += [(f'{base}_{side}', code, side) for side in ('left', 'right')]
        return out

    def signals(self) -> list[dict]:
        out = []
        for fid, code, side in self.rows():
            entry = self.codes[code]
            names = self.rocketbox_names(code, side if entry['read'] == 'sided' else None)
            evidence = [FACS_RECORD] + ([ROCKETBOX] if names else []) + ([HAGER] if code in HAGER_CODES else [])
            label = f'AU {code} {entry["name"]}'
            metadata = {'facs_code': code, 'facs_table': entry['table']}
            if entry['disposition'] == 'mapped':
                shorts = self.shorts(fid)
                if not shorts:
                    raise SystemExit(f'{fid}: no canonical signal in the FACS audit')
                group = self.b.group(shorts)
                direction = entry['read'] == 'direction'
                label += f', toward the {side}' if direction else f', {side}' if side else ''
                metadata['group'] = group
                if names:
                    metadata['aligned_names'] = {ROCKETBOX: names}
                if side:
                    metadata['side_note'] = self.side_note
                verb = 'them' if len(shorts) > 1 else 'it'
                metadata['reason'] = (f'Code number and name from {FACS_RECORD}; read into canonical {join(shorts)} '
                                      f'by facs_{group}.to_rcef and written from {verb} by rcef_{group}.to_facs, both '
                                      f"proposed approximate hops; the numeric encoding is RCEF's own, not a FACS "
                                      f'score.')
                calibration = self.calibration[entry['table']].replace('au<NN>', self.local(fid))
                out.append({'id': fid, 'label': label, 'value_type': 'scalar', 'units': '1',
                            'domain': {'min': 0.0, 'max': 1.0}, 'calibration': calibration, 'disposition': 'mapped',
                            'evidence': evidence, 'evidence_status': 'proposed', 'native_id': self.notation(fid),
                            'surface': FACS_PROFILE, 'side': 'shared' if direction else side or 'shared',
                            'neutral': 0.0, 'metadata': metadata, 'region': self.b.by_short[shorts[0]]['region']})
                continue
            row = self.unmapped[code]
            if names:
                metadata['aligned_names'] = {ROCKETBOX: names}
            metadata['reason'] = row['reason'][0].upper() + row['reason'][1:] + '.'
            out.append({'id': fid, 'label': label, 'value_type': 'scalar', 'units': 'unknown', 'domain': {},
                        'calibration': FACS_CALIBRATION_UNMAPPED, 'disposition': entry['disposition'],
                        'evidence': evidence, 'evidence_status': 'proposed', 'native_id': code,
                        'surface': FACS_PROFILE, 'side': 'shared', 'metadata': metadata, 'region': row['region']})
        return out

    def profile(self, signals: list[dict]) -> dict:
        groups = [g for g in self.b.groups if any(s['metadata'].get('group') == g for s in signals)]
        return {'id': FACS_PROFILE, 'label': 'FACS codes in RCEF numeric encoding (draft)',
                'signal_ids': [s['id'] for s in signals], 'evidence': [FACS_RECORD],
                'metadata': {'vocabulary_version': '1.0', 'vocabulary_status': 'draft', 'scope': self.scope,
                             'groups': groups}}

    # -- hops
    def hop(self, kind: str, rid: str, fid: str, shorts: list[str], inputs, outputs, operator: dict) -> dict:
        notation, code = self.notation(fid), self.code_of(fid)
        if kind == 'in_fan':
            correspondence = (f'correspondence: FACS {notation} is one value for canonical {join(self.shorts(fid))}; '
                              f'this mapping writes {shorts[0]}.')
        else:
            correspondence = f'correspondence: FACS {notation} corresponds to canonical {join(shorts)}.'
        endpoints = f'endpoints: {self.opening[self.codes[code]["table"]]}; {FACS_CLAUSES[kind]}'
        rows = [self.audit[s] for s in shorts]
        keys = list(dict.fromkeys(k for r in rows if r['verdict'] != 'same' for k in r['keys']))
        if keys:
            endpoints += '; ' + DIFFERS.format(('losses ' if len(keys) > 1 else 'loss ') + join(keys))
        losses = {'in_fan': [SYMMETRY], 'out_mean': [ASYMMETRY]}.get(kind, [])
        every = [k for named, ks in self.encoding if named == set(self.audit) for k in ks]
        found = every + ([SIDE_KEY] if notation[0] in 'LR' else []) + [k for r in rows for k in r['keys']]
        found += [k for named, ks in self.encoding if named != set(self.audit) and set(shorts) & named for k in ks]
        losses += [f'{k}: {self.b.docs["keys"][k]}' for k in dict.fromkeys(found)]
        if 'tongue_out' in shorts:
            losses.append(NO_LENGTH)
        evidence = [FACS_RECORD] + ([HAGER] if code == '43' else []) + [OWN]
        return self.b.rule(rid, inputs, outputs, operator, [correspondence, endpoints + '.'], losses, evidence)

    def in_maps(self) -> list[dict]:
        maps = []
        for group in self.b.groups:
            members = [s['short'] for s in self.b.signals if s['group'] == group]
            mine = [s for s in members if s in self.audit]
            if not mine:
                continue
            if mine != members:
                raise SystemExit(f'facs_{group}.to_rcef does not write its whole group')
            rules = []
            for short in mine:
                fid = self.audit[short]['id']
                kind = 'in_fan' if len(self.aligned[fid]) > 1 else 'in_copy'
                rules.append(self.hop(kind, f'facs_rcef.{short}', fid, [short], [fid], [self.b.cid(short)], copy()))
            maps.append({'id': f'facs_{group}.to_rcef', 'rules': rules})
        return maps

    def out_maps(self, signals: list[dict]) -> list[dict]:
        maps = []
        for group in self.b.groups:
            rules = []
            for s in signals:
                if s['disposition'] != 'mapped' or s['metadata']['group'] != group:
                    continue
                shorts = self.shorts(s['id'])
                mean = len(shorts) > 1
                operator = {'id': 'weighted_sum', 'weights': [0.5] * len(shorts)} if mean else copy()
                rules.append(self.hop('out_mean' if mean else 'out_copy', f'rcef_facs.{self.local(s["id"])}', s['id'],
                                      shorts, [self.b.cid(x) for x in shorts], [s['id']], operator))
            if rules:
                maps.append({'id': f'rcef_{group}.to_facs', 'rules': rules})
        return maps

    def files(self) -> dict[str, str]:
        signals = self.signals()
        profile = self.profile(signals)
        parts = [FACS_HEADER, '# FACS codes as an expression set, vocabulary version 1.0 (draft). See the FACS\n'
                              '# section of docs/canonical-set.md and docs/facs-intensity.md.\n']
        parts += ['\n[[signals]]\n' + ''.join(f'{k} = {value(v)}\n' for k, v in s.items()) for s in signals]
        parts.append('\n[[profiles]]\n' + ''.join(f'{k} = {value(v)}\n' for k, v in profile.items()))
        intro = ('# The maps between the canonical expression set and FACS codes (facs.code): one map\n'
                 '# per canonical group and direction. In-maps are facs_<group>.to_rcef; out-maps are\n'
                 '# rcef_<group>.to_facs.\n')
        return {FACS_FILE: ''.join(parts),
                FACS_MAPS_FILE: maps_toml('FACS', self.in_maps() + self.out_maps(signals), intro, FACS_HEADER)}


# ---------------------------------------------------------------- the canonical visemes

VISEME_PROFILE = 'rcef.canonical_viseme'
IPA_RECORD = 'ipa_chart_doulos_2020'
IPA_FIXTURE = 'tests/fixtures/ipa_chart_symbols.json'
INTERMEDIATE_SUM = f'{INTERMEDIATE}viseme_alveolar_floor_sum'
# The viseme sets: META's 15 classes and VRM's 5 vowel presets. Records as in PROVIDERS; every viseme hop also cites
# the IPA chart record, which defines the classes.
VISEME_PROVIDERS = {
    'visemes': {'name': 'META', 'profile': 'openxr.visemes', 'id': 'openxr.visemes.XR_FACE_TRACKING_VISEME_{}_META',
                'records': ['xr_visemes', 'xr_registry'], 'audit': 'META visemes'},
    'vrm': {'name': 'VRM', 'profile': 'vrm.preset', 'id': 'vrm.preset.{}', 'records': ['vrm_expressions'],
            'audit': 'VRM'},
}
VISEME_GAIN = 'META gain and full-activation pose not published'
VISEME_SCOPE_KEY = 'meta_viseme_class_scope'
META_TO_OTHER = ('from a source other than META: consonant and rest classes not produced; outputs may sum to 0 or '
                 'above 1; META validity contract (sum 1 when valid; invalid arrays are zero) not met')
VRM_DROPPED = 'consonant and rest classes are dropped, so outputs no longer sum to 1'
SUM_CLAUSE = 'the canonical value is the sum of the META classes {}, clamped at 1'
OTHER_SYMBOLS = {  # place and manner of the chart's "other symbols"
    'ʍ': ('labial-velar', 'fricative'), 'w': ('labial-velar', 'approximant'), 'ɥ': ('labial-palatal', 'approximant'),
    'ʜ': ('epiglottal', 'fricative'), 'ʢ': ('epiglottal', 'fricative'), 'ʡ': ('epiglottal', 'plosive'),
    'ɕ': ('alveolo-palatal', 'fricative'), 'ʑ': ('alveolo-palatal', 'fricative'),
    'ɺ': ('alveolar', 'lateral flap'), 'ɧ': ('postalveolar and velar', 'fricative')}


def table_after(text: str, heading: str, marker: str) -> list[dict]:
    """The first Markdown table after the line that starts with `marker`, inside the section under `heading`."""
    lines = text.splitlines()
    start = lines.index(heading)
    at = next(n for n in range(start + 1, len(lines)) if lines[n].startswith(marker))
    return table('\n'.join([heading, *lines[at + 1:]]), heading)


def cell_or_none(cell: str) -> str:
    return '' if cell == 'none' else cell


class VisemeBuilder:
    def __init__(self, root: Path = ROOT, a1: dict | None = None):
        doc = (root / SIGNAL_DOC).read_text(encoding='utf-8')
        audit_doc = (root / AUDIT_DOC).read_text(encoding='utf-8')
        self.a1 = a1 or read_a1(root)
        self.calibration = {}
        for kind, label in (('class', 'Viseme classes'), ('aggregate', 'Viseme aggregates')):
            found = re.search(rf'^- \*\*{label}:\*\* `(rcef\.canonical\.v1:<short_name>: [^`]+)`$', doc, re.M)
            self.calibration[kind] = found.group(1)
        heading = '### Viseme signals'
        shapes = {ticks(r['Short name'])[0]: r for r in table_after(doc, heading, '**Visible shape.**')}
        notes = {ticks(r['Short name'])[0]: r for r in table_after(doc, heading, '**Notes on shape classes')}
        fixture = json.loads((root / IPA_FIXTURE).read_text(encoding='utf-8'))['symbols']
        self.signals = []
        for row in table(doc, heading):
            short = ticks(row['Short name'])[0]
            parts = ticks(row['IPA chart symbols']) if row['Group'] == 'viseme_aggregate' else [short]
            members = [s for s in fixture if s['class'] in parts]
            if row['Group'] != 'viseme_aggregate' and row['IPA chart symbols'] != 'none':
                if [s['symbol'] for s in members] != row['IPA chart symbols'].split():
                    raise SystemExit(f'{short}: the IPA chart symbols disagree with {IPA_FIXTURE}')
            self.signals.append({
                'short': short, 'label': row['Label'], 'group': row['Group'], 'members': members, 'parts': parts,
                'rule': cell_or_none(row['By rule']), 'definition': plain(row['Definition']),
                'shape_class': cell_or_none(row['Shape class']), 'shape_floor': row['Shape floor'],
                'meta': row['META'], 'vrm': cell_or_none(row['VRM']), 'shape': shapes.get(short),
                'shape_note': cell_or_none(notes[short]['Shape note']) if short in notes else '',
                'floor_note': cell_or_none(notes[short]['Shape-floor note']) if short in notes else ''})
        self.by_short = {s['short']: s for s in self.signals}
        listed = [ticks(r['Group'])[0] for r in table(doc, '### Groups')]
        self.groups = [g for g in listed if any(s['group'] == g for s in self.signals)]
        if set(self.groups) != {s['group'] for s in self.signals}:
            raise SystemExit('a viseme group is missing from the groups table')
        self.keys = {ticks(r['Key'])[0]: r['Loss text'] for r in table(audit_doc, '## Loss keys')}
        self.audit = {}
        for key, spec in VISEME_PROVIDERS.items():
            rows = {}
            for row in table(audit_doc, '## ' + spec['audit']):
                short = ticks(row['Signal'])[0]
                if short in self.by_short:
                    rows[short] = {'verdict': row['Verdict'], 'paraphrase': row['Paraphrase'],
                                   'keys': [k for k in ticks(row['Owning hop, key']) if k in self.keys]}
            self.audit[key] = rows
        self.a16 = {}  # VRM preset -> (META cell and example, VRM remark), from today's viseme map
        for rule in self.a1['maps']['visemes.to_vrm']:
            for text in rule['assumptions']:
                found = re.match(
                    r'^META viseme (\w+) corresponds to VRM preset (\w+) \(META (.+); VRM remark (.+)\)\.$', text)
                if found:
                    self.a16[found.group(2)] = (found.group(1), found.group(3), found.group(4))

    def cid(self, short: str) -> str:
        return f'{VISEME_PROFILE}.{short}'

    def sid(self, key: str, native: str) -> str:
        return VISEME_PROVIDERS[key]['id'].format(native)

    def meta_names(self, s: dict) -> list[str]:
        return re.findall(r'\b[A-Z]{1,3}\b', s['meta'])

    # -- signals
    def features(self, s: dict) -> dict:
        consonant, vowel = {'place': [], 'manner': []}, {'height': [], 'backness': [], 'rounding': []}
        for m in s['members']:
            if m['section'] == 'Vowels':
                height, rest = m['cell'].split(' × ')
                backness, rounding = rest.split(', ')
                for k, v in (('height', height), ('backness', backness), ('rounding', rounding)):
                    if v.lower() not in vowel[k]:
                        vowel[k].append(v.lower())
                continue
            if m['section'] == 'Other symbols':
                place, manner = OTHER_SYMBOLS[m['symbol']]
            else:
                manner, place = m['cell'].split(' × ')
                manner = {'Clicks': 'click', 'Voiced implosives': 'implosive'}.get(manner, manner)
            for k, v in (('place', place), ('manner', manner)):
                if v.lower() not in consonant[k]:
                    consonant[k].append(v.lower())
        if s['short'] == 'dental':  # the IPA dental stops, nasals and laterals stay in the coronal classes
            consonant['manner'] = ['dental fricative', 'interdental (by rule)', 'linguolabial (by rule)']
        out = {}
        if s['group'] in ('viseme_vowel',):
            out.update({f'ipa_{k}': v for k, v in vowel.items()})
            glides = [m['symbol'] for m in s['members'] if m['section'] != 'Vowels']
            if glides:
                out['ipa_glides'] = glides
        elif s['members']:
            out.update({f'ipa_{k}': v for k, v in consonant.items()})
        return out

    def viseme_signals(self) -> list[dict]:
        out = []
        for s in self.signals:
            aggregate = s['group'] == 'viseme_aggregate'
            metadata = {'definition': s['definition'], 'ipa_members': [m['symbol'] for m in s['members']],
                        'ipa_members_assumed': [m['symbol'] for m in s['members'] if m['evidence'].startswith('A')],
                        'ipa_rules': s['rule'], **self.features(s)}
            if s['shape']:
                metadata['shape'] = {k: s['shape'][k.title()] for k in ('lips', 'teeth', 'tongue', 'jaw')}
            if s['shape_class']:
                metadata['shape_class'] = s['shape_class']
            if s['shape_note']:
                metadata['shape_note'] = s['shape_note']
            metadata['shape_floor'] = s['shape_floor']
            if s['floor_note']:
                metadata['shape_floor_note'] = s['floor_note']
            aligned = {'openxr.visemes': self.meta_names(s)}
            if s['vrm']:
                aligned['vrm.preset'] = [s['vrm']]
            anchors = ['docs/canonical-set-audit.md#meta-visemes']
            if s['short'] in self.audit['vrm']:
                anchors.append('docs/canonical-set-audit.md#vrm')
            if s['members'] and not aggregate:
                anchors.append('docs/canonical-set-audit.md#ipa-reference-rows')
            metadata.update({'group': s['group'], 'aligned_names': aligned, 'audit': anchors})
            if aggregate:
                metadata['aggregates'] = s['parts']
                calibration = self.calibration['aggregate'].replace('<classes>', join(s['parts']))
            else:
                calibration = self.calibration['class']
            out.append({'id': self.cid(s['short']), 'label': s['label'], 'value_type': 'scalar',
                        'units': 'probability', 'domain': {'min': 0.0, 'max': 1.0},
                        'calibration': calibration.replace('<short_name>', s['short']), 'disposition': 'mapped',
                        'evidence': [OWN, IPA_RECORD], 'evidence_status': 'proposed', 'side': 'shared',
                        'coupling': 'aggregate_of_simplex_classes' if aggregate else 'probability_simplex',
                        'metadata': metadata, 'region': 'mouth'})
        return out

    def viseme_profile(self) -> dict:
        return {'id': VISEME_PROFILE, 'label': 'RCEF canonical viseme set (draft)',
                'signal_ids': [self.cid(s['short']) for s in self.signals], 'evidence': [OWN, IPA_RECORD],
                'metadata': {'vocabulary_version': '1.0', 'vocabulary_status': 'draft',
                             'scope': 'IPA shape classes, minimal under parity when the META and VRM hops target '
                                      'partition classes, plus the floor aggregate alveolar_floor; each value is the '
                                      'source\'s class weight, with no shared or measured gain',
                             'groups': self.groups}}

    # -- hops
    def endpoints(self, key: str, shorts: list[str], clause: str) -> str:
        text = f'endpoints: {OPENING.format(possessive(VISEME_PROVIDERS[key]["name"]))}; {clause}'
        keys = list(dict.fromkeys(k for s in shorts if self.audit[key].get(s, {}).get('verdict', 'same') != 'same'
                                  for k in self.audit[key][s]['keys']))
        if keys:
            text += '; ' + DIFFERS.format(('losses ' if len(keys) > 1 else 'loss ') + join(keys))
        return text + '.'

    def audit_losses(self, key: str, shorts: list[str]) -> list[str]:
        return [f'{k}: {self.keys[k]}' for s in shorts for k in self.audit[key].get(s, {}).get('keys', [])]

    def evidence(self, key: str) -> list[str]:
        return [*VISEME_PROVIDERS[key]['records'], IPA_RECORD, OWN]

    def rule(self, rid, inputs, outputs, operator, assumptions, losses, evidence) -> dict:
        refs = inputs + outputs
        return {'id': rid, 'inputs': inputs, 'outputs': outputs, 'operator': operator, 'disposition': 'mapped',
                'mapping_quality': 'approximate', 'evidence_status': 'proposed', 'assumptions': assumptions,
                'evidence': evidence,
                'loss_annotations': [{'category': 'signal', 'effect': 'approximated', 'reason': r, 'refs': refs,
                                      'units': '1'} for r in losses]}

    def meta_correspondence(self, s: dict) -> str:
        native = s['meta']
        if s['short'] == 'sil':
            return ('correspondence: META viseme SIL, which META calls neutral, corresponds to canonical sil: no speech '
                    'articulation.')
        vowel = next((v for v in self.a16.values() if v[0] == native), None)
        if vowel:
            sounds = f' (META {vowel[1]})'
        else:
            found = re.match(r'class probability for the sounds? ([^.:]+)', self.audit['visemes'][s['short']]['paraphrase'])
            if not found:
                raise SystemExit(f'{s["short"]}: the META audit row names no example sounds')
            sounds = ' (META ' + re.sub(r' \((.+)\)$', r', read as \1', found.group(1).strip()) + ')'
        return (f'correspondence: META viseme {native}{sounds} corresponds to canonical {s["short"]}; '
                'RCEF reads META\'s example sounds as members of this IPA shape class.')

    def meta_hop(self, s: dict, direction: str) -> dict:
        sid, cid = self.sid('visemes', s['meta']), self.cid(s['short'])
        losses = [VISEME_GAIN, f'{VISEME_SCOPE_KEY}: {self.keys[VISEME_SCOPE_KEY]}',
                  *self.audit_losses('visemes', [s['short']])]
        if direction == 'out' and s['group'] == 'viseme_vowel':
            losses.append(META_TO_OTHER)
        rid = f'visemes_rcef.{s["short"]}' if direction == 'in' else f'rcef_visemes.{s["meta"]}'
        inputs, outputs = ([sid], [cid]) if direction == 'in' else ([cid], [sid])
        assumptions = [self.meta_correspondence(s), self.endpoints('visemes', [s['short']], CLAUSES['in_copy'])]
        return self.rule(rid, inputs, outputs, copy(), assumptions, losses, self.evidence('visemes'))

    def aggregate_rules(self, s: dict) -> list[dict]:
        names = self.meta_names(s)
        inputs = [self.sid('visemes', n) for n in names]
        assumptions = [
            f'correspondence: canonical {s["short"]} is the union of the classes {join(s["parts"])}, which META '
            f'{join(names)} carry one to one.',
            self.endpoints('visemes', [s['short']], SUM_CLAUSE.format(join(names)))]
        losses = [VISEME_GAIN, *self.audit_losses('visemes', [s['short']])]
        evidence = self.evidence('visemes')
        return [self.rule(f'visemes_rcef.{INTERMEDIATE_SUM[len(INTERMEDIATE):]}', inputs, [INTERMEDIATE_SUM],
                          {'id': 'weighted_sum', 'weights': [1.0] * len(inputs)}, assumptions, losses, evidence),
                self.rule(f'visemes_rcef.{s["short"]}', [INTERMEDIATE_SUM], [self.cid(s['short'])],
                          {'id': 'piecewise_linear', 'knots': [[0.0, 0.0], [1.0, 1.0], [float(len(inputs)), 1.0]]},
                          assumptions, losses, evidence)]

    def vrm_hop(self, s: dict, direction: str) -> dict:
        preset = s['vrm']
        sid, cid = self.sid('vrm', preset), self.cid(s['short'])
        remark = self.a16[preset][2]
        assumptions = [f'correspondence: VRM preset {preset} (remark {remark}) corresponds to canonical {s["short"]}; '
                       'RCEF reads the remark as a vowel of this IPA shape class.',
                       self.endpoints('vrm', [s['short']], CLAUSES['in_copy'])]
        losses = self.audit_losses('vrm', [s['short']])
        if direction == 'in':
            assumptions.append('vrm.probability_as_weight: the VRM expression weight (0 to 1), authored per model, '
                               'is read as the canonical class probability (0 to 1); the unit changes from VRM\'s '
                               'weight to probability.')
            rid, inputs, outputs = f'vrm_rcef.{s["short"]}', [sid], [cid]
        else:
            assumptions += ['vrm.probability_as_weight: the canonical class probability (0 to 1) is used directly as '
                            'the VRM expression weight (0 to 1); the unit changes from probability to VRM\'s weight.',
                            'vrm.phoneme_label_only: phoneme-label correspondence only; no published table maps META '
                            'visemes or the canonical classes to VRM presets.',
                            *['vrm.downstream_effects: ' + a for r in self.a1['maps']['visemes.to_vrm']
                              if r['outputs'] == [sid] for a in r['assumptions'] if a.startswith('VRM isBinary')]]
            losses.append(VRM_DROPPED)
            rid, inputs, outputs = f'rcef_vrm.{preset}', [cid], [sid]
        return self.rule(rid, inputs, outputs, copy(), assumptions, losses, self.evidence('vrm'))

    def meta_maps(self) -> list[dict]:
        maps = []
        for group in self.groups:
            members = [s for s in self.signals if s['group'] == group]
            if group == 'viseme_aggregate':
                maps.append({'id': 'visemes_aggregate.to_rcef',
                             'rules': [r for s in members for r in self.aggregate_rules(s)]})
            else:
                maps.append({'id': f'visemes_{group[len("viseme_"):]}.to_rcef',
                             'rules': [self.meta_hop(s, 'in') for s in members]})
        for group in self.groups:
            if group != 'viseme_aggregate':
                maps.append({'id': f'rcef_{group}.to_visemes',
                             'rules': [self.meta_hop(s, 'out') for s in self.signals if s['group'] == group]})
        return maps

    def vrm_maps(self) -> list[dict]:
        vowels = [s for s in self.signals if s['vrm']]
        by_preset = {s['vrm']: s for s in vowels}
        order = [r['outputs'][0].rsplit('.', 1)[1] for r in self.a1['maps']['visemes.to_vrm']]
        return [{'id': 'vrm_vowel.to_rcef', 'rules': [self.vrm_hop(s, 'in') for s in vowels]},
                {'id': 'rcef_viseme_vowel.to_vrm', 'rules': [self.vrm_hop(by_preset[p], 'out') for p in order]}]


# ---------------------------------------------------------------- the viseme pose bridge

POSE_RECORD = 'viseme-poses.rocketbox-features'
POSE_EVIDENCE = f'calibration.{POSE_RECORD}'
POSE_MAP = 'rcef_viseme_pose.to_rcef_expression'
POSE_FILE = 'mappings/canonical_viseme_pose.toml'
INTERMEDIATE_FILE = 'data/intermediate.toml'
POSE_MARKER = ('# Below this line: written by scripts/build_canonical.py from the calibration record\n'
               f'# {POSE_RECORD}. Edit the record or the script, not this part.\n')
POSE_HEADER = ('# SPDX-License-Identifier: CC-BY-SA-4.0\n'
               '# Original RCEF data. Written by scripts/build_canonical.py from the frozen poses and held-out\n'
               f'# cells of calibration/{POSE_RECORD}.cal. Edit the script, not this file.\n')
POSE_INTRO = (f'# The viseme pose bridge, from calibration/{POSE_RECORD}.cal: each canonical expression\n'
              '# signal is the clamped sum of class weight times frozen pose, over the canonical viseme\n'
              '# classes whose held-out cells pass. See docs/canonical-set.md.\n')
POSE_RECORDS = ['xr_visemes', 'apple_blendshapes', IPA_RECORD, OWN]
CALIBRATION_STATUS = ('calibration_status: the record is calibrated_software, a fit to the geometry of example rigs, '
                      'not a measurement of any tracker; pack schema 1.0 has no such evidence status, so the mapping '
                      'is proposed.')
POSE_COMMON = [
    'coarticulation: not modelled; each class is one static pose, and the poses of a blend of classes add up; RCEF '
    'has no operator over time.',
    'teeth_tongue: teeth and tongue are not represented; the bridge writes no tongue_out, blink, gaze, jaw_sideways '
    'or mouth_shift value.',
    CALIBRATION_STATUS,
]
# Measured by examples/viseme_bridge.py (examples/README.md, section 7), not by the record.
ICT_BILABIAL = ('on ICT-FaceKit, a rig from another library, the bilabial pose opens the lips on the mid line from '
                '0.61 to 2.95 mm instead of keeping them closed')


def load_check():
    """check.py as a module, for its pass rule of calibration records (shape cells, or the perceptual gate)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('rcef_check', ROOT / 'check.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PoseBridge:
    """The bridge from the canonical viseme classes whose held-out cells pass to the canonical expression signals."""

    def __init__(self, root: Path, visemes: VisemeBuilder, expression: list[dict]):
        import tomllib
        self.root = root
        record = tomllib.loads((root / f'calibration/{POSE_RECORD}.cal').read_text(encoding='utf-8'))
        cells = record.get('cells', [])
        check = load_check()
        self.classes = [c for c in record['channels'] if cells and check.channel_passes(record, c)]
        self.by_features = [c for c in self.classes if not all(check.cell_passes(record, x) for x in cells
                                                              if x['channel'] == c)]
        self.failing = [c for c in record['channels'] if c not in self.classes]
        self.poses = {}
        for curve in record['curves']:
            self.poses.setdefault(curve['output'], {})[curve['input']] = curve['knots'][1][1]
        moving = [x['p95'] for x in cells if x['channel'] in self.classes and x['channel'] not in self.by_features
                  and x['p95'] > 0]
        self.training = record['training']['conditions'] // len(record['channels'])
        self.held_out = len({x['identity'] for x in cells})
        self.residual = (min(moving), max(moving)) if moving else (0.0, 0.0)
        self.visemes = visemes
        self.expression = {s['id']: s for s in expression}

    def short(self, sid: str) -> str:
        return sid.rsplit('.', 1)[1]

    def common(self) -> list[str]:
        """The assumptions every sum and clamp of the bridge states, with the rig counts of the record."""
        out = [f'example_rigs: the poses are fitted to the sculpted viseme shapes of {self.training} Rocketbox rigs, '
               'measured in their own ARKit units by one bounded fit for all of them, with Left and Right tied; on '
               f'each of {self.held_out} other Rocketbox rigs, which the fit did not use, each pose read here either '
               "reproduces its class's own shape to within half of its motion (shape gate) or meets its class's "
               'visible mouth features within their frozen tolerances (perceptual gate); all '
               f'{self.training + self.held_out} rigs come from one library, and rigs from other libraries render '
               'the same ARKit weights differently (calibration record rig-gains.ict-rocketbox-female)'
               + (f'; {ICT_BILABIAL}.' if f'{VISEME_PROFILE}.bilabial' in self.classes else '.')]
        if self.by_features:
            out.append('perceptual_tolerance: the tolerances of the perceptual gate are the spread of one library\'s '
                       'sculpts (the training rigs\' own visemes), not measured perceptual thresholds; no viewer '
                       'judged them.')
        return out + POSE_COMMON

    def helper(self, cid: str) -> str:
        return f'{INTERMEDIATE}viseme_pose_{self.short(cid)}'

    def sum_helper(self, sid: str) -> str:
        return f'{INTERMEDIATE}viseme_pose_sum_{self.short(sid)}'

    def losses(self) -> list[str]:
        low, high = self.residual
        out = ['viseme_pose_example_rigs: poses of example Rocketbox rigs in their own ARKit units; the geometry of a '
               'rig from another library differs',
               f"viseme_pose_residual: part of each viseme's own motion is not reproduced (on the held-out rigs "
               f'{low:.2f} to {high:.2f} of it, for the classes read by their shape that move the face)']
        if self.by_features:
            out.append(f'viseme_pose_perceptual_gate: {join([self.short(c) for c in self.by_features])} are read '
                       'because their visible mouth features pass, though their whole-face shape error is more than '
                       'half of the motion')
        if self.failing:
            out.append(f'viseme_pose_classes_not_read: {join([self.short(c) for c in self.failing])} failed both '
                       'held-out gates and are not read')
        return out

    def rule(self, rid, inputs, outputs, operator, assumptions, evidence) -> dict:
        refs = inputs + outputs
        return {'id': rid, 'inputs': inputs, 'outputs': outputs, 'operator': operator, 'disposition': 'mapped',
                'mapping_quality': 'approximate', 'evidence_status': 'proposed', 'assumptions': assumptions,
                'evidence': evidence,
                'loss_annotations': [{'category': 'signal', 'effect': 'approximated', 'reason': r, 'refs': refs,
                                      'units': '1'} for r in self.losses()]}

    def maps(self) -> list[dict]:
        if not self.classes:
            return []
        rules = []
        for cid in self.classes:
            meta = self.visemes.by_short[self.short(cid)]['meta']
            rules.append(self.rule(
                f'rcef_viseme_pose.{self.short(cid)}', [cid], [self.helper(cid)], copy(),
                [f'correspondence: canonical {self.short(cid)} at weight 1 reaches its pose, the face of the META '
                 f'{meta} viseme shapes of {self.training} Rocketbox rigs measured in their ARKit shapes (calibration '
                 'record '
                 f'{POSE_RECORD}).',
                 'units: the class probability (0 to 1) is read as the activation of the class\'s pose (0 to 1); '
                 'the unit changes from probability to 1.'],
                POSE_RECORDS))
        names = join([self.short(c) for c in self.classes])
        read = (f'classes: the bridge reads the {len(self.classes)} classes that pass the shape or the perceptual '
                f'gate on every held-out rig ({names})'
                + (f'; {join([self.short(c) for c in self.failing])} failed and are not read, so weight on them '
                   'moves no expression signal.' if self.failing else '.'))
        k = float(len(self.classes))
        for sid, poses in self.poses.items():
            short = self.short(sid)
            assumptions = [f'pose: canonical {short} is the sum of each class weight times the frozen pose of the '
                           f'class in {short} (calibration record {POSE_RECORD}), clamped at 1.', read, *self.common()]
            rules.append(self.rule(f'rcef_viseme_pose.{short}_sum', [self.helper(c) for c in self.classes],
                                   [self.sum_helper(sid)], {'id': 'weighted_sum',
                                                            'weights': [poses[c] for c in self.classes]},
                                   assumptions, [POSE_EVIDENCE, *POSE_RECORDS]))
            rules.append(self.rule(f'rcef_viseme_pose.{short}', [self.sum_helper(sid)], [sid],
                                   {'id': 'piecewise_linear', 'knots': [[0.0, 0.0], [1.0, 1.0], [k, 1.0]]},
                                   assumptions, POSE_RECORDS))
        return [{'id': POSE_MAP, 'rules': rules}]

    def helpers(self) -> list[dict]:
        if not self.classes:
            return []
        reason = 'Intermediate value of a proposed approximate translation.'
        out = []
        for cid in self.classes:
            short = self.short(cid)
            out.append({'id': self.helper(cid), 'label': f'RCEF activation of the {short} viseme pose',
                        'value_type': 'scalar', 'units': '1', 'domain': {'min': 0.0, 'max': 1.0},
                        'calibration': f'rcef.intermediate.v1:viseme_pose_{short}: canonical {short} read as the '
                                       'activation of its pose, 0 to 1',
                        'disposition': 'mapped', 'evidence': [OWN, IPA_RECORD], 'evidence_status': 'proposed',
                        'side': 'shared', 'neutral': 0.0,
                        'metadata': {'definition': f'The weight of canonical {short}, read as how far its viseme pose '
                                                   f'is reached, from 0 to 1. Computed inside {POSE_MAP}; no '
                                                   'provider reads or writes it.', 'reason': reason},
                        'region': 'mouth'})
        k = float(len(self.classes))
        for sid in self.poses:
            short, signal = self.short(sid), self.expression[sid]
            out.append({'id': self.sum_helper(sid), 'label': f'RCEF sum of the viseme poses in {short}',
                        'value_type': 'scalar', 'units': '1', 'domain': {'min': 0.0, 'max': k},
                        'calibration': f'rcef.intermediate.v1:viseme_pose_sum_{short}: sum of the viseme poses in '
                                       f'{short} before the clamp, 0 to {len(self.classes)}',
                        'disposition': 'mapped', 'evidence': [OWN, 'apple_blendshapes'], 'evidence_status': 'proposed',
                        'side': signal['side'], 'neutral': 0.0,
                        'metadata': {'definition': f'The sum of each viseme class activation times its pose in '
                                                   f'canonical {short}, from 0 to {len(self.classes)}. Computed '
                                                   f'inside {POSE_MAP} and clamped at 1 into {short}; no provider '
                                                   'reads or writes it.', 'reason': reason},
                        'region': signal['region']})
        return out

    def intermediate_toml(self) -> str:
        """data/intermediate.toml: its hand-written part, then the bridge helpers and the profile of all."""
        import tomllib
        text = (self.root / INTERMEDIATE_FILE).read_text(encoding='utf-8')
        if POSE_MARKER not in text:
            raise SystemExit(f'{INTERMEDIATE_FILE} has lost its marker line; restore it')
        hand = text.split(POSE_MARKER)[0]
        helpers = self.helpers()
        ids = [s['id'] for s in tomllib.loads(hand).get('signals', [])] + [s['id'] for s in helpers]
        profile = {'id': 'rcef.intermediate', 'label': 'RCEF intermediate values inside translations',
                   'signal_ids': ids, 'evidence': ['rcef_definitions']}
        parts = [hand, POSE_MARKER]
        parts += ['\n[[signals]]\n' + ''.join(f'{k} = {value(v)}\n' for k, v in s.items()) for s in helpers]
        parts.append('\n[[profiles]]\n' + ''.join(f'{k} = {value(v)}\n' for k, v in profile.items()))
        return ''.join(parts)


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
# docs/canonical-set-audit.md, tests/fixtures/ipa_chart_symbols.json and the
# retired A1 direct maps (tests/fixtures/baseline-dea1713.pack.json). Edit
# those, then run the script.
'''


def signals_toml(signals: list[dict], profile: dict, title: str = 'canonical expression set') -> str:
    parts = [HEADER, f'# The {title}, vocabulary version 1.0 (draft). See docs/canonical-set.md.\n']
    for s in signals:
        parts.append('\n[[signals]]\n' + ''.join(f'{k} = {value(v)}\n' for k, v in s.items()))
    parts.append('\n[[profiles]]\n' + ''.join(f'{k} = {value(v)}\n' for k, v in profile.items()))
    return ''.join(parts)


def maps_toml(name: str, maps: list[dict], intro: str | None = None, header: str = HEADER) -> str:
    parts = [header, intro or f'# The maps between the canonical sets and {name}: one map per canonical group and\n'
                              '# direction. In-maps are <set>_<group>.to_rcef; out-maps are rcef_<group>.to_<set>.\n']
    for m in maps:
        parts.append(f'\n[[mappings]]\nid = {value(m["id"])}\n')
        for r in m['rules']:
            parts.append('\n[[mappings.rules]]\n')
            for k, v in r.items():
                if k in ('assumptions', 'loss_annotations') and v:
                    parts.append(f'{k} = [\n' + ''.join(f'  {value(x)},\n' for x in v) + ']\n')
                else:
                    parts.append(f'{k} = {value(v)}\n')
    return ''.join(parts)


def render(root: Path = ROOT) -> dict[str, str]:
    builder = Builder(root)
    visemes = VisemeBuilder(root, builder.a1)
    files = {'data/canonical_expression.toml': signals_toml(builder.canonical_signals(), builder.profile()),
             'data/canonical_viseme.toml': signals_toml(visemes.viseme_signals(), visemes.viseme_profile(),
                                                        'canonical viseme set')}
    for key, path in FILES.items():
        maps = builder.maps(key) + (visemes.vrm_maps() if key == 'vrm' else [])
        files[path] = maps_toml(PROVIDERS[key]['name'], maps)
    files['mappings/canonical_visemes.toml'] = maps_toml('META visemes', visemes.meta_maps())
    bridge = PoseBridge(root, visemes, builder.canonical_signals())
    files[POSE_FILE] = maps_toml('', bridge.maps(), POSE_INTRO, POSE_HEADER)
    files[INTERMEDIATE_FILE] = bridge.intermediate_toml()
    files.update(FacsBuilder(root, builder).files())
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
