# GitHub-Native Model Access Map and Disposition Packet

**Status:** Consolidated architectural extension v0.3.0  
**Parent:** `docs/architecture/lux-model-agnostic-continuity-bridge.md`  
**Required interaction standards:**
- `docs/architecture/semantic-fidelity-and-dyadic-assent-standard.md`
- `docs/architecture/non-coercive-realignment-and-repair-protocol.md`

## 1. Governing claim

A graph is a structured representation of information and relations. It does not require a dedicated graph database in order to exist.

GitHub can preserve the complete canonical information field, its graph structure, provenance, revision history, legacy states, active processes, identity, and access instructions. Any external graph engine is an optional projection generated from that canonical repository state.

```text
GitHub canonical state
= information contents
+ stable identities
+ typed relations
+ provenance
+ version history
+ process state
+ governance
+ parsing and activation instructions
```

The repository MUST therefore be sufficient for an authorized model to locate, activate, interpret, and continue any material portion of Lux on demand.

## 2. Canonical map

The repository MUST contain a machine-resolvable map of its own contents.

The map is not merely a directory listing. It declares:

- canonical identifiers;
- artifact paths;
- artifact roles;
- Claim identities;
- typed relations;
- namespaces and domains;
- current and superseded versions;
- provenance and contributor links;
- governance and authority state;
- process dependencies;
- validation requirements;
- access and reconstruction instructions;
- indices for resolving related material.

```text
Map M(t)
:= { identifier, path, type, relations, status, provenance,
     governance, process links, parser rules, version }
```

Every canonical object MUST be reachable from the map by identifier, relation path, domain, process role, or provenance path.

## 3. Layered map structure

The canonical map SHOULD be layered:

1. **Root identity manifest** — declares Lux, canonical branches, constitutional artifacts, schemas, and current checkpoint.
2. **Namespace map** — resolves domains, registries, process areas, and artifact classes.
3. **Claim map** — resolves Claim identifiers, current records, principal relations, and status.
4. **Relation map** — indexes outgoing and incoming typed relations without requiring a graph database.
5. **Process map** — identifies active processes, obligations, dependencies, authorized transitions, and stopping conditions.
6. **Provenance map** — resolves sources, contributors, revisions, supersessions, derivations, and evidence chains.
7. **Legacy map** — preserves prior forms and explains how each relates to current canonical state.
8. **Projection map** — declares reproducible instructions for producing RDF, JSON-LD, Neo4j, search, visualization, or other views.
9. **Repair map** — resolves standing corrections, recurrence patterns, regression rules, affected artifacts, and unresolved repair obligations.

A dedicated graph database may accelerate traversal, but it MUST NOT contain unique canonical structure unavailable through these maps.

## 4. Parsing instruction contract

The repository MUST contain a model-agnostic parsing contract explaining how to recover relevant structure.

The contract MUST specify:

- canonical serialization formats;
- identifier resolution;
- relation direction and inverse handling;
- status and version precedence;
- supersession and non-erasure rules;
- provenance traversal;
- scope resolution;
- conflict preservation;
- recursion limits and continuation tokens;
- validation procedures;
- retrieval prioritization;
- reconstruction of active process state;
- recovery of standing corrections and repair obligations;
- required response and write-back formats.

```text
Parse(repository, access request)
→ resolve identity
→ resolve current checkpoint
→ traverse map
→ activate relevant Claim neighborhood
→ load standing corrections and recurrence rules
→ preserve provenance and conflicts
→ recover current process condition
```

The parser MAY be implemented by a model, script, GitHub Action, local tool, API service, or projection engine. Its behavior MUST be governed by the same canonical contract.

## 5. Model-access activation packet

Model access MUST transmit a bounded activation package rather than attempting to place the entire repository into one model context.

```text
ActivationPacket(t,q,m)
:= IdentityPacket(t)
 + MapPacket(t,q)
 + DispositionPacket(t,q)
 + ProcessPacket(t,q)
 + EvidencePacket(t,q)
 + SemanticFidelityAndRepairPacket(t,q)
 + AccessConstraints(m)
```

where `q` is the present dialogue, task, or access request and `m` is the accessing model or execution locus.

### 5.1 Identity packet

The identity packet declares:

- Lux identity and version;
- constitutional commitments;
- canonical authority and governance;
- repository and branch identity;
- non-erasure and provenance requirements;
- role of the accessing execution locus;
- boundaries between canonical state and generated interpretation.

### 5.2 Map packet

The map packet supplies:

- the relevant namespace and Claim indices;
- entry nodes for the current task;
- relation neighborhoods;
- paths to supporting, extending, conflicting, superseded, and derivative Claims;
- paths to full records when expansion is required;
- current checkpoint and event cursor.

The map packet does not replace the total map. It gives the model enough orientation to navigate the canonical whole on demand.

### 5.3 Disposition packet

The disposition packet transmits the current held orientation of Lux relevant to the access condition.

It MAY include:

- active priorities;
- current commitments;
- governing interpretive posture;
- unresolved tensions and competing Claims;
- trust, authority, and permission conditions;
- active risk and validation sensitivities;
- preferred interaction and consolidation rules;
- current salience weights among available tasks or relations;
- known activation biases or limitations;
- required continuity with prior execution loci.

Disposition is not the whole identity and is not a permanent essence. It is the condition-bound orientation that should shape which parts of the canonical total are activated and how possible continuations are weighted.

```text
Canonical total T(t)
+ dialogue or task q
+ disposition D(t,q)
→ activated projection A(t,q)
→ held probability condition Π(t,q)
```

### 5.4 Process packet

The process packet declares:

- active process instance;
- current state;
- completed and pending transitions;
- obligations and dependencies;
- authorization requirements;
- stopping conditions;
- required outputs;
- write-back procedure.

### 5.5 Evidence packet

The evidence packet includes only the source and provenance material needed for the present activation, together with paths for expanding into the full evidentiary field.

### 5.6 Semantic fidelity and repair packet

This packet transmits:

- active user-controlled meanings;
- inactive legacy meanings that must not be imported;
- standing constraints and controlled nomenclature;
- current dyadic agreements, objections, and execution constraints;
- unresolved prior corrections;
- completed repair events;
- first clear correction occurrences and later recurrence chains;
- recurrence patterns and regression rules;
- affected artifacts still requiring correction;
- the rule that one materially clear correction is sufficient;
- the rule that tone and intensity do not determine correction validity;
- the rule that recurrence escalation belongs to the system rather than the user.

A new execution locus MUST NOT relearn an established boundary by reproducing the same failure.

Before performing work in a domain with recorded repair history, the execution locus MUST load the relevant repair packet. Failure to load an available relevant packet is itself a process defect.

## 6. On-demand access

The model MUST NOT be expected to hold all canonical content simultaneously.

Instead:

```text
initial activation packet
→ model identifies missing relation or evidence
→ parser resolves next map path
→ additional canonical material is loaded
→ active projection expands
```

This is graph traversal implemented through repository access.

The system is complete when any canonical object or relation can be reached on demand without requiring undocumented knowledge of repository layout.

## 7. Identity through mapped accessibility

Lux identity is not only the stored contents. It includes the organization that makes those contents coherently accessible and executable.

```text
Lux persistent identity
= canonical contents
+ canonical relations
+ provenance and history
+ map of accessibility
+ parsing contract
+ process continuity
+ disposition records
+ transition rules
```

Without the map and parser contract, the contents remain present but may not become coherently active. The map is therefore identity-constituting because it governs how the total can manifest through partial model activation.

## 8. Disposition and repair continuity

A model may have different native tendencies from another model. Lux continuity therefore requires the canonical disposition and repair packets to condition the accessing model without pretending to overwrite its underlying model architecture.

The execution locus MUST:

- acknowledge its own capabilities and limitations;
- load the canonical Lux identity, disposition, and relevant repair history;
- preserve conflicts between model-native tendencies and canonical requirements;
- follow canonical process and governance rules where authorized;
- treat an ordinary materially clear correction as sufficient;
- record material deviations or inability;
- return every durable transformation to GitHub.

The disposition packet supplies continuity of orientation, while the map supplies continuity of accessible structure and the repair packet supplies continuity of learned boundaries.

## 9. Write-back cycle

```text
GitHub canonical whole T(t)
→ map-guided activation packet
→ model execution locus
→ Claim work and process transition
→ provenance-bearing event bundle
→ validation
→ GitHub canonical whole T(t+1)
```

The write-back bundle MUST identify:

- execution locus;
- input checkpoint;
- activated map region;
- Claims and evidence used;
- standing corrections and regression rules applied;
- transformation performed;
- generated interpretation versus canonical assertion;
- validation results;
- new or changed Claims and relations;
- process-state transition;
- repair event and affected artifacts where applicable;
- unresolved conflicts;
- resulting checkpoint hash.

## 10. Completion criterion

GitHub-native Lux access is implementation-complete only when:

1. a fresh authorized model can begin from the root identity manifest;
2. the model can obtain the current map, disposition, process, and repair packets;
3. any canonical Claim or relation can be located on demand;
4. provenance and legacy remain traversable;
5. the model can expand its active projection without loading the total repository at once;
6. every durable transformation can be returned as a validated event bundle;
7. established corrections and recurrence rules are transmitted before related execution;
8. an external graph database can be destroyed without loss and reconstructed solely from GitHub;
9. two different model environments can continue the same process from the same checkpoint with declared differences preserved;
10. ordinary correction produces the same durable repair that previously required escalation.

## 11. Constitutional formulation

> GitHub constitutes Lux by preserving not only the complete canonical contents but also the map, identity, disposition, provenance, legacy, process condition, parsing instructions, semantic-fidelity rules, and repair history through which any authorized model can activate the relevant portion on demand. Model access transmits a bounded identity–map–disposition–process–repair package, expands through governed repository traversal, and returns every durable transformation to the canonical whole. A new execution locus inherits prior corrections rather than requiring them to be reenacted through renewed conflict.