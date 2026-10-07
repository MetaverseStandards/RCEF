# Authoring and mapping proposal

SPDX-License-Identifier: CC-BY-SA-4.0

## Wire contract

`pack.toml` carries independent schema/data/operator versions and pack identity/license. Sorted TOML fragments use only the shared `signals`, `profiles`, `mappings`, and `evidence` arrays. Signals declare immutable IDs, labels, scalar units/domains, explicit calibration, disposition, evidence and status; optional metadata inventories native fields. Profiles list IDs for typed virtual snapshots. Unknown wire keys are rejected; format-specific details belong inside metadata.

Rules use `id`, `inputs`, `outputs`, `operator`, `disposition`, mapped `mapping_quality`, optional coupling, assumptions, evidence/status and loss annotations. Unary identity/affine use one input/output. Weighted sums use ordered finite weights and one output. Survey strings are data. There is no implicit clamp, inverse, bilateral merge or synthesis.

The six shared APIs return typed `Result(value, report)` with no value on errors: `validate_authoring(document)`, `compile_pack(validated_authoring)`, `inspect_asset(bytes, format, resolver=None, sidecar=None)`, `compile_mapping(pack, source_snapshot, target_snapshot, mapping_id, allow_approximation=False)`, `evaluate_mapping(compiled_mapping, samples)`, and `annotate_asset(snapshot, annotations)`. The shared `load_authoring` and `profile_snapshot` helpers supply pack inputs and virtual channels.

## Executable examples

`arkit.to_canonical` preserves nine Apple-native coefficients. `fb2.to_canonical` preserves eight FB2 direction-specific eye rotation fractions. `vrcft_eye.to_canonical` preserves left/right raw openness and pupil diameter. Each target calibration explicitly matches its input provider basis; the target IDs include that provider scope.

`fixture.affine` applies `0.5*x + 0.5` to an original signed basis: `-1 → 0`, `0 → 0.5`, `1 → 1`. This is an explicit basis conversion with no implicit clamp.

`fixture.bilateral` averages original left/right brow channels with weights `[0.5, 0.5]`. Both `[1,0]` and `[0,1]` yield `0.5`: side asymmetry is irrecoverable. Its signal loss is approximate, geometry effect unknown, and compilation requires approximation opt-in. `survey.ambiguous` is an unresolved MediaPipe-to-Apple candidate that cannot compile for evaluation.

Samples carry seconds timestamps, typed values by signal ID, and validity by ID. Missing or invalid required input yields errors and no evaluated value. Domains are checked before and after operators. Profile snapshots do not establish physical asset bindings: reuse against assets requires structural indices and asset/resource hashes in sidecars.

## Release limits and remaining evidence

Full selected inventory parity is a data gate, independent of cross-provider calibration. Device availability, geometry equivalence, VRM binding execution, Roblox compliance, native kernels and host integration require separate measured acceptance. No formal standards adoption or visual accuracy is established here.

Remaining evidence: MediaPipe model calibration/provenance, FB1 numeric bounds, FB2 directional maximum angles, VRCFT raw gaze units and source contradictions, Roblox required-pose authority, and permission for redistributing VRM specification prose. These gaps remain machine-readable and block the affected derived executions. VRM references are linked; source prose and figures are not redistributed.
