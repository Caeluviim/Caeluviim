# Source-Bound Evidence Intake Pipeline

**Module:** Evidence Intake v0.1.0

**Status:** Implemented as a proposal; not ratified

**Position:** Strictly upstream of SICRP record generation

**Depends on:** SICRP v0.1.0 and the SICRP deterministic runtime v0.1.0

## 1. Purpose and boundary

This module controls whether factual material is admissible for use in a
Structural Insolvency and Collective Resolution Plane record. It does not
decide whether structural insolvency exists, whether collective resolution has
occurred, whether an EMGN novelty witness is valid, or whether any module is
ratified.

The pipeline is:

```text
raw source
  -> source capture
  -> claim extraction
  -> support mapping
  -> quarantine decision
  -> eligible SICRP assertion
```

Its governing invariant is:

```text
No claim enters a SICRP record unless every material assertion has
source-bound support.
```

JSON Schema or SHACL conformance is necessary but not sufficient for release:

```text
manifest conforms != claim released
authority assessed != claim supported
claim released != SICRP claim validated
```

## 2. Formal core

The normative topology is:

```text
SourceArtifact
  -> SourceSnapshot
  -> SourceLocator
  -> ExtractedClaim
  -> ClaimSpan
  -> SupportRelation or ContradictionRelation
  -> EvidenceBundle
  -> QuarantineRecord or ReleaseDecision
  -> EligibleSICRPAssertion
```

The required first-class entities are:

- `SourceArtifact`
- `SourceSnapshot`
- `SourceLocator`
- `ExtractedClaim`
- `ClaimSpan`
- `SupportRelation`
- `ContradictionRelation`
- `SourceAuthorityAssessment`
- `EvidenceBundle`
- `UnsupportedClaim`
- `QuarantineRecord`
- `ReleaseDecision`
- `IntakeManifest`

`MaterialClaimSegment` makes the support scope of a compound claim explicit.
`SICRPAssertionRequest` records the requested downstream use.
`EligibleSICRPAssertion` is generated only for a released claim.

## 3. Claim states

The vocabulary defines all lifecycle states:

```text
captured
supported
partially_supported
contradicted
unverifiable
quarantined
released
```

The deterministic evaluator distinguishes the support judgment from the final
admissibility judgment:

| Support state | Meaning | Default final state |
|---|---|---|
| `supported` | Every material segment has valid in-scope support | `released` only if every release gate passes |
| `partially_supported` | Some, but not all, material segments are supported | `quarantined` |
| `contradicted` | Material unresolved contradictory evidence exists | `quarantined` |
| `unverifiable` | Snapshot, locator, digest, trace, or reference integrity failed | `quarantined` |

The input's recorded state is not trusted. A mismatch between recorded state
and computed admissibility is itself a blocking fact.

## 4. Immutable source capture

A `SourceSnapshot` binds:

- a repository-relative content path;
- the exact byte length;
- a SHA-256 digest;
- the capture time;
- the source artifact;
- an explicit immutable flag.

The runtime resolves the path beneath the project root, rejects symlinks,
reads the actual bytes, and verifies length and digest. A locator is a
snapshot-bound UTF-8 byte range with:

- inclusive start and exclusive end offsets;
- the exact decoded quote;
- a quote SHA-256 digest;
- an explicit set of claims for which that locator may be used.

Changing the source after intake produces `SNAPSHOT_DIGEST_MISMATCH` and
`SNAPSHOT_LENGTH_MISMATCH`. Changing the quoted text or byte range produces
`QUOTE_SNAPSHOT_MISMATCH`, `QUOTE_DIGEST_MISMATCH`, or
`LOCATOR_RANGE_INVALID`.

## 5. Material support coverage

Each `ExtractedClaim` declares every material segment. A valid support
relation must bind:

1. the claim;
2. one exact source locator;
3. one or more exact claim spans;
4. the material segments supported by that locator;
5. a support verdict;
6. direct or inferential support mode;
7. a prose scope boundary.

Complete support is computed as set equality:

```text
covered material segments = declared material segments
```

The evaluator does not trust `declared_complete_support`. It independently
computes coverage and rejects a partially supported compound claim.

For a claim presented as observation, inferential-only support is not direct
observation. It produces `UNSUPPORTED_INFERENCE_AS_OBSERVATION`.

## 6. Contradiction and authority boundaries

Every contradiction recorded within the manifest's stated search scope must
appear in both the evidence bundle and the release decision. An unresolved
material contradiction blocks release.

The runtime can mechanically test disclosure consistency inside the intake
manifest. It cannot discover unknown evidence outside the captured search
scope. Therefore release also requires a recorded contradiction-search method
and a completed-search declaration. A missing or inconsistent declaration
fails closed as `CONTRADICTORY_EVIDENCE_OMITTED`.

A `SourceAuthorityAssessment` addresses authorship, institutional status, and
authority scope. It is explicitly marked `not_a_support_relation`. An
authority assessment with no support relation produces
`AUTHORITY_SUBSTITUTED_FOR_SUPPORT`.

## 7. Release rule

For a claim `c`, release implies all of the following:

```text
Release(c) ->
  immutable source snapshot exists
  and exact source locator exists
  and normalized claim is traceable through exact spans
  and explicit support relations exist
  and every material segment is covered
  and contradictory evidence is disclosed
  and all content digests verify
  and support remains within its declared scope
  and release authority is recorded
  and the release decision is approved
  and no active quarantine remains
```

The implementation is fail-closed:

```text
not CompleteSupport(c) -> Quarantined(c)
```

A release decision cannot override a failed mechanical gate. Conversely, the
deterministic evaluator checks the existence and consistency of release
authority but does not confer independent validation or ratification.

## 8. Explicit rejected failure modes

| Failure mode | Operational fact |
|---|---|
| Citation exists but does not support the claim | `CITATION_DOES_NOT_SUPPORT_CLAIM` |
| Source supports only part of a compound claim | `PARTIAL_COMPOUND_SUPPORT` |
| Locator is missing or unstable | `LOCATOR_MISSING`, `LOCATOR_UNSTABLE` |
| Source content changed after intake | `SNAPSHOT_DIGEST_MISMATCH` |
| Quoted text differs from captured snapshot | `QUOTE_SNAPSHOT_MISMATCH` |
| Unsupported inference is presented as observation | `UNSUPPORTED_INFERENCE_AS_OBSERVATION` |
| Authority assessment substitutes for support | `AUTHORITY_SUBSTITUTED_FOR_SUPPORT` |
| Generated text is treated as an external source | `GENERATED_TEXT_AS_EXTERNAL_SOURCE` |
| Contradictory evidence is omitted | `CONTRADICTORY_EVIDENCE_OMITTED` |
| Evidence is reused beyond stated support scope | `SUPPORT_SCOPE_EXCEEDED` |

Additional release facts include `RELEASE_AUTHORITY_MISSING`,
`RELEASE_DECISION_DENIED`, `UNRESOLVED_CONTRADICTION`,
`CONTENT_DIGEST_ATTESTATION_MISSING`, and `ACTIVE_QUARANTINE`.

Every failure is stored as a claim-bound, queryable `FailureFact`, not only as
prose in a log.

## 9. Graph separation

An ingestion creates five named graphs from a caller-supplied base URI:

| Suffix | Contents |
|---|---|
| `/intake` | Complete validated RDF intake manifest |
| `/quarantine` | Quarantined claim projections only |
| `/asserted` | Released claim projections and eligible SICRP assertions only |
| `/assessment/{digest}` | Deterministic assessment and failure facts |
| `/metadata` | Graph-set identities and input/assessment digests |

Before atomic commit, the store proves both:

```text
triples(G_quarantine) intersect triples(G_asserted) = empty
```

and:

```text
claimSubjects(G_quarantine) intersect claimSubjects(G_asserted) = empty
```

If either check fails, ingestion aborts. The `/asserted` graph is an
evidence-intake release graph, not a completed SICRP record graph.

## 10. Downstream interface

The only supported downstream interface is:

```text
intake result
  -> released payload
  -> SICRP record generator
  -> SICRP evaluator
  -> graph ingestion
```

The `release` command emits only:

- released claims;
- their material segments;
- evidence-bundle references;
- eligible SICRP assertion requests.

It includes no quarantined claim identifier, claim text, or assertion request.
The SICRP generator must consume this payload rather than the full intake
manifest.

## 11. Determinism and governance

Canonical JSON uses UTF-8, sorted keys, compact separators, and rejects
non-finite numbers. The assessment identifier is derived from the assessment
digest, and eligible assertion identifiers are derived from their complete
payload.

The evaluator always records:

```text
independent_validation_conferred = false
sicrp_validation_conferred = false
ratification_conferred = false
```

The module governance record remains `proposed`, requires two independent
validators, forbids self-ratification, and binds every implementation artifact
by SHA-256.

## 12. Local operation

Validate JSON, RDF/SHACL, JSON/RDF alignment, snapshots, and deterministic
assessment:

```bash
python scripts/evidence_intake.py --project-root . validate \
  --manifest examples/evidence-intake-manifest.valid.json \
  --rdf examples/evidence-intake-manifest.valid.ttl
```

Evaluate admissibility:

```bash
python scripts/evidence_intake.py --project-root . evaluate \
  --manifest examples/evidence-intake-manifest.valid.json
```

Emit released claims only:

```bash
python scripts/evidence_intake.py --project-root . release \
  --manifest examples/evidence-intake-manifest.valid.json
```

Atomically ingest separated named graphs:

```bash
python scripts/evidence_intake.py --project-root . ingest \
  --manifest examples/evidence-intake-manifest.valid.json \
  --rdf examples/evidence-intake-manifest.valid.ttl \
  --store .caeluviim/evidence-intake.trig \
  --graph-base urn:caeluviim:graph:evidence-intake:example
```

Query quarantine facts:

```bash
python scripts/evidence_intake.py --project-root . query \
  --store .caeluviim/evidence-intake.trig \
  --sparql-file queries/evidence-intake-quarantine.rq
```

Query released assertion candidates:

```bash
python scripts/evidence_intake.py --project-root . query \
  --store .caeluviim/evidence-intake.trig \
  --sparql-file queries/evidence-intake-released-assertions.rq
```

## 13. Current example

The checked example produces:

```text
pipeline_result = released_with_quarantine
released_claim_count = 1
quarantined_claim_count = 1
eligible_sicrp_assertion_count = 1
graphs_disjoint = true
```

The rule-replacement observation is completely source-bound and released.
The compound coverage claim is only partially supported and is directly
contradicted by the captured audit statement. It remains queryable in
quarantine and is absent from the released payload and asserted graph.

## 14. Machine artifacts

- Manifest schema: `schemas/evidence-intake-manifest.schema.json`
- Assessment schema: `schemas/evidence-intake-assessment.schema.json`
- Governance schema: `schemas/evidence-intake-status.schema.json`
- Ontology: `ontology/evidence-intake.ttl`
- Intake SHACL: `shapes/evidence-intake.shacl.ttl`
- Assessment SHACL: `shapes/evidence-intake-assessment.shacl.ttl`
- JSON example: `examples/evidence-intake-manifest.valid.json`
- RDF example: `examples/evidence-intake-manifest.valid.ttl`
- Immutable source fixture: `examples/evidence-intake/source/`
- Deterministic assessment: `examples/evidence-intake-assessment.json`
- Evaluator and store: `src/evidence_intake/`
- CLI: `scripts/evidence_intake.py`
- Checked queries: `queries/evidence-intake-*.rq`
- Tests: `tests/test_evidence_intake.py`
- CI: `.github/workflows/validate-evidence-intake.yml`
