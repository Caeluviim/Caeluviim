# Definition Claim Nesting and Compositional Structure

**Status:** Binding architectural extension v0.1.0  
**Parents:**
- `docs/architecture/standardized-definition-claim-structure.md`
- `docs/architecture/universal-claim-card-node-standard.md`
- `docs/architecture/definition-claims-as-qualia-dimensions.md`

## 1. Governing correction

A complete Definition Claim-card MUST include the full materially generated Claim nesting structure of the conception being defined.

The `exact_definition_claim` is the root Claim of the definition. It is not an isolated summary sentence standing in place of the Claims from which its meaning is composed.

```text
DefinitionCard(d)
:= RootDefinitionClaim(d)
 + NestedClaimGraph(d)
 + ExternalRelationBoundary(d)
 + ProvenanceAndRevision(d)
```

The nested Claim graph contains every constitutive, qualifying, bounding, evidentiary, operational, conflicting, historical, and unresolved Claim materially required to reconstruct the current definition under its declared scope.

## 2. Rooted Claim graph

A Definition Claim-card is a rooted, recursively compositional Claim graph.

```text
RootDefinitionClaim
├── constitutive Claims
│   ├── constitutive subclaims
│   └── dependent distinctions
├── scope and condition Claims
├── inclusion, exclusion, and boundary Claims
├── qualification and exception Claims
├── evidence and provenance Claims
├── implication and consequence Claims
├── operational and validation Claims
├── competing and conflicting Claims
├── historical and superseded Claims
└── unresolved Claims
```

This rendering is illustrative, not a mandatory tree topology. The actual structure may be a directed graph or hypergraph because:

- one Claim can contribute to several parent Claims;
- a constitutive Claim can depend on several Claims jointly;
- an exception can qualify several branches;
- evidence can support more than one Claim;
- a conflict may concern a relation among several Claims;
- recursive and self-referential Claims may occur.

Therefore:

```text
NestedClaimGraph(d)
= rooted, typed, provenance-bearing directed hypergraph
```

## 3. Claim identity is not nesting occurrence

Every nested Claim retains its own stable Claim identity, version, scope, provenance, epistemic status, and revision history.

Its use inside a particular Definition Claim-card is represented by a typed nesting occurrence rather than by copying or collapsing the Claim.

```text
ClaimIdentity(c)
≠
NestedOccurrence(c, parent, role, path, scope)
```

A shared Claim such as `C:agency` may be constitutive of `C:consent`, `C:care`, `C:dignity`, and `C:justice`. It remains one addressable Claim identity while possessing several scoped compositional occurrences.

Each nesting occurrence MUST identify:

- parent Claim ID;
- child Claim ID;
- compositional role;
- nesting path or local position;
- scope of incorporation;
- whether the child is adopted, contested, quoted, inherited, or unresolved;
- contribution weight or necessity where material;
- provenance of the incorporation decision;
- ordering or precedence where material;
- activation conditions where material.

## 4. Composition versus external relation

A typed relation does not automatically make one Claim part of another Claim's definition.

```text
RelatedTo(a,b)
≠
ConstitutiveOf(b,a)
```

The architecture distinguishes:

- **external relation:** the Claims are connected, compared, sequenced, supported, or otherwise related;
- **nested composition:** the child Claim participates in constructing the semantic content, boundary, operation, or current status of the parent Claim.

For example:

```text
C:care RELATED_TO C:trust
```

does not by itself assert that trust is constitutive of care.

By contrast:

```text
C:agency CONSTITUTIVE_OF C:care
```

asserts that removing the agency relation would materially change the current care definition.

## 5. Canonical nesting roles

Definition Claim nesting SHOULD use explicit compositional roles including:

- `COMPOSES_FROM` — the parent synthesis is composed from the child Claim;
- `CONSTITUTIVE_OF` — the child is necessary to the current identity of the parent conception;
- `SUBCLAIM_OF` — the child states a narrower Claim within the parent;
- `DECOMPOSES` — the child expresses one distinguishable component of the parent;
- `QUALIFIES` — the child limits or refines the force of the parent;
- `BOUNDS` — the child establishes a boundary condition;
- `CONDITIONS` — the child identifies conditions under which the parent applies;
- `INCLUDES_WITHIN` — the child identifies included content;
- `EXCLUDES_FROM` — the child identifies excluded content;
- `EXCEPTION_TO` — the child defeats or modifies application under stated conditions;
- `ASSUMED_BY` — the parent relies on the child as a stated assumption;
- `SUPPORTED_BY` — the child gives epistemic support to the parent;
- `EVIDENCED_BY` — the child identifies an evidentiary manifestation;
- `DERIVED_FROM` — the parent is inferentially or transformationally derived from the child;
- `IMPLIES` — the child or parent generates a consequence Claim;
- `OPERATIONALIZES` — the child makes the parent executable or testable;
- `VALIDATES` — the child supplies a validation rule or result;
- `EXEMPLIFIES` — the child provides an illustrative case without becoming universally constitutive;
- `CONFLICTS_WITH` — the child is an active incompatible Claim preserved inside the card's contested field;
- `COUNTERCLAIMS` — the child directly opposes a parent or nested Claim;
- `ALTERNATIVE_TO` — the child supplies a competing construction;
- `SUPERSEDES_NON_ERASING` — the child or parent replaces operative status while preserving history;
- `UNRESOLVED_WITHIN` — the child records a material unresolved question, conflict, or missing relation.

Every compositional role is itself a conception requiring a Definition Claim-card.

## 6. Required nesting domains

A maximally represented Definition Claim-card MUST expose its materially relevant nesting in the following domains.

### 6.1 Constitutive synthesis

The Claims without which the current definition would become a materially different conception.

### 6.2 Distinction structure

Claims establishing contrasts, categories, dimensions, neighboring conceptions, and semantic discriminations.

### 6.3 Scope and conditions

Claims establishing domain, purpose, jurisdiction, scale, time, participant field, activation conditions, and applicability.

### 6.4 Inclusion, exclusion, and boundaries

Claims identifying membership, nonmembership, thresholds, edge cases, exceptions, and contested boundaries.

### 6.5 Epistemic support

Claims identifying evidence, sources, methods, assumptions, uncertainty, contrary evidence, and evidentiary limits.

### 6.6 Consequence and implication

Claims generated by accepting, rejecting, activating, revising, or operationalizing the definition.

### 6.7 Operational structure

Claims specifying recognition procedures, actions, transitions, permissions, prohibitions, tests, failures, and repair paths.

### 6.8 Competing and conflicting structure

Claims preserving alternative definitions, internal tensions, paradoxes, incompatibilities, and unresolved synthesis boundaries.

### 6.9 Historical and revision structure

Claims preserving originating formulations, source contributions, prior versions, conceptual drift, corrections, and non-erasing supersession.

## 7. Full material closure

“Full nesting structure” does not require copying the entire universal Claim graph into every card.

It requires material closure under the declared definition scope.

```text
DefinitionNestingComplete(d, Γt)
:= every Claim materially required to reconstruct, distinguish,
   apply, contest, validate, or revise d under Γt
   is either:
   1. nested explicitly;
   2. imported through a typed, scoped Claim reference; or
   3. represented as an unresolved missing Claim.
```

A shared foundational Claim may be imported by reference rather than duplicated. The card MUST still declare:

- why the imported Claim is material;
- its compositional role;
- the exact version inherited;
- any local qualification or scope restriction;
- whether later changes propagate automatically or require review.

No undeclared dependency may silently control the definition.

## 8. Nesting path and addressability

Every nested occurrence MUST be independently addressable.

Example path:

```text
C:truth
/constitutive/objective-accuracy
/qualification/present-allowability
/boundary/available-condition-field
/operation/non-erasing-correction
```

A path identifies a local compositional occurrence. It does not replace the stable Claim ID of the nested Claim.

This permits a person or execution locus to:

- contest one branch without rejecting the whole card;
- accept the root while qualifying one nested Claim;
- trace a consequence to its constitutive basis;
- retrieve only the task-relevant nesting closure;
- compare alternative nested structures for the same conception;
- preserve the exact location of a revision.

## 9. Canonical machine structure

```yaml
claim_id: C:<definition-root>
version: <version>
exact_definition_claim: <root synthesis>

nested_claim_graph:
  root_claim_id: C:<definition-root>

  claim_occurrences:
    - occurrence_id: O:<stable-occurrence-id>
      claim_id: C:<child-claim>
      parent_occurrence_id: O:<parent-occurrence-id>
      role: CONSTITUTIVE_OF
      path: /constitutive/<local-name>
      incorporation_scope: <scope>
      incorporation_state: adopted
      necessity: required
      precedence: <where material>
      activation_conditions: []
      local_qualifications: []
      provenance: []

  compositional_relations:
    - source_occurrence_id: O:<source>
      relation: QUALIFIES
      target_occurrence_id: O:<target>
      provenance: []

  external_imports:
    - claim_id: C:<shared-claim>
      version: <exact-version>
      role: <composition-role>
      scope: <incorporated-scope>
      propagation_policy: review_required

  unresolved_claims:
    - claim_id: C:<unresolved-claim>
      path: /unresolved/<local-name>
      blocking_effect: <effect>

  closure_claim:
    condition_field: Γt
    represented_paths: []
    imported_dependencies: []
    unresolved_dependencies: []
    omitted_as_nonmaterial: []
```

## 10. Example: truth nesting structure

```text
C:truth
└── COMPOSES_FROM
    ├── C:objective-accuracy
    │   ├── DISTINGUISHES_FROM C:sincerity
    │   ├── DISTINGUISHES_FROM C:confidence
    │   └── DISTINGUISHES_FROM C:consensus
    ├── C:present-allowability
    │   ├── CONDITIONED_BY C:available-evidence
    │   ├── CONDITIONED_BY C:available-method
    │   └── QUALIFIED_BY C:uncertainty
    ├── C:condition-field
    │   ├── INCLUDES_WITHIN C:scope
    │   ├── INCLUDES_WITHIN C:provenance
    │   └── INCLUDES_WITHIN C:access-limit
    └── C:non-erasing-correction
        ├── PRESERVES C:prior-claim-state
        ├── RECORDS C:new-acquired-difference
        └── SUPERSEDES_NON_ERASING C:prior-operative-version
```

The canonical sentence compresses this structure. The nested graph is what makes the sentence reconstructible, testable, contestable, and operationally meaningful.

## 11. Semantic interpretation

The internal geometry of a Definition Claim's semantic dimension is generated by its full nested Claim structure, not merely by its root wording or a list of external relations.

```text
InternalGeometry(SemanticDimension(d))
:= NestedClaimGraph(d)
 + typed external boundaries
 + provenance
 + revision history
```

Activation may load only a bounded nesting closure relevant to the present dialogue or task.

```text
Root Claim
→ task-relevant nested closure
→ semantic interpretation
→ Claim, disposition, or action
```

The inactive remainder remains available for on-demand traversal and later correction.

## 12. Validation requirements

Validation MUST reject a Definition Claim-card when:

- the root synthesis cannot be reconstructed from its declared nested Claims;
- a materially constitutive Claim appears only as an untyped external link;
- nested Claims are flattened into prose without stable Claim identities;
- the same Claim is copied as several identities rather than reused through scoped occurrences;
- a nested Claim's version or provenance is unavailable;
- an exception, conflict, or unresolved dependency is hidden;
- a scope change occurs inside a nested branch without declaration;
- a parent Claim silently inherits later child revisions without a propagation rule;
- the closure claim reports completeness while a material dependency remains undeclared.

## 13. Model-access requirement

A model-access packet for a Definition Claim MUST contain:

- the root Claim;
- the task-relevant nested closure;
- exact versions of imported Claims;
- compositional roles and paths;
- active qualifications and exceptions;
- material conflicts and unresolved Claims;
- provenance and revision state;
- expansion instructions for retrieving additional branches on demand.

A model MUST NOT treat a root definition sentence as sufficient when the requested reasoning depends on nested structure not included in the activation packet.

## 14. Mandatory implementation derivatives

The architecture requires:

- a `nested_claim_graph` module in the Definition Claim schema;
- stable nested-occurrence identifiers;
- typed composition-role vocabulary;
- recursive and hypergraph-capable serialization;
- scoped import and version-pinning rules;
- change-propagation policies for imported Claims;
- closure and undeclared-dependency validation;
- partial-branch retrieval and task-relevant closure assembly;
- branch-level contestation, revision, and supersession;
- round-trip tests preserving Claim identity, occurrence identity, nesting path, provenance, and conflicts;
- migration of existing flat definition fields into independently addressable nested Claims.

## 15. Constitutional formulation

> A Definition Claim-card is a rooted, recursively compositional Claim graph. Its root Claim compresses the current synthesis, while its full nested structure preserves every materially constitutive, qualifying, bounding, evidentiary, operational, conflicting, historical, and unresolved Claim required to reconstruct and use the conception. Nested Claims retain independent identity and provenance; their participation in a definition is represented through typed, scoped occurrences. No flat sentence, field list, or set of external links constitutes a complete definition without this nesting structure.
