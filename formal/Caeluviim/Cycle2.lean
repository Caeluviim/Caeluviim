import Mathlib.Data.Finset.Union

/-!
# Recursive Reflective Knowledge Calculus — Cycle 2

This module formalizes the first structural layer of the Cycle 2 repair:

* static signatures are separated from runtime vocabularies and states;
* relation occurrences are objects;
* incidence maps are morphisms;
* operator symbols are separated from their denotations;
* runtime history is append-only; and
* historical monotonicity (M1) is proved.

Span composition is intentionally left behind an abstract interface until the
base category and its pullback conditions have been mechanized.
-/

namespace Caeluviim.RRKC.Cycle2

universe u

/-- The static language and governance declarations. Changing runtime
populations do not occur in this structure. -/
structure StaticSignature where
  FacetType : Type u
  Role : Type u
  RoleSignature : Type u
  roleDeclarations : RoleSignature → List (Role × FacetType)
  Operator : Type u
  FormationRuleSymbol : Type u
  Judgment : Type u
  StructuralConstraint : Type u
  GovernancePolicy : Type u
  governance : GovernancePolicy

/-- A small, dependency-free presentation of a category. `comp f g` means
first `f`, then `g` (that is, `g ∘ f` in conventional notation). -/
structure FacetCategory (sig : StaticSignature) where
  Facet : Type u
  Hom : Facet → Facet → Type u
  id : (A : Facet) → Hom A A
  comp : {A B C : Facet} → Hom A B → Hom B C → Hom A C
  comp_assoc :
    ∀ {A B C D : Facet}
      (f : Hom A B) (g : Hom B C) (h : Hom C D),
      comp (comp f g) h = comp f (comp g h)
  id_comp :
    ∀ {A B : Facet} (f : Hom A B),
      comp (id A) f = f
  comp_id :
    ∀ {A B : Facet} (f : Hom A B),
      comp f (id B) = f
  HasType : Facet → sig.FacetType → Prop
  relationFacet : sig.FacetType

/-- A role-typed structural map from a reified relation occurrence to one of
its participants. The map, not the relation occurrence, is a morphism. -/
structure Incidence
    {sig : StaticSignature}
    (baseCategory : FacetCategory sig)
    (relation : baseCategory.Facet) where
  participant : baseCategory.Facet
  role : sig.Role
  arrow : baseCategory.Hom relation participant

/-- The general arbitrary-arity representation. `apex` is the addressable
relation occurrence. Its incidence legs carry the semantic roles. -/
structure RelationOccurrence
    {sig : StaticSignature}
    (baseCategory : FacetCategory sig) where
  apex : baseCategory.Facet
  relationType : baseCategory.Facet
  roleSignature : sig.RoleSignature
  apexIsRelation : baseCategory.HasType apex baseCategory.relationFacet
  instantiates : baseCategory.Hom apex relationType
  incidences : List (Incidence baseCategory apex)

/-- The binary specialization of a relation occurrence, presented as a span.
No claim is made here that arbitrary semantic relations compose. -/
structure BinaryRelationSpan
    {sig : StaticSignature}
    (baseCategory : FacetCategory sig)
    (A C : baseCategory.Facet) where
  occurrence : RelationOccurrence baseCategory
  sourceRole : sig.Role
  targetRole : sig.Role
  sourceLeg : baseCategory.Hom occurrence.apex A
  targetLeg : baseCategory.Hom occurrence.apex C

/-- Abstract evidence that a selected cospan has a pullback. Cycle 2 does not
postulate that every cospan in the facet category has one. -/
structure PullbackCone
    {sig : StaticSignature}
    (baseCategory : FacetCategory sig)
    {A X Y : baseCategory.Facet}
    (left : baseCategory.Hom X A)
    (right : baseCategory.Hom Y A) where
  apex : baseCategory.Facet
  fst : baseCategory.Hom apex X
  snd : baseCategory.Hom apex Y
  commutes :
    baseCategory.comp fst left = baseCategory.comp snd right
  lift :
    {Q : baseCategory.Facet} →
    (q₁ : baseCategory.Hom Q X) →
    (q₂ : baseCategory.Hom Q Y) →
    baseCategory.comp q₁ left = baseCategory.comp q₂ right →
    baseCategory.Hom Q apex
  lift_fst :
    ∀ {Q : baseCategory.Facet}
      (q₁ : baseCategory.Hom Q X)
      (q₂ : baseCategory.Hom Q Y)
      (h : baseCategory.comp q₁ left = baseCategory.comp q₂ right),
      baseCategory.comp (lift q₁ q₂ h) fst = q₁
  lift_snd :
    ∀ {Q : baseCategory.Facet}
      (q₁ : baseCategory.Hom Q X)
      (q₂ : baseCategory.Hom Q Y)
      (h : baseCategory.comp q₁ left = baseCategory.comp q₂ right),
      baseCategory.comp (lift q₁ q₂ h) snd = q₂
  lift_unique :
    ∀ {Q : baseCategory.Facet}
      (q₁ : baseCategory.Hom Q X)
      (q₂ : baseCategory.Hom Q Y)
      (h : baseCategory.comp q₁ left = baseCategory.comp q₂ right)
      (candidate : baseCategory.Hom Q apex),
      baseCategory.comp candidate fst = q₁ →
      baseCategory.comp candidate snd = q₂ →
      candidate = lift q₁ q₂ h

/-- Four-valued evidence-bearing validation result. -/
inductive ValidationResult where
  | pass
  | fail
  | unknown
  | error
  deriving Repr, DecidableEq

/-- Runtime carrier types and the explicit projection wiring from history into
facet, relation, provenance, validation, governance, and execution views. -/
structure RuntimeVocabulary (sig : StaticSignature) where
  LedgerId : Type u
  LedgerPosition : Type u
  LedgerEntry : Type u
  ActiveView : Type u
  Workspace : Type u
  ExecutionRecord : Type u
  Provenance : Type u
  FacetRevision : Type u
  RelationRevision : Type u
  ProvenanceRecord : Type u
  ValidationDimension : Type u
  ValidationReport : Type u
  GovernanceEvent : Type u
  GovernanceActor : Type u
  GovernanceState : Type u
  entryId : LedgerEntry → LedgerId
  stableEntryIdentity : Function.Injective entryId
  entryPosition : LedgerEntry → LedgerPosition
  stableLedgerPosition : Function.Injective entryPosition
  relationAsFacet : RelationRevision → FacetRevision
  facetRevisions : Finset LedgerEntry → Set FacetRevision
  relationRevisions : Finset LedgerEntry → Set RelationRevision
  provenanceRecords : Finset LedgerEntry → Set ProvenanceRecord
  validationReports : Finset LedgerEntry → Set ValidationReport
  governanceEvents : Finset LedgerEntry → List GovernanceEvent
  executionRecords : Finset LedgerEntry → Set ExecutionRecord
  relationProjectionContained :
    ∀ history relation,
      relation ∈ relationRevisions history →
      relationAsFacet relation ∈ facetRevisions history
  provenanceGraph : Set ProvenanceRecord → Provenance
  validate :
    ValidationDimension →
    LedgerEntry →
    ValidationResult × ValidationReport
  validationReportGrounded :
    ∀ history report,
      report ∈ validationReports history →
      ∃ dimension entry result,
        entry ∈ history ∧ validate dimension entry = (result, report)
  initialGovernanceState : sig.GovernancePolicy → GovernanceState
  governanceActor : GovernanceEvent → GovernanceActor
  governanceEnabled :
    sig.GovernancePolicy →
    GovernanceState →
    GovernanceEvent →
    Prop
  governanceAuthority :
    sig.GovernancePolicy →
    GovernanceActor →
    GovernanceEvent →
    Prop
  applyGovernanceEvent :
    sig.GovernancePolicy →
    GovernanceState →
    GovernanceEvent →
    GovernanceState
  GovernanceTraceLegal :
    sig.GovernancePolicy →
    List GovernanceEvent →
    Prop
  activeFrom :
    sig.GovernancePolicy →
    GovernanceState →
    Finset LedgerEntry →
    ActiveView
  workspaceAfterAppend : Workspace → Finset LedgerEntry → Workspace
  WellFormedState : Finset LedgerEntry → ActiveView → Workspace → Prop
  WellFormedDelta :
    Finset LedgerEntry → Provenance → ExecutionRecord → Prop
  DeltaProvenanceCovers : Finset LedgerEntry → Provenance → Prop

/-- The canonical runtime state `⟨H, A, W⟩`. -/
structure RuntimeState
    (sig : StaticSignature)
    (V : RuntimeVocabulary sig) where
  history : Finset V.LedgerEntry
  active : V.ActiveView
  workspace : V.Workspace

/-- A successful append carries both the new entries and the evidence required
to account for their production. -/
structure Delta
    {sig : StaticSignature}
    (V : RuntimeVocabulary sig) where
  entries : Finset V.LedgerEntry
  provenance : V.Provenance
  record : V.ExecutionRecord
  provenanceCovers : V.DeltaProvenanceCovers entries provenance
  wellFormed : V.WellFormedDelta entries provenance record

/-- Replay an ordered governance-event projection under the static policy. -/
def GovernanceStateFromHistory
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    (history : Finset V.LedgerEntry) : V.GovernanceState :=
  (V.governanceEvents history).foldl
    (V.applyGovernanceEvent sig.governance)
    (V.initialGovernanceState sig.governance)

/-- The governance transition state is derived from the static policy and the
ordered governance-event projection of history. -/
def GovernanceStateOf
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    (state : RuntimeState sig V) : V.GovernanceState :=
  GovernanceStateFromHistory state.history

/-- The active view follows one explicit dependency chain:
static policy → projected governance events → governance state → active view. -/
def DerivedActiveView
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    (state : RuntimeState sig V) : V.ActiveView :=
  V.activeFrom sig.governance (GovernanceStateOf state) state.history

/-- State well-formedness includes active-view coherence rather than leaving
the active component disconnected from governance. -/
def StateWellFormed
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    (state : RuntimeState sig V) : Prop :=
  V.WellFormedState state.history state.active state.workspace ∧
    V.GovernanceTraceLegal
      sig.governance
      (V.governanceEvents state.history) ∧
    state.active = DerivedActiveView state

/-- Apply a provenance-bearing append. The active view is recomputed under the
fixed governance policy and the workspace follows its declared lifecycle. -/
def applyDelta
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    [DecidableEq V.LedgerEntry]
    (state : RuntimeState sig V)
    (delta : Delta V) : RuntimeState sig V :=
  let nextHistory := state.history ∪ delta.entries
  let nextGovernance := GovernanceStateFromHistory nextHistory
  {
    history := nextHistory
    active := V.activeFrom sig.governance nextGovernance nextHistory
    workspace := V.workspaceAfterAppend state.workspace delta.entries
  }

/-- Successful admissible transitions are exactly provenance-bearing appends
whose resulting state satisfies the declared well-formedness constraints. -/
inductive Transition
    {sig : StaticSignature}
    (V : RuntimeVocabulary sig)
    [DecidableEq V.LedgerEntry] :
    RuntimeState sig V → RuntimeState sig V → Prop where
  | append
      (state : RuntimeState sig V)
      (delta : Delta V)
      (wellFormedAfter : StateWellFormed (applyDelta state delta)) :
      Transition V state (applyDelta state delta)

/-- Carrier types used by a frozen execution configuration. -/
structure ExecutionVocabulary where
  Task : Type u
  CorpusSnapshot : Type u
  Parameters : Type u
  ResourceBudget : Type u
  NondeterminismTrace : Type u
  Agent : Type u
  ClockContext : Type u
  RuleOrdering : Type u
  ExternalResponseTrace : Type u
  SemanticVersion : Type u

/-- The frozen execution configuration includes every input required by the
replay claim, with descriptive identifiers instead of font distinctions. -/
structure ExecutionConfiguration (X : ExecutionVocabulary) where
  task : X.Task
  corpus : X.CorpusSnapshot
  parameters : X.Parameters
  resourceBudget : X.ResourceBudget
  nondeterminismTrace : X.NondeterminismTrace
  agent : X.Agent
  clock : X.ClockContext
  ruleOrdering : X.RuleOrdering
  externalResponseTrace : X.ExternalResponseTrace
  semanticVersion : X.SemanticVersion

/-- Explicit failure states for malformed input, failed validation, exhausted
budgets, unavailable dependencies, or domain errors. -/
inductive TransitionFailure where
  | malformedInput
  | validationFailure
  | budgetExhausted
  | dependencyUnavailable
  | outsideOperatorDomain
  deriving Repr, DecidableEq

/-- A generic log-bearing partial computation. -/
inductive ExecutionOutcome
    {sig : StaticSignature}
    (V : RuntimeVocabulary sig)
    (α : Type u) where
  | success (value : α) (log : List V.ExecutionRecord)
  | failure (reason : TransitionFailure) (log : List V.ExecutionRecord)

namespace ExecutionOutcome

/-- Monadic bind accumulates logs on both successful and failed continuations.
This is the composition operation required by the execution pipeline. -/
def bind
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    {α β : Type u}
    (outcome : ExecutionOutcome V α)
    (next : α → ExecutionOutcome V β) :
    ExecutionOutcome V β :=
  match outcome with
  | .success value priorLog =>
      match next value with
      | .success result laterLog =>
          .success result (priorLog ++ laterLog)
      | .failure reason laterLog =>
          .failure reason (priorLog ++ laterLog)
  | .failure reason priorLog =>
      .failure reason priorLog

end ExecutionOutcome

/-- A state step is a partial, log-bearing state computation. -/
abbrev StateStep
    (sig : StaticSignature)
    (V : RuntimeVocabulary sig) :=
  RuntimeState sig V → ExecutionOutcome V (RuntimeState sig V)

/-- Identity for state-step composition. -/
def pureStep
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig} :
    StateStep sig V :=
  fun state => .success state []

/-- Kleisli composition, kept distinct from structural composition in the
facet category. -/
def kleisliCompose
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    (first second : StateStep sig V) :
    StateStep sig V :=
  fun state => ExecutionOutcome.bind (first state) second

/-- Assemble audit, plan, expansion, correction, repair, validation, and log
steps without losing partiality or emitted records. -/
def assembleSteps
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    (steps : List (StateStep sig V)) :
    StateStep sig V :=
  steps.foldl kleisliCompose pureStep

/-- The semantic interpretation of an operator symbol. No functoriality is
asserted by this type. -/
abbrev OperatorDenotation
    (sig : StaticSignature)
    (V : RuntimeVocabulary sig)
    (X : ExecutionVocabulary) :=
  ExecutionConfiguration X → sig.Operator → StateStep sig V

/-- Interpret an ordered operator program under one frozen configuration and
assemble it with log-accumulating Kleisli composition. -/
def executionPipeline
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    {X : ExecutionVocabulary}
    (denotation : OperatorDenotation sig V X)
    (configuration : ExecutionConfiguration X)
    (operators : List sig.Operator) :
    StateStep sig V :=
  assembleSteps (operators.map (denotation configuration))

/-- Fixed points belong to the defined execution step; there is no orphan
capital-omega operator. Emitted logs need not be empty. -/
def IsExecutionFixedPoint
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    (execution : StateStep sig V)
    (state : RuntimeState sig V) : Prop :=
  ∃ log, execution state = .success state log

/-- Shared digest vocabulary permits comparison between distinct executors. -/
structure ReplayVocabulary where
  ResultDigest : Type u

/-- One executor manifestation. Two values of this structure are required for
a non-tautological replay comparison. -/
structure Executor
    (sig : StaticSignature)
    (V : RuntimeVocabulary sig)
    (X : ExecutionVocabulary)
    (R : ReplayVocabulary) where
  implementationVersion : X.SemanticVersion
  run :
    ExecutionConfiguration X →
    RuntimeState sig V →
    ExecutionOutcome V (RuntimeState sig V)
  digest :
    ExecutionOutcome V (RuntimeState sig V) →
    R.ResultDigest

/-- M6's intended two-run content. This proposition is not proved merely by
reflexivity because `leftExecutor` and `rightExecutor` are distinct inputs. -/
def ReplayAgreement
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    {X : ExecutionVocabulary}
    {R : ReplayVocabulary}
    (leftExecutor rightExecutor : Executor sig V X R) : Prop :=
  ∀ input state,
    leftExecutor.digest (leftExecutor.run input state) =
      rightExecutor.digest (rightExecutor.run input state)

/-- A deployment reflection tower is finite and ends at an explicitly trusted
checker. Infinite reflective ascent is not an execution prerequisite. -/
structure ReflectionBoundary where
  KernelId : Type u
  ProofArtifact : Type u
  CheckResult : Type u
  topLevel : Nat
  trustedKernelId : KernelId
  trustedChecker : ProofArtifact → CheckResult

/-- Operations needed to state provenance-union laws. No algebraic law is
embedded here; P1–P4 remain proof obligations. -/
structure ProvenanceUnionCandidate
    {sig : StaticSignature}
    (V : RuntimeVocabulary sig) where
  normalize : V.Provenance → V.Provenance
  graphUnion : V.Provenance → V.Provenance → V.Provenance
  empty : V.Provenance
  canonicallyIsomorphic : V.Provenance → V.Provenance → Prop

def lineageUnion
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    (candidate : ProvenanceUnionCandidate V)
    (left right : V.Provenance) : V.Provenance :=
  candidate.normalize (candidate.graphUnion left right)

def ProvenanceAssociative
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    (candidate : ProvenanceUnionCandidate V) : Prop :=
  ∀ left middle right,
    candidate.canonicallyIsomorphic
      (lineageUnion candidate left (lineageUnion candidate middle right))
      (lineageUnion candidate (lineageUnion candidate left middle) right)

def ProvenanceCommutative
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    (candidate : ProvenanceUnionCandidate V) : Prop :=
  ∀ left right,
    candidate.canonicallyIsomorphic
      (lineageUnion candidate left right)
      (lineageUnion candidate right left)

def ProvenanceIdempotent
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    (candidate : ProvenanceUnionCandidate V) : Prop :=
  ∀ provenance,
    candidate.canonicallyIsomorphic
      (lineageUnion candidate provenance provenance)
      provenance

def ProvenanceEmptyIdentity
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    (candidate : ProvenanceUnionCandidate V) : Prop :=
  ∀ provenance,
    candidate.canonicallyIsomorphic
      (lineageUnion candidate provenance candidate.empty)
      provenance

/-- M1 — Historical monotonicity.

Every event present before an admissible transition remains present after it.
This theorem concerns history only; it says nothing about continued membership
in the governed active view. -/
theorem historical_monotonicity
    {sig : StaticSignature}
    {V : RuntimeVocabulary sig}
    [DecidableEq V.LedgerEntry]
    {before after : RuntimeState sig V}
    (transition : Transition V before after) :
    before.history ⊆ after.history := by
  cases transition with
  | append delta wellFormedAfter =>
      intro entry presentBefore
      exact Finset.mem_union_left delta.entries presentBefore

/-- The required status discipline for metatheoretic statements. -/
inductive MetatheoryStatus where
  | definition
  | axiom
  | provedTheorem
  | conditionalTheorem
  | proofObligation
  | conjecture
  | rejectedClaim
  deriving Repr, DecidableEq

/-- Machine-readable Cycle 2 register identifiers. -/
inductive MetatheoryId where
  | M1HistoricalMonotonicity
  | M2ActiveViewDeterminism
  | M3TypePreservation
  | M4ProvenancePreservation
  | M5RelativeReflectionPreservation
  | M6ReplayDeterminism
  | M7Confluence
  | M8FixedPointExistence
  | M9Termination
  | M10SpanCompositionCoherence
  deriving Repr, DecidableEq

/-- Provenance laws are separately registered because identifier normalization
must be proved adequate before any of them can be used. -/
inductive ProvenanceLawId where
  | P1Associativity
  | P2Commutativity
  | P3Idempotency
  | P4EmptyIdentity
  deriving Repr, DecidableEq

/-- The specification's current proof-status register. -/
def metatheoryStatus : MetatheoryId → MetatheoryStatus
  | .M1HistoricalMonotonicity => .provedTheorem
  | .M2ActiveViewDeterminism => .conditionalTheorem
  | .M3TypePreservation => .proofObligation
  | .M4ProvenancePreservation => .proofObligation
  | .M5RelativeReflectionPreservation => .proofObligation
  | .M6ReplayDeterminism => .conditionalTheorem
  | .M7Confluence => .conjecture
  | .M8FixedPointExistence => .conjecture
  | .M9Termination => .proofObligation
  | .M10SpanCompositionCoherence => .conditionalTheorem

/-- No provenance algebraic law is promoted beyond proof-obligation status. -/
def provenanceLawStatus : ProvenanceLawId → MetatheoryStatus
  | .P1Associativity => .proofObligation
  | .P2Commutativity => .proofObligation
  | .P3Idempotency => .proofObligation
  | .P4EmptyIdentity => .proofObligation

end Caeluviim.RRKC.Cycle2
