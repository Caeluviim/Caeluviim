# SICRP Deterministic Operational Evaluation and Local Graph Ingestion

**Runtime identifier:** `sicrp-runtime/0.1.0`  
**Status:** Implemented proposal — not a validator or ratifying authority  
**Depends on:** Structural Insolvency and Collective Resolution Plane v0.1.0  
**Execution profile:** Local, deterministic, evidence-bearing, append-only

## 1. Purpose

This runtime turns a SICRP v0.1.0 record into:

1. a Draft 2020-12 JSON Schema result;
2. an RDF/SHACL result;
3. an exact JSON-to-RDF entity and EMGN-bridge alignment result;
4. a deterministic provisional assessment;
5. evidence-bearing obligation results;
6. an atomic local named-graph ingestion; and
7. queryable resolution blockers.

It does not convert machine execution into independent validation. It never
confers ratification, never validates EMGN novelty, and never treats
improvement for an initiating claimant as collective resolution.

## 2. Separated result layers

The runtime keeps four result layers distinct.

| Layer | Question | Runtime result |
| --- | --- | --- |
| Record conformance | Is the record structurally coherent and internally linked? | `record_conforms` |
| Structural-insolvency support | Does the record complete the obligation, deficit, mechanism, flow, exclusion, constituency, and capacity path? | `supported` or `not_supported` |
| Collective-resolution requirements | Do all substantive resolution gates pass? | `requirements_satisfied` or `not_established` |
| Governance | Has an authorized independent process validated or ratified the claim? | Recorded as input; never conferred by the runtime |

`requirements_satisfied` is still provisional. It is not the governance state
`validated` and it is not `ratified`.

The runtime always emits:

```text
assessment_status = provisional
self_ratification_permitted = false
ratification_conferred = false
novelty_validated = false
individual_improvement_sufficient = false
```

## 3. Determinism

Evaluation is deterministic relative to:

- the exact input JSON value;
- SICRP record schema v0.1.0;
- runtime semantics `sicrp-runtime/0.1.0`; and
- the explicit `as_of` value.

If `as_of` is omitted, the runtime uses
`record.provenance.generated_at`. It does not read the system clock.

Canonical JSON uses sorted keys, UTF-8, no insignificant whitespace, and no
NaN values. The runtime records:

- `input_digest`: SHA-256 of the canonical input record;
- `assessment_digest`: SHA-256 of the canonical assessment before its
  identifier and digest are attached; and
- `assessment_id`:
  `urn:caeluviim:assessment:sicrp-runtime:{assessment_digest}`.

Identical inputs and `as_of` values produce byte-equivalent assessment values.

## 4. Evidence-bearing obligations

Each obligation result contains:

- stable obligation identifier;
- validation dimension;
- pass, fail, unknown, or error status;
- machine-readable result code;
- human-readable message;
- the higher-level result it blocks;
- subject references; and
- evidence references.

The implemented obligations are:

| Obligation | Principal success/failure codes | Blocks |
| --- | --- | --- |
| `O-JSON-SCHEMA` | `RECORD_SCHEMA_CONFORMS`, `RECORD_SCHEMA_INVALID` | Record and resolution |
| `O-REFERENCE-INTEGRITY` | `REFERENCE_INTEGRITY_PASSES`, `REFERENCE_INTEGRITY_FAILED` | Record and resolution |
| `O-DEFICIT-ARITHMETIC` | `DEFICIT_ARITHMETIC_PASSES`, `DEFICIT_ARITHMETIC_FAILED` | Record and resolution |
| `O-TEMPORAL-ORDER` | `TEMPORAL_ORDER_PASSES`, `TEMPORAL_ORDER_FAILED` | Record |
| `O-VALIDATOR-INDEPENDENCE` | `VALIDATOR_INDEPENDENCE_PASSES`, `VALIDATOR_INDEPENDENCE_FAILED` | Record and resolution |
| `O-STRUCTURAL-INSOLVENCY` | `STRUCTURAL_INSOLVENCY_SUPPORTED`, `STRUCTURAL_INSOLVENCY_NOT_SUPPORTED` | Structural-insolvency support |
| `O-COLLECTIVE-COVERAGE` | `COVERAGE_COMPLETE`, `COVERAGE_INCOMPLETE` | Resolution |
| `O-RESIDUAL-DISCLOSURE` | `RESIDUAL_DISCLOSURE_PASSES`, `RESIDUAL_DISCLOSURE_FAILED` | Record and resolution |
| `O-RESIDUAL-RESOLUTION` | `NO_ACTIVE_RESIDUAL_INSOLVENCY`, `RESIDUAL_INSOLVENCY_REMAINS` | Resolution |
| `O-VALIDATOR-QUORUM` | `VALIDATOR_QUORUM_MET`, `VALIDATOR_QUORUM_MISSING` | Resolution |
| `O-INTERVENTION-VERIFICATION` | `INTERVENTIONS_VERIFIED`, `INTERVENTION_UNVERIFIED` | Resolution |
| `O-CONDITION-VALIDATION` | `CONDITIONS_VALIDATED`, `CONDITION_UNVALIDATED` | Resolution |
| `O-DECLARED-RESOLUTION-CRITERIA` | `DECLARED_CRITERIA_COMPLETE`, `DECLARED_CRITERIA_INCOMPLETE` | Resolution |
| `O-EMGN-ALIGNMENT` | `EMGN_BRIDGE_PRESERVED`, `EMGN_BRIDGE_INCOMPLETE` | Record |

A disclosed residual may therefore pass disclosure while still failing the
resolution gate. The two facts are not collapsed.

## 5. Actual measurement overrides asserted labels

The runtime does not accept a Boolean criterion as its sole proof.

Examples:

- `coverage_complete = true` is insufficient unless an after-observation
  meets the distributional-coverage threshold and the distributional effect
  includes both initiating and non-initiating scopes;
- `independent_validation_recorded = true` is insufficient unless the required
  number of distinct independent validators supplied supporting assessments;
- a completed intervention is not accepted as verified;
- a disclosed active residual remains a collective-resolution blocker; and
- a correct asserted shortfall is recomputed from required and observed
  quantities in compatible units.

## 6. JSON and RDF validation

The `validate` operation requires both serializations.

The JSON record must conform to:

```text
schemas/sicrp-record.schema.json
```

The RDF record must conform to:

```text
ontology/sicrp.ttl
shapes/sicrp.shacl.ttl
```

The alignment pass then requires:

- every first-class JSON entity identifier to appear as an RDF subject with
  its exact SICRP class;
- the collective-resolution claim identifier to be typed as
  `sicrp:CollectiveResolutionClaim`; and
- the RDF `sicrp:EMGNTrace` to match the JSON discrepancy, residue,
  remediation, transition-regime, reachability, and optional novelty-witness
  references exactly.

SHACL conformance without JSON/RDF identity alignment is not accepted for
ingestion.

## 7. Local graph store

The local store is an RDF Dataset serialized as TriG.

For an ingestion graph `G`, it contains:

| Named graph | Content |
| --- | --- |
| `G` | Validated SICRP RDF record |
| `G#ingestion` | Input digest, assessment digest, record reference, and assessment-graph link |
| `G#assessment/{digest}` | Provisional assessment and obligation-result projection |

The assessment projection conforms to:

```text
ontology/sicrp-runtime.ttl
shapes/sicrp-assessment.shacl.ttl
```

The writer:

1. validates before acquiring the write lock;
2. takes an exclusive `fcntl` lock;
3. rejects a named-graph collision;
4. treats an identical record and assessment as idempotent;
5. writes a temporary file in the store directory;
6. flushes it to disk;
7. atomically replaces the prior TriG file; and
8. flushes the containing directory.

An existing named graph is never silently replaced. A new record revision or
different `as_of` configuration requires a new named-graph URI.

## 8. CLI

Run from the repository root:

```bash
python scripts/sicrp_runtime.py --project-root . validate \
  --record examples/sicrp-record.valid.json \
  --rdf examples/sicrp-record.valid.ttl
```

Produce the deterministic provisional assessment:

```bash
python scripts/sicrp_runtime.py --project-root . evaluate \
  --record examples/sicrp-record.valid.json
```

Ingest the validated pair into a local store:

```bash
python scripts/sicrp_runtime.py --project-root . ingest \
  --record examples/sicrp-record.valid.json \
  --rdf examples/sicrp-record.valid.ttl \
  --store .caeluviim/sicrp.trig \
  --graph urn:caeluviim:graph:sicrp:example-001
```

Inspect the store:

```bash
python scripts/sicrp_runtime.py --project-root . inspect \
  --store .caeluviim/sicrp.trig
```

Query current resolution blockers:

```bash
python scripts/sicrp_runtime.py --project-root . query \
  --store .caeluviim/sicrp.trig \
  --sparql-file queries/sicrp-resolution-blockers.rq
```

Commands write JSON to stdout by default. `--output PATH` writes the same JSON
to a file. Validation and evaluation return exit status `1` for record-level
failure. A conforming record whose collective-resolution requirements remain
unsatisfied returns `0`, because record conformance and resolution are
different judgments.

## 9. Current conforming example result

For the v0.1.0 example:

```text
record_conforms = true
structural_insolvency.verdict = supported
collective_resolution.verdict = not_established
```

The queryable resolution blockers are:

```text
CONDITION_UNVALIDATED
COVERAGE_INCOMPLETE
DECLARED_CRITERIA_INCOMPLETE
INTERVENTION_UNVERIFIED
RESIDUAL_INSOLVENCY_REMAINS
VALIDATOR_QUORUM_MISSING
```

This is the intended result. The example contains meaningful improvement and
population-generalization evidence, but it also discloses incomplete coverage,
an active residual, an unverified intervention, an unvalidated condition, and
only one independent supporting validator.

## 10. EMGN boundary

The runtime preserves the bridge:

```text
observed institutional failure
  -> retained structural error residue
  -> collective remediation
  -> changed allocation regime
  -> new reachable material conditions
```

It reports the referenced discrepancy, residue, remediation, transition
regimes, and reachability snapshots. It does not infer that a new material
condition is outside prior embedded reachability. That remains an EMGN novelty
witness and governance obligation.

## 11. Machine artifacts

- Assessment schema: `schemas/sicrp-assessment.schema.json`
- Provisional assessment example:
  `examples/sicrp-assessment.provisional.json`
- Runtime governance/status record:
  `governance/sicrp-runtime-v0.1.0.status.json`
- Runtime vocabulary: `ontology/sicrp-runtime.ttl`
- Assessment SHACL: `shapes/sicrp-assessment.shacl.ttl`
- Evaluator: `src/sicrp_runtime/evaluator.py`
- Atomic graph store: `src/sicrp_runtime/store.py`
- CLI: `src/sicrp_runtime/cli.py`
- Executable wrapper: `scripts/sicrp_runtime.py`
- Blocker query: `queries/sicrp-resolution-blockers.rq`
- Tests: `tests/test_sicrp_runtime.py`
- CI workflow: `.github/workflows/validate-sicrp-runtime.yml`
