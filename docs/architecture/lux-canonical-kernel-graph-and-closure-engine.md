# Lux Canonical Kernel Graph and Closure Engine

**Architecture ID:** `urn:caeluviim:architecture:lux-kernel-closure:0.1.0`  
**Status:** proposed implementation, source-bound  
**Source:** `urn:caeluviim:source:lux-kernel-graph-mapping:2026-08-02`  
**Operational substrate:** repository manifests + Python validator + Neo4j ingestion runtime  
**Selected first implementation:** closure checker

## 1. Decision

The closure checker is implemented before the drafting engine, temporal state tracking, and proof-assistant integration.

The dependency order is:

`kernel representation → closure computation → missing-necessity report → legal drafting translation → temporal revision → formal verification`

Drafting cannot be meaningfully constrained by the kernel until antecedent claims, forward consequences, evidence relations, context, standards, provenance, and declared necessities are inspectable.

## 2. Source-preserving adaptation

The submitted material is preserved as the source proposal. This implementation does not claim that the Julia sketch was already executable or that it was the repository’s existing runtime.

The repository already uses a Python/Neo4j ingestion system with:

- stable URI identifiers
- append-only manifests
- SHA-256 source hashes
- allowlisted node labels and relationship types
- reified `RelationAssertion` entities
- transactional ingestion
- conflict detection
- automatic source and ingestion provenance links

The kernel is therefore translated into that substrate rather than replacing it with a second in-memory graph authority.

## 3. Kernel representation

Every named principle, concept, invariant, mode, facet, and required relation type is represented as an addressable graph entity.

| Kernel item | Runtime labels | Principal properties |
|---|---|---|
| Principle | `Rule`, `Claim` | name, section, text, canonical identifier, epistemic status |
| Concept | `Claim`, `Proposition` | name, definition, compressed form, canonical identifier |
| Invariant | `Rule`, `Claim` | invariant number, name, text |
| Encoding mode | `Claim`, `Proposition` | mode name, definition, kernel role |
| Required relation type | `Rule` | relation name, implementation status |
| Source section | `SourceSpan` | section, title, source-bound text |
| Submitted kernel | `Utterance` | title, speaker role, capture time, source hash |

Each derived entity is linked to the source section from which it was formalized. The runtime also automatically links each ingested entity and reified relationship assertion to the source record and ingestion event.

## 4. Relation representation

The submitted relation vocabulary is preserved as `Rule` nodes. Runtime edges use the repository’s existing allowlist. The exact submitted semantic relation is retained in the edge property `semantic_relation`.

Example:

```json
{
  "type": "DEPENDS_ON",
  "from": "urn:caeluviim:kernel:concept:closure",
  "to": "urn:caeluviim:kernel:concept:backnesting",
  "properties": {
    "semantic_relation": "CONTRIBUTES_TO"
  }
}
```

This representation avoids silently expanding the executable Cypher allowlist while preserving the named relation for inspection and later ratified promotion.

## 5. Closure semantics

The submitted formal structure is retained:

- `β(c) = c ∪ AntecedentClaims(c)`
- `φ(c) = {c' | c ⪯ c'}`
- `Closure(c) = β*(c) ∪ c ∪ φ*(c)`

The operational checker computes:

### 5.1 Backnest

Backnest traversal follows outgoing antecedent-bearing relationships:

- `DEPENDS_ON`
- `DERIVED_FROM`
- `EVIDENCED_BY`
- `PART_OF`
- `USED_CONTEXT`
- `USED_EVIDENCE_SET`
- `EVALUATED_UNDER_STANDARD`
- `EVALUATED_WITHIN_DOMAIN`
- `HAS_REASON`
- `HAS_ALTERNATIVE`
- `PRESUPPOSES`

Incoming `SUPPORTS` relationships are also treated as evidentiary antecedents.

### 5.2 Forward nest

Forward traversal follows outgoing consequence-bearing relationships:

- `EXTENDS`
- `REVISES`
- `SUPERSEDES`
- `IMPLEMENTS`
- `PROJECTS_TO`
- `PREDICTS`
- `PARTICIPATES_IN`
- `MATERIALIZED`
- `ENTAILS`

A claim that depends on the selected claim is also included as a forward dependent by traversing antecedent-bearing relationships in reverse.

### 5.3 Declared necessities

A claim may declare:

- `required_relation_types`
- `required_target_ids`
- `minimum_evidence_count`
- `require_provenance`

The checker reports missing relation types, unreachable required targets, insufficient evidence, and absent manifest-level provenance.

### 5.4 Epistemic boundary

`closure_complete = true` means that the represented graph satisfies the claim’s declared reachability and evidence-count requirements.

It does **not** mean:

- the claim is true
- the evidence is sufficient under law
- an authority accepted the claim
- a governance body ratified the claim
- no contradictory claim exists
- every relevant source has been found

Truth assessment remains a separate activity requiring proposition identity, evidence, context, standard, domain, assessor, time, justification, and revision state.

## 6. Legal claim-tracking binding

A legal domain graph binds to the kernel through explicit graph relationships rather than by copying semantic meaning implicitly.

| Legal entity | Kernel binding |
|---|---|
| pleaded factual proposition | `IMPLEMENTS` or `ANALOG_OF` Claim |
| cause-of-action element | Claim with declared required targets and evidence threshold |
| evidence item | `EVIDENCED_BY` from claim or `SUPPORTS` into claim |
| legal authority | `EVALUATED_UNDER_STANDARD`, `AUTHORIZED`, or `GOVERNED_BY` as applicable |
| deadline | Boundary claim indexed to jurisdiction, event, and purpose |
| complaint paragraph | linguistic Translation of one or more claims |
| amendment | new immutable representation connected by `REVISES` or `SUPERSEDES` |
| anticipated consequence | `PREDICTS`, `PROJECTS_TO`, or forward-dependent claim |

A drafting engine may consume a closure report, but it must not convert a missing requirement into invented facts, evidence, authority, or assent.

## 7. Corrections required to operationalize the submitted Julia sketch

These are implementation translations, not alterations to the source proposal:

1. `anything` and `everything` are referenced before they are created in the submitted Julia ordering.
2. An edge dictionary keyed only by `(src, dst)` cannot preserve multiple relation assertions between the same pair. The repository runtime reifies each relationship with its own URI.
3. An evidence-to-claim `SUPPORTS` relation is not automatically identical to `CORRECTS` or `CONSTRAINS_INTERPRETATION`; the asserted relation must remain explicit.
4. Graph traversal alone cannot answer “Is this claim true?” Closure and truth assessment remain separate.
5. The submitted node-count statement is an estimate. The production manifest is the auditable count.

## 8. Implemented artifacts

- immutable submitted source record
- architecture specification
- production ingestion manifest
- closure computation module
- `caeluviim-graph closure` CLI command
- unit tests for complete closure, missing evidence, missing targets, reverse dependencies, non-claim rejection, and production-manifest validation

## 9. CLI

```bash
python -m caeluviim_graph.cli closure \
  ingest/manifests/lux-kernel-core-v0.1.0.json \
  urn:caeluviim:kernel:principle:master-thesis
```

The command validates the manifest before computing closure and returns deterministic JSON.

## 10. Acceptance criteria

1. The source record remains immutable and hash-addressed.
2. Every kernel entity has a stable URI and source-span derivation.
3. Every relationship assertion is independently addressable after ingestion.
4. The kernel manifest validates against the existing ingestion schema.
5. The closure checker identifies antecedents, forward dependents, evidence, provenance, and missing declared necessities.
6. The closure checker never reports truth or ratification.
7. The production sync ingests the manifest idempotently.
8. Existing manifests and tests remain valid.
