# Repository Truth Ledger

**Status:** descriptive audit control, not ratification
**Date:** 2026-08-07

This file exists to prevent repository presence from being confused with operational reality.

## What `main` currently proves

A commit on `main` proves only that GitHub accepted repository content at that commit. It does **not**, by itself, prove that a service is deployed, a graph is live, an ingestion occurred, a test actually ran, a legal theory is correct, or a governance proposition is ratified.

## Current repository facts observed on 2026-08-07

- `main` currently contains merged formal, identity, legal, and operations material.
- The recent history contains automated `main-write-guard` restoration commits after direct pushes. Therefore direct-push attempts must not be treated as durable changes merely because a transient commit existed.
- Multiple overlapping open pull requests exist, including competing governance/repair proposals and older branches whose bases predate substantial changes to `main`.
- The README describes repository memory and a Neo4j runtime as operational implementation substrates. Those descriptions are repository claims. They are not runtime evidence.

## Evidence classes

| Class | What qualifies | What may be claimed |
|---|---|---|
| Repository evidence | commit, tree, file, PR, review, workflow metadata | the artifact exists in GitHub |
| Test evidence | recorded workflow/job result or an execution trace tied to an exact commit | the specified test ran with the recorded result |
| Runtime evidence | runtime-generated receipt containing runtime identifier, source commit, manifest, timestamp, result, node count, relationship count, validation result, and receipt hash | the identified runtime performed the identified ingestion |
| Governance evidence | required approvals/ratification record under the applicable rule | the proposition reached the recorded governance state |

Absence of the stronger evidence class forbids promotion of a weaker class into the stronger claim.

## Immediate cleanup rule

Until the repository is consolidated:

1. Treat open PRs as proposals only.
2. Do not infer live graph state from manifests, schemas, README text, commits, or test fixtures.
3. Do not infer successful execution from prose saying that validation occurred; require the execution evidence itself.
4. Prefer one canonical implementation path over overlapping repair documents.
5. Before merging an old PR, compare it against current `main`; close or supersede it when its purpose has already been absorbed or contradicted.
6. Any future runtime claim must identify its receipt. If there is no receipt, say `NOT RUNTIME VERIFIED`.

## Consolidation target

The repository should converge toward four clearly separated planes:

- **spec/** — normative/formal definitions;
- **runtime/** — executable implementation;
- **evidence/** — machine-generated test/runtime receipts;
- **records/** — proposals, decisions, historical material.

Documentation may explain these planes but must not manufacture evidence for them.

## Acceptance criterion

The repository stops being self-referential documentation when a clean checkout can execute a bounded end-to-end path that produces a machine-generated receipt whose source commit is the checkout commit and whose claimed counts can be independently recomputed. Until then, implementation artifacts may be useful, but live-system claims remain unverified.
