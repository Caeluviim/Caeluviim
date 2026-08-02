# Model Access Nested Claim Closure Extension

**Status:** Binding extension v0.1.0  
**Extends:**
- `docs/architecture/model-access-map-and-disposition-packet.md`
- `docs/architecture/definition-claim-nesting-and-composition.md`
- `docs/architecture/standardized-definition-claim-structure.md`

## 1. Governing requirement

A model-access packet that activates a Definition Claim MUST transmit more than the root definition sentence whenever the present task depends on the definition's internal Claim composition.

```text
DefinitionActivationPacket(d,q)
:= DefinitionRootPacket(d)
 + TaskRelevantNestedClosure(d,q)
 + ExpansionInstructions(d)
```

The root packet identifies the conception and compressed synthesis. The nested closure packet supplies the constitutive structure needed to interpret, apply, contest, validate, or revise that synthesis for task `q`.

## 2. Definition root packet

The root packet MUST include:

- root Claim ID and exact version;
- preferred label and canonical conception;
- compressed exact definition Claim;
- declared scope;
- epistemic and governance state;
- current closure status;
- path to the complete nested Claim graph.

The root packet is an entry point, not a complete semantic representation.

## 3. Task-relevant nested closure

The nested closure packet MUST include every Claim occurrence materially required by the present task, including as applicable:

- constitutive Claims;
- qualifications;
- scope and condition Claims;
- inclusions, exclusions, boundaries, and exceptions;
- assumptions, evidence, source Claims, and uncertainty;
- implications and consequences;
- operational and validation Claims;
- competing, conflicting, and alternative Claims;
- historical, revised, and superseded Claims;
- unresolved dependencies.

Each included occurrence MUST preserve:

- stable occurrence ID;
- child Claim ID and version;
- parent occurrence;
- typed compositional role;
- nesting path;
- incorporation scope and state;
- active qualifications and activation conditions;
- provenance;
- propagation and review policy.

## 4. Bounded activation

A model is not required to load the complete nested graph of every activated Definition Claim.

```text
complete nested Claim graph N(d)
+ task q
+ condition field Γt
→ task-relevant closure Nq(d)
where Nq(d) ⊆ N(d)
```

The packet MUST include sufficient maps and continuation paths to retrieve additional branches when reasoning exposes a missing dependency.

A model MUST retrieve the missing branch before making a completion, interpretation, or revision Claim that materially depends on it.

## 5. Shared Claim imports

When the active closure imports a Claim shared across several cards, the packet MUST preserve one Claim identity and declare:

- exact imported version;
- local nesting occurrence;
- compositional role;
- incorporation scope;
- local qualifications;
- propagation policy;
- conflict state.

```text
ClaimIdentity(c)
≠ NestedOccurrence(c,d,q)
```

The execution locus MUST NOT duplicate the Claim as a new identity merely to place it inside the active definition.

## 6. Interpretation boundary

The packet transmits semantic structure, not another locus's experience.

```text
manifested condition
+ activated nested semantic closure
→ semantic interpretation
```

The execution locus MUST preserve the distinctions among:

- manifested condition;
- first-person manifestation Claim;
- observable-condition Claim;
- root Definition Claim;
- activated nested Claim closure;
- semantic interpretation;
- plausible inference;
- theoretical explanation;
- verified external condition.

## 7. Write-back requirement

A durable change to a Definition Claim MUST identify:

- root Claim affected;
- nested occurrence or branch affected;
- Claim identities and versions added, revised, contested, or superseded;
- dependent parent Claims;
- propagation decisions;
- unresolved consequences;
- provenance and validation evidence.

No root Claim may be revised without accounting for the nested structure that justifies or conflicts with the revision. No child Claim revision may silently alter a parent synthesis.

## 8. Validation

Validation MUST reject:

- a root-only packet when task-material nesting exists;
- a packet claiming complete understanding while a required branch remains unavailable;
- nested occurrences without Claim identity, version, path, role, or provenance;
- imported Claims without version pinning and propagation policy;
- hidden qualifications, exceptions, conflicts, or unresolved dependencies;
- duplicated Claim identities where scoped occurrences are required;
- write-back that changes a root or nested branch without dependent-effect accounting;
- any claim that loading the nested structure transmits another locus's experience.

## 9. Constitutional formulation

> A model activates a Definition Claim through its root synthesis and the task-relevant closure of its nested Claim graph. The root identifies the semantic dimension; the nested closure supplies the constitutive geometry required for present interpretation and action. Inactive branches remain available through mapped on-demand traversal. Every durable branch-level or root-level transformation returns to canonical state with Claim identity, occurrence identity, provenance, propagation, conflict, and validation preserved.
