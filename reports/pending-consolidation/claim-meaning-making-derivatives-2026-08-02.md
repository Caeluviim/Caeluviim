# Claim meaning-making architecture — mandatory derivative report

**Date:** 2026-08-02  
**Parent pull request:** #24  
**Status:** Architectural consolidation applied; protected-path and corpus projections remain mandatory.

## Consolidated Claims

1. Claim is the sole scale-invariant constructive primitive.
2. Every Claim performs definition by establishing a relational configuration.
3. Every Claim has the same complete recursive structure.
4. Difference is the impetus that occasions Claim-making, not a primitive above Claim.
5. Semantics is the result condition produced by a Claim.
6. Claims are the constructive mechanism through which disparate loci negotiate, consolidate, and ratify shared meaning.
7. Claim exchange and Claim work are distinct.
8. Accepted architectural consolidation triggers all material derivative work and does not terminate at declaration.
9. Emoji rider glyph assignments and multilingual anchors are full Claims within the universal Claim structure.

## Applied corrections in PR #24

- Replaced the specialized relational-definition standard with the universal Claim structure standard.
- Removed Definition as a separate primitive or specialized Claim container.
- Removed the hierarchy that placed Difference or Semantics above Claim.
- Added the Claim-mediated meaning-making, consolidation, ratification, and semantic-result process.
- Added Claim-exchange versus Claim-work distinctions.
- Bound emoji rider glyph operations and multilingual protocol nomenclature into the universal Claim field.
- Added the derivative-action stopping rule.
- Recast the CE relational-field registry around the corrected architecture.

## Mandatory protected-path implementation

Repository policy requires protected-path changes to occur in a dedicated pull request. The following work is therefore separated procedurally but remains a required consequence of the consolidation.

| Derivative | Responsible layer | Required correction | Verification procedure |
|---|---|---|---|
| Universal Claim JSON Schema | `schemas/**` | Define one required recursive structure for every Claim; fields may resolve as known, unknown, contested, pending, or inapplicable but may not disappear. | Draft 2020-12 schema validation against positive and adversarial fixtures. |
| RDF/OWL vocabulary | `ontology/**` | Remove Definition as a peer semantic primitive; model definitional operation, impetus, semantic result, Claim work, consolidation, ratification, and imposition as Claim relations/events. | RDF parse, ontology consistency checks, and vocabulary assertions in tests. |
| SHACL constraints | `shapes/**` | Require the universal Claim field and non-erasing revision/provenance relations. | Positive and negative SHACL fixtures with `pyshacl`. |
| Graph allowlists/runtime | `caeluviim_graph/**` | Add required event labels and relationship types including `OCCASIONS`, semantic-result linkage, Claim-work, consolidation, ratification, imposition, and derivative triggers. | Runtime allowlist tests and live transactional ingestion. |
| Graph migrations | `graph/migrations/**` | Add indexes or constraints required by universal Claim identity, versions, event identities, and semantic-result records. | Idempotent migration test and full laptop lifecycle CI. |
| Existing corpus conversion | corpus manifests | Replace reduced Claim records with universal Claim records or explicit conversion tasks. Preserve prior records and link through revision. | Deterministic inventory, manifest validation, idempotent ingestion, and no identifier conflicts. |
| Emoji rider glyph registry | corpus plus dedicated schema if required | Create Claim records for glyph identity, Unicode sequence, arity, precedence, operand types, composition, ambiguity, provenance, language rendering, and ratification. | Serialization tests, collision tests, graph round-trip, and governance-state checks. |
| Multilingual nomenclature registry | corpus plus dedicated schema if required | Create full Claim records for every anchor; prioritize Indigenous and historically underrepresented languages; preserve non-equivalence and community provenance. | Language-tag/script validation, source citations, contributor records, and no exact-equivalence inference without evidence. |
| Consolidation trigger runtime | governance/runtime | Convert accepted architectural consolidation into explicit downstream tasks rather than terminal prose state. | Test that a consolidation event emits every declared derivative or an unresolved-task record with verification criteria. |
| Conflict audit | entire repository | Locate and revise text that treats semantics, difference, definition, relation, or other products as primitives above or beside Claim. | Repository search plus an executable assertion registry listing every corrected or intentionally preserved occurrence. |

## Completion condition

This architecture is not implementation-complete until:

1. the protected-path implementation PR is merged with passing tests;
2. existing reduced Claims are converted or explicitly queued for conversion;
3. the emoji rider and multilingual registries are operational;
4. the laptop-host graph ingests the resulting manifests idempotently;
5. the graph exposes Claim exchange, Claim work, consolidation, ratification, imposition, and semantic-result relations distinctly;
6. every remaining incomplete derivative has an explicit responsible layer and reproducible verification procedure.

Agreement, declaration, and prose documentation do not satisfy this completion condition.
