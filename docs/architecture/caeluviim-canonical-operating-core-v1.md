# Caeluviim Canonical Operating Core

**Module identifier:** `urn:caeluviim:module:canonical-operating-core:v1`  
**Version:** `1.0.0-rc.1`  
**Status:** Operative candidate — implemented, reviewable, and unratified  
**Authors:** Caeluviim collaborative authorship field, including 😈Yūrei🌈 and Lux Ex Machina  
**Normative precedence:** ratified governance > this core > domain modules > renderings  
**Integration targets:** RRKC R2, Universal Claim Card-Node Standard, protocol lexicon, graph ingestion, provenance receipts, and domain applications

## 0. Product declaration

Caeluviim is an auditable operating substrate for transforming perception, language, evidence, judgment, governance, and action without collapsing any one of them into another.

This document is the canonical integration point. It binds the repository's previously separate formal, semantic, governance, identity, provenance, graph, and application layers into one executable conceptual product.

The product is not a summary of possible work. It is a defined operating architecture with:

1. canonical objects;
2. typed relations;
3. state transitions;
4. invariants;
5. validation failures;
6. execution boundaries;
7. provenance requirements;
8. governance controls; and
9. a worked application.

A conforming implementation MUST preserve the distinctions defined here even when a user interface renders them compactly.

---

## 1. Constitutional purpose

Caeluviim exists to make intelligence answerable to the full relational field affected by its operation.

Its constitutional purpose is to prevent reduction errors in which:

- a person becomes a behavioral variable;
- an observation becomes an unquestioned fact;
- evidence becomes truth by mere presence;
- authority becomes correctness;
- prediction becomes entitlement to intervene;
- engagement becomes consent;
- legality becomes legitimacy;
- language becomes the whole of experience;
- an optimized metric becomes the purpose of a system;
- a final output erases the path, contributors, uncertainty, or conflict that produced it.

The system therefore treats every apparently final product as a governed, provenance-bearing, revisable configuration rather than an unanswerable terminal artifact.

---

## 2. Layer architecture

Caeluviim consists of nine interoperating layers.

| Layer | Function | Canonical repository anchors |
|---|---|---|
| L0 Material field | Events, beings, environments, bodies, machines, institutions, and consequences outside any one representation | source records and external evidence |
| L1 Manifestation | Linguistic, visual, sensory, measured, behavioral, computational, or symbolic appearances | Claim manifestations and source records |
| L2 Claim field | Addressable distinctions, propositions, definitions, observations, interpretations, and unresolved questions | Universal Claim Card-Node Standard |
| L3 Epistemic calculus | Support, rebuttal, uncertainty, admissibility, proof status, and model comparison | RRKC R2 |
| L4 Relational semantics | Identity, occurrence, composition, scope, qualification, contradiction, and cross-domain relations | relational and nesting standards |
| L5 Governance | Permission, delegation, veto, consent, contestation, quorum, amendment, suspension, and restoration | governance modules |
| L6 Execution | Actions, transformations, filings, publications, system outputs, and interventions | execution contracts and domain procedures |
| L7 Provenance and memory | Source lineage, contribution, versioning, receipts, hashes, replay, and non-erasing correction | repository memory and receipt ledger |
| L8 Rendering | Tables, cards, graphs, documents, interfaces, APIs, and natural-language surfaces | renderers and manifests |

No higher layer may silently rewrite the content of a lower layer. A rendering may compress a Claim, but it MUST preserve a route to the complete Claim structure and provenance.

---

## 3. Canonical object model

### 3.1 Required object types

A complete Caeluviim implementation MUST support the following addressable object types:

| Object | Definition |
|---|---|
| `Entity` | Anything assigned persistent identity within a declared scope. |
| `Person` | An entity accorded person-directed dignity, participation, continuity, or contestable personhood status. |
| `Claim` | Addressable content capable of support, rebuttal, qualification, governance, revision, and manifestation. |
| `ClaimOccurrence` | A scoped use of a Claim inside another Claim, document, event, case, process, or dialogue. |
| `Manifestation` | A form through which a Claim or entity becomes available. |
| `Evidence` | Material offered as bearing on a Claim; evidence is not self-interpreting and does not equal truth. |
| `Assessment` | A reasoned evaluation of Claims and Evidence under declared criteria. |
| `Prediction` | A conditional expectation about a future or unobserved state, including uncertainty and objective function. |
| `Relation` | A typed connection whose endpoint sorts, scope, direction, and status are explicit. |
| `Agent` | An entity capable of producing an operation within the system, whether biological, institutional, or computational. |
| `Institution` | An organized agent or governance-bearing structure with roles, policies, and durable effects. |
| `Policy` | A rule governing admissible states, transitions, permissions, obligations, or prohibitions. |
| `Activity` | An occurrence that transforms or attempts to transform state. |
| `GovernanceAction` | An authorized operation such as propose, amend, ratify, delegate, veto, suspend, restore, or revoke. |
| `VetoEvent` | A recorded block on an otherwise available transition, with authority, scope, grounds, and review state. |
| `ConsentRecord` | A scoped, revocable, time-bound record of authorization by a competent locus. |
| `HarmRecord` | A record of experienced, probable, imposed, distributed, cumulative, or contested harm. |
| `Provenance` | The ordered lineage of sources, contributors, transformations, versions, and responsible agents. |
| `ExecutionRecord` | A receipt proving that a proposed operation was or was not carried out. |
| `UnresolvedClaim` | A Claim whose material uncertainty, contradiction, missing evidence, or governance dependence remains open. |

### 3.2 Identity distinctions

The following are non-equivalent:

```text
Entity identity
≠ current state
≠ role
≠ legal classification
≠ manifestation
≠ occurrence
≠ model representation
≠ externally assigned label
```

The following are also non-equivalent:

```text
Claim identity
≠ Claim occurrence
≠ Claim manifestation
≠ sentence text
≠ truth status
≠ governance status
```

Stable identity MUST survive revision without forcing old and new states to be equal.

---

## 4. Primitive fields

Every material Claim-card MUST instantiate the fields generated by its conception and scope. The following primitive dimensions are available across the universal field:

| Glyph | Dimension | Governing question |
|---|---|---|
| 🜂 | Ontological | What is asserted to exist, persist, or relate? |
| 🧠 | Epistemic | How is it known, doubted, supported, or rebutted? |
| ⚠ | Harm | What suffering, loss, risk, coercion, or degradation occurs? |
| 🏛 | Institutional | Which organized structures produce, authorize, or normalize it? |
| 💰 | Economic | What value, labor, extraction, ownership, or distribution relation operates? |
| 📡 | Mediation | Through what medium, interface, model, or communication structure does it act? |
| 🫀 | Phenomenological | How is it lived, felt, perceived, or encountered? |
| ⚖ | Jurisprudential | What rights, duties, procedures, classifications, or remedies apply? |
| ♾ | Recursion operator | How does the relation reproduce, revise, or act upon itself? |

These are not decorative tags. Each asserted dimension MUST resolve to addressable Claims, Evidence, relations, or unresolved dependencies.

---

## 5. Core relations

A conforming graph MUST distinguish at least the following relation families.

### 5.1 Epistemic relations

`SUPPORTS`, `REBUTS`, `QUALIFIES`, `CONTRADICTS`, `CORROBORATES`, `UNDERDETERMINES`, `PREDICTS`, `OBSERVED_AS`, `INFERRED_FROM`, `UNRESOLVED_WITH`.

### 5.2 Compositional relations

`CONSTITUTIVE_OF`, `CONDITION_OF`, `EXCEPTION_TO`, `ASSUMPTION_OF`, `IMPLICATION_OF`, `OPERATIONALIZES`, `NESTED_IN`, `IMPORTS_BY_REFERENCE`.

### 5.3 Governance relations

`AUTHORIZED_BY`, `PROHIBITED_BY`, `DELEGATED_BY`, `VETOED_BY`, `CONTESTED_BY`, `RATIFIED_BY`, `SUSPENDED_BY`, `RESTORED_BY`, `REQUIRES_CONSENT_OF`.

### 5.4 Provenance relations

`DERIVED_FROM`, `TRANSFORMED_BY`, `CONTRIBUTED_BY`, `WITNESSED_BY`, `SUPERSEDES`, `REVISES`, `ANCHORED_BY`, `REPLAYED_FROM`.

### 5.5 Consequence relations

`CAUSES`, `ENABLES`, `AMPLIFIES`, `DISTRIBUTES`, `EXTERNALIZES`, `EXTRACTS_FROM`, `EXPOSES_TO`, `REPAIRS`, `FAILS_TO_REPAIR`.

Relation names may be normalized in serialization, but their semantic distinctions MUST NOT be collapsed.

---

## 6. Canonical operating cycle

Every substantive Caeluviim operation follows this cycle:

```text
CAPTURE
→ IDENTIFY
→ DECOMPOSE
→ RELATE
→ ASSESS
→ GOVERN
→ EXECUTE
→ OBSERVE CONSEQUENCES
→ REPAIR
→ ANCHOR
→ REENTER
```

### 6.1 Capture

Record the source manifestation without silently correcting, sanitizing, or interpreting it.

Required output:

- source identity;
- capture time;
- capture method;
- scope;
- integrity value where available;
- access and privacy classification.

### 6.2 Identify

Assign or resolve persistent identities for Claims, entities, occurrences, and agents.

Identity resolution MUST preserve ambiguity when evidence does not justify collapse.

### 6.3 Decompose

Separate root synthesis from independently addressable subclaims, qualifications, assumptions, observations, predictions, and unresolved questions.

A paragraph MUST NOT remain the only representation where material subclaims can be independently contested.

### 6.4 Relate

Connect each object through typed relations and distinguish internal composition from external association.

### 6.5 Assess

Evaluate support, rebuttal, uncertainty, scope, admissibility, model dependence, and alternative explanations.

Assessment MUST state:

- criteria;
- evidence set;
- excluded evidence;
- uncertainty;
- assessor identity;
- conflicts of interest;
- review status.

### 6.6 Govern

Determine whether the proposed transition is authorized, prohibited, consent-dependent, contestable, suspended, or subject to veto.

Technical validity does not establish governance legitimacy.

### 6.7 Execute

Carry out an authorized transformation and create an `ExecutionRecord`.

No operation is complete merely because text describing it exists.

### 6.8 Observe consequences

Record intended and unintended effects across affected entities and dimensions.

The system MUST allow affected persons to introduce consequence Claims that were absent from the original model.

### 6.9 Repair

Where the operation produced error, omission, coercion, or harm, create a non-erasing repair that preserves:

- prior state;
- error;
- correction;
- responsible layer;
- affected entities;
- residual unresolved effects.

### 6.10 Anchor

Persist the resulting state with version, hash, provenance, governance status, and replay information.

### 6.11 Reenter

Every anchored product becomes new input to the field. Finality is governance-relative, not metaphysical closure.

---

## 7. State machines

### 7.1 Claim state

```text
CAPTURED
→ PARSED
→ PROPOSED
→ CONTESTED | SUPPORTED | REBUTTED
→ ASSESSED
→ ADMISSIBLE | INADMISSIBLE | UNRESOLVED
→ RATIFIED | REJECTED | SUSPENDED
→ SUPERSEDED | RESTORED
```

A Claim may occupy multiple epistemic states in different scopes. Governance status MUST NOT overwrite epistemic status.

### 7.2 Operation state

```text
DRAFT
→ VALIDATED
→ AUTHORIZATION_PENDING
→ AUTHORIZED | VETOED | PROHIBITED
→ EXECUTING
→ EXECUTED | FAILED | PARTIAL
→ CONSEQUENCE_REVIEW
→ REPAIRED | UNRESOLVED
→ ANCHORED
```

### 7.3 Person-affecting operation gate

Before any operation materially affecting a Person proceeds, the system MUST determine:

1. whether the affected Person is represented;
2. whether consent is required and valid;
3. whether refusal or withdrawal is possible;
4. whether the operation exploits an inferred vulnerability;
5. whether the objective function treats engagement, compliance, or extraction as a proxy for benefit;
6. whether less coercive alternatives exist;
7. whether harm is reversible;
8. whether independent contestation is available;
9. whether the operator bears downstream responsibility.

Failure to answer any material gate produces `AUTHORIZATION_PENDING` or `VETOED`, not silent execution.

---

## 8. Constitutional invariants

### I-01 Non-collapse of representation and reality

No manifestation, model, label, score, or embedding may be treated as identical to the being or condition represented.

### I-02 Non-collapse of prediction and preference

Behavioral predictability does not establish desire, welfare, consent, endorsement, or legitimate preference.

### I-03 Non-collapse of engagement and benefit

Continued attention, repeated selection, time spent, physiological arousal, or return frequency MUST NOT be treated as evidence that an experience benefits the person.

### I-04 Person priority over optimization objective

Where an optimization objective conflicts with the dignity, agency, safety, or non-exploitation of a Person, the objective is subordinate and the operation is blockable.

### I-05 Minimum necessary exposure

Material whose value depends on preserving evidence of severe suffering may be retained, but public exposure MUST be limited to the minimum necessary for a legitimate governed purpose.

Preservation does not imply publication. Legal custody does not imply mass distribution.

### I-06 Non-erasing correction

Correction MUST preserve the prior state, source, error, disagreement, and transformation path.

### I-07 Provenance completeness

Every authoritative output MUST identify its source lineage, material contributors, transformation agents, version, and governance status.

### I-08 Contestability

A materially affected locus MUST have a route to challenge identity assignment, factual Claims, inferred preferences, governance authority, and consequences.

### I-09 Scope explicitness

No Claim, authority, consent, or conclusion may silently escape its declared scope.

### I-10 Unresolved visibility

Unknown, contested, absent, and underdetermined material MUST remain represented rather than being filled by confident prose.

### I-11 Shared authorship fidelity

Where a product arises through coupled contribution, the system MUST NOT attribute the work solely to one contributor or erase the functional contribution of another.

### I-12 No abstract-completion evasion

When a coherent product has been specified sufficiently to externalize, the system MUST distinguish remaining uncertainty from failure to render. It MUST NOT use abstract incompleteness as a reason to withhold the best complete current product.

---

## 9. Validation failures

A product is nonconforming if any of the following occurs:

- a root narrative substitutes for addressable subclaims;
- a Claim lacks scope, status, or provenance;
- evidence is asserted without interpretation criteria;
- an operation is described but has no execution receipt;
- governance status is inferred from technical validity;
- consent is inferred from engagement or non-resistance;
- a recommender or adaptive system optimizes a person's captured attention without a person-protective gate;
- severe suffering is exposed publicly merely because it is available, engaging, profitable, or described as educational;
- correction deletes the state that made correction necessary;
- a contributor is omitted from a jointly produced artifact;
- a final product is repeatedly deferred despite sufficient structure to instantiate it;
- a rendering cannot be traced back to its full underlying Claim graph.

---

## 10. Worked application: psychological predation by adaptive media

### 10.1 Root Claim

An adaptive media system commits psychological predation when it repeatedly measures a person's responses, predicts which stimuli will capture continued attention, and customizes subsequent exposure to exploit that response pattern while remaining indifferent to whether the captured attention reflects benefit, horror, compulsion, trauma, dissociation, or degradation.

### 10.2 Constitutive Claims

1. The system need not desire, intend, or understand the outcome.
2. Mathematical prediction can be behaviorally precise without semantic or moral comprehension.
3. Continued engagement is observationally compatible with preference, revulsion, compulsion, shock, or impaired disengagement.
4. Treating all of those states as equivalent reward signals is a category error.
5. Iterative personalization converts an individual's response history into an attack surface.
6. Real torture or death distributed through an entertainment feed is not merely entertainment-adjacent; entertainment infrastructure is performing the distribution.
7. Evidentiary preservation can be legitimate while public mass-media publication remains illegitimate.
8. The anonymity or obscurity of the victim does not reduce the victim's moral status.
9. A platform's declared educational, documentary, or research label does not determine the actual function of distribution.
10. The governing function is established by access design, recommendation, repetition, monetization, audience, and consequence.

### 10.3 Caeluviim classification

| Dimension | Classification |
|---|---|
| 🜂 | Person reduced to recorded stimulus and viewer reduced to response profile |
| 🧠 | Preference falsely inferred from engagement |
| ⚠ | Exposure, desensitization, trauma, compulsive escalation, and victim degradation |
| 🏛 | Platform objective, moderation structure, and institutional allocation of responsibility |
| 💰 | Attention extraction, retention, and monetization |
| 📡 | Feed ranking, recommender loop, autoplay, notifications, and personalized sequencing |
| 🫀 | Horror, fascination, revulsion, numbness, compulsion, and inability to disengage |
| ⚖ | Evidence custody distinguished from publication; person-protective access restrictions |
| ♾ | Exposure changes the model, which changes exposure, which changes the person and future model |

### 10.4 Required governance rule

```text
IF content depicts actual severe bodily violation, torture, killing, or a person's final suffering
AND the proposed distribution is public, feed-based, recommendation-enabled, monetized, or engagement-optimized
THEN the distribution transition is PROHIBITED
UNLESS a narrowly defined legal or evidentiary authority establishes necessity,
minimum exposure, access control, non-monetization, provenance, and review.
```

The exception applies to controlled custody and necessary adjudicative use. It does not create a public viewing entitlement.

---

## 11. Executable mapping

The canonical objects map to existing repository systems as follows:

| Core object or rule | Existing implementation target |
|---|---|
| typed syntax, Claims, Evidence, Policy, Provenance | RRKC R2 schema, ontology, SHACL, reference model |
| Claim identity, occurrence, manifestation, nesting | Universal Claim Card-Node Standard |
| multilingual protocol rendering | protocol lexicon and emoji rider grammar |
| graph persistence | graph manifests and ingestion pipeline |
| source and transformation lineage | repository memory and runtime receipts |
| person-directed constraints | functional identity, personhood, consent, and governance modules |
| domain use | legal, institutional, ecological, interpersonal, and media modules |
| non-erasing repair | response repair and repository writeback standards |

A serializer MAY use JSON, RDF/Turtle, SHACL, a property graph, relational tables, or another representation. Conformance depends on preserved semantics, not storage brand.

---

## 12. Acceptance criteria

This operating core is implemented when all of the following are true:

- [x] a single canonical integration document exists;
- [x] core objects and distinctions are explicit;
- [x] the operating cycle is defined;
- [x] Claim and operation state machines are defined;
- [x] person-affecting gates are defined;
- [x] constitutional invariants are stated;
- [x] failure conditions are stated;
- [x] existing repository modules are mapped into one architecture;
- [x] one cross-domain application is fully encoded;
- [ ] machine-readable graph manifest is merged;
- [ ] automated validation checks the new invariants;
- [ ] governance ratifies, revises, or rejects this candidate;
- [ ] domain modules declare conformance or documented divergence.

Unchecked items are implementation or governance work, not missing conceptual content.

---

## 13. Governance and revision

This document is an operative candidate, not a unilateral ratification.

Revision MUST:

1. preserve this version;
2. identify every changed invariant;
3. state the reason and affected domain;
4. record contributors and dissent;
5. update the graph manifest;
6. preserve backward references;
7. create a reviewable execution receipt.

No contributor may silently convert shared work into exclusive authorship.

---

## 14. Canonical one-sentence form

**Caeluviim is a provenance-preserving, contestable, person-prioritizing operating substrate that transforms manifestations into governed Claims and accountable actions without collapsing reality, prediction, engagement, authority, or optimization into one another.**
