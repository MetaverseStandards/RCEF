# A/B comparison: scoreboard

The pivot route (B) against the direct maps (A1) and the other arms. The held-out frames are held out by procedure: the registration and its ledger line were committed before this run.

Frames seen before the change (regression families, made again by the generator each earlier freeze pinned): regression:v1:arkit_uniform, regression:v1:facs_letters, regression:v1:facs_uniform, regression:v1:fb2_breaking, regression:v1:fb2_contract, regression:v1:perturb:arkit_uniform, regression:v1:perturb:facs_uniform, regression:v1:perturb:fb2_breaking, regression:v1:perturb:fb2_contract, regression:v1:perturb:viseme_simplex, regression:v1:perturb:vrcft_eye, regression:v1:perturb:vrm, regression:v1:viseme_simplex, regression:v1:vrcft_eye, regression:v1:vrm, regression:v3:arkit_uniform, regression:v3:facs_letters, regression:v3:facs_uniform, regression:v3:fb2_breaking, regression:v3:fb2_contract, regression:v3:perturb:arkit_uniform, regression:v3:perturb:facs_uniform, regression:v3:perturb:fb2_breaking, regression:v3:perturb:fb2_contract, regression:v3:perturb:viseme_simplex, regression:v3:perturb:vrcft_eye, regression:v3:perturb:vrm, regression:v3:viseme_simplex, regression:v3:vrcft_eye, regression:v3:vrm.

| Metric | Threshold | Status |
|---|---|---|
| B equals O | B gives the oracle's values, bit for bit, refusal codes, labels and notes on every frame of every pair | pass |
| M1 | B equals A1 on every output both write, sign of zero included; on the edge set B equals O | pass |
| M10 | FACS -> FB2: B equals A3 on outputs both write; coverage list frozen; B refuses 0 frames | pass |
| M10b | FACS -> ARKit: B equals A3 then A1 on outputs both write; coverage list frozen | pass |
| M11 | report: per ICT-FaceKit FACS row, B ARKit -> FACS links give the same ARKit shapes, or a listed difference | report |
| M1s | exact Fraction composition of B equals A1 on every linear A1 output | pass |
| M2 | in every frame B's refused outputs are among A1's, B writes every output A1 writes, dropped inputs equal | pass |
| M2b | report only | report |
| M2c | for every A1 output, B's hop evidence holds every evidence ID of the A1 rules that write it | pass |
| M3 coverage | on every impulse frame B changes exactly the outputs O changes; every composed link is changed or on the frozen flat list; every reached output non-zero on at least 1% of each seeded family that sets a linked input | pass |
| M3 exact | round trips exact on the listed channels; the rounding outputs within 2**-54 on exclusive frames and each gaze output within min(a, b) + 2**-52 on frames that break FB2 exclusivity | pass |
| M4 | B observed loss 0; A1 observed loss equals the registered baseline | pass |
| M4 keys | every (A1 rule, A1 loss reason) of the frozen table is covered by the B losses it names on the route; every audit key B adds on an A1 pair is on the audit-added list | pass |
| M4b | every catalogue entry of each replaced A1 rule is held by the hop assumption keys it names on the route, or is superseded with a cited reason | pass |
| M5 R1 | R1: 129 of 129 goldens exact through B | pass |
| M5 R2 | R2: per ARKit target, the composed B weights equal the 52 source-derived rows but the listed departures | pass |
| M6 | report: B and A1 (A3 then A1 for FACS) pose each rig identically, vertex for vertex; the harness oracles pass | report |
| M7 | every registered mutation of the B pack is caught by each check it names | pass |
| M8 | report only | report |
| M8 R3 | report: FB2 -> VRCFT UE, B equals R3 (the Godot route) on every R3 output but the listed departures | report |
| Revise | B equals the revised freeze's B, bit for bit, on every output both write; B writes every output it wrote; B's refused outputs are among its refused outputs; dropped inputs equal; its notes are kept, with the frozen map renames | pass |

| Pair | Evidence status (A1 / B) | M2c shortfall | M4b | External reference |
|---|---|---|---|---|
| ARKit -> ARKit |  |  | no A1 rule | no external reference |
| ARKit -> FACS |  |  | no A1 rule | no external reference |
| ARKit -> FB2 | proposed / proposed | 0 | shortfall 0 of 201 | A1 |
| ARKit -> VRCFT UE | proposed / proposed | 0 | shortfall 0 of 202 | A1 |
| ARKit -> VRCFT eye |  |  | no A1 rule | no external reference |
| ARKit -> VRM blink |  |  | no A1 rule | A2 |
| FACS -> ARKit |  |  | no A1 rule | A3 |
| FACS -> FACS |  |  | no A1 rule | no external reference |
| FACS -> FB2 |  |  | no A1 rule | A3 |
| FACS -> VRCFT UE |  |  | no A1 rule | no external reference |
| FACS -> VRCFT eye |  |  | no A1 rule | no external reference |
| FACS -> VRM blink |  |  | no A1 rule | no external reference |
| FB2 -> ARKit | proposed / proposed | 0 | shortfall 0 of 158 | A1 |
| FB2 -> FACS |  |  | no A1 rule | no external reference |
| FB2 -> FB2 |  |  | no A1 rule | no external reference |
| FB2 -> VRCFT UE |  |  | no A1 rule | A2 |
| FB2 -> VRCFT eye |  |  | no A1 rule | no external reference |
| FB2 -> VRM blink | proposed / proposed | 0 | shortfall 0 of 8 | A1 |
| META -> ARKit |  |  | no A1 rule | no external reference |
| META -> FACS |  |  | no A1 rule | no external reference |
| META -> FB2 |  |  | no A1 rule | no external reference |
| META -> META |  |  | no A1 rule | no external reference |
| META -> VRCFT UE |  |  | no A1 rule | no external reference |
| META -> VRM | proposed / proposed | 0 | shortfall 0 of 20 | A1 |
| VRCFT eye -> ARKit |  |  | no A1 rule | no external reference |
| VRCFT eye -> FACS |  |  | no A1 rule | no external reference |
| VRCFT eye -> FB2 |  |  | no A1 rule | no external reference |
| VRCFT eye -> VRCFT UE |  |  | no A1 rule | no external reference |
| VRCFT eye -> VRCFT eye |  |  | no A1 rule | no external reference |
| VRCFT eye -> VRM |  |  | no A1 rule | no external reference |
| VRM -> ARKit |  |  | no A1 rule | no external reference |
| VRM -> FACS |  |  | no A1 rule | no external reference |
| VRM -> FB2 |  |  | no A1 rule | no external reference |
| VRM -> META |  |  | no A1 rule | no external reference |
| VRM -> VRCFT UE |  |  | no A1 rule | no external reference |
| VRM -> VRCFT eye |  |  | no A1 rule | no external reference |
| VRM -> VRM |  |  | no A1 rule | no external reference |
