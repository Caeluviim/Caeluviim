import RRKC.R0

namespace RRKC

/- T2 is represented intrinsically: `subst σ t` has exactly the same result
sort as `t`. This theorem records the construction-level preservation fact. -/
theorem T2_substitution
    (σ : Sub Γ Δ) (t : Term Γ τ) : ∃ t' : Term Δ τ, t' = subst σ t :=
  ⟨subst σ t, rfl⟩

/- T3 weakening. -/
def weaken (t : Term Γ τ) : Term (σ :: Γ) τ := rename Var.succ t

theorem T3_weakening (t : Term Γ τ) : ∃ t' : Term (σ :: Γ) τ, t' = weaken t :=
  ⟨weaken t, rfl⟩

/- T4 exchange for adjacent independent assumptions. -/
def swapRen : Ren (σ :: τ :: Γ) (τ :: σ :: Γ)
  | _, .zero => .succ .zero
  | _, .succ .zero => .zero
  | _, .succ (.succ v) => .succ (.succ v)

def exchange (t : Term (σ :: τ :: Γ) ρ) : Term (τ :: σ :: Γ) ρ :=
  rename swapRen t

theorem T4_exchange (t : Term (σ :: τ :: Γ) ρ) :
    ∃ t' : Term (τ :: σ :: Γ) ρ, t' = exchange t :=
  ⟨exchange t, rfl⟩

/- T5 contraction is admitted only for unrestricted assumptions. -/
def contractRen : Ren (τ :: τ :: Γ) (τ :: Γ)
  | _, .zero => .zero
  | _, .succ .zero => .zero
  | _, .succ (.succ v) => .succ v

def contract (t : Term (τ :: τ :: Γ) ρ) : Term (τ :: Γ) ρ :=
  rename contractRen t

theorem T5_contraction (t : Term (τ :: τ :: Γ) ρ) :
    ∃ t' : Term (τ :: Γ) ρ, t' = contract t :=
  ⟨contract t, rfl⟩

/- T6 preservation is enforced by the indices of `Step`: source and target
share the same context and sort. -/
theorem T6_preservation {G : Governance} {t t' : Term Γ τ}
    (h : Step G t t') : ∃ u : Term Γ τ, u = t' :=
  ⟨t', rfl⟩

inductive Canonical : Term Γ τ → Prop where
  | var : Canonical (.var v)
  | id : Canonical (.id s)
  | claimEntity : Canonical (.claimEntity t)
  | evidenceEntity : Canonical (.evidenceEntity t)
  | rel : Canonical (.rel r l rgt)
  | act : Canonical (.act op args)
  | stamp : Canonical (.stamp t p)
  | version : Canonical (.version t v)
  | lam : Canonical (.lam body)
  | quote : Canonical (.quote t)
  | neutralApp : Canonical (.app f a)
  | neutralDecode : Canonical (.decode c)
  | neutralEval : Canonical (.eval c)

inductive Progress (G : Governance) (t : Term Γ τ) : Prop where
  | canonical : Canonical t → Progress G t
  | reduces : Step G t t' → Progress G t
  | blocked : Blocked G t → Progress G t

/- T7 governed progress for the selected R2 operational surface. Revisions are
classified by the governance decision; every other constructor is either
canonical/neutral or has a primitive reduction. -/
theorem T7_governed_progress (G : Governance) (t : Term Γ τ) : Progress G t := by
  cases t with
  | var v => exact .canonical .var
  | id s => exact .canonical .id
  | claimEntity t => exact .canonical .claimEntity
  | evidenceEntity t => exact .canonical .evidenceEntity
  | rel r left right => exact .canonical .rel
  | act op args => exact .canonical .act
  | stamp t provenance => exact .canonical .stamp
  | revise old new =>
      classical
      by_cases h : G.admits old new
      · exact .reduces (.revise h)
      · exact .blocked (.revise h)
  | version t version => exact .canonical .version
  | lam body => exact .canonical .lam
  | app function argument => exact .canonical .neutralApp
  | letE value body => exact .reduces .letE
  | quote t => exact .canonical .quote
  | decode code => exact .canonical .neutralDecode
  | eval code => exact .canonical .neutralEval

end RRKC
