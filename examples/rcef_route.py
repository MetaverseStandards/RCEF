# SPDX-License-Identifier: MIT
"""Translate frames from one expression set to another through RCEF's canonical sets.

A route runs source -> canonical -> target. RCEF has one map per set pair and
direction: an in-map from the source into a canonical set, and an out-map from
a canonical set to the target. The maps are found in the pack by the profiles
their signals belong to, not by their names. VRM has maps to and from both
canonical sets (blinks and vowels), so a VRM route can run two in-maps or two
out-maps.

Each map runs once on all frames, with msf-character-tools' partial
evaluation, so a bad input refuses only the outputs that read it:

- Each map gets only its own inputs. An input missing from a frame makes the
  outputs that read it "not available": a target output that reads one is
  labelled "not available from source" (not a refusal).
- An in-map output that is refused (an invalid or out-of-domain input) makes
  every target output that reads it "refused upstream at <in-map>". Only the
  canonical values that an out-map or a bridge reads count: a bad value that
  no target output reads refuses nothing.
- An out-map output that is refused is labelled "refused at <out-map>".
- A target output that no selected in-map can write is "not available from
  source". So is one that reads a value that is not available as well as one
  that is refused: it would not be written without the refusal either.
- A non-zero source value is "dropped" when no in-map output that reaches the
  target reads it.
- Toward META visemes from another set, Route writes no isValid flag and says
  so in the frame's notes.
- A bridge is a map from one canonical set to the other: the viseme pose
  bridge writes canonical expression signals from viseme classes. Route runs
  it only when the target reads what it writes, the source cannot write that
  itself, and the source writes some of what the bridge reads. Then the route
  is in-maps -> bridge -> out-maps. A class that no selected in-map can write
  counts as 0 in the bridge, and the notes of each frame where the bridge
  writes a value say so. A class refused upstream refuses the bridge outputs
  that read it.

One-hop mode (`maps=[...]`) runs the named maps straight from source to
target, as rcef_translate.Translator does, with whole-map evaluation: a
refusal refuses all outputs of that map on that frame. The A/B comparison runs
the retired direct maps this way, on the frozen pack that still holds them
(ab/README.md).
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
ZERO_FILLED = 'bridge {}: the source writes no {}; counted as 0'


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


def refusal(diagnostics) -> dict:
    """Codes and references (after "/samples/<n>/") of a refusal's diagnostics."""
    return {'codes': sorted({d.code for d in diagnostics}),
            'refs': sorted({d.ref.split('/', 3)[3] for d in diagnostics if d.ref.count('/') >= 3})}


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
        # A map whose every mapping is unresolved (survey.ambiguous) is a record, not a translation: msf-character-tools
        # refuses to compile it, so Route never selects it.
        self.rules = {m['id']: m['rules'] for m in document['mappings']
                      if any(r['disposition'] != 'unresolved' for r in m['rules'])}
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
        self.bridges, self.fill = [], {}
        if self.one_hop:
            self.in_maps, self.out_maps = [], list(maps)
            hops = [(m, source, target) for m in maps]
        else:
            self.out_maps = [m for m, (i, o) in ends.items() if home(i, canonical) and home(o, [target])]
            wanted = {i for m in self.out_maps for i in ends[m][0]}
            direct = {s for m, (i, o) in ends.items() if home(i, [source]) and home(o, canonical) for s in o}
            self.bridges = [m for m, (i, o) in ends.items() if home(i, canonical) and home(o, canonical)
                            and home(i, canonical) != home(o, canonical)
                            and wanted & set(o) and not direct & set(o) and direct & set(i)]
            wanted |= {i for m in self.bridges for i in ends[m][0]}
            self.in_maps = [m for m, (i, o) in ends.items()
                            if home(i, [source]) and home(o, canonical) and wanted & set(o)]
            hops = ([(m, source, home(ends[m][1], canonical)) for m in self.in_maps]
                    + [(m, home(ends[m][0], canonical), home(ends[m][1], canonical)) for m in self.bridges]
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
        # The canonical values that count: those an out-map or a bridge reads.
        self.read = {i for m in self.out_maps + self.bridges for i in self.mappings[m].required_inputs}
        # Which in-map or bridge writes each canonical signal; a bridge input that none writes counts as 0.
        self.writer = {o: m for m in self.in_maps for o in ends[m][1]}
        self.fill = {m: sorted(s for s in self.mappings[m].required_inputs if s not in self.writer)
                     for m in self.bridges}
        self.writer.update({o: m for m in self.bridges for o in ends[m][1]})
        if self.one_hop:
            self.kept = self.read
        else:
            self.kept = {i for m in self.in_maps for i in self.mappings[m].required_inputs
                         if reaches(self.rules[m], i) & self.read}

    def valid(self, sid: str, flags: dict[str, bool]) -> bool:
        """A signal's validity is the AND of the provider flags its record names; canonical signals name none."""
        validity = self.signals[sid].get('validity')
        return all(flags[name.strip()] for name in validity.split(' AND ')) if validity else True

    def translate(self, frames: list[dict]) -> list[dict]:
        """Per frame: output values, refusals by map, labels of outputs not written, dropped inputs and notes.

        A frame is {'time', 'values': {signal ID: value}, 'flags': {flag: bool}},
        with an optional 'segment' label, as rcef_frames.Frames.read gives. A
        refusal holds the codes and references of the map's refused outputs that
        count, and those outputs.
        """
        results = [{'time': f['time'], 'segment': f.get('segment', ''), 'values': {}, 'refused': {}, 'labels': {},
                    'dropped': sorted(s for s, v in f['values'].items() if v != 0 and s not in self.kept),
                    'notes': [META_NOT_ASSERTED] if self.target == META and self.source != META else []}
                   for f in frames]
        if self.one_hop:
            for mapping in self.out_maps:
                outputs = self.mappings[mapping].output_ids
                for i, values in enumerate(self._whole(mapping, frames, results)):
                    if values is None:
                        results[i]['labels'].update(dict.fromkeys(outputs, f'refused at {mapping}'))
                    else:
                        results[i]['values'].update(values)
            return results
        middle = [{'time': f['time'], 'values': {}} for f in frames]
        # Per frame, the maps that refused each canonical value that is not written.
        causes = [{} for _ in frames]
        for mapping in self.in_maps:
            self._keep(mapping, self._partial(mapping, frames), middle, results, causes)
        for mapping in self.bridges:
            fill = dict.fromkeys(self.fill[mapping], 0.0)
            evaluated = self._partial(mapping, [{'time': f['time'], 'values': {**fill, **f['values']}} for f in middle])
            self._keep(mapping, evaluated, middle, results, causes)
            # A bridge output that is not available because its inputs were refused upstream is refused upstream too.
            for row in evaluated.unavailable:
                found = causes[row['sample']]
                if all(s in found for s in row['inputs']):
                    found[row['output']] = set().union(*(found[s] for s in row['inputs']))
            if fill:
                note = ZERO_FILLED.format(mapping, ', '.join(s.rsplit('.', 1)[1] for s in fill))
                for i, sample in enumerate(evaluated.samples):
                    if sample['values']:
                        results[i]['notes'].append(note)
        for mapping in self.out_maps:
            evaluated = self._partial(mapping, middle)
            for i, sample in enumerate(evaluated.samples):
                results[i]['values'].update(sample['values'])
            self._refusals(mapping, evaluated, results)
            for row in evaluated.refusals:
                results[row['sample']]['labels'][row['output']] = f'refused at {mapping}'
            for row in evaluated.unavailable:
                found, missing = causes[row['sample']], row['inputs']
                if all(s in found for s in missing):
                    label = f'refused upstream at {", ".join(sorted(set().union(*(found[s] for s in missing))))}'
                else:
                    label = NOT_AVAILABLE
                results[row['sample']]['labels'][row['output']] = label
        return results

    def _partial(self, mapping: str, frames: list[dict]):
        """One map on every frame with partial evaluation: its written values, refusals and unavailable outputs."""
        outcome = msf.evaluate_mapping(self.mappings[mapping], self._samples(mapping, frames), partial=True)
        if not outcome.ok:
            # Only a fault that no output owns fails a partial evaluation; Route gives each map only its own inputs.
            raise SystemExit(outcome.report.to_dict())
        return outcome.value

    def _samples(self, mapping: str, frames: list[dict]) -> list[dict]:
        """Each frame as a sample of the map: only its own inputs that the frame holds, with their validity."""
        compiled, samples = self.mappings[mapping], []
        for frame in frames:
            values, flags = frame['values'], frame.get('flags', {})
            given = [s for s in compiled.required_inputs if s in values]
            samples.append({'timestamp': frame['time'], 'values': {s: values[s] for s in given},
                            'validity': {s: self.valid(s, flags) for s in given}})
        return samples

    def _refusals(self, mapping: str, evaluated, results: list[dict]) -> None:
        """Record each frame's refused outputs of a map that count: all of an out-map's, and the canonical values
        that an out-map or a bridge reads."""
        counted = None if mapping in self.out_maps else self.read
        by_frame = {}
        for row in evaluated.refusals:
            if counted is None or row['output'] in counted:
                by_frame.setdefault(row['sample'], []).append(row)
        for i, rows in by_frame.items():
            results[i]['refused'][mapping] = {**refusal([d for r in rows for d in r['diagnostics']]),
                                              'outputs': sorted(r['output'] for r in rows)}

    def _keep(self, mapping: str, evaluated, middle: list[dict], results: list[dict], causes: list[dict]) -> None:
        """Add an in-map's or a bridge's values to the canonical frames, and note its refused outputs that count."""
        for i, sample in enumerate(evaluated.samples):
            middle[i]['values'].update(sample['values'])
        self._refusals(mapping, evaluated, results)
        for row in evaluated.refusals:
            if row['output'] in self.read:
                causes[row['sample']][row['output']] = {mapping}

    def _whole(self, mapping: str, frames: list[dict], results: list[dict]) -> list[dict | None]:
        """One-hop mode: the map's output values for each frame, or None where it refused the frame."""
        written = [None] * len(frames)
        self._evaluate(mapping, self._samples(mapping, frames), list(range(len(frames))), results, written)
        return written

    def _evaluate(self, mapping, samples, span, results, written):
        if not span:
            return
        outcome = msf.evaluate_mapping(self.mappings[mapping], [samples[i] for i in span])
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
            results[i]['refused'][mapping] = refusal(diagnostics)
        self._evaluate(mapping, samples, [i for i in span if i not in refused], results, written)
