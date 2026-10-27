# SPDX-License-Identifier: MIT
"""Translate provider frames with RCEF's maps through the msf-tools public API.

Used by translate_fb2_to_arkit.py, translate_visemes_to_vrm.py,
face_pipeline.py and viseme_pipeline.py.
"""
from __future__ import annotations
import csv
import json
import os
from pathlib import Path

import msf_tools as msf

ROOT = Path(__file__).resolve().parents[1]


def cache_home() -> Path:
    """$XDG_CACHE_HOME, or ~/.cache: where the examples write by default, outside the checkout."""
    return Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache')


def load_pack(document: dict) -> msf.Pack:
    """Validate and compile a pack document, such as generated/rcef.pack.json."""
    validated = msf.validate_authoring(document)
    if not validated.ok:
        raise SystemExit(validated.report.to_dict())
    return msf.compile_pack(validated.value).value


class Translator:
    """The compiled RCEF maps from one source profile to one target profile."""

    def __init__(self, source: str, target: str, mappings: list[str], prefix: str, suffix: str,
                 root: Path = ROOT, pack: msf.Pack | None = None, compiled: dict | None = None):
        """`pack` replaces the published pack; `compiled` holds maps already compiled from it."""
        self.pack = pack or load_pack(json.loads((root / 'generated/rcef.pack.json').read_text(encoding='utf-8')))
        self.signals = {s['id']: s for s in self.pack.document['signals']}
        self.prefix, self.suffix = prefix, suffix
        self.mappings, snapshots = {}, None
        for mapping in mappings:
            if compiled and mapping in compiled:
                self.mappings[mapping] = compiled[mapping]
                continue
            snapshots = snapshots or (msf.profile_snapshot(self.pack, source).value,
                                      msf.profile_snapshot(self.pack, target).value)
            # RCEF's cross-provider mappings are proposed approximations, so they compile
            # only with the approximation opt-in.
            result = msf.compile_mapping(self.pack, *snapshots, mapping, True)
            if not result.ok:
                raise SystemExit(result.report.to_dict())
            self.mappings[mapping] = result.value
        rules = {m['id']: m['rules'] for m in self.pack.document['mappings']}
        # Values a map computes for its own later mappings are not outputs.
        computed = {i for m in mappings for r in rules[m] for i in r['inputs']}
        self.outputs = [o for m in mappings for r in rules[m] for o in r['outputs'] if o not in computed]
        self.inputs = {i for m in self.mappings.values() for i in m.required_inputs}

    def signal_id(self, name: str) -> str:
        return f'{self.prefix}{name}{self.suffix}'

    def short(self, sid: str) -> str:
        """The provider's own channel name for an input, or the last ID part for an output."""
        if sid.startswith(self.prefix) and sid.endswith(self.suffix):
            return sid[len(self.prefix):len(sid) - len(self.suffix)]
        return sid.rsplit('.', 1)[-1]

    def valid(self, sid: str, flags: dict[str, bool]) -> bool:
        """A signal's validity is the AND of the provider flags its record names; ARKit names none."""
        validity = self.signals[sid].get('validity')
        return all(flags[name.strip()] for name in validity.split(' AND ')) if validity else True

    def read(self, path: Path) -> list[dict]:
        with path.open(encoding='utf-8', newline='') as handle:
            rows = list(csv.DictReader(handle))
        channels = [c for c in rows[0] if self.signal_id(c) in self.signals]
        known = {name.strip() for s in self.signals.values() if s.get('validity')
                 for name in s['validity'].split(' AND ')}
        flags = [c for c in rows[0] if c in known]
        # Anything else (such as an expression's phase) is a label carried through.
        labels = [c for c in rows[0] if c not in channels and c not in known and c not in ('time', 'segment')]
        return [{'time': float(r['time']), 'segment': r.get('segment', ''),
                 'values': {self.signal_id(c): float(r[c]) for c in channels},
                 'flags': {f: r[f] == '1' for f in flags}, 'labels': {c: r[c] for c in labels}} for r in rows]

    def translate(self, frames: list[dict]) -> list[dict]:
        """Per frame: output values, refusals by map, and non-zero inputs no mapping reads."""
        results = [{'time': f['time'], 'segment': f['segment'], 'values': {}, 'refused': [], 'dropped': []}
                   for f in frames]
        for mapping, compiled in self.mappings.items():
            # msf-tools refuses a frame if any channel it is given is marked invalid,
            # even one the map does not read, so each map gets only its own inputs.
            inputs = sorted(compiled.required_inputs)
            samples = [{'timestamp': f['time'], 'values': {i: f['values'][i] for i in inputs},
                        'validity': {i: self.valid(i, f['flags']) for i in inputs}} for f in frames]
            self._evaluate(mapping, compiled, samples, list(range(len(samples))), results)
        for frame, result in zip(frames, results):
            result['dropped'] = sorted(self.short(s) for s, v in frame['values'].items()
                                       if v != 0 and s not in self.inputs)
        return results

    def _evaluate(self, mapping, compiled, samples, span, results):
        outcome = msf.evaluate_mapping(compiled, [samples[i] for i in span])
        if outcome.ok:
            for i, sample in zip(span, outcome.value.samples):
                results[i]['values'].update(sample['values'])
            return
        # A failed call returns no values, but every error names its sample
        # ("/samples/<n>/..."), so the refused frames are labelled and the rest
        # evaluated again without them.
        refusals = {}
        for diagnostic in outcome.report.diagnostics:
            if diagnostic.severity != 'error':
                continue
            parts = diagnostic.ref.split('/')
            if len(parts) < 3 or parts[1] != 'samples':
                raise SystemExit(outcome.report.to_dict())
            refusals.setdefault(span[int(parts[2])], []).append(diagnostic)
        for i, diagnostics in refusals.items():
            codes = sorted({d.code for d in diagnostics})
            refs = sorted({self.short(d.ref.rsplit('/', 1)[-1]) for d in diagnostics})
            results[i]['refused'].append(f'{mapping}: {", ".join(codes)} on {len(refs)} inputs ({", ".join(refs)})')
        rest = [i for i in span if i not in refusals]
        if rest:
            self._evaluate(mapping, compiled, samples, rest, results)

    def write(self, results: list[dict], path: Path) -> None:
        columns = [self.short(o) for o in self.outputs]
        with path.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle, lineterminator='\n')
            writer.writerow(['time', 'segment', *columns, 'refused', 'dropped'])
            for r in results:
                writer.writerow([f'{r["time"]:.6f}', r['segment'],
                                 *(repr(r['values'][o]) if o in r['values'] else '' for o in self.outputs),
                                 '; '.join(r['refused']), ' '.join(r['dropped'])])


def fb2_to_arkit(root: Path = ROOT, **options) -> Translator:
    return Translator('openxr.fb2', 'arkit.coefficient', ['fb2.to_arkit', 'fb2_gaze.to_arkit'],
                      'openxr.fb2.XR_FACE_EXPRESSION2_', '_FB', root, **options)


def arkit_to_fb2(root: Path = ROOT, **options) -> Translator:
    return Translator('arkit.coefficient', 'openxr.fb2', ['arkit.to_fb2', 'arkit_gaze.to_fb2'],
                      'openxr.fb2.XR_FACE_EXPRESSION2_', '_FB', root, **options)


def visemes_to_vrm(root: Path = ROOT, **options) -> Translator:
    return Translator('openxr.visemes', 'vrm.preset', ['visemes.to_vrm'],
                      'openxr.visemes.XR_FACE_TRACKING_VISEME_', '_META', root, **options)


def fb2_to_vrm(root: Path = ROOT, **options) -> Translator:
    return Translator('openxr.fb2', 'vrm.preset', ['fb2.to_vrm'], 'openxr.fb2.XR_FACE_EXPRESSION2_', '_FB', root, **options)
