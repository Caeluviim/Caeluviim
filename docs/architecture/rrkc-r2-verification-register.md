# RRKC R2 Verification Register

**Applies to:** `urn:caeluviim:module:rrkc:r2`  
**Register date:** 2026-08-03  
**Module governance status:** Proposed and unratified  
**Formal toolchain:** Lean 4.30.0 / Lake 5.0.0  
**Machine boundary:** `formal/rrkc/RRKC/R0.lean` and `formal/rrkc/RRKC/Metatheory.lean`

## Authority and supersession

This live register supersedes only the verification-status table in Section XV and the obsolete T7-axiom item in Section XVIII of `rrkc-r2-formal-specification.md`. It does not alter the normative syntax, calculus, governance, provenance, reflection, refinement, or conformance requirements of that specification.

A result is marked **machine-proved** here only when all of the following hold:

1. its Lean declaration contains no `sorry`, `admit`, or top-level `axiom` placeholder;
2. the dependency-free RRKC package builds under the pinned Lean toolchain;
3. the build includes the `RRKC.R0`, `RRKC.Metatheory`, and `RRKC` modules rather than completing with zero jobs; and
4. the bundled Lean environment checker accepts the compiled environment.

## Current theorem register

| Theorem | Exact proved or checked scope | Status | Evidence |
|---|---|---|---|
| T1 Decidable formation | Concrete Python reference checker and JSON/RDF structural validation | Executable-instance-checked | `reference_model.type_of`, schema tests, RDF parsing tests |
| T2 Substitution | Intrinsically typed substitution returns a term of the original result sort under a sort-preserving substitution | **Machine-proved** | `RRKC.T2_substitution` |
| T3 Weakening | Renaming embeds a term into a context extended by one unused assumption | **Machine-proved** | `RRKC.T3_weakening` |
| T4 Exchange | Two adjacent independent assumptions may be exchanged | **Machine-proved** | `RRKC.T4_exchange`; no dependent-context exchange claim |
| T5 Contraction | Two adjacent assumptions of the same unrestricted sort may be contracted | **Machine-proved** | `RRKC.T5_contraction`; no linear/resource-sensitive contraction claim |
| T6 Preservation | Every constructor of the intrinsic `Step` relation has source and target in the same context and sort | **Machine-proved** | `RRKC.T6_preservation` |
| T7 Governed progress | Every term constructor in the selected R2 operational surface is classified as canonical/neutral, reducible, or governance-blocked | **Machine-proved** | `RRKC.T7_governed_progress`; revision case splits on `Governance.admits` |
| T8 Definitional soundness | R0 denotational semantics | Specified, unproved | Semantic domains and interpretation proof remain required |
| T9 Local confluence | R0 critical pairs | Specified, unproved | Critical-pair analysis remains required |
| T10 Global confluence | Terminating fragment `K_SN` | Specified, unproved | Depends on T9 and a machine proof of termination |
| T11 Normalization soundness | Partial normalizer on `K_SN` | Specified, unproved | Normalizer and semantic equivalence proof remain required |
| T12 Normal-form canonicality | Observationally complete `K_SN` fragment | Specified, unproved | Observation completeness remains required |
| T13 Decode/quote | Binder-complete encoding layer | Specified, unproved | Canonical-code representation and structural induction remain required |
| T14 Reflection soundness | Canonical quotation/evaluation instances | Executable-instance-checked | Python reference reduction; universal Lean theorem remains required |
| T15 Provenance preservation | Concrete replay graph instances | Executable-instance-checked | Event/order/input/output isomorphism tests |
| T16 Replay correctness | Concrete provenance half only | Executable-instance-checked | Semantic-result equality theorem remains required |
| T17 Refinement preservation | RX forward simulation | Specified, unproved | Concrete abstraction map remains required |
| T18 Conservative extension | Layerwise erasure | Specified, unproved | Erasure definitions and proofs remain required |
| T19 Relative consistency | Verified erasure translation | Specified, unproved | Conditional theorem remains required |
| T20 Self-hosting adequacy | RS fixed point and interpreter agreement | Specified, unproved | Fixed-point construction and internal/external agreement remain required |

## Machine-verification procedure

The workflow `.github/workflows/rrkc-formal.yml` performs:

1. a source scan rejecting proof placeholders;
2. `lake build` in `formal/rrkc` using `leanprover/lean4:v4.30.0`; and
3. bundled `leanchecker` replay of the compiled environment.

The accepted proof revision built five Lake jobs, including `RRKC.R0`, `RRKC.Metatheory`, and the `RRKC` root module. This distinction is material: an earlier package configuration returned a successful zero-job build and was rejected as non-evidence.

An attempted auxiliary nanoda check was not used as proof evidence because its parser failed on the Lean 4.30 export with an `invalid digit found in string` error after the Lean build and bundled checker had succeeded. The repository therefore records only compatible, completed verification procedures.

## Remaining formal sequence

The next proof sequence is:

1. make the Ott source generate or mechanically compare against the intrinsic Lean syntax;
2. define denotational semantics and prove T8;
3. enumerate R0 critical pairs and prove T9;
4. formalize the `K_SN` measure and prove termination, T10, T11, and T12;
5. define canonical code and prove T13–T14;
6. formalize provenance semantics and complete T15–T16 universally;
7. define RX abstraction and prove T17–T19; and
8. construct the RS fixed point and prove T20.

No open item in this sequence is represented as ratified, complete, or machine-proved.
