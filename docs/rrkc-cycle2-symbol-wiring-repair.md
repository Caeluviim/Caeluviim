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

M10 is labeled **Conditional theorem**. Its exact condition is a
`SpanCoherencePackage`: selected pullbacks, left-unitor, right-unitor, and
associator span isomorphisms, and a `SpanCoherenceProof` containing the
triangle and pentagon equations. `selectedPullbacks_imply_M10Condition`
constructs this package from any supplied `SelectedPullbacks` value. No
selected-pullback profile, and therefore no such package, is globally
asserted for every facet category.

### Binary span composition boundary

Cycle 2 distinguishes a semantic relation occurrence from the structural span
used by categorical composition:

```text
BinaryRelationSpan := relation occurrence + typed source/target roles and legs
StructuralSpan     := apex + typed source/target legs
```

Forgetting the semantic decoration is total:

```text
toStructuralSpan : BinaryRelationSpan(A, B) -> StructuralSpan(A, B)
```

The converse is not total. A pullback apex is not automatically a new
`RelationOccurrence`; promotion requires separate relation-facet typing,
formation, instantiation, and provenance evidence.

`PullbackCone(left, right)` includes the commuting square, mediating morphism,
factorization equations, and uniqueness equation. Pullback existence is not
embedded in `FacetCategory`.

Two selection interfaces are kept distinct:

```text
SelectedPullbacks(baseCategory)
```

is the stronger sufficient assumption for the ordinary bicategory-of-spans
construction and chooses a pullback for every cospan. Defining this interface
does not assert that every admitted facet category implements it.

```text
BinarySpanCompositionInterface(baseCategory, roleDiscipline)
```

is the minimal operational assumption. It chooses a pullback only for two
adjacent binary relation spans when:

1. the target object of the first span is the source object of the second; and
2. the first target role and second source role satisfy the declared
   `RoleCompatibility` predicate.

Composition is then:

```text
composeBinaryRelationSpans :
  compatible(first.targetRole, second.sourceRole)
  -> StructuralSpan(A, C)
```

The diagonal span:

```text
A <-id- A -id-> A
```

is the structural identity definition. Pullback composition is not claimed to
be literally unital or associative. `SpanIsomorphism` preserves both endpoint
legs, and `SpanComparisonData` records:

- a left unitor up to span isomorphism;
- a right unitor up to span isomorphism; and
- an associator up to span isomorphism.

The canonical comparisons are not accepted as additional trusted input.
`canonicalLeftUnitor`, `canonicalRightUnitor`, and `canonicalAssociator`
construct them from selected pullback lifts. Their inverse laws follow from
pullback extensionality. Lean also proves their left-unitor, right-unitor, and
associator naturality.

`canonicalSpanTriangle` and `canonicalSpanPentagon` derive both C2 equations
from the same universal properties. The pentagon proof flattens both paths
to four constituent projections and applies nested pullback uniqueness.
`canonicalSpanCoherenceProof` is therefore an output, not an assumed witness.
No coherence, strictification, or additional choice axiom is added.

C2 is a **Conditional theorem** under a supplied `SelectedPullbacks` profile.
C1 remains the separate proof obligation that the required pullbacks can be
selected for the chosen facet-category profile. M10 may be used only under
that same existence boundary.

### Span 2-cells and proved strict laws

A leg-preserving 2-cell is:

```text
SpanTwoCell(first, second) := {
  arrow : first.apex -> second.apex,
  arrow ; second.sourceLeg = first.sourceLeg,
  arrow ; second.targetLeg = first.targetLeg
}
```

Identity is the base-category identity on the apex. Vertical composition is
base-category path composition. Lean proves:

```text
identity ; alpha = alpha
alpha ; identity = alpha
(alpha ; beta) ; gamma = alpha ; (beta ; gamma)
```

The forward and inverse cells extracted from `SpanIsomorphism` also cancel in
both vertical orders.

For:

```text
alpha : first  => first'
beta  : second => second'
```

the horizontal composite is the unique morphism from the source pullback apex
to the target pullback apex whose projections are:

```text
sourcePullback.fst ; alpha
sourcePullback.snd ; beta
```

The compatibility equation follows from:

- the source pullback square;
- `alpha` preserving the shared target leg; and
- `beta` preserving the shared source leg.

Lean proves both projection equations, horizontal preservation of identity,
and the interchange law:

```text
(alpha1 ; alpha2) * (beta1 ; beta2)
  =
(alpha1 * beta1) ; (alpha2 * beta2)
```

These results use only the `FacetCategory` laws, the selected pullback
universal property, and pullback uniqueness.

### Constructive triangle and pentagon coherence

For composable spans `first` and `second`, `SpanTriangleEquation` compares:

```text
associator(first, identity, second)
  ; (identity(first) * leftUnitor(second))
```

with:

```text
rightUnitor(first) * identity(second)
```

For four composable spans, `SpanPentagonEquation` compares the standard
two-associator route:

```text
associator(first * second, third, fourth)
  ; associator(first, second, third * fourth)
```

with the standard three-step route:

```text
(associator(first, second, third) * identity(fourth))
  ; associator(first, second * third, fourth)
  ; (identity(first) * associator(second, third, fourth))
```

Both sides are Lean-checked 2-cells with identical source and target spans.
`SpanCoherenceProof` requires equality of these paths.
`SpanCoherencePackage` combines the selected pullbacks, chosen comparisons,
and those proofs. `canonicalSpanCoherencePackage` constructs one from any
supplied selected-pullback profile; no such profile is globally asserted.
`M10SpanCompositionCoherenceCondition(baseCategory)` is exactly the
proposition that such a package is nonempty for that base category.

The fine-grained register is:

| Identifier | Statement | Status |
| --- | --- | --- |
| S1 | Vertical left and right identity | Proved theorem |
| S2 | Vertical associativity | Proved theorem |
| S3 | Horizontal pullback-projection equations | Proved theorem |
| S4 | Horizontal preservation of identity | Proved theorem |
| S5 | Interchange | Proved theorem |
| S6 | Triangle equation for the canonical comparisons | Proved theorem |
| S7 | Pentagon equation for the canonical comparisons | Proved theorem |
| S8 | Canonical left-unitor naturality | Proved theorem |
| S9 | Canonical right-unitor naturality | Proved theorem |
| S10 | Canonical associator naturality | Proved theorem |

C2 is therefore a **Conditional theorem**: `SelectedPullbacks` is sufficient
to derive its canonical comparisons and both coherence equations. M10
remains a **Conditional theorem** because neither selected-pullback existence
nor the resulting package is asserted globally.

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

## 9. Typed multispan composition boundary

Arbitrary-arity formation and arbitrary-arity composition remain distinct.
The mechanized composition boundary now introduces:

```text
TypedMultispan(baseCategory, Port)
```

with an apex and a role-typed leg to the participant at every port.

A `MultispanGluing` declares:

- a joint index type;
- the consumed left and right port for every joint;
- equality of the two participant objects at every joint;
- semantic-role compatibility at every joint; and
- the exposed ports, proven to be exactly those not consumed by a joint.

The output boundary is the disjoint sum of the exposed left and right ports.
A `MultispanComposite` is evidence for one gluing. It supplies:

- the composite apex;
- projections to both input apexes;
- and commutativity of every joined pair of legs after the declared
  participant equality;
- a mediating morphism for every other cone satisfying all joint equations;
- factorization through both input-apex projections; and
- uniqueness of that mediating morphism.

The result's exposed legs are not free fields: each is derived by composing
the relevant apex projection with the corresponding unconsumed input leg.

`TypedMultispanCompositionInterface` requests such evidence for every declared
gluing. The declaration of this structure is not a claim that it has an
inhabitant.

The categorical obligation register is:

| Identifier | Statement | Status |
| --- | --- | --- |
| C1 | Required binary pullbacks can be selected for the chosen profile | Proof obligation |
| C2 | Canonical span comparisons satisfy triangle and pentagon coherence under selected pullbacks | Conditional theorem |
| C3 | Typed composites exist for the chosen multispan gluings | Proof obligation |
| C4 | Multispan composition is associative under a declared comparison | Proof obligation |
| C5 | Multispan composition preserves the declared typing judgments | Proof obligation |

No selected-pullback existence, multispan existence, multispan
associativity, type-preservation, or confluence conclusion follows from the
interface declarations alone. M7 confluence remains an open conjecture.

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
- Binary relation composition requires role compatibility and selected
  pullback evidence and returns a structural span.
- Structural-span horizontal identity and associativity are stated up to
  leg-preserving span isomorphism, not literal equality.
- Span 2-cell vertical laws, horizontal projection laws, horizontal identity,
  and interchange are proved from existing assumptions.
- Canonical unitors and associator, all three naturality laws, triangle, and
  pentagon are constructed and proved from selected pullback universal
  properties; S6–S10 are proved theorems.
- C2 is conditional on `SelectedPullbacks`; no extra coherence or choice
  assumption is required, while C1 remains a pullback-selection obligation.
- Typed multispan composition has a witness interface while C3–C5 retain
  existence and law claims as proof obligations.
- The reflection tower used by an executable deployment ends at a declared
  trusted kernel.

These corrections are normative for the Lean conversion.
