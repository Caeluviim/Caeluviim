# RRKC Cycle 2 — Symbol and Wiring Repair

Status: Proposed normative correction  
Ratification: Not yet validated  
Applies to: Cycle 2 Sections 6, 8, 9, 11, 15, 18, 19, 21, 24, 26–30, and Part X

This correction removes the remaining Cycle 1 residue and supplies the
connective definitions that the first Cycle 2 draft omitted. It is a semantic
repair, not a relabeling pass.

## 1. Unique execution and fixed-point symbol

Capital `Ω` is deleted. It has no declaration in Cycle 2.

The only assembled execution object is:

```text
Exec[signature, configuration] : RuntimeState -> ExecutionOutcome RuntimeState Log
```

where `ExecutionOutcome` can be successful or can carry a declared failure.
A fixed point is consequently a state whose successful execution returns the
same state, with a possibly nonempty emitted log:

```text
IsExecutionFixedPoint(Exec, state)
  := exists log, Exec(state) = Success(state, log)
```

M8 asks whether a fixed point of this defined execution exists. It makes no
claim about an undeclared `Ω`.

Status: **Definition** for `IsExecutionFixedPoint`; **Conjecture** for M8.

## 2. Log-accumulating partial composition

An operator step is not typed as an ordinary endomorphism:

```text
StateStep := RuntimeState -> ExecutionOutcome RuntimeState Log
```

The composition used by the execution pipeline is Kleisli composition:

```text
(first >=> second)(state) :=
  match first(state) with
  | Success(next, log1) =>
      match second(next) with
      | Success(final, log2) => Success(final, log1 ++ log2)
      | Failure(reason, log2) => Failure(reason, log1 ++ log2)
  | Failure(reason, log1) => Failure(reason, log1)
```

The assembled cycle is:

```text
Exec[signature, configuration] :=
  audit
  >=> plan
  >=> expand
  >=> correct
  >=> repair
  >=> validate
  >=> log
```

This operation is distinct from structural composition in the facet category.
It preserves partiality and emitted logs. A successful transition can be a
morphism in the state-transition category. An execution attempt is a
log-bearing partial computation and is not thereby a morphism or a functor.

A functorial lifting remains a **Proof obligation** and must provide a mapping
on both objects and successful transition morphisms, plus identity and
composition proofs.

## 3. Replay determinism compares two runs

The reflexive formula:

```text
Exec[signature, configuration](state)
  = Exec[signature, configuration](state)
```

is deleted because it is tautological.

Let `leftExecutor` and `rightExecutor` be two distinguished executor
manifestations. Let `FrozenInput` include:

- static signature identifier;
- initial state digest;
- task;
- source-corpus snapshot or retrieval trace;
- execution parameters;
- resource budget;
- nondeterminism trace;
- clock context;
- rule ordering;
- external-response trace; and
- semantic implementation version.

Define:

```text
ReplayAgreement(leftExecutor, rightExecutor) :=
  for every frozen input and initial state,
  digest(leftExecutor.run(input, state))
    = digest(rightExecutor.run(input, state))
```

M6 is a **Conditional theorem** only for executor pairs certified to implement
the same transition semantics and canonical result digest. The two executor
arguments make the claim a reproducibility property rather than reflexivity.

## 4. Provenance normalization and law status

The lineage operation is defined from an explicit normalizer:

```text
lineageUnion(left, right)
  := normalizeProvenance(graphUnion(left, right))
```

The normalizer must define stable identifier equivalence before duplicate
nodes can be collapsed.

The following are not assumed laws:

| Identifier | Statement | Status |
| --- | --- | --- |
| P1 | Associativity up to canonical graph isomorphism | Proof obligation |
| P2 | Commutativity up to canonical graph isomorphism | Proof obligation |
| P3 | Idempotency up to canonical graph isomorphism | Proof obligation |
| P4 | Empty-lineage identity up to canonical graph isomorphism | Proof obligation |

M4 remains a **Proof obligation** and depends on the required subset of
P1–P4 plus transition-by-transition provenance coverage. In particular, P3
cannot be used until identifier normalization is shown to recognize stable
identity correctly.

M10 is labeled **Conditional theorem**. Its condition is the existence of the
required pullbacks plus the selected equivalence/coherence construction.

## 5. Ledger projection wiring

For a history `history`, the following are declared functions rather than
unexplained independent fields:

```text
facetRevisions(history)
relationRevisions(history)
provenanceRecords(history)
validationReports(history)
governanceEvents(history)
executionRecords(history)
```

The runtime vocabulary must also provide:

```text
relationAsFacet : RelationRevision -> FacetRevision
```

and prove:

```text
relation in relationRevisions(history)
  -> relationAsFacet(relation) in facetRevisions(history)
```

Thus `R(state) subset E(state)` follows from an explicit compatibility
condition instead of being asserted by notation.

### Provenance connection

`provenanceRecords(history)` is interpreted by the same provenance structure
used by provenance-bearing deltas. A delta includes both its provenance graph
and a coverage witness connecting that graph to every appended entry.

### Validation connection

Validation has a declared dimension, four-valued result, and evidence report:

```text
validate :
  ValidationDimension
  -> LedgerEntry
  -> ValidationResult * ValidationReport
```

`validationReports(history)` is the ledger projection of those evidence
objects. Credibility remains outside structural conformance.

### Governance connection

The three governance layers are related as follows:

```text
projectedEvents := governanceEvents(history)
governanceState :=
  deriveGovernanceState(signature.governancePolicy, projectedEvents)
activeView :=
  deriveActiveView(
    signature.governancePolicy,
    governanceState,
    history
  )
```

The static policy, governance transition state, projected governance events,
and active view therefore have one explicit dependency chain.

## 6. Active-view determinism status

M2 remains a **Conditional theorem**. Part X obligation 8 is renamed:

> Discharge the four antecedents of active-view determinism for each bounded
> execution profile.

The theorem statement does not need to be reproved; the remaining work is to
establish totality, determinism, fixed policy, and absence of unrecorded
dependencies for the selected implementation.

## 7. Identifier discipline

Mechanized identifiers use descriptive names:

| Ambiguous prose symbol | Mechanized name |
| --- | --- |
| facet universe `F` | `Facet` or `FacetUniverse` |
| formation-rule component `F` | `FormationRuleSymbol` |
| base category `B` | `baseCategory` |
| resource budget `B` | `ResourceBudget` |
| governance transition system | `GovernanceSystem` |
| governance event projection | `governanceEvents` |

Font distinctions are not used to carry semantic identity.

## 8. Finite reflection boundary

A deployment has a finite reflective height and an explicitly trusted top
checker:

```text
ReflectionBoundary := {
  topLevel : Nat,
  trustedKernelId : KernelId,
  trustedChecker : ProofArtifact -> CheckResult
}
```

For every `level < topLevel`, level `level + 1` may validate claims about
`level`. The top checker is trusted axiomatically relative to the deployment;
it does not certify its own unrestricted global soundness.

An unbounded reflective tower may still be studied as a mathematical object,
but no executable profile depends on completing an infinite ascent.

Status: **Definition** for the finite deployment boundary; relative reflection
preservation remains **Proof obligation** M5.

## 9. Remaining multispan obligation

Arbitrary-arity relation formation is defined. Only binary span composition is
currently specified. Typed multispan composition remains Part X obligation 3
and is not implied by the binary construction.

## 10. Corrected closure impact

The following Cycle 2 closure claims are narrowed:

- Defect 5 is closed only after all remaining `Ω` references are removed.
- Provenance composition is expressible, but its algebraic laws remain P1–P4.
- Replay determinism is expressible across two executor manifestations.
- The execution pipeline is composable through log-accumulating Kleisli
  composition.
- Ledger projections are connected to the provenance, validation, and
  governance structures they expose.
- M10 uses the permitted label **Conditional theorem**.
- The reflection tower used by an executable deployment ends at a declared
  trusted kernel.

These corrections are normative for the Lean conversion.
