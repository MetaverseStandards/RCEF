# SPDX-License-Identifier: MIT
"""Translate provider frames with RCEF's mappings through the msf-tools public API.

Used by translate_fb2_to_arkit.py, translate_visemes_to_vrm.py and
face_pipeline.py. Only the public msf-tools API is used.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

import msf_tools as msf

ROOT = Path(__file__).resolve().parents[1]


class Translator:
    """The compiled RCEF mappings from one source profile to one target profile."""

    def __init__(self, source: str, target: str, mappings: list[str], prefix: str, suffix: str,
                 root: Path = ROOT):
        # The published pack is the consumer-facing artifact, so it is what we load.
        validated = msf.validate_authoring(json.loads((root / 'generated/rcef.pack.json').read_text(encoding='utf-8')))
        if not validated.ok:
            raise SystemExit(validated.report.to_dict())
        self.pack = msf.compile_pack(validated.value).value
        self.signals = {s['id']: s for s in self.pack.document['signals']}
        source_snapshot = msf.profile_snapshot(self.pack, source).value
        target_snapshot = msf.profile_snapshot(self.pack, target).value
        self.prefix, self.suffix = prefix, suffix
        self.mappings = {}
        for mapping in mappings:
            # RCEF's cross-provider rules are proposed approximations, so they compile
            # only with the approximation opt-in.
            result = msf.compile_mapping(self.pack, source_snapshot, target_snapshot, mapping, True)
            if not result.ok:
                raise SystemExit(result.report.to_dict())
            self.mappings[mapping] = result.value
        rules = {m['id']: m['rules'] for m in self.pack.document['mappings']}
        self.outputs = [o for m in mappings for r in rules[m] for o in r['outputs']]
        self.inputs = {i for compiled in self.mappings.values() for i in compiled.required_inputs}

    def signal_id(self, name: str) -> str:
        return f'{self.prefix}{name}{self.suffix}'

    def short(self, sid: str) -> str:
        """The provider's own channel name for an input, or the last ID part for an output."""
        if sid.startswith(self.prefix) and sid.endswith(self.suffix):
            return sid[len(self.prefix):len(sid) - len(self.suffix)]
        return sid.rsplit('.', 1)[-1]

    def valid(self, sid: str, flags: dict[str, bool]) -> bool:
        """A signal's validity is the AND of the provider flags its record names."""
        return all(flags[name.strip()] for name in self.signals[sid]['validity'].split(' AND '))

    def read(self, path: Path) -> list[dict]:
        with path.open(encoding='utf-8', newline='') as handle:
            rows = list(csv.DictReader(handle))
        channels = [c for c in rows[0] if self.signal_id(c) in self.signals]
        flags = [c for c in rows[0] if c not in channels and c not in ('time', 'segment')]
        return [{'time': float(r['time']), 'segment': r.get('segment', ''),
                 'values': {self.signal_id(c): float(r[c]) for c in channels},
                 'flags': {f: r[f] == '1' for f in flags}} for r in rows]

    def translate(self, frames: list[dict]) -> list[dict]:
        """Per frame: output values, refusals by mapping, and non-zero inputs no rule reads."""
        results = [{'time': f['time'], 'segment': f['segment'], 'values': {}, 'refused': [], 'dropped': []}
                   for f in frames]
        for mapping, compiled in self.mappings.items():
            # msf-tools refuses a frame if any channel it is given is marked invalid,
            # even one the mapping does not read, so each mapping gets only its own inputs.
            inputs = sorted(compiled.required_inputs)
            samples = [{'timestamp': f['time'], 'values': {i: f['values'][i] for i in inputs},
                        'validity': {i: self.valid(i, f['flags']) for i in inputs}} for f in frames]
            # Frames are independent, so consecutive frames with the same validity go
            # in one call; a failed call is retried frame by frame to place the refusals.
            start = 0
            while start < len(samples):
                end = start + 1
                while end < len(samples) and samples[end]['validity'] == samples[start]['validity']:
                    end += 1
                self._evaluate(mapping, compiled, samples, range(start, end), results)
                start = end
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
        if len(span) > 1:
            for i in span:
                self._evaluate(mapping, compiled, samples, range(i, i + 1), results)
            return
        codes = sorted({d.code for d in outcome.report.diagnostics})
        refs = sorted({self.short(d.ref.rsplit('/', 1)[-1]) for d in outcome.report.diagnostics})
        results[span[0]]['refused'].append(f'{mapping}: {", ".join(codes)} on {len(refs)} inputs ({", ".join(refs)})')

    def write(self, results: list[dict], path: Path) -> None:
        columns = [self.short(o) for o in self.outputs]
        with path.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle, lineterminator='\n')
            writer.writerow(['time', 'segment', *columns, 'refused', 'dropped'])
            for r in results:
                writer.writerow([f'{r["time"]:.6f}', r['segment'],
                                 *(repr(r['values'][o]) if o in r['values'] else '' for o in self.outputs),
                                 '; '.join(r['refused']), ' '.join(r['dropped'])])


def fb2_to_arkit(root: Path = ROOT) -> Translator:
    return Translator('openxr.fb2', 'arkit.coefficient', ['fb2.to_arkit', 'fb2_gaze.to_arkit'],
                      'openxr.fb2.XR_FACE_EXPRESSION2_', '_FB', root)


def visemes_to_vrm(root: Path = ROOT) -> Translator:
    return Translator('openxr.visemes', 'vrm.preset', ['visemes.to_vrm'],
                      'openxr.visemes.XR_FACE_TRACKING_VISEME_', '_META', root)
