# SPDX-License-Identifier: MIT
"""A pure-Python oracle (O) for msf-character-tools 0.6.0 map evaluation, and for routes made of such maps.

It reads maps from a pack document and evaluates frames as the locked
msf-character-tools does (core/src/mapping.cpp, Evaluator::frame, and
core/src/math3d.cpp), in binary64 and in the same order of operations:

- frame checks: unknown channels, explicit boolean validity, the input
  domain, invalid inputs and missing required inputs;
- rules in dependency waves, as compile orders them; a rule with a missing
  input is skipped;
- affine: add(product(scale, x), offset); weighted_sum: from +0.0, add each
  product(weight, input) in order; piecewise_linear: the knot value when x is
  a knot, else ya + t * (yb - ya) with t = (x - xa) / (xb - xa), clamped to
  [min(ya, yb), max(ya, yb)] with Python's min and max, which keep the first
  argument on ties;
- a non-finite sum, product or quotient, a non-zero product or quotient that
  underflows to zero, a zero divisor and an output outside its domain each
  refuse the frame.

Domain bounds are compared as binary64 values. That is exact for the bounds
RCEF uses (whole numbers); msf-character-tools compares the decimal text.

Partial evaluation (docs/reference.md of msf-character-tools, "Partial
evaluation") scopes each fault to the outputs that depend on it, through the
rules: an output is written when nothing it depends on failed; refused when an
input it reads is bad (supplied but invalid, out of domain or of the wrong
type) or a rule it depends on fails; and not available when only missing
inputs stop it.

A route is in-maps, then any bridges (maps from one canonical set to the
other, such as the viseme pose bridge), then out-maps, as examples/rcef_route.py
documents it, each map evaluated partially. Only the canonical values that an
out-map or a bridge reads count. An out-map output that reads a value refused
upstream is labelled "refused upstream at" the maps that refused it, unless it
also reads a value that is not available: then it is not available from
source. A bridge input that no in-map of the route writes counts as 0, and each
frame where the bridge writes a value gets a note saying so.

The A/B harness (scripts/ab_compare.py) uses it to give the pivot route's
expected values and refusals before any registered run (ab/README.md).
"""
from __future__ import annotations
import bisect
from dataclasses import dataclass
import math
import struct


# Route's labels and notes (examples/rcef_route.py), written out here so that O does not read Route's code.
NOT_AVAILABLE = 'not available from source'
META = 'openxr.visemes'
META_NOT_ASSERTED = 'META validity not asserted'
ZERO_FILLED = 'bridge {}: the source writes no {}; counted as 0'


class Fault(Exception):
    def __init__(self, code: str, ref: str):
        super().__init__(code, ref)
        self.code, self.ref = code, ref


def _finite(value, ref):
    if not math.isfinite(value):
        raise Fault('E_NONFINITE', ref)
    return value


def add(a, b, ref):
    return _finite(a + b, ref)


def sub(a, b, ref):
    return _finite(a - b, ref)


def product(a, b, ref):
    result = _finite(a * b, ref)
    if result == 0 and a != 0 and b != 0:
        raise Fault('E_NONFINITE', ref)
    return result


def divide(a, b, ref):
    if b == 0:
        raise Fault('E_SINGULAR', ref)
    result = _finite(a / b, ref)
    if result == 0 and a != 0:
        raise Fault('E_NONFINITE', ref)
    return result


def py_max(a, b):
    return b if b > a else a


def py_min(a, b):
    return b if b < a else a


def piecewise(knots, x, ref):
    xs = [k[0] for k in knots]
    i = bisect.bisect_right(xs, x) - 1
    if xs[i] == x:
        return knots[i][1]
    (xa, ya), (xb, yb) = knots[i], knots[i + 1]
    t = divide(sub(x, xa, ref), sub(xb, xa, ref), ref)
    value = add(ya, product(t, sub(yb, ya, ref), ref), ref)
    return py_min(py_max(value, py_min(ya, yb)), py_max(ya, yb))


def in_domain(value, domain, ref):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise Fault('E_TYPE', ref)
    low, high = domain.get('min'), domain.get('max')
    if (low is not None and value < low) or (high is not None and value > high):
        raise Fault('E_DOMAIN', ref)


@dataclass(frozen=True)
class Plan:
    """A map as compile leaves it: required inputs, rules in execution order and target-bound outputs."""
    required: tuple
    instructions: tuple
    outputs: tuple


class Oracle:
    def __init__(self, document: dict):
        self.signals = {s['id']: s for s in document['signals']}
        self.maps = {m['id']: m['rules'] for m in document['mappings']}
        self.profiles = {p['id']: p['signal_ids'] for p in document['profiles']}
        self._plans = {}

    def plan(self, mapping: str, target: str) -> Plan:
        if (mapping, target) in self._plans:
            return self._plans[mapping, target]
        rules = self.maps[mapping]
        writer = {}
        for n, rule in enumerate(rules):
            writer[rule['outputs'][0]] = n
        # Dependency waves: a rule joins the wave after the one holding its last dependency.
        dependents, pending = [[] for _ in rules], []
        for n, rule in enumerate(rules):
            needs = sorted({writer[s] for s in rule['inputs'] if s in writer})
            pending.append(len(needs))
            for need in needs:
                dependents[need].append(n)
        order, wave = [], [n for n in range(len(rules)) if not pending[n]]
        while wave:
            ready = []
            for n in wave:
                order.append(rules[n])
                for d in dependents[n]:
                    pending[d] -= 1
                    if not pending[d]:
                        ready.append(d)
            wave = sorted(ready)
        required = tuple(dict.fromkeys(s for r in rules for s in r['inputs'] if s not in writer))
        members = set(self.profiles[target])
        outputs = tuple(dict.fromkeys(r['outputs'][0] for r in rules if r['outputs'][0] in members))
        self._plans[mapping, target] = plan = Plan(required, tuple(order), outputs)
        return plan

    def frame(self, mapping: str, source: str, target: str, values: dict, validity: dict, index: int = 0):
        """(outputs, diagnostics) for one frame: outputs is None when any diagnostic refuses it.

        Diagnostics are sorted (code, ref) pairs, with refs as msf-character-tools
        writes them ("/samples/<index>/<signal>" or ".../rules/<rule id>").
        """
        plan = self.plan(mapping, target)
        sources = set(self.profiles[source])
        ref = f'/samples/{index}'
        known, invalid, diagnostics = {}, set(), []
        for sid in set(values) | set(validity):
            try:
                if type(sid) is not str or sid not in sources:
                    raise Fault('E_SAMPLE_REFERENCE', ref)
                if sid not in values or type(validity.get(sid)) is not bool:
                    raise Fault('E_VALIDITY', f'{ref}/{sid}')
                in_domain(values[sid], self.signals[sid]['domain'], f'{ref}/{sid}')
                if not validity[sid]:
                    raise Fault('E_INVALID_SAMPLE', f'{ref}/{sid}')
                known[sid] = float(values[sid])
            except Fault as fault:
                diagnostics.append((fault.code, fault.ref))
                invalid.add(sid)
        for sid in plan.required:
            if sid not in known and sid not in invalid:
                diagnostics.append(('E_MISSING_SAMPLE', f'{ref}/{sid}'))
        for rule in plan.instructions:
            inputs = rule['inputs']
            if any(s not in known for s in inputs):
                continue
            operator, at = rule['operator'], f'{ref}/rules/{rule["id"]}'
            try:
                if operator['id'] == 'identity':
                    value = known[inputs[0]]
                elif operator['id'] == 'affine':
                    value = add(product(operator['scale'], known[inputs[0]], at), operator['offset'], at)
                elif operator['id'] == 'weighted_sum':
                    value = 0.0
                    for weight, sid in zip(operator['weights'], inputs):
                        value = add(value, product(weight, known[sid], at), at)
                else:
                    value = piecewise(operator['knots'], known[inputs[0]], at)
                in_domain(value, self.signals[rule['outputs'][0]]['domain'], at)
                known[rule['outputs'][0]] = value
            except Fault as fault:
                diagnostics.append((fault.code, fault.ref))
        if diagnostics:
            return None, sorted(diagnostics)
        return {sid: known[sid] for sid in plan.outputs}, []

    def partial(self, mapping: str, source: str, target: str, values: dict, validity: dict, index: int = 0):
        """(written, refused, unavailable) for one frame with partial evaluation.

        written maps outputs to values; refused maps each refused output to the
        sorted (code, ref) pairs of the faults it depends on; unavailable maps
        each output that only missing inputs stop to those inputs. The caller
        gives only the map's own inputs, so no fault fails the whole frame.
        """
        plan = self.plan(mapping, target)
        sources = set(self.profiles[source])
        ref = f'/samples/{index}'
        known, faults = {}, {}  # faults: signal -> the (code, ref) pairs it depends on
        for sid in set(values) | set(validity):
            if type(sid) is not str or sid not in sources or sid not in plan.required:
                raise ValueError(f'{mapping}: {sid!r} is not an input of the map')
            try:
                if sid not in values or type(validity.get(sid)) is not bool:
                    raise Fault('E_VALIDITY', f'{ref}/{sid}')
                in_domain(values[sid], self.signals[sid]['domain'], f'{ref}/{sid}')
                if not validity[sid]:
                    raise Fault('E_INVALID_SAMPLE', f'{ref}/{sid}')
                known[sid] = float(values[sid])
            except Fault as fault:
                faults[sid] = {(fault.code, fault.ref)}
        for sid in plan.required:
            if sid not in known and sid not in faults:
                faults[sid] = {('E_MISSING_SAMPLE', f'{ref}/{sid}')}
        for rule in plan.instructions:
            inputs, output = rule['inputs'], rule['outputs'][0]
            upstream = set().union(*(faults.get(s, set()) for s in inputs))
            if upstream:
                faults[output] = upstream
                continue
            operator, at = rule['operator'], f'{ref}/rules/{rule["id"]}'
            try:
                if operator['id'] == 'identity':
                    value = known[inputs[0]]
                elif operator['id'] == 'affine':
                    value = add(product(operator['scale'], known[inputs[0]], at), operator['offset'], at)
                elif operator['id'] == 'weighted_sum':
                    value = 0.0
                    for weight, sid in zip(operator['weights'], inputs):
                        value = add(value, product(weight, known[sid], at), at)
                else:
                    value = piecewise(operator['knots'], known[inputs[0]], at)
                in_domain(value, self.signals[output]['domain'], at)
                known[output] = value
            except Fault as fault:
                faults[output] = {(fault.code, fault.ref)}
        written, refused, unavailable = {}, {}, {}
        for sid in plan.outputs:
            if sid in known:
                written[sid] = known[sid]
            elif any(code != 'E_MISSING_SAMPLE' for code, _ in faults[sid]):
                refused[sid] = sorted(faults[sid])
            else:
                unavailable[sid] = sorted(r.rsplit('/', 1)[1] for _, r in faults[sid])
        return written, refused, unavailable

    def valid(self, sid: str, flags: dict) -> bool:
        validity = self.signals[sid].get('validity')
        return all(flags[name.strip()] for name in validity.split(' AND ')) if validity else True

    def run(self, mapping: str, source: str, target: str, values: dict, flags: dict, partial: bool = False):
        """One map on one frame, given only its own required inputs that the frame holds (as Route sends them)."""
        given = [s for s in self.plan(mapping, target).required if s in values]
        evaluate = self.partial if partial else self.frame
        return evaluate(mapping, source, target, {s: values[s] for s in given}, {s: self.valid(s, flags) for s in given})

    def route(self, source: str, target: str, in_hops: list, out_maps: list, values: dict, flags: dict,
              bridges: list = ()) -> dict:
        """The expected result of a route on one frame.

        in_hops lists (in-map, canonical profile); bridges lists (bridge, the
        canonical profile it reads, the one it writes); out_maps lists
        (out-map, canonical profile). With no in-hops the out-maps read the
        source frame with whole-map evaluation (one-hop mode). The result holds
        values, refusals by map, labels of outputs not written and notes, as
        rcef_route.Route gives them: a refusal holds its codes, the references
        after "/samples/<n>/" and the refused outputs that count.
        """
        notes = [META_NOT_ASSERTED] if target == META and source != META else []
        result = {'values': {}, 'refused': {}, 'labels': {}, 'notes': notes}
        if not in_hops:
            for mapping, _ in out_maps:
                plan = self.plan(mapping, target)
                outputs, diagnostics = self.run(mapping, source, target, values, flags)
                if outputs is None:
                    result['refused'][mapping] = refusal(diagnostics)
                    result['labels'].update(dict.fromkeys(plan.outputs, f'refused at {mapping}'))
                else:
                    result['values'].update(outputs)
            return result
        # The canonical values that count: those an out-map or a bridge reads.
        counted = {s for m, c in out_maps for s in self.plan(m, target).required}
        counted |= {s for m, _, dst in bridges for s in self.plan(m, dst).required}
        middle, writer, upstream = {}, {}, {}  # upstream: canonical value -> the maps that refused it
        for mapping, canonical in in_hops:
            written, refused, _ = self.run(mapping, source, canonical, values, flags, partial=True)
            writer.update(dict.fromkeys(self.plan(mapping, canonical).outputs, mapping))
            middle.update(written)
            mine = {o: d for o, d in refused.items() if o in counted}
            if mine:
                result['refused'][mapping] = refusal(mine)
                upstream.update({o: {mapping} for o in mine})
        fills = {m: [s for s in self.plan(m, dst).required if s not in writer] for m, _, dst in bridges}
        for mapping, src, dst in bridges:
            fill = sorted(fills[mapping])
            written, refused, unavailable = self.run(mapping, src, dst, {**dict.fromkeys(fill, 0.0), **middle}, {},
                                                     partial=True)
            middle.update(written)
            mine = {o: d for o, d in refused.items() if o in counted}
            if mine:
                result['refused'][mapping] = refusal(mine)
                upstream.update({o: {mapping} for o in mine})
            for output, missing in unavailable.items():
                if all(s in upstream for s in missing):
                    upstream[output] = set().union(*(upstream[s] for s in missing))
            if fill and written:
                notes.append(ZERO_FILLED.format(mapping, ', '.join(s.rsplit('.', 1)[1] for s in fill)))
        for mapping, canonical in out_maps:
            written, refused, unavailable = self.run(mapping, canonical, target, middle, {}, partial=True)
            result['values'].update(written)
            if refused:
                result['refused'][mapping] = refusal(refused)
                result['labels'].update(dict.fromkeys(refused, f'refused at {mapping}'))
            for output, missing in unavailable.items():
                if all(s in upstream for s in missing):
                    label = f'refused upstream at {", ".join(sorted(set().union(*(upstream[s] for s in missing))))}'
                else:
                    label = NOT_AVAILABLE
                result['labels'][output] = label
        return result


def refusal(diagnostics) -> dict:
    """A refusal from sorted (code, ref) pairs, or from {output: pairs} for the outputs that partial evaluation
    refused (then it also lists those outputs)."""
    if isinstance(diagnostics, dict):
        pairs = [d for found in diagnostics.values() for d in found]
        return {**refusal(pairs), 'outputs': sorted(diagnostics)}
    return {'codes': sorted({code for code, _ in diagnostics}),
            'refs': sorted({ref.split('/', 3)[3] for _, ref in diagnostics if ref.count('/') >= 3})}


def changed(zero: dict, other: dict) -> set:
    """Outputs whose value differs, bit for bit, between two route results; written versus not counts too."""
    a, b = ({k: struct.pack('>d', v) for k, v in r['values'].items()} for r in (zero, other))
    return {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
