import type {
  AcceptedDapOperation,
  ActorClass,
  DapAuthorityState,
  DapDistrictState,
  DapMembershipState,
  DapOperationEnvelope,
  DapProposalState,
} from "./types";

function cloneState(state: DapDistrictState) {
  return structuredClone(state);
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

function asString(value: unknown, fallback = "") {
  return typeof value === "string" ? value : fallback;
}

function asInteger(value: unknown, fallback = 0) {
  return Number.isSafeInteger(value) ? (value as number) : fallback;
}

function asStringArray(value: unknown) {
  return Array.isArray(value) && value.every((item) => typeof item === "string") ? [...value] : [];
}

function ordering(left: AcceptedDapOperation, right: AcceptedDapOperation) {
  const lamport = left.envelope.causal.logical_time.lamport - right.envelope.causal.logical_time.lamport;
  if (lamport) return lamport;
  const encoder = new TextEncoder();
  const a = encoder.encode(left.envelope.operation_id);
  const b = encoder.encode(right.envelope.operation_id);
  const length = Math.min(a.length, b.length);
  for (let index = 0; index < length; index += 1) {
    if (a[index] !== b[index]) return a[index] - b[index];
  }
  return a.length - b.length;
}

export function orderAcceptedOperations(operations: AcceptedDapOperation[]) {
  const byId = new Map(operations.map((item) => [item.envelope.operation_id, item]));
  const outgoing = new Map<string, Set<string>>();
  const indegree = new Map<string, number>();
  for (const operation of operations) {
    indegree.set(operation.envelope.operation_id, 0);
    outgoing.set(operation.envelope.operation_id, new Set());
  }
  for (const operation of operations) {
    const before = new Set([
      ...operation.envelope.dependencies,
      ...operation.envelope.parent_ids,
      ...(operation.envelope.causal.previous_author_operation ? [operation.envelope.causal.previous_author_operation] : []),
    ]);
    for (const predecessor of before) {
      if (!byId.has(predecessor)) continue;
      const edges = outgoing.get(predecessor)!;
      if (edges.has(operation.envelope.operation_id)) continue;
      edges.add(operation.envelope.operation_id);
      indegree.set(operation.envelope.operation_id, (indegree.get(operation.envelope.operation_id) ?? 0) + 1);
    }
  }
  const ready = operations.filter((item) => indegree.get(item.envelope.operation_id) === 0).sort(ordering);
  const ordered: AcceptedDapOperation[] = [];
  while (ready.length) {
    const next = ready.shift()!;
    ordered.push(next);
    for (const target of outgoing.get(next.envelope.operation_id) ?? []) {
      const remaining = (indegree.get(target) ?? 0) - 1;
      indegree.set(target, remaining);
      if (remaining === 0) {
        ready.push(byId.get(target)!);
        ready.sort(ordering);
      }
    }
  }
  if (ordered.length !== operations.length) throw new Error("ERR_CAUSAL_CYCLE");
  return ordered;
}

export function createGenesisState(operation: DapOperationEnvelope): DapDistrictState {
  const payload = operation.payload;
  const identity = asRecord(payload.genesis_identity);
  const identityId = asString(identity.identity_id);
  const keyId = asString(identity.signing_key_id);
  const actorClass = asString(identity.actor_class, operation.author.actor_class) as ActorClass;
  const membership = asRecord(payload.initial_membership);
  const initialAuthorities = Array.isArray(payload.initial_authorities) ? payload.initial_authorities.map(asRecord) : [];
  const initialResources = asRecord(payload.initial_resources);
  const proposalRecords = asRecord(initialResources.proposals);
  const proposals: Record<string, DapProposalState> = {};
  for (const [proposalId, rawProposal] of Object.entries(proposalRecords)) {
    const proposal = asRecord(rawProposal);
    const version = asInteger(proposal.current_version, 1);
    proposals[proposalId] = {
      proposal_id: proposalId,
      state: asString(proposal.state, "draft"),
      title: asString(proposal.title),
      body: asString(proposal.body),
      current_version: version,
      decision_rule_id: typeof proposal.decision_rule_id === "string" ? proposal.decision_rule_id : null,
      review_period_seconds: Number.isSafeInteger(proposal.review_period_seconds) ? (proposal.review_period_seconds as number) : null,
      submitted_at: typeof proposal.submitted_at === "string" ? proposal.submitted_at : null,
      created_by: asString(proposal.created_by, identityId),
      versions: [{
        version,
        title: asString(proposal.title),
        body: asString(proposal.body),
        operation_id: operation.operation_id,
      }],
    };
  }
  const authorities: Record<string, DapAuthorityState> = {};
  for (const rawAuthority of initialAuthorities) {
    const authorityId = asString(rawAuthority.authority_id);
    if (!authorityId) continue;
    authorities[authorityId] = {
      authority_id: authorityId,
      issuer_id: asString(rawAuthority.issuer_id, identityId),
      recipient_id: asString(rawAuthority.recipient_id, identityId),
      root_issuer_id: asString(rawAuthority.root_issuer_id, asString(rawAuthority.issuer_id, identityId)),
      capabilities: asStringArray(rawAuthority.capabilities),
      scope: asStringArray(rawAuthority.scope),
      weight: asInteger(rawAuthority.weight),
      delegable: rawAuthority.delegable === true,
      maximum_delegation_depth: asInteger(rawAuthority.maximum_delegation_depth),
      delegation_depth: asInteger(rawAuthority.delegation_depth),
      parent_authority_id: typeof rawAuthority.parent_authority_id === "string" ? rawAuthority.parent_authority_id : null,
      status: "active",
      valid_from: typeof rawAuthority.valid_from === "string" ? rawAuthority.valid_from : null,
      expires_at: typeof rawAuthority.expires_at === "string" ? rawAuthority.expires_at : null,
      created_by_operation: operation.operation_id,
    };
  }
  const membershipState: DapMembershipState = {
    identity_id: identityId,
    status: (asString(membership.status, "active") as DapMembershipState["status"]),
    roles: asStringArray(membership.roles),
    updated_by_operation: operation.operation_id,
  };
  return {
    district: {
      district_id: operation.district_id,
      name: asString(payload.district_name, operation.district_id),
      status: "active",
      protocol_version: "dap/0.2",
      active_ruleset_id: operation.ruleset_id,
      district_time: asString(payload.district_time, operation.created_at),
      current_checkpoint_id: null,
    },
    identities: {
      [identityId]: { identity_id: identityId, actor_class: actorClass, declared_by_operation: operation.operation_id },
    },
    keys: {
      [keyId]: {
        key_id: keyId,
        identity_id: identityId,
        algorithm: "Ed25519",
        public_key: asString(identity.public_key),
        status: "active",
        author_sequence: operation.causal.author_sequence,
        previous_author_operation: operation.operation_id,
        delegated_by: null,
        valid_from: null,
        expires_at: null,
      },
    },
    memberships: { [identityId]: membershipState },
    authorities,
    proposals,
    votes: {},
    vetoes: {},
    evidence: {},
    documents: {},
    checkpoints: {},
    reversals: {},
    federation: {},
    forks: {},
    unresolved_conflicts: {},
  };
}

function applyMembership(state: DapDistrictState, operation: DapOperationEnvelope, status: DapMembershipState["status"]) {
  const identityId = asString(operation.payload.identity_id, operation.target.resource_id);
  const current = state.memberships[identityId];
  state.memberships[identityId] = {
    identity_id: identityId,
    status,
    roles: asStringArray(operation.payload.roles).length ? asStringArray(operation.payload.roles) : current?.roles ?? [],
    updated_by_operation: operation.operation_id,
  };
}

function applyAuthority(state: DapDistrictState, operation: DapOperationEnvelope, delegated: boolean) {
  const payload = operation.payload;
  const authorityId = asString(payload.authority_id, operation.target.resource_id);
  const parentId = typeof payload.parent_authority_id === "string" ? payload.parent_authority_id : null;
  const parent = parentId ? state.authorities[parentId] : null;
  state.authorities[authorityId] = {
    authority_id: authorityId,
    issuer_id: operation.author.identity_id,
    recipient_id: asString(payload.recipient_id),
    root_issuer_id: parent?.root_issuer_id ?? operation.author.identity_id,
    capabilities: asStringArray(payload.capabilities),
    scope: asStringArray(payload.scope),
    weight: asInteger(payload.weight),
    delegable: payload.delegable === true,
    maximum_delegation_depth: asInteger(payload.maximum_delegation_depth),
    delegation_depth: delegated ? (parent?.delegation_depth ?? 0) + 1 : 0,
    parent_authority_id: parentId,
    status: "active",
    valid_from: typeof payload.valid_from === "string" ? payload.valid_from : null,
    expires_at: typeof payload.expires_at === "string" ? payload.expires_at : null,
    created_by_operation: operation.operation_id,
  };
}

function applyProposal(state: DapDistrictState, operation: DapOperationEnvelope) {
  const payload = operation.payload;
  const proposalId = asString(payload.proposal_id, operation.target.resource_id);
  const current = state.proposals[proposalId];
  if (operation.operation_type === "PROPOSAL_CREATE") {
    const version = asInteger(payload.proposal_version, 1);
    state.proposals[proposalId] = {
      proposal_id: proposalId,
      state: "draft",
      title: asString(payload.title),
      body: asString(payload.body),
      current_version: version,
      decision_rule_id: typeof payload.decision_rule_id === "string" ? payload.decision_rule_id : null,
      review_period_seconds: Number.isSafeInteger(payload.review_period_seconds) ? (payload.review_period_seconds as number) : null,
      submitted_at: null,
      created_by: operation.author.identity_id,
      versions: [{ version, title: asString(payload.title), body: asString(payload.body), operation_id: operation.operation_id }],
    };
    return;
  }
  if (!current) return;
  if (operation.operation_type === "PROPOSAL_AMEND") {
    const version = asInteger(payload.proposal_version, current.current_version + 1);
    current.current_version = version;
    current.title = asString(payload.title, current.title);
    current.body = asString(payload.body, current.body);
    current.state = "amended";
    current.versions.push({ version, title: current.title, body: current.body, operation_id: operation.operation_id });
  } else if (operation.operation_type === "PROPOSAL_SUBMIT") {
    current.state = "submitted";
    current.decision_rule_id = asString(payload.decision_rule_id, current.decision_rule_id ?? "") || null;
    current.review_period_seconds = Number.isSafeInteger(payload.review_period_seconds)
      ? (payload.review_period_seconds as number)
      : current.review_period_seconds;
    current.submitted_at = state.district.district_time;
  } else if (operation.operation_type === "PROPOSAL_REVIEW_BEGIN") {
    current.state = "in_review";
    current.decision_rule_id = asString(payload.decision_rule_id, current.decision_rule_id ?? "") || null;
    current.review_period_seconds = asInteger(payload.review_period_seconds, current.review_period_seconds ?? 0);
    current.submitted_at = operation.created_at;
  }
  else if (operation.operation_type === "PROPOSAL_ACCEPT") current.state = "accepted";
  else if (operation.operation_type === "PROPOSAL_REJECT") current.state = "rejected";
  else if (operation.operation_type === "PROPOSAL_ACTIVATE") current.state = "active";
  else if (operation.operation_type === "PROPOSAL_ARCHIVE") current.state = "archived";
}

export function applyEffectiveOperation(state: DapDistrictState, operation: DapOperationEnvelope) {
  const next = cloneState(state);
  if (["MEMBERSHIP_NOMINATE", "MEMBERSHIP_ATTEST"].includes(operation.operation_type)) {
    applyMembership(next, operation, "probationary");
  } else if (operation.operation_type === "MEMBERSHIP_ACTIVATE") applyMembership(next, operation, "active");
  else if (operation.operation_type === "MEMBERSHIP_SUSPEND") applyMembership(next, operation, "suspended");
  else if (operation.operation_type === "MEMBERSHIP_REMOVE") applyMembership(next, operation, "removed");
  else if (operation.operation_type === "IDENTITY_DECLARE") {
    const identityId = asString(operation.payload.identity_id, operation.target.resource_id);
    next.identities[identityId] = {
      identity_id: identityId,
      actor_class: asString(operation.payload.actor_class, operation.author.actor_class) as ActorClass,
      declared_by_operation: operation.operation_id,
    };
  } else if (operation.operation_type === "KEY_DELEGATE") {
    const keyId = asString(operation.payload.key_id, operation.target.resource_id);
    next.keys[keyId] = {
      key_id: keyId,
      identity_id: asString(operation.payload.identity_id),
      algorithm: "Ed25519",
      public_key: asString(operation.payload.public_key),
      status: "active",
      author_sequence: 0,
      previous_author_operation: null,
      delegated_by: operation.author.signing_key_id,
      valid_from: typeof operation.payload.valid_from === "string" ? operation.payload.valid_from : null,
      expires_at: typeof operation.payload.expires_at === "string" ? operation.payload.expires_at : null,
    };
  } else if (operation.operation_type === "KEY_REVOKE") {
    const keyId = asString(operation.payload.key_id, operation.target.resource_id);
    if (next.keys[keyId]) next.keys[keyId].status = "revoked";
  } else if (operation.operation_type === "AUTHORITY_GRANT") applyAuthority(next, operation, false);
  else if (operation.operation_type === "AUTHORITY_DELEGATE") applyAuthority(next, operation, true);
  else if (operation.operation_type === "AUTHORITY_REVOKE") {
    const authorityId = asString(operation.payload.authority_id, operation.target.resource_id);
    if (next.authorities[authorityId]) next.authorities[authorityId].status = "revoked";
  } else if (operation.operation_type.startsWith("PROPOSAL_")) applyProposal(next, operation);
  else if (operation.operation_type === "VOTE_CAST") {
    next.votes[operation.operation_id] = {
      operation_id: operation.operation_id,
      proposal_id: asString(operation.payload.proposal_id, operation.target.resource_id),
      proposal_version: asInteger(operation.payload.proposal_version),
      voter_id: operation.author.identity_id,
      choice: asString(operation.payload.choice),
      decision_rule_id: asString(operation.payload.decision_rule_id),
      weight: asInteger(operation.payload.weight, 1),
      effective: true,
    };
  } else if (operation.operation_type === "VETO_ATTACH") {
    next.vetoes[operation.operation_id] = {
      operation_id: operation.operation_id,
      target_id: operation.target.resource_id,
      veto_class: operation.payload.veto_class,
      reason: operation.payload.reason,
      status: "active",
      attached_by: operation.author.identity_id,
    };
    const proposal = next.proposals[operation.target.resource_id];
    if (proposal) proposal.state = "submitted_contested";
  } else if (operation.operation_type === "VETO_RESOLVE") {
    const vetoId = asString(operation.payload.veto_operation_id);
    if (next.vetoes[vetoId]) next.vetoes[vetoId].status = "resolved";
    const proposal = next.proposals[operation.target.resource_id];
    if (proposal) proposal.state = asString(operation.payload.resulting_state, "submitted");
  } else if (operation.operation_type === "EVIDENCE_REGISTER") {
    next.evidence[operation.target.resource_id] = { ...operation.payload, operation_id: operation.operation_id };
  } else if (["DOCUMENT_PATCH", "DOCUMENT_SNAPSHOT"].includes(operation.operation_type)) {
    next.documents[operation.target.resource_id] = { ...operation.payload, operation_id: operation.operation_id };
  } else if (operation.operation_type === "CHECKPOINT_FINALIZE") {
    const checkpointId = asString(operation.payload.checkpoint_id, operation.target.resource_id);
    next.checkpoints[checkpointId] = { ...operation.payload, operation_id: operation.operation_id };
    next.district.current_checkpoint_id = checkpointId;
    next.district.district_time = asString(operation.payload.district_time, next.district.district_time);
  } else if (operation.operation_type === "RULESET_ACTIVATE") {
    next.district.active_ruleset_id = asString(operation.payload.ruleset_id, next.district.active_ruleset_id);
  } else if (operation.operation_type === "OPERATION_REVERSE") {
    const targetOperationId = asString(operation.payload.operation_id);
    const compensation = asRecord(operation.payload.compensation);
    next.reversals ??= {};
    next.reversals[targetOperationId] = {
      operation_id: operation.operation_id,
      target_operation_id: targetOperationId,
      reason: asString(operation.payload.reason),
      compensation,
    };
    if (compensation.kind === "void_vote") delete next.votes[targetOperationId];
    else if (compensation.kind === "revoke_authority") {
      const authority = Object.values(next.authorities).find((item) => item.created_by_operation === targetOperationId);
      if (authority) authority.status = "revoked";
    } else if (compensation.kind === "resolve_veto") {
      if (next.vetoes[targetOperationId]) next.vetoes[targetOperationId].status = "reversed";
      const targetId = asString(next.vetoes[targetOperationId]?.target_id);
      if (targetId && next.proposals[targetId]) next.proposals[targetId].state = asString(compensation.resulting_state, "submitted");
    } else if (compensation.kind === "set_proposal_state") {
      const proposal = Object.values(next.proposals).find((item) => item.versions.some((version) => version.operation_id === targetOperationId));
      if (proposal) proposal.state = asString(compensation.resulting_state, proposal.state);
    }
  } else if (operation.operation_type === "FORK_DECLARE") {
    next.forks[operation.target.resource_id] = { ...operation.payload, operation_id: operation.operation_id };
  }
  return next;
}

export function reduceAcceptedOperations(operations: AcceptedDapOperation[]) {
  const ordered = orderAcceptedOperations(operations);
  const genesis = ordered.find((item) => item.envelope.operation_type === "DISTRICT_CREATE");
  if (!genesis) throw new Error("ERR_GENESIS_MISSING");
  let state = createGenesisState(genesis.envelope);
  for (const accepted of ordered) {
    if (accepted.envelope.operation_id === genesis.envelope.operation_id) continue;
    if (accepted.disposition === "ACCEPTED_EFFECTIVE") state = applyEffectiveOperation(state, accepted.envelope);
  }
  return { state, ordered };
}
