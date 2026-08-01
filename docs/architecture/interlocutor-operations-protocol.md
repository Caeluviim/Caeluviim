# Interlocutor Operations Protocol

**Status:** Proposed v0.1.0  
**Purpose:** Make linguistic operations, transformations, interpretations, force assignments, and truth assessments explicit, provenance-preserving, contestable, and machine-auditable in real time.

## 1. Design commitments

| Commitment | Normative requirement |
|---|---|
| Immutable original language | Every captured utterance is stored as an immutable byte sequence with a content hash. No normalization, correction, paraphrase, summary, or interpretation may overwrite it. |
| Span-addressable provenance | Every quotation, proposition extraction, operation detection, and inference cites one or more immutable source spans. |
| Quotation/interpretation separation | Quoted language and system-generated interpretation are different entity types and must never be silently substituted for one another. |
| Explicit transformation events | Every transformation records input, output, operation type, agent, rule/model version, parameters, timestamp, and determinism class. |
| Contestable inferred force | Illocutionary force, implicature, stance, framing, intent, and social meaning are assessments, never hidden properties of the source utterance. Each assessment exposes alternatives and supports contestation. |
| Context-indexed truth | Truth assessment is a function of proposition, context, evidence, standard, jurisdiction, and time. No assessment may be represented as context-free when any input is material. |
| Revision without erasure | Corrections and supersessions create new records linked to prior records. Earlier records remain retrievable. |
| Language-operation visibility | Linguistic operations represented in the scholarly taxonomy are instantiable as graph data, not only prose definitions. |

## 2. Typed formal vocabulary

| Symbol | Type | Meaning |
|---|---|---|
| `u` | `Utterance` | Immutable source utterance. |
| `s(u,a:b)` | `SourceSpan` | Character span `[a,b)` in utterance `u`. Canonical serialized form: `urn:caeluviim:utterance:<sha256>#char=a:b`. |
| `q` | `Quotation` | Exact reproduction of one or more source spans. |
| `τ` | `TransformationEvent` | Event that transforms or derives one representation from another. |
| `ι` | `Interpretation` | A contestable interpretive product derived from cited spans and context. |
| `φ` | `ForceAssignment` | A contestable assignment of illocutionary or interactional force. |
| `p` | `Proposition` | Proposition extracted or constructed from language. |
| `c_t` | `ContextSnapshot` | Versioned context at time `t`. |
| `ε` | `EvidenceSet` | Versioned evidence set used in an assessment. |
| `σ` | `AssessmentStandard` | Standard of evaluation, proof, or support. |
| `j` | `JurisdictionOrDomain` | Jurisdiction, discourse domain, institution, or rule-governed practice. |
| `A` | `TruthAssessment` | Structured assessment result. |
| `C(x)` | `ContestationEvent` | Challenge to record `x`, including grounds and proposed alternative. |
| `R(x→x')` | `RevisionRelation` | Non-destructive revision or supersession relation. |

## 3. Context-indexed truth function

```text
T : Proposition × ContextSnapshot × EvidenceSet × AssessmentStandard
    × JurisdictionOrDomain × Time → TruthAssessment
```

`TruthAssessment` is a record, not a bare Boolean.

| Field | Allowed values / constraint |
|---|---|
| `status` | `supported`, `unsupported`, `contradicted`, `unresolved`, `indeterminate`, `inapplicable`, or `disputed` |
| `confidence` | Decimal in `[0,1]`; confidence is not truth and cannot replace status or reasons. |
| `proposition_id` | Required. |
| `context_id` | Required. |
| `evidence_set_id` | Required. |
| `standard_id` | Required. |
| `jurisdiction_or_domain_id` | Required when domain rules affect assessment. |
| `assessment_time` | Required. |
| `reason_ids` | One or more explicit reasons, rules, evidence evaluations, or defeaters. |
| `alternative_assessment_ids` | Zero or more competing assessments. |
| `rule_version_id` | Required for machine-produced assessments. |

### 3.1 Subjective claims

Subjective language is not converted into an unqualified external fact.

| Layer | Example | Permitted assessment |
|---|---|---|
| Utterance occurrence | A speaker produced the words “I feel ignored.” | The occurrence and exact wording can be supported by the immutable record. |
| Attributed avowal | The speaker stated that they felt ignored. | Supportable as an attributed report when the quotation is authentic. |
| Internal-state claim | The speaker in fact had the named internal state. | Not independently established merely by the utterance; preserve as first-person avowal unless additional evidence and an appropriate standard are supplied. |
| Globalized interpretation | “The speaker is irrational” or “nothing abusive happened.” | Prohibited as a direct transformation from the avowal; requires a separately sourced proposition, explicit standard, evidence, and contestable assessment. |

The system must not weaken a direct claim into language about a mere “experience,” “perception,” or “feeling” unless that transformation is explicitly labeled, justified, and contestable.

## 4. Operation classes

| Canonical class | Representative operations | Primary graph result |
|---|---|---|
| Semiotic | sign relation, signifier/signified, icon, index, symbol, interpretant, semiosis, code | `SignRelation`, `InterpretantRelation`, `CodeMembership` |
| Referential | sense/reference, denotation, description, rigid designation, deixis, indexicality, coreference | `ReferenceAssignment`, `Designation`, `CoreferenceAssertion` |
| Propositional-semantic | predication, compositionality, truth conditions, entailment, contradiction | `Proposition`, `PredicateApplication`, `EntailmentAssertion` |
| Pragmatic | speech act, illocutionary force, implicature, presupposition, relevance, common ground | `ForceAssignment`, `ImplicatureAssertion`, `PresuppositionAssertion` |
| Interactional | turn allocation, adjacency pair, sequence organization, repair, alignment, affiliation, stance | `TurnRelation`, `AdjacencyPair`, `RepairEvent`, `StanceAssignment` |
| Cognitive-semantic | categorization, prototype, metaphor, frame, construal, profiling, mental spaces, blending | `CategoryAssignment`, `ConceptualMapping`, `FrameEvocation`, `ConstrualAssignment` |
| Structural-linguistic | constituency, dependency, transformation, morphology, phonology, recursion | `SyntacticRelation`, `MorphologicalOperation`, `PhonologicalOperation` |
| Rhetorical-argumentative | ethos, pathos, logos, enthymeme, warrant, rebuttal, framing, identification | `ArgumentComponent`, `RhetoricalOperation`, `FrameAssignment` |
| Metalinguistic | quotation, gloss, definition, reported speech, autonymy, self-reference | `Quotation`, `DefinitionAssignment`, `MentionUseRelation` |
| Social-institutional | register, style shifting, language ideology, symbolic power, institutional declaration | `RegisterAssignment`, `SocialIndexicality`, `AuthorityCondition` |
| Acquisition-developmental | statistical learning, joint attention, scaffolding, construction learning, cultural transmission | `LearningOperation` |
| Provenance-governance | capture, transformation, assessment, contestation, revision, validation | `prov:Entity`, `prov:Activity`, `prov:Agent`, and Caeluviim-specific assessment nodes |

## 5. Provenance model

The protocol aligns with W3C PROV-O while retaining Caeluviim-specific linguistic semantics.

| Caeluviim entity | PROV-O alignment |
|---|---|
| `Utterance`, `SourceSpan`, `Quotation`, `Interpretation`, `Proposition`, `TruthAssessment` | `prov:Entity` |
| `TransformationEvent`, `RepairEvent`, `ContestationEvent`, `AssessmentActivity` | `prov:Activity` |
| Human, synthetic person, institution, model, validator | `prov:Agent` |
| Input use | `prov:used` |
| Output generation | `prov:wasGeneratedBy` |
| Derivation | `prov:wasDerivedFrom` |
| Responsible agent | `prov:wasAssociatedWith` / `prov:wasAttributedTo` |
| Revision | `prov:wasRevisionOf` plus explicit `supersedes` semantics |

## 6. Minimal invariants

| ID | Invariant |
|---|---|
| IO-INV-001 | An utterance content hash must resolve to exactly one immutable byte sequence. |
| IO-INV-002 | A quotation must cite **at least one** immutable source span and must reproduce each cited span exactly. |
| IO-INV-003 | A transformation event must not overwrite its input entity. |
| IO-INV-004 | Every derived entity must identify the transformation activity and source entity or entities from which it was derived. |
| IO-INV-005 | Interpretation, force, implicature, presupposition, stance, frame, and intent assignments must be explicitly marked as inferred and contestable. |
| IO-INV-006 | A truth assessment must include the complete input tuple required by `T`, its status, confidence, reasons, and rule version when machine-produced. |
| IO-INV-007 | Contestation and revision must preserve the contested or revised record and create explicit links to the new record. |
| IO-INV-008 | Duplicate scholarly rows must not create accidental duplicate canonical operation types. Each occurrence links to one canonical operation concept or declares a reason for distinction. |
| IO-INV-009 | No inferred claim may be presented as a quotation or attributed to a source speaker without an exact supporting span. |
| IO-INV-010 | No subjective avowal may be globalized, psychologized, or weakened without an explicit transformation event and preserved original wording. |
| IO-INV-011 | Operation detection must expose alternative analyses whenever more than one materially plausible operation or force exists. |
| IO-INV-012 | Machine-produced records must identify model or rule version and determinism class. |

## 7. Recursion and self-reference termination

Unlimited semiosis is represented without permitting unbounded runtime recursion.

| Rule | Requirement |
|---|---|
| Derivation acyclicity | `prov:wasDerivedFrom` and direct transformation-input relations must be acyclic within one derivation run. |
| Semantic-state repetition | If a derivation produces a semantic-state hash already present in its ancestry, processing stops with `status = unresolved` and `termination_reason = repeated_state`. |
| Maximum depth | Each run declares a maximum derivation depth. Exceeding it produces an explicit unresolved result rather than silently truncating. |
| Metalanguage level | Self-reference records declare object-language and metalanguage levels. A rule may not collapse levels without an explicit bridge transformation. |
| External continuation | Further interpretation may occur in a new derivation run linked to the prior run; the prior run remains closed and replayable. |

## 8. Determinism and replay

| Determinism class | Replay guarantee |
|---|---|
| `deterministic` | Exact output must be reproducible from immutable inputs, code/rule version, and parameters. |
| `seeded_stochastic` | Exact output requires recorded seed, model artifact, runtime version, and parameters. |
| `model_generated` | The original output is preserved immutably. A later replay may verify inputs and procedure but must not claim bit-exact regeneration unless the model artifact and execution environment are frozen and reproducible. |
| `human_judgment` | Replay reconstructs evidence and decision conditions; it does not claim deterministic reproduction of judgment. |

## 9. End-to-end processing contract

| Stage | Input | Output | Required provenance |
|---|---|---|---|
| Capture | Incoming language event | `Utterance` | content hash, agent, timestamp, channel, encoding |
| Span selection | `Utterance` | `SourceSpan` | character offsets and utterance hash |
| Quotation | One or more spans | `Quotation` | exact cited spans |
| Structural analysis | Span or quotation | syntax/morphology/discourse records | operation type, rule/model version, alternatives |
| Proposition extraction | Span or interpretation | `Proposition` | cited spans and transformation event |
| Pragmatic analysis | Span plus context | force, implicature, presupposition, stance records | context snapshot, confidence, alternatives |
| Truth assessment | proposition plus full `T` tuple | `TruthAssessment` | evidence, standard, jurisdiction/domain, time, reasons |
| Contestation | Any contestable record | `ContestationEvent` | challenger, target, grounds, proposed alternative |
| Revision | Existing record plus new grounds | New record and `R(x→x')` | preserved prior record, revision rationale |

## 10. Governance status

This module is proposed. The scholarly taxonomy is a provenance source and design input, not a declaration that every citation has completed independent verification. Corrected records must preserve the originally supplied record, the correction, correction basis, and verification status.

A fixed number of validators is not embedded as a universal rule. Validation requirements are selected by versioned governance policy according to operation type, risk, protected-path status, expertise requirements, conflicts of interest, and available independent evidence.
