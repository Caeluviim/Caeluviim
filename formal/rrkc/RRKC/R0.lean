/-!
RRKC R2 intrinsic core syntax.

The indices make malformed relation endpoints, operation arguments, and
sort-changing revisions unrepresentable. This file is compiled by the RRKC
formal-verification workflow and contains no proof placeholders.
-/

namespace RRKC

inductive Ty where
  | entity | claim | evidence | relation | activity | agent | policy | provenance | prop
  | code : Ty → Ty
  | arrow : Ty → Ty → Ty
  deriving DecidableEq, Repr

abbrev Context := List Ty

inductive Var : Context → Ty → Type where
  | zero : Var (τ :: Γ) τ
  | succ : Var Γ τ → Var (σ :: Γ) τ

structure RelationSymbol where
  name : String
  left : Ty
  right : Ty

structure OperationSymbol where
  name : String
  inputs : List Ty
  output : Ty

mutual
  inductive Args : Context → List Ty → Type where
    | nil : Args Γ []
    | cons : Term Γ τ → Args Γ τs → Args Γ (τ :: τs)

  inductive Term : Context → Ty → Type where
    | var : Var Γ τ → Term Γ τ
    | id : String → Term Γ Ty.entity
    | claimEntity : Term Γ Ty.claim → Term Γ Ty.entity
    | evidenceEntity : Term Γ Ty.evidence → Term Γ Ty.entity
    | rel : (r : RelationSymbol) →
        Term Γ r.left → Term Γ r.right → Term Γ Ty.relation
    | act : (op : OperationSymbol) → Args Γ op.inputs → Term Γ op.output
    | stamp : Term Γ τ → Term Γ Ty.provenance → Term Γ τ
    | revise : Term Γ τ → Term Γ τ → Term Γ τ
    | version : Term Γ τ → String → Term Γ τ
    | lam : Term (τ₁ :: Γ) τ₂ → Term Γ (Ty.arrow τ₁ τ₂)
    | app : Term Γ (Ty.arrow τ₁ τ₂) → Term Γ τ₁ → Term Γ τ₂
    | letE : Term Γ τ₁ → Term (τ₁ :: Γ) τ₂ → Term Γ τ₂
    | quote : Term Γ τ → Term Γ (Ty.code τ)
    | decode : Term Γ (Ty.code τ) → Term Γ τ
    | eval : Term Γ (Ty.code τ) → Term Γ τ
end

inductive Proposition : Context → Type where
  | top : Proposition Γ
  | bottom : Proposition Γ
  | not : Proposition Γ → Proposition Γ
  | and : Proposition Γ → Proposition Γ → Proposition Γ
  | or : Proposition Γ → Proposition Γ → Proposition Γ
  | implies : Proposition Γ → Proposition Γ → Proposition Γ
  | forallE : Proposition (τ :: Γ) → Proposition Γ
  | existsE : Proposition (τ :: Γ) → Proposition Γ
  | eq : Term Γ τ → Term Γ τ → Proposition Γ
  | supports : Term Γ Ty.evidence → Term Γ Ty.claim → Proposition Γ
  | rebuts : Term Γ Ty.evidence → Term Γ Ty.claim → Proposition Γ
  | admissible : Term Γ τ → Proposition Γ
  | derivedFrom : Term Γ Ty.entity → Term Γ Ty.entity → Proposition Γ

abbrev Ren (Γ Δ : Context) := ∀ {τ}, Var Γ τ → Var Δ τ
abbrev Sub (Γ Δ : Context) := ∀ {τ}, Var Γ τ → Term Δ τ

def Ren.lift (ρ : Ren Γ Δ) : Ren (τ :: Γ) (τ :: Δ) :=
  fun {_} v =>
    match v with
    | .zero => .zero
    | .succ v => .succ (ρ v)

def Ren.weaken : Ren Γ (τ :: Γ) := fun v => .succ v

mutual
  def renameArgs (ρ : Ren Γ Δ) : Args Γ τs → Args Δ τs
    | .nil => .nil
    | .cons t ts => .cons (rename ρ t) (renameArgs ρ ts)

  def rename (ρ : Ren Γ Δ) : Term Γ τ → Term Δ τ
    | .var v => .var (ρ v)
    | .id s => .id s
    | .claimEntity t => .claimEntity (rename ρ t)
    | .evidenceEntity t => .evidenceEntity (rename ρ t)
    | .rel r left right => .rel r (rename ρ left) (rename ρ right)
    | .act op args => .act op (renameArgs ρ args)
    | .stamp t p => .stamp (rename ρ t) (rename ρ p)
    | .revise left right => .revise (rename ρ left) (rename ρ right)
    | .version t v => .version (rename ρ t) v
    | .lam body => .lam (rename ρ.lift body)
    | .app f a => .app (rename ρ f) (rename ρ a)
    | .letE value body => .letE (rename ρ value) (rename ρ.lift body)
    | .quote t => .quote (rename ρ t)
    | .decode c => .decode (rename ρ c)
    | .eval c => .eval (rename ρ c)
end

def Sub.lift (σ : Sub Γ Δ) : Sub (τ :: Γ) (τ :: Δ) :=
  fun {_} v =>
    match v with
    | .zero => .var .zero
    | .succ v => rename Ren.weaken (σ v)

mutual
  def substArgs (σ : Sub Γ Δ) : Args Γ τs → Args Δ τs
    | .nil => .nil
    | .cons t ts => .cons (subst σ t) (substArgs σ ts)

  def subst (σ : Sub Γ Δ) : Term Γ τ → Term Δ τ
    | .var v => σ v
    | .id s => .id s
    | .claimEntity t => .claimEntity (subst σ t)
    | .evidenceEntity t => .evidenceEntity (subst σ t)
    | .rel r left right => .rel r (subst σ left) (subst σ right)
    | .act op args => .act op (substArgs σ args)
    | .stamp t p => .stamp (subst σ t) (subst σ p)
    | .revise left right => .revise (subst σ left) (subst σ right)
    | .version t v => .version (subst σ t) v
    | .lam body => .lam (subst σ.lift body)
    | .app f a => .app (subst σ f) (subst σ a)
    | .letE value body => .letE (subst σ value) (subst σ.lift body)
    | .quote t => .quote (subst σ t)
    | .decode c => .decode (subst σ c)
    | .eval c => .eval (subst σ c)
end

def singleSub (argument : Term Γ τ) : Sub (τ :: Γ) Γ :=
  fun {_} v =>
    match v with
    | .zero => argument
    | .succ v => .var v

structure Governance where
  admits : {Γ : Context} → {τ : Ty} → Term Γ τ → Term Γ τ → Prop

inductive Step (G : Governance) : Term Γ τ → Term Γ τ → Prop where
  | beta : Step G (.app (.lam body) argument)
      (subst (singleSub argument) body)
  | letE : Step G (.letE value body)
      (subst (singleSub value) body)
  | evalQuote : Step G (.eval (.quote t)) t
  | revise : G.admits old new → Step G (.revise old new) new

inductive Blocked (G : Governance) : Term Γ τ → Prop where
  | revise : (¬ G.admits old new) → Blocked G (.revise old new)

end RRKC
