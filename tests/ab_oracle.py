# SPDX-License-Identifier: MIT
"""A pure-Python oracle (O) for msf-character-tools 0.5.0 map evaluation, and for routes made of such maps.

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

A3, the A/B harness and the oracle's own test use it to give expected values
and refusal codes before any registered run of the pivot route (ab/README.md).
"""
from __future__ import annotations
import bisect
from dataclasses import dataclass
import math
import struct


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

    def valid(self, sid: str, flags: dict) -> bool:
        validity = self.signals[sid].get('validity')
        return all(flags[name.strip()] for name in validity.split(' AND ')) if validity else True

    def run(self, mapping: str, source: str, target: str, values: dict, flags: dict):
        """One map on one frame, given only its own required inputs that the frame holds (as Route sends them)."""
        given = [s for s in self.plan(mapping, target).required if s in values]
        return self.frame(mapping, source, target, {s: values[s] for s in given},
                          {s: self.valid(s, flags) for s in given})

    def route(self, source: str, target: str, in_hops: list, out_maps: list, values: dict, flags: dict) -> dict:
        """The expected result of a route on one frame.

        in_hops lists (in-map, canonical profile); out_maps lists (out-map,
        canonical profile). With no in-hops the out-maps read the source frame
        (one-hop mode). The result holds values, refusal codes by map and
        labels of outputs not written, as rcef_route.Route gives them.
        """
        result = {'values': {}, 'refused': {}, 'labels': {}}
        middle, writer = (dict(values), {}) if not in_hops else ({}, {})
        for mapping, canonical in in_hops:
            outputs, diagnostics = self.run(mapping, source, canonical, values, flags)
            writer.update(dict.fromkeys(self.plan(mapping, canonical).outputs, mapping))
            if outputs is None:
                result['refused'][mapping] = sorted({code for code, _ in diagnostics})
            else:
                middle.update(outputs)
        for mapping, canonical in out_maps:
            plan = self.plan(mapping, target)
            missing = [s for s in plan.required if s not in middle]
            if in_hops and missing:
                if any(s not in writer for s in missing):
                    label = 'not available from source'
                else:
                    label = f'refused upstream at {", ".join(sorted({writer[s] for s in missing}))}'
                result['labels'].update(dict.fromkeys(plan.outputs, label))
                continue
            outputs, diagnostics = self.run(mapping, canonical if in_hops else source, target, middle,
                                            {} if in_hops else flags)
            if outputs is None:
                result['refused'][mapping] = sorted({code for code, _ in diagnostics})
                result['labels'].update(dict.fromkeys(plan.outputs, f'refused at {mapping}'))
            else:
                result['values'].update(outputs)
        return result


def changed(zero: dict, other: dict) -> set:
    """Outputs whose value differs, bit for bit, between two route results; written versus not counts too."""
    a, b = ({k: struct.pack('>d', v) for k, v in r['values'].items()} for r in (zero, other))
    return {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
