# SPDX-License-Identifier: MIT
"""Read provider frames from a CSV, translate them through RCEF's canonical sets, and write a CSV.

Used by translate_fb2_to_arkit.py, translate_visemes_to_vrm.py, face_pipeline.py,
viseme_pipeline.py and viseme_bridge.py. rcef_route.Route does the translation
(source -> canonical -> target); this module adds the CSV format of the examples.

- A refusal names the hop map that refused the frame, its codes and the inputs
  it refused, for example "fb2_gaze.to_rcef: E_INVALID_SAMPLE on 8 inputs (...)".
- "dropped" lists the non-zero inputs that do not reach the target, by the
  provider's own channel names.
- The output columns are the target signals that the route can write from the
  source, unless a column order is given. A target signal whose canonical group
  the source cannot write is left out (Route labels it "not available from source").
"""
from __future__ import annotations
import csv
from pathlib import Path

import msf_character_tools as msf

import rcef_route
from rcef_translate import ROOT, cache_home, load_pack  # noqa: F401  (the examples use cache_home and load_pack)

FB2 = ('openxr.fb2.XR_FACE_EXPRESSION2_', '_FB')
VISEMES = ('openxr.visemes.XR_FACE_TRACKING_VISEME_', '_META')
ARKIT = ('arkit.coefficient.', '')
# The column order of the FB2 -> ARKit output that the examples have always written. It is fixed here, so the
# published outputs stay the same byte for byte; the route writes the 52 coefficients in another order.
ARKIT_COLUMNS = (
    'eyeBlinkLeft', 'eyeBlinkRight', 'jawOpen', 'mouthClose', 'browInnerUp', 'cheekPuff', 'mouthSmileLeft',
    'mouthSmileRight', 'mouthShrugUpper', 'mouthShrugLower', 'browDownLeft', 'browDownRight', 'browOuterUpLeft',
    'browOuterUpRight', 'cheekSquintLeft', 'cheekSquintRight', 'eyeSquintLeft', 'eyeSquintRight', 'eyeWideLeft',
    'eyeWideRight', 'jawForward', 'jawLeft', 'jawRight', 'mouthDimpleLeft', 'mouthDimpleRight', 'mouthFrownLeft',
    'mouthFrownRight', 'mouthFunnel', 'mouthLeft', 'mouthLowerDownLeft', 'mouthLowerDownRight', 'mouthPressLeft',
    'mouthPressRight', 'mouthPucker', 'mouthRight', 'mouthRollLower', 'mouthRollUpper', 'mouthStretchLeft',
    'mouthStretchRight', 'mouthUpperUpLeft', 'mouthUpperUpRight', 'noseSneerLeft', 'noseSneerRight', 'tongueOut',
    'eyeLookOutLeft', 'eyeLookInLeft', 'eyeLookOutRight', 'eyeLookInRight', 'eyeLookDownLeft', 'eyeLookDownRight',
    'eyeLookUpLeft', 'eyeLookUpRight')


class Frames:
    """A Route from one source set to one target set, with the CSV reading and writing of the examples."""

    def __init__(self, source: str, target: str, prefix: str, suffix: str, columns: tuple[str, ...] | None = None,
                 target_affixes: tuple[str, str] | None = None, root: Path = ROOT, pack: msf.Pack | None = None,
                 compiled: dict | None = None):
        """`prefix` and `suffix` turn a CSV column into a source signal ID; `columns` fixes the output columns.

        `target_affixes` (prefix, suffix) give the target's own channel names; the default strips `<target>.`.
        `pack` replaces the published pack; `compiled` holds maps already compiled from it, by map ID.
        """
        self.route = route = rcef_route.Route(source, target, pack=pack, compiled=compiled, root=root)
        self.pack, self.signals = route.pack, route.signals
        self.source, self.target, self.prefix, self.suffix = source, target, prefix, suffix
        self.affixes = [(prefix, suffix), target_affixes or (f'{target}.', '')]
        writable = [o for m in route.out_maps if all(i in route.writer for i in route.mappings[m].required_inputs)
                    for o in rcef_route.map_ends(route.rules[m])[1]]
        self.outputs = writable if columns is None else [f'{target}.{c}' for c in columns]
        if sorted(self.outputs) != sorted(writable):
            raise SystemExit(f'{source} -> {target}: the columns are not the signals that the route writes')
        # A frame that lacks one of these is refused (E_MISSING_SAMPLE).
        self.inputs = {i for m in route.in_maps for i in route.mappings[m].required_inputs}

    def signal_id(self, name: str) -> str:
        return f'{self.prefix}{name}{self.suffix}'

    def short(self, sid: str) -> str:
        """The provider's own channel name for a source or target signal, or the last ID part for any other."""
        for prefix, suffix in self.affixes:
            if sid.startswith(prefix) and sid.endswith(suffix):
                return sid[len(prefix):len(sid) - len(suffix)]
        return sid.rsplit('.', 1)[-1]

    def valid(self, sid: str, flags: dict[str, bool]) -> bool:
        return self.route.valid(sid, flags)

    def read(self, path: Path) -> list[dict]:
        """One frame per row: values by signal ID, validity flags, and every other column as a label."""
        with path.open(encoding='utf-8', newline='') as handle:
            rows = list(csv.DictReader(handle))
        channels = [c for c in rows[0] if self.signal_id(c) in self.signals]
        known = {name.strip() for s in self.signals.values() if s.get('validity')
                 for name in s['validity'].split(' AND ')}
        flags = [c for c in rows[0] if c in known]
        labels = [c for c in rows[0] if c not in channels and c not in known and c not in ('time', 'segment')]
        return [{'time': float(r['time']), 'segment': r.get('segment', ''),
                 'values': {self.signal_id(c): float(r[c]) for c in channels},
                 'flags': {f: r[f] == '1' for f in flags}, 'labels': {c: r[c] for c in labels}} for r in rows]

    def translate(self, frames: list[dict]) -> list[dict]:
        """Route's result per frame, with each refusal as one line of text and the dropped inputs by short name."""
        out = []
        for result in self.route.translate(frames):
            refused = []
            for mapping, refusal in result['refused'].items():
                refs = sorted({self.short(ref.rsplit('/', 1)[-1]) for ref in refusal['refs']})
                refused.append(f'{mapping}: {", ".join(refusal["codes"])} on {len(refs)} inputs ({", ".join(refs)})')
            out.append({**result, 'refused': refused, 'dropped': sorted(self.short(s) for s in result['dropped'])})
        return out

    def write(self, results: list[dict], path: Path) -> None:
        columns = [self.short(o) for o in self.outputs]
        with path.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle, lineterminator='\n')
            writer.writerow(['time', 'segment', *columns, 'refused', 'dropped'])
            for r in results:
                writer.writerow([f'{r["time"]:.6f}', r['segment'],
                                 *(repr(r['values'][o]) if o in r['values'] else '' for o in self.outputs),
                                 '; '.join(r['refused']), ' '.join(r['dropped'])])


def fb2_to_arkit(**options) -> Frames:
    return Frames('openxr.fb2', 'arkit.coefficient', *FB2, columns=ARKIT_COLUMNS, **options)


def arkit_to_fb2(**options) -> Frames:
    return Frames('arkit.coefficient', 'openxr.fb2', *ARKIT, target_affixes=FB2, **options)


def visemes_to_vrm(**options) -> Frames:
    return Frames('openxr.visemes', 'vrm.preset', *VISEMES, columns=('aa', 'ih', 'ou', 'ee', 'oh'), **options)


def visemes_to_arkit(**options) -> Frames:
    return Frames('openxr.visemes', 'arkit.coefficient', *VISEMES, **options)


def fb2_to_vrm(**options) -> Frames:
    return Frames('openxr.fb2', 'vrm.preset', *FB2, columns=('blinkLeft', 'blinkRight'), **options)
