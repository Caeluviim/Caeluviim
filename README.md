# Caeluviim

Caeluviim is a provenance-tracked formal architecture for representing claims, agents, relations, evidence, governance, revision, and the construction of new reachable futures.

## Implemented formal modules

| Module | Status | Primary specification | Machine constraints |
|---|---|---|---|
| Error-Mediated Generative Non-Closure | Proposed v0.1.0 | [`docs/architecture/error-mediated-generative-nonclosure.md`](docs/architecture/error-mediated-generative-nonclosure.md) | JSON Schema, OWL/RDF vocabulary, SHACL shapes, executable tests |
| Structural Insolvency and Collective Resolution Plane | Proposed v0.1.0 | [`docs/architecture/structural-insolvency-collective-resolution.md`](docs/architecture/structural-insolvency-collective-resolution.md) | JSON Schema, OWL/RDF vocabulary, SHACL shapes, executable tests, artifact-hash governance record |

## Repository structure

- `docs/architecture/` — normative architecture specifications
- `schemas/` — JSON Schema validation contracts
- `ontology/` — RDF/OWL vocabulary
- `shapes/` — SHACL graph constraints
- `examples/` — conforming instance records
- `governance/` — machine-readable implementation and ratification status
- `tests/` — executable structural validation

## Validation

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
pyshacl -s shapes/emgn.shacl.ttl -e ontology/emgn.ttl examples/emgn-record.valid.ttl
pyshacl -a -i rdfs -s shapes/sicrp.shacl.ttl -e ontology/sicrp.ttl examples/sicrp-record.valid.ttl
```

## Governance state

The current modules are implemented but remain **proposed**, not ratified. Ratification requires two independent validators who are not the proposer, with provenance recorded in each module's governance record.

The SICRP example deliberately stops at `supported`: it records mechanism change and improvement beyond the initiating claimant while disclosing incomplete population coverage. Individual improvement is never accepted as proof of collective resolution.
