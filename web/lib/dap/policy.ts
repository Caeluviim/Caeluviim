import { canonicalEncode } from "./canonical";
import type {
  AcceptedDapOperation,
  DapAuthorityState,
  DapDistrictState,
  DapExpression,
  DapOperationEnvelope,
  DapOperationRule,
  DapRuleset,
} from "./types";

export const UNKNOWN = Symbol("DAP_UNKNOWN");
export type DapPolicyValue = unknown | typeof UNKNOWN;

const timestampPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;

function decodePointerToken(token: string) {
  return token.replaceAll("~1", "/").replaceAll("~0", "~");
}

export function resolvePath(context: unknown, pointer: string): DapPolicyValue {
  if (!pointer.startsWith("/")) return UNKNOWN;
  let current = context;
  for (const rawToken of pointer.slice(1).split("/")) {
    const token = decodePointerToken(rawToken);
    if (current === null || typeof current !== "object" || !(token in current)) return UNKNOWN;
    current = (current as Record<string, unknown>)[token];
  }
  return current;
}

function isScalar(value: unknown) {
  return value === null || ["boolean", "number", "string"].includes(typeof value);
}

function sameScalarType(left: unknown, right: unknown) {
  if (!isScalar(left) || !isScalar(right)) return false;
  if (left === null || right === null) return left === null && right === null;
  return typeof left === typeof right;
}

function compareOrdered(left: unknown, right: unknown) {
  if (Number.isSafeInteger(left) && Number.isSafeInteger(right)) return Math.sign((left as number) - (right as number));
  if (typeof left === "string" && typeof right === "string" && timestampPattern.test(left) && timestampPattern.test(right)) {
    return left === right ? 0 : left < right ? -1 : 1;
  }
  return UNKNOWN;
}

function valueKey(value: unknown) {
  return isScalar(value) ? canonicalEncode(value) : UNKNOWN;
}

function safeIntegerBinary(left: unknown, right: unknown, operator: (a: number, b: number) => number) {
  if (!Number.isSafeInteger(left) || !Number.isSafeInteger(right)) return UNKNOWN;
  const value = operator(left as number, right as number);
  return Number.isSafeInteger(value) && !Object.is(value, -0) ? value : UNKNOWN;
}

export function scopeContains(grantScope: unknown, targetScope: unknown, wildcardEnabled = false) {
  if (!Array.isArray(grantScope) || !Array.isArray(targetScope)) return UNKNOWN;
  if (grantScope.some((item) => typeof item !== "string") || targetScope.some((item) => typeof item !== "string")) return UNKNOWN;
  for (let index = 0; index < grantScope.length; index += 1) {
    const segment = grantScope[index];
    if (segment === "**") return wildcardEnabled && index === grantScope.length - 1;
    if (index >= targetScope.length) return false;
    if (segment === "*") {
      if (!wildcardEnabled) return false;
    } else if (segment !== targetScope[index]) {
      return false;
    }
  }
  return true;
}

export function evaluateExpression(expression: DapExpression, context: unknown): DapPolicyValue {
  if (expression === null || ["boolean", "string", "number"].includes(typeof expression)) return expression;
  if (Array.isArray(expression)) return expression.map((item) => evaluateExpression(item, context));
  if (!expression || typeof expression !== "object") return UNKNOWN;
  const entries = Object.entries(expression);
  if (entries.length !== 1) return UNKNOWN;
  const [operator, argument] = entries[0];
  if (operator === "path") return typeof argument === "string" ? resolvePath(context, argument) : UNKNOWN;
  if (operator === "exists") return evaluateExpression(argument, context) !== UNKNOWN;
  if (operator === "not") {
    const value = evaluateExpression(argument, context);
    return value === UNKNOWN || typeof value !== "boolean" ? UNKNOWN : !value;
  }
  if (operator === "all" || operator === "any") {
    if (!Array.isArray(argument)) return UNKNOWN;
    const values = argument.map((item) => evaluateExpression(item, context));
    if (values.some((value) => value !== UNKNOWN && typeof value !== "boolean")) return UNKNOWN;
    if (operator === "all") {
      if (values.includes(false)) return false;
      return values.includes(UNKNOWN) ? UNKNOWN : true;
    }
    if (values.includes(true)) return true;
    return values.includes(UNKNOWN) ? UNKNOWN : false;
  }
  if (operator === "count") {
    const value = evaluateExpression(argument, context);
    return Array.isArray(value) ? value.length : UNKNOWN;
  }
  if (operator === "distinct_count") {
    if (!Array.isArray(argument) || argument.length !== 2 || typeof argument[1] !== "string") return UNKNOWN;
    const collection = evaluateExpression(argument[0], context);
    if (!Array.isArray(collection)) return UNKNOWN;
    const values = collection.map((item) => {
      if (!item || typeof item !== "object" || !(argument[1] as string in item)) return UNKNOWN;
      return valueKey((item as Record<string, unknown>)[argument[1] as string]);
    });
    if (values.includes(UNKNOWN)) return UNKNOWN;
    return new Set(values).size;
  }
  if (!Array.isArray(argument) || argument.length !== 2) return UNKNOWN;
  const left = evaluateExpression(argument[0], context);
  const right = evaluateExpression(argument[1], context);
  if (left === UNKNOWN || right === UNKNOWN) return UNKNOWN;
  if (operator === "eq" || operator === "neq") {
    if (!sameScalarType(left, right)) return UNKNOWN;
    return operator === "eq" ? left === right : left !== right;
  }
  if (["lt", "lte", "gt", "gte"].includes(operator)) {
    const comparison = compareOrdered(left, right);
    if (comparison === UNKNOWN) return UNKNOWN;
    if (operator === "lt") return comparison < 0;
    if (operator === "lte") return comparison <= 0;
    if (operator === "gt") return comparison > 0;
    return comparison >= 0;
  }
  if (operator === "in") {
    if (!Array.isArray(right) || !isScalar(left)) return UNKNOWN;
    const needle = valueKey(left);
    const values = right.map(valueKey);
    return values.includes(UNKNOWN) ? UNKNOWN : values.includes(needle);
  }
  if (operator === "contains_all" || operator === "subset") {
    if (!Array.isArray(left) || !Array.isArray(right)) return UNKNOWN;
    const leftKeys = left.map(valueKey);
    const rightKeys = right.map(valueKey);
    if (leftKeys.includes(UNKNOWN) || rightKeys.includes(UNKNOWN)) return UNKNOWN;
    const candidate = operator === "contains_all" ? rightKeys : leftKeys;
    const container = new Set(operator === "contains_all" ? leftKeys : rightKeys);
    return candidate.every((item) => container.has(item));
  }
  if (operator === "scope_contains") {
    return scopeContains(left, right, (context as { candidate?: { wildcard_scope?: boolean } })?.candidate?.wildcard_scope === true);
  }
  if (operator === "add") return safeIntegerBinary(left, right, (a, b) => a + b);
  if (operator === "sub") return safeIntegerBinary(left, right, (a, b) => a - b);
  if (operator === "mul") return safeIntegerBinary(left, right, (a, b) => a * b);
  if (operator === "min") return safeIntegerBinary(left, right, Math.min);
  if (operator === "max") return safeIntegerBinary(left, right, Math.max);
  return UNKNOWN;
}

export function ratioSatisfied(actualWeight: number, baseWeight: number, ratio: { numerator: number; denominator: number }) {
  if (![actualWeight, baseWeight, ratio.numerator, ratio.denominator].every(Number.isSafeInteger)) return UNKNOWN;
  if (actualWeight < 0 || baseWeight < 0 || ratio.numerator < 0 || ratio.denominator <= 0) return UNKNOWN;
  if (baseWeight === 0) return false;
  return BigInt(actualWeight) * BigInt(ratio.denominator) >= BigInt(baseWeight) * BigInt(ratio.numerator);
}

function capabilityIncludes(ruleset: DapRuleset, granted: string, required: string, visiting = new Set<string>()): boolean {
  if (granted === required) return true;
  if (visiting.has(granted)) return false;
  visiting.add(granted);
  const declaration = ruleset.capabilities.find((item) => item.capability_id === granted);
  return declaration?.implies.some((item) => capabilityIncludes(ruleset, item, required, visiting)) ?? false;
}

function authorityTimeValid(authority: DapAuthorityState, districtTime: string) {
  if (authority.valid_from && districtTime < authority.valid_from) return false;
  if (authority.expires_at && districtTime >= authority.expires_at) return false;
  return true;
}

export function aggregateAuthority(
  paths: DapAuthorityState[],
  mode: DapOperationRule["authority"]["aggregation"],
  numericScale: number,
  minimumWeight: number,
) {
  const roots = new Map<string, number>();
  for (const path of paths) roots.set(path.root_issuer_id, Math.max(roots.get(path.root_issuer_id) ?? 0, path.weight));
  const weights = [...roots.values()];
  const maximum = weights.length ? Math.max(...weights) : 0;
  if (mode === "maximum" || mode === "non_aggregating") {
    return { weight: maximum, rootIssuers: roots.size, qualifyingRootIssuers: weights.filter((weight) => weight >= minimumWeight).length };
  }
  if (mode === "sum_capped" || mode === "issuer_diversity") {
    return {
      weight: Math.min(weights.reduce((total, weight) => total + weight, 0), numericScale),
      rootIssuers: roots.size,
      qualifyingRootIssuers: weights.filter((weight) => weight >= minimumWeight).length,
    };
  }
  const qualifying = weights.filter((weight) => weight >= minimumWeight);
  return {
    weight: qualifying.length ? Math.min(...qualifying) : 0,
    rootIssuers: roots.size,
    qualifyingRootIssuers: qualifying.length,
  };
}

export type AuthorityResolution = {
  valid: boolean;
  acceptedPathIds: string[];
  rejectedPaths: Array<{ authority_id: string; reason_code: string }>;
  effectiveWeight: number;
  rootIssuers: number;
};

export function resolveAuthority(
  operation: DapOperationEnvelope,
  rule: DapOperationRule,
  ruleset: DapRuleset,
  state: DapDistrictState,
): AuthorityResolution {
  if (!rule.authority.required) {
    return { valid: true, acceptedPathIds: [], rejectedPaths: [], effectiveWeight: 0, rootIssuers: 0 };
  }
  const accepted: DapAuthorityState[] = [];
  const rejectedPaths: AuthorityResolution["rejectedPaths"] = [];
  for (const authorityId of operation.authorization.authority_ids) {
    const authority = state.authorities[authorityId];
    let reason: string | null = null;
    if (!authority) reason = "ERR_AUTHORITY_UNKNOWN";
    else if (authority.status !== "active") reason = "ERR_AUTHORITY_INACTIVE";
    else if (authority.recipient_id !== operation.author.identity_id) reason = "ERR_AUTHORITY_RECIPIENT";
    else if (!authorityTimeValid(authority, state.district.district_time)) reason = "ERR_AUTHORITY_TIME";
    else if (authority.delegation_depth > rule.authority.maximum_delegation_depth) reason = "ERR_DELEGATION_DEPTH";
    else if (!authority.capabilities.some((capability) => capabilityIncludes(ruleset, capability, rule.required_capability))) {
      reason = "ERR_CAPABILITY";
    } else if (
      rule.authority.scope_mode === "contain_target" &&
      scopeContains(authority.scope, operation.target.scope_path, ruleset.defaults.wildcard_scope) !== true
    ) {
      reason = "ERR_SCOPE";
    } else if (
      rule.authority.scope_mode === "exact_target" &&
      canonicalEncode(authority.scope) !== canonicalEncode(operation.target.scope_path)
    ) {
      reason = "ERR_SCOPE";
    }
    if (reason) rejectedPaths.push({ authority_id: authorityId, reason_code: reason });
    else accepted.push(authority);
  }
  const aggregate = aggregateAuthority(accepted, rule.authority.aggregation, ruleset.numeric_scale, rule.authority.minimum_weight);
  const enoughWeight = aggregate.weight >= rule.authority.minimum_weight;
  const enoughIssuers =
    !["independent_threshold", "issuer_diversity"].includes(rule.authority.aggregation) ||
    aggregate.qualifyingRootIssuers >= rule.authority.minimum_root_issuers;
  return {
    valid: accepted.length > 0 && enoughWeight && enoughIssuers,
    acceptedPathIds: accepted.map((item) => item.authority_id).sort(),
    rejectedPaths,
    effectiveWeight: aggregate.weight,
    rootIssuers: aggregate.rootIssuers,
  };
}

export function resourceFromState(state: DapDistrictState, operation: DapOperationEnvelope) {
  if (operation.target.resource_type === "district") return state.district;
  if (operation.target.resource_type === "identity") return state.identities[operation.target.resource_id] ?? null;
  if (operation.target.resource_type === "key") return state.keys[operation.target.resource_id] ?? null;
  if (operation.target.resource_type === "proposal") return state.proposals[operation.target.resource_id] ?? null;
  if (operation.target.resource_type === "authority") return state.authorities[operation.target.resource_id] ?? null;
  if (operation.target.resource_type === "membership") return state.memberships[operation.target.resource_id] ?? null;
  if (operation.target.resource_type === "evidence") return state.evidence[operation.target.resource_id] ?? null;
  if (operation.target.resource_type === "document") return state.documents[operation.target.resource_id] ?? null;
  if (operation.target.resource_type === "checkpoint") return state.checkpoints[operation.target.resource_id] ?? null;
  if (operation.target.resource_type === "veto") return state.vetoes[operation.target.resource_id] ?? null;
  return null;
}

export function deriveDecisionFacts(state: DapDistrictState, ruleset: DapRuleset, operation: DapOperationEnvelope) {
  const decisions: Record<string, Record<string, unknown>> = {};
  const proposalId = String(operation.payload.proposal_id ?? operation.target.resource_id);
  const proposalVersion = Number(operation.payload.proposal_version ?? state.proposals[proposalId]?.current_version ?? 0);
  for (const rule of ruleset.decision_rules) {
    const eligible = Object.values(state.memberships).filter((membership) => membership.status === "active");
    const currentVotes = Object.values(state.votes).filter(
      (vote) => vote.proposal_id === proposalId && vote.proposal_version === proposalVersion && vote.decision_rule_id === rule.decision_rule_id,
    );
    const latestByVoter = new Map<string, (typeof currentVotes)[number]>();
    for (const vote of currentVotes) latestByVoter.set(vote.voter_id, vote);
    const votes = [...latestByVoter.values()];
    const eligibleWeight = rule.weighting === "one_member_one_vote" ? eligible.length : ruleset.numeric_scale * eligible.length;
    const participatingWeight = votes.reduce((sum, vote) => sum + vote.weight, 0);
    const affirmativeWeight = votes.filter((vote) => ["approve", "resolve_veto", "accept"].includes(vote.choice)).reduce((sum, vote) => sum + vote.weight, 0);
    const abstainingWeight = votes.filter((vote) => vote.choice === "abstain").reduce((sum, vote) => sum + vote.weight, 0);
    const approvalBase =
      rule.approval.base === "eligible"
        ? eligibleWeight
        : rule.approval.base === "participating"
          ? participatingWeight
          : participatingWeight - abstainingWeight;
    const quorumPassed = ratioSatisfied(participatingWeight, eligibleWeight, rule.quorum) === true;
    const approvalPassed = ratioSatisfied(affirmativeWeight, approvalBase, rule.approval.ratio) === true;
    decisions[rule.decision_rule_id.replace(/^rule:/, "").replaceAll("-", "_")] = {
      passed: quorumPassed && approvalPassed,
      quorum_passed: quorumPassed,
      approval_passed: approvalPassed,
      eligible_weight: eligibleWeight,
      participating_weight: participatingWeight,
      affirmative_weight: affirmativeWeight,
      abstaining_weight: abstainingWeight,
    };
  }
  return decisions;
}

export function buildPolicyContext(
  state: DapDistrictState,
  ruleset: DapRuleset,
  operation: DapOperationEnvelope,
  acceptedOperations: AcceptedDapOperation[],
  authority: AuthorityResolution,
) {
  const target = resourceFromState(state, operation);
  const reviewSeconds = Number(operation.payload.review_period_seconds ?? 0);
  const created = Date.parse(operation.created_at);
  const reviewEndsAt = Number.isSafeInteger(reviewSeconds) && reviewSeconds >= 0 && Number.isFinite(created)
    ? new Date(created + reviewSeconds * 1000).toISOString().replace(".000Z", "Z")
    : undefined;
  return {
    operation,
    pre_state: { ...state, target: target ?? undefined },
    history: {
      accepted_operation_ids: acceptedOperations.map((item) => item.envelope.operation_id),
    },
    checkpoint: {
      checkpoint_id: state.district.current_checkpoint_id,
      district_time: state.district.district_time,
    },
    derived: {
      membership_status: state.memberships[operation.author.identity_id]?.status,
      authority_weight: authority.effectiveWeight,
      accepted_authority_path_ids: authority.acceptedPathIds,
      review_ends_at: reviewEndsAt,
      decisions: deriveDecisionFacts(state, ruleset, operation),
      author_has_target_conflict: false,
    },
    candidate: {
      wildcard_scope: ruleset.defaults.wildcard_scope,
      required_capability: operation.authorization.required_capability,
      member: state.memberships[operation.author.identity_id],
    },
  };
}
