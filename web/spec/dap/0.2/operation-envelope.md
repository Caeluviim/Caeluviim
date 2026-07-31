# Operation Envelope and Validation Specification v0.2

Status: working draft

## 1. Purpose

The operation envelope is the canonical unit of action in DAP. No client,
administrator, hub, reducer, or storage layer may mutate authoritative district
state directly.

An operation can be structurally valid, cryptographically valid, admissible,
accepted, and effective. These are separate states. Acceptance does not imply
immediate effect: an accepted operation may await quorum, review, delay,
countersignature, dependency, evidence, or veto resolution.

## 2. Lifecycle

```text
Constructed -> Signed -> Submitted
  -> Protocol and schema validation
  -> Identifier and cryptographic validation
  -> Replay, district, and causal validation
  -> Membership, authority, and scope validation
  -> Ruleset, transition, and conflict validation
  -> Accepted, rejected, quarantined, or duplicate
  -> Deterministic reduction when effective
```

The submission store, accepted-operation log, and derived-state projection are
distinct logical stores. An implementation MAY colocate them physically but
MUST preserve their semantics.

## 3. Canonical envelope

```text
OperationEnvelope {
  protocol_version
  ruleset_id
  operation_id
  district_id
  author
  operation_type
  target
  payload
  evidence_ids
  parent_ids
  dependencies
  causal
  authorization
  created_at
  valid_from
  expires_at
  nonce
  content_hash
  signature
}
```

The wire form is UTF-8 JSON conforming to
[`operation-envelope.schema.json`](schemas/operation-envelope.schema.json).
Unknown top-level fields are forbidden in v0.2.

### 3.1 Version and ruleset binding

`protocol_version` MUST be `dap/0.2` for this specification.

`ruleset_id` identifies the exact content-addressed district ruleset requested
for evaluation. The ruleset MUST be active at the operation's causal
evaluation point. A ruleset proposal or activation is validated under its
predecessor ruleset; a ruleset never authorizes its own activation. Genesis
MUST bind an initial ruleset.

### 3.2 Identifier, content hash, and signature

Define `operation_body` as the complete envelope with `operation_id`,
`content_hash`, and `signature` removed.

Before canonical encoding, set-valued arrays MUST be sorted by UTF-8 byte order
and MUST NOT contain duplicates:

- `evidence_ids`;
- `parent_ids`;
- `dependencies`;
- `authorization.authority_ids`.

Order is semantic and MUST be preserved for `target.scope_path` and
`authorization.delegation_chain`.

```text
body_bytes = canonical_encode(operation_body)
digest = SHA-256(UTF8("DAP-OPERATION-0.2") || 0x00 || body_bytes)
content_hash = "sha256:" || lowercase_hex(digest)
operation_id = "op:" || multibase_base58btc(digest)
signature.value = base64url_no_padding(Ed25519.sign(digest, signing_key))
```

Ed25519 is mandatory to implement in v0.2. Additional algorithms require an
explicit compatibility profile. A signature covers the raw 32-byte digest,
not the textual `content_hash`.

This construction provides content addressing, idempotent duplicate detection,
tamper detection, and stable references without a recursive preimage.

### 3.3 District

`district_id` identifies the one district history that receives the operation.
One operation MUST NOT directly mutate two district histories. Cross-district
actions use corresponding export, import, fork, or merge operations in every
affected district.

### 3.4 Author

```text
author {
  identity_id
  signing_key_id
  actor_class
}
```

`identity_id` names the persistent root identity. `signing_key_id` names the
delegated signing key. `actor_class` is one of:

- `human_direct`;
- `human_assisted`;
- `autonomous_agent`;
- `institutional_agent`;
- `service_actor`;
- `witness`;
- `archive`.

Actor class is a signed, auditable declaration. It is not proof of biological,
legal, or institutional status. Human and machine actors use the same
envelope.

### 3.5 Operation type

The type MUST be defined by the core registry or bound ruleset. District types
MUST use a district-qualified name and MUST NOT redefine a core type within the
same protocol version.

Core v0.2 types are:

```text
IDENTITY_DECLARE       IDENTITY_UPDATE        KEY_DELEGATE
KEY_REVOKE             DISTRICT_CREATE        RULESET_PROPOSE
RULESET_ACCEPT         RULESET_ACTIVATE       MEMBERSHIP_NOMINATE
MEMBERSHIP_ATTEST      MEMBERSHIP_ACTIVATE    MEMBERSHIP_SUSPEND
MEMBERSHIP_REMOVE      AUTHORITY_GRANT         AUTHORITY_REVOKE
AUTHORITY_DELEGATE     PROPOSAL_CREATE         PROPOSAL_AMEND
PROPOSAL_SUBMIT        PROPOSAL_REVIEW_BEGIN   PROPOSAL_ACCEPT
PROPOSAL_REJECT        PROPOSAL_ACTIVATE       PROPOSAL_ARCHIVE
COMMENT_ADD            ASSESSMENT_SUBMIT       OBSERVATION_SUBMIT
PREDICTION_SUBMIT      EVIDENCE_REGISTER       VOTE_CAST
OBJECTION_RAISE        VETO_ATTACH             VETO_RESOLVE
DOCUMENT_PATCH         DOCUMENT_SNAPSHOT       OPERATION_REJECT
OPERATION_REVERSE      CHECKPOINT_PROPOSE      CHECKPOINT_ATTEST
CHECKPOINT_FINALIZE    EXPORT_CREATE           IMPORT_ACCEPT
FORK_DECLARE           MERGE_PROPOSE           MERGE_ACCEPT
```

`OPERATION_REJECT` is a governance action against an accepted pending or
contested operation. It is not a substitute for a validator's rejection
disposition. Type payloads, transitions, and reducers are separately versioned
registry entries.

### 3.6 Target and payload

```text
target {
  resource_type
  resource_id
  scope_path[]
}
```

Each scope segment is an opaque, NFC-normalized string. Containment is segment
based, never raw string-prefix matching. A grant scope contains a target when
all grant segments match the corresponding target segments. `*` matches one
segment and terminal `**` matches zero or more segments when the active ruleset
permits wildcards.

`payload` is type-specific data. Every registered operation type MUST define
required and optional fields, a closed-field policy, permitted values,
transition semantics, validation guards, conflict keys, and reduction behavior.
Signed payloads MUST NOT contain binary floating-point numbers.

### 3.7 Evidence, parents, and dependencies

`evidence_ids` references immutable registered or provenance-preserving
imported evidence. A reference asserts a relationship, not truth.

`parent_ids` records semantic response or derivation links. Parent links do not
create district-wide total order.

`dependencies` lists operations whose accepted or effective status is required.
Each type rule MUST declare which status is required. Missing dependencies
produce the rule's declared outcome: rejection, pending, or quarantine. A
validator MUST NOT silently choose among these outcomes.

### 3.8 Causal metadata

```text
causal {
  author_sequence
  previous_author_operation
  observed_checkpoint
  logical_time { lamport, tie_breaker }
}
```

`author_sequence` is a strictly increasing positive integer per signing key and
district. `previous_author_operation` links the preceding operation by that key
in that district. Together they detect replay, gaps, and equivocation but do
not create total order.

`observed_checkpoint` identifies the latest finalized checkpoint known to the
author. `logical_time.lamport` MUST be greater than the Lamport values of every
declared parent, dependency, and previous-author operation. The tie breaker is
the author's `identity_id` in v0.2.

Rulesets MAY reject or quarantine operations based on a stale checkpoint, but
staleness MUST be calculated from accepted checkpoint history rather than
network arrival time.

### 3.9 Authorization claim

```text
authorization {
  authority_ids[]
  delegation_chain[]
  required_capability
}
```

This structure states the authority path the author relies on. The validator
MUST independently derive the required capability from the operation rule,
resolve the authority graph, and compare the result with the claim. Informal
reputation and trust are not authority.

Each delegation link MUST be accepted, active, scope-containing,
capability-compatible, temporally valid, and unrevoked in the evaluation
pre-state. Delegation cycles are invalid.

### 3.10 Time and nonce

`created_at`, `valid_from`, and `expires_at` are RFC 3339 UTC timestamps with
exactly second precision and the `Z` suffix. The validity interval is half-open:
`[valid_from, expires_at)`. Null `valid_from` means no lower bound; null
`expires_at` means no upper bound.

`created_at` is a signed claim. `district_time` is the timestamp committed by
the latest finalized checkpoint in the evaluation pre-state. Only
`district_time` can deterministically open or close effect windows. Validator
local clocks MAY reject implausible submissions at the transport edge but MUST
NOT change authoritative state.

`nonce` distinguishes intentionally separate operations with otherwise equal
bodies. It does not replace the author sequence. It MUST contain at least 128
bits of entropy when randomly generated.

## 4. Canonical serialization

`canonical_encode` is deterministic JSON with these rules:

1. input is decoded as UTF-8; malformed UTF-8 and duplicate object keys fail;
2. object keys and string values are normalized to Unicode NFC; normalization
   collisions between keys fail;
3. object keys are sorted by lexicographic UTF-8 byte order after NFC;
4. arrays preserve order, subject to the set-field normalization above;
5. only null, booleans, strings, safe integers, arrays, and objects are allowed;
6. negative zero and binary floating point are forbidden;
7. fixed-point governance values are signed decimal strings or scaled integers;
8. strings use JSON escapes with no insignificant whitespace;
9. timestamps use the UTC form specified in section 3.10;
10. absent optional fields MUST be encoded as explicit null where the schema
    requires a nullable field. Missing and null are never silently equated.

Implementations MUST compare canonical test vectors before claiming hash or
signature interoperability.

## 5. Ordered validation

Validation consumes the submitted envelope, the bound ruleset, accepted
history, evaluation pre-state, registered keys and schemas, and finalized
checkpoint data. A stage MUST NOT report success unless all required inputs are
known.

| Stage | Required checks | Representative results |
|---|---|---|
| 1 Protocol | version, envelope shape, closed fields, types, sizes, identifier encodings | `VALID_PROTOCOL`, `INVALID_PROTOCOL` |
| 2 Schema | operation-type payload schema | `VALID_SCHEMA`, `INVALID_SCHEMA` |
| 3 Identifier | canonical body, operation ID, content hash | `VALID_IDENTIFIER`, `ERR_OPERATION_ID`, `ERR_CONTENT_HASH` |
| 4 Cryptographic | key existence, algorithm, signature, identity binding, delegation, expiry, revocation | `VALID_SIGNATURE`, `UNKNOWN_KEY`, `REVOKED_KEY`, `EXPIRED_KEY` |
| 5 Replay | operation ID, nonce policy, author sequence, author chain | `NEW_OPERATION`, `EXACT_DUPLICATE`, `REPLAY`, `AUTHOR_CHAIN_CONFLICT` |
| 6 District | district existence/status, target district, active ruleset and protocol | `VALID_DISTRICT`, `ERR_DISTRICT`, `ERR_RULESET_BINDING` |
| 7 Causal | parents, dependencies, per-key chain, Lamport time, checkpoint, stale-state rule | `VALID_CAUSAL`, `ERR_PARENT_MISSING`, `ERR_DEPENDENCY_MISSING` |
| 8 Membership | membership class required by the operation rule | `VALID_MEMBERSHIP`, `ERR_MEMBERSHIP` |
| 9 Authority | capability, grant, chain, jurisdiction, domain, weight, delegation bounds and conflicts | `VALID_AUTHORITY`, `ERR_CAPABILITY`, `ERR_AUTHORITY_WEIGHT` |
| 10 Scope | segment-wise scope containment and permitted wildcard use | `VALID_SCOPE`, `ERR_SCOPE` |
| 11 Ruleset | deterministic contextual guards, thresholds, actor restrictions and evidence | `VALID_RULESET`, `ERR_RULESET`, `ERR_AGENT_RESTRICTION` |
| 12 Transition | legal transition from evaluation pre-state | `VALID_STATE_TRANSITION`, `ERR_STATE_TRANSITION` |
| 13 Conflict | declared conflict key and per-type policy | `NO_CONFLICT`, `ERR_CONFLICT`, `CONTESTED` |
| 14 Classification | precedence rules and effect gates | final disposition |

An exact duplicate is acknowledged idempotently with the original disposition.
Unknown keys, unavailable history, unsupported compatibility dependencies, and
unresolvable forks are quarantined rather than falsely rejected.

## 6. Acceptance classification

The v0.2 dispositions are:

- `ACCEPTED_EFFECTIVE`: accepted and presently contributes to derived state;
- `ACCEPTED_PENDING`: accepted but awaiting a deterministic condition;
- `ACCEPTED_CONTESTED`: accepted and subject to an effective objection or veto;
- `REJECTED`: evaluated and invalid under protocol, authority, or ruleset;
- `QUARANTINED`: evaluation inputs are insufficient or incompatible;
- `SUPERSEDED`: valid accepted history that no longer controls current state;
- `DUPLICATE`: an idempotent repeat of an already processed operation.

Classification precedence is:

1. exact duplicate;
2. quarantine for unavailable facts required to evaluate validity;
3. rejection for known-invalid facts;
4. supersession under an accepted conflict or lifecycle rule;
5. contested status from an effective objection or veto;
6. pending status from unsatisfied effect gates;
7. effective status.

Rulesets may refine reason codes and pending conditions but MUST NOT reorder
this precedence in v0.2.

## 7. Dispositions and rejection

Rejected submissions MAY be retained outside the accepted-operation stream.
Their evaluation record is a signed object:

```text
OperationDisposition {
  submitted_operation_id
  disposition
  validator_id
  ruleset_id
  reason_codes[]
  explanation
  evaluated_at_checkpoint
  history_root_before
  state_root_before
  signature
}
```

`evaluated_at_checkpoint` replaces an unauditable validator wall-clock time.
For accepted operations, `ValidationResult` additionally records
`history_root_after`, `state_root_after`, and `pending_conditions`. A pending
operation changes the accepted-history root even when the derived-state root is
unchanged.

Core rejection reasons include:

```text
ERR_PROTOCOL_VERSION       ERR_SCHEMA
ERR_OPERATION_ID           ERR_CONTENT_HASH
ERR_SIGNATURE              ERR_UNKNOWN_KEY
ERR_REVOKED_KEY            ERR_EXPIRED_KEY
ERR_REPLAY                 ERR_AUTHOR_CHAIN
ERR_DISTRICT               ERR_RULESET_BINDING
ERR_PARENT_MISSING         ERR_DEPENDENCY_MISSING
ERR_MEMBERSHIP             ERR_CAPABILITY
ERR_SCOPE                  ERR_AUTHORITY_WEIGHT
ERR_QUORUM                 ERR_RULESET
ERR_STATE_TRANSITION       ERR_CONFLICT
ERR_EXPIRED                ERR_AGENT_RESTRICTION
ERR_CONSTITUTIONAL_CONSTRAINT
```

A changed submission is a new operation with a new body digest. Rejection does
not permit mutation and reuse of the old ID.

## 8. Deterministic reduction

```text
reduce(genesis_state, finalized_checkpoint, accepted_operations,
       active_rulesets, protocol_version) -> DistrictState
```

The reducer MUST be versioned, deterministic, side-effect free,
independently executable, explicit about conflicts, and insensitive to
transport order except where accepted causal structure requires sequencing.

Ordering is a stable topological sort by:

1. dependencies whose rule requires effectiveness;
2. dependencies whose rule requires acceptance;
3. explicit parents where the type declares ordering significance;
4. proposal-version dependencies;
5. Lamport value;
6. operation ID by UTF-8 byte order.

Cycles in required causal edges are quarantined. Semantic parents that do not
declare ordering significance do not create graph edges for the topological
sort.

The output contains identities, keys, membership, authorities, proposals,
votes, vetoes, evidence, documents, checkpoints, federation, forks, and
unresolved conflicts. Every projection field MUST be reproducible from
accepted history.

## 9. Authority resolution

Authority is derived only from accepted effective authority, membership, and
key operations. A grant contains issuer, recipient, jurisdiction, domain,
capability, scope, scaled integer weight, delegation permission, maximum depth,
constraints, and validity bounds.

Every delegation MUST satisfy:

```text
delegated_scope is contained by received_scope
delegated_capability is equal to or implied by received_capability
delegated_weight <= received_weight
delegated_duration <= remaining_duration
delegated_depth < maximum_delegation_depth
```

Where multiple paths reach an actor, the ruleset declares one of `maximum`,
`sum_capped`, `independent_threshold`, `issuer_diversity`, or
`non_aggregating`. The v0.2 default is non-aggregation by ultimate issuer:
paths with the same root issuer contribute at most the maximum valid path
weight, never their sum.

Trust is a derived evaluation and is not authority. A ruleset can convert a
trust condition into authority only through an accepted authority operation
whose grant and limits remain independently auditable.

## 10. Checkpoints and roots

A finalized checkpoint commits to all of:

- protocol version;
- active ruleset ID;
- ordered accepted-operation history root;
- derived-state root;
- unresolved-conflict root;
- district time;
- parent checkpoint.

The history root and state root MUST be separate. Two histories can project the
same current state while retaining different accepted pending or superseded
operations.

## 11. Mandatory invariants

1. No authoritative state mutation exists without an accepted operation.
2. Every accepted operation has a verifiable author signature.
3. Every operation belongs to exactly one district history.
4. Every operation binds the ruleset under which it requests validation.
5. Authority is derived only from accepted authority operations.
6. Authority cannot exceed scope, capability, duration, weight, or delegation bounds.
7. Rejected operations do not affect authoritative derived state.
8. Reversal never deletes history.
9. A veto attaches to a target and never changes the target's signed content.
10. Trust is not authority without an explicit accepted conversion operation.
11. Human and machine actors use the same envelope and declare actor class.
12. Transport order and local wall clocks do not define governance validity.
13. Storage is not authoritative unless reconstructed from operation history.
14. District rules and validation decisions are version-bound.
15. Every checkpoint commits separately to exact accepted history and state.

## 12. Minimum conformance

A conforming implementation can generate canonical IDs, verify Ed25519
signatures, validate key delegation and per-key chains, resolve district
membership and scoped authority, apply rules deterministically, classify all
v0.2 dispositions, reconstruct state from accepted operations, preserve signed
rejection dispositions, reverse without deletion, expose active rulesets, and
reproduce history and state roots.

The envelope is the common substrate for governance, authority, trust,
evidence, collaboration, federation, forks, merges, audit, and AI
participation. It is the protocol's unit of accountable agency.
