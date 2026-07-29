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
| Binary relation as span | `BinaryRelationSpan` | Definition |
| Pullback requirement | `PullbackCone` | Abstract interface |
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
| M1–M10 and P1–P4 status registers | `metatheoryStatus`, `provenanceLawStatus` | Definition |

No declaration asserts type preservation, provenance preservation, relative
reflection, termination, fixed-point existence, confluence, or functoriality.
Replay agreement takes two distinct executor manifestations and is not stated
as equality of an expression with itself.

## Validation

With Lean installed through Elan:

```sh
cd formal
lake build
```

The project pins Mathlib to the same Lean release and imports only the
`Finset` union surface required by the fixed theorem kernel. Category and
pullback data remain represented locally.

## Next proof boundary

Before span composition is implemented, define:

1. the exact class of facet categories admitted by the protocol;
2. which cospans must have selected pullbacks;
3. role compatibility for multispan legs; and
4. equivalence or bicategorical coherence for composite span apexes.

The normative symbol-and-wiring corrections driving this module are recorded
in [`../docs/rrkc-cycle2-symbol-wiring-repair.md`](../docs/rrkc-cycle2-symbol-wiring-repair.md).
