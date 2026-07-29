# Caeluviim

Caeluviim is a provenance-tracked formal architecture for representing claims, agents, relations, evidence, governance, revision, and the construction of new reachable futures.

## Implemented formal modules

| Module | Status | Primary specification | Machine constraints |
|---|---|---|---|
| Error-Mediated Generative Non-Closure | Proposed v0.1.0 | [`docs/architecture/error-mediated-generative-nonclosure.md`](docs/architecture/error-mediated-generative-nonclosure.md) | JSON Schema, OWL/RDF vocabulary, SHACL shapes, executable tests |

## Repository structure

- `docs/architecture/` — normative architecture specifications
- `schemas/` — JSON Schema validation contracts
- `ontology/` — RDF/OWL vocabulary
- `shapes/` — SHACL graph constraints
- `examples/` — conforming instance records
- `tests/` — executable structural validation

## Validation

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
pyshacl -s shapes/emgn.shacl.ttl -e ontology/emgn.ttl examples/emgn-record.valid.ttl
```

## Governance state

The current module is implemented but remains **proposed**, not ratified. Ratification requires two independent validators who are not the proposer, with provenance recorded in the module's governance record.
