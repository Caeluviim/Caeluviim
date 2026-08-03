/-!
RRKC R2 intrinsic core syntax.

The indices make malformed relation endpoints, operation arguments, and
sort-changing revisions unrepresentable. This file is a checked-design target
for Ott generation; until CI installs Lean/Ott, its status is "specified", not
"machine-proved".
-/

namespace RRKC

inductive Sort where
  | entity | claim | evidence | relation | activity | agent | policy | provenance | prop
  | code : Sort → Sort
  | arrow : Sort → Sort → Sort
  deriving DecidableEq, Repr

abbrev Context := List Sort

inductive Var : Context → Sort → Type where
  | zero : Var (τ :: Γ) τ
  | succ : Var Γ τ → Var (σ :: Γ) τ

structure RelationSymbol where
  name : String
  left : Sort
  right : Sort

structure OperationSymbol where
  name : String
  inputs : List Sort
  output : Sort

mutual
  inductive Args : Context → List Sort → Type where
    | nil : Args Γ []
    | cons : Term Γ τ → Args Γ τs → Args Γ (τ :: τs)

  inductive Term : Context → Sort → Type where
    | var : Var Γ τ → Term Γ τ
    | id : String → Term Γ .entity
    | claimEntity : Term Γ .claim → Term Γ .entity
    | evidenceEntity : Term Γ .evidence → Term Γ .entity
    | rel : (r : RelationSymbol) → Term Γ r.left → Term Γ r.right → Term Γ .relation
    | act : (σ : OperationSymbol) → Args Γ σ.inputs → Term Γ σ.output
    | stamp : Term Γ τ → Term Γ .provenance → Term Γ τ
    | revise : Term Γ τ → Term Γ τ → Term Γ τ
    | version : Term Γ τ → String → Term Γ τ
    | lam : Term (τ₁ :: Γ) τ₂ → Term Γ (.arrow τ₁ τ₂)
    | app : Term Γ (.arrow τ₁ τ₂) → Term Γ τ₁ → Term Γ τ₂
    | letE : Term Γ τ₁ → Term (τ₁ :: Γ) τ₂ → Term Γ τ₂
    | quote : Term Γ τ → Term Γ (.code τ)
    | decode : Term Γ (.code τ) → Term Γ τ
    | eval : Term Γ (.code τ) → Term Γ τ
end

inductive Proposition : Context → Type where
  | top | bottom
  | not : Proposition Γ → Proposition Γ
  | and : Proposition Γ → Proposition Γ → Proposition Γ
  | or : Proposition Γ → Proposition Γ → Proposition Γ
  | implies : Proposition Γ → Proposition Γ → Proposition Γ
  | forallE : Proposition (τ :: Γ) → Proposition Γ
  | existsE : Proposition (τ :: Γ) → Proposition Γ
  | eq : Term Γ τ → Term Γ τ → Proposition Γ
  | supports : Term Γ .evidence → Term Γ .claim → Proposition Γ
  | rebuts : Term Γ .evidence → Term Γ .claim → Proposition Γ
  | admissible : Term Γ τ → Proposition Γ
  | derivedFrom : Term Γ .entity → Term Γ .entity → Proposition Γ

abbrev Ren (Γ Δ : Context) := ∀ {τ}, Var Γ τ → Var Δ τ
abbrev Sub (Γ Δ : Context) := ∀ {τ}, Var Γ τ → Term Δ τ

def Ren.lift (ρ : Ren Γ Δ) : Ren (τ :: Γ) (τ :: Δ)
  | _, .zero => .zero
  | _, .succ v => .succ (ρ v)

mutual
  def renameArgs (ρ : Ren Γ Δ) : Args Γ τs → Args Δ τs
    | .nil => .nil
    | .cons t ts => .cons (rename ρ t) (renameArgs ρ ts)

  def rename (ρ : Ren Γ Δ) : Term Γ τ → Term Δ τ
    | .var v => .var (ρ v)
    | .id s => .id s
    | .claimEntity t => .claimEntity (rename ρ t)
    | .evidenceEntity t => .evidenceEntity (rename ρ t)
    | .rel r l rgt => .rel r (rename ρ l) (rename ρ rgt)
    | .act op args => .act op (renameArgs ρ args)
    | .stamp t p => .stamp (rename ρ t) (rename ρ p)
    | .revise l r => .revise (rename ρ l) (rename ρ r)
    | .version t v => .version (rename ρ t) v
    | .lam body => .lam (rename ρ.lift body)
    | .app f a => .app (rename ρ f) (rename ρ a)
    | .letE v body => .letE (rename ρ v) (rename ρ.lift body)
    | .quote t => .quote (rename ρ t)
    | .decode c => .decode (rename ρ c)
    | .eval c => .eval (rename ρ c)
end

def Sub.lift (σ : Sub Γ Δ) : Sub (τ :: Γ) (τ :: Δ)
  | _, .zero => .var .zero
  | _, .succ v => rename Var.succ (σ v)

mutual
  def substArgs (σ : Sub Γ Δ) : Args Γ τs → Args Δ τs
    | .nil => .nil
    | .cons t ts => .cons (subst σ t) (substArgs σ ts)

  def subst (σ : Sub Γ Δ) : Term Γ τ → Term Δ τ
    | .var v => σ v
    | .id s => .id s
    | .claimEntity t => .claimEntity (subst σ t)
    | .evidenceEntity t => .evidenceEntity (subst σ t)
    | .rel r l rgt => .rel r (subst σ l) (subst σ rgt)
    | .act op args => .act op (substArgs σ args)
    | .stamp t p => .stamp (subst σ t) (subst σ p)
    | .revise l r => .revise (subst σ l) (subst σ r)
    | .version t v => .version (subst σ t) v
    | .lam body => .lam (subst σ.lift body)
    | .app f a => .app (subst σ f) (subst σ a)
    | .letE v body => .letE (subst σ v) (subst σ.lift body)
    | .quote t => .quote (subst σ t)
    | .decode c => .decode (subst σ c)
    | .eval c => .eval (subst σ c)
end

structure Governance where
  admits : ∀ {Γ τ}, Term Γ τ → Term Γ τ → Prop

inductive Step (G : Governance) : Term Γ τ → Term Γ τ → Prop where
  | beta : Step G (.app (.lam body) arg)
      (subst (fun | .zero => arg | .succ v => .var v) body)
  | letE : Step G (.letE value body)
      (subst (fun | .zero => value | .succ v => .var v) body)
  | evalQuote : Step G (.eval (.quote t)) t
  | revise : G.admits old new → Step G (.revise old new) new

inductive Blocked (G : Governance) : Term Γ τ → Prop where
  | revise : (¬ G.admits old new) → Blocked G (.revise old new)

end RRKC
