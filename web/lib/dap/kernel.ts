import { z } from "zod";
import { env } from "cloudflare:workers";
import {
  canonicalEncode,
  domainDigest,
  historyRoot,
  operationIdentifiers,
  rulesetIdentifier,
  signEd25519Pkcs8,
  stateRoot,
  verifyEd25519,
} from "./canonical";
import {
  buildPolicyContext,
  evaluateExpression,
  resolveAuthority,
  resolvePath,
  resourceFromState,
  scopeContains,
  UNKNOWN,
} from "./policy";
import { createGenesisState, reduceAcceptedOperations } from "./reducer";
import {
  acceptDapOperation,
  createDapGenesis,
  getAcceptedDapOperation,
  getAcceptedDapOperations,
  getDapDistrict,
  getDapRuleset,
  getDapState,
  getDapSubmission,
  getLastKeyOperation,
  saveRejectedDapSubmission,
} from "./store";
import {
  ACTOR_CLASSES,
  DAP_PROTOCOL_VERSION,
  DAP_RULE_LANGUAGE_VERSION,
  type AcceptedDapOperation,
  type DapDisposition,
  type DapGuard,
  type DapOperationEnvelope,
  type DapOperationRule,
  type DapRuleset,
  type DapStageResult,
  type DapValidationResult,
  type StoredDapState,
} from "./types";

const identifierPattern = /^[A-Za-z][A-Za-z0-9._-]*:[^\s]+$/;
const operationIdPattern = /^op:z[1-9A-HJ-NP-Za-km-z]{43,50}$/;
const rulesetIdPattern = /^ruleset:z[1-9A-HJ-NP-Za-km-z]{43,50}$/;
const hashPattern = /^sha256:[a-f0-9]{64}$/;
const timestampPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
const capabilityPattern = /^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$/;

const identifier = z.string().min(3).max(512).regex(identifierPattern);
const operationId = z.string().regex(operationIdPattern);
const rulesetId = z.string().regex(rulesetIdPattern);
const timestamp = z.string().regex(timestampPattern);
const stringSet = (item: z.ZodTypeAny = identifier) => z.array(item).max(256);

const envelopeSchema = z
  .object({
    protocol_version: z.literal(DAP_PROTOCOL_VERSION),
    ruleset_id: rulesetId,
    operation_id: operationId,
    district_id: z.string().regex(/^district:[A-Za-z0-9._:-]+$/),
    author: z
      .object({
        identity_id: identifier,
        signing_key_id: identifier,
        actor_class: z.enum(ACTOR_CLASSES),
      })
      .strict(),
    operation_type: z.string().min(1).max(128).regex(/^(?:[A-Z][A-Z0-9_]*|district:[A-Za-z0-9._:-]+\/[A-Za-z][A-Za-z0-9._-]*)$/),
    target: z
      .object({
        resource_type: z.string().min(1).max(128).regex(/^[A-Za-z][A-Za-z0-9._-]*$/),
        resource_id: identifier,
        scope_path: z.array(z.string().min(1).max(256)).min(1).max(64),
      })
      .strict(),
    payload: z.record(z.string(), z.unknown()),
    evidence_ids: stringSet(),
    parent_ids: stringSet(operationId),
    dependencies: stringSet(operationId),
    causal: z
      .object({
        author_sequence: z.number().int().positive().safe(),
        previous_author_operation: operationId.nullable(),
        observed_checkpoint: identifier.nullable(),
        logical_time: z
          .object({
            lamport: z.number().int().positive().safe(),
            tie_breaker: identifier,
          })
          .strict(),
      })
      .strict(),
    authorization: z
      .object({
        authority_ids: stringSet(),
        delegation_chain: stringSet(),
        required_capability: z.string().min(1).max(128).regex(capabilityPattern),
      })
      .strict(),
    created_at: timestamp,
    valid_from: timestamp.nullable(),
    expires_at: timestamp.nullable(),
    nonce: z.string().min(22).max(128).regex(/^[A-Za-z0-9_-]+$/),
    content_hash: z.string().regex(hashPattern),
    signature: z
      .object({
        algorithm: z.literal("Ed25519"),
        value: z.string().length(86).regex(/^[A-Za-z0-9_-]+$/),
      })
      .strict(),
  })
  .strict();

const guardSchema = z
  .object({
    guard_id: identifier,
    assert: z.unknown(),
    on_false: z.enum(["reject", "pending", "contested", "supersede"]),
    on_unknown: z.enum(["reject", "pending", "quarantine"]),
    reason_code: z.string().regex(/^[A-Z][A-Z0-9_]*$/),
    pending_condition: z.string().max(128).nullable(),
  })
  .strict();

const operationRuleSchema = z
  .object({
    operation_type: z.string().min(1),
    required_capability: z.string().regex(capabilityPattern),
    allowed_actor_classes: z.array(z.enum(ACTOR_CLASSES)).min(1),
    allowed_membership_statuses: z.array(z.string().min(1)).min(1),
    authority: z
      .object({
        required: z.boolean(),
        minimum_weight: z.number().int().nonnegative().safe(),
        aggregation: z.enum(["non_aggregating", "maximum", "sum_capped", "independent_threshold", "issuer_diversity"]),
        minimum_root_issuers: z.number().int().positive().safe(),
        scope_mode: z.enum(["contain_target", "exact_target", "district_wide"]),
        jurisdiction_mode: z.enum(["contain_target", "exact_target", "not_applicable"]),
        domain_mode: z.enum(["contain_target", "exact_target", "not_applicable"]),
        maximum_delegation_depth: z.number().int().nonnegative().max(64),
        conflict_of_interest_guard: z.unknown().nullable(),
      })
      .strict(),
    evidence: z
      .object({
        minimum_count: z.number().int().nonnegative().max(256),
        required_record_types: z.array(z.string()),
        require_registered: z.boolean(),
        require_immutable: z.boolean(),
        require_provenance: z.boolean(),
      })
      .strict(),
    dependencies: z
      .object({
        required_status: z.enum(["accepted", "effective", "typed"]),
        missing_dependency: z.enum(["reject", "pending", "quarantine"]),
        parents_establish_order: z.boolean(),
      })
      .strict(),
    guards: z.array(guardSchema),
    transition: z
      .object({
        resource_type: z.string().min(1),
        from: z.array(z.string().min(1)).min(1),
        pending_state: z.string().nullable(),
        contested_state: z.string().nullable(),
        effective_state: z.string().min(1),
        terminal: z.boolean(),
      })
      .strict(),
    effect_gates: z.array(guardSchema),
    conflict: z
      .object({
        conflict_class: identifier,
        key: z.array(z.string().startsWith("/")).min(1),
        policy: z.enum(["reject_later", "accept_both", "supersede", "merge", "require_resolution", "select_by_rule"]),
        selector: z.string().nullable(),
        merge_reducer_id: identifier.nullable(),
      })
      .strict(),
    veto: z.record(z.string(), z.unknown()).nullable(),
  })
  .strict();

const rulesetSchema = z
  .object({
    protocol_version: z.literal(DAP_PROTOCOL_VERSION),
    language_version: z.literal(DAP_RULE_LANGUAGE_VERSION),
    ruleset_id: rulesetId,
    district_id: z.string().regex(/^district:[A-Za-z0-9._:-]+$/),
    ruleset_version: z.number().int().positive().safe(),
    predecessor_ruleset_id: rulesetId.nullable(),
    effective_from_checkpoint: identifier.nullable(),
    numeric_scale: z.number().int().positive().max(1_000_000_000),
    defaults: z
      .object({
        unknown_fact: z.enum(["reject", "pending", "quarantine"]),
        missing_dependency: z.enum(["reject", "pending", "quarantine"]),
        unregistered_operation: z.literal("reject"),
        conflict_policy: z.enum(["reject_later", "accept_both", "supersede", "merge", "require_resolution", "select_by_rule"]),
        authority_aggregation: z.enum(["non_aggregating", "maximum", "sum_capped", "independent_threshold", "issuer_diversity"]),
        wildcard_scope: z.boolean(),
      })
      .strict(),
    capabilities: z.array(
      z.object({ capability_id: z.string().regex(capabilityPattern), implies: z.array(z.string().regex(capabilityPattern)) }).strict(),
    ),
    decision_rules: z.array(z.record(z.string(), z.unknown())),
    operation_rules: z.array(operationRuleSchema).min(1),
    reason_catalog: z.array(
      z
        .object({
          code: z.string().regex(/^[A-Z][A-Z0-9_]*$/),
          default_disposition: z.enum([
            "ACCEPTED_EFFECTIVE",
            "ACCEPTED_PENDING",
            "ACCEPTED_CONTESTED",
            "REJECTED",
            "QUARANTINED",
            "SUPERSEDED",
            "DUPLICATE",
          ]),
          description: z.string().min(1),
        })
        .strict(),
    ),
  })
  .strict();

const genesisPayloadSchema = z
  .object({
    district_name: z.string().min(1).max(200),
    district_time: timestamp,
    genesis_identity: z
      .object({
        identity_id: identifier,
        signing_key_id: identifier,
        actor_class: z.enum(ACTOR_CLASSES),
        public_key: z.string().length(43).regex(/^[A-Za-z0-9_-]+$/),
      })
      .strict(),
    initial_membership: z
      .object({
        status: z.literal("active"),
        roles: z.array(z.string().min(1)),
      })
      .strict(),
    initial_authorities: z.array(z.record(z.string(), z.unknown())).min(1),
    initial_resources: z.record(z.string(), z.unknown()),
    ruleset: rulesetSchema,
  })
  .strict();

const payloadSchemas: Record<string, z.ZodTypeAny> = {
  IDENTITY_DECLARE: z.object({ identity_id: identifier, actor_class: z.enum(ACTOR_CLASSES) }),
  KEY_DELEGATE: z.object({ identity_id: identifier, key_id: identifier, public_key: z.string().length(43) }),
  KEY_REVOKE: z.object({ key_id: identifier, revocation_reason: z.string().min(1), effective_time: timestamp }),
  MEMBERSHIP_NOMINATE: z.object({ identity_id: identifier, roles: z.array(z.string()) }),
  MEMBERSHIP_ATTEST: z.object({ identity_id: identifier }),
  MEMBERSHIP_ACTIVATE: z.object({ identity_id: identifier, roles: z.array(z.string()) }),
  MEMBERSHIP_SUSPEND: z.object({ identity_id: identifier, reason: z.string().min(1) }),
  MEMBERSHIP_REMOVE: z.object({ identity_id: identifier, reason: z.string().min(1) }),
  AUTHORITY_GRANT: z.object({
    authority_id: identifier,
    recipient_id: identifier,
    capabilities: z.array(z.string().regex(capabilityPattern)).min(1),
    scope: z.array(z.string()).min(1),
    weight: z.number().int().nonnegative(),
    delegable: z.boolean(),
    maximum_delegation_depth: z.number().int().nonnegative(),
    valid_from: timestamp.nullable(),
    expires_at: timestamp.nullable(),
  }),
  AUTHORITY_DELEGATE: z.object({
    authority_id: identifier,
    parent_authority_id: identifier,
    recipient_id: identifier,
    capabilities: z.array(z.string().regex(capabilityPattern)).min(1),
    scope: z.array(z.string()).min(1),
    weight: z.number().int().nonnegative(),
    delegable: z.boolean(),
    maximum_delegation_depth: z.number().int().nonnegative(),
    valid_from: timestamp.nullable(),
    expires_at: timestamp.nullable(),
  }),
  AUTHORITY_REVOKE: z.object({ authority_id: identifier, reason: z.string().min(1) }),
  PROPOSAL_CREATE: z.object({
    proposal_id: identifier,
    proposal_version: z.number().int().positive(),
    title: z.string().min(1),
    body: z.string().min(1),
    decision_rule_id: identifier.nullable().optional(),
    review_period_seconds: z.number().int().nonnegative().optional(),
  }),
  PROPOSAL_AMEND: z.object({
    proposal_id: identifier,
    proposal_version: z.number().int().positive(),
    title: z.string().min(1).optional(),
    body: z.string().min(1).optional(),
  }),
  PROPOSAL_SUBMIT: z.object({
    proposal_id: identifier,
    proposal_version: z.number().int().positive(),
    decision_rule_id: identifier,
    review_period_seconds: z.number().int().nonnegative(),
  }),
  PROPOSAL_REVIEW_BEGIN: z.object({
    proposal_id: identifier,
    proposal_version: z.number().int().positive(),
    submission_operation_id: operationId,
    decision_rule_id: identifier,
    review_period_seconds: z.number().int().nonnegative(),
  }),
  PROPOSAL_ACCEPT: z.object({
    proposal_id: identifier,
    proposal_version: z.number().int().positive(),
    decision_rule_id: identifier,
  }),
  PROPOSAL_REJECT: z.object({
    proposal_id: identifier,
    proposal_version: z.number().int().positive(),
    decision_rule_id: identifier,
  }),
  PROPOSAL_ACTIVATE: z.object({
    proposal_id: identifier,
    proposal_version: z.number().int().positive(),
  }),
  PROPOSAL_ARCHIVE: z.object({ proposal_id: identifier, reason: z.string().min(1) }),
  VOTE_CAST: z.object({
    proposal_id: identifier,
    proposal_version: z.number().int().positive(),
    choice: z.string().min(1),
    decision_rule_id: identifier,
    weight: z.number().int().positive().optional(),
  }),
  VETO_ATTACH: z.object({ veto_class: z.string().min(1), reason: z.string().min(1), requested_remedy: z.string().min(1) }),
  VETO_RESOLVE: z.object({ veto_operation_id: operationId, resulting_state: z.string().min(1) }),
  EVIDENCE_REGISTER: z.object({ record_type: z.string().min(1), content_hash: z.string().min(1), provenance: z.record(z.string(), z.unknown()) }),
  CHECKPOINT_FINALIZE: z.object({
    checkpoint_id: identifier,
    district_time: timestamp,
    history_root_before: z.string().startsWith("history:z"),
    state_root_before: z.string().startsWith("state:z"),
    parent_checkpoint_id: identifier.nullable(),
  }),
  RULESET_PROPOSE: z.object({ ruleset: rulesetSchema }),
  RULESET_ACTIVATE: z.object({ ruleset_id: rulesetId }),
  OPERATION_REVERSE: z.object({
    operation_id: operationId,
    reason: z.string().min(1),
    compensation: z.discriminatedUnion("kind", [
      z.object({ kind: z.literal("void_vote") }),
      z.object({ kind: z.literal("revoke_authority") }),
      z.object({ kind: z.literal("resolve_veto"), resulting_state: z.string().min(1) }),
      z.object({ kind: z.literal("set_proposal_state"), resulting_state: z.string().min(1) }),
    ]),
  }),
};

function stage(stageNumber: number, name: string, result: string): DapStageResult {
  return { stage: stageNumber, name, result };
}

function unique<T>(values: T[]) {
  return [...new Set(values)];
}

async function validationResult(
  operation: DapOperationEnvelope,
  disposition: DapDisposition,
  stages: DapStageResult[],
  reasons: string[],
  pending: string[],
  before: StoredDapState | null,
  after: StoredDapState | null,
): Promise<DapValidationResult> {
  const result: DapValidationResult = {
    operation_id: operation.operation_id,
    disposition,
    stage_results: stages,
    reason_codes: unique(reasons),
    pending_conditions: unique(pending),
    ruleset_id: operation.ruleset_id,
    history_root_before: before?.history_root ?? null,
    history_root_after: after?.history_root ?? before?.history_root ?? null,
    state_root_before: before?.state_root ?? null,
    state_root_after: after?.state_root ?? before?.state_root ?? null,
    accepted_operation_count: after?.accepted_count ?? before?.accepted_count ?? 0,
    effective_at_checkpoint: disposition === "ACCEPTED_EFFECTIVE" ? before?.state.district.current_checkpoint_id ?? null : null,
    evaluated_at: new Date().toISOString(),
    validator_signature: null,
  };
  const validatorId = env.DAP_VALIDATOR_ID?.trim();
  const signingKeyId = env.DAP_VALIDATOR_KEY_ID?.trim();
  const publicKey = env.DAP_VALIDATOR_PUBLIC_KEY?.trim();
  const privateKey = env.DAP_VALIDATOR_PRIVATE_KEY_PKCS8?.trim();
  if (!validatorId || !signingKeyId || !publicKey || !privateKey) return result;
  const body = { ...result } as Record<string, unknown>;
  delete body.validator_signature;
  const digest = await domainDigest("DAP-DISPOSITION-0.2", body);
  const value = await signEd25519Pkcs8(privateKey, digest);
  if (!(await verifyEd25519(publicKey, value, digest))) throw new Error("DAP validator signing configuration is invalid");
  result.validator_signature = {
    validator_id: validatorId,
    signing_key_id: signingKeyId,
    algorithm: "Ed25519",
    public_key: publicKey,
    value,
  };
  return result;
}

function rulesetSemanticErrors(ruleset: DapRuleset) {
  const errors: string[] = [];
  const uniqueIds = (values: string[], code: string) => {
    if (new Set(values).size !== values.length) errors.push(code);
  };
  const capabilityIds = ruleset.capabilities.map((item) => item.capability_id);
  const reasonCodes = ruleset.reason_catalog.map((item) => item.code);
  const capabilities = new Set(capabilityIds);
  const reasons = new Set(reasonCodes);
  const operationTypes = new Set(ruleset.operation_rules.map((item) => item.operation_type));
  uniqueIds(capabilityIds, "ERR_RULESET_CAPABILITY_DUPLICATE");
  uniqueIds(ruleset.operation_rules.map((item) => item.operation_type), "ERR_RULESET_OPERATION_DUPLICATE");
  uniqueIds(reasonCodes, "ERR_RULESET_REASON_DUPLICATE");
  const visiting = new Set<string>();
  const visited = new Set<string>();
  const visit = (capabilityId: string) => {
    if (visiting.has(capabilityId)) {
      errors.push("ERR_RULESET_CAPABILITY_CYCLE");
      return;
    }
    if (visited.has(capabilityId)) return;
    visiting.add(capabilityId);
    const declaration = ruleset.capabilities.find((item) => item.capability_id === capabilityId);
    declaration?.implies.forEach(visit);
    visiting.delete(capabilityId);
    visited.add(capabilityId);
  };
  for (const capability of ruleset.capabilities) {
    if (capability.implies.some((item) => !capabilities.has(item))) errors.push("ERR_RULESET_CAPABILITY_REFERENCE");
    visit(capability.capability_id);
  }
  for (const rule of ruleset.operation_rules) {
    if (!capabilities.has(rule.required_capability)) errors.push("ERR_RULESET_CAPABILITY_REFERENCE");
    for (const guard of [...rule.guards, ...rule.effect_gates]) {
      if (!reasons.has(guard.reason_code)) errors.push("ERR_RULESET_REASON_REFERENCE");
    }
    const veto = rule.veto as Record<string, unknown> | null;
    if (veto?.enabled === true) {
      if (typeof veto.resolution_operation_type !== "string" || !operationTypes.has(veto.resolution_operation_type)) {
        errors.push("ERR_RULESET_VETO_RESOLUTION");
      }
      if (!Number.isSafeInteger(veto.review_period_seconds) || Number(veto.review_period_seconds) <= 0) {
        errors.push("ERR_RULESET_VETO_PERIOD");
      }
    }
  }
  return unique(errors);
}

function exactRatioSatisfied(value: number, base: number, ratio: { numerator: number; denominator: number }) {
  if (![value, base, ratio.numerator, ratio.denominator].every(Number.isSafeInteger) || ratio.denominator <= 0) return false;
  return BigInt(value) * BigInt(ratio.denominator) >= BigInt(base) * BigInt(ratio.numerator);
}

function proposalDecisionReasons(operation: DapOperationEnvelope, before: StoredDapState, ruleset: DapRuleset) {
  if (!["PROPOSAL_ACCEPT", "PROPOSAL_REJECT"].includes(operation.operation_type)) return [];
  const proposal = before.state.proposals[operation.target.resource_id];
  const decision = ruleset.decision_rules.find((item) => item.decision_rule_id === operation.payload.decision_rule_id);
  if (!proposal || !decision || decision.weighting !== "one_member_one_vote") return ["ERR_DECISION_RULE"];
  const eligible = Object.values(before.state.memberships).filter((membership) => membership.status === "active").length;
  const votes = Object.values(before.state.votes).filter(
    (vote) =>
      vote.effective &&
      vote.proposal_id === proposal.proposal_id &&
      vote.proposal_version === Number(operation.payload.proposal_version) &&
      vote.decision_rule_id === decision.decision_rule_id &&
      before.state.memberships[vote.voter_id]?.status === "active",
  );
  const uniqueVotes = [...new Map(votes.map((vote) => [vote.voter_id, vote])).values()];
  if (!exactRatioSatisfied(uniqueVotes.length, eligible, decision.quorum)) return ["ERR_QUORUM"];
  const approve = uniqueVotes.filter((vote) => vote.choice === "approve").length;
  const reject = uniqueVotes.filter((vote) => vote.choice === "reject").length;
  const nonAbstaining = uniqueVotes.filter((vote) => vote.choice !== "abstain").length;
  const approvalBase = decision.approval.base === "eligible"
    ? eligible
    : decision.approval.base === "participating"
      ? uniqueVotes.length
      : nonAbstaining;
  const tied = approve === reject;
  const approved = exactRatioSatisfied(approve, approvalBase, decision.approval.ratio) && !(tied && decision.tie_policy === "reject");
  if (operation.operation_type === "PROPOSAL_ACCEPT" && !approved) return ["ERR_DECISION_REJECTED"];
  if (operation.operation_type === "PROPOSAL_REJECT" && approved) return ["ERR_DECISION_APPROVED"];
  return [];
}

async function validateIdentifiers(operation: DapOperationEnvelope) {
  try {
    const identifiers = await operationIdentifiers(operation);
    const reasons: string[] = [];
    if (identifiers.operationId !== operation.operation_id) reasons.push("ERR_OPERATION_ID");
    if (identifiers.contentHash !== operation.content_hash) reasons.push("ERR_CONTENT_HASH");
    return { ...identifiers, reasons };
  } catch {
    return { digest: new Uint8Array(), operationId: "", contentHash: "", reasons: ["ERR_CANONICAL_ENCODING"] };
  }
}

async function rejectAndStore(
  operation: DapOperationEnvelope,
  disposition: "REJECTED" | "QUARANTINED",
  stages: DapStageResult[],
  reasons: string[],
  pending: string[],
  before: StoredDapState | null,
) {
  const result = await validationResult(operation, disposition, stages, reasons, pending, before, null);
  await saveRejectedDapSubmission(operation, result);
  return result;
}

function validateTypePayload(operation: DapOperationEnvelope) {
  const schema = payloadSchemas[operation.operation_type];
  if (!schema) return operation.operation_type.startsWith("district:") ? [] : ["ERR_OPERATION_TYPE"];
  return schema.safeParse(operation.payload).success ? [] : ["ERR_SCHEMA"];
}

async function coreSemanticReasons(
  operation: DapOperationEnvelope,
  before: StoredDapState,
  ruleset: DapRuleset,
) {
  const reasons: string[] = [];
  const payload = operation.payload;
  const targetMatches = (field: string) => payload[field] === operation.target.resource_id;
  if (operation.operation_type === "IDENTITY_DECLARE" && !targetMatches("identity_id")) reasons.push("ERR_TARGET");
  if (["KEY_DELEGATE", "KEY_REVOKE"].includes(operation.operation_type) && !targetMatches("key_id")) reasons.push("ERR_TARGET");
  if (operation.operation_type.startsWith("PROPOSAL_") && !targetMatches("proposal_id")) reasons.push("ERR_TARGET");
  if (operation.operation_type === "VOTE_CAST" && !targetMatches("proposal_id")) reasons.push("ERR_TARGET");
  if (["AUTHORITY_GRANT", "AUTHORITY_DELEGATE", "AUTHORITY_REVOKE"].includes(operation.operation_type) && !targetMatches("authority_id")) {
    reasons.push("ERR_TARGET");
  }
  if (["MEMBERSHIP_NOMINATE", "MEMBERSHIP_ATTEST", "MEMBERSHIP_ACTIVATE", "MEMBERSHIP_SUSPEND", "MEMBERSHIP_REMOVE"].includes(operation.operation_type)) {
    if (!targetMatches("identity_id")) reasons.push("ERR_TARGET");
  }
  if (operation.operation_type === "KEY_DELEGATE") {
    if (!before.state.identities[String(payload.identity_id)]) reasons.push("ERR_IDENTITY_UNKNOWN");
    if (before.state.keys[String(payload.key_id)]) reasons.push("ERR_KEY_EXISTS");
  }
  if (operation.operation_type === "KEY_REVOKE" && !before.state.keys[String(payload.key_id)]) reasons.push("ERR_UNKNOWN_KEY");
  if (operation.operation_type === "AUTHORITY_GRANT") {
    if (!before.state.identities[String(payload.recipient_id)]) reasons.push("ERR_IDENTITY_UNKNOWN");
    if (before.state.authorities[String(payload.authority_id)]) reasons.push("ERR_AUTHORITY_EXISTS");
    if (Number(payload.weight) > ruleset.numeric_scale) reasons.push("ERR_AUTHORITY_WEIGHT");
  }
  if (operation.operation_type === "AUTHORITY_DELEGATE") {
    const parent = before.state.authorities[String(payload.parent_authority_id)];
    if (!parent) reasons.push("ERR_AUTHORITY_UNKNOWN");
    else {
      if (parent.status !== "active" || !parent.delegable) reasons.push("ERR_AUTHORITY_DELEGATION");
      if (parent.recipient_id !== operation.author.identity_id) reasons.push("ERR_AUTHORITY_RECIPIENT");
      if (Number(payload.weight) > parent.weight) reasons.push("ERR_AUTHORITY_WEIGHT");
      if ((parent.delegation_depth + 1) >= parent.maximum_delegation_depth) reasons.push("ERR_DELEGATION_DEPTH");
      if (!Array.isArray(payload.capabilities) || payload.capabilities.some((item) => !parent.capabilities.includes(String(item)))) {
        reasons.push("ERR_CAPABILITY");
      }
      if (scopeContains(parent.scope, payload.scope, ruleset.defaults.wildcard_scope) !== true) reasons.push("ERR_SCOPE");
      if (parent.expires_at && typeof payload.expires_at === "string" && payload.expires_at > parent.expires_at) reasons.push("ERR_AUTHORITY_TIME");
    }
    if (!before.state.identities[String(payload.recipient_id)]) reasons.push("ERR_IDENTITY_UNKNOWN");
    if (before.state.authorities[String(payload.authority_id)]) reasons.push("ERR_AUTHORITY_EXISTS");
  }
  if (operation.operation_type === "AUTHORITY_REVOKE" && !before.state.authorities[String(payload.authority_id)]) {
    reasons.push("ERR_AUTHORITY_UNKNOWN");
  }
  if (operation.operation_type === "PROPOSAL_AMEND") {
    const proposal = before.state.proposals[operation.target.resource_id];
    if (proposal && Number(payload.proposal_version) !== proposal.current_version + 1) reasons.push("ERR_PROPOSAL_VERSION");
  }
  if (operation.operation_type === "PROPOSAL_SUBMIT") {
    const proposal = before.state.proposals[operation.target.resource_id];
    if (proposal && Number(payload.proposal_version) !== proposal.current_version) reasons.push("ERR_PROPOSAL_VERSION");
    if (!ruleset.decision_rules.some((decision) => decision.decision_rule_id === payload.decision_rule_id)) reasons.push("ERR_DECISION_RULE");
  }
  if (["PROPOSAL_REVIEW_BEGIN", "PROPOSAL_ACCEPT", "PROPOSAL_REJECT", "PROPOSAL_ACTIVATE"].includes(operation.operation_type)) {
    const proposal = before.state.proposals[operation.target.resource_id];
    if (!proposal || Number(payload.proposal_version) !== proposal.current_version) reasons.push("ERR_PROPOSAL_VERSION");
  }
  if (operation.operation_type === "PROPOSAL_REVIEW_BEGIN") {
    const submission = await getAcceptedDapOperation(String(payload.submission_operation_id));
    if (
      !submission ||
      submission.envelope.operation_type !== "PROPOSAL_SUBMIT" ||
      submission.envelope.target.resource_id !== operation.target.resource_id ||
      submission.envelope.payload.proposal_version !== payload.proposal_version ||
      submission.envelope.payload.decision_rule_id !== payload.decision_rule_id ||
      submission.envelope.payload.review_period_seconds !== payload.review_period_seconds
    ) reasons.push("ERR_PROPOSAL_SUBMISSION");
    else {
      const reviewCompleteAt = Date.parse(submission.envelope.created_at) + Number(payload.review_period_seconds) * 1000;
      if (!Number.isFinite(reviewCompleteAt) || Date.parse(before.state.district.district_time) < reviewCompleteAt) {
        reasons.push("ERR_REVIEW_PERIOD");
      }
    }
  }
  reasons.push(...proposalDecisionReasons(operation, before, ruleset));
  if (operation.operation_type === "VOTE_CAST") {
    const proposal = before.state.proposals[String(payload.proposal_id)];
    const decision = ruleset.decision_rules.find((item) => item.decision_rule_id === payload.decision_rule_id);
    if (!proposal || proposal.current_version !== Number(payload.proposal_version)) reasons.push("ERR_PROPOSAL_VERSION");
    if (!decision || !decision.ballot.includes(String(payload.choice))) reasons.push("ERR_BALLOT_CHOICE");
    if (decision?.weighting === "one_member_one_vote" && payload.weight !== undefined && payload.weight !== 1) reasons.push("ERR_VOTE_WEIGHT");
    const priorVote = Object.values(before.state.votes).find(
      (vote) =>
        vote.proposal_id === payload.proposal_id &&
        vote.proposal_version === payload.proposal_version &&
        vote.voter_id === operation.author.identity_id &&
        vote.decision_rule_id === payload.decision_rule_id,
    );
    if (priorVote && decision?.duplicate_vote_policy === "reject_later") reasons.push("ERR_DUPLICATE_VOTE");
  }
  if (operation.operation_type === "VETO_ATTACH" && !before.state.proposals[operation.target.resource_id]) reasons.push("ERR_TARGET");
  if (operation.operation_type === "VETO_RESOLVE" && !before.state.vetoes[String(payload.veto_operation_id)]) reasons.push("ERR_VETO_UNKNOWN");
  if (operation.operation_type === "CHECKPOINT_FINALIZE" && !targetMatches("checkpoint_id")) reasons.push("ERR_TARGET");
  if (operation.operation_type === "OPERATION_REVERSE") {
    if (!targetMatches("operation_id")) reasons.push("ERR_TARGET");
    const target = await getAcceptedDapOperation(String(payload.operation_id));
    if (!target || target.disposition !== "ACCEPTED_EFFECTIVE") reasons.push("ERR_REVERSE_TARGET");
    else if (target.envelope.operation_type === "DISTRICT_CREATE") reasons.push("ERR_CONSTITUTIONAL_CONSTRAINT");
    else if (before.state.reversals?.[target.envelope.operation_id]) reasons.push("ERR_ALREADY_REVERSED");
    else {
      const compensation = payload.compensation as Record<string, unknown>;
      const compatible =
        (compensation.kind === "void_vote" && target.envelope.operation_type === "VOTE_CAST") ||
        (compensation.kind === "revoke_authority" && ["AUTHORITY_GRANT", "AUTHORITY_DELEGATE"].includes(target.envelope.operation_type)) ||
        (compensation.kind === "resolve_veto" && target.envelope.operation_type === "VETO_ATTACH") ||
        (compensation.kind === "set_proposal_state" && target.envelope.operation_type.startsWith("PROPOSAL_"));
      if (!compatible) reasons.push("ERR_REVERSE_COMPENSATION");
      const accepted = await getAcceptedDapOperations(operation.district_id);
      const liveDependent = accepted.some(
        (candidate) =>
          !before.state.reversals?.[candidate.envelope.operation_id] &&
          (candidate.envelope.dependencies.includes(target.envelope.operation_id) ||
            candidate.envelope.parent_ids.includes(target.envelope.operation_id)),
      );
      if (liveDependent) reasons.push("ERR_REVERSE_DEPENDENT_OPERATION");
    }
  }
  if (operation.operation_type === "RULESET_PROPOSE") {
    const proposed = payload.ruleset as DapRuleset;
    if ((await rulesetIdentifier(proposed)) !== proposed.ruleset_id) reasons.push("ERR_RULESET_ID");
    if (proposed.district_id !== operation.district_id || proposed.predecessor_ruleset_id !== ruleset.ruleset_id) reasons.push("ERR_RULESET_BINDING");
    if (proposed.ruleset_version !== ruleset.ruleset_version + 1) reasons.push("ERR_RULESET_VERSION");
    reasons.push(...rulesetSemanticErrors(proposed));
  }
  if (operation.operation_type === "RULESET_ACTIVATE") {
    const proposed = await getDapRuleset(String(payload.ruleset_id));
    if (!proposed || proposed.predecessor_ruleset_id !== ruleset.ruleset_id) reasons.push("ERR_RULESET_BINDING");
  }
  if (operation.operation_type === "CHECKPOINT_FINALIZE") {
    if (payload.history_root_before !== before.history_root || payload.state_root_before !== before.state_root) reasons.push("ERR_CHECKPOINT_ROOT");
    if (payload.parent_checkpoint_id !== before.state.district.current_checkpoint_id) reasons.push("ERR_CHECKPOINT_PARENT");
    if (String(payload.district_time) < before.state.district.district_time) reasons.push("ERR_CHECKPOINT_TIME");
  }
  return unique(reasons);
}

async function validateGenesis(operation: DapOperationEnvelope, stages: DapStageResult[]) {
  const parsed = genesisPayloadSchema.safeParse(operation.payload);
  if (!parsed.success || operation.operation_type !== "DISTRICT_CREATE") {
    stages.push(stage(2, "schema", "INVALID_SCHEMA"));
    return rejectAndStore(operation, "REJECTED", stages, ["ERR_SCHEMA"], [], null);
  }
  const payload = parsed.data;
  const ruleset = payload.ruleset as DapRuleset;
  const reasons: string[] = [];
  if (ruleset.district_id !== operation.district_id || ruleset.ruleset_id !== operation.ruleset_id) reasons.push("ERR_RULESET_BINDING");
  if (ruleset.ruleset_version !== 1 || ruleset.predecessor_ruleset_id !== null) reasons.push("ERR_GENESIS_RULESET");
  if ((await rulesetIdentifier(ruleset)) !== ruleset.ruleset_id) reasons.push("ERR_RULESET_ID");
  reasons.push(...rulesetSemanticErrors(ruleset));
  if (payload.genesis_identity.identity_id !== operation.author.identity_id) reasons.push("ERR_GENESIS_IDENTITY");
  if (payload.genesis_identity.signing_key_id !== operation.author.signing_key_id) reasons.push("ERR_GENESIS_KEY");
  if (payload.genesis_identity.actor_class !== operation.author.actor_class) reasons.push("ERR_AGENT_RESTRICTION");
  if (operation.target.resource_type !== "district" || operation.target.resource_id !== operation.district_id) reasons.push("ERR_DISTRICT");
  if (operation.target.scope_path.length !== 1 || operation.target.scope_path[0] !== operation.district_id) reasons.push("ERR_SCOPE");
  if (operation.causal.author_sequence !== 1 || operation.causal.previous_author_operation !== null) reasons.push("ERR_AUTHOR_CHAIN");
  if (operation.parent_ids.length || operation.dependencies.length) reasons.push("ERR_CAUSAL");
  if (operation.causal.logical_time.tie_breaker !== operation.author.identity_id) reasons.push("ERR_LOGICAL_TIME");
  for (const authorityValue of payload.initial_authorities) {
    const authority = authorityValue as Record<string, unknown>;
    if (authority.recipient_id !== operation.author.identity_id) reasons.push("ERR_GENESIS_AUTHORITY_RECIPIENT");
    if (!Array.isArray(authority.scope) || authority.scope[0] !== operation.district_id) reasons.push("ERR_SCOPE");
    if (!Number.isSafeInteger(authority.weight) || Number(authority.weight) > ruleset.numeric_scale) reasons.push("ERR_AUTHORITY_WEIGHT");
    if (!Array.isArray(authority.capabilities) || authority.capabilities.some((item) => !ruleset.capabilities.some((cap) => cap.capability_id === item))) {
      reasons.push("ERR_CAPABILITY");
    }
  }
  stages.push(stage(2, "schema", reasons.length ? "INVALID_SCHEMA" : "VALID_SCHEMA"));
  const identifiers = await validateIdentifiers(operation);
  reasons.push(...identifiers.reasons);
  stages.push(stage(3, "identifier", identifiers.reasons.length ? "INVALID_IDENTIFIER" : "VALID_IDENTIFIER"));
  const signatureValid = identifiers.digest.length === 32 && (await verifyEd25519(payload.genesis_identity.public_key, operation.signature.value, identifiers.digest));
  if (!signatureValid) reasons.push("ERR_SIGNATURE");
  stages.push(stage(4, "cryptographic", signatureValid ? "VALID_SIGNATURE" : "INVALID_SIGNATURE"));
  if (reasons.length) return rejectAndStore(operation, "REJECTED", stages, reasons, [], null);
  stages.push(
    stage(5, "replay", "NEW_OPERATION"),
    stage(6, "district", "VALID_GENESIS_DISTRICT"),
    stage(7, "causal", "VALID_CAUSAL"),
    stage(8, "membership", "BOOTSTRAP_MEMBERSHIP"),
    stage(9, "authority", "BOOTSTRAP_AUTHORITY"),
    stage(10, "scope", "VALID_SCOPE"),
    stage(11, "ruleset", "VALID_GENESIS_RULESET"),
    stage(12, "state_transition", "VALID_STATE_TRANSITION"),
    stage(13, "conflict", "NO_CONFLICT"),
  );
  const state = createGenesisState(operation);
  const history = await historyRoot([operation.operation_id]);
  const stateHash = await stateRoot(state);
  const stored: StoredDapState = {
    district_id: operation.district_id,
    history_root: history,
    state_root: stateHash,
    accepted_count: 1,
    state,
    updated_at: new Date().toISOString(),
  };
  const result = await validationResult(operation, "ACCEPTED_EFFECTIVE", [...stages, stage(14, "classification", "ACCEPTED_EFFECTIVE")], [], [], null, stored);
  await createDapGenesis(operation, ruleset, stored, result);
  return result;
}

type GuardOutcome = {
  rejects: string[];
  quarantines: string[];
  pending: string[];
  contested: string[];
  superseded: string[];
};

function applyGuard(guard: DapGuard, context: unknown, outcome: GuardOutcome) {
  const value = evaluateExpression(guard.assert, context);
  if (value === true) return;
  const action = value === UNKNOWN ? guard.on_unknown : guard.on_false;
  if (action === "reject") outcome.rejects.push(guard.reason_code);
  else if (action === "quarantine") outcome.quarantines.push(guard.reason_code);
  else if (action === "pending") outcome.pending.push(guard.pending_condition ?? guard.reason_code);
  else if (action === "contested") outcome.contested.push(guard.reason_code);
  else if (action === "supersede") outcome.superseded.push(guard.reason_code);
}

function conflictKey(rule: DapOperationRule, context: unknown) {
  const values = rule.conflict.key.map((path) => resolvePath(context, path));
  return values.includes(UNKNOWN) ? null : JSON.stringify(values);
}

async function validateNormalOperation(
  operation: DapOperationEnvelope,
  stages: DapStageResult[],
  district: NonNullable<Awaited<ReturnType<typeof getDapDistrict>>>,
) {
  const before = await getDapState(operation.district_id);
  if (!before) return rejectAndStore(operation, "QUARANTINED", stages, ["ERR_STATE_UNAVAILABLE"], [], null);
  const ruleset = await getDapRuleset(operation.ruleset_id);
  if (!ruleset || district.active_ruleset_id !== operation.ruleset_id) {
    stages.push(stage(6, "district", "ERR_RULESET_BINDING"));
    return rejectAndStore(operation, "REJECTED", stages, ["ERR_RULESET_BINDING"], [], before);
  }
  const rule = ruleset.operation_rules.find((item) => item.operation_type === operation.operation_type);
  const schemaReasons = validateTypePayload(operation);
  if (!rule) schemaReasons.push("ERR_OPERATION_TYPE");
  stages.push(stage(2, "schema", schemaReasons.length ? "INVALID_SCHEMA" : "VALID_SCHEMA"));
  if (schemaReasons.length) return rejectAndStore(operation, "REJECTED", stages, schemaReasons, [], before);

  const identifiers = await validateIdentifiers(operation);
  stages.push(stage(3, "identifier", identifiers.reasons.length ? "INVALID_IDENTIFIER" : "VALID_IDENTIFIER"));
  if (identifiers.reasons.length) return rejectAndStore(operation, "REJECTED", stages, identifiers.reasons, [], before);

  const key = before.state.keys[operation.author.signing_key_id];
  const cryptoReasons: string[] = [];
  if (!key) cryptoReasons.push("ERR_UNKNOWN_KEY");
  else if (key.identity_id !== operation.author.identity_id) cryptoReasons.push("ERR_KEY_IDENTITY");
  else if (before.state.identities[operation.author.identity_id]?.actor_class !== operation.author.actor_class) {
    cryptoReasons.push("ERR_AGENT_RESTRICTION");
  }
  else if (key.status === "revoked") cryptoReasons.push("ERR_REVOKED_KEY");
  else if (key.status === "expired") cryptoReasons.push("ERR_EXPIRED_KEY");
  else if (key.valid_from && before.state.district.district_time < key.valid_from) cryptoReasons.push("ERR_KEY_NOT_YET_VALID");
  else if (key.expires_at && before.state.district.district_time >= key.expires_at) cryptoReasons.push("ERR_EXPIRED_KEY");
  else if (!(await verifyEd25519(key.public_key, operation.signature.value, identifiers.digest))) cryptoReasons.push("ERR_SIGNATURE");
  stages.push(stage(4, "cryptographic", cryptoReasons.length ? "INVALID_SIGNATURE" : "VALID_SIGNATURE"));
  if (cryptoReasons.length) return rejectAndStore(operation, cryptoReasons.includes("ERR_UNKNOWN_KEY") ? "QUARANTINED" : "REJECTED", stages, cryptoReasons, [], before);

  const existing = await getDapSubmission(operation.operation_id);
  if (existing) {
    stages.push(stage(5, "replay", "EXACT_DUPLICATE"));
    return validationResult(operation, "DUPLICATE", [...stages, stage(14, "classification", "DUPLICATE")], [], [], before, before);
  }
  const lastKeyOperation = await getLastKeyOperation(operation.district_id, operation.author.signing_key_id);
  const replayReasons: string[] = [];
  if (lastKeyOperation) {
    if (operation.causal.author_sequence !== lastKeyOperation.author_sequence + 1) replayReasons.push("ERR_AUTHOR_CHAIN");
    if (operation.causal.previous_author_operation !== lastKeyOperation.operation_id) replayReasons.push("ERR_AUTHOR_CHAIN");
  } else if (operation.causal.author_sequence !== 1 || operation.causal.previous_author_operation !== null) {
    replayReasons.push("ERR_AUTHOR_CHAIN");
  }
  stages.push(stage(5, "replay", replayReasons.length ? "AUTHOR_CHAIN_CONFLICT" : "NEW_OPERATION"));
  if (replayReasons.length) return rejectAndStore(operation, "REJECTED", stages, replayReasons, [], before);

  stages.push(stage(6, "district", "VALID_DISTRICT"));
  const accepted = await getAcceptedDapOperations(operation.district_id);
  const acceptedById = new Map(accepted.map((item) => [item.envelope.operation_id, item]));
  const causalReasons: string[] = [];
  for (const parent of operation.parent_ids) if (!acceptedById.has(parent)) causalReasons.push("ERR_PARENT_MISSING");
  const missingDependencies = operation.dependencies.filter((dependency) => {
    const candidate = acceptedById.get(dependency);
    if (!candidate) return true;
    return rule!.dependencies.required_status === "effective" && candidate.disposition !== "ACCEPTED_EFFECTIVE";
  });
  const causalReferences = [
    ...operation.parent_ids,
    ...operation.dependencies,
    ...(operation.causal.previous_author_operation ? [operation.causal.previous_author_operation] : []),
  ];
  if (causalReferences.some((id) => {
    const referenced = acceptedById.get(id);
    return referenced && referenced.envelope.causal.logical_time.lamport >= operation.causal.logical_time.lamport;
  })) causalReasons.push("ERR_LOGICAL_TIME");
  if (operation.causal.logical_time.tie_breaker !== operation.author.identity_id) causalReasons.push("ERR_LOGICAL_TIME");
  stages.push(stage(7, "causal", causalReasons.length ? "INVALID_CAUSAL" : "VALID_CAUSAL"));
  if (causalReasons.length) return rejectAndStore(operation, "REJECTED", stages, causalReasons, [], before);

  const outcome: GuardOutcome = { rejects: [], quarantines: [], pending: [], contested: [], superseded: [] };
  outcome.rejects.push(...(await coreSemanticReasons(operation, before, ruleset)));
  if (missingDependencies.length) {
    if (rule!.dependencies.missing_dependency === "reject") outcome.rejects.push("ERR_DEPENDENCY_MISSING");
    else if (rule!.dependencies.missing_dependency === "quarantine") outcome.quarantines.push("ERR_DEPENDENCY_MISSING");
    else outcome.pending.push("DEPENDENCY_MISSING");
  }

  const membership = before.state.memberships[operation.author.identity_id];
  const membershipValid = Boolean(membership && rule!.allowed_membership_statuses.includes(membership.status));
  if (!membershipValid) outcome.rejects.push("ERR_MEMBERSHIP");
  if (!rule!.allowed_actor_classes.includes(operation.author.actor_class)) outcome.rejects.push("ERR_AGENT_RESTRICTION");
  stages.push(stage(8, "membership", membershipValid ? "VALID_MEMBERSHIP" : "INVALID_MEMBERSHIP"));

  if (operation.authorization.required_capability !== rule!.required_capability) outcome.rejects.push("ERR_CAPABILITY");
  const authority = resolveAuthority(operation, rule!, ruleset, before.state);
  if (!authority.valid) outcome.rejects.push("ERR_AUTHORITY");
  outcome.rejects.push(...authority.rejectedPaths.map((item) => item.reason_code));
  if (operation.authorization.delegation_chain.some((authorityId) => !before.state.authorities[authorityId])) {
    outcome.rejects.push("ERR_DELEGATION_CHAIN");
  }
  if (authority.acceptedPathIds.some((authorityId) => !operation.authorization.delegation_chain.includes(authorityId))) {
    outcome.rejects.push("ERR_DELEGATION_CHAIN");
  }
  stages.push(stage(9, "authority", authority.valid ? "VALID_AUTHORITY" : "INVALID_AUTHORITY"));
  stages.push(stage(10, "scope", authority.rejectedPaths.some((item) => item.reason_code === "ERR_SCOPE") ? "INVALID_SCOPE" : "VALID_SCOPE"));

  if (operation.evidence_ids.length < rule!.evidence.minimum_count) outcome.rejects.push("ERR_EVIDENCE_REQUIRED");
  if (rule!.evidence.require_registered) {
    for (const evidenceId of operation.evidence_ids) if (!before.state.evidence[evidenceId]) outcome.quarantines.push("ERR_EVIDENCE_UNKNOWN");
  }

  const context = buildPolicyContext(before.state, ruleset, operation, accepted, authority);
  if (rule!.authority.conflict_of_interest_guard !== null) {
    const conflictValue = evaluateExpression(rule!.authority.conflict_of_interest_guard, context);
    if (conflictValue === false) outcome.rejects.push("ERR_CONFLICT_OF_INTEREST");
    else if (conflictValue === UNKNOWN) outcome.quarantines.push("ERR_CONFLICT_OF_INTEREST_UNKNOWN");
  }
  for (const guard of rule!.guards) applyGuard(guard, context, outcome);
  stages.push(stage(11, "ruleset", outcome.rejects.length || outcome.quarantines.length ? "INVALID_RULESET" : "VALID_RULESET"));

  const currentTarget = resourceFromState(before.state, operation);
  const currentState = currentTarget && typeof currentTarget === "object"
    ? "state" in currentTarget
      ? String((currentTarget as { state: unknown }).state)
      : "status" in currentTarget
        ? String((currentTarget as { status: unknown }).status)
        : "present"
    : "absent";
  const transitionValid = rule!.transition.resource_type === operation.target.resource_type && rule!.transition.from.includes(currentState);
  if (!transitionValid) outcome.rejects.push("ERR_STATE_TRANSITION");
  stages.push(stage(12, "state_transition", transitionValid ? "VALID_STATE_TRANSITION" : "INVALID_STATE_TRANSITION"));

  const candidateConflictKey = conflictKey(rule!, context);
  const conflicts: AcceptedDapOperation[] = [];
  for (const existingOperation of accepted) {
    if (before.state.reversals?.[existingOperation.envelope.operation_id]) continue;
    const existingRule = ruleset.operation_rules.find((item) => item.operation_type === existingOperation.envelope.operation_type);
    if (!existingRule || existingRule.conflict.conflict_class !== rule!.conflict.conflict_class) continue;
    const existingAuthority = resolveAuthority(existingOperation.envelope, existingRule, ruleset, before.state);
    const existingContext = buildPolicyContext(before.state, ruleset, existingOperation.envelope, accepted, existingAuthority);
    if (candidateConflictKey && conflictKey(existingRule, existingContext) === candidateConflictKey) conflicts.push(existingOperation);
  }
  if (conflicts.length) {
    if (rule!.conflict.policy === "reject_later") outcome.rejects.push("ERR_CONFLICT");
    else if (rule!.conflict.policy === "require_resolution") outcome.contested.push("CONFLICT_REQUIRES_RESOLUTION");
    else if (rule!.conflict.policy === "supersede") outcome.superseded.push("SUPERSEDED_BY_RULE");
    else if (["merge", "select_by_rule"].includes(rule!.conflict.policy)) outcome.quarantines.push("ERR_REDUCER_UNAVAILABLE");
  }
  stages.push(stage(13, "conflict", conflicts.length ? "CONFLICT_FOUND" : "NO_CONFLICT"));

  const districtTime = before.state.district.district_time;
  if (operation.expires_at && districtTime >= operation.expires_at) outcome.rejects.push("ERR_EXPIRED");
  else if (operation.valid_from && districtTime < operation.valid_from) outcome.pending.push("VALID_FROM_NOT_REACHED");
  for (const guard of rule!.effect_gates) applyGuard(guard, context, outcome);

  const activeVetoes = Object.values(before.state.vetoes).filter(
    (veto) => veto.target_id === operation.target.resource_id && veto.status === "active",
  );
  if (activeVetoes.length && rule!.veto) outcome.contested.push("ACTIVE_VETO");

  let disposition: DapDisposition = "ACCEPTED_EFFECTIVE";
  if (outcome.quarantines.length) disposition = "QUARANTINED";
  else if (outcome.rejects.length) disposition = "REJECTED";
  else if (outcome.superseded.length) disposition = "SUPERSEDED";
  else if (outcome.contested.length) disposition = "ACCEPTED_CONTESTED";
  else if (outcome.pending.length) disposition = "ACCEPTED_PENDING";
  const reasons = unique([...outcome.rejects, ...outcome.quarantines, ...outcome.contested, ...outcome.superseded]);
  if (disposition === "REJECTED" || disposition === "QUARANTINED") {
    stages.push(stage(14, "classification", disposition));
    return rejectAndStore(operation, disposition, stages, reasons, outcome.pending, before);
  }

  const acceptedCandidate: AcceptedDapOperation = {
    envelope: operation,
    disposition: disposition as AcceptedDapOperation["disposition"],
  };
  const reduced = reduceAcceptedOperations([...accepted, acceptedCandidate]);
  const operationIds = reduced.ordered.map((item) => item.envelope.operation_id);
  const after: StoredDapState = {
    district_id: operation.district_id,
    history_root: await historyRoot(operationIds),
    state_root: await stateRoot(reduced.state),
    accepted_count: operationIds.length,
    state: reduced.state,
    updated_at: new Date().toISOString(),
  };
  stages.push(stage(14, "classification", disposition));
  const result = await validationResult(operation, disposition, stages, reasons, outcome.pending, before, after);
  const persisted = await acceptDapOperation(operation, before, after, result);
  if (!persisted) {
    return rejectAndStore(operation, "QUARANTINED", stages, ["ERR_CONCURRENT_STATE"], [], await getDapState(operation.district_id));
  }
  return result;
}

export type DapSubmissionOutcome = {
  ok: boolean;
  httpStatus: number;
  result?: DapValidationResult;
  errors?: Array<{ path: string; message: string }>;
};

export async function submitDapOperation(input: unknown): Promise<DapSubmissionOutcome> {
  const parsed = envelopeSchema.safeParse(input);
  if (!parsed.success) {
    return {
      ok: false,
      httpStatus: 400,
      errors: parsed.error.issues.map((issue) => ({ path: issue.path.join("."), message: issue.message })),
    };
  }
  const operation = parsed.data as DapOperationEnvelope;
  const stages = [stage(1, "protocol", "VALID_PROTOCOL")];
  const duplicateIdentifiers = await validateIdentifiers(operation);
  if (!duplicateIdentifiers.reasons.length) {
    const existing = await getDapSubmission(operation.operation_id);
    if (existing && canonicalEncode(existing.operation) === canonicalEncode(operation)) {
      const current = await getDapState(operation.district_id);
      const duplicate = await validationResult(
        operation,
        "DUPLICATE",
        [
          ...stages,
          stage(2, "schema", "VALID_SCHEMA"),
          stage(3, "identifier", "VALID_IDENTIFIER"),
          stage(4, "cryptographic", "PREVIOUSLY_VERIFIED_SIGNATURE"),
          stage(5, "replay", "EXACT_DUPLICATE"),
          stage(14, "classification", "DUPLICATE"),
        ],
        [],
        [],
        current,
        current,
      );
      return { ok: true, httpStatus: 200, result: duplicate };
    }
  }
  const district = await getDapDistrict(operation.district_id);
  let result: DapValidationResult;
  if (!district) result = await validateGenesis(operation, stages);
  else if (operation.operation_type === "DISTRICT_CREATE") {
    result = await rejectAndStore(operation, "REJECTED", stages, ["ERR_DISTRICT_EXISTS"], [], await getDapState(operation.district_id));
  } else result = await validateNormalOperation(operation, stages, district);
  return {
    ok: ["ACCEPTED_EFFECTIVE", "ACCEPTED_PENDING", "ACCEPTED_CONTESTED", "SUPERSEDED", "DUPLICATE"].includes(result.disposition),
    httpStatus: result.disposition === "DUPLICATE" ? 200 : result.disposition.startsWith("ACCEPTED") || result.disposition === "SUPERSEDED" ? 202 : result.disposition === "QUARANTINED" ? 409 : 422,
    result,
  };
}

export async function reconstructDapDistrict(districtId: string) {
  const stored = await getDapState(districtId);
  if (!stored) return null;
  const accepted = await getAcceptedDapOperations(districtId);
  const reduced = reduceAcceptedOperations(accepted);
  const operationIds = reduced.ordered.map((item) => item.envelope.operation_id);
  const reconstructedHistoryRoot = await historyRoot(operationIds);
  const reconstructedStateRoot = await stateRoot(reduced.state);
  return {
    district_id: districtId,
    accepted_operation_count: accepted.length,
    stored_history_root: stored.history_root,
    reconstructed_history_root: reconstructedHistoryRoot,
    history_root_matches: stored.history_root === reconstructedHistoryRoot,
    stored_state_root: stored.state_root,
    reconstructed_state_root: reconstructedStateRoot,
    state_root_matches: stored.state_root === reconstructedStateRoot,
    state: reduced.state,
    ordered_operation_ids: operationIds,
  };
}

export async function getDapOperationStatus(operationId: string) {
  const submission = await getDapSubmission(operationId);
  const accepted = await getAcceptedDapOperation(operationId);
  return submission ? { ...submission, accepted: Boolean(accepted) } : null;
}
