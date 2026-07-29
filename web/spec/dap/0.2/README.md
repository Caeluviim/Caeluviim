# Districted Authority Protocol v0.2

Status: working draft

DAP is an operation-sourced governance protocol. Its governing invariant is:

> Authoritative state is the deterministic reduction of valid, accepted
> operations.

This directory contains the normative protocol artifacts for version 0.2:

- [Operation envelope and validation](operation-envelope.md) defines the unit
  of accountable agency, staged validation, dispositions, and reduction.
- [Ruleset language](ruleset-language.md) defines the closed, deterministic
  policy language used to decide authority, thresholds, timing, conflicts,
  transitions, and veto effects.
- [`operation-envelope.schema.json`](schemas/operation-envelope.schema.json)
  validates the wire envelope.
- [`ruleset.schema.json`](schemas/ruleset.schema.json) validates ruleset
  documents and their expression trees.
- [`alpha-12.ruleset.json`](examples/alpha-12.ruleset.json) is a complete
  example district ruleset.
- [`proposal-submit.operation.json`](examples/proposal-submit.operation.json)
  is a content-addressed operation fixture.

Normative terms such as MUST, MUST NOT, SHOULD, and MAY are to be interpreted
as requirement levels. Prose controls semantics; schemas enforce the
machine-checkable structural subset.

## Conformance boundaries

DAP v0.2 separates five facts that implementations MUST NOT collapse:

1. structural validity;
2. cryptographic validity;
3. admissibility under the bound ruleset and pre-state;
4. acceptance into district history;
5. effect in derived state.

An implementation is not conformant merely because it can store an envelope.
It must reproduce identifiers, validation outcomes, accepted-history roots,
and derived-state roots from the same inputs.

## Normative corrections from the initial envelope draft

The v0.2 encoding makes three necessary clarifications:

1. `operation_id`, `content_hash`, and `signature` are all excluded from the
   body preimage. This removes recursive hashing. The first two fields are
   deterministic encodings of the same SHA-256 body digest.
2. `ruleset_id` is an envelope field. Validation cannot be reproduced later if
   the operation does not identify the ruleset under which it requests
   evaluation.
3. Governance time is `district_time`, derived from finalized checkpoints.
   `created_at`, `valid_from`, and `expires_at` are signed claims and bounds;
   local validator clocks never independently change authoritative state.

These corrections preserve the stated protocol model while making it
independently executable.
