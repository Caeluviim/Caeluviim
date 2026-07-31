export const DAP_PROTOCOL_VERSION = "dap/0.2" as const;
export const DAP_RULE_LANGUAGE_VERSION = "dap-rules/0.2" as const;

export const ACTOR_CLASSES = [
  "human_direct",
  "human_assisted",
  "autonomous_agent",
  "institutional_agent",
  "service_actor",
  "witness",
  "archive",
] as const;

export type ActorClass = (typeof ACTOR_CLASSES)[number];

export const DISPOSITIONS = [
  "ACCEPTED_EFFECTIVE",
  "ACCEPTED_PENDING",
  "ACCEPTED_CONTESTED",
  "REJECTED",
  "QUARANTINED",
  "SUPERSEDED",
  "DUPLICATE",
] as const;

export type DapDisposition = (typeof DISPOSITIONS)[number];

export type DapSignature = {
  algorithm: "Ed25519";
  value: string;
};

export type DapOperationEnvelope = {
  protocol_version: typeof DAP_PROTOCOL_VERSION;
  ruleset_id: string;
  operation_id: string;
  district_id: string;
  author: {
    identity_id: string;
    signing_key_id: string;
    actor_class: ActorClass;
  };
  operation_type: string;
  target: {
    resource_type: string;
    resource_id: string;
    scope_path: string[];
  };
  payload: Record<string, unknown>;
  evidence_ids: string[];
  parent_ids: string[];
  dependencies: string[];
  causal: {
    author_sequence: number;
    previous_author_operation: string | null;
    observed_checkpoint: string | null;
    logical_time: {
      lamport: number;
      tie_breaker: string;
    };
  };
  authorization: {
    authority_ids: string[];
    delegation_chain: string[];
    required_capability: string;
  };
  created_at: string;
  valid_from: string | null;
  expires_at: string | null;
  nonce: string;
  content_hash: string;
  signature: DapSignature;
};

export type DapExpression = unknown;

export type DapGuard = {
  guard_id: string;
  assert: DapExpression;
  on_false: "reject" | "pending" | "contested" | "supersede";
  on_unknown: "reject" | "pending" | "quarantine";
  reason_code: string;
  pending_condition: string | null;
};

export type DapAuthorityPolicy = {
  required: boolean;
  minimum_weight: number;
  aggregation: "non_aggregating" | "maximum" | "sum_capped" | "independent_threshold" | "issuer_diversity";
  minimum_root_issuers: number;
  scope_mode: "contain_target" | "exact_target" | "district_wide";
  jurisdiction_mode: "contain_target" | "exact_target" | "not_applicable";
  domain_mode: "contain_target" | "exact_target" | "not_applicable";
  maximum_delegation_depth: number;
  conflict_of_interest_guard: DapExpression | null;
};

export type DapEvidencePolicy = {
  minimum_count: number;
  required_record_types: string[];
  require_registered: boolean;
  require_immutable: boolean;
  require_provenance: boolean;
};

export type DapOperationRule = {
  operation_type: string;
  required_capability: string;
  allowed_actor_classes: ActorClass[];
  allowed_membership_statuses: string[];
  authority: DapAuthorityPolicy;
  evidence: DapEvidencePolicy;
  dependencies: {
    required_status: "accepted" | "effective" | "typed";
    missing_dependency: "reject" | "pending" | "quarantine";
    parents_establish_order: boolean;
  };
  guards: DapGuard[];
  transition: {
    resource_type: string;
    from: string[];
    pending_state: string | null;
    contested_state: string | null;
    effective_state: string;
    terminal: boolean;
  };
  effect_gates: DapGuard[];
  conflict: {
    conflict_class: string;
    key: string[];
    policy: "reject_later" | "accept_both" | "supersede" | "merge" | "require_resolution" | "select_by_rule";
    selector: string | null;
    merge_reducer_id: string | null;
  };
  veto: Record<string, unknown> | null;
};

export type DapDecisionRule = {
  decision_rule_id: string;
  electorate: DapExpression;
  snapshot: string;
  ballot: string[];
  weighting: "one_member_one_vote" | "authority_weighted";
  quorum: { numerator: number; denominator: number };
  approval: {
    ratio: { numerator: number; denominator: number };
    base: "eligible" | "participating" | "non_abstaining";
  };
  tie_policy: "reject" | "pending" | "authorized_tie_break";
  duplicate_vote_policy: "reject_later" | "supersede_earlier";
};

export type DapRuleset = {
  protocol_version: typeof DAP_PROTOCOL_VERSION;
  language_version: typeof DAP_RULE_LANGUAGE_VERSION;
  ruleset_id: string;
  district_id: string;
  ruleset_version: number;
  predecessor_ruleset_id: string | null;
  effective_from_checkpoint: string | null;
  numeric_scale: number;
  defaults: {
    unknown_fact: "reject" | "pending" | "quarantine";
    missing_dependency: "reject" | "pending" | "quarantine";
    unregistered_operation: "reject";
    conflict_policy: DapOperationRule["conflict"]["policy"];
    authority_aggregation: DapAuthorityPolicy["aggregation"];
    wildcard_scope: boolean;
  };
  capabilities: Array<{ capability_id: string; implies: string[] }>;
  decision_rules: DapDecisionRule[];
  operation_rules: DapOperationRule[];
  reason_catalog: Array<{
    code: string;
    default_disposition: DapDisposition;
    description: string;
  }>;
};

export type DapKeyState = {
  key_id: string;
  identity_id: string;
  algorithm: "Ed25519";
  public_key: string;
  status: "active" | "revoked" | "expired";
  author_sequence: number;
  previous_author_operation: string | null;
  delegated_by: string | null;
  valid_from: string | null;
  expires_at: string | null;
};

export type DapMembershipState = {
  identity_id: string;
  status: "active" | "probationary" | "suspended" | "removed" | "external" | "service-only";
  roles: string[];
  updated_by_operation: string;
};

export type DapAuthorityState = {
  authority_id: string;
  issuer_id: string;
  recipient_id: string;
  root_issuer_id: string;
  capabilities: string[];
  scope: string[];
  weight: number;
  delegable: boolean;
  maximum_delegation_depth: number;
  delegation_depth: number;
  parent_authority_id: string | null;
  status: "active" | "revoked" | "suspended";
  valid_from: string | null;
  expires_at: string | null;
  created_by_operation: string;
};

export type DapProposalState = {
  proposal_id: string;
  state: string;
  title: string;
  body: string;
  current_version: number;
  decision_rule_id: string | null;
  review_period_seconds: number | null;
  submitted_at: string | null;
  created_by: string;
  versions: Array<{
    version: number;
    title: string;
    body: string;
    operation_id: string;
  }>;
};

export type DapVoteState = {
  operation_id: string;
  proposal_id: string;
  proposal_version: number;
  voter_id: string;
  choice: string;
  decision_rule_id: string;
  weight: number;
  effective: boolean;
};

export type DapDistrictState = {
  district: {
    district_id: string;
    name: string;
    status: "active" | "suspended" | "archived";
    protocol_version: typeof DAP_PROTOCOL_VERSION;
    active_ruleset_id: string;
    district_time: string;
    current_checkpoint_id: string | null;
  };
  identities: Record<string, { identity_id: string; actor_class: ActorClass; declared_by_operation: string }>;
  keys: Record<string, DapKeyState>;
  memberships: Record<string, DapMembershipState>;
  authorities: Record<string, DapAuthorityState>;
  proposals: Record<string, DapProposalState>;
  votes: Record<string, DapVoteState>;
  vetoes: Record<string, Record<string, unknown>>;
  evidence: Record<string, Record<string, unknown>>;
  documents: Record<string, Record<string, unknown>>;
  checkpoints: Record<string, Record<string, unknown>>;
  reversals: Record<string, Record<string, unknown>>;
  federation: Record<string, Record<string, unknown>>;
  forks: Record<string, Record<string, unknown>>;
  unresolved_conflicts: Record<string, Record<string, unknown>>;
};

export type AcceptedDapOperation = {
  envelope: DapOperationEnvelope;
  disposition: Extract<DapDisposition, "ACCEPTED_EFFECTIVE" | "ACCEPTED_PENDING" | "ACCEPTED_CONTESTED" | "SUPERSEDED">;
};

export type DapStageResult = {
  stage: number;
  name: string;
  result: string;
};

export type DapValidationResult = {
  operation_id: string;
  disposition: DapDisposition;
  stage_results: DapStageResult[];
  reason_codes: string[];
  pending_conditions: string[];
  ruleset_id: string;
  history_root_before: string | null;
  history_root_after: string | null;
  state_root_before: string | null;
  state_root_after: string | null;
  accepted_operation_count: number;
  effective_at_checkpoint: string | null;
  evaluated_at: string;
  validator_signature: null | {
    validator_id: string;
    signing_key_id: string;
    algorithm: "Ed25519";
    public_key: string;
    value: string;
  };
};

export type StoredDapDistrict = {
  district_id: string;
  name: string;
  protocol_version: string;
  active_ruleset_id: string;
  genesis_operation_id: string;
  status: string;
  created_at: string;
};

export type StoredDapState = {
  district_id: string;
  history_root: string;
  state_root: string;
  accepted_count: number;
  state: DapDistrictState;
  updated_at: string;
};
