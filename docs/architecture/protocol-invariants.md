# Protocol Invariants

Status: Proposed v0.1.0

These invariants are implementation-independent protocol guarantees. Implementations MUST fail closed when an effective-state mutation would violate them.

## Identity and authority

- Every effective action has exactly one acting identity and at least one verifiable signing key.
- Every effective capability grant has provenance and an authority basis.
- Delegated authority is a subset of parent authority.
- Revoked or expired authority cannot authorize later actions.
- A proposer cannot validate the same proposal.
- Multiple keys or manifestations controlled by one identity count once for independence and quorum.

## Provenance

- Every claim, evidence item, assessment, governance action, trust observation, and graph assertion has provenance.
- Every provenance record resolves to a source or generating event and an identity.
- No accepted evidence reference is orphaned.
- Exact source text and transformed representations remain distinguishable.

## Content integrity

- Canonically equivalent records produce identical content hashes.
- A stable identifier cannot resolve to conflicting content hashes without an explicit supersession or conflict record.
- Append-only events are never mutated in place.
- Every effective state root is reproducible from accepted events and declared algorithms.

## Governance

- Acceptance and execution are distinct events.
- Every decision cites the exact proposal hash and policy version evaluated.
- Required validator independence is checked at decision time.
- Contested material remains visible and cannot be silently normalized into consensus.
- Protected-path changes require the acknowledgments and rollback plan declared by repository policy.

## Trust

- Trust does not create authority.
- Every computed trust value exposes its evidence, weights, confidence, scope, and algorithm version.
- Missing evidence is unknown, not adverse evidence.
- Duplicate evidence is not counted twice.
- Self-assessment is not independent validation.

## Graph structure

- No effective relation has a missing endpoint.
- Reified relations preserve subject, predicate, object, provenance, and assertion identity.
- Authority delegation cycles are invalid unless an explicit governance policy permits and bounds them.
- Supersession chains are acyclic.
- Quarantined objects cannot participate in effective-state projection.

## Operational verification

A conforming implementation SHOULD expose a command that evaluates all invariants against:

1. an ingestion candidate before commit
2. the committed event ledger
3. the projected graph
4. a reconstructed graph produced from the ledger

The command MUST report invariant identifiers, affected record identifiers, and evidence sufficient to reproduce each result.