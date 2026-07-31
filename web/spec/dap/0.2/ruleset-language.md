# District Ruleset Language Specification v0.2

Status: working draft

## 1. Purpose

The DAP ruleset language is a closed, data-only policy language. It determines
who may submit an operation, which authority must support it, what conditions
make it admissible, when it becomes effective, how conflicts are handled, and
how objections and vetoes affect it.

The language is intentionally not general-purpose. A ruleset MUST NOT perform
I/O, read a validator clock, call a network service, execute user code, generate
random values, or inspect data outside its declared evaluation context.

```text
evaluate(ruleset, operation, pre_state, accepted_history, checkpoint_facts)
  -> RulesetDecision
```

The same inputs MUST produce byte-identical machine-readable decisions.

## 2. Ruleset lifecycle and identity

A ruleset document has these top-level fields:

```text
Ruleset {
  protocol_version
  language_version
  ruleset_id
  district_id
  ruleset_version
  predecessor_ruleset_id
  effective_from_checkpoint
  numeric_scale
  defaults
  capabilities[]
  decision_rules[]
  operation_rules[]
  reason_catalog[]
}
```

`ruleset_version` is a strictly increasing district-local integer.
`predecessor_ruleset_id` is null only for the genesis ruleset. A non-genesis
ruleset is valid only when:

1. its predecessor is the active ruleset;
2. `RULESET_PROPOSE` accepted the exact content-addressed document;
3. `RULESET_ACCEPT` satisfied the predecessor's amendment decision rule;
4. `RULESET_ACTIVATE` satisfied the predecessor's activation rule; and
5. `effective_from_checkpoint` is that activation checkpoint or a later one.

The proposed ruleset never validates its own proposal, acceptance, or
activation.

Define `ruleset_body` as the ruleset document with `ruleset_id` removed:

```text
digest = SHA-256(UTF8("DAP-RULESET-0.2") || 0x00 || canonical_encode(ruleset_body))
ruleset_id = "ruleset:" || multibase_base58btc(digest)
```

Ruleset documents use the canonical encoding defined by the operation
specification. Any collection declared as a set by this document MUST be sorted
by UTF-8 byte order and contain no duplicates.

## 3. Evaluation context

Rules can read only these immutable roots:

| Root | Meaning |
|---|---|
| `/operation` | Canonical submitted envelope |
| `/pre_state` | Derived state immediately before this operation in deterministic reduction order |
| `/history` | Accepted-operation indexes committed by `history_root_before` |
| `/checkpoint` | Finalized checkpoint, district time, and committed roots |
| `/derived` | Validator-computed facts such as resolved membership and authority paths |
| `/candidate` | Type-registry facts such as required capability and proposed transition |

Paths are RFC 6901-style JSON Pointers restricted to these roots. A path does
not invoke code. Missing paths evaluate as `UNKNOWN`, not null.

The evaluation context MUST commit to:

```text
EvaluationContextCommitment {
  operation_id
  ruleset_id
  checkpoint_id
  history_root_before
  state_root_before
  operation_registry_root
  key_registry_root
}
```

This makes the policy decision reproducible and prevents hidden validator input.

## 4. Value model

The language supports:

- null;
- boolean;
- NFC strings;
- signed safe integers;
- arrays;
- objects;
- `UNKNOWN`, an evaluator result that is never serializable as ruleset input.

Binary floating point, implicit type conversion, locale-sensitive comparison,
regular expressions, and unbounded arithmetic are prohibited. Governance
weights use integers at `numeric_scale`; v0.2 recommends `1000000`.

All string equality is code-point exact after NFC. Ordering uses UTF-8 byte
order. Integer operations fail to `UNKNOWN` on overflow beyond the signed
safe-integer range.

## 5. Expression language

An expression is either a literal value or one of the closed expression forms
below. Every operator has fixed arity and exact operand types.

### 5.1 Data access

```json
{ "path": "/operation/author/actor_class" }
```

`path` returns the value at that exact context path or `UNKNOWN`.

### 5.2 Logical expressions

```json
{ "all": [expr, expr] }
{ "any": [expr, expr] }
{ "not": expr }
```

Logical operators use strong Kleene three-valued logic:

| Inputs | `all` | `any` |
|---|---|---|
| contains decisive false / true | false | true |
| otherwise contains unknown | unknown | unknown |
| otherwise | true | false |

`not UNKNOWN` is `UNKNOWN`. Empty `all` is true; empty `any` is false.

### 5.3 Comparison and collection expressions

```json
{ "eq": [left, right] }
{ "neq": [left, right] }
{ "lt": [left, right] }
{ "lte": [left, right] }
{ "gt": [left, right] }
{ "gte": [left, right] }
{ "in": [item, array] }
{ "contains_all": [array, required_array] }
{ "subset": [candidate_array, containing_array] }
{ "exists": { "path": "/pre_state/proposals/proposal:q3-roadmap" } }
{ "count": { "path": "/derived/eligible_voters" } }
{ "distinct_count": [{ "path": "/derived/attestations" }, "issuer_id"] }
{ "scope_contains": [grant_scope, target_scope] }
```

Comparisons require equal scalar types. `lt`, `lte`, `gt`, and `gte` accept
integers or RFC 3339 UTC timestamp strings, never mixed types. `subset` uses set
semantics and requires duplicate-free arrays. `scope_contains` uses the segment
rules in the envelope specification.

### 5.4 Integer arithmetic

```json
{ "add": [integer_expr, integer_expr] }
{ "sub": [integer_expr, integer_expr] }
{ "mul": [integer_expr, integer_expr] }
{ "min": [integer_expr, integer_expr] }
{ "max": [integer_expr, integer_expr] }
```

Division is deliberately absent. Ratios are evaluated by non-negative integer
cross multiplication. This avoids rounding disagreements.

Every expression form appears explicitly in the ruleset JSON Schema. An
unrecognized form is invalid schema, not `UNKNOWN`.

## 6. Guard semantics

Context-dependent requirements are ordered guards:

```text
Guard {
  guard_id
  assert
  on_false: reject | pending | contested | supersede
  on_unknown: reject | pending | quarantine
  reason_code
  pending_condition
}
```

Guards are evaluated in declared array order to produce a stable explanation,
but all guards are evaluated unless an earlier base-protocol stage makes safe
evaluation impossible. `reason_codes` retain guard order and MUST NOT contain
duplicates.

`on_unknown: reject` SHOULD be limited to facts the submitter was required to
provide. Missing external history, keys, or checkpoints normally quarantine.

## 7. Capabilities and authority

A capability declaration has an ID and an optional set of weaker capabilities
it implies. The implication graph MUST be acyclic. Capability matching is exact
or follows a directed implication edge; capability names are not string
prefixes and have no implicit wildcard semantics.

Each operation rule declares one required capability and an authority policy:

```text
AuthorityPolicy {
  required
  minimum_weight
  aggregation
  minimum_root_issuers
  scope_mode
  jurisdiction_mode
  domain_mode
  maximum_delegation_depth
  conflict_of_interest_guard
}
```

The validator resolves paths from accepted effective grants in `pre_state`.
Every path is rejected as a unit if any edge is expired, revoked, suspended,
out of scope, capability-incompatible, jurisdiction-incompatible,
domain-incompatible, too deep, or creates a cycle.

Aggregation modes are:

- `non_aggregating`: take the maximum valid path weight per ultimate issuer,
  then take the maximum of those issuer weights;
- `maximum`: take the maximum valid path weight;
- `sum_capped`: take one maximum path per ultimate issuer, sum, and cap at
  `numeric_scale`;
- `independent_threshold`: require `minimum_root_issuers` distinct roots, each
  independently meeting `minimum_weight`;
- `issuer_diversity`: sum one maximum path per root and also require
  `minimum_root_issuers`.

No mode stacks two paths from the same ultimate issuer. Rulesets MAY make trust
a guard on issuance of an authority grant, but authority evaluation never reads
trust as a substitute for a grant.

## 8. Membership and actor policy

Each operation rule declares sorted, duplicate-free `allowed_actor_classes` and
`allowed_membership_statuses`. Membership is resolved at `state_root_before`.
The author MUST meet both lists.

Actor restrictions are capability-specific. For example, a ruleset can allow
an autonomous agent to create and amend proposals while excluding it from
proposal activation. No rule may infer actor class from user-agent strings,
network origin, prose claims, or key shape.

## 9. Evidence policy

An evidence policy declares:

```text
EvidencePolicy {
  minimum_count
  required_record_types[]
  require_registered
  require_immutable
  require_provenance
}
```

Evidence policy validates relationships and record properties, not the truth of
the evidence. Truth or sufficiency judgments require separate signed
assessments or decision operations.

## 10. Dependencies and causal policy

An operation rule selects one dependency mode:

- `accepted`: every listed dependency must be in accepted history;
- `effective`: every listed dependency must currently be effective;
- `typed`: the type registry declares required status per dependency role.

It also declares `missing_dependency` as `reject`, `pending`, or `quarantine`.
Dependency cycles are always quarantined. Parent ordering is used only when
`parents_establish_order` is true for the operation type.

## 11. State transitions

A transition policy contains a resource type, allowed source states, and the
state produced when the operation is effective:

```text
TransitionPolicy {
  resource_type
  from[]
  pending_state
  contested_state
  effective_state
  terminal
}
```

`from` is matched against `pre_state`. A missing target is distinct from a
target in a state named `absent`; creation rules explicitly use `absent`.
Accepted pending and contested operations MAY project procedural status but
MUST NOT apply `effective_state` behavior.

Terminal transitions cannot be exited unless a separately registered
restoration or reversal operation explicitly names that source state.
`OPERATION_REVERSE` adds a compensating transition and never deletes the
reversed operation.

## 12. Decision rules and thresholds

A reusable decision rule declares:

```text
DecisionRule {
  decision_rule_id
  electorate
  snapshot
  ballot
  weighting
  quorum
  approval
  tie_policy
  duplicate_vote_policy
}
```

`snapshot` is one of `proposal_submission_checkpoint`,
`review_begin_checkpoint`, or an explicitly named finalized checkpoint. Voter
eligibility and weights are frozen at that snapshot unless the rule explicitly
selects `live_checkpoint`; the live mode SHOULD be avoided for constitutional
decisions.

`ballot` declares the closed set of choices. `weighting` is
`one_member_one_vote` or `authority_weighted`. Duplicate votes are keyed by
identity and proposal version, not signing key. The duplicate policy is
`reject_later` or `supersede_earlier`; transport order is never used, so
"later" means deterministic operation order.

Quorum and approval ratios are reduced, non-negative integer fractions:

```text
ratio { numerator, denominator }
```

Quorum is satisfied exactly when:

```text
participating_weight * quorum.denominator
  >= eligible_weight * quorum.numerator
```

Approval is satisfied exactly when:

```text
affirmative_weight * approval.denominator
  >= approval_base_weight * approval.numerator
```

`approval_base` is one of `eligible`, `participating`, or `non_abstaining`.
Abstention behavior is therefore explicit. A zero approval base does not pass.
Tie policy is `reject`, `pending`, or a separately authorized tie-break
operation; no validator chooses a winner.

## 13. Time and effect gates

Timing policies read `/checkpoint/district_time`. They never read system time.
Durations are non-negative integer seconds and timestamps are UTC seconds.

A time window is half-open. An operation before `valid_from` is accepted pending
when otherwise valid. A not-yet-effective operation at or after `expires_at`
becomes `SUPERSEDED` with its declared expiry reason. An already effective
operation remains historical and is changed only by an accepted expiration,
revocation, transition, or reversal rule.

An operation rule may declare effect gates. All effect gates must evaluate true
for `ACCEPTED_EFFECTIVE`. False gates create `ACCEPTED_PENDING`; unknown gates
use the guard's declared unknown behavior.

Elapsed review periods are measured between finalized checkpoint district
times. A timestamp claim in an operation payload cannot itself prove that a
review period elapsed.

## 14. Conflicts

Every operation rule declares a conflict key as a non-empty array of context
paths and one policy:

- `reject_later`;
- `accept_both`;
- `supersede`;
- `merge`;
- `require_resolution`;
- `select_by_rule`.

The conflict key is evaluated to a canonical tuple. Operations conflict only
when their type registry declares them members of the same conflict class and
their tuples match. A global last-write-wins policy is forbidden.

`supersede` and `select_by_rule` must name a deterministic selector such as
highest proposal version or lexical operation ID. `merge` must name a
registered, versioned, pure merge reducer. `require_resolution` produces
`ACCEPTED_CONTESTED` until an effective resolution operation references every
conflict member.

## 15. Objections and vetoes

Objections and vetoes are operations, not mutable flags. A veto policy declares:

```text
VetoPolicy {
  enabled
  veto_operation_type
  allowed_veto_classes[]
  required_capability
  evidence_policy
  attachable_target_states[]
  effect
  review_period_seconds
  resolution_operation_type
  resolution_decision_rule_id
}
```

The effect is one of:

- `contest_only`: target remains otherwise effective but is visibly contested;
- `suspend_effect`: target's effect is suspended prospectively;
- `block_activation`: pending target cannot become effective;
- `require_resolution`: target enters contested status until resolution.

A veto never alters the target envelope, never deletes history, and never
retroactively makes a valid signature invalid. Only an accepted effective
`VETO_RESOLVE`, `OPERATION_REVERSE`, or other registered resolution type changes
its effect. Emergency vetoes MUST declare a maximum review period and a
resolution path; an indefinite unreviewable veto is non-conformant.

## 16. Rule selection and evaluation algorithm

Given an operation that passed base protocol, schema, identifier,
cryptographic, replay, district, and causal validation:

1. Load the exact `ruleset_id` and confirm it is active at the evaluation
   checkpoint.
2. Select exactly one operation rule by `operation_type`. Zero or multiple
   matches reject.
3. Independently compare the rule capability with
   `authorization.required_capability`.
4. Resolve actor class and membership status.
5. Resolve every claimed and available authority path, then apply scope,
   domain, jurisdiction, delegation, aggregation, and conflict-of-interest
   constraints.
6. Evaluate evidence and ordered guards.
7. Validate the declared state transition.
8. Compute the conflict tuple and apply its policy.
9. Apply accepted objections and vetoes under classification precedence.
10. Evaluate timing, quorum, countersignature, and other effect gates.
11. Emit `RulesetDecision` and its context commitment.

The algorithm MUST collect all safely evaluable reasons instead of returning
only the first policy failure.

## 17. Decision output

```text
RulesetDecision {
  operation_id
  ruleset_id
  disposition
  required_capability
  resolved_membership_status
  accepted_authority_path_ids[]
  rejected_authority_paths[]
  effective_authority_weight
  guard_results[]
  conflict_operation_ids[]
  veto_operation_ids[]
  reason_codes[]
  pending_conditions[]
  transition
  context_commitment
}
```

Authority path and operation ID arrays are UTF-8 sorted. Explanatory human text
may accompany the decision but is never the normative reason. Validators MUST
emit machine-readable guard outcomes and reason codes.

## 18. Defaults and closed-world behavior

Each ruleset declares defaults for unknown facts, missing dependencies,
unregistered operation types, conflict policy, authority aggregation, and
wildcard scope. In v0.2:

- an unregistered operation type is rejected;
- an unavailable fact needed for validity is quarantined;
- an unsatisfied but satisfiable effect gate is pending;
- authority does not aggregate across paths from one root issuer;
- scope wildcards are disabled unless explicitly enabled;
- undeclared fields and implicit capabilities are forbidden.

A district may choose stricter results but may not silently rely on
implementation defaults.

## 19. Static ruleset validation

Before a ruleset may be proposed, validators MUST verify:

1. JSON Schema conformance;
2. canonical `ruleset_id`;
3. exact district and protocol binding;
4. unique IDs for capabilities, decisions, guards, and reasons;
5. acyclic capability implication graph;
6. exactly one operation rule per registered operation type it governs;
7. references to existing capabilities, decisions, and reason codes;
8. reduced ratios with nonzero denominators;
9. valid expression paths and operator arity;
10. sorted unique set fields;
11. no unreachable transition introduced by accidental state-name mismatch;
12. no veto policy without a resolution operation and bounded review path;
13. no custom merge or selector without a content-addressed registered reducer;
14. no rule that reads undeclared or nondeterministic context.

Schema validity alone is insufficient; these cross-reference and graph checks
are mandatory semantic validation.

## 20. Minimal conformance vectors

A rules engine claiming v0.2 conformance MUST publish vectors demonstrating:

- true, false, and unknown three-valued logic;
- NFC canonicalization and normalization-collision rejection;
- stable operation and ruleset identifiers;
- exact rational threshold boundaries;
- same-root delegation paths not stacking;
- scope segment and wildcard behavior;
- actor-class exclusion despite otherwise sufficient authority;
- pending review and quorum gates;
- veto attachment, contest, and resolution without target mutation;
- deterministic conflict selection under shuffled transport order;
- different history roots with equal projected state roots;
- quarantine for missing history rather than false rejection.

The example ruleset and verification script in this directory are the first
normative vectors. A production conformance suite must extend them across every
core operation type.
