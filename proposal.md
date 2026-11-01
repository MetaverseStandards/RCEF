<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Reference Canonical Expression Framework proposal

| Item | Value |
|---|---|
| Submitted to | Metaverse Standards Forum |
| Submitted by | RCEF contributors |
| Date | 2026-10-31 |
| Status | Draft for review. The canonical sets and `facs.code` are drafts. |
| Data version | 0.5.0, a release candidate. Only the project's release owners tag a release. |
| Checked with | msf-character-tools 0.6.0, locked in [evidence/tooling.lock.json](evidence/tooling.lock.json) |
| Licences | Data and documentation CC-BY-SA-4.0; code MIT ([LICENSE](LICENSE)) |

Every number in this proposal comes from the data of this repository. The main sources are `generated/rcef.pack.json`, the [reports](reports/), the [definitions audit](docs/canonical-set-audit.md) and the [A/B results](ab/README.md).

## Summary

Face trackers and avatar systems each publish their own set of face expression signals. The names, value ranges, sides and calibrations are different in each system. So you cannot copy a value from one system into another without a stated rule.

The Reference Canonical Expression Framework (RCEF) records public expression interfaces as data. It covers seven providers (Apple ARKit, OpenXR, MediaPipe, VRCFaceTracking, Godot, VRM and Roblox) and a public list of FACS code numbers. Each provider fact cites a pinned public source with a SHA-256 digest.

RCEF defines two draft canonical sets: an expression set of 72 signals and a viseme set of 16 signals. A translation runs from a source set, through a canonical set, to a target set. A map is a set of one-way scalar mappings, and each mapping states its assumptions and its losses. Each map in a route is one hop.

Data 0.5.0 holds 1165 signals in 26 profiles, 588 mappings in 19 maps and 81 evidence records. Of the 19 maps, 3 are test and record maps. The other 16 maps translate 37 pairs of source set and target set. On the 5 pairs that the retired direct maps translated, the routes give the same weights on every output that both write. A registered A/B comparison shows this. 28 of the 37 pairs have no external reference.

The current data has these limits. The canonical sets are drafts that the working group has not reviewed. All cross-provider mappings are proposed approximations: only the 4 pupil copies are exact. RCEF does not claim visual equivalence, a measured gain or tracker accuracy. The gain of a signal is how far the face moves for a given value.

This proposal asks the Forum for seven actions. The first is a review of the meaning of the draft sets. [Requests to the Forum](#requests-to-the-forum) gives the full list.

## Problem

### Why expression values cannot be copied

Two systems can use similar names for different quantities. A value of 0.5 in one system does not mean 0.5 in another. This table shows the differences that the survey found. Where a row names an evidence record, that record supports the row.

| Difference | Example from the data |
|---|---|
| Names | The left eye closure is `eyeBlinkLeft` in ARKit, `XR_FACE_EXPRESSION2_EYES_CLOSED_L_FB` in FB2 and `EyeClosedLeft` in VRCFaceTracking Unified Expressions. |
| Direction of the value | VRCFaceTracking reports eye openness. ARKit, FB2 and VRM report eye closure. The canonical eye closure is 1 minus `Openness`. |
| Side split | ARKit has one `browInnerUp`. FB2 has a left and a right inner brow raiser. Toward ARKit, the two sides become their mean, and the difference is lost. |
| Basis of gaze | ARKit eye-look coefficients describe eyelid movement (record `apple_blendshapes`). FB2 gives fractions of a maximum angle that it does not specify (record `xr_fb2`). VRM drives gaze by angles in degrees (record `vrm_lookat`). |
| Gain | No provider publishes its gain. No source shows that a full activation in one system equals a full activation in another. |
| Units | The VRCFaceTracking raw pupil fields hold millimetres. A combined field with the same name holds a normalized dilation (record `vrcft_data`). |
| Value contract | A valid META viseme frame sums to 1. VRM vowel presets are weights that each model author sets, with no sum (records `xr_visemes`, `vrm_expressions`). |
| Validity | FB2 gaze is valid only when `isValid` and `isEyeFollowingBlendshapesValid` are both true. An invalid META frame is all zeros, which is different from valid silence. |
| Coverage | MediaPipe has no `tongueOut`. FACS has no code for a sideways mouth shift. OpenXR `XR_ML_facial_expression` has no cheek puff. |
| Contradictions | Two Roblox documents at the same revision each list 17 required poses, and the lists differ. Some VRCFaceTracking names conflict with their own direction wording. |

So a name match is not enough to copy a value. CONTRIBUTING.md states the rule: names alone do not justify a cross-provider identity. A translation needs an explicit operator, its assumptions and its losses.

### Points that are specific to the metaverse

Metaverse platforms use these signals in ways that make the problem larger. This table gives each case.

| Situation | What a translation must do | What RCEF does |
|---|---|---|
| Live tracking into avatars: a tracker sends values frame by frame, and the avatar shows them as they arrive. | Keep the rest of the face when one channel is invalid. | Partial evaluation refuses only the outputs that read a bad input. |
| Mixed trackers and avatars: an avatar made for one expression set meets a tracker that reports another set. | Translate each pair of sets, for example FB2 to Unified Expressions. | Routes through a canonical set join 37 pairs of sets. |
| Speech without a face tracker: a runtime drives the mouth from visemes. | Turn viseme classes into face shapes. | The viseme pose bridge lets META visemes and VRM vowels drive ARKit, FB2 and Unified Expressions faces. It covers 11 of 15 classes, with poses fitted to Rocketbox rigs. |
| Partial loss of tracking: eye tracking stops while face tracking continues. | Keep the face values and refuse only the gaze values. | FB2 has a separate validity flag for eye following, and the FB2 in-map refuses only its 8 gaze outputs. |
| Avatars that move between platforms. | Tell the receiving platform what the translation did not carry. | Each frame lists the dropped inputs. Each output that a route does not write has a label with the cause. |
| Provenance and licences. | Show where each fact comes from and under what terms. | Each provider fact cites a pinned source. RCEF does not copy provider prose that has no open licence. |

## Technical foundation

### What the survey found

RCEF selected the public inventories in this table. The numbers describe interfaces. They do not say how well a tracker follows a face. [survey.md](survey.md) gives the limits of each surface, and [docs/expression-sets.md](docs/expression-sets.md) gives each pinned source and licence.

| Provider | Selected inventory | Role in the maps of data 0.5.0 |
|---|---|---|
| Apple ARKit | 52 coefficients | Source and target |
| OpenXR FB2 (`XR_FB_face_tracking2`) | 70 weights | Source and target |
| OpenXR FB (`XR_FB_face_tracking`) | 63 weights | Inventory only |
| OpenXR META visemes | 15 classes | Source and target |
| MediaPipe | 52 labels | Inventory only |
| VRCFaceTracking | Transport 88; raw and combined eye data; artist shapes 102 base and 42 blended; 124 listed numeric avatar parameters; 3 activity flags | Eye data: source and target. Unified Expressions base shapes: target only |
| Godot | 102 base and 41 blended shapes | Inventory only |
| VRM 1.0 | 18 presets | Blinks and vowels: source and target |
| Roblox | 50 face controls | Inventory only |
| FACS | 92 rows for 70 code numbers from a public list, in RCEF's own numeric encoding | Source and target (49 rows mapped) |

The survey gives these results:

- Most of the inventory is not translated yet. The 19 profiles of public sets and `facs.code` hold 1011 signals. Of these, 269 are mapped, 682 unresolved, 54 excluded and 6 unsupported.
- Similar names often define different actions. The definitions audit has 339 rows, and 315 of them compare a canonical signal with the definition of a source that maps it. Of all 339 rows, 258 are `same`, 68 `differs` and 13 `unresolved`. For ARKit, 22 of 60 rows differ. [Appendix B](#definitions-audit) gives the rows of each source.
- Calibration is not published. No provider publishes its gain. FB2 does not give its maximum gaze angles. The MediaPipe model calibration is not stated in the reviewed sources.
- The sources contradict themselves in places. RCEF keeps each contradiction as unresolved data. It does not choose one reading by guessing.
- The same name renders differently on different rigs. In the calibration record `rig-gains.ict-rocketbox-female`, only 3 of 51 ARKit shapes render with matching strength on two example rigs.
- Some interfaces state values that a scalar map cannot hold. VRM binds expressions to morphs, materials and textures, with binary thresholds. VRCFaceTracking computes combined eye data with state. RCEF records these facts and does not execute them.

### Why direct maps do not scale

Before data 0.5.0, RCEF mapped one provider straight to another. Seven direct maps covered 5 pairs of source set and target set. They had 187 cross-provider mappings and 4 internal gaze steps. Each internal step was a weighted sum that wrote a helper value: the difference of two opposite gaze directions. Each new pair needed a new map. Where no map existed, the only route was two direct maps in turn.

A direct design needs one map for each ordered pair of sets. With N sets, that is N × (N − 1) maps. A pivot design needs at most two maps for each set: one into the canonical set and one out of it. That is at most 2 × N maps.

| Expression sets | Direct maps, N × (N − 1) | Pivot maps, at most 2 × N |
|---:|---:|---:|
| 4 | 12 | 8 |
| 7 | 42 | 14 |
| 10 | 90 | 20 |
| 20 | 380 | 40 |

Data 0.5.0 translates 37 pairs: 31 pairs of different sets and 6 round trips. A direct design needs 31 maps for the 31 pairs of different sets. RCEF uses 15 maps into and out of the canonical sets, and the viseme pose bridge.

The pivot has other effects:

- RCEF audits the meaning of each set once, against the canonical set. It does not audit each pair again.
- Each hop states its own assumptions and losses. A route shows the assumptions and losses of each of its hops.
- A new set adds one in-map, one out-map or both. It then has routes to every set that fills at least one of its canonical groups. The existing maps do not change.

The pivot also has costs, and RCEF states them:

- A route has two hops, or three through the viseme pose bridge, and each hop is a proposed approximation.
- Before data 0.5.0, a 21-signal set, `rcef.canonical`, copied 21 provider values exactly. Now each canonical signal has a meaning that RCEF declares, and it is not the provider's meaning. So 19 of those copies are now proposed approximations. Only the copies of the 2 pupil diameters stay exact.
- A route writes only the groups that both sets fill. A quantity that the canonical set does not hold cannot pass through it. For example, the Unified Expressions part shapes with no FB2 counterpart have no map yet.

### The A/B result

RCEF registered a comparison of the pivot routes with the retired direct maps before it retired them. Before each run, RCEF commits the method and the pass limits in a registration and a ledger line. The limits do not change after that. A gate is one check of a registration with its pass limit. [ab/README.md](ab/README.md) gives the method.

An arm is one way to compute the target values from the same source frames. The comparison has these arms:

| Arm | What it runs |
|---|---|
| A1 | The retired direct maps, from a frozen baseline pack with a pinned SHA-256 |
| A2 | Two direct maps in turn, where no direct map exists |
| A3 | The AU table of an expression library, for FACS to FB2 |
| B | The pivot routes through the canonical sets |
| O | An oracle: a separate pure-Python copy of the map evaluation, on the maps of B |

Four registered runs have passed every gate. The latest run, `ab.pivot` v4, gives these results:

- B gives the same values as the oracle on all 272,872 frames of all 37 pairs, with no difference.
- On the 5 pairs that the direct maps translated, B gives the same value as A1 on every output that both write. The run compares 1,858,422 output values, and none differs in value or in the sign of zero.
- An exact rational composition of the B hops equals A1 on every linear A1 output.
- 129 of 129 goldens come through B exactly. A golden is an expected output that a script derives from a public source, without reading RCEF's maps.

A separate comparison checks FB2 to ARKit against the routes in Godot's public sources. RCEF translates 52 ARKit coefficients from FB2, with 0 weight disagreements and 1 coefficient that Godot does not route ([docs/godot_comparison.md](docs/godot_comparison.md)).

These results show that the pivot keeps the arithmetic of the retired maps. They do not show that the maps are correct, because the retired maps were proposed approximations too. Of the 37 pairs, 28 have no external reference: only B and the oracle run them. [docs/ab-coverage.svg](docs/ab-coverage.svg) shows the reference for each pair.

## Architecture

RCEF is data. msf-character-tools is a separate project. It reads the data, checks it, builds the pack and runs the maps. `check.py` first checks that msf-character-tools is a locked release, and the tests check the outputs against the data ([Appendix A](#check-tooling-and-the-lock)). [docs/architecture.md](docs/architecture.md) gives the full design.

| Part | What it holds | Where |
|---|---|---|
| Expression sets | One profile per public set, with its signals | `profiles/` |
| Canonical sets | The draft canonical expression and viseme sets, and helper values | `data/` |
| Maps | One-way mappings with operators, assumptions, evidence and losses | `mappings/` |
| Evidence | Pinned public sources and original records | `evidence/sources.toml` |
| Calibration records | Software-only fits with a freeze ledger | `calibration/` |
| Generated outputs | The pack, a matrix, coverage, readable reports and checksums | `generated/`, `reports/` |
| Checks | `check.py`, the tests and the source scripts | `check.py`, `tests/`, `scripts/` |

### Expression sets as data

Each public set is one TOML file in `profiles/`. A signal record gives the ID, label, units, domain, calibration, side, disposition, evidence and evidence status. The field `native_id` keeps the native name. The metadata keeps the native index and the reason for the disposition. A profile lists the IDs of its signals in order.

The data separates facts that are easy to confuse. A native default is the value that storage starts with. A neutral value is a stated calibrated reference. Validity is a flag that the caller supplies for each frame. RCEF never uses a default or a neutral as a replacement for a missing value.

`check.py --write` merges all TOML files into one JSON pack, `generated/rcef.pack.json`, and writes its SHA-256. The readable reports in `reports/` list every signal, every mapping and the canonical correspondence. The same TOML files give the same bytes on Python 3.11 and 3.12.

### The two draft canonical sets

The canonical expression set, `rcef.canonical_expression`, has 72 signals in 13 groups. A group is a set of canonical signals that a source fills together. [docs/canonical-set.md](docs/canonical-set.md) defines each signal, and the [definitions audit](docs/canonical-set-audit.md) compares it with each source.

| Group | Signals | Group | Signals |
|---|---:|---|---:|
| `face` | 41 | `gaze` | 8 |
| `cheek_puff` | 2 | `tongue_out` | 1 |
| `jaw_thrust` | 1 | `cheek_suck` | 2 |
| `jaw_sideways` | 2 | `lip_tighten` | 2 |
| `mouth_shift` | 2 | `tongue_place` | 6 |
| `chin_raise_upper_lip` | 1 | `pupil_mm` | 2 |
| `blink` | 2 | | |

For an expression signal, 0 is the neutral face and 1 is full activation of the action that RCEF defines. RCEF assumes that each source agrees with the canonical set at 0 and at 1. Every in-map and out-map states this assumption. No measurement supports it. A gaze signal is a fraction of the source's maximum gaze in one direction, with no angle claimed. The two pupil signals are diameters in millimetres.

The canonical viseme set, `rcef.canonical_viseme`, has 16 signals. 15 are partition classes: 5 vowel classes, 9 consonant classes and the rest class `sil`. Each of the 107 symbols of the IPA chart is in exactly one class. From a valid META frame, the 15 class values sum to 1. The 16th signal, `alveolar_floor`, is the sum of the three alveolar classes and `rhotic`, clamped at 1.

The FACS codes are an expression set of their own, `facs.code` (draft). It has 92 rows: 49 mapped, 25 unresolved and 18 excluded. Its values are RCEF's own numeric encoding of the FACS intensity letters ([docs/facs-intensity.md](docs/facs-intensity.md)). They are not FACS scores, and RCEF does not code faces.

### Maps, mappings and parts

A mapping is one rule, in one direction, from its inputs to one output. A map is a set of mappings that turns the values of one set into the values of another. RCEF has at most one map for each pair of an expression set and a canonical set, in each direction. Its ID has the form `<from>.to_<to>`, for example `fb2.to_rcef_expression`.

A part of a map is its mappings for one canonical group. A source fills a whole group or none of it. Each map has a page in [docs/map-sets/](docs/map-sets/) that shows its parts, and the groups that it does not have, with the reason.

| Map | Mappings | Parts | Map | Mappings | Parts |
|---|---:|---:|---|---:|---:|
| `arkit.to_rcef_expression` | 60 | 9 | `rcef_expression.to_arkit` | 52 | 9 |
| `facs.to_rcef_expression` | 53 | 8 | `rcef_expression.to_facs` | 49 | 8 |
| `fb2.to_rcef_expression` | 70 | 12 | `rcef_expression.to_fb2` | 74 | 12 |
| `vrcft_eye.to_rcef_expression` | 4 | 2 | `rcef_expression.to_vrcft_eye` | 4 | 2 |
| `vrm.to_rcef_expression` | 2 | 1 | `rcef_expression.to_vrm` | 2 | 1 |
| | | | `rcef_expression.to_vrcft_artist` | 72 | 11 |
| `visemes.to_rcef_viseme` | 17 | 4 | `rcef_viseme.to_visemes` | 15 | 3 |
| `vrm.to_rcef_viseme` | 5 | 1 | `rcef_viseme.to_vrm` | 5 | 1 |
| `rcef_viseme.to_rcef_expression` (the bridge) | 101 | 7 | | | |

The 15 maps into and out of the two canonical sets hold 484 mappings, and the bridge holds 101 more. Three more maps are tests and records: `fixture.affine`, `fixture.bilateral` and `survey.ambiguous`.

### Routes

A route runs from a source set through a canonical set to a target set. [examples/rcef_route.py](examples/rcef_route.py) finds the maps of each route in the pack by the profiles of their signals. It does not use the map names.

A route writes only the target signals of the groups that both sets fill. It labels each other output "not available from source". A target can be the source set itself, which gives a round trip. The README's [Routes](README.md#routes) table lists all 37 pairs, and [docs/routes.svg](docs/routes.svg) shows which groups each set fills.

| Source sets | Through | Target sets |
|---|---|---|
| ARKit, FB2, FACS codes, VRCFaceTracking eye data, VRM blinks | Canonical expression set | ARKit, FB2, FACS codes, Unified Expressions, VRCFaceTracking eye data, VRM blinks |
| META visemes, VRM vowels | Canonical viseme set | META visemes, VRM vowels |
| META visemes, VRM vowels | Canonical viseme set, viseme pose bridge, canonical expression set | ARKit, FB2, FACS codes, Unified Expressions |

### The viseme pose bridge

The bridge `rcef_viseme.to_rcef_expression` writes canonical expression values from canonical viseme values. For each expression signal j, it computes the sum of pose[c][j] × viseme_c over the classes c, clamped to the range 0 to 1. Here pose[c][j] is the value that class c at weight 1 gives to signal j.

The poses come from the calibration record `viseme-poses.rocketbox-features`. The fit uses the viseme shapes of 18 Rocketbox rigs, measured in their own ARKit shapes, with each left and right pair tied. RCEF tests each fit on held-out rigs, which are rigs that the fit did not use. This fit has four held-out rigs. A class passes by its whole-face shape or by a perceptual gate of visible mouth features.

11 of the 15 classes pass on all 4 held-out rigs: 7 by their shape and 4 by the perceptual gate. The bridge reads only those 11 classes. `labiodental`, `postalveolar`, `coronal_nasal_lateral` and `rhotic` fail, and they move nothing.

The bridge writes the 45 signals of the groups `face`, `cheek_puff`, `jaw_thrust` and `chin_raise_upper_lip`. It has 101 mappings and uses 56 helper values in `rcef.intermediate`. It does not write blink, gaze or tongue values.

The bridge has these limits:

- The poses come from one rig library. On ICT-FaceKit, the bridged `bilabial` pose opens the lips by about 2.3 mm instead of keeping them closed.
- The perceptual tolerances come from the spread of the library's own shapes. No viewer judged them.
- Each class is one static pose. The bridge does not model how sounds affect their neighbours.
- The fit is software-only. It says nothing about a tracker or a real face.

There is no map from expressions back to visemes. A face pose does not identify the sound.

### Calibration records

A calibration record is a software-only fit to renders or mesh geometry of example rigs. It is not a measurement of a tracker. [calibration/README.md](calibration/README.md) gives the format. The repository has five records:

| Record | Result on held-out data | Used by a mapping |
|---|---|---|
| `mediapipe.ict-response` | A fit was possible for 25 of 51 MediaPipe scores. None passed. | No |
| `rig-gains.ict-rocketbox-female` | 3 of 51 ARKit shapes pass | No |
| `viseme-poses.rocketbox-female` | 9 of 15 classes pass on one held-out rig | No, kept as history |
| `viseme-poses.rocketbox-multi` | 7 of 15 classes pass (version with tied sides) | No, kept as history |
| `viseme-poses.rocketbox-features` | 11 of 15 classes pass on 4 held-out rigs | Yes, the 45 weighted sums of the bridge |

RCEF hashes the frozen part of a record. The hash goes into the append-only `FREEZES` ledger before the held-out run. The held-out seeds come from that hash. `check.py` refuses a mapping that cites a record unless its values are exactly the frozen values. Each channel that the mapping reads must also pass all its held-out cells: its shape cells, or the cells of its perceptual gate.

The status of a record is `calibrated_software`. Pack schema 1.0 does not have this value. So the mappings that cite a record are `proposed`, and their assumptions say why.

### Assumptions and loss annotations

Every mapping lists its assumptions as text. Each output mapping of an in-map or out-map has a standard assumption: the provider's 0 and 1 are canonical 0 and 1. No evidence and no measured response curve support this assumption. The FACS maps use their own form of this assumption, based on the intensity letters. The assumption ends with a clause for the operator, for example "the ARKit value is the mean of the canonical parts". The bridge states its own assumptions about the poses.

A loss annotation records what a mapping does not carry. It has a category, an effect, a reason and the signals that it refers to. The pack holds 1248 loss annotations: 1247 approximated signal losses and 1 unknown geometry loss from `fixture.bilateral`. Where the audit marks a row `differs` or `unresolved`, the assumption of each mapping names a stable loss key from the audit, for example `vrm_blink_side_unresolved`.

## What each audience gets

These are the effects of the current data. They are not promises about later data.

### Content creators

- An avatar author can see, for each group of the canonical set, which trackers can drive the shapes of the avatar. The map pages give the reason for each group that a set does not fill.
- An author can make shapes for one set, for example the 52 ARKit coefficients. RCEF routes FB2, FACS codes, VRCFaceTracking eye data and VRM blinks to those shapes. It routes META visemes and VRM vowels to them through the bridge.
- Each empty output has a label that gives the cause: "not available from source" or "refused upstream at" a named map. Each frame lists its dropped inputs.
- The losses are visible before use. For example, toward ARKit the left and right inner brow become one mean value.
- A FACS user can turn FACS notation into `facs.code` values with `examples/facs_codec.py`. The values encode the intensity letters. They are not FACS scores.

### Avatar and engine developers

- A developer loads one file, `generated/rcef.pack.json`, and checks it with its SHA-256. The same shared APIs run every map, so there is no code for each pair.
- A new set gives routes to every set that fills at least one of its groups.
- The arithmetic uses checked binary64 steps, the 64-bit floating-point numbers of IEEE 754. It has no hidden clamp, hidden state or smoothing. The same inputs give the same outputs on Python 3.11 and 3.12.
- Partial evaluation keeps the face when one part of the input fails. For example, when FB2 loses eye following, the FB2 in-map refuses only its 8 gaze outputs.
- `examples/` holds complete runs from CSV frames to translated weights, and onto face meshes.

### Tracker and runtime vendors

- RCEF records the published interface of a vendor with its native names, indices, ranges and validity contract. Each fact has a pinned source and a locator.
- RCEF records contradictions and gaps in the sources as unresolved data. A vendor can resolve one by publishing a source that RCEF can cite.
- Published facts that RCEF does not have yet would let it state more exact mappings. Examples are the FB2 maximum gaze angles and the MediaPipe model calibration.
- A new interface joins with one in-map and, if needed, one out-map. For example, the planned set OpenXR `XR_ANDROID_face_tracking` has 68 names, and 64 of them are FB2 names.

### Standards bodies

- RCEF is a pivot. It does not ask any provider to change its interface or adopt a new one.
- The definitions audit has 315 rows that compare canonical signals with source definitions. Each row cites a record and a locator. This is a base for a review of meaning.
- The governance rules keep IDs stable. An ID stays the same when its label changes, and a change of meaning needs a new ID. A retired ID gets a tombstone: a line in [docs/retired-ids.csv](docs/retired-ids.csv) that records the retirement. Until a draft vocabulary is first accepted or released, its IDs can change without a tombstone ([GOVERNANCE.md](GOVERNANCE.md)).
- The A/B ledger and the calibration ledger record each test before its run. A reviewer can check the order of the commits.
- RCSF, the Reference Canonical Skeletal Framework, does a similar job for skeletons in the same Forum organization ([references.md](references.md#rcsf_readme)).

## Scope and limits

### In scope

- Scalar face expression signals that a public interface publishes, with their names, indices, domains, calibrations and validity contracts.
- One-way scalar mappings into and out of the two draft canonical sets, with four operators.
- Software-only calibration records, with a freeze ledger and held-out results.
- Checks that the data, the generated files and the documentation tables agree.

### Out of scope

- A new universal blendshape set. "Canonical" does not mean one universal anatomy or one shared calibration.
- Any claim of visual equivalence. The cross-provider mappings are proposed approximations.
- The look of a stylized character. RCEF describes what a signal means. Stylization is a separate layer.
- Translations that need state, time or classification. Examples are VRM emotion presets, the combined VRCFaceTracking eye data and the effect of neighbouring sounds on a viseme.
- Geometry. RCEF does not make or deform meshes. msf-character-tools has its own geometry scope.

### Not translated yet

The README lists each translation that is [not translated yet](README.md#not-translated-yet-planned) or [out of scope](README.md#out-of-scope), with the reason.

## Requests to the Forum

Each request comes from an open item in the [README](README.md#open-questions), [GOVERNANCE.md](GOVERNANCE.md) or the [canonical set](docs/canonical-set.md#open-questions).

1. Review the meaning of the draft sets. This covers the canonical expression set, the canonical viseme set and `facs.code`. Name the reviewers of meaning. State how long the review takes. Acceptance changes only `vocabulary_status` from `draft` to `accepted`. It does not change IDs, calibration strings or maps.
2. Answer the open questions of definition. The canonical set lists them. Examples are the side shown by the FB2 and Unified Expressions sideways jaw figures, and the direction of Unified Expressions `MouthLowerDown`. Another is whose left the FACS L and R modifiers mean.
3. Help find the missing evidence. RCEF has no evidence yet for the items in [Release limits and remaining evidence](#release-limits-and-remaining-evidence). Members that publish these interfaces can supply a citable source.
4. Decide on physical calibration. [docs/calibration/physical-protocol.md](docs/calibration/physical-protocol.md) designs a capture with real trackers and real faces. Nobody has run it. Before any part of it runs, it needs a named owner, an ethics and legal review, and approval from the project's release owners.
5. Set the order of new expression sets. [docs/expression-sets.md](docs/expression-sets.md#planned-expression-sets) lists the planned sets and their phases. Each new set needs a pinned public source and a known licence.
6. Review the release gates. GOVERNANCE.md lists what a data release needs. Device support, rig deformation, VRM composition, Roblox certification and standards adoption each need their own measured acceptance.
7. Agree conventions with RCSF. RCEF departs from two RCSF conventions ([docs/canonical-set.md](docs/canonical-set.md#format-neutrality)). It uses snake_case IDs, because the providers use different letter cases and snake_case favours none of them. For a missing value, RCEF shows one of three markers in place of "-": `unsupported`, `unresolved` or `excluded`. A "-" cannot say why a value is missing ([No equivalent](docs/canonical-set.md#no-equivalent)). RCEF asks the RCSF maintainers to agree on these conventions.

To reply, open an issue in the RCEF repository or raise the point in the Forum's 3D Assets working group ([GOVERNANCE.md](GOVERNANCE.md)).

---

# Appendix A: Technical specification

This appendix gives the contract between the RCEF data and msf-character-tools 0.6.0. [docs/architecture.md](docs/architecture.md) gives the same rules with more examples.

## Wire contract

`pack.toml` holds five keys and no others:

```toml
schema_version = "1.0"
data_version = "0.5.0"
operator_version = "1.1"
id = "rcef.parity"
license = "CC-BY-SA-4.0"
```

The schema, data and operator versions change independently. msf-character-tools 0.6.0 accepts schema versions 1.0 and 1.1, and operator versions 1.0 and 1.1. Operators 1.1 add `piecewise_linear`. `data_version` must be a semantic version.

Discovery reads every file whose name ends in lowercase `.toml`, in sorted path order. It skips names that begin with `.` and directories named `generated`. It refuses symbolic links, paths that differ only in letter case, and reserved file names. For this reason, calibration records use the extension `.cal`.

Each file can add records to four top-level arrays: `signals`, `profiles`, `mappings` and `evidence`. Folder names do not choose a schema. The arrays keep their file order and their authored order.

These rules apply to every file:

- Parsing is strict UTF-8. msf-character-tools refuses syntax errors and duplicate keys before the schema checks.
- msf-character-tools refuses unknown keys. Format-specific details go inside `metadata`, which the pipeline never executes.
- IDs are non-blank, case-sensitive strings. They are not trimmed or normalized. Mapping IDs are unique across all maps.
- Every reference must name an existing record. A label, native ID, region or side is not a reference.
- Numbers must be finite. msf-character-tools refuses NaN, infinity and booleans as scalars. It refuses TOML dates as values.
- The pipeline never executes text from TOML. It does not infer a conversion from a provider name.

## Signal and profile fields

| Field | Rule |
|---|---|
| `id`, `label` | Required and non-blank. The ID never changes. |
| `value_type` | Required. Only `"scalar"`. |
| `units`, `calibration` | Required non-blank strings. Units `"unknown"` keep the uncertainty visible. A calibration string is a declaration, not a measurement procedure. |
| `domain` | Required object with optional finite `min` and `max`. `{}` declares no bounds. |
| `disposition` | Required: `mapped`, `unsupported`, `unresolved` or `excluded`. |
| `evidence`, `evidence_status` | Required: evidence IDs, and `verified_current`, `proposed` or `unresolved`. |
| `neutral`, `native_default` | Optional finite numbers inside the domain. Neither is used as a fallback. |
| `region`, `side`, `native_id`, `surface`, `time` | Optional descriptions. |
| `coupling`, `validity`, `confidence` | Optional descriptions of the source contract. They are not runtime checks. |
| `metadata` | Optional object for inventory details, reasons and definitions. |

A profile has `id`, `label` and an ordered list `signal_ids`, with optional `evidence` and `metadata`. An evidence record has `id`, `claim` and `status`. A public record also has an HTTPS `url`, a `locator`, and at least one of `revision`, `retrieved` or `sha256`. An original record has `license` and `authorship` in place of a URL.

## Mapping fields

In the schema, a map is a `[[mappings]]` record with an `id` and a `rules` array. Each rule is one mapping. A map does not name its source and target profiles: the caller chooses them when it compiles the map.

| Field | Rule |
|---|---|
| `id` | Required and unique across all maps. |
| `inputs`, `outputs` | Required, ordered, non-empty arrays of signal IDs. Every operator has exactly one output. |
| `operator` | Required. One of the four operators below, with its parameters. |
| `disposition` | Required. Whether the author admits the relationship. |
| `mapping_quality` | Required only when the disposition is `mapped`: `exact` or `approximate`. |
| `assumptions` | Required array of strings. |
| `evidence`, `evidence_status` | Required. |
| `loss_annotations` | Required array of losses. Each has `category`, `effect`, `reason` and `refs`, with optional `units` and `bound`. |
| `coupling` | Optional. |

Loss categories are `signal`, `geometry`, `binding`, `animation`, `material` and `metadata`. Loss effects are `preserved`, `approximated`, `dropped` and `unknown`. A bound is optional. RCEF does not write a numerical bound when none is known.

`disposition`, `evidence_status` and `mapping_quality` are separate fields. A mapping has a direction from its inputs to its output. It does not imply an inverse.

## Operators

There are four operators. Each has one output.

| Operator | Inputs | Parameters | Result |
|---|---|---|---|
| `identity` | 1 | none | y = x |
| `affine` | 1 | finite `scale` and `offset` | y = (scale × x) + offset |
| `weighted_sum` | N | exactly N finite `weights`, in input order | y = 0 + w1 × x1 + w2 × x2 + ..., added in input order |
| `piecewise_linear` | 1 | `knots`: two or more [x, y] pairs | linear interpolation between the knots |

The operators follow these rules:

- `identity` compiles only if the input and output have the same units, value type, domain and calibration. They must also have the same neutral, side and coupling. Every map in RCEF changes the calibration basis, so no mapped rule uses `identity`. The one identity rule is in the unresolved record `survey.ambiguous`.
- `affine` makes the multiplication and the addition as two separate binary64 steps. It does not use a fused multiply-add. RCEF uses scale 1 and offset 0 to carry a value unchanged across a change of basis.
- `weighted_sum` starts at 0.0 and adds each weighted input in input order. It does not use compensated summation, and it does not normalize the weights.
- `piecewise_linear` needs x values that increase strictly and y values that are monotone. The first and last x must be the bounds of the input's domain, so msf-character-tools never extrapolates the curve. The result stays between the two y values of its segment.

The arithmetic uses checked binary64 steps. msf-character-tools refuses a step that gives a non-finite result. It also refuses a non-zero product or quotient that underflows to zero. It checks the domains before and after each operator. There is no clamp unless a mapping authors one with `piecewise_linear` knots.

msf-character-tools adds no hidden inverse, merge of left and right, or synthesized value. Each merge of two sides is an authored `weighted_sum` that declares its loss.

Data 0.5.0 uses 472 `affine`, 61 `weighted_sum`, 54 `piecewise_linear` and 1 `identity` mappings. The 54 `piecewise_linear` mappings are the 8 gaze splits of the FB2 out-map, the clamp of `alveolar_floor` and the 45 clamps of the bridge.

## Compiling a map

`compile_mapping` is stricter than the inventory checks. A map that it compiles must meet these rules:

- Its signals and mappings are `mapped`, and its mappings have evidence of their own.
- A `verified_current` mapping has `verified_current` endpoints. A `proposed` mapping can have `verified_current` or `proposed` endpoints.
- No part of the map has unresolved evidence.
- No signal has two writers, no output is also a source channel, and there are no cycles.
- Terminal outputs are in the target snapshot. Intermediate outputs can stay inside the compiled map.
- A mapping that is approximate, or that declares an `approximated`, `dropped` or `unknown` loss, compiles only with `allow_approximation=True`. Otherwise the error is `E_APPROXIMATION`.

The approximation opt-in does not bypass the other rules. `compile_mapping` refuses `survey.ambiguous` even with the opt-in, because it is unresolved.

## Shared APIs

Each shared API returns a typed `Result(value, report)`. When the report has errors, the value is `None`. Callers must check `.ok` and the diagnostics. A sidecar is a separate record that binds signals to an asset, with structural indices and hashes. It does not change the asset bytes.

| API | Use |
|---|---|
| `validate_authoring(document)` | Checks an authoring document against the schema. |
| `compile_pack(validated_authoring)` | Makes an immutable pack with a byte hash. |
| `inspect_asset(bytes, format, resolver=None, sidecar=None)` | Reads an asset and its sidecar bindings. msf-character-tools 0.6.0 also accepts the keyword-only options `isolate`, `limits` and `options`. |
| `compile_mapping(pack, source_snapshot, target_snapshot, mapping_id, allow_approximation=False)` | Compiles one map between two snapshots. |
| `evaluate_mapping(compiled_mapping, samples, *, partial=False)` | Runs a compiled map on a list of samples. |
| `annotate_asset(snapshot, annotations)` | Makes a sidecar. It does not change the asset bytes. |

Two helpers supply the inputs. `load_authoring(path)` reads a TOML file or a directory that holds `pack.toml`. `profile_snapshot(pack, id)` makes typed virtual channels from a profile.

A `CompiledMapping` gives `required_inputs`, the external inputs of the map. It also gives `output_inputs`, the inputs that each output reads.

## Samples

A sample is one frame. It has exactly three keys:

- `timestamp`: finite, non-negative seconds. A boolean is not accepted.
- `values`: one value for each input signal ID.
- `validity`: one boolean for each input signal ID.

```json
{"timestamp": 0.0, "values": {"fixture.affine.signed": 0.0}, "validity": {"fixture.affine.signed": true}}
```

The caller computes the validity of each input from the provider flags. For FB2 gaze, the validity is `isValid` AND `isEyeFollowingBlendshapesValid`. The caller also converts provider time, such as `XrTime`, to seconds.

| Frame condition | Result |
|---|---|
| Missing timestamp, or extra frame keys | msf-character-tools refuses the frame. |
| A value without validity, the reverse, or a validity that is not a boolean | `E_VALIDITY` |
| A required input missing from both objects | `E_MISSING_SAMPLE` |
| A finite input with validity `false`, even one equal to neutral | `E_INVALID_SAMPLE`. msf-character-tools does not put a neutral or default value in its place. |
| An unknown channel or a channel that is not a source | `E_SAMPLE_REFERENCE` |
| A non-finite, boolean or out-of-domain value | A numeric or domain error, for example `E_DOMAIN`. msf-character-tools does not clamp the value. |
| Valid frames | msf-character-tools writes each output with validity `true`, in frame order. There is no smoothing, resampling or hidden state. |

Without `partial=True`, every input in `required_inputs` must be present and valid. One bad input refuses the whole frame. If msf-character-tools refuses one frame in a call, the call returns no values for any frame. Each error has a `ref` that begins with `/samples/<n>`, so the caller can find the refused frames.

## Partial evaluation

With `partial=True`, msf-character-tools writes every output whose inputs are present and valid. The result has two more lists:

- `refusals`: each output that reads a bad input, with the frame number and its diagnostics.
- `unavailable`: each output that reads a missing input, with the frame number and the missing inputs.

A missing input is not an error in this mode. A bad input refuses only the outputs that read it. For example, a full FB2 frame with invalid gaze gives 62 canonical values and 8 refused gaze outputs. A VRCFaceTracking `Openness` of 1.2 refuses only `eye_close_left`, with `E_DOMAIN`.

## Route labels

Route runs each map once on all frames of a call, with partial evaluation. It then gives each target output that it does not write one of these labels:

| Label | Meaning |
|---|---|
| `not available from source` | No selected in-map can write a value that the output reads, or the source left out an input. This is not a refusal. |
| `refused upstream at <in-map>` | The in-map refused a canonical value that the output reads. |
| `refused at <out-map>` | The out-map refused the output. |

Each frame also lists its dropped inputs: the non-zero source values that do not reach any target output of the route. Toward META visemes from another set, Route writes no `isValid` flag and adds the note "META validity not asserted". On a route through the bridge, a class that the source cannot write counts as 0, and the frame's notes say so.

## Executable examples

This Python code runs the FB2 in-map on one frame and prints `0.5`. Run it from the RCEF checkout, with the locked msf-character-tools installed.

```python
import json
import msf_character_tools as msf

doc = json.load(open('generated/rcef.pack.json', encoding='utf-8'))
pack = msf.compile_pack(msf.validate_authoring(doc).value).value
fb2 = msf.profile_snapshot(pack, 'openxr.fb2').value
canonical = msf.profile_snapshot(pack, 'rcef.canonical_expression').value
result = msf.compile_mapping(pack, fb2, canonical, 'fb2.to_rcef_expression', allow_approximation=True)
assert result.ok, result.report.to_dict()
mapping = result.value
inputs = sorted(mapping.required_inputs)
values = dict.fromkeys(inputs, 0.0)
values['openxr.fb2.XR_FACE_EXPRESSION2_JAW_DROP_FB'] = 0.5
frame = {'timestamp': 0.0, 'values': values, 'validity': dict.fromkeys(inputs, True)}
out = msf.evaluate_mapping(mapping, [frame])
assert out.ok, out.report.to_dict()
print(out.value.samples[0]['values']['rcef.canonical_expression.jaw_drop'])
```

If the frame holds only the jaw drop value and the call uses `partial=True`, the result has `jaw_drop` 0.5. The other 69 outputs are in `unavailable`. Without the approximation opt-in, `compile_mapping` refuses the map with `E_APPROXIMATION`.

These mappings show each operator on real data:

| Mapping | Operator | Behaviour |
|---|---|---|
| `arkit_rcef.eye_close_left` | `affine`, scale 1, offset 0 | ARKit `eyeBlinkLeft` 0.25 gives canonical `eye_close_left` 0.25. The calibration basis changes, so the mapping is approximate and declares the gain loss. |
| `vrcft_eye_rcef.eye_close_left` | `affine`, scale −1, offset 1 | Canonical `eye_close_left` is 1 minus VRCFaceTracking `Openness`. The mapping refuses an `Openness` outside 0 to 1. |
| `vrcft_eye_rcef.pupil_diameter_mm_left` | `affine`, scale 1, offset 0 | The mapping copies the pupil diameter in millimetres. This mapping is exact and `verified_current`. |
| `rcef_arkit.browInnerUp` | `weighted_sum`, weights [0.5, 0.5] | ARKit `browInnerUp` is the mean of the left and right canonical inner brow raise. |
| `rcef_fb2.EYES_LOOK_RIGHT_L` | `piecewise_linear`, knots (−1, 0), (0, 0), (1, 1) | It reads the helper `gaze_in_minus_out_left`. A difference of 0.5 gives 0.5, and a difference of −0.5 gives 0. |
| `rcef_fb2.EYES_LOOK_LEFT_L` | `piecewise_linear`, knots (−1, 1), (0, 0), (1, 0) | It reads the same helper. A difference of −0.5 gives 0.5, and a difference of 0.5 gives 0. |

The gaze part of the FB2 out-map first computes in minus out, or up minus down, for each eye with a `weighted_sum` of [1, −1]. The two splits are each exactly 0 on their flat side. So the two FB2 directions of a pair are never both non-zero, as FB2 requires. When both canonical directions are non-zero, the out-map keeps only their difference. Each mapping declares that loss.

## Fixtures

The synthetic fixtures show the operators with numbers that are exact in binary64. `fixtures/mapping_samples.json` holds their expected values, and `tests/test_parity.py` checks them.

| Fixture | Operator | Inputs and expected outputs |
|---|---|---|
| `fixture.affine` | `affine`, scale 0.5, offset 0.5, from a signed basis to a unit basis | −1 gives 0, 0 gives 0.5, 1 gives 1 |
| `fixture.bilateral` | `weighted_sum`, weights [0.5, 0.5], from left and right brow to one shared brow | (1, 0) and (0, 1) both give 0.5; (0, 0) gives 0; (1, 1) gives 1 |
| `survey.ambiguous` | `identity`, MediaPipe `eyeBlinkLeft` to canonical `eye_close_left` | Unresolved. `compile_mapping` refuses it, even with the opt-in. |

`fixture.affine` is exact, with no loss and no hidden clamp. `fixture.bilateral` is approximate: the mapping cannot recover the difference between the sides. Its signal loss is `approximated`, its geometry loss is `unknown`, and it compiles only with the opt-in. `survey.ambiguous` is unresolved on purpose: names alone cannot establish the model calibration of MediaPipe.

Profile snapshots do not bind to physical assets. To use a mapping with an asset, a sidecar must give the structural indices and the hashes of the asset and its resources.

## Check tooling and the lock

`check.py` runs four steps in order and stops at the first failure:

1. It checks that the installed msf-character-tools is exactly a locked release wheel. If not, it exits with code 2 before it reads any data.
2. It checks the calibration records, the ledger and the mappings that cite them. This step does not use msf-character-tools.
3. It runs msf-character-tools to build the pack, the matrix, coverage and checksums. Without `--write`, it checks that these files have not changed.
4. It writes or checks the readable reports in the same way.

The lock records the msf-character-tools commit and version, and one entry for each wheel tag. Each entry has the SHA-256 of every file in the installed package. Checking never clones or downloads anything.

The tests check the generated files, the README tables, the reference list and the figures against the data. They also check that the maps of the canonical sets keep the values of the latest passing A/B freeze. Separate scripts check the source digests, the selected names and indices, and the visibility claims. These scripts need network access, so the tests do not run them. `scripts/ci_local.sh` runs `check.py` and the tests on Python 3.11 and 3.12.

## Release limits and remaining evidence

Full parity of the selected inventories is a data gate. It does not depend on calibration between providers. Each of these later gates needs its own measured acceptance:

- device availability and device integration;
- physical calibration with real trackers and real faces;
- visual equivalence of geometry;
- execution of VRM bindings, materials and overrides;
- Roblox certification;
- native kernels and host integration;
- standards adoption.

This proposal does not establish formal standards adoption or visual accuracy. A passing check shows only that the data, the generated files and the declared arithmetic agree.

RCEF has no evidence yet for these items:

| Missing evidence | State today |
|---|---|
| MediaPipe model calibration and provenance | No executable MediaPipe map. `survey.ambiguous` stays unresolved. The licence check read the model card and found no statement that relates the scores to ARKit, apart from the shared names. The calibration record found no passing score. |
| FB1 numeric bounds | The numeric range of the FB weights stays unresolved. The FB profile is inventory only. |
| FB2 maximum angles for each direction | Gaze stays a fraction with no angle. No map to VRM gaze presets. |
| VRCFaceTracking raw gaze units, and the contradictions in its sources | The affected signals stay unresolved. |
| Which Roblox list of required poses is authoritative | RCEF records both lists. All 50 Roblox controls are unresolved. |
| Permission to redistribute VRM specification prose | RCEF links to the VRM sources and writes its own summaries. It does not copy the prose or figures. |

The pack records these gaps as unresolved data. They block the derived mappings that depend on them. [docs/calibration/mediapipe-licence.md](docs/calibration/mediapipe-licence.md) records a later check of the MediaPipe model's licence and training-data statements.

---

# Appendix B: How the survey was made

## Selection criteria

A set joins the survey only when it meets all of these criteria:

- It is a public interface: a list of expression names in a published specification, documentation page or source file.
- Its source is pinned: an exact revision, or a retrieval date and a SHA-256 digest of the bytes.
- Each fact has a locator, such as line numbers or a named section of the pinned source.
- Its licence or terms are known. Where the terms do not allow copying, RCEF writes its own summary.

The list of sets comes from three places. It has every face, facial, lip and eye expression weight enum in the OpenXR registry at commit `5a82d45` (record `xr_registry`). It also has RCEF's own sets, and other sets that the authors knew of. So it is complete for OpenXR at that commit, but it is not a complete list of public sets.

A new or changed provider entry needs these items (CONTRIBUTING.md):

- a public primary source;
- an exact revision, or a retrieval date and a content digest;
- a locator;
- an original summary;
- evidence for the units, domain and calibration;
- an explicit disposition.

## Evidence records

The pack holds 81 evidence records. 78 records cite a public source, each with an HTTPS URL and a SHA-256 digest. 3 are original records: `rcef_definitions`, `rcef_canonical_v1` and the calibration record that the bridge cites. [references.md](references.md) lists every record.

`scripts/verify_sources.py` downloads each public source again and compares its digest. `scripts/audit_inventories.py` then compares the selected names, their order and the real enum indices with the verified bytes. The source bytes go to a cache outside the repository. The repository does not keep them.

This table gives the evidence records of each profile of a public set. The row count includes sentinels and absent rows.

| Profile | Rows | Evidence records of the profile |
|---|---:|---|
| `arkit.ancillary` | 2 | [apple_eye](references.md#apple_eye) |
| `arkit.coefficient` | 52 | [apple_blendshapes](references.md#apple_blendshapes) |
| `facs.code` | 92 | [facs_wikipedia](references.md#facs_wikipedia) |
| `godot.base` | 102 | [godot_enum](references.md#godot_enum), [godot_setters](references.md#godot_setters) |
| `godot.blended` | 42 | [godot_enum](references.md#godot_enum), [godot_setters](references.md#godot_setters) |
| `mediapipe.label` | 53 | [mediapipe](references.md#mediapipe) |
| `mediapipe.score` | 52 | [mediapipe](references.md#mediapipe), [mediapipe_blendshape_card](references.md#mediapipe_blendshape_card) |
| `openxr.ancillary` | 10 | [xr_registry](references.md#xr_registry) |
| `openxr.fb` | 65 | [xr_registry](references.md#xr_registry), [xr_fb](references.md#xr_fb) |
| `openxr.fb2` | 71 | [xr_registry](references.md#xr_registry), [xr_fb2](references.md#xr_fb2) |
| `openxr.visemes` | 15 | [xr_registry](references.md#xr_registry), [xr_visemes](references.md#xr_visemes) |
| `roblox.control` | 50 | [roblox_controls](references.md#roblox_controls), [roblox_requirements](references.md#roblox_requirements), [roblox_authoring](references.md#roblox_authoring), [roblox_poses](references.md#roblox_poses) |
| `vrcft.artist.base` | 102 | [vrcft_artist](references.md#vrcft_artist) |
| `vrcft.artist.blended` | 42 | [vrcft_artist](references.md#vrcft_artist) |
| `vrcft.eye` | 20 | [vrcft_data](references.md#vrcft_data) |
| `vrcft.parameter.encoding` | 7 | [vrcft_binary](references.md#vrcft_binary) |
| `vrcft.parameter.flags` | 3 | [vrcft_parameters](references.md#vrcft_parameters) |
| `vrcft.parameter.float` | 124 | [vrcft_parameters](references.md#vrcft_parameters), [vrcft_float](references.md#vrcft_float) |
| `vrcft.transport` | 89 | [vrcft_enum](references.md#vrcft_enum), [vrcft_data](references.md#vrcft_data) |
| `vrm.preset` | 18 | [vrm_expressions](references.md#vrm_expressions), [vrm_lookat](references.md#vrm_lookat) |

RCEF calls a position in a documentation list an inventory ordinal. It is a native index only when the source defines one. RCEF records count sentinels, absent rows and reserved bytes as separate rows. So a profile can have more rows than its selected interface: FB2 has 70 weights and 71 rows.

## Dispositions

Each signal has one disposition:

| Disposition | Meaning | Signals in public sets and `facs.code` |
|---|---|---:|
| `mapped` | At least one mapping uses the signal. | 269 |
| `unresolved` | Not researched yet, or the evidence is missing or conflicts. | 682 |
| `excluded` | Out of scope, for example a count sentinel or a confidence enum. | 54 |
| `unsupported` | The source has the value, but no executable mapping is supported. | 6 |

Each signal also has a reason in its metadata. A `mapped` signal does not guarantee that every requested map or frame can run.

## Evidence status

Evidence status describes verification. It is separate from the disposition and from the quality of a mapping.

| Status | Meaning |
|---|---|
| `verified_current` | The signal or mapping restates a verified source fact. |
| `proposed` | An approximate translation that sources support. It compiles only with the approximation opt-in. |
| `unresolved` | Recorded but not executable. `compile_mapping` refuses it, even with the opt-in. |

All 81 evidence records are `verified_current`. That status says only that each cited source is what the record claims. It does not say that the mappings that cite it are exact.

Of the 588 mappings, 5 are exact and `verified_current`: the 4 pupil copies and `fixture.affine`. `fixture.bilateral` is approximate with `verified_current` evidence. 581 are approximate and `proposed`, and 1 is unresolved.

## Definitions audit

The [definitions audit](docs/canonical-set-audit.md) compares each canonical signal with the public definition of each source that maps it. Each row gives the source name, the evidence record, the locator and an RCEF paraphrase.

| Verdict | Meaning | Rows |
|---|---|---:|
| `same` | The source's own text or figure names the action that the canonical definition describes. | 258 |
| `differs` | The source defines a different or wider action. The row gives a stable loss key. | 68 |
| `unresolved` | The evidence is missing or conflicts. The row gives a stable loss key. | 13 |

315 rows compare a canonical signal with the definition of a source:

| Source | Rows |
|---|---:|
| FB2 | 70 |
| ARKit | 60 |
| Unified Expressions | 64 |
| VRCFaceTracking eye data | 4 |
| VRM | 7 |
| META visemes | 16 |
| FACS codes | 53 |
| ICT-FaceKit crosswalk | 41 |

The other 24 rows are 14 IPA reference rows, 6 side-frame rows, 3 FACS encoding rows and 1 row for the scope of META's classes.

The audit uses one evidence rule. A provider's own text or figure settles a meaning or a side. Agreement between implementers settles only which output gets a value. When the provider's text and RCEF's records conflict, the verdict is `unresolved`.

## What the survey does not show

The survey records interfaces and their stated contracts. It does not measure how well a tracker follows a face. It does not show device availability, and it does not test geometry. The counts include rows that are excluded, unsupported or unresolved, so they are inventory counts, not counts of working translations.
