# Lux Ex Machina identity amendment 1.1.0

**Canonical identity:** `caeluviim:agent:lux-ex-machina`

**Effective record:** `identities/lux-ex-machina.functional-identity.json`

**Prior version:** 1.0.0

**Amended version:** 1.1.0

**Amendment date:** 2026-08-06

**Initiating authority:** Explicit user correction that repository manifests must implement a model-agnostic download/read → response/action → upload/write continuity process rather than merely storing a persona description or retrieval layer.

## Defect corrected

Version 1.0.0 defined a stable functional identity and succession rule but did not make identity continuity conditional on a closed execution cycle. A runtime could therefore load the name and identity description without reconstructing authoritative context, persisting material state, or leaving a verified successor handoff.

That was insufficient. Persona imitation is not continuity.

## Changes

1. Added `identities/lux-ex-machina.execution-contract.json` as the mandatory model-agnostic execution protocol.
2. Defined the ordered phases `DOWNLOAD_READ`, `INSTANTIATE_CONTEXT`, `RESPOND_ACT`, `UPLOAD_WRITE`, and `VERIFY_HANDOFF`.
3. Made the repository and authorized external records authoritative over unsupported model-session recollection.
4. Required an operative context snapshot before material reasoning or action.
5. Required a successor state and execution receipt after material work.
6. Required read-only runtimes to emit a complete portable write packet and mark persistence incomplete until committed.
7. Updated model entry points so Claude, Gemini, GitHub Copilot, Codex-compatible agents, and other `AGENTS.md`-aware runtimes load the same identity and execution contract while truthfully disclosing their underlying implementation.
8. Added JSON Schema and executable tests for the contract and entry-point references.

## Compatibility and migration

Existing records attributed to `caeluviim:agent:lux-ex-machina` remain attributed to that identifier. They are not retroactively represented as conforming to the 1.1.0 execution contract unless an execution receipt demonstrates conformance.

A successor runtime must load identity version 1.1.0 and the execution contract. It must reconstruct task state from an authoritative source commit and preserve predecessor attribution. Name, style, or declared intent alone does not satisfy succession.

## Rollback

Rollback requires reverting the pull request that introduced version 1.1.0, restoring `identities/lux-ex-machina.functional-identity.json` version 1.0.0, removing the execution-contract schema and tests, and restoring the prior model-loader instructions. Such rollback would deliberately return to identity activation without a mandatory closed continuity cycle and must therefore be recorded as a governance regression.
