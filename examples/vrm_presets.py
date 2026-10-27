# SPDX-License-Identifier: MIT
"""VRM 1.0 expression presets -> morph target weights, for rendering translated VRM weights.

Follows the pinned VRMC_vrm-1.0 expressions.md (evidence id vrm_expressions):
an expression's value is clamped to [0, 1] (lines 132-135), isBinary turns a
value above 0.5 into 1 and anything else into 0 (line 123), and each
morphTargetBind adds value x bind weight to its node's morph target (binding
table, lines 286-292; update algorithm, lines 336-341). Overrides
(overrideBlink, overrideLookAt, overrideMouth) are out of scope: frames that
would need one are labelled instead. Material colour and texture binds are
not rendered.
"""
from __future__ import annotations


def presets(document: dict) -> dict[str, dict]:
    """The preset expressions of a VRM 1.0 glTF document, by name."""
    return dict(document['extensions']['VRMC_vrm']['expressions'].get('preset', {}))


def expression_value(expression: dict, value: float) -> float:
    value = min(max(value, 0.0), 1.0)
    if expression.get('isBinary'):
        value = 1.0 if value > 0.5 else 0.0
    return value


def morph_weights(expressions: dict[str, dict], values: dict[str, float]) -> tuple[dict[int, dict[int, float]], list[str]]:
    """{node: {morph index: weight}} for preset values, and labels for what is not rendered."""
    weights, labels = {}, []
    for name, value in values.items():
        expression = expressions.get(name)
        if expression is None:
            labels.append(f'{name}: this model has no such expression')
            continue
        value = expression_value(expression, value)
        if value == 0:
            continue
        overrides = [k for k in ('overrideBlink', 'overrideLookAt', 'overrideMouth')
                     if expression.get(k, 'none') != 'none']
        if overrides:
            labels.append(f'{name}: {", ".join(overrides)} not applied')
        if not expression.get('morphTargetBinds'):
            labels.append(f'{name}: no morph target binds on this model')
        for bind in expression.get('morphTargetBinds', []):
            node = weights.setdefault(bind['node'], {})
            node[bind['index']] = node.get(bind['index'], 0.0) + value * bind['weight']
    return weights, labels
