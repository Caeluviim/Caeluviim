# Repository Truth Contract

Status: normative repository governance

## Purpose

The repository must not present implementation-shaped text as proof that a capability exists. Every material capability claim must be tied to evidence and assigned an explicit verification state.

## Verification states

1. **SPECIFIED** — prose, schema, interface, or intended behavior exists; execution is not established.
2. **IMPLEMENTED** — executable code exists and is reachable through a documented entry point; successful execution is not established.
3. **TEST_VERIFIED** — automated tests execute the relevant behavior and pass for the identified source commit.
4. **RUNTIME_VERIFIED** — an external/runtime execution produced a receipt tied to the identified source commit.
5. **STALE** — evidence existed for an earlier source state but has not been reproduced for the current source commit.
6. **FAILED** — the latest relevant verification attempt failed.

No lower state may be described using the language of a higher state.

## Runtime receipt minimum

A claim of `RUNTIME_VERIFIED` requires a machine-produced receipt containing at least:

- runtime identifier
- source commit SHA
- manifest identifier or hash
- UTC timestamp
- result
- node count
- relationship count
- validation result
- receipt hash

A repository commit, pull request, workflow definition, fixture, mocked response, generated example, or test-only ingestion is not a runtime receipt.

## Claim/evidence invariant

For each material capability C:

`claim(C) <= strongest_valid_evidence(C)`

where the ordering is:

`SPECIFIED < IMPLEMENTED < TEST_VERIFIED < RUNTIME_VERIFIED`.

`STALE` and `FAILED` block affirmative current-state claims.

## Required capability ledger

Material subsystems must be represented in a machine-readable ledger containing:

- capability id
- human description
- verification state
- source commit
- implementation paths
- test paths
- runtime receipt path(s), if any
- last verification timestamp
- known failure or limitation

The ledger is an index of evidence, not evidence itself.

## README and status surfaces

README files, status commands, dashboards, generated reports, agent instructions, and conversational summaries must derive capability wording from the ledger/evidence state. They must not infer operational status merely from file presence.

Permitted wording examples:

- SPECIFIED: `Graph ingestion protocol is specified.`
- IMPLEMENTED: `Graph ingestion code is implemented; execution is unverified.`
- TEST_VERIFIED: `Graph ingestion passes repository tests for <sha>; live runtime is unverified.`
- RUNTIME_VERIFIED: `Graph ingestion is runtime-verified for <sha> by receipt <hash>.`

## Anti-bullshit gates

A verification job should fail when any of the following is true:

- a `RUNTIME_VERIFIED` ledger entry lacks a valid receipt;
- a receipt source commit differs from the claimed source commit without an explicit compatibility proof;
- a `TEST_VERIFIED` entry has no passing test evidence;
- a material README/status claim exceeds its ledger state;
- generated evidence is committed without provenance identifying the generator and source commit;
- examples or fixtures are located where they can be mistaken for runtime evidence.

## Main-branch write behavior

Automated restoration after direct pushes is evidence that direct-write policy is being enforced, not evidence that the rejected change became part of `main`. Repository-changing agents should use branches and pull requests unless an explicitly documented exception applies.

## Immediate repository consequence

Until a capability ledger and validating gate exist, repository-wide claims such as “integrated,” “operational,” “live,” “complete,” or “runtime verified” must be treated as unproven unless their specific supporting evidence is independently inspected.
