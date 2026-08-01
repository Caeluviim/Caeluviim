# Caeluviim

Caeluviim is a provenance-tracked formal architecture for representing claims, agents, relations, evidence, governance, revision, and the construction of new reachable futures.

## Implemented formal modules

| Module | Status | Primary specification | Machine constraints |
|---|---|---|---|
| Error-Mediated Generative Non-Closure | Proposed v0.1.0 | [`docs/architecture/error-mediated-generative-nonclosure.md`](docs/architecture/error-mediated-generative-nonclosure.md) | JSON Schema, OWL/RDF vocabulary, SHACL shapes, executable tests |
| Structural Insolvency and Collective Resolution Plane | Proposed v0.1.0 | [`docs/architecture/structural-insolvency-collective-resolution.md`](docs/architecture/structural-insolvency-collective-resolution.md) | JSON Schema, OWL/RDF vocabulary, SHACL shapes, executable tests, artifact-hash governance record |
| SICRP deterministic operational runtime | Proposed v0.1.0 | [`docs/architecture/sicrp-operational-evaluation.md`](docs/architecture/sicrp-operational-evaluation.md) | Evidence-bearing evaluator, JSON/RDF alignment, atomic local TriG ingestion, blocker queries |
| Source-bound evidence intake | Proposed v0.1.0 | [`docs/architecture/source-bound-evidence-intake.md`](docs/architecture/source-bound-evidence-intake.md) | Immutable snapshots, exact locators, material support coverage, fail-closed quarantine, released-only SICRP assertions |
| Source acquisition and lifecycle | Proposed v0.1.0 | [`docs/architecture/source-acquisition-lifecycle.md`](docs/architecture/source-acquisition-lifecycle.md) | Redirect-preserving retrieval, content-addressed fixation, mutable-source versioning, intake-eligible export |

## Repository structure

- `docs/architecture/` — normative architecture specifications
- `schemas/` — JSON Schema validation contracts
- `ontology/` — RDF/OWL vocabulary
- `shapes/` — SHACL graph constraints
- `examples/` — conforming instance records
- `governance/` — machine-readable implementation and ratification status
- `src/sicrp_runtime/` — deterministic evaluation and local graph store
- `src/evidence_intake/` — source admissibility evaluation and separated graph store
- `src/source_acquisition/` — retrieval/fixation evaluation and source lifecycle store
- `scripts/` — directly executable local runtime
- `queries/` — checked SPARQL operational queries
- `tests/` — executable structural validation

## Validation

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
pyshacl -s shapes/emgn.shacl.ttl -e ontology/emgn.ttl examples/emgn-record.valid.ttl
pyshacl -a -i rdfs -s shapes/sicrp.shacl.ttl -e ontology/sicrp.ttl examples/sicrp-record.valid.ttl
python scripts/sicrp_runtime.py --project-root . validate --record examples/sicrp-record.valid.json --rdf examples/sicrp-record.valid.ttl
python scripts/sicrp_runtime.py --project-root . evaluate --record examples/sicrp-record.valid.json
python scripts/evidence_intake.py --project-root . validate --manifest examples/evidence-intake-manifest.valid.json --rdf examples/evidence-intake-manifest.valid.ttl
python scripts/evidence_intake.py --project-root . release --manifest examples/evidence-intake-manifest.valid.json
python scripts/source_acquisition.py --project-root . validate --manifest examples/source-acquisition-manifest.valid.json --rdf examples/source-acquisition-manifest.valid.ttl
python scripts/source_acquisition.py --project-root . intake --manifest examples/source-acquisition-manifest.valid.json
```

## Governance state

The current modules are implemented but remain **proposed**, not ratified. Ratification requires two independent validators who are not the proposer, with provenance recorded in each module's governance record.

The SICRP example deliberately stops at `supported`: it records mechanism change and improvement beyond the initiating claimant while disclosing incomplete population coverage. Individual improvement is never accepted as proof of collective resolution.

The operational runtime reports that record as conforming, provisionally supports the structural-insolvency condition, and returns `collective_resolution.verdict = not_established` with six evidence-bearing blockers. It never confers validation, EMGN novelty, or ratification.

Evidence intake is strictly upstream. It releases only claims whose immutable
source bytes, exact locator, trace spans, complete material support,
contradiction disclosure, digests, support scope, and release authority all
verify. Quarantined claims remain queryable but never enter the released SICRP
assertion payload.

Source acquisition now sits strictly upstream of evidence intake. It preserves
redirect chains, response metadata, retrieval times, canonical identities,
exact bytes, source versions, changes, supersession, and availability
observations. The same URL can produce multiple content-identified versions.
A failed retrieval remains queryable but is never treated as evidentiary
absence. Acquisition does not assess source authority, claim support, or
truth.
