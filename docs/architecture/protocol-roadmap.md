# Caeluviim Protocol Roadmap

Last updated: 2026-08-01

| Component | Maturity | Current evidence | Blocking items | Next executable action |
|---|---|---|---|---|
| EMGN | Proposed | Specification, Schema, OWL, SHACL, tests | Two independent validators | Record signed validations against exact module hash |
| Core ontology | Emerging | RDF vocabulary and graph ingestion model | Stable core identity and authority vocabulary | Align ontology terms to identity-authority schemas |
| Graph runtime | Operational local | Transactional content-addressed ingestion and lifecycle CI | Hosted reproducibility evidence | Require green hosted graph lifecycle check on merge candidates |
| Identity model | Proposed | Identity and authority specification and Schema | RDF/SHACL mapping and validator review | Add conforming and adversarial fixtures |
| Authority engine | Proposed | Capability, delegation, revocation, and ceiling model | Runtime resolver and event projection | Implement deterministic authorization resolver |
| Governance runtime | Proposed | Executable state-machine specification | Runtime records, decision function, integration tests | Implement proposal and validation event types |
| Trust engine | Proposed | Contextual multidimensional trust specification and Schema | Policy weights, decay rules, computation runtime | Implement transparent computation receipt |
| Protocol invariants | Proposed | Normative invariant registry | Machine invariant evaluator | Add pre-ingest, ledger, projection, and reconstruction checks |
| Reality Audit Board | Planned | Governance independence requirements | Governance runtime and validator registry | Define board composition and case lifecycle |
| Veto engine | Planned | Authority-ceiling concepts | Executable governance and conflict semantics | Specify veto attachment without claim mutation |
| Simulation | Planned | Milestone definition | Stable authority, trust, and governance state transitions | Build reference simulation model |
| Human pilot | Planned | Metrics inventory | Ratified protocol subset and operational safeguards | Select bounded pilot and evidence plan |
| Production corpus | Ready with gate | Issue #8 entry criteria and manifests | Hosted CI, authority boundary, review | Activate only after merge-gate evidence |
| Supply chain | Partial | Version-ranged dependencies and versioned container tag | Lockfile, SBOM, action SHA pinning | Add reproducible dependency and release artifacts |
| Branch enforcement | Reactive | Main Write Guard | Native branch protection or ruleset | Require PRs, hosted checks, and review at GitHub boundary |

## Maturity definitions

- `Planned`: objective exists without normative machine artifacts.
- `Proposed`: normative and machine artifacts exist but are not ratified.
- `Operational local`: executable under the declared localhost boundary.
- `Ratified`: governance requirements are satisfied for an exact content hash.
- `Production`: ratified, deployed, monitored, recoverable, and supported by reproducible evidence.

## Merge discipline

A roadmap state changes only when the referenced evidence exists on the exact repository tree. Local success, narrative declaration, or issue checklists alone do not advance maturity.