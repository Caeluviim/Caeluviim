# Interpersonal definition corpus — implementation and source-binding register

**Date:** 2026-08-02  
**Parent pull request:** #24  
**Status:** Human-readable Definition Claim corpus and machine-resolvable manifest created; protected-path implementation and external source binding remain mandatory.

## Applied consolidation

The following artifacts now exist:

- `corpus/definitions/interpersonal-morality-care-harm-and-mediation.md`
- `graph/manifests/interpersonal-morality-care-harm-mediation.json`

The corpus includes:

- 42 stable Definition Claim identities;
- 25 expanded human-readable Definition Claim-cards;
- the current truth definition;
- formal expressions for truth, care, harm, repair, and moral evaluation;
- distinctions among care, validation, agreement, control, mediation, adjudication, apology, repair, disagreement, conflict, consent, coercion, manipulation, abuse, and neglect;
- an explicit therapeutic and mediation knowledge-family expansion map;
- machine-resolvable exact definitions, states, source paths, and principal relation neighborhoods.

## Governing formulations preserved

1. Truth is maximal presently allowable objective accuracy under the available condition field.
2. Separate literal content, plausible inference, and verified intent.
3. Attach each apology to a concrete rule change, artifact correction, or validation test.
4. Record the consent basis, scope, and revocability for consequential actions.
5. Limit relational claims to observable acts and current capabilities.
6. Shared history or familiarity does not override present consent or boundaries.
7. Linguistic absence can constitute neglect when communication is materially required for security, coordination, recognition, or care.

## Mandatory implementation derivatives

| Derivative | Responsible layer | Required result | Verification |
|---|---|---|---|
| Definition Claim schema records | `schemas/**` and canonical corpus | Represent every indexed interpersonal conception through the standardized kernel and material conditional modules. | Schema validation for all 42 entries. |
| RDF/OWL vocabulary | `ontology/**` | Add classes and relations for morality, care, harm, dignity, consent, responsibility, power, coercion, manipulation, abuse, neglect, mediation, therapeutic mediation, repair, justice, and related conceptions. | RDF parse and vocabulary assertion tests. |
| SHACL constraints | `shapes/**` | Enforce scope, provenance, consent dimensions, responsibility attribution, source distinction, and unresolved-conflict visibility. | Positive and negative fixtures. |
| Runtime relation allowlist | `caeluviim_graph/**` | Add typed edges required by the interpersonal corpus. | Runtime ingestion and round-trip tests. |
| Exact-meaning separation | model access and validation | Preserve literal content, plausible inference, verified intent, experienced consequence, and independently supported consequence as distinct Claims. | Conflation rejection fixtures. |
| Care validation | interaction validator | Reject self-declared care that does not resolve to observable acts, consent, consequence awareness, or accountability. | False-care and demonstrated-care cases. |
| Harm representation | graph and evidence layers | Represent degraded capacity or condition, causal or maintaining relation, severity, duration, reversibility, responsibility, and repair. | Multi-domain harm fixtures. |
| Consent record | process and governance layers | Record basis, information supplied, scope, duration, conditions, voluntariness, and revocation. | Consent expansion and invalidation tests. |
| Apology and repair distinction | repair runtime | Require concrete correction, restoration, or recurrence prevention before apology can satisfy a repair obligation. | Apology-only rejection test. |
| Mediation role boundary | process schemas | Distinguish facilitation, therapy, legal advice, adjudication, governance, and participant authority. | Role-conflict fixtures. |
| Non-coercive disagreement | interaction validation | Preserve disagreement without automatically classifying hostility, rupture, pathology, or moral failure. | Tone-independent disagreement tests. |
| Therapeutic source binding | sources and provenance | Attach primary scholarly or professional sources, named frameworks, methods, limits, conflicts, authority boundaries, and jurisdictional constraints. | Source coverage and citation-location checks. |
| Multilingual and glyph realization | corpus registries | Add language anchors and glyphs only with provenance, non-equivalence, and governance state. | Language and collision validation. |
| Case and interaction integration | legal and interaction graphs | Connect events to interpersonal definitions, evidence, responsibility, repair, procedural obligations, and competing interpretations. | End-to-end event-to-repair traversal. |

## Source-binding waves

### Wave A — foundational relational operations

- active and reflective listening;
- validation and recognition;
- empathy, compassion, and perspective-taking;
- therapeutic alliance and rupture repair;
- consent, boundaries, confidentiality, and professional roles.

### Wave B — conflict and mediation

- mediation;
- transformative mediation;
- conflict transformation;
- restorative practices and restorative justice;
- de-escalation;
- nonviolent communication.

### Wave C — therapeutic-relational frameworks

- motivational interviewing;
- mentalization;
- emotion regulation and co-regulation;
- attachment and relational patterns;
- family-systems and group-process approaches;
- narrative and meaning-reconstruction approaches;
- solution-focused and strengths-oriented processes.

### Wave D — power, ethics, and repair

- power analysis and anti-oppressive practice;
- moral injury and relational injury distinctions;
- accountability, apology, forgiveness, reconciliation, and repair;
- justice, fairness, reciprocity, dignity, and recognition frameworks.

## Completion conditions

The interpersonal definition field is not implementation-complete until:

1. all 42 indexed conceptions have canonical machine records;
2. all 25 expanded cards validate against the standardized Definition Claim schema;
3. every material dependency has a stable Claim ID or unresolved-definition record;
4. therapeutic and mediation Claims are source-bound before professional implementation;
5. competing frameworks and definitions remain separately visible;
6. interaction events can traverse to harm, responsibility, repair, and recurrence-prevention Claims;
7. validation rejects the identified category conflations;
8. model-access packets transmit the operative interpersonal definitions and controlled distinctions;
9. future corrections update both the human-readable cards and machine manifest non-erasingly.
