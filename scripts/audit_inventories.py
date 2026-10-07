#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare authoring names/indices with exact digest-verified public source bytes."""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import tomllib
import xml.etree.ElementTree as ET


class Tables(HTMLParser):
    """Extract factual table cells; never execute documentation scripts."""
    def __init__(self):
        super().__init__()
        self.tables, self.table, self.cell = [], None, None
        self.row = []

    def handle_starttag(self, tag, attrs):
        if tag == 'table': self.table = []
        if tag == 'tr': self.row = []
        if tag in ('th', 'td'): self.cell = []

    def handle_data(self, data):
        if self.cell is not None: self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('th', 'td') and self.cell is not None:
            self.row.append(''.join(self.cell))
            self.cell = None
        if tag == 'tr' and self.table is not None: self.table.append(self.row)
        if tag == 'table':
            self.tables.append(self.table)
            self.table = None


def audit(cache: Path) -> dict:
    root = Path(__file__).resolve().parents[1]
    evidence = tomllib.loads((root / 'evidence/sources.toml').read_text())['evidence']
    digests = {e['id']: e['sha256'] for e in evidence if 'sha256' in e}
    def source(id):
        data = (cache / id).read_bytes()
        if hashlib.sha256(data).hexdigest() != digests[id]:
            raise ValueError(f'{id}: evidence digest mismatch')
        return data.decode('utf-8-sig')
    def native(profile):
        signals = tomllib.loads((root / 'profiles' / f'{profile}.toml').read_text())['signals']
        return [s for s in signals if s['metadata'].get('selected', True)]
    checked = {}
    def compare(profile, names, count, *, indices=None, all_entries=False):
        entries = (tomllib.loads((root / 'profiles' / f'{profile}.toml').read_text())['signals']
                   if all_entries else native(profile))
        authored = [s['native_id'] for s in entries]
        if len(names) != count or authored != names:
            raise ValueError(f'{profile}: exact name/order/count mismatch')
        if indices is not None and [s['metadata']['native_index'] for s in entries] != indices:
            raise ValueError(f'{profile}: native index mismatch')
        checked[profile] = count
    apple = json.loads(source('apple_blendshapes'))
    names = [apple['references'][id]['title'] for section in apple['topicSections']
             if section['title'] != 'Creating a Blend Shape Location' for id in section['identifiers']]
    compare('arkit.coefficient', names, 52)
    media = source('mediapipe').split('kBlendshapeNames = {')[1].split('};')[0]
    compare('mediapipe.label', re.findall(r'"(\w+)"', media), 52)
    registry = ET.fromstring(source('xr_registry'))
    for profile, enum, count in [('openxr.fb','XrFaceExpressionFB',63),
                                 ('openxr.fb2','XrFaceExpression2FB',70),
                                 ('openxr.visemes','XrFaceTrackingVisemeMETA',15)]:
        values = [e.attrib for e in registry.find(f"./enums[@name='{enum}']")
                  if int(e.attrib['value']) < count]
        compare(profile, [e['name'] for e in values], count,
                indices=[int(e['value']) for e in values])
    transport = source('vrcft_enum').split('public enum UnifiedExpressions')[1].split('internal enum')[0]
    names = re.findall(r'^\s*(\w+)\s*,?\s*(?://.*)?$', transport, re.M)
    compare('vrcft.transport', [n for n in names if n != 'Max'], 88, indices=list(range(88)))
    artist = Tables(); artist.feed(source('vrcft_artist'))
    for index, profile, count in [(1,'vrcft.artist.base',102),(2,'vrcft.artist.blended',42)]:
        compare(profile, [r[1].rstrip('¹') for r in artist.tables[index][1:]], count)
    godot = source('godot_enum').split('enum BlendShapeEntry')[1].split('};')[0]
    base, blended = godot.split('// Blended Shapes')
    compare('godot.base', re.findall(r'^\s*(FT_\w+)',base,re.M), 102, indices=list(range(102)))
    compare('godot.blended', [n for n in re.findall(r'^\s*(FT_\w+)',blended,re.M) if n!='FT_MAX'],
            41, indices=list(range(102,143)))
    vrm = source('vrm_expressions').split('## Preset Expressions')[1].split('## Custom Expressions')[0]
    compare('vrm.preset',[n for n in re.findall(r'^\|\s*(\w+)\s*\|',vrm,re.M) if n!='Name'],18)
    controls = re.findall(r'^  - name: FaceControls\.(\w+)',source('roblox_controls'),re.M)
    compare('roblox.control', controls, 50)
    poses = re.findall(r'^## (.+)',source('roblox_poses'),re.M)
    if set(poses) != set(controls): raise ValueError('Roblox pose-reference/control mismatch')
    params = Tables(); params.feed(source('vrcft_parameters'))
    names = [r[0] for t in params.tables[:-1] for r in t[1:]]
    names = [n[:-1] if n in ('v2/JawClench1','v2/JawMandibleRaise1') else n for n in names]
    compare('vrcft.parameter.float', names, 124)
    compare('vrcft.parameter.flags',[r[0] for r in params.tables[-1][1:]],3)
    # Eye data is a component projection of a struct, with explicit field evidence.
    eye = source('vrcft_data')
    for declaration in ('public Vector2 Gaze;', 'public float PupilDiameter_MM;', 'public float Openness = 1.0f;'):
        if declaration not in eye: raise ValueError('VRCFT raw-eye field declaration changed')
    fields = [s['native_id'] for s in native('vrcft.eye')]
    if fields != [e+'.'+f for e in ('Left','Right','Combined')
                  for f in ('Gaze.x','Gaze.y','Openness','PupilDiameter_MM')]:
        raise ValueError('VRCFT eye component projection mismatch')
    checked['vrcft.eye'] = 12
    return {'verified_profiles':checked,'failures':[]}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True,
                        help='exact bytes fetched by verify_sources.py outside the repository')
    args=parser.parse_args()
    try:
        result=audit(args.cache.resolve(strict=True))
    except (ValueError, OSError, KeyError, IndexError, ET.ParseError) as exc:
        print(json.dumps({'failures':[str(exc)]}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
