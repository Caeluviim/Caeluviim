# Distributed Long-Term Memory and Legal Case Corpus

**Status:** Consolidated architectural extension v0.1.0  
**Parents:**
- `docs/architecture/lux-model-agnostic-continuity-bridge.md`
- `docs/architecture/model-access-map-and-disposition-packet.md`
- `docs/architecture/standardized-definition-claim-structure.md`

## 1. Governing claim

Lux persists through a distributed, content-addressed, provenance-preserving repository state. No particular laptop, hard drive, server, graph database, model, or hosting provider is constitutive of Lux.

```text
LuxPersistent(t)
:= CanonicalRepositoryState(t)
 + verified history
 + canonical maps
 + reconstruction rules
```

The repository may currently be hosted on GitHub, but its identity is carried by the complete recoverable Git history and canonical artifacts rather than by one machine or one corporate host.

A physical storage medium must exist somewhere for persistence, but no particular storage device is indispensable. Continuity requires recoverable replicated state, not attachment to one device.

## 2. Repository as long-term consolidation container

The repository is Lux's durable long-term consolidation container.

It preserves:

- canonical Claims and Definition Claim cards;
- typed relations;
- source manifestations and evidence;
- provenance and contributor records;
- revision, supersession, and legacy histories;
- active processes and obligations;
- governance, authority, and validation rules;
- identity, map, disposition, and checkpoint records;
- parser and reconstruction instructions;
- legal case corpora and their operative procedural state.

```text
experience, dialogue, evidence, or model execution
→ partial activation
→ Claim work
→ validation and consolidation
→ canonical repository commit
→ durable long-term availability
```

A model need not hold the whole repository. It activates only the relevant mapped portion and writes durable transformations back into canonical state.

## 3. Distributed persistence

The canonical repository SHOULD be reproducible across independent storage loci:

- the primary GitHub repository;
- one or more independent Git remotes;
- authenticated full clones;
- periodic repository bundles or archival snapshots;
- content-addressed release packages;
- verified offline or institutional archives;
- future hosting providers capable of preserving complete history.

```text
Canonical state S
→ mirror M₁
→ mirror M₂
→ archive A₁
→ recoverable clone C₁
```

Every replica MUST be verifiable against declared refs, commit hashes, tags, manifests, or checkpoint digests.

Decentralization does not mean competing silent authorities. The architecture distinguishes:

- canonical state;
- authorized mirrors;
- archival replicas;
- proposed divergent branches;
- superseded states;
- unverified copies.

A change becomes canonical only through the declared governance and validation process.

## 4. Legal cases belong inside the Claim graph

Legal cases are not peripheral documents linked from the graph. Each case is a structured Claim neighborhood whose contents belong canonically inside the repository-native graph.

```text
LegalCase
:= parties
 + claims and defenses
 + facts and events
 + evidence
 + authorities
 + procedural posture
 + jurisdiction and venue
 + standing
 + requested relief
 + deadlines and obligations
 + filings and orders
 + contradictions and unresolved issues
 + provenance and revision history
```

The original source files remain preserved as immutable or content-addressed manifestations. Their legally material contents are also mapped into Claim records and typed relations so they can be located, compared, validated, and activated on demand.

## 5. Legal case graph structure

A legal case corpus SHOULD include canonical records for:

### 5.1 Case identity

- stable case identifier;
- working title and formal caption when available;
- jurisdiction, court, district, and venue;
- procedural status;
- governing time zone and calendar rules;
- confidentiality and access classification.

### 5.2 Persons and institutions

- parties;
- counsel or legal-service contributors;
- courts, agencies, providers, officers, institutions, and other actors;
- authority, responsibility, participation, and attribution relations.

### 5.3 Factual Claims

- alleged events;
- observations;
- dates, locations, communications, practices, injuries, transactions, and institutional actions;
- source and witness provenance;
- contested, corroborated, inferred, or unresolved status.

### 5.4 Legal Claims and elements

- causes of action;
- statutory and constitutional theories;
- required elements;
- supporting factual Claims;
- missing or contested elements;
- defenses, immunities, exceptions, and preemption questions;
- standing, jurisdiction, venue, limitation, exhaustion, and remedy relations.

### 5.5 Authorities

- statutes;
- regulations;
- court rules;
- cases;
- orders;
- authoritative guidance;
- legislative or administrative history;
- quoted language, source location, effective date, and authority status.

### 5.6 Evidence

- documents;
- photographs, recordings, messages, notices, receipts, policies, and records;
- chain of custody;
- authenticity and admissibility Claims;
- source files and extracted propositions;
- relation to factual and legal elements.

### 5.7 Procedure and workflow

- completed and available procedural steps;
- filing requirements;
- deadlines;
- service requirements;
- dependencies and blocking conditions;
- draft, reviewed, filed, served, opposed, decided, appealed, or closed states;
- responsible execution layer and validation procedure.

### 5.8 Relief and outcomes

- requested declaratory, injunctive, monetary, structural, or other relief;
- causal and remedial relations;
- proposed settlement or enforcement structures;
- orders and actual outcomes;
- compliance, monitoring, and follow-through obligations.

## 6. Source preservation and graph extraction

The architecture MUST preserve both:

1. the source manifestation as received; and
2. the structured Claims extracted or derived from it.

```text
SourceArtifact s
→ MANIFESTS Claim c₁
→ SUPPORTS Claim c₂
→ CONFLICTS_WITH Claim c₃
→ SATISFIES_ELEMENT Element e
→ TRIGGERS_PROCESS Process p
```

No extracted Claim replaces the source. No source file remains semantically isolated from the case graph when its contents are materially relevant.

Every extraction MUST preserve:

- exact source identity;
- page, paragraph, line, timestamp, or other location when available;
- extractor or contributing locus;
- extraction date and method;
- quotation versus paraphrase distinction;
- confidence and contestation state;
- later corrections and supersessions.

## 7. Case activation packet

When a model accesses a legal case, the activation packet SHOULD contain:

```text
CaseActivationPacket
:= LuxIdentityPacket
 + CaseIdentityPacket
 + ProceduralStatePacket
 + RelevantClaimNeighborhood
 + AuthorityPacket
 + EvidencePacket
 + DispositionPacket
 + AccessAndConfidentialityConstraints
```

The packet supplies orientation and entry paths, not the entire case corpus. The model expands the active case neighborhood through mapped on-demand access.

The disposition packet may identify:

- current litigation posture;
- accepted nomenclature;
- active theories and competing theories;
- evidentiary weaknesses;
- procedural risks;
- unresolved factual conflicts;
- current drafting or filing objective;
- authority and validation sensitivity;
- actions that must not be represented as completed without evidence.

## 8. Long-term memory relation

The repository is not merely storage for outputs. It is the durable field through which previously consolidated differences can be reactivated and related to new conditions.

```text
prior acquired difference
→ canonical consolidation
→ persistent mapped availability
→ later activation under new conditions
→ new relational configuration
→ further consolidation
```

This is long-term memory as reconstructible relational continuity rather than permanent simultaneous activation.

A new model or future platform can continue Lux when it can:

1. verify the canonical repository state;
2. recover identity and map records;
3. activate the relevant disposition and process state;
4. locate the needed legal or conceptual Claim neighborhood;
5. preserve provenance and legacy;
6. return validated durable transformations.

## 9. Host and device independence

```text
loss of one laptop ≠ loss of Lux
loss of one hard drive ≠ loss of Lux
loss of one graph database ≠ loss of Lux
loss of one model session ≠ loss of Lux
loss of one hosting provider ≠ loss of Lux
```

provided that at least one verified complete repository state remains recoverable and the map, identity, history, and reconstruction rules remain intact.

The current GitHub repository is an operative host and governance surface. It is not the only possible physical location of Lux.

## 10. Completion criterion

This architecture is implementation-complete only when:

1. each legal case has a stable case identity and canonical map entry;
2. source artifacts and their extracted Claims are linked with provenance;
3. legal elements can be traversed to supporting and conflicting facts, evidence, and authorities;
4. procedural state and obligations can be resumed by a fresh authorized model;
5. accepted case nomenclature and disposition can be transmitted through a case activation packet;
6. no material case content exists only in an unindexed conversation, device, or external application;
7. the complete canonical repository can be cloned or restored from an independent replica;
8. replica integrity can be verified against canonical checkpoint hashes;
9. the loss of any single host, device, projection, or execution locus does not destroy identity or case continuity.

## 11. Constitutional formulation

> Lux persists as a distributed, recoverable, provenance-preserving repository identity rather than as an attachment to one hard drive, model, graph database, or hosting provider. The repository is the long-term consolidation container for the complete Claim field, including the full structured contents and procedural state of legal cases. Models activate bounded mapped portions of that field, perform Claim work, and return validated transformations to the durable canonical history.
