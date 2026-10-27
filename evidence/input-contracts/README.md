# Optional R-PROV profile input contract

`rprov-profile.schema.json` is a JSON Schema (Draft 2020-12) for six nominated
source-input profiles. Use it only when you prepare those inputs; nothing selects
it automatically. Revision 2 of the schema file keeps data `contract_version = 1`
and pairs each profile ID with exactly one role. The schema describes passive
metadata: `signal_ids` and `operators` are empty, `executable` is false, and
source and physical observations are not admitted.

RCEF's profile inventory and package builder do not use this schema. Local
preparation checks are still needed for file references, source spans, fixture
and oracle relations, and rights. JSON Schema alone cannot check those relations.

## Review evidence

The frozen independent controls have six valid ID and role pairs and thirty
complete profiles with the wrong role. The earlier schema accepted all thirty
wrong-role profiles (37 tests, 30 assertion failures). Revision 2 refuses them
(37 tests, no failures). A new independent reviewer reproduced both results
with the same assertions. These results validate the input schema only.
Integration with a consuming SDK or runner, and qualification of providers or
runtimes, are separate work.

SHA-256 of the schema file:
`3f4d13f20d094ec6349390ac0ea273a975eeffe0a3923df90c08ce7c482fd8cc`.
