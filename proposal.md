# Authoring and mapping proposal

SPDX-License-Identifier: CC-BY-SA-4.0

## Wire contract

`pack.toml` holds the schema, data and operator versions, which change independently, and the pack's identity and license. The TOML fragments are read in sorted order and use only the shared `signals`, `profiles`, `mappings` and `evidence` arrays. A signal declares an ID that never changes, a label, scalar units and domain, an explicit calibration, a disposition, evidence and an evidence status. Its optional metadata records native fields. A profile lists signal IDs for typed virtual snapshots. Unknown wire keys are refused. Format-specific details go inside metadata.

A mapping (a rule in the schema) has `id`, `inputs`, `outputs`, `operator`, `disposition`, `mapping_quality` when mapped, optional coupling, assumptions, evidence, evidence status and loss annotations. Identity and affine take one input and give one output. A weighted sum takes ordered finite weights and gives one output. Survey strings are data. There is no hidden clamp, inverse, merge of left and right, or synthesized value.

The six shared APIs return a typed `Result(value, report)`, with no value when there are errors: `validate_authoring(document)`, `compile_pack(validated_authoring)`, `inspect_asset(bytes, format, resolver=None, sidecar=None)`, `compile_mapping(pack, source_snapshot, target_snapshot, mapping_id, allow_approximation=False)`, `evaluate_mapping(compiled_mapping, samples)`, and `annotate_asset(snapshot, annotations)`. The shared helpers `load_authoring` and `profile_snapshot` supply the pack inputs and the virtual channels.

## Executable examples

`arkit_blink.to_rcef` carries Apple's two blink coefficients into the canonical expression set unchanged, with an affine scale of 1. The calibration changes from the ARKit basis to the canonical one, so the mapping is approximate and declares the loss. `vrcft_eye_blink.to_rcef` computes canonical eye closure as `1 − Openness`.

`fixture.affine` applies `0.5*x + 0.5` to an original signed basis: `-1 → 0`, `0 → 0.5`, `1 → 1`. This is an explicit basis conversion, with no hidden clamp.

`fixture.bilateral` averages original left and right brow channels with weights `[0.5, 0.5]`. Both `[1,0]` and `[0,1]` give `0.5`, so the difference between the sides cannot be recovered. Its signal loss is approximate, its effect on geometry is unknown, and it compiles only with the approximation opt-in. `survey.ambiguous` is an unresolved candidate from MediaPipe to the canonical expression set. It cannot be compiled for evaluation.

A sample has a timestamp in seconds, typed values by signal ID, and validity by signal ID. A missing or invalid required input gives errors and no evaluated value. Domains are checked before and after each operator. Profile snapshots do not bind to physical assets. To use a mapping with an asset, a sidecar must give structural indices and the asset and resource hashes.

## Release limits and remaining evidence

Full parity of the selected inventories is a data gate. It does not depend on cross-provider calibration. Device availability, geometry equivalence, execution of VRM bindings, Roblox compliance, native kernels and host integration each need their own measured acceptance. This proposal establishes no formal standards adoption and no visual accuracy.

Evidence still missing: MediaPipe model calibration and provenance, FB1 numeric bounds, FB2 maximum angles per direction, VRCFT raw gaze units and source contradictions, which Roblox list of required poses is authoritative, and permission to redistribute VRM specification prose. These gaps are recorded in machine-readable form, and they block the derived mappings that depend on them. The VRM references are links; the source prose and figures are not redistributed.
