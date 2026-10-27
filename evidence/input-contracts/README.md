# Optional R-PROV profile input contract

`rprov-profile.schema.json` is a Draft 2020-12 schema for six nominated source-input
profiles. Select it explicitly when preparing those inputs. Schema artifact revision
2 retains data `contract_version = 1` and pairs each profile ID with exactly one
role. It describes passive metadata: `signal_ids` and `operators` are empty,
`executable` is false, and source/physical observations are unadmitted.

The existing profile inventory and package builder do not select this schema.
Filesystem references, source spans, fixture/oracle relations and rights still need
local preparation checks; JSON Schema alone does not establish those relations.

## Review evidence

The frozen independent controls contain six valid ID/role pairs and thirty complete
wrong-role profiles. The earlier schema admitted all thirty wrong-role profiles
(37 tests, 30 assertion failures); revision 2 refuses them (37 tests, no failures).
A fresh independent reviewer reproduced both results with the same assertions.
These results validate the input schema; consuming SDK/runner integration and
provider or runtime qualification are separate work.

Source artifact SHA-256:
`3f4d13f20d094ec6349390ac0ea273a975eeffe0a3923df90c08ce7c482fd8cc`.
