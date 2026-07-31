# Example artifact boundary

Files in this directory are deterministic machine-validation fixtures unless a file explicitly states otherwise.

A fixture may contain identifiers, timestamps, hashes, validator references, claim states, governance states, source references, or reachability witnesses needed to exercise JSON Schema, RDF/OWL, SHACL, runtime, ingestion, query, and governance constraints. Those values demonstrate the shape and behavior of a conforming record only.

They do **not** establish that:

- the represented event occurred;
- the represented source is authoritative;
- the represented claim is empirically supported or true;
- the named validator exists or performed a review;
- the recorded hash anchors an independently witnessed artifact;
- a module or instance has actually been validated or ratified;
- a synthetic novelty witness establishes real-world new reachability.

Placeholder or synthetic values must never be promoted into production governance evidence. Actual validation and ratification require independently attributable assessments, verified provenance, content-addressed artifacts, and the quorum and proposer-independence rules declared by the relevant module.

Repository documentation and user interfaces should label these files as examples or fixtures whenever they are displayed outside a test context.
