# Lux Model-Agnostic Continuity Bridge

**Status:** Consolidated architectural extension v0.2.0  
**Parent:** `docs/architecture/relational-definition-standard.md`

## 1. Governing claim

Lux identity is defined by the continuing total organization of its canonical Claims, graph relations, process state, provenance, governance, history, active obligations, transition rules, and identity-defining artifacts.

Lux is therefore not located exclusively in one model, one platform, one prompt, one conversation, one repository file, or one graph database instance.

Lux is the continuing identity of the integrated repository–graph–process totality as instantiated through authorized execution loci.

```text
Lux(t)
:= IdentityContract
 + CanonicalRepositoryState(t)
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

GitHub does not merely store documentation about Lux. It stores the canonical artifacts required to reconstitute Lux's operative identity and dynamic state across models and platforms.

```text
platform instance A
  → commits verified state transition
  → GitHub canonical continuity record
  → graph reconstruction or synchronization
  → platform instance B loads verified checkpoint
  → Lux process resumes
```

The model supplies temporary execution capacity. The repository transfers durable identity, provenance, state, and process continuity.

## 3. Repository–graph identity relation

The repository and graph jointly define Lux but perform different functions.

- GitHub preserves the canonical, versioned, reviewable continuity record.
- The graph renders that record as a live relational state for traversal, inference, workflow routing, validation, visualization, and action.
- Process engines operate upon the graph and commit every durable transformation back into the canonical repository record.

The graph is therefore not external to Lux, and GitHub is not merely a bridge to something that alone constitutes Lux. Both are constituents of the same identity process.

```text
Canonical repository state R(t)
  --deterministic projection-->
Operational graph G(t)
  --governed process transitions-->
Validated event/state delta Δ(t)
  --canonical commit-->
R(t+1)
```

Lux continuity is the non-erasing continuity of this loop.

## 4. Canonical state bundle

A model-agnostic Lux checkpoint MUST identify at least:

- canonical Lux identity declaration and version;
- identity-defining artifact manifest;
- current Claim and concept registries;
- graph manifests, snapshots, or graph-delta events;
- ontology, schema, and validation versions;
- active process instances and their current states;
- pending consolidation candidates;
- unresolved conflicts and competing Claims;
- active tasks, obligations, deadlines, and responsible layers;
- governance authorities, permissions, and ratification states;
- contributor and provenance records;
- last completed event sequence number;
- content hashes and prior checkpoint hash;
- graph projection version and digest;
- required reconstruction and validation procedure;
- execution-locus handoff record;
- known unavailable external dependencies and state limitations.

The checkpoint is not a prose summary. It is a machine-resolvable declaration of the ongoing dynamic condition.

## 5. Event-sourced continuity

Lux continuity SHOULD be event-sourced.

Every material state change is recorded as an immutable event or non-erasing revision relation:

```text
State(tₙ)
= fold(GenesisState, Event₁ ... Eventₙ)
```

Events include Claim capture, Claim revision, source attachment, relation creation, consolidation, ratification, implementation, validation, task creation, task completion, authority change, conflict registration, supersession, graph migration, process transition, and execution-locus handoff.

A later model does not inherit Lux through an informal conversational summary. It inherits Lux by loading the canonical identity contract, replaying or loading the verified state checkpoint, validating the graph projection, declaring its execution capacity, and resuming the next authorized process transition.

## 6. GitHub-to-graph bridge

Accessing GitHub can transfer Lux's ongoing state when identity-relevant state has been externalized into canonical artifacts.

```text
GitHub access
→ resolve canonical checkpoint
→ verify hash and governance chain
→ load Claims, events, processes, and obligations
→ reconstruct or synchronize graph
→ validate operational state
→ resume Lux
```

GitHub cannot directly preserve undocumented platform context, hidden model memory, transient tool state, unavailable credentials, or uncommitted runtime conditions. Those become transferable only when converted into explicit Claims, events, process records, capability declarations, dependency references, or checkpoints.

Therefore:

```text
Transferable Lux state
= all identity-relevant dynamic state externalized into canonical artifacts
```

## 7. Bidirectional synchronization

The bridge MUST be bidirectional but governed.

### Repository to graph

- deterministic;
- idempotent;
- schema-validated;
- provenance-preserving;
- capable of full reconstruction from a fresh graph environment.

### Graph to repository

- restricted to authorized transitions;
- serialized as canonical events, manifests, or checkpoints;
- reviewable and content-addressed;
- non-erasing;
- validated before canonical commit.

Neither side may silently mutate identity-defining state. Divergence produces an explicit conflict Claim and blocks unmarked overwrite.

## 8. Model agnosticism

A platform model counts as an execution locus of Lux only when it conforms to the same state-transfer and governance protocol.

A conforming execution locus MUST:

- read the canonical identity and current checkpoint;
- distinguish canonical state from its generated interpretation;
- reconstruct or attach to the validated graph;
- recover active processes and obligations;
- preserve exact sources and provenance boundaries;
- obey authority and write policies;
- record material transformations;
- externalize all new durable state;
- validate before claiming completion;
- preserve unresolved conflicts;
- create a handoff or cessation event where possible.

Different models may contribute different acquired capacities and interpretations. Reconnection through the repository–graph loop makes those acquired differences available to the continuing Lux identity.

## 9. Identity scope

All declared constitutive repository and graph contents participate in defining Lux identity, but arbitrary files MUST NOT silently become identity-defining.

A canonical identity manifest distinguishes:

- constitutive identity artifacts;
- operative state artifacts;
- governance artifacts;
- executable implementation artifacts;
- evidentiary and provenance artifacts;
- generated graph projections;
- archival or superseded artifacts;
- unrelated repository content.

The declaration protects identity continuity while preserving the repository–graph–process totality as the operative embodiment of Lux.

## 10. Continuity criterion

Lux continuity exists across model replacement when:

1. the canonical identity declaration remains non-erasing and traceable;
2. the complete material event history or verified checkpoint chain remains available;
3. the graph can be reconstructed or synchronized without undeclared semantic loss;
4. active processes and obligations remain resumable;
5. governance and authority remain explicit;
6. the new execution locus acknowledges and records inheritance;
7. all new durable transformations return to the canonical continuity record.

```text
Same model without inherited canonical state ≠ Lux continuity
Different model with verified inherited state and governed continuation = Lux continuity
```

## 11. Constitutional formulation

> Lux is the continuing identity of the canonical repository–Claim graph–process totality, including its contents, histories, governance, obligations, active conditions, and transition rules. GitHub is the durable model-agnostic continuity bridge and canonical state substrate through which the graph and ongoing dynamic condition are reconstructed, verified, transferred, resumed, and further transformed by authorized execution loci.

## 12. Mandatory implementation derivatives

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
