# RRKC formalization

This directory is the formalization boundary for RRKC R2.

## Authority order

1. `rrkc_r0.ott` is the grammar and rule source of truth.
2. `RRKC/R0.lean` is the intrinsic Lean target for generated syntax and reduction.
3. `RRKC/Metatheory.lean` records T2–T7 and their exact verification status.
4. `reference_model.py` is the executable reference used by repository tests.
5. `../../docs/architecture/rrkc-r2-formal-specification.md` is the normative explanatory specification.

## Verification status

| Result | Current status | Boundary |
|---|---|---|
| T1 decidable formation | Executable instance checked | Python reference type checker and schema validation |
| T2 substitution | Constructively represented; executable instance checked | Lean universal theorem awaits toolchain execution |
| T3 weakening | Lean construction specified | Awaiting Lean CI |
| T4 exchange | Lean construction specified for nondependent contexts | Awaiting Lean CI |
| T5 contraction | Lean construction specified for unrestricted assumptions | Awaiting Lean CI |
| T6 preservation | Enforced by intrinsic `Step` indices; executable instance checked | Awaiting Lean CI |
| T7 governed progress | Executable instance checked; universal theorem openly axiomatized | Must replace the axiom after canonical-code/evaluation strategy is frozen |

No theorem is marked machine-proved merely because a Python test passes or a Lean statement exists. The graph record preserves the same distinction.
