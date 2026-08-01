# Source Acquisition and Lifecycle Plane

**Module:** Source Acquisition v0.1.0

**Status:** Implemented as a proposal; not ratified

**Position:** Strictly upstream of Source-Bound Evidence Intake

## 1. Purpose

This module controls whether an exact retrieved representation is recoverable,
immutable, version-aware, and eligible to enter evidence intake. It closes the
provenance gap between a live citation and the bytes actually evaluated.

The executable boundary is:

```text
source discovery
  -> retrieval
  -> content identification
  -> snapshot fixation
  -> version comparison
  -> intake eligibility
```

Acquisition establishes transport and fixation facts only. It does not
establish source authority, evidentiary support, claim truth, SICRP validity,
or ratification.

```text
retrieval succeeded != source authoritative
source fixed != claim supported
retrieval failed != claim false or unsupported
```

## 2. Formal core

The required first-class entities are:

- `SourceRequest`
- `RetrievalAttempt`
- `RetrievedRepresentation`
- `CanonicalSourceIdentity`
- `SourceVersion`
- `SnapshotFixation`
- `AcquisitionFailure`
- `ChangeEvent`
- `SupersessionRelation`
- `SourceAvailabilityObservation`
- `AcquisitionManifest`

`RedirectHop` preserves each transport transition. `AcquisitionAssessment`,
`AcquisitionFailureFact`, `IntakeEligibleSnapshot`, and
`AcquisitionGraphSet` support deterministic execution and querying.

## 3. Content-addressed fixation

A snapshot identifier is derived from the exact retrieved bytes:

```text
SnapshotID(s) = urn:caeluviim:snapshot:sha256:H(exact bytes of s)
```

The evaluator independently reads the repository-relative fixation path,
rejects an escaping path or symlink, computes the byte length and SHA-256
digest, and compares both with:

- the retrieved representation;
- the snapshot fixation;
- the source version;
- the content-addressed snapshot identifier.

The manifest's recorded digest is never trusted as its own proof.

An intake-eligible snapshot must therefore satisfy:

```text
actual digest
  = representation digest
  = fixation digest
  = source-version digest
  = digest component of SnapshotID
```

## 4. URL identity is not content identity

A `SourceRequest.requested_uri` records where retrieval began. A
`CanonicalSourceIdentity` records the stable logical source identity selected
after redirect resolution. A `SourceVersion` records one content-identified
representation of that source.

```text
same requested URL != same source version
same final URL != same source version
```

The example requests the same allocation-register URL twice. Both requests
resolve to the same final URL and canonical identity, but the exact bytes and
digests differ. The two representations therefore receive distinct snapshot
and version identifiers.

Every version identifier includes its SHA-256 digest. A URL-derived version
identifier fails with `VERSION_ID_NOT_CONTENT_BOUND`.

## 5. Retrieval record

Every `RetrievalAttempt` preserves:

- the source request and requested URI;
- start and completion timestamps;
- transport;
- outcome;
- the ordered redirect chain;
- every hop URI, response status, and Location target;
- the final URI for a successful retrieval;
- either one retrieved representation or one acquisition failure.

A `RetrievedRepresentation` additionally preserves:

- retrieval time;
- canonical source identity;
- response status;
- media type;
- response headers;
- content path;
- exact byte length and digest.

Redirect hop sequences must be contiguous from zero. Each redirect Location
must equal the next hop URI, and the final URI must equal the last hop URI.

## 6. Mutable-source lifecycle

Versions are ordered by observation time within each canonical source
identity. When consecutive versions have different byte digests, both a
`ChangeEvent` and `SupersessionRelation` are mandatory:

```text
s(t+1) != s(t)
  -> ChangeEvent(s(t), s(t+1))
  and SupersessionRelation(s(t), s(t+1))
```

The change event binds the canonical identity, both version identifiers, both
digests, detection time, and the digest-comparison method. The supersession
relation records that the earlier version remains immutable but is no longer
the latest captured representation.

Prior snapshots are never silently replaced or rewritten. Missing lifecycle
facts fail closed as:

- `CHANGE_EVENT_MISSING`
- `CHANGE_EVENT_MISMATCH`
- `SUPERSESSION_RELATION_MISSING`

## 7. Retrieval failure boundary

A failed or blocked attempt must have both:

- an `AcquisitionFailure`; and
- a `SourceAvailabilityObservation`.

Both structures are constrained to:

```text
evidentiary_absence_inferred = false
```

The deterministic failure fact `RETRIEVAL_NOT_SUCCESSFUL` means only that the
attempt did not yield fixed bytes. It does not mean the requested source lacks
content, a proposition is false, evidence is absent, or a later attempt will
also fail.

Failed attempts cannot produce a retrieved representation and never appear in
the intake-eligible payload.

## 8. Authority ceiling

Every acquisition manifest has an explicit authority boundary:

```json
{
  "source_authority_assessed": false,
  "claim_support_assessed": false,
  "truth_assessed": false
}
```

JSON Schema fixes all three values to `false`. SHACL imposes the same
constraint on the RDF manifest. The deterministic evaluator records
`authority_boundary_preserved = true` only when the boundary is intact.

Acquisition software may report that bytes were faithfully retrieved and
fixed. It has no power to convert retrieval into an authority judgment,
support relation, truth finding, evidence-intake release, SICRP validation,
or governance decision.

## 9. Intake eligibility

A source version is intake-eligible only when:

1. its successful attempt references a valid source request;
2. its redirect chain and final URI are complete and internally consistent;
3. its retrieved representation has response metadata, media type, timestamp,
   final URI, and canonical identity;
4. the exact file bytes remain available below the project root;
5. byte length and digest verify at every fixation layer;
6. the snapshot identifier is content-addressed;
7. the version identifier is content-bound;
8. any changed predecessor has a matching change event and supersession
   relation;
9. the acquisition authority boundary remains intact.

The evaluator is fail-closed. Any failed version gate also makes its retrieval
attempt ineligible.

The `intake` command exports only eligible snapshot records. Each record
includes the immutable fixation, source version, canonical identity, retrieval
attempt, requested URI, final URI, retrieval time, media type, content path,
byte length, and digest.

## 10. Evidence-intake integration

Every evidence-intake manifest now requires an `acquisition_record` containing:

- the acquisition manifest identifier, repository path, and exact file digest;
- the deterministic acquisition assessment identifier, path, and exact file
  digest.

Every evidence-intake `SourceSnapshot` must also name its
`acquisition_fixation_ref`.

Before evaluating claim support, the evidence-intake runtime independently
verifies:

- both acquisition artifact file digests;
- the manifest and assessment identifier linkage;
- the canonical manifest digest in the assessment;
- the content-addressed assessment identifier;
- the acquisition authority boundary;
- snapshot inclusion in `eligible_snapshot_refs`;
- exact fixation identity, path, length, digest, and immutability.

Thus a live URL, an unverified acquisition manifest, or a snapshot absent from
the eligible acquisition assessment cannot release a claim.

## 11. Named-graph execution

Atomic local ingestion creates six named graphs:

| Suffix | Contents |
|---|---|
| `/acquisition` | Complete validated RDF acquisition manifest |
| `/eligible` | Intake-eligible snapshot projections only |
| `/failures` | Ineligible attempts and deterministic failure facts only |
| `/lifecycle` | Versions, change events, and supersession relations |
| `/assessment/{digest}` | Deterministic assessment identity and result |
| `/metadata` | Graph-set and input/assessment identities |

Before commit, the store proves:

```text
triples(G_eligible) intersect triples(G_failures) = empty
subjects(G_eligible) intersect subjects(G_failures) = empty
```

This separation prevents a failed attempt from becoming intake-eligible by
graph union or projection accident.

## 12. End-to-end architecture

The complete executable path is:

```text
Acquisition
  -> Evidence Intake
  -> SICRP Generation
  -> SICRP Evaluation
  -> Graph Ingestion
```

Each transition is a separate fail-closed boundary:

- acquisition eligibility does not release a claim;
- evidence-intake release does not validate a SICRP claim;
- SICRP conformance does not establish collective resolution;
- deterministic evaluation does not confer independent validation or
  ratification.

## 13. Local operation

Validate JSON Schema, RDF/SHACL, cross-format alignment, exact bytes, version
lifecycle, and the deterministic assessment:

```bash
python scripts/source_acquisition.py --project-root . validate \
  --manifest examples/source-acquisition-manifest.valid.json \
  --rdf examples/source-acquisition-manifest.valid.ttl
```

Evaluate acquisition eligibility:

```bash
python scripts/source_acquisition.py --project-root . evaluate \
  --manifest examples/source-acquisition-manifest.valid.json
```

Emit the intake-eligible acquisition payload:

```bash
python scripts/source_acquisition.py --project-root . intake \
  --manifest examples/source-acquisition-manifest.valid.json
```

Ingest the separated named graphs:

```bash
python scripts/source_acquisition.py --project-root . ingest \
  --manifest examples/source-acquisition-manifest.valid.json \
  --rdf examples/source-acquisition-manifest.valid.ttl \
  --store .caeluviim/source-acquisition.trig \
  --graph-base urn:caeluviim:graph:source-acquisition:example
```

Query changed versions, failures, or intake-eligible snapshots:

```bash
python scripts/source_acquisition.py --project-root . query \
  --store .caeluviim/source-acquisition.trig \
  --sparql-file queries/source-acquisition-changes.rq
```

## 14. Current example

The checked example records:

```text
pipeline_result = eligible_with_failures
intake_eligible_snapshot_count = 3
ineligible_attempt_count = 1
change_event_count = 1
graphs_disjoint = true
```

Two versions share the same requested and final URL but have different exact
bytes and source-version identities. A third eligible acquisition supplies the
snapshot consumed by the evidence-intake example. A blocked restricted-audit
request remains queryable only as an acquisition failure and availability
observation.

## 15. Governance

The implementation status is `implemented`; governance remains `proposed`.
The proposer cannot self-ratify. Ratification requires two independent
validators, and the governance record binds every module artifact by SHA-256.
