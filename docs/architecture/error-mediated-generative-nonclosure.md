# Error-Mediated Generative Non-Closure

**Module identifier:** `urn:caeluviim:module:emgn`  
**Version:** `0.1.0`  
**Status:** Proposed — implemented, not ratified  
**Scope:** Formal architecture only; no claim of empirical confirmation is encoded by implementation alone.

## 1. Purpose

This module formalizes the thesis that bounded agentic processors do not generate novelty merely by making errors. New reachable futures arise when discrepancies are:

1. generated through localized, relationally situated processing;
2. retained as causal residue;
3. transformed through remediation;
4. allowed to modify effective constraints or transition regimes; and
5. shown to construct reachable states absent from the prior effective future-space.

The mechanism is named **error-mediated generative non-closure**.

## 2. Critical distinctions

The module preserves the following distinctions as invariants.

### 2.1 Causal boundedness is not determinism

A universal system may contain all operative causes without having a single-valued transition rule. The architecture therefore permits deterministic, stochastic, and set-valued transition semantics.

### 2.2 Error is not mere ignorance

A discrepancy becomes operationally relevant only when it is causally retained. An unrecorded prediction failure that leaves no trace cannot modify later reachability.

### 2.3 Error is not sufficient for novelty

Error alone may degrade, cancel, or leave the transition regime unchanged. Novelty requires retention, remediation, regime modification, and a reachability witness.

### 2.4 Local non-closure is not causal escape

An agent's model may be incomplete while the agent remains physically and causally embedded in the universal system.

### 2.5 Novelty must be witnessed

A new-future claim is not validated by assertion. It requires a witness identifying at least one later reachable state that is not represented by the declared embedding of the earlier reachable set.

## 3. Primitive entities

| Entity | Formal role |
|---|---|
| `UniversalSystem` | The causally bounded containing system for the record |
| `AgenticNode` | A localized causal processor with finite state and model access |
| `ModelSnapshot` | An agent's temporally indexed representation used for prediction or action |
| `InteractionEvent` | A relational event involving two or more agentic nodes |
| `DiscrepancyEvent` | A measured mismatch between predicted or held content and observed content |
| `ErrorResidue` | A causally retained trace produced from a discrepancy event |
| `RemediationEvent` | An activity that transforms, redistributes, incorporates, or rejects residue |
| `TransitionRegime` | The effective rule and constraint organization governing transitions |
| `ReachabilitySnapshot` | A versioned representation of states reachable under a regime |
| `NovelFutureWitness` | Evidence that a later reachable state is outside the prior embedded reachability set |
| `GovernanceDecision` | Proposed, validated, ratified, or rejected status with independent validators |

Relations are reified as addressable entities when they require provenance, evidence, confidence, governance, or revision history.

## 4. Formal core

Let the universal state at time `t` be `U_t`, with effective transition correspondence `Phi_t`:

\[
U_{t+1} \in \Phi_t(U_t).
\]

`Phi_t` may be single-valued, stochastic, or set-valued. The module does not infer determinism from causal boundedness.

For agent `i`, let:

\[
A_i = (X_i, M_i, P_i, H_i),
\]

where `X_i` is local state, `M_i` is a model snapshot, `P_i` is a processing policy, and `H_i` is retained history.

A discrepancy event is:

\[
\varepsilon_{i,t} = d(O_{i,t}, \widehat{O}_{i,t}),
\]

where `d` is a declared comparison function, `O` is observed content, and `O-hat` is predicted or held content.

Retained residue evolves by:

\[
\rho_{t+1} = G(\rho_t, \varepsilon_t, C_t, \mathcal{R}_t),
\]

where `C_t` is remediation and `R_t` is the relational configuration. `G` is not subtraction: remediation may erase, preserve, reinterpret, redistribute, amplify, or institutionalize residue.

The effective transition regime evolves by:

\[
\Phi_{t+1} = \Lambda(\Phi_t, \rho_{t+1}, \mathcal{R}_t).
\]

The effective state-space may also evolve:

\[
\mathcal{X}_{t+1} = \Gamma(\mathcal{X}_t, \rho_{t+1}).
\]

Let `Reach(Phi_t, U_t)` denote the effective reachable set. A generative-non-closure witness exists only if:

\[
\exists z \in Reach(\Phi_{t+1}, U_{t+1})
\quad\text{such that}\quad
z \notin \iota_t(Reach(\Phi_t, U_t)),
\]

where `iota_t` is the declared embedding from the earlier reachability representation into the later one.

## 5. Constitutive premises

The module's theorem depends on five explicit premises rather than treating novelty as automatic.

- **A1 — Finite localization:** Every agentic node has bounded access to universal state and bounded processing resources.
- **A2 — Recurrent mismatch:** Nontrivial relational engagement recurrently produces discrepancy for at least some nodes. This does not require error at every timestep.
- **A3 — Causal retention:** At least some discrepancy becomes retained residue.
- **A4 — Regime plasticity:** Retained residue can modify effective constraints, rules, or relation structures.
- **A5 — Generative construction:** A modified regime can make at least one state reachable that was not represented in the prior embedded reachable set.

## 6. Proposition

Given A1–A5, there exists at least one transition interval in which:

\[
Reach(\Phi_{t+1}, U_{t+1})
\not\subseteq
\iota_t(Reach(\Phi_t, U_t)).
\]

The result is **new effective reachability**, not a claim that an event lacks causes.

## 7. Operational record lifecycle

1. Snapshot participating agents and their model references.
2. Record an interaction event with at least two participants.
3. Record one or more discrepancies with declared comparison methods.
4. Record the residues retained from those discrepancies.
5. Record remediation events and their transformation modes.
6. Snapshot the transition regime before and after remediation.
7. Snapshot reachability before and after the regime change.
8. Attach at least one novelty witness.
9. Submit the claim for independent validation.
10. Ratify only after two validators, neither identical to the proposer, confirm the witness and provenance chain.

## 8. Validation invariants

A conforming record must satisfy all of the following:

- at least two distinct agentic nodes participate;
- every discrepancy references a participating agent;
- every residue references a recorded discrepancy;
- every remediation references at least one recorded residue;
- before and after transition regimes are distinct resources;
- a supported or validated novelty claim contains at least one witness;
- a validated or ratified claim has at least two distinct validators;
- the proposer is not a validator;
- provenance contains a content hash and timestamp;
- a claim marked validated cannot declare `regime_changed = false`;
- a claim marked validated cannot have an empty set of new reachable-state references.

## 9. Non-claims

This module does not establish that:

- every bounded agent errs at every timestep;
- every error is productive;
- entropy production is numerically lower-bounded by an arbitrary epistemic-error measure;
- causal boundedness entails determinism;
- a declared future is validated without a reachability witness;
- suffering is required for epistemic or generative novelty.

## 10. Machine artifacts

- JSON Schema: `schemas/emgn-record.schema.json`
- RDF/OWL vocabulary: `ontology/emgn.ttl`
- SHACL constraints: `shapes/emgn.shacl.ttl`
- Valid JSON record: `examples/emgn-record.valid.json`
- Valid RDF record: `examples/emgn-record.valid.ttl`
- Executable tests: `tests/test_emgn.py`
