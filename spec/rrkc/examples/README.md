# RRKC governed-transition examples

These fixtures instantiate `../governed-transition-event.schema.json` and are intentionally specification/test material, not runtime ingestion receipts.

- `ratify-authorized.example.json` demonstrates a ratification whose evidence is admissible, whose governance authorization is affirmative, and whose transition is not veto-blocked.
- `veto-blocked.example.json` demonstrates that admissibility and governance remain independent judgments: the claim may be epistemically contested while governance independently blocks the transition through an active veto.

The integrity hashes in these examples are syntactic fixtures chosen to satisfy the schema's hexadecimal shape constraints. They are **not** claims that RFC 8785 canonicalization and digest verification were executed over these files. Runtime verification requires an actual runtime-generated receipt and should not be inferred from repository fixtures.

These examples exist to make the governance model inspectable and to provide stable inputs for future JSON Schema validation tests.
