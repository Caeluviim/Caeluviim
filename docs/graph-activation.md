# Graph activation and ingestion batches

Caeluviim can ingest a source-and-mapping batch, create signed ledger events, project accepted mappings into RDF, validate the result with SHACL, and optionally replace and validate the corresponding native Neo4j partition.

## Minimal activation

```bash
caeluviim --data-dir .caeluviim ingest batch \
  --input examples/ingestion-batch.v0.1.json
```

The command returns a machine-readable activation receipt containing:

- the accepted activation event identifier and recorded timestamp;
- the content-addressed receipt identifier and object identifier;
- source, mapping, accepted, and quarantined counts;
- projected triple count and SHACL result;
- ledger state root and signature count;
- whether the invocation was an idempotent replay.

Re-running the same manifest does not create a second activation event. The manifest's `started_at`, source content, mappings, reviews, and provenance fields are part of the deterministic operation body.

## Activate and project to the native graph

```bash
caeluviim --data-dir .caeluviim ingest batch \
  --input examples/ingestion-batch.v0.1.json \
  --project-native
```

This form installs or starts the repository-managed loopback-only Neo4j runtime, replaces the relevant graph partition from the authoritative ledger projection, and validates the live node and edge set against the RDF-derived expected projection.

## Mapping boundary

Mappings enter as attributed analysis candidates. A mapping without a review remains quarantined and is not projected as an accepted semantic object. A reviewed mapping is projected only when its decision is `accept`.

For batch ingestion, the declared reviewer must match the signing identity selected by the ledger:

- public batches: `member:founder`;
- non-public batches: the batch `owner_id`.

This closes reviewer-label substitution within the batch pathway. The broader prototype still uses service-mediated local member-key custody and must not be described as independently controlled member identity.

## Scope and confidentiality

All sources in one batch share the batch scope. Non-public batches require `owner_id`; their source content, receipt, and projection remain in the member partition plus public context. Public and private material should not be mixed into one activation batch.

## Operational timestamp boundary

`activation_started_at` is the ledger-recorded time of the accepted `INGESTION_BATCH_ACTIVATE` event. It is evidence that Caeluviim graph-ingestion operations began for that declared batch.

It does not, by itself, establish an external payment obligation, settlement date, damages-accrual date, statutory deadline, or other legal or financial consequence. Any such consequence requires its own authority, agreement, or adjudicative basis and should be represented as a separate sourced claim.

## Production sequence

1. Prepare a manifest from source material without silently transforming the source text.
2. Keep uncertain mappings unreviewed or contested.
3. Run the batch command and preserve the returned receipt.
4. Require SHACL conformance before projection is treated as operational.
5. Run native projection validation when Neo4j is used.
6. Record subsequent corrections as new batches or superseding review events rather than overwriting history.
