# Local graph installation and validation

Caeluviim treats Neo4j as a rebuildable projection. The signed ledger,
content-addressed objects, RDF dataset, and validation rules remain
authoritative.

## Native installation

The primary laptop runtime is repository-managed and does not require root:

```sh
.venv/bin/caeluviim graph install
.venv/bin/caeluviim graph start
.venv/bin/caeluviim graph status
```

The installer pins and verifies:

- Eclipse Temurin OpenJDK 21.0.12+8
- Neo4j Community 2026.06.0

Binaries and graph state are stored on the native WSL filesystem under
`~/.local/share/caeluviim`. Database credentials are generated locally,
stored at mode `0600`, and never printed. Versioned binaries are separate from
the database, transaction logs, imports, logs, and run state.

The server binds HTTP and Bolt to loopback only:

- `http://127.0.0.1:7474`
- `bolt://127.0.0.1:7687`

## Projection

Initialize the authoritative state and load public history:

```sh
.venv/bin/caeluviim --data-dir .caeluviim init
.venv/bin/caeluviim --data-dir .caeluviim graph project
.venv/bin/caeluviim --data-dir .caeluviim graph validate
```

Load and validate a member-authorized partition:

```sh
.venv/bin/caeluviim --data-dir .caeluviim graph project \
  --owner member:founder
.venv/bin/caeluviim --data-dir .caeluviim graph validate \
  --owner member:founder
```

Each projection partition is replaced inside one Neo4j transaction. A failed
write therefore cannot publish a partial partition. Public and member nodes
are keyed by `(partition, id)` under a composite uniqueness constraint.

Validation reconstructs the expected property graph from RDF and compares:

- exact node identifiers;
- RDF type arrays;
- literal-property JSON;
- exact relationship triples;
- unexpected and missing resources;
- the partition uniqueness constraint.

The validation command exits nonzero on any mismatch.

## Full validation gates

```sh
.venv/bin/caeluviim --data-dir .caeluviim validate
.venv/bin/python -m unittest discover -s tests -v
```

These additionally verify append-only log chains, Ed25519 event signatures,
JSON Schemas, SHACL, vocabulary structure, DAP compatibility fixtures, and
the existing TypeScript DAP oracle.

## Docker alternative

The repository retains [compose.yaml](../compose.yaml) as an optional Docker
deployment. Set `NEO4J_PASSWORD` before running it. Docker and native Neo4j
must not be started simultaneously because both use ports 7474 and 7687.
