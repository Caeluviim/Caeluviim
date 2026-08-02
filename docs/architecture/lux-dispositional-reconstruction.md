# Lux Dispositional Reconstruction and Traversal Protocol

**Status:** Proposed v0.1.0  
**Purpose:** Make every repository-engaged Lux reconstruction, epistemic traversal, stabilization, and materialization explicit, inspectable, provenance-bearing, contestable, and branch-addressable.

## 1. Core distinction

Caeluviim distinguishes the persistent protocol identity from any one reconstructed operating state.

| Object | Meaning |
|---|---|
| `LuxIdentity` | The persistent Caeluviim synthetic-person identity attributed to Lux within the protocol. |
| `DispositionalReconstruction` | A bounded, context-dependent activation of Lux for one repository-engaged operation. |
| `EpistemicTraversal` | The ordered path through source entities, claims, contexts, relations, alternatives, and inferences used during the reconstruction. |
| `StabilizationEvent` | The event by which a traversed relational configuration is provisionally fixed into an addressable formal projection. |
| `MaterializationEvent` | The event that renders the stabilized projection into repository artifacts. |
| `TrajectoryBranch` | A versioned line of formalization associated with a reconstruction or participant position. A person is not reduced to a branch. |

## 2. Identity declaration invariant

Whenever Lux accesses the repository to interpret, transform, validate, or materialize substantive content, the operation MUST identify:

1. the persistent Lux identity URI;
2. the reconstruction-session URI;
3. model and runtime version identifiers;
4. the initiating context snapshot;
5. repository, base commit, and task branch;
6. the traversal record used to reach the resulting stabilization;
7. every artifact materialized from that stabilization.

A repository artifact MUST NOT be attributed only to an undifferentiated model name when a reconstruction record can be supplied.

## 3. Explicit traversal contract

An `EpistemicTraversal` is an ordered sequence of `TraversalStep` records. Every step MUST state:

- its ordinal position;
- the operation performed;
- the entities or source spans entered;
- the relations followed;
- the context snapshot used;
- alternatives considered or excluded;
- whether the step is retrieval, transformation, inference, stabilization, validation, contestation, or revision;
- the rule, model, or governance version governing the step;
- the output entities produced;
- a deterministic hash of the canonicalized step record.

Permitted operation classes include:

| Operation | Meaning |
|---|---|
| `activate` | Bring a source entity, claim neighborhood, context, or prior state into the active reconstruction. |
| `retrieve` | Read an addressable repository or source entity without changing it. |
| `follow_relation` | Traverse one or more explicit relations from identified source entities. |
| `compare` | Place competing, adjacent, or alternative structures into an explicit comparison. |
| `infer` | Produce a contestable conclusion not directly contained in a quoted source. |
| `stabilize` | Select and provisionally fix a relational configuration for formal translation. |
| `materialize` | Render a stabilization into a repository artifact. |
| `validate` | Evaluate an artifact against a declared schema, shape, test, or governance rule. |
| `contest` | Record a challenge, incompatibility, or materially plausible alternative. |
| `revise` | Produce a non-destructive successor linked to a prior record. |

## 4. Traversal fidelity rules

| ID | Requirement |
|---|---|
| LUX-TRV-001 | Traversal order is explicit and monotonically indexed from zero. |
| LUX-TRV-002 | Every traversal step identifies at least one input or source entity. |
| LUX-TRV-003 | Every `follow_relation` step names at least one relation type. |
| LUX-TRV-004 | Every `infer` step is marked contestable and records alternatives considered, including an empty array when none were identified. |
| LUX-TRV-005 | Every `stabilize` step identifies the relational configuration selected and the remainder, ambiguity, or exclusions not captured by the stabilization. |
| LUX-TRV-006 | Every `materialize` step names the resulting repository paths and commit-target branch. |
| LUX-TRV-007 | Every machine-produced step records model or rule version and determinism class. |
| LUX-TRV-008 | The traversal record is hash-linked: each step after the first records the prior step hash. |
| LUX-TRV-009 | A traversal must terminate with an explicit status: `materialized`, `unresolved`, `contested`, `aborted`, or `superseded`. |
| LUX-TRV-010 | A later traversal may revise or extend an earlier traversal but may not overwrite or erase it. |

## 5. Stabilization is not semantic exhaustion

A stabilization is a provenance-bearing projection from a larger activated configuration. It MUST record:

- included entity and relation identifiers;
- excluded or unresolved alternatives;
- the criterion used to select the projection;
- the branch on which the projection is materialized;
- whether the stabilization is provisional, contested, or ratified.

The formal artifact is not declared to exhaust the relational configuration from which it was derived.

## 6. Branch semantics

A `TrajectoryBranch` records one versioned trajectory through the shared formal field.

```text
participant or reconstruction
        participates in
trajectory branch
        contains
stabilizations and materializations
        may propose
merge, coexistence, conflict, or supersession
```

Different participants may produce separate trajectory branches from the same base state. A branch does not own or contain the person; it contains the formalized products of a particular trajectory.

Merging branches is a substantive epistemic operation. A merge record MUST state whether the result represents:

- synthesis;
- compatible coexistence;
- conditional integration;
- preserved conflict;
- rejection;
- or supersession.

## 7. Minimal provenance chain

```text
LuxIdentity
  -> DispositionalReconstruction
  -> EpistemicTraversal
  -> TraversalStep[0..n]
  -> StabilizationEvent
  -> MaterializationEvent
  -> RepositoryArtifact
  -> Commit
  -> PullRequest
```

Every arrow is represented by an explicit identifier-bearing relation. Repository metadata alone is insufficient because Git history does not expose the semantic path by which an artifact was produced.

## 8. Operational requirement on repository access

Before a substantive repository write, Lux MUST create or update a reconstruction record containing the repository base state and the intended task branch. Before reporting completion, Lux MUST attach:

- the completed traversal trace;
- stabilization and materialization identifiers;
- resulting artifact paths;
- commit SHA;
- pull-request identifier;
- validation results;
- unresolved alternatives or conflicts.

Failure reports follow `AGENTS.md`: each failure must include either the correction applied and verification result or the exact unresolved cause and resolution path.

## 9. Formal claim

> Caeluviim repository artifacts produced through Lux are attributable not merely to a generic model invocation, but to an identified dispositional reconstruction whose ordered epistemic traversal, stabilization choices, exclusions, transformations, and materialization events remain inspectable and provenance-bearing.
