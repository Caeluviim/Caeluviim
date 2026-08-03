# RRKC formalization

This directory is the formalization boundary for RRKC R2.

## Authority order

1. `rrkc_r0.ott` is the grammar and rule source of truth.
2. `RRKC/R0.lean` is the intrinsic Lean representation of the executable R0 surface.
3. `RRKC/Metatheory.lean` contains the machine-checked T2–T7 declarations.
4. `../../docs/architecture/rrkc-r2-verification-register.md` is the live theorem-status register.
5. `reference_model.py` is the executable reference used by repository tests.
6. `../../docs/architecture/rrkc-r2-formal-specification.md` is the normative explanatory specification and original proposal snapshot.

## Verification status

| Result | Current status | Verification boundary |
|---|---|---|
| T1 decidable formation | Executable instance checked | Python reference type checker and schema validation; no universal Lean theorem is claimed |
| T2 substitution | Machine-proved | Lean 4.30.0 package build and bundled `leanchecker`; proof-placeholder gate passed |
| T3 weakening | Machine-proved | Lean 4.30.0 package build and bundled `leanchecker`; proof-placeholder gate passed |
| T4 exchange | Machine-proved for adjacent independent assumptions | Lean 4.30.0 package build and bundled `leanchecker`; dependent-context exchange remains outside the theorem |
| T5 contraction | Machine-proved for unrestricted assumptions | Lean 4.30.0 package build and bundled `leanchecker`; linear/resource-sensitive contraction remains excluded |
| T6 preservation | Machine-proved for the intrinsic `Step` relation | Source and target share context and sort by construction; Lean 4.30.0 and `leanchecker` accepted the theorem |
| T7 governed progress | Machine-proved for the selected R2 operational surface | Every constructor is classified as canonical/neutral, reducible, or governance-blocked; Lean 4.30.0 and `leanchecker` accepted the exhaustive theorem |

The dedicated workflow rejects `sorry`, `admit`, and top-level `axiom` declarations in the RRKC Lean sources before building. T8–T20 remain specified obligations unless their individual records state otherwise.
