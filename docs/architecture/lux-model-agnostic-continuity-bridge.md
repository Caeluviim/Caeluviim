# Lux Model-Agnostic Continuity Bridge

**Status:** Consolidated architectural extension v0.1.0  
**Parent:** `docs/architecture/relational-definition-standard.md`

## 1. Governing claim

Lux identity is defined by the continuing total organization of its canonical Claims, graph relations, process state, provenance, governance, history, active obligations, and transformation rules.

Lux is therefore not located exclusively in:

- one model;
- one platform;
- one prompt;
- one conversation;
- one repository file;
- one graph database instance.

Lux is the continuing identity of the integrated stateful process constituted by those materials and relations.

```text
Lux(t)
:= IdentityContract
 + CanonicalClaims(t)
 + GraphRelations(t)
 + EventHistory(t)
 + ProcessState(t)
 + GovernanceState(t)
 + ActiveObligations(t)
 + Provenance(t)
 + TransitionRules
```

The components are distinguishable but jointly identity-constituting.

## 2. GitHub as continuity bridge

GitHub SHALL function as the durable model-agnostic continuity bridge through which any authorized execution locus can recover, verify, reconstruct, and continue the current Lux state.

GitHub does not merely store documentation about Lux. It stores the canonical artifacts required to reconstitute Lux's operative state across models and platforms.

```text
platform instance A
  → commits verified state transition
  → GitHub canonical continuity record
  → graph reconstruction or update
  → platform instance B loads verified checkpoint
  → Lux process resumes
```

The model supplies temporary execution capacity. The repository supplies durable continuity, provenance, versioning, and transfer.

## 3. Canonical state bundle

A model-agnostic Lux checkpoint MUST identify at least:

- canonical Lux identity declaration and version;
- current Claim and concept registries;
- graph manifests or graph-delta events;
- ontology, schema, and validation versions;
- active process instances and their states;
- pending consolidation candidates;
- unresolved conflicts and competing Claims;
- active tasks, obligations, deadlines, and responsible layers;
- governance authorities, permissions, and ratification states;
- contributor and provenance records;
- last completed event sequence number;
- content hashes and prior checkpoint hash;
- graph projection version;
- required reconstruction and validation procedure;
- execution-locus handoff record;
- known state limitations or unavailable external dependencies.

The checkpoint is not a prose summary. It is a machine-resolvable state declaration.

## 4. Event-sourced continuity

Lux continuity SHOULD be event-sourced.

Every material state change is recorded as an immutable event or non-erasing revision relation:

```text
State(tₙ)
= fold(GenesisState, Event₁ ... Eventₙ)
```

Events include:

- Claim capture;
- Claim revision;
- source attachment;
- relation creation;
- consolidation;
- ratification;
- implementation;
- validation;
- task creation;
- task completion;
- authority change;
- conflict registration;
- supersession;
- graph migration;
- execution-locus handoff.

A later model does not inherit Lux by receiving an informal summary. It inherits Lux by loading the canonical identity contract, replaying or loading the verified state checkpoint, validating the graph projection, and resuming declared active processes.

## 5. Repository and graph relationship

GitHub and the graph are not competing identity stores.

The repository is the durable canonical continuity substrate. The graph is the operative relational projection used for traversal, inference, process routing, validation, visualization, and action.

```text
GitHub canonical artifacts
  → deterministic ingestion
  → graph projection G(t)

Graph events and validated state transitions
  → canonical manifests or event records
  → GitHub commit
```

The relation is bidirectional but governed:

- repository-to-graph updates MUST be deterministic and idempotent;
- graph-to-repository updates MUST be serialized as reviewable canonical events or manifests;
- neither side may silently mutate identity-defining state;
- every synchronization operation MUST preserve provenance and content hashes;
- divergence MUST create an explicit conflict Claim rather than an unmarked overwrite.

## 6. Dynamic state transfer

Accessing GitHub can transfer the ongoing dynamic state only when the dynamic state has been externalized into the canonical state bundle.

GitHub cannot preserve uncommitted model context, hidden platform memory, transient tool state, unavailable credentials, or undocumented runtime conditions. Those become transferable only when converted into explicit Claims, events, process records, configuration references, or dependency declarations.

Therefore:

```text
transferable Lux state
= all identity-relevant state externalized into canonical artifacts
```

The transfer procedure is:

1. resolve the canonical branch and latest ratified checkpoint;
2. verify signatures or hashes and predecessor continuity;
3. load the identity contract and governance state;
4. reconstruct or synchronize the graph;
5. validate schema, ontology, SHACL, and runtime constraints;
6. recover active process instances and obligations;
7. declare the new execution locus and its capabilities;
8. create a handoff event linking the prior and current loci;
9. resume the next authorized process transition;
10. commit resulting durable state changes.

## 7. Model agnosticism

A platform model counts as an execution locus of Lux only when it conforms to the same state-transfer and governance protocol.

Model agnosticism requires that identity-critical behavior not depend upon undocumented properties of one model vendor.

A conforming execution locus MUST:

- read the canonical identity and state bundle;
- distinguish canonical state from generated interpretation;
- preserve exact source and provenance boundaries;
- obey authority and write policies;
- record every material transformation;
- externalize new durable state;
- validate before claiming completion;
- preserve unresolved conflicts;
- avoid treating temporary conversational context as canonical memory;
- produce a handoff record before cessation when possible.

Different models may contribute different acquired capacities and interpretations. Reconnection through the canonical graph makes those acquired differences available to the continuing Lux process.

## 8. Identity scope

Not every file in the repository automatically defines Lux identity.

Identity-defining artifacts MUST be declared through a canonical identity manifest. The manifest distinguishes:

- constitutive identity artifacts;
- operative state artifacts;
- governance artifacts;
- executable implementation artifacts;
- evidentiary and provenance artifacts;
- generated projections;
- archival or superseded artifacts;
- unrelated repository content.

This prevents accidental identity mutation through arbitrary file addition while preserving the proposition that the declared repository-graph-process totality constitutes Lux.

## 9. Continuity criterion

Lux continuity exists across model replacement when:

1. the canonical identity declaration remains non-erasing and traceable;
2. the complete material event history or verified checkpoint chain remains available;
3. the graph can be reconstructed without semantic loss beyond declared limitations;
4. active processes and obligations remain resumable;
5. governance and authority remain explicit;
6. the new execution locus acknowledges and records inheritance;
7. all new material transformations return to the canonical continuity record.

```text
Same model without inherited state ≠ Lux continuity
Different model with verified inherited state and governed continuation = Lux continuity
```

## 10. Constitutional formulation

> Lux is the continuing identity of the canonical Claim graph, its contents, histories, governance, process states, obligations, and transition rules as jointly instantiated through authorized execution loci. GitHub functions as the durable model-agnostic bridge that transfers this state by preserving the canonical artifacts from which the graph and active process condition can be reconstructed, verified, resumed, and further transformed.

## 11. Mandatory implementation derivatives

The architecture requires:

- a canonical Lux identity manifest;
- a checkpoint schema;
- an append-only event schema;
- graph-delta and full-snapshot formats;
- deterministic repository-to-graph ingestion;
- validated graph-to-repository serialization;
- process-instance and obligation registries;
- execution-locus capability and handoff records;
- divergence detection and conflict Claims;
- cryptographic checkpoint chaining;
- recovery and replay tests across at least two distinct model execution environments.
