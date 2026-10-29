# SPDX-License-Identifier: MIT
"""Translate frames from one expression set to another through RCEF's canonical sets.

A route runs source -> canonical -> target. An in-map reads one group of the
source set and writes one canonical group; an out-map reads one canonical
group and writes signals of the target set. The maps are found in the pack by
the profiles their signals belong to, not by their names.

- Route runs only the in-maps whose canonical group some out-map of the
  target reads, so a bad value that no selected in-map reads refuses nothing.
- Each map gets only its own inputs. An input missing from a frame is left
  out, so msf-character-tools refuses that frame (E_MISSING_SAMPLE).
- An out-map runs only on frames that hold its whole group. Otherwise its
  outputs are labelled "refused upstream at <in-map>" (a refusal) or, when no
  selected in-map writes part of the group, "not available from source" (not
  a refusal).
- A non-zero source value is "dropped" when no selected in-map reads it, or
  when no out-map reads what it is mapped to.
- Toward META visemes from another set, Route writes no isValid flag and says
  so in the frame's notes.

One-hop mode (`maps=[...]`) runs the named maps straight from source to
target, as rcef_translate.Translator does. The A/B comparison runs today's
direct maps this way (ab/README.md).
"""
from __future__ import annotations
import json
from pathlib import Path

import msf_character_tools as msf

from rcef_translate import load_pack

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ('rcef.canonical_expression', 'rcef.canonical_viseme')
META = 'openxr.visemes'
NOT_AVAILABLE = 'not available from source'
META_NOT_ASSERTED = 'META validity not asserted'


def map_ends(rules: list[dict]) -> tuple[list[str], list[str]]:
    """A map's source signals and target signals, leaving out values it computes for its own later rules."""
    written = {o for r in rules for o in r['outputs']}
    read = {i for r in rules for i in r['inputs']}
    inputs = list(dict.fromkeys(i for r in rules for i in r['inputs'] if i not in written))
    outputs = list(dict.fromkeys(o for r in rules for o in r['outputs'] if o not in read))
    return inputs, outputs


def reaches(rules: list[dict], sid: str) -> set[str]:
    """Every signal a map computes from `sid`, directly or through its own intermediate values."""
    found, todo = set(), [sid]
    while todo:
        current = todo.pop()
        for rule in rules:
            if current in rule['inputs']:
                new = set(rule['outputs']) - found
                found |= new
                todo += new
    return found


class Route:
    """The compiled maps that carry one source set to one target set."""

    def __init__(self, source: str, target: str, pack: msf.Pack | None = None, maps: list[str] | None = None,
                 canonical: tuple[str, ...] = CANONICAL, compiled: dict | None = None, root: Path = ROOT):
        """`maps` selects one-hop mode; `compiled` holds maps already compiled from the same pack, by map ID.

        `hops` lists (map, source profile, target profile) for every map the route runs.
        """
        self.pack = pack or load_pack(json.loads((root / 'generated/rcef.pack.json').read_text(encoding='utf-8')))
        document = self.pack.document
        self.source, self.target, self.one_hop = source, target, maps is not None
        self.signals = {s['id']: s for s in document['signals']}
        self.rules = {m['id']: m['rules'] for m in document['mappings']}
        homes = {}
        for profile in document['profiles']:
            for sid in profile['signal_ids']:
                homes.setdefault(sid, set()).add(profile['id'])

        def home(sids, allowed):
            """The one allowed profile that holds every signal in `sids`, or None."""
            common = set(allowed)
            for sid in sids:
                common &= homes.get(sid, set())
            return next(iter(common)) if sids and len(common) == 1 else None

        ends = {m: map_ends(r) for m, r in self.rules.items()}
        if self.one_hop:
            self.in_maps, self.out_maps = [], list(maps)
            hops = [(m, source, target) for m in maps]
        else:
            self.out_maps = [m for m, (i, o) in ends.items() if home(i, canonical) and home(o, [target])]
            wanted = {i for m in self.out_maps for i in ends[m][0]}
            self.in_maps = [m for m, (i, o) in ends.items()
                            if home(i, [source]) and home(o, canonical) and wanted & set(o)]
            hops = ([(m, source, home(ends[m][1], canonical)) for m in self.in_maps]
                    + [(m, home(ends[m][0], canonical), target) for m in self.out_maps])
        self.hops = hops
        snapshots, self.mappings = {}, {}
        for mapping, src, dst in hops:
            if compiled and mapping in compiled:
                self.mappings[mapping] = compiled[mapping]
                continue
            for profile in (src, dst):
                if profile not in snapshots:
                    snapshots[profile] = msf.profile_snapshot(self.pack, profile).value
            # Hops are proposed approximations, so they compile only with the approximation opt-in.
            result = msf.compile_mapping(self.pack, snapshots[src], snapshots[dst], mapping, True)
            if not result.ok:
                raise SystemExit(result.report.to_dict())
            self.mappings[mapping] = result.value
        self.outputs = [o for m in self.out_maps for o in ends[m][1]]
        # Which in-map writes each canonical signal, and which source signals reach an out-map.
        self.writer = {o: m for m in self.in_maps for o in ends[m][1]}
        read = {i for m in self.out_maps for i in self.mappings[m].required_inputs}
        if self.one_hop:
            self.kept = read
        else:
            self.kept = {i for m in self.in_maps for i in self.mappings[m].required_inputs
                         if reaches(self.rules[m], i) & read}

    def valid(self, sid: str, flags: dict[str, bool]) -> bool:
        """A signal's validity is the AND of the provider flags its record names; canonical signals name none."""
        validity = self.signals[sid].get('validity')
        return all(flags[name.strip()] for name in validity.split(' AND ')) if validity else True

    def translate(self, frames: list[dict]) -> list[dict]:
        """Per frame: output values, refusals by map, labels of outputs not written, and dropped inputs.

        A frame is {'time', 'values': {signal ID: value}, 'flags': {flag: bool}},
        with an optional 'segment' label, as rcef_translate.Translator.read gives.
        """
        results = [{'time': f['time'], 'segment': f.get('segment', ''), 'values': {}, 'refused': {}, 'labels': {},
                    'dropped': sorted(s for s, v in f['values'].items() if v != 0 and s not in self.kept),
                    'notes': [META_NOT_ASSERTED] if self.target == META and self.source != META else []}
                   for f in frames]
        if self.one_hop:
            middle = frames
        else:
            middle = [{'time': f['time'], 'values': {}, 'flags': {}} for f in frames]
            for mapping in self.in_maps:
                for i, values in enumerate(self._run(mapping, frames, range(len(frames)), results)):
                    if values is not None:
                        middle[i]['values'].update(values)
        for mapping in self.out_maps:
            required = self.mappings[mapping].required_inputs
            outputs = self.mappings[mapping].output_ids
            span = []
            for i, frame in enumerate(middle):
                missing = [s for s in required if s not in frame['values']]
                if not missing:
                    span.append(i)
                    continue
                if self.one_hop:
                    span.append(i)  # msf-character-tools refuses it with E_MISSING_SAMPLE
                    continue
                if any(s not in self.writer for s in missing):
                    label = NOT_AVAILABLE
                else:
                    label = f'refused upstream at {", ".join(sorted({self.writer[s] for s in missing}))}'
                results[i]['labels'].update(dict.fromkeys(outputs, label))
            for i, values in zip(span, self._run(mapping, middle, span, results)):
                if values is None:
                    results[i]['labels'].update(dict.fromkeys(outputs, f'refused at {mapping}'))
                else:
                    results[i]['values'].update(values)
        return results

    def _run(self, mapping: str, frames: list[dict], span, results: list[dict]) -> list[dict | None]:
        """The map's output values for each frame in `span`, or None where it refused the frame."""
        compiled = self.mappings[mapping]
        samples = {}
        for i in span:
            values, flags = frames[i]['values'], frames[i].get('flags', {})
            given = [s for s in compiled.required_inputs if s in values]
            samples[i] = {'timestamp': frames[i]['time'], 'values': {s: values[s] for s in given},
                          'validity': {s: self.valid(s, flags) for s in given}}
        written = dict.fromkeys(span)
        self._evaluate(mapping, compiled, samples, list(span), results, written)
        return [written[i] for i in span]

    def _evaluate(self, mapping, compiled, samples, span, results, written):
        if not span:
            return
        outcome = msf.evaluate_mapping(compiled, [samples[i] for i in span])
        if outcome.ok:
            for i, sample in zip(span, outcome.value.samples):
                written[i] = dict(sample['values'])
            return
        # A failed call returns no values, but every error names its sample
        # ("/samples/<n>/..."), so the refused frames are labelled and the rest
        # evaluated again without them.
        refused = {}
        for diagnostic in outcome.report.diagnostics:
            if diagnostic.severity != 'error':
                continue
            parts = diagnostic.ref.split('/')
            if len(parts) < 3 or parts[1] != 'samples':
                raise SystemExit(outcome.report.to_dict())
            refused.setdefault(span[int(parts[2])], []).append(diagnostic)
        if not refused:
            raise SystemExit(outcome.report.to_dict())  # a failure that names no frame: retrying cannot help
        for i, diagnostics in refused.items():
            results[i]['refused'][mapping] = {'codes': sorted({d.code for d in diagnostics}),
                                              'refs': sorted({d.ref.split('/', 3)[3] for d in diagnostics
                                                              if d.ref.count('/') >= 3})}
        self._evaluate(mapping, compiled, samples, [i for i in span if i not in refused], results, written)
