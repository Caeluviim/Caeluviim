# RRKC Cycle 2 Lean boundary

This directory contains the first Lean 4 conversion target for the
**Recursive Reflective Knowledge Calculus — Cycle 2 Structural Repair**.

The formalized surface is deliberately narrow:

| Cycle 2 component | Lean declaration | Status |
| --- | --- | --- |
| Static signature `Σ` | `StaticSignature` | Definition |
| Facets and structural morphisms | `FacetCategory` | Definition with category laws |
| Reified relation occurrence | `RelationOccurrence` | Definition |
| Role-typed incidence map | `Incidence` | Definition |
| Binary relation as decorated span | `BinaryRelationSpan` | Definition |
| Composable underlying span | `StructuralSpan` | Definition |
| Pullback universal property | `PullbackCone` | Witness type |
| All-cospan selected pullbacks | `SelectedPullbacks` | Sufficient interface; no global inhabitant |
| Role-compatible binary pullbacks | `BinarySpanCompositionInterface` | Minimal interface; C1 proof obligation |
| Binary span composition | `composeBinaryRelationSpans` | Definition from supplied pullback evidence |
| Structural identity span | `StructuralSpan.identity` | Definition |
| Span equivalence and comparisons | `SpanIsomorphism`, `SpanComparisonData` | Evidence types; triangle/pentagon are C2 |
| Leg-preserving span 2-cell | `SpanTwoCell` | Definition |
| 2-cell identity and vertical composition | `SpanTwoCell.identity`, `SpanTwoCell.vertical` | Definition; identity/associativity proved |
| Pullback-induced horizontal composition | `SpanTwoCell.horizontal` | Definition; projections, identity, and interchange proved |
| Triangle and pentagon equations | `SpanTriangleEquation`, `SpanPentagonEquation` | Typed propositions; S6–S7 obligations |
| Coherence proof/package | `SpanCoherenceProof`, `SpanCoherencePackage` | Evidence types; no global inhabitant |
| M10 antecedent | `M10SpanCompositionCoherenceCondition` | Nonemptiness of a coherence package |
| Typed arbitrary-arity multispan | `TypedMultispan` | Definition |
| Typed multispan gluing | `MultispanGluing` | Definition |
| Multispan composite witness | `MultispanComposite` | Evidence type; existence not asserted |
| Multispan composition implementation | `TypedMultispanCompositionInterface` | Interface; no global inhabitant |
| Execution configuration `χ` | `ExecutionConfiguration` | Definition |
| Runtime state `SΣ = ⟨H,A,W⟩` | `RuntimeState` with `Finset` history | Definition |
| Stable ledger-entry identity | `RuntimeVocabulary.entryId` and `stableEntryIdentity` | Required interface |
| Ledger substructure wiring | Typed history projections and `relationProjectionContained` | Required interface |
| Stable ledger ordering | `entryPosition` and `stableLedgerPosition` | Required interface |
| Provenance-bearing delta | `Delta` | Definition |
| Governance transition wiring | Ordered `governanceEvents`, replay operations, authority, and trace legality | Required interface |
| Governed active-view derivation | `GovernanceStateFromHistory`, `DerivedActiveView`, and `applyDelta` | Required interface |
| Evidence-bearing validation | `validate` and `validationReportGrounded` | Required interface |
| Workspace lifecycle | `RuntimeVocabulary.workspaceAfterAppend` | Required interface |
| State and delta constraints | `StateWellFormed`, `WellFormedDelta` | Required judgments |
| Transition failure states | `TransitionFailure` | Definition |
| Operator semantics | `OperatorDenotation` and `StateStep` | Definition, not a functor |
| Log-accumulating composition | `ExecutionOutcome.bind` and `kleisliCompose` | Definition |
| Configuration-bound execution | `executionPipeline` under `ExecutionConfiguration` | Definition |
| Execution fixed point | `IsExecutionFixedPoint` | Definition; M8 remains conjecture |
| Two-executor replay | `Executor` and `ReplayAgreement` | Definition; M6 remains conditional |
| Provenance union laws | `ProvenanceUnionCandidate` and P1–P4 predicates | Proof obligations |
| Finite trusted reflection top | `ReflectionBoundary` | Definition |
| Append-only transition | `Transition.append` | Definition |
| Historical monotonicity M1 | `historical_monotonicity` | Proved theorem |
| M1–M10, P1–P4, C1–C5, and S1–S7 status registers | `metatheoryStatus`, `provenanceLawStatus`, `categoricalObligationStatus`, `spanLawStatus` | Definition |

No declaration asserts type preservation, provenance preservation, relative
reflection, termination, fixed-point existence, confluence, functoriality,
pullback availability, multispan-composite existence, multispan
associativity, or triangle/pentagon coherence for arbitrary chosen comparison
data. Replay agreement takes two distinct executor manifestations and is not
stated as equality of an expression with itself.

## Validation

With Lean installed through Elan:

```sh
cd formal
lake build
```

The project pins Mathlib to the same Lean release and imports only the
`Finset` union surface required by the fixed theorem kernel. Category,
pullback, span-isomorphism, and multispan data remain represented locally.

## Categorical proof boundary

Cycle 2 now distinguishes two pullback assumptions:

1. `SelectedPullbacks` is the stronger sufficient assumption used to state
   general structural-span unitors and associators. It selects a pullback for
   every cospan but is not globally inhabited.
2. `BinarySpanCompositionInterface` is the minimal operational assumption. It
   selects pullbacks only for adjacent binary relation occurrences whose
   endpoint types agree and whose semantic roles satisfy a declared
   `RoleCompatibility` predicate.

Pullback composition returns a `StructuralSpan`. It does not silently promote
the pullback apex to a `RelationOccurrence`; that requires separate relation
typing, formation, and provenance evidence.

The diagonal `StructuralSpan.identity` is defined, while unitality and
associativity are represented up to `SpanIsomorphism`. A
`SpanComparisonPackage` contains selected pullbacks and chosen unitor and
associator isomorphisms. Those comparison data are not mislabeled as a full
coherence proof: C2 separately requires the triangle and pentagon equations.
The equations are now mechanized as `SpanTriangleEquation` and
`SpanPentagonEquation`. A `SpanCoherencePackage` contains their proofs, and
M10 is conditional on that stronger package. No package is asserted to exist,
and no strictification is assumed.

`SpanTwoCell` supplies the leg-preserving 2-cell language needed to state
these equations. Identity and vertical composition are inherited from
`FacetCategory`. Horizontal composition is induced by the target pullback's
universal property. Lean proves:

- vertical left/right identity and associativity;
- cancellation of the two cells extracted from a `SpanIsomorphism`;
- both horizontal pullback-projection equations;
- horizontal preservation of identity; and
- interchange.

Accordingly S1–S5 are proved theorems. S6 triangle and S7 pentagon remain proof
obligations, so C2 is not promoted.

Typed multispan gluing declares:

- a joint index;
- the consumed left and right ports;
- participant equality at each joint;
- semantic-role compatibility;
- and the exact unconsumed output boundary.

`MultispanComposite` is the witness type for one such gluing, and
`TypedMultispanCompositionInterface` is the implementation interface for all
declared gluings. The witness contains the simultaneous joint equations,
universal mediating map, both factorization equations, and uniqueness; exposed
result legs are derived from the two apex projections. C1–C5 keep binary
pullback selection, span triangle/pentagon coherence, multispan existence,
multispan associativity, and multispan type preservation at proof-obligation
status. M7 confluence remains a conjecture.

The next proof work is to construct comparison data for a selected bounded
facet-category profile and prove S6–S7, rather than merely supplying an
arbitrary `SpanCoherenceProof` as trusted input.

The normative symbol-and-wiring corrections driving this module are recorded
in [`../docs/rrkc-cycle2-symbol-wiring-repair.md`](../docs/rrkc-cycle2-symbol-wiring-repair.md).
