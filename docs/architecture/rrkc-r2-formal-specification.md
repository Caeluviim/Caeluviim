# RRKC R2 — Closed Formal Specification

**Module identifier:** `urn:caeluviim:module:rrkc:r2`  
**Version:** `2.0.0`  
**Status:** Proposed — implemented as a specification and executable reference, not ratified  
**Governing order:** Mathematical foundation → formal language → calculus → execution model  
**Tower:** `R0 ⊂ RE ⊂ RR ⊂ RS ⊂ RX`

## 0. Normative boundary

The words **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are normative. A file that parses, a test that passes, or a record that ingests does not by itself establish theoremhood, semantic truth, governance ratification, or empirical validity.

R2 closes the syntactic and inferential gaps identified in R1:

1. binders are explicit;
2. proposition syntax is separate from term syntax;
3. relation and operation applications are signature-indexed;
4. every term constructor has a formation and sorting rule;
5. revisions preserve sort before governance is consulted;
6. governance operations transform governance state;
7. observation contexts and canonical code are declared;
8. provenance precedence is a strict acyclic order;
9. the terminating reflective fragment has a well-founded measure; and
10. theorem status distinguishes specification, executable checking, and machine proof.

## I. Mathematical universe

Let `U0 ∈ U1 ∈ ...` be a selected Grothendieck-style hierarchy. All finite syntax, derivations, contexts, signatures, and execution records used by a conforming implementation inhabit `U0`. Collections of models and semantic domains MAY inhabit `U1` or higher.

For self-hosting, protocol configurations form a pointed CPO `(C, ⊑C, ⊥C, ⊔C)`. The order `⊑C` is the information-approximation order. It is not the implementation-refinement relation introduced in Section XIV.

A configuration constructor `F : C → C` MUST be Scott-continuous when the Kleene construction is used:

`P* = lfp(F) = ⊔n≥0 F^n(⊥C)`.

A conforming alternative MAY use a complete lattice `(L, ≤L)` and monotone `F`, obtaining fixed points by Knaster–Tarski. An implementation MUST state which construction it uses and MUST NOT infer continuity from monotonicity.

## II. Signatures

A signature is:

`Σ = (S, OR, OO, arR, arO, C0)`

where:

- `S` is the set of sorts;
- `OR` is the set of relation symbols;
- `OO` is the set of operation symbols;
- `arR : OR → S × S` gives the permitted left and right endpoint sorts;
- `arO : OO → S* × S` gives the ordered input sorts and output sort of an operation; and
- `C0` is the set of declared constants and their sorts.

A relation or operation symbol not declared in `Σ` is ill formed. Matching only the number of arguments is insufficient; every argument sort MUST match the declared profile.

## III. Sorts, terms, and propositions

### III.1 Sorts

`τ ::= Entity | Claim | Evidence | Relation | Activity | Agent | Policy | Provenance | Prop | Code_l(τ) | τ1 → τ2`

`Code_l(τ)` is code at reflection level `l ∈ ℕ`. Surface notation `Code(τ)` abbreviates a level chosen by the enclosing layer. Evaluation MUST strictly lower code level in the terminating fragment.

### III.2 Terms

`e ::= x_τ`

`| id(a)`

`| claim(e)`

`| evidence(e)`

`| rel(r,e1,e2)`

`| act(σ,[e1,...,en])`

`| stamp(e,π)`

`| revise(e,e')`

`| e@v`

`| λx:τ.e`

`| e1 e2`

`| let x:τ=e1 in e2`

`| quote_l(e)`

`| decode_l(c)`

`| eval_l(c)`

The binders are `λx:τ.e` and `let x:τ=e1 in e2`. The variable is bound only in the body, not in the `let` value. Quotation is structural and does not bind free variables.

### III.3 Propositions

`φ ::= ⊤ | ⊥ | ¬φ | φ∧ψ | φ∨ψ | φ⇒ψ`

`| ∀x:τ.φ | ∃x:τ.φ`

`| e1 =_τ e2`

`| Supports(d,p)`

`| Rebuts(d,p)`

`| Proof(π,φ)`

`| Admissible(T)`

`| Precedes(n1,n2)`

`| DerivedFrom(e,e')`

`Claim` and `Prop` are distinct. `Claim` is protocol content that can be addressed, governed, supported, rebutted, versioned, and represented as an entity. `Prop` is the internal logical sort used by proof judgments. A signature MAY provide a constructor `asserts : Claim → Prop`, but no implicit coercion is permitted.

### III.4 Contexts

Typing contexts are finite ordered lists:

`Γ ::= · | Γ,x:τ`.

Governance states are:

`ΓG = (P,R,Δ,V,Q)`

where `P` is policy state, `R` is roles and permissions, `Δ` is a delegation DAG, `V` is the active veto/block set, and `Q` contains operation-specific quorum or authorization evidence.

## IV. Binding, substitution, and alpha-equivalence

`FV` and `BV` are defined by structural recursion. Critical cases are:

- `FV(λx:τ.e) = FV(e) \ {x}`;
- `BV(λx:τ.e) = BV(e) ∪ {x}`;
- `FV(let x:τ=e1 in e2) = FV(e1) ∪ (FV(e2) \ {x})`;
- `BV(let x:τ=e1 in e2) = BV(e1) ∪ BV(e2) ∪ {x}`;
- `FV(∀x:τ.φ) = FV(φ) \ {x}`; and
- `FV(∃x:τ.φ) = FV(φ) \ {x}`.

Capture-avoiding substitution `e[e'/x]` is defined structurally. When entering a binder `y`, if `y ∈ FV(e')` and `y ≠ x`, the binder MUST first be alpha-renamed to a fresh name. The same rule applies to propositions.

Alpha-equivalence `=_α` is the least congruence identifying terms and propositions that differ only by consistent renaming of bound variables. Persistent identifiers, constants, free variables, relation symbols, operation symbols, and version identifiers are not alpha-renamable.

## V. Formation and static semantics

Judgments include:

- `Γ ⊢ e wf`;
- `Γ ⊢ e : τ`;
- `Γ ⊢ φ prop`;
- `Γ ⊢ π : φ`;
- `Γ ⊢ e1 = e2 : τ`; and
- `Γ ⊢ e1 ≡ e2 : τ`.

### V.1 Term sorting rules

**Variable**

If `(x:τ) ∈ Γ`, then `Γ ⊢ x : τ`.

**Identifier**

If `a` is a declared identifier, then `Γ ⊢ id(a) : Entity`.

**Claim entity**

If `Γ ⊢ p : Claim`, then `Γ ⊢ claim(p) : Entity`.

**Evidence entity**

If `Γ ⊢ d : Evidence`, then `Γ ⊢ evidence(d) : Entity`.

**Relation**

If `arR(r)=(τ1,τ2)`, `Γ ⊢ e1:τ1`, and `Γ ⊢ e2:τ2`, then:

`Γ ⊢ rel(r,e1,e2) : Relation`.

**Activity**

If `arO(σ)=([τ1,...,τn],τ)`, and each `Γ ⊢ ei:τi`, then:

`Γ ⊢ act(σ,[e1,...,en]) : τ`.

Operations may return `Activity` or another declared sort. R1's unconditional `Activity` result is therefore replaced by the declared output sort.

**Stamp**

If `Γ ⊢ e:τ` and `Γ ⊢ π:Provenance`, then `Γ ⊢ stamp(e,π):τ`.

**Revision**

If `Γ ⊢ e:τ` and `Γ ⊢ e':τ`, then `Γ ⊢ revise(e,e'):τ`.

A sort-changing revision is ill formed before any governance judgment is attempted.

**Version**

If `Γ ⊢ e:τ`, then `Γ ⊢ e@v:τ`.

**Lambda**

If `Γ,x:τ1 ⊢ e:τ2`, then `Γ ⊢ λx:τ1.e : τ1→τ2`.

**Application**

If `Γ ⊢ e1:τ1→τ2` and `Γ ⊢ e2:τ1`, then `Γ ⊢ e1 e2:τ2`.

**Let**

If `Γ ⊢ e1:τ1` and `Γ,x:τ1 ⊢ e2:τ2`, then:

`Γ ⊢ let x:τ1=e1 in e2 : τ2`.

**Quote**

If `Γ ⊢ e:τ`, then `Γ ⊢ quote_l(e):Code_l(τ)`.

**Decode**

If `Γ ⊢ c:Code_l(τ)` and `CanonicalCode_l(c)`, then `Γ ⊢ decode_l(c):τ`.

**Eval**

If `Γ ⊢ c:Code_(l+1)(τ)`, then `Γ ⊢ eval_l(c):τ`.

Typing `eval` does not establish that it reduces. Reduction requires canonical code or another explicitly admitted evaluator rule.

### V.2 Proposition formation

The usual propositional rules apply. Quantifiers extend the context. Equality requires both terms to have the same sort. `Supports` requires `Evidence × Claim`; `Rebuts` requires `Evidence × Claim`; and `DerivedFrom` uses addressable entities or another signature-declared endpoint profile.

### V.3 Decidability

**T1 — Decidable formation.** Given finite `Γ`, finite `Σ`, and finite syntax, `wf`, term sorting, and proposition formation are decidable. This theorem does not imply decidable proof search, governance authorization, normalization, or semantic truth.

## VI. Identity, equality, and observation

`persistentId : EntityVersion → Identifier` satisfies:

`persistentId(e@vi)=persistentId(e@vj)` for versions in the same identity lineage.

The converse is prohibited:

`persistentId(e1)=persistentId(e2)` does not imply structural equality, definitional equality, semantic equality, or contextual equivalence.

Definitional equality `=` is the least typed congruence containing:

- beta equality;
- `let` substitution;
- canonical decode/quote equality;
- admitted governed revision equality after the corresponding transition is derived; and
- declared computation equations for signature operations.

Observation contexts are typed one-hole contexts:

`Oτ = { C[-] | Γ ⊢ C[e] : Observation for every Γ ⊢ e:τ }`.

`Observation` is a signature-declared result sort or external observation carrier. `Obs` maps a terminating observable execution to a canonical observation record containing result, explicit blocked status, emitted provenance, and governance-state delta.

Contextual equivalence is:

`e1 ≡ e2 : τ` iff for every admitted `C ∈ Oτ`, either both executions diverge, or both terminate with equal observations, including equal blocked/unblocked class and provenance-equivalent audit output.

Definitional equality MUST imply contextual equivalence. The converse is not assumed.

## VII. Operational semantics and governed progress

Reduction is typed and governance-threaded:

`Γ;ΓG ⊢ ⟨e,ΓG⟩ → ⟨e',ΓG'⟩`.

Core reductions include:

**Beta**

`(λx:τ.e) v → e[v/x]` when the selected evaluation strategy treats `v` as a value.

**Let**

`let x:τ=v in e → e[v/x]`.

**Eval quote**

`eval_l(quote_(l+1)(e)) → e`.

**Governed revision**

If `ΓG ⊢ Revise(e,e') admissible` and both terms have sort `τ`, then:

`⟨revise(e,e'),ΓG⟩ → ⟨e',ΓG'⟩`,

where `ΓG'` records the authorization evidence, operation event, and resulting policy state. A revision is not authorized by its syntax.

If admissibility is not derivable or a veto blocks the transition, evaluation returns the explicit result `blocked(revise(e,e'), reason, ΓG)`. This is not an unexplained stuck state.

`→*` is the reflexive-transitive closure of governed reduction.

**T6 — Preservation.** If `Γ ⊢ e:τ` and `Γ;ΓG ⊢ ⟨e,ΓG⟩→⟨e',ΓG'⟩`, then `Γ ⊢ e':τ`.

**T7 — Governed progress.** If `· ⊢ e:τ`, then exactly one admitted execution classification applies at the current step:

1. `e` is canonical or neutral under the selected open/closed-term policy;
2. a reduction exists;
3. governance explicitly blocks the requested transition; or
4. the term is rejected as outside the executable fragment with a typed diagnostic.

A conforming engine MUST NOT represent a denied governance operation as ordinary success or as an unclassified runtime failure.

## VIII. Proof and evidence judgments

Proof and evidential support remain distinct:

- `Γ ⊢ π:φ` means `π` is a proof object for proposition `φ` in the selected logic;
- `Γ ⊢ d supports p` means evidence `d` supports claim `p` under a declared assessment standard; and
- `Γ ⊢ d rebuts p` means evidence `d` rebuts claim `p` under a declared assessment standard.

A claim is contested when at least one support judgment and one rebuttal judgment are derivable. Contestedness does not select a winner and does not imply inconsistency of the underlying logic.

No scalar confidence belongs to the core judgments. An external measurement extension MAY define `μ : Evidence × Claim × Standard → [0,1]`, but `μ` MUST NOT redefine proof, truth, support, rebuttal, or admissibility.

## IX. Denotational and model semantics

For each sort `τ`, choose domain `Dτ`. An environment `ρ` maps every `x:τ` in `Γ` to an element of `Dτ`.

`⟦Γ ⊢ e:τ⟧ρ ∈ Dτ`.

Semantic equality is:

`e1 ≈ e2` iff for every compatible `ρ`, `⟦e1⟧ρ = ⟦e2⟧ρ`.

**T8 — Definitional soundness.** `e1=e2:τ` implies `e1≈e2`.

Contextual equivalence implies semantic equality only on an explicitly declared observationally adequate fragment. No full-abstraction claim is made without a proof that `Obs` characterizes the selected denotation.

A model is `M=(D,I)` and satisfaction is `M ⊨ φ`. Governance-state models interpret the set of admissible state transitions, not merely Boolean labels attached to objects.

## X. Governance logic

Primitive operations are:

`σG ∈ {amend, ratify, revoke, delegate, veto, suspend, restore}`.

A governance transition has the form:

`ΓG ⊢ q --σG,w--> q' ⊣ ΓG'`

where `w` is the authorization witness containing actor, role, delegated authority path, policy version, quorum evidence when required, timestamp, and provenance event identifier.

Every primitive operation MUST define:

1. source-state preconditions;
2. role and delegation conditions;
3. quorum or unilateral-authority conditions;
4. veto interaction;
5. target-state update;
6. governance-state update;
7. emitted provenance; and
8. inverse or compensating operation when one exists.

`Δ` MUST be a DAG. If imported data contains a delegation cycle, the transition is invalid until a declared cycle-resolution operation produces an acyclic state.

A veto is represented as a state-transforming operation that adds a typed block with scope, authority, target, effective interval, and revocation conditions. `suspend` and `restore` change operational availability without erasing historical ratification or revocation records.

## XI. Provenance calculus

A provenance graph is:

`Π=(N,≺,λ,ι,ω)`

where:

- `N` is a finite set of event identifiers;
- `≺` is strict, irreflexive, transitive, and acyclic;
- `λ:N→ΣP` labels each event;
- `ι:N→Entity*` assigns ordered inputs; and
- `ω:N→Entity*` assigns ordered outputs.

Because `≺` is strict, reflexivity and antisymmetry are not included. A non-strict closure `≼` MAY be defined by `n1≼n2` iff `n1=n2` or `n1≺n2`.

`Π ⊢ e derivedFrom e'` holds when a path of event input/output dependencies connects `e'` to `e`, with every intermediate entity and event recorded.

`Replay(Π)` reconstructs a provenance graph and execution result. It MAY allocate new in-memory objects and reconstruction timestamps outside the represented event data.

**T15 — Provenance preservation.** Replay preserves event correspondence, labels, input/output incidence, and strict precedence up to graph isomorphism.

**T16 — Replay correctness.** Replay produces both:

1. `Π' ≅ Π`; and
2. a semantic execution result equal to the original result under the declared semantic equality.

Literal object identity `Replay(Π)=Π` is rejected unless separately required by a byte-reproduction profile.

## XII. Encoding and reflection

### XII.1 Canonical code

`CanonicalCode_l(c,τ)` is the smallest decidable predicate generated by the canonical serialization of each syntax constructor, using:

- explicit constructor tags;
- explicit sort indices;
- de Bruijn indices or alpha-normalized binder names;
- declared namespace identifiers;
- deterministic sequence order;
- no implementation pointers or ambient mutable references; and
- a declared canonical byte encoding for hashing.

Two alpha-equivalent source terms MUST encode to code-equivalent canonical representations.

### XII.2 Encoding layer RE

`RE = R0 + quote + decode`.

Quotation is total on typed terms. Decode is partial and applies only to canonical code.

**T13 — Decode/quote.** `decode_l(quote_l(e)) =_α e`, proved by structural induction over every term and proposition constructor, including binder cases.

RE MUST be conservative over R0 for propositions containing no `Code`, `quote`, or `decode` constructors.

### XII.3 Reflective layer RR

`RR = RE + eval`.

`eval_l : Code_(l+1)(τ) ⇀ τ`.

The primitive rule is `eval_l(quote_(l+1)(e))→e`. No generic reduction exists for a noncanonical code value unless a signature extension supplies and proves one.

**T14 — Reflection soundness.** For typed `e`, `eval_l(quote_(l+1)(e)) ≡ e`.

Unrestricted RR is not strongly normalizing.

### XII.4 Termination fragment K_SN

`K_SN` contains terms satisfying all of the following:

1. no `eval` occurs syntactically beneath `quote`;
2. every evaluation lowers code level from `l+1` to `l`;
3. every recursive signature operation is accepted only with a structurally decreasing argument certificate; and
4. governance transition evaluation cannot recursively synthesize a same-or-higher-level evaluator without leaving `K_SN`.

The termination measure is the lexicographic pair:

`m(e) = (maximum active Code level, number of reducible constructors)`.

Every `K_SN` reduction MUST strictly decrease `m` under the declared evaluation strategy.

## XIII. Self-hosting

`RS` contains canonical internal representations of syntax, signatures, rules, governance logic, provenance logic, and an interpreter. Merely storing the repository source text does not satisfy self-hosting.

The protocol configuration fixed point is constructed by the selected CPO or lattice method. A conforming RS implementation must establish:

**T20 — Self-hosting adequacy**

`eval(quote(P*)) ≈ P*`

and

`Run_internal(quote(RS),e) ≡ Run_external(RS,e)`

on the declared observational fragment.

The construction requires an explicit fixed-point, recursion, or diagonal argument. Naming or embedding the system inside itself is insufficient.

## XIV. Refinement and execution

The implementation-refinement relation is written `⊑R`, distinct from `⊑C`.

`a ⊑R c` means concrete state `c` realizes abstract state `a` according to a declared abstraction map `α`.

**T17 — Refinement preservation.** If `a→a'` and `a⊑R c`, then there exists `c'` such that `c→*c'` and `a'⊑R c'`.

**T18 — Conservative extension.** Each higher tower layer must provide an erasure translation to the lower layer and prove that lower-language theorems are not newly derivable solely from the extension.

**T19 — Relative consistency.** If the erasure translation is total, derivation-preserving, and maps contradiction to contradiction, consistency of the stronger layer implies consistency of the erased lower fragment. This is conditional, not an absolute consistency proof.

`RX` realizes RS through persistence, storage, distribution, execution, and audit.

RX MUST:

- preserve persistent identifiers across serialization, migration, and reload;
- preserve or correctly reconstruct provenance precedence across distributed replication;
- emit a valid acyclic `Π` for every governed state transition;
- distinguish technical validation from substantive validation and ratification;
- reject hidden global governance checks;
- report blocked transitions as blocked; and
- satisfy T16 for replay within the supported execution profile.

## XV. Metatheory status

The theorem register is authoritative about verification status:

| Theorem | Required result | R2 status |
|---|---|---|
| T1 | Decidable formation | Executable instance checked |
| T2 | Substitution | Constructively represented; executable instance checked |
| T3 | Weakening | Lean construction specified |
| T4 | Exchange | Restricted to nondependent contexts; Lean construction specified |
| T5 | Contraction | Restricted to unrestricted assumptions; Lean construction specified |
| T6 | Preservation | Intrinsic Lean indices plus executable instance checks |
| T7 | Governed progress | Executable instance checked; universal Lean theorem not yet discharged |
| T8 | Definitional soundness | Specified |
| T9 | Local confluence | Specified critical-pair obligation |
| T10 | Global confluence | Restricted to terminating fragment and dependent on T9 |
| T11 | Normalization soundness | Specified for partial normalizer |
| T12 | Canonicality of normal forms | Restricted to observationally complete fragment |
| T13 | Decode/quote | Specified structural-induction obligation |
| T14 | Reflection soundness | Executable canonical round-trip checked |
| T15 | Provenance preservation | Executable graph-isomorphism checked |
| T16 | Replay correctness | Provenance half executable; semantic-result theorem specified |
| T17 | Refinement preservation | Specified simulation obligation |
| T18 | Conservative extension | Specified layerwise erasure obligation |
| T19 | Relative consistency | Specified conditional erasure result |
| T20 | Self-hosting adequacy | Specified fixed-point and interpreter-agreement obligation |

No result marked “specified” is to be described as proved. No executable instance check is a universal theorem.

## XVI. Conformance

An implementation conforms to RRKC R2 only if all of the following hold:

1. every term and proposition constructor is implemented with explicit formation and sorting;
2. binders, free variables, bound variables, alpha-equivalence, and capture-avoiding substitution match Sections III–IV;
3. relations and activities are checked against `arR` and `arO`;
4. revision source and target sorts are equal before governance is evaluated;
5. governance operations transform `ΓG` and emit authorization provenance;
6. quotation is total on typed syntax, while decode and eval remain partial;
7. canonical code is decidable and deterministic;
8. unrestricted reflection is not claimed strongly normalizing;
9. `K_SN` enforces code-level decrease and the syntactic no-eval-under-quote restriction;
10. provenance precedence is strict and acyclic;
11. replay is judged by provenance isomorphism and semantic result equality;
12. persistent identity, definitional equality, semantic equality, and contextual equivalence remain distinct;
13. confidence scalars remain outside core proof, evidence, truth, and governance judgments;
14. technical validation, semantic validation, and ratification remain distinct states; and
15. theorem status is reported exactly as specified, executable-instance-checked, machine-proved, or rejected.

## XVII. Machine artifacts

- Ott source: `formal/rrkc/rrkc_r0.ott`
- Lean intrinsic syntax: `formal/rrkc/RRKC/R0.lean`
- Lean metatheory register: `formal/rrkc/RRKC/Metatheory.lean`
- Executable reference: `formal/rrkc/reference_model.py`
- JSON Schema: `schemas/rrkc-r2.schema.json`
- RDF/OWL vocabulary: `ontology/rrkc.ttl`
- SHACL constraints: `shapes/rrkc.shacl.ttl`
- Valid JSON record: `examples/rrkc-r2.valid.json`
- Valid RDF record: `examples/rrkc-r2.valid.ttl`
- Executable tests: `tests/test_rrkc_r2.py`
- Graph-ingestion manifest: `ingest/manifests/rrkc-r2.json`

## XVIII. Remaining proof boundary

R2 closes the formal-language defects in R1. The remaining boundary is not missing syntax; it is proof completion and self-hosted execution:

1. install Ott and Lean in CI;
2. generate or compare the Lean syntax against the Ott source;
3. replace the explicit T7 axiom with an exhaustive theorem after fixing the canonical-code evaluation strategy;
4. discharge T8–T14 on the declared semantic and terminating fragments;
5. prove the semantic-result half of T16;
6. define the concrete RX abstraction map and prove T17; and
7. construct the RS fixed point and prove T20.

Those items remain visible theorem obligations. They are not silently converted into implementation claims.
