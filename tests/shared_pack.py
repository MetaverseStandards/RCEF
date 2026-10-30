# SPDX-License-Identifier: MIT
"""One compiled RCEF pack shared by the test modules that only read it.

Loading and compiling the full pack takes about a second, and msf-character-tools
records are immutable, so modules share one copy instead of compiling their own.
"""
from functools import cache
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import msf_character_tools as msf

ROOT = Path(__file__).resolve().parents[1]


@cache
def authoring():
    loaded = msf.load_authoring(ROOT)
    if loaded.value is None:
        raise AssertionError(loaded.report.to_dict())
    return loaded.value


def document():
    """A fresh, editable dictionary copy of the authored data."""
    return authoring().to_dict()


@cache
def pack():
    compiled = msf.compile_pack(authoring())
    if compiled.value is None:
        raise AssertionError(compiled.report.to_dict())
    return compiled.value


def registered_pack(abreg: str):
    """The B pack that a committed A/B registration (such as 'ab/ab.pivot-v1.abreg') pinned, as a document.

    It is read from the commit that added the registration, and its SHA-256 must be the registration's
    b_pack_sha256. None when the checkout has no Git history.
    """
    added = subprocess.run(['git', 'log', '--format=%H', '--diff-filter=A', '--', abreg], cwd=ROOT,
                           capture_output=True, text=True)
    if added.returncode or not added.stdout.split():
        return None
    shown = subprocess.run(['git', 'show', f'{added.stdout.split()[-1]}:generated/rcef.pack.json'], cwd=ROOT,
                           capture_output=True, check=True)
    pinned = json.loads((ROOT / abreg).read_text(encoding='utf-8'))['pins']['b_pack_sha256']
    if hashlib.sha256(shown.stdout).hexdigest() != pinned:
        raise AssertionError(f'{abreg}: the pack of the commit that added it is not the pack it pins')
    return json.loads(shown.stdout)


@cache
def snapshot(profile_id):
    return msf.profile_snapshot(pack(), profile_id).value


@cache
def mapping(mapping_id, source, target, approximate=True):
    result = msf.compile_mapping(pack(), snapshot(source), snapshot(target), mapping_id, approximate)
    if result.value is None:
        raise AssertionError((mapping_id, result.report.to_dict()))
    return result.value


@cache
def frames(kind):
    """examples/rcef_frames.py's `kind` factory (such as 'fb2_to_arkit') on the shared pack, built once."""
    sys.path.insert(0, str(ROOT / 'examples'))
    import rcef_frames
    return getattr(rcef_frames, kind)(pack=pack())


def cut(document, mapping_ids, whole=()):
    """The document cut down to some maps, the records they use, and every signal of the profiles in `whole`.

    msf-character-tools rechecks the whole pack on every call, so the many changed
    copies that the mutation tests build stay fast only when the pack is small.
    """
    mappings = [m for m in document['mappings'] if m['id'] in mapping_ids]
    members = {sid for m in mappings for r in m['rules'] for sid in r['inputs'] + r['outputs']}
    members |= {sid for p in document['profiles'] if p['id'] in whole for sid in p['signal_ids']}
    profiles = [{**p, 'signal_ids': [sid for sid in p['signal_ids'] if sid in members]}
                for p in document['profiles'] if members & set(p['signal_ids'])]
    signals = [s for s in document['signals'] if s['id'] in members]
    cited = {e for record in profiles + signals + [r for m in mappings for r in m['rules']]
             for e in record.get('evidence', [])}
    return {**document, 'profiles': profiles, 'signals': signals, 'mappings': mappings,
            'evidence': [e for e in document['evidence'] if e['id'] in cited]}
