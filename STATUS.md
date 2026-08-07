# Caeluviim Repository Status

**Status date:** 2026-08-07

This file is the repository's evidence boundary. It exists to prevent documentation, merged code, or test artifacts from being represented as a functioning deployed Caeluviim system without the evidence required to support that claim.

## What is verified

- This GitHub repository exists and is writable through the connected GitHub integration.
- `main` contains merged source, documentation, legal-work-product, and governance artifacts.
- Repository history shows the main-write guard restoring `main` after direct pushes.

## What is NOT verified

As of this status update, repository search produced **no runtime-generated ingestion receipt** matching the project's required verification model. Therefore none of the following is claimed here as operational fact:

- a live Caeluviim graph runtime;
- successful production ingestion;
- a deployed knowledge service;
- current production node or relationship counts;
- runtime semantic validation;
- end-to-end operation outside repository/test evidence.

Merged code is **repository evidence**, not runtime evidence. CI/test output is **test evidence**, not production-runtime evidence.

## Runtime verification contract

A runtime claim becomes verified only when a runtime-generated receipt is preserved with all of these fields:

1. runtime identifier
2. source commit
3. manifest
4. timestamp
5. result
6. node count
7. relationship count
8. validation result
9. receipt hash

Until such a receipt exists, runtime-facing status MUST be described as `UNVERIFIED` or, where appropriate, `TEST-ONLY` / `MERGED-NOT-RUNTIME-VERIFIED`.

## Immediate repository rule

Do not use repository size, commit count, merged PR count, schemas, manifests, migrations, documentation, or test fixtures as substitutes for proof that Caeluviim is running. Claims must identify their evidence class explicitly.

## Current disposition

**Repository:** real.

**Artifacts/code:** present.

**Live integrated Caeluviim runtime:** **UNVERIFIED.**

This status remains authoritative until superseded by stronger evidence, preferably a valid runtime receipt satisfying the contract above.
