import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createPublicKey, generateKeyPairSync, randomBytes, sign, verify as verifySignature } from "node:crypto";
import { rm } from "node:fs/promises";
import { after, before, test } from "node:test";
import { fileURLToPath } from "node:url";
import { domainDigest, operationIdentifiers, rulesetIdentifier } from "../lib/dap/reference.mjs";

const baseUrl = "http://127.0.0.1:3210";
const testStatePath = fileURLToPath(
  new URL(`../.wrangler/test-state-${process.pid}`, import.meta.url),
);
let server;
let output = "";
const validatorKeyPair = generateKeyPairSync("ed25519");
const validatorPrivateKeyPkcs8 = validatorKeyPair.privateKey.export({ format: "der", type: "pkcs8" }).toString("base64url");
const validatorPublicKey = createPublicKey(validatorKeyPair.privateKey).export({ format: "der", type: "spki" }).subarray(-32).toString("base64url");

function assertSignedDisposition(result) {
  assert.equal(result.validator_signature?.validator_id, "validator:caeluviim-test");
  assert.equal(result.validator_signature?.signing_key_id, "key:caeluviim-validator-test");
  assert.equal(result.validator_signature?.public_key, validatorPublicKey);
  const body = { ...result };
  delete body.validator_signature;
  const digest = domainDigest("DAP-DISPOSITION-0.2", body);
  assert.equal(
    verifySignature(null, digest, validatorKeyPair.publicKey, Buffer.from(result.validator_signature.value, "base64url")),
    true,
  );
}

async function callMcp(method, params, id = 1) {
  const response = await fetch(`${baseUrl}/mcp`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      accept: "application/json, text/event-stream",
    },
    body: JSON.stringify({ jsonrpc: "2.0", id, method, params }),
  });
  assert.equal(response.status, 200);
  const payload = await response.json();
  assert.equal(payload.error, undefined);
  return payload.result;
}

async function waitForServer() {
  const deadline = Date.now() + 180_000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`${baseUrl}/api/health`);
      if (response.ok) return;
    } catch {
      // The production server is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 300));
  }
  throw new Error(`Production test server did not start.\n${output}`);
}

function dapRule(operationType, capability, from, effectiveState, effectGates = [], resourceType = "proposal") {
  return {
    operation_type: operationType,
    required_capability: capability,
    allowed_actor_classes: ["human_direct"],
    allowed_membership_statuses: ["active"],
    authority: {
      required: true,
      minimum_weight: 1,
      aggregation: "non_aggregating",
      minimum_root_issuers: 1,
      scope_mode: "contain_target",
      jurisdiction_mode: "not_applicable",
      domain_mode: "not_applicable",
      maximum_delegation_depth: 4,
      conflict_of_interest_guard: null,
    },
    evidence: {
      minimum_count: 0,
      required_record_types: [],
      require_registered: true,
      require_immutable: true,
      require_provenance: true,
    },
    dependencies: {
      required_status: "accepted",
      missing_dependency: "reject",
      parents_establish_order: true,
    },
    guards: [],
    transition: {
      resource_type: resourceType,
      from,
      pending_state: operationType === "PROPOSAL_SUBMIT" ? "submitted_pending" : null,
      contested_state: operationType === "PROPOSAL_SUBMIT" ? "submitted_contested" : null,
      effective_state: effectiveState,
      terminal: false,
    },
    effect_gates: effectGates,
    conflict: {
      conflict_class: `conflict:${operationType.toLocaleLowerCase().replaceAll("_", "-")}`,
      key: ["/operation/target/resource_id"],
      policy: "reject_later",
      selector: null,
      merge_reducer_id: null,
    },
    veto: null,
  };
}

function signDapOperation(body, privateKey) {
  const operation = {
    ...body,
    operation_id: `op:z${"1".repeat(43)}`,
    content_hash: `sha256:${"a".repeat(64)}`,
    signature: { algorithm: "Ed25519", value: "A".repeat(86) },
  };
  const identifiers = operationIdentifiers(operation);
  operation.operation_id = identifiers.operationId;
  operation.content_hash = identifiers.contentHash;
  operation.signature.value = sign(null, identifiers.digest, privateKey).toString("base64url");
  return operation;
}

async function postDap(path, operation) {
  const response = await fetch(`${baseUrl}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(operation),
  });
  return { response, body: await response.json() };
}

before(async () => {
  server = spawn("npm", ["run", "dev", "--", "--port", "3210", "--host", "127.0.0.1"], {
    cwd: new URL("../", import.meta.url),
    env: {
      ...process.env,
      WRANGLER_LOG_PATH: ".wrangler/test.log",
      DAP_VALIDATOR_ID: "validator:caeluviim-test",
      DAP_VALIDATOR_KEY_ID: "key:caeluviim-validator-test",
      DAP_VALIDATOR_PUBLIC_KEY: validatorPublicKey,
      DAP_VALIDATOR_PRIVATE_KEY_PKCS8: validatorPrivateKeyPkcs8,
      CAELUVIIM_PERSIST_PATH: testStatePath,
    },
    stdio: ["ignore", "pipe", "pipe"],
    detached: true,
  });
  server.stdout.on("data", (chunk) => {
    output = `${output}${chunk}`.slice(-20_000);
  });
  server.stderr.on("data", (chunk) => {
    output = `${output}${chunk}`.slice(-20_000);
  });
  await waitForServer();
});

after(async () => {
  if (server && !server.killed) {
    try {
      process.kill(-server.pid, "SIGTERM");
    } catch {
      server.kill("SIGTERM");
    }
    await new Promise((resolve) => {
      server.once("exit", resolve);
      setTimeout(resolve, 2_000);
    });
  }
  await rm(testStatePath, { recursive: true, force: true });
});

test("server-renders the collective web service", async () => {
  const response = await fetch(`${baseUrl}/`);
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /<title>Caeluviim — Graph\/Table Response Protocol<\/title>/i);
  assert.match(html, /Source-bound knowledge service/i);
  assert.match(html, /Ground every claim/i);
  assert.match(html, /11(?:<!-- -->)? categories always/i);
  assert.match(html, /Remote AI-platform knowledge and grounding tools/i);
  assert.match(html, /Knowledge graph explorer/i);
  assert.match(html, /Verify authority from signed history/i);
  assert.match(html, /Submit a signed operation/i);
  assert.doesNotMatch(html, /offline fallback|codex-preview|react-loading-skeleton/i);
});

test("exposes agentic MCP graph tools and rejects ungrounded mappings", async () => {
  const initialized = await callMcp("initialize", {
    protocolVersion: "2025-06-18",
    capabilities: {},
    clientInfo: { name: "caeluviim-integration-test", version: "1.0" },
  });
  assert.equal(initialized.serverInfo.name, "caeluviim-source-bound-knowledge-graph");

  const listed = await callMcp("tools/list", {}, 2);
  const toolNames = listed.tools.map((tool) => tool.name);
  assert.deepEqual(
    [
      "explore_topic_coverage",
      "fetch_knowledge_record",
      "get_knowledge_neighborhood",
      "get_dap_history",
      "get_dap_operation_disposition",
      "get_protocol_schema",
      "ingest_knowledge_record",
      "list_dap_districts",
      "link_knowledge_records",
      "map_grounded_response",
      "query_language_force",
      "reconstruct_dap_district",
      "record_language_act",
      "record_operative_effect",
      "search_knowledge",
      "submit_signed_dap_operation",
    ].sort(),
    [...toolNames].sort(),
  );

  const fixtureTopic = `plasmapheresis-test-${Date.now()}`;
  const ingest = await callMcp(
    "tools/call",
    {
      name: "ingest_knowledge_record",
      arguments: {
        recordType: "Process",
        label: "Plasma separation integration fixture",
        content: "Synthetic process node used only to verify the provenance contract.",
        domains: ["biology", "medicine"],
        topics: [fixtureTopic, "plasma separation"],
        sourceTitle: "Caeluviim integration fixture",
        sourceUrl: "https://example.test/caeluviim-fixture",
        sourceLocator: "fixture paragraph 1",
        sourceExcerpt: "Synthetic excerpt used only to verify source-bound ingestion.",
        constructionRule: "Treat as an integration fixture, not medical evidence.",
      },
    },
    3,
  );
  assert.equal(ingest.structuredContent.persisted, true);
  const record = ingest.structuredContent.record;
  assert.match(record.id, /^urn:caeluviim:knowledge:sha256:[a-f0-9]{64}$/);
  assert.match(record.sourceHash, /^sha256:[a-f0-9]{64}$/);
  assert.equal(record.provenanceComplete, true);

  const coverage = await callMcp(
    "tools/call",
    {
      name: "explore_topic_coverage",
      arguments: {
        topic: fixtureTopic,
        requiredDomains: ["biology", "medicine", "economics"],
        requiredFacets: ["plasma separation", "dialysis analog"],
      },
    },
    4,
  );
  assert.equal(coverage.structuredContent.counts.biology, 1);
  assert.equal(coverage.structuredContent.counts.economics, 0);
  assert.deepEqual(coverage.structuredContent.missingDomains, ["economics"]);
  assert.equal(coverage.structuredContent.facetTable[1].status, "gap");

  const mapped = await callMcp(
    "tools/call",
    {
      name: "map_grounded_response",
      arguments: {
        prompt: "Explain the test fixture.",
        statements: [
          {
            text: "The fixture contains a plasma separation process node.",
            categories: ["response_control", "ai_protocol"],
            knowledgeRecordIds: [record.id],
          },
        ],
      },
    },
    5,
  );
  assert.equal(mapped.structuredContent.provenanceComplete, true);
  assert.equal(mapped.structuredContent.columns.length, 11);
  assert.equal(mapped.structuredContent.citations[0].id, record.id);

  const rejected = await callMcp(
    "tools/call",
    {
      name: "map_grounded_response",
      arguments: {
        prompt: "Reject an unsupported statement.",
        statements: [
          {
            text: "Unsupported statement.",
            categories: ["response_control"],
            knowledgeRecordIds: ["urn:caeluviim:knowledge:missing"],
          },
        ],
      },
    },
    6,
  );
  assert.equal(rejected.isError, true);
  assert.match(rejected.content[0].text, /missing/i);
});

test("records and queries source-bound language force without promoting claimed effects", async () => {
  const fixture = `language-force-${Date.now()}`;
  const jurisdiction = `integration-test:${fixture}`;
  let requestId = 30;
  const ingest = async (recordType, label, content) => {
    const result = await callMcp(
      "tools/call",
      {
        name: "ingest_knowledge_record",
        arguments: {
          recordType,
          label,
          content,
          domains: ["law"],
          topics: [fixture, "operative language"],
          sourceTitle: "Caeluviim language-force integration fixture",
          sourceUrl: `https://example.test/${fixture}`,
          sourceLocator: `${label} fixture`,
          sourceExcerpt: content,
          constructionRule: "Treat as a synthetic integration fixture and preserve its exact role.",
        },
      },
      requestId++,
    );
    assert.equal(result.structuredContent.persisted, true);
    return result.structuredContent.record;
  };

  const [source, expression, proposition, actor, target, authority] = await Promise.all([
    ingest("Source", "Revocation source", "Synthetic source documenting a permit revocation utterance."),
    ingest("LanguageExpression", "Revocation wording", "The permit is revoked."),
    ingest("Proposition", "Revocation proposition", "The identified permit no longer has operative status."),
    ingest("Actor", "Issuing official", "Synthetic actor identified as the speaker."),
    ingest("Entity", "Permit 42", "Synthetic permit targeted by the utterance."),
    ingest("Authority", "Revocation authority", "Synthetic authority basis for revoking Permit 42."),
  ]);

  const recorded = await callMcp(
    "tools/call",
    {
      name: "record_language_act",
      arguments: {
        label: "Permit revocation declaration",
        expressionRecordId: expression.id,
        contentRecordIds: [proposition.id],
        speakerRecordId: actor.id,
        addresseeRecordIds: [target.id],
        sourceRecordId: source.id,
        evidenceRecordIds: [source.id, authority.id],
        authorityRecordIds: [authority.id],
        actType: "declarative",
        force: "revocation",
        medium: "written",
        language: "en",
        polarity: "affirmative",
        deonticOperator: "power",
        status: "verified",
        authorityStatus: "verified",
        conditions: ["Permit 42 is within the issuing official's scope."],
        scopePath: ["fixture", "permit:42"],
        jurisdiction,
      },
    },
    requestId++,
  );
  assert.equal(recorded.structuredContent.persisted, true);
  const act = recorded.structuredContent.act;
  assert.match(act.id, /^urn:caeluviim:language-act:sha256:[a-f0-9]{64}$/);

  const effective = await callMcp(
    "tools/call",
    {
      name: "record_operative_effect",
      arguments: {
        label: "Permit 42 revoked",
        languageActId: act.id,
        effectKind: "normative",
        operator: "revokes",
        status: "effective",
        description: "The fixture represents Permit 42 as revoked under the cited authority.",
        targetRecordIds: [target.id],
        bearerRecordIds: [target.id],
        basisRecordIds: [authority.id],
        authorityRecordIds: [authority.id],
        evidenceRecordIds: [source.id, authority.id],
        scopePath: ["fixture", "permit:42"],
        jurisdiction,
      },
    },
    requestId++,
  );
  assert.equal(effective.structuredContent.persisted, true);
  assert.match(
    effective.structuredContent.effect.id,
    /^urn:caeluviim:operative-effect:sha256:[a-f0-9]{64}$/,
  );

  const rejected = await callMcp(
    "tools/call",
    {
      name: "record_operative_effect",
      arguments: {
        label: "Unsupported effective revocation",
        languageActId: act.id,
        effectKind: "normative",
        operator: "revokes",
        status: "effective",
        description: "This must be rejected because no authority or signed operation is supplied.",
        targetRecordIds: [target.id],
        basisRecordIds: [source.id],
        evidenceRecordIds: [source.id],
      },
    },
    requestId++,
  );
  assert.equal(rejected.isError, true);
  assert.match(rejected.content[0].text, /requires authority records or a realized signed operation/i);

  const wrongAuthorityType = await callMcp(
    "tools/call",
    {
      name: "record_operative_effect",
      arguments: {
        label: "Source disguised as authority",
        languageActId: act.id,
        effectKind: "normative",
        operator: "revokes",
        status: "effective",
        description: "This must be rejected because a source record is not an authority record.",
        targetRecordIds: [target.id],
        basisRecordIds: [source.id],
        authorityRecordIds: [source.id],
        evidenceRecordIds: [source.id],
      },
    },
    requestId++,
  );
  assert.equal(wrongAuthorityType.isError, true);
  assert.match(wrongAuthorityType.content[0].text, /authority.*must use Authority or Rule or Protocol/i);

  const queried = await callMcp(
    "tools/call",
    {
      name: "query_language_force",
      arguments: {
        query: "revocation",
        effectStatuses: ["effective"],
        jurisdiction,
      },
    },
    requestId++,
  );
  assert.equal(queried.structuredContent.actCount, 1);
  assert.equal(queried.structuredContent.effectCount, 1);
  assert.ok(queried.structuredContent.recordCount >= 6);
  assert.ok(
    queried.structuredContent.graph.edges.some(
      (edge) => edge.predicate === "arisesFrom" && edge.object === act.id,
    ),
  );
  assert.ok(
    queried.structuredContent.graph.edges.some(
      (edge) => edge.predicate === "authorizedBy" && edge.object === authority.id,
    ),
  );

  const jsonLdResponse = await fetch(
    `${baseUrl}/api/language/graph?q=revocation&jurisdiction=${encodeURIComponent(jurisdiction)}&format=jsonld`,
  );
  assert.equal(jsonLdResponse.status, 200);
  assert.match(jsonLdResponse.headers.get("content-type"), /application\/ld\+json/);
  const jsonLd = await jsonLdResponse.json();
  assert.ok(jsonLd["@graph"].some((node) => node["@id"] === act.id));

  const nquadsResponse = await fetch(
    `${baseUrl}/api/language/graph?q=revocation&jurisdiction=${encodeURIComponent(jurisdiction)}&format=nquads`,
  );
  assert.equal(nquadsResponse.status, 200);
  assert.match(nquadsResponse.headers.get("content-type"), /application\/n-quads/);
  const nquads = await nquadsResponse.text();
  assert.match(nquads, /ontology\/core#arisesFrom/);
  assert.match(nquads, /ontology\/core#EvidenceBoundRelation/);
  assert.match(nquads, /ontology\/core#supportedBy/);
});

test("publishes, deduplicates, and projects a complete response event", async () => {
  const prompt = `Verify legal standing and source provenance for integration test ${Date.now()}.`;
  const requestBody = JSON.stringify({
    prompt,
    sources: [{ title: "Primary authority", url: "https://example.test/authority" }],
  });
  const publish = () =>
    fetch(`${baseUrl}/api/respond`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: requestBody,
    });

  const first = await publish();
  assert.equal(first.status, 200);
  const payload = await first.json();
  const duplicate = await publish();
  assert.equal(duplicate.status, 200);
  const duplicatePayload = await duplicate.json();

  assert.equal(payload.persisted, true);
  assert.equal(payload.columns.length, 11);
  assert.equal(new Set(payload.columns.map((column) => column.key)).size, 11);
  assert.ok(payload.columns.findIndex((column) => column.key === "legal") < payload.columns.findIndex((column) => column.key === "emoji_rider"));
  assert.equal(payload.row.emoji_rider, "");
  assert.match(payload.csv, /Legal/);
  assert.match(payload.event.eventId, /^urn:caeluviim:event:sha256:[a-f0-9]{64}$/);
  assert.match(payload.event.contentHash, /^sha256:[a-f0-9]{64}$/);
  assert.equal(payload.event.consentScope, "collective");
  assert.equal(payload.event.ingestionStatus, "projected");
  assert.equal(payload.graph.nodes.length, 14);
  assert.equal(payload.graph.edges.length, 13);
  assert.equal(duplicatePayload.event.eventId, payload.event.eventId);

  const events = await fetch(`${baseUrl}/api/events?limit=100`).then((result) => result.json());
  assert.equal(events.events.filter((event) => event.eventId === payload.event.eventId).length, 1);

  const graph = await fetch(`${baseUrl}/api/graph?limit=100`).then((result) => result.json());
  assert.ok(graph.nodes.some((node) => node.id === payload.id));
  assert.ok(graph.edges.some((edge) => edge.subject === payload.id && edge.predicate === "hasCategory"));
});

test("operates a signed district from genesis through deterministic reconstruction", async () => {
  const { privateKey } = generateKeyPairSync("ed25519");
  const publicKey = createPublicKey(privateKey).export({ format: "der", type: "spki" }).subarray(-32).toString("base64url");
  const { privateKey: memberPrivateKey } = generateKeyPairSync("ed25519");
  const memberPublicKey = createPublicKey(memberPrivateKey).export({ format: "der", type: "spki" }).subarray(-32).toString("base64url");
  const suffix = `${Date.now()}-${randomBytes(4).toString("hex")}`;
  const districtId = `district:kernel-${suffix}`;
  const identityId = `identity:founder-${suffix}`;
  const keyId = `key:founder-${suffix}`;
  const authorityId = `authority:root-${suffix}`;
  const memberIdentityId = `identity:member-${suffix}`;
  const memberKeyId = `key:member-${suffix}`;
  const memberAuthorityId = `authority:member-${suffix}`;
  const evidenceId = `evidence:safety-${suffix}`;
  const checkpointId = `checkpoint:kernel-${suffix}`;
  const proposalId = `proposal:commons-${suffix}`;
  const acceptedProposalId = `proposal:accepted-${suffix}`;
  const reviewGate = {
    guard_id: `guard:review-${suffix}`,
    assert: false,
    on_false: "pending",
    on_unknown: "pending",
    reason_code: "REVIEW_NOT_COMPLETE",
    pending_condition: "REVIEW_NOT_COMPLETE",
  };
  const vetoAttachRule = dapRule(
    "VETO_ATTACH",
    "veto.attach.safety",
    ["draft"],
    "submitted_contested",
    [],
    "proposal",
  );
  vetoAttachRule.evidence.minimum_count = 1;
  vetoAttachRule.evidence.required_record_types = ["Evidence"];
  const ruleset = {
    protocol_version: "dap/0.2",
    language_version: "dap-rules/0.2",
    ruleset_id: `ruleset:z${"1".repeat(43)}`,
    district_id: districtId,
    ruleset_version: 1,
    predecessor_ruleset_id: null,
    effective_from_checkpoint: null,
    numeric_scale: 1000000,
    defaults: {
      unknown_fact: "quarantine",
      missing_dependency: "reject",
      unregistered_operation: "reject",
      conflict_policy: "reject_later",
      authority_aggregation: "non_aggregating",
      wildcard_scope: false,
    },
    capabilities: [
      { capability_id: "authority.delegate", implies: [] },
      { capability_id: "authority.revoke", implies: [] },
      { capability_id: "checkpoint.finalize", implies: [] },
      { capability_id: "evidence.register", implies: [] },
      { capability_id: "identity.declare", implies: [] },
      { capability_id: "key.delegate", implies: [] },
      { capability_id: "key.revoke", implies: [] },
      { capability_id: "membership.activate", implies: [] },
      { capability_id: "membership.nominate", implies: [] },
      { capability_id: "membership.suspend", implies: [] },
      { capability_id: "operation.reverse", implies: [] },
      { capability_id: "proposal.create", implies: [] },
      { capability_id: "proposal.archive", implies: [] },
      { capability_id: "proposal.accept", implies: [] },
      { capability_id: "proposal.activate", implies: [] },
      { capability_id: "proposal.reject", implies: [] },
      { capability_id: "proposal.review", implies: [] },
      { capability_id: "proposal.submit", implies: [] },
      { capability_id: "proposal.vote", implies: [] },
      { capability_id: "ruleset.activate", implies: [] },
      { capability_id: "ruleset.propose", implies: [] },
      { capability_id: "veto.attach.safety", implies: [] },
      { capability_id: "veto.resolve.safety", implies: [] },
    ],
    decision_rules: [
      {
        decision_rule_id: "rule:test-vote",
        electorate: true,
        snapshot: "live_checkpoint",
        ballot: ["abstain", "approve", "reject"],
        weighting: "one_member_one_vote",
        quorum: { numerator: 1, denominator: 2 },
        approval: { ratio: { numerator: 1, denominator: 2 }, base: "non_abstaining" },
        tie_policy: "reject",
        duplicate_vote_policy: "reject_later",
      },
    ],
    operation_rules: [
      dapRule("AUTHORITY_DELEGATE", "authority.delegate", ["absent"], "active", [], "authority"),
      dapRule("AUTHORITY_REVOKE", "authority.revoke", ["active"], "revoked", [], "authority"),
      dapRule("CHECKPOINT_FINALIZE", "checkpoint.finalize", ["absent"], "finalized", [], "checkpoint"),
      dapRule("EVIDENCE_REGISTER", "evidence.register", ["absent"], "registered", [], "evidence"),
      dapRule("IDENTITY_DECLARE", "identity.declare", ["absent"], "declared", [], "identity"),
      dapRule("KEY_DELEGATE", "key.delegate", ["absent"], "active", [], "key"),
      dapRule("KEY_REVOKE", "key.revoke", ["active"], "revoked", [], "key"),
      dapRule("MEMBERSHIP_ACTIVATE", "membership.activate", ["probationary"], "active", [], "membership"),
      dapRule("MEMBERSHIP_NOMINATE", "membership.nominate", ["absent"], "probationary", [], "membership"),
      dapRule("MEMBERSHIP_SUSPEND", "membership.suspend", ["active"], "suspended", [], "membership"),
      dapRule("OPERATION_REVERSE", "operation.reverse", ["absent"], "reversed", [], "operation"),
      dapRule("PROPOSAL_CREATE", "proposal.create", ["absent"], "draft"),
      dapRule("PROPOSAL_ARCHIVE", "proposal.archive", ["active", "rejected"], "archived"),
      dapRule("PROPOSAL_ACCEPT", "proposal.accept", ["in_review"], "accepted"),
      dapRule("PROPOSAL_ACTIVATE", "proposal.activate", ["accepted"], "active"),
      dapRule("PROPOSAL_REJECT", "proposal.reject", ["in_review"], "rejected"),
      dapRule("PROPOSAL_REVIEW_BEGIN", "proposal.review", ["draft"], "in_review"),
      dapRule("PROPOSAL_SUBMIT", "proposal.submit", ["draft"], "submitted", [reviewGate]),
      dapRule("RULESET_ACTIVATE", "ruleset.activate", ["absent"], "active", [], "ruleset"),
      dapRule("RULESET_PROPOSE", "ruleset.propose", ["absent"], "proposed", [], "ruleset"),
      dapRule("VOTE_CAST", "proposal.vote", ["draft"], "draft", [], "proposal"),
      vetoAttachRule,
      dapRule("VETO_RESOLVE", "veto.resolve.safety", ["submitted_contested"], "draft", [], "proposal"),
    ],
    reason_catalog: [
      {
        code: "REVIEW_NOT_COMPLETE",
        default_disposition: "ACCEPTED_PENDING",
        description: "The deterministic review gate remains open.",
      },
    ],
  };
  ruleset.ruleset_id = rulesetIdentifier(ruleset);

  const genesis = signDapOperation(
    {
      protocol_version: "dap/0.2",
      ruleset_id: ruleset.ruleset_id,
      district_id: districtId,
      author: { identity_id: identityId, signing_key_id: keyId, actor_class: "human_direct" },
      operation_type: "DISTRICT_CREATE",
      target: { resource_type: "district", resource_id: districtId, scope_path: [districtId] },
      payload: {
        district_name: "Caeluviim Commons kernel test",
        district_time: "2026-07-19T18:00:00Z",
        genesis_identity: {
          identity_id: identityId,
          signing_key_id: keyId,
          actor_class: "human_direct",
          public_key: publicKey,
        },
        initial_membership: { status: "active", roles: ["founder"] },
        initial_authorities: [
          {
            authority_id: authorityId,
            issuer_id: identityId,
            recipient_id: identityId,
            root_issuer_id: identityId,
            capabilities: ruleset.capabilities.map((capability) => capability.capability_id),
            scope: [districtId],
            weight: 1000000,
            delegable: true,
            maximum_delegation_depth: 4,
            delegation_depth: 0,
            parent_authority_id: null,
            valid_from: null,
            expires_at: null,
          },
        ],
        initial_resources: { proposals: {} },
        ruleset,
      },
      evidence_ids: [],
      parent_ids: [],
      dependencies: [],
      causal: {
        author_sequence: 1,
        previous_author_operation: null,
        observed_checkpoint: null,
        logical_time: { lamport: 1, tie_breaker: identityId },
      },
      authorization: { authority_ids: [], delegation_chain: [], required_capability: "district.create" },
      created_at: "2026-07-19T18:00:00Z",
      valid_from: null,
      expires_at: null,
      nonce: randomBytes(16).toString("base64url"),
    },
    privateKey,
  );

  const genesisResult = await postDap("/api/districts", genesis);
  assert.equal(genesisResult.response.status, 202, JSON.stringify(genesisResult.body));
  assert.equal(genesisResult.body.result.disposition, "ACCEPTED_EFFECTIVE");
  assert.equal(genesisResult.body.result.accepted_operation_count, 1);
  assertSignedDisposition(genesisResult.body.result);
  assert.match(genesisResult.body.result.history_root_after, /^history:z/);
  assert.match(genesisResult.body.result.state_root_after, /^state:z/);

  const duplicateGenesis = await postDap("/api/districts", genesis);
  assert.equal(duplicateGenesis.response.status, 200, JSON.stringify(duplicateGenesis.body));
  assert.equal(duplicateGenesis.body.result.disposition, "DUPLICATE");

  const laterOperation = ({
    operationType,
    resourceType,
    resourceId,
    payload,
    capability,
    sequence,
    previous,
    lamport,
    dependencies = [],
    parentIds = [],
    evidenceIds = [],
    authorityIds = [authorityId],
    delegationChain = [authorityId],
    authorIdentity = identityId,
    authorKey = keyId,
    signingKey = privateKey,
    boundRulesetId = ruleset.ruleset_id,
  }) =>
    signDapOperation(
      {
        protocol_version: "dap/0.2",
        ruleset_id: boundRulesetId,
        district_id: districtId,
        author: { identity_id: authorIdentity, signing_key_id: authorKey, actor_class: "human_direct" },
        operation_type: operationType,
        target: {
          resource_type: resourceType,
          resource_id: resourceId,
          scope_path: [districtId, `${resourceType}:${resourceId}`],
        },
        payload,
        evidence_ids: [...evidenceIds].sort(),
        parent_ids: [...parentIds].sort(),
        dependencies: [...dependencies].sort(),
        causal: {
          author_sequence: sequence,
          previous_author_operation: previous,
          observed_checkpoint: null,
          logical_time: { lamport, tie_breaker: authorIdentity },
        },
        authorization: {
          authority_ids: [...authorityIds].sort(),
          delegation_chain: delegationChain,
          required_capability: capability,
        },
        created_at: `2026-07-19T18:${String(lamport).padStart(2, "0")}:00Z`,
        valid_from: null,
        expires_at: null,
        nonce: randomBytes(16).toString("base64url"),
      },
      signingKey,
    );

  const createProposal = signDapOperation(
    {
      protocol_version: "dap/0.2",
      ruleset_id: ruleset.ruleset_id,
      district_id: districtId,
      author: { identity_id: identityId, signing_key_id: keyId, actor_class: "human_direct" },
      operation_type: "PROPOSAL_CREATE",
      target: {
        resource_type: "proposal",
        resource_id: proposalId,
        scope_path: [districtId, "repository:governance", proposalId],
      },
      payload: {
        proposal_id: proposalId,
        proposal_version: 1,
        title: "Operational commons proposal",
        body: "Proves signed admission and deterministic reduction.",
        decision_rule_id: null,
        review_period_seconds: 0,
      },
      evidence_ids: [],
      parent_ids: [],
      dependencies: [genesis.operation_id],
      causal: {
        author_sequence: 2,
        previous_author_operation: genesis.operation_id,
        observed_checkpoint: null,
        logical_time: { lamport: 2, tie_breaker: identityId },
      },
      authorization: {
        authority_ids: [authorityId],
        delegation_chain: [authorityId],
        required_capability: "proposal.create",
      },
      created_at: "2026-07-19T18:01:00Z",
      valid_from: null,
      expires_at: null,
      nonce: randomBytes(16).toString("base64url"),
    },
    privateKey,
  );
  const createResult = await postDap("/api/districts/operations", createProposal);
  assert.equal(createResult.response.status, 202, JSON.stringify(createResult.body));
  assert.equal(createResult.body.result.disposition, "ACCEPTED_EFFECTIVE");

  const stateAfterCreate = await fetch(`${baseUrl}/api/districts/state?district_id=${encodeURIComponent(districtId)}`).then((result) => result.json());
  assert.equal(stateAfterCreate.accepted_count, 2);
  assert.equal(stateAfterCreate.state.proposals[proposalId].state, "draft");

  const submitProposal = signDapOperation(
    {
      protocol_version: "dap/0.2",
      ruleset_id: ruleset.ruleset_id,
      district_id: districtId,
      author: { identity_id: identityId, signing_key_id: keyId, actor_class: "human_direct" },
      operation_type: "PROPOSAL_SUBMIT",
      target: {
        resource_type: "proposal",
        resource_id: proposalId,
        scope_path: [districtId, "repository:governance", proposalId],
      },
      payload: {
        proposal_id: proposalId,
        proposal_version: 1,
        decision_rule_id: "rule:test-vote",
        review_period_seconds: 86400,
      },
      evidence_ids: [],
      parent_ids: [createProposal.operation_id],
      dependencies: [createProposal.operation_id],
      causal: {
        author_sequence: 3,
        previous_author_operation: createProposal.operation_id,
        observed_checkpoint: null,
        logical_time: { lamport: 3, tie_breaker: identityId },
      },
      authorization: {
        authority_ids: [authorityId],
        delegation_chain: [authorityId],
        required_capability: "proposal.submit",
      },
      created_at: "2026-07-19T18:02:00Z",
      valid_from: null,
      expires_at: null,
      nonce: randomBytes(16).toString("base64url"),
    },
    privateKey,
  );
  const submitResult = await postDap("/api/districts/operations", submitProposal);
  assert.equal(submitResult.response.status, 202, JSON.stringify(submitResult.body));
  assert.equal(submitResult.body.result.disposition, "ACCEPTED_PENDING");
  assert.deepEqual(submitResult.body.result.pending_conditions, ["REVIEW_NOT_COMPLETE"]);
  assert.notEqual(submitResult.body.result.history_root_before, submitResult.body.result.history_root_after);
  assert.equal(submitResult.body.result.state_root_before, submitResult.body.result.state_root_after);

  const duplicateSubmit = await postDap("/api/districts/operations", submitProposal);
  assert.equal(duplicateSubmit.response.status, 200, JSON.stringify(duplicateSubmit.body));
  assert.equal(duplicateSubmit.body.result.disposition, "DUPLICATE");

  const invalidSignature = signDapOperation(
    {
      ...createProposal,
      target: {
        ...createProposal.target,
        resource_id: `proposal:invalid-signature-${suffix}`,
        scope_path: [districtId, "repository:governance", `proposal:invalid-signature-${suffix}`],
      },
      payload: {
        ...createProposal.payload,
        proposal_id: `proposal:invalid-signature-${suffix}`,
      },
      dependencies: [submitProposal.operation_id],
      causal: {
        author_sequence: 4,
        previous_author_operation: submitProposal.operation_id,
        observed_checkpoint: null,
        logical_time: { lamport: 4, tie_breaker: identityId },
      },
      nonce: randomBytes(16).toString("base64url"),
    },
    privateKey,
  );
  invalidSignature.signature.value = `${invalidSignature.signature.value[0] === "A" ? "B" : "A"}${invalidSignature.signature.value.slice(1)}`;
  const invalidSignatureResult = await postDap("/api/districts/operations", invalidSignature);
  assert.equal(invalidSignatureResult.response.status, 422, JSON.stringify(invalidSignatureResult.body));
  assert.equal(invalidSignatureResult.body.result.disposition, "REJECTED");
  assertSignedDisposition(invalidSignatureResult.body.result);
  assert.ok(invalidSignatureResult.body.result.reason_codes.includes("ERR_SIGNATURE"));

  const authorGap = signDapOperation(
    {
      ...createProposal,
      target: {
        ...createProposal.target,
        resource_id: `proposal:author-gap-${suffix}`,
        scope_path: [districtId, "repository:governance", `proposal:author-gap-${suffix}`],
      },
      payload: {
        ...createProposal.payload,
        proposal_id: `proposal:author-gap-${suffix}`,
      },
      dependencies: [submitProposal.operation_id],
      causal: {
        author_sequence: 5,
        previous_author_operation: submitProposal.operation_id,
        observed_checkpoint: null,
        logical_time: { lamport: 5, tie_breaker: identityId },
      },
      nonce: randomBytes(16).toString("base64url"),
    },
    privateKey,
  );
  const authorGapResult = await postDap("/api/districts/operations", authorGap);
  assert.equal(authorGapResult.response.status, 422, JSON.stringify(authorGapResult.body));
  assert.equal(authorGapResult.body.result.disposition, "REJECTED");
  assert.deepEqual(authorGapResult.body.result.reason_codes, ["ERR_AUTHOR_CHAIN"]);

  const declareMember = laterOperation({
    operationType: "IDENTITY_DECLARE",
    resourceType: "identity",
    resourceId: memberIdentityId,
    payload: { identity_id: memberIdentityId, actor_class: "human_direct" },
    capability: "identity.declare",
    sequence: 4,
    previous: submitProposal.operation_id,
    lamport: 6,
    dependencies: [submitProposal.operation_id],
  });
  const declareMemberResult = await postDap("/api/districts/operations", declareMember);
  assert.equal(declareMemberResult.response.status, 202, JSON.stringify(declareMemberResult.body));
  assert.equal(declareMemberResult.body.result.disposition, "ACCEPTED_EFFECTIVE");

  const delegateMemberKey = laterOperation({
    operationType: "KEY_DELEGATE",
    resourceType: "key",
    resourceId: memberKeyId,
    payload: { identity_id: memberIdentityId, key_id: memberKeyId, public_key: memberPublicKey },
    capability: "key.delegate",
    sequence: 5,
    previous: declareMember.operation_id,
    lamport: 7,
    dependencies: [declareMember.operation_id],
  });
  const delegateKeyResult = await postDap("/api/districts/operations", delegateMemberKey);
  assert.equal(delegateKeyResult.response.status, 202, JSON.stringify(delegateKeyResult.body));

  const nominateMember = laterOperation({
    operationType: "MEMBERSHIP_NOMINATE",
    resourceType: "membership",
    resourceId: memberIdentityId,
    payload: { identity_id: memberIdentityId, roles: ["voter", "safety-reviewer"] },
    capability: "membership.nominate",
    sequence: 6,
    previous: delegateMemberKey.operation_id,
    lamport: 8,
    dependencies: [delegateMemberKey.operation_id],
  });
  const nominateResult = await postDap("/api/districts/operations", nominateMember);
  assert.equal(nominateResult.response.status, 202, JSON.stringify(nominateResult.body));

  const activateMember = laterOperation({
    operationType: "MEMBERSHIP_ACTIVATE",
    resourceType: "membership",
    resourceId: memberIdentityId,
    payload: { identity_id: memberIdentityId, roles: ["voter", "safety-reviewer"] },
    capability: "membership.activate",
    sequence: 7,
    previous: nominateMember.operation_id,
    lamport: 9,
    dependencies: [nominateMember.operation_id],
  });
  const activateResult = await postDap("/api/districts/operations", activateMember);
  assert.equal(activateResult.response.status, 202, JSON.stringify(activateResult.body));

  const delegateMemberAuthority = laterOperation({
    operationType: "AUTHORITY_DELEGATE",
    resourceType: "authority",
    resourceId: memberAuthorityId,
    payload: {
      authority_id: memberAuthorityId,
      parent_authority_id: authorityId,
      recipient_id: memberIdentityId,
      capabilities: ["proposal.vote", "veto.attach.safety"],
      scope: [districtId],
      weight: 500000,
      delegable: false,
      maximum_delegation_depth: 2,
      valid_from: null,
      expires_at: null,
    },
    capability: "authority.delegate",
    sequence: 8,
    previous: activateMember.operation_id,
    lamport: 10,
    dependencies: [activateMember.operation_id],
  });
  const delegateAuthorityResult = await postDap("/api/districts/operations", delegateMemberAuthority);
  assert.equal(delegateAuthorityResult.response.status, 202, JSON.stringify(delegateAuthorityResult.body));

  const registerEvidence = laterOperation({
    operationType: "EVIDENCE_REGISTER",
    resourceType: "evidence",
    resourceId: evidenceId,
    payload: {
      record_type: "Evidence",
      content_hash: `sha256:${"b".repeat(64)}`,
      provenance: { source: "kernel-test", locator: "test vector" },
    },
    capability: "evidence.register",
    sequence: 9,
    previous: delegateMemberAuthority.operation_id,
    lamport: 11,
    dependencies: [delegateMemberAuthority.operation_id],
  });
  const evidenceResult = await postDap("/api/districts/operations", registerEvidence);
  assert.equal(evidenceResult.response.status, 202, JSON.stringify(evidenceResult.body));

  const castVote = laterOperation({
    operationType: "VOTE_CAST",
    resourceType: "proposal",
    resourceId: proposalId,
    payload: {
      proposal_id: proposalId,
      proposal_version: 1,
      choice: "approve",
      decision_rule_id: "rule:test-vote",
      weight: 1,
    },
    capability: "proposal.vote",
    sequence: 1,
    previous: null,
    lamport: 12,
    dependencies: [activateMember.operation_id, delegateMemberAuthority.operation_id],
    authorityIds: [memberAuthorityId],
    delegationChain: [authorityId, memberAuthorityId],
    authorIdentity: memberIdentityId,
    authorKey: memberKeyId,
    signingKey: memberPrivateKey,
  });
  const voteResult = await postDap("/api/districts/operations", castVote);
  assert.equal(voteResult.response.status, 202, JSON.stringify(voteResult.body));
  assert.equal(voteResult.body.result.disposition, "ACCEPTED_EFFECTIVE");

  const attachVeto = laterOperation({
    operationType: "VETO_ATTACH",
    resourceType: "proposal",
    resourceId: proposalId,
    payload: {
      veto_class: "safety",
      reason: "Signed safety review vector",
      requested_remedy: "Resolve through the registered veto path",
    },
    capability: "veto.attach.safety",
    sequence: 2,
    previous: castVote.operation_id,
    lamport: 13,
    dependencies: [registerEvidence.operation_id],
    parentIds: [registerEvidence.operation_id],
    evidenceIds: [evidenceId],
    authorityIds: [memberAuthorityId],
    delegationChain: [authorityId, memberAuthorityId],
    authorIdentity: memberIdentityId,
    authorKey: memberKeyId,
    signingKey: memberPrivateKey,
  });
  const vetoResult = await postDap("/api/districts/operations", attachVeto);
  assert.equal(vetoResult.response.status, 202, JSON.stringify(vetoResult.body));
  assert.equal(vetoResult.body.result.disposition, "ACCEPTED_EFFECTIVE");

  const resolveVeto = laterOperation({
    operationType: "VETO_RESOLVE",
    resourceType: "proposal",
    resourceId: proposalId,
    payload: { veto_operation_id: attachVeto.operation_id, resulting_state: "draft" },
    capability: "veto.resolve.safety",
    sequence: 10,
    previous: registerEvidence.operation_id,
    lamport: 14,
    dependencies: [attachVeto.operation_id],
    parentIds: [attachVeto.operation_id],
  });
  const resolveResult = await postDap("/api/districts/operations", resolveVeto);
  assert.equal(resolveResult.response.status, 202, JSON.stringify(resolveResult.body));

  const duplicateVote = laterOperation({
    operationType: "VOTE_CAST",
    resourceType: "proposal",
    resourceId: proposalId,
    payload: {
      proposal_id: proposalId,
      proposal_version: 1,
      choice: "approve",
      decision_rule_id: "rule:test-vote",
      weight: 1,
    },
    capability: "proposal.vote",
    sequence: 3,
    previous: attachVeto.operation_id,
    lamport: 15,
    dependencies: [resolveVeto.operation_id],
    authorityIds: [memberAuthorityId],
    delegationChain: [authorityId, memberAuthorityId],
    authorIdentity: memberIdentityId,
    authorKey: memberKeyId,
    signingKey: memberPrivateKey,
  });
  const duplicateVoteResult = await postDap("/api/districts/operations", duplicateVote);
  assert.equal(duplicateVoteResult.response.status, 422, JSON.stringify(duplicateVoteResult.body));
  assert.ok(duplicateVoteResult.body.result.reason_codes.includes("ERR_DUPLICATE_VOTE"));

  const excessiveDelegation = laterOperation({
    operationType: "AUTHORITY_DELEGATE",
    resourceType: "authority",
    resourceId: `authority:excessive-${suffix}`,
    payload: {
      authority_id: `authority:excessive-${suffix}`,
      parent_authority_id: authorityId,
      recipient_id: memberIdentityId,
      capabilities: ["proposal.vote"],
      scope: [districtId],
      weight: 1000001,
      delegable: false,
      maximum_delegation_depth: 2,
      valid_from: null,
      expires_at: null,
    },
    capability: "authority.delegate",
    sequence: 11,
    previous: resolveVeto.operation_id,
    lamport: 16,
    dependencies: [resolveVeto.operation_id],
  });
  const excessiveDelegationResult = await postDap("/api/districts/operations", excessiveDelegation);
  assert.equal(excessiveDelegationResult.response.status, 422, JSON.stringify(excessiveDelegationResult.body));
  assert.ok(excessiveDelegationResult.body.result.reason_codes.includes("ERR_AUTHORITY_WEIGHT"));

  const rulesetV2 = structuredClone(ruleset);
  rulesetV2.ruleset_id = `ruleset:z${"1".repeat(43)}`;
  rulesetV2.ruleset_version = 2;
  rulesetV2.predecessor_ruleset_id = ruleset.ruleset_id;
  rulesetV2.ruleset_id = rulesetIdentifier(rulesetV2);
  const proposeRuleset = laterOperation({
    operationType: "RULESET_PROPOSE",
    resourceType: "ruleset",
    resourceId: rulesetV2.ruleset_id,
    payload: { ruleset: rulesetV2 },
    capability: "ruleset.propose",
    sequence: 11,
    previous: resolveVeto.operation_id,
    lamport: 17,
    dependencies: [resolveVeto.operation_id],
  });
  const proposeRulesetResult = await postDap("/api/districts/operations", proposeRuleset);
  assert.equal(proposeRulesetResult.response.status, 202, JSON.stringify(proposeRulesetResult.body));

  const activateRuleset = laterOperation({
    operationType: "RULESET_ACTIVATE",
    resourceType: "ruleset",
    resourceId: rulesetV2.ruleset_id,
    payload: { ruleset_id: rulesetV2.ruleset_id },
    capability: "ruleset.activate",
    sequence: 12,
    previous: proposeRuleset.operation_id,
    lamport: 18,
    dependencies: [proposeRuleset.operation_id],
  });
  const activateRulesetResult = await postDap("/api/districts/operations", activateRuleset);
  assert.equal(activateRulesetResult.response.status, 202, JSON.stringify(activateRulesetResult.body));

  const staleRulesetOperation = laterOperation({
    operationType: "PROPOSAL_CREATE",
    resourceType: "proposal",
    resourceId: `proposal:stale-ruleset-${suffix}`,
    payload: {
      proposal_id: `proposal:stale-ruleset-${suffix}`,
      proposal_version: 1,
      title: "Stale ruleset operation",
      body: "Must not enter accepted history.",
      decision_rule_id: null,
      review_period_seconds: 0,
    },
    capability: "proposal.create",
    sequence: 13,
    previous: activateRuleset.operation_id,
    lamport: 19,
    dependencies: [activateRuleset.operation_id],
  });
  const staleRulesetResult = await postDap("/api/districts/operations", staleRulesetOperation);
  assert.equal(staleRulesetResult.response.status, 422, JSON.stringify(staleRulesetResult.body));
  assert.deepEqual(staleRulesetResult.body.result.reason_codes, ["ERR_RULESET_BINDING"]);

  const stateBeforeCheckpoint = await fetch(
    `${baseUrl}/api/districts/state?district_id=${encodeURIComponent(districtId)}`,
  ).then((result) => result.json());
  const finalizeCheckpoint = laterOperation({
    operationType: "CHECKPOINT_FINALIZE",
    resourceType: "checkpoint",
    resourceId: checkpointId,
    payload: {
      checkpoint_id: checkpointId,
      district_time: "2026-07-20T19:00:00Z",
      history_root_before: stateBeforeCheckpoint.history_root,
      state_root_before: stateBeforeCheckpoint.state_root,
      parent_checkpoint_id: null,
    },
    capability: "checkpoint.finalize",
    sequence: 13,
    previous: activateRuleset.operation_id,
    lamport: 20,
    dependencies: [activateRuleset.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const checkpointResult = await postDap("/api/districts/operations", finalizeCheckpoint);
  assert.equal(checkpointResult.response.status, 202, JSON.stringify(checkpointResult.body));
  assert.equal(checkpointResult.body.result.disposition, "ACCEPTED_EFFECTIVE");

  const unsafeReverseVeto = laterOperation({
    operationType: "OPERATION_REVERSE",
    resourceType: "operation",
    resourceId: attachVeto.operation_id,
    payload: {
      operation_id: attachVeto.operation_id,
      reason: "Must fail because the signed veto resolution depends on this operation.",
      compensation: { kind: "resolve_veto", resulting_state: "draft" },
    },
    capability: "operation.reverse",
    sequence: 14,
    previous: finalizeCheckpoint.operation_id,
    lamport: 21,
    dependencies: [finalizeCheckpoint.operation_id],
    parentIds: [attachVeto.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const unsafeReverseResult = await postDap("/api/districts/operations", unsafeReverseVeto);
  assert.equal(unsafeReverseResult.response.status, 422, JSON.stringify(unsafeReverseResult.body));
  assert.ok(unsafeReverseResult.body.result.reason_codes.includes("ERR_REVERSE_DEPENDENT_OPERATION"));

  const reverseVote = laterOperation({
    operationType: "OPERATION_REVERSE",
    resourceType: "operation",
    resourceId: castVote.operation_id,
    payload: {
      operation_id: castVote.operation_id,
      reason: "The ballot was withdrawn through an auditable compensating operation.",
      compensation: { kind: "void_vote" },
    },
    capability: "operation.reverse",
    sequence: 14,
    previous: finalizeCheckpoint.operation_id,
    lamport: 21,
    dependencies: [finalizeCheckpoint.operation_id, castVote.operation_id],
    parentIds: [castVote.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const reverseVoteResult = await postDap("/api/districts/operations", reverseVote);
  assert.equal(reverseVoteResult.response.status, 202, JSON.stringify(reverseVoteResult.body));
  assert.equal(reverseVoteResult.body.result.disposition, "ACCEPTED_EFFECTIVE");

  const replacementVote = laterOperation({
    operationType: "VOTE_CAST",
    resourceType: "proposal",
    resourceId: proposalId,
    payload: {
      proposal_id: proposalId,
      proposal_version: 1,
      choice: "reject",
      decision_rule_id: "rule:test-vote",
      weight: 1,
    },
    capability: "proposal.vote",
    sequence: 3,
    previous: attachVeto.operation_id,
    lamport: 22,
    dependencies: [reverseVote.operation_id],
    authorityIds: [memberAuthorityId],
    delegationChain: [authorityId, memberAuthorityId],
    authorIdentity: memberIdentityId,
    authorKey: memberKeyId,
    signingKey: memberPrivateKey,
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const replacementVoteResult = await postDap("/api/districts/operations", replacementVote);
  assert.equal(replacementVoteResult.response.status, 202, JSON.stringify(replacementVoteResult.body));
  assert.equal(replacementVoteResult.body.result.disposition, "ACCEPTED_EFFECTIVE");

  const beginReview = laterOperation({
    operationType: "PROPOSAL_REVIEW_BEGIN",
    resourceType: "proposal",
    resourceId: proposalId,
    payload: {
      proposal_id: proposalId,
      proposal_version: 1,
      submission_operation_id: submitProposal.operation_id,
      decision_rule_id: "rule:test-vote",
      review_period_seconds: 86400,
    },
    capability: "proposal.review",
    sequence: 15,
    previous: reverseVote.operation_id,
    lamport: 23,
    dependencies: [submitProposal.operation_id, replacementVote.operation_id],
    parentIds: [submitProposal.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const reviewResult = await postDap("/api/districts/operations", beginReview);
  assert.equal(reviewResult.response.status, 202, JSON.stringify(reviewResult.body));

  const contradictedAcceptance = laterOperation({
    operationType: "PROPOSAL_ACCEPT",
    resourceType: "proposal",
    resourceId: proposalId,
    payload: { proposal_id: proposalId, proposal_version: 1, decision_rule_id: "rule:test-vote" },
    capability: "proposal.accept",
    sequence: 16,
    previous: beginReview.operation_id,
    lamport: 24,
    dependencies: [beginReview.operation_id, replacementVote.operation_id],
    parentIds: [replacementVote.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const contradictedAcceptanceResult = await postDap("/api/districts/operations", contradictedAcceptance);
  assert.equal(contradictedAcceptanceResult.response.status, 422, JSON.stringify(contradictedAcceptanceResult.body));
  assert.ok(contradictedAcceptanceResult.body.result.reason_codes.includes("ERR_DECISION_REJECTED"));

  const rejectProposal = laterOperation({
    operationType: "PROPOSAL_REJECT",
    resourceType: "proposal",
    resourceId: proposalId,
    payload: { proposal_id: proposalId, proposal_version: 1, decision_rule_id: "rule:test-vote" },
    capability: "proposal.reject",
    sequence: 16,
    previous: beginReview.operation_id,
    lamport: 24,
    dependencies: [beginReview.operation_id, replacementVote.operation_id],
    parentIds: [replacementVote.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const rejectProposalResult = await postDap("/api/districts/operations", rejectProposal);
  assert.equal(rejectProposalResult.response.status, 202, JSON.stringify(rejectProposalResult.body));

  const archiveProposal = laterOperation({
    operationType: "PROPOSAL_ARCHIVE",
    resourceType: "proposal",
    resourceId: proposalId,
    payload: { proposal_id: proposalId, reason: "The decision is complete and remains reconstructable." },
    capability: "proposal.archive",
    sequence: 17,
    previous: rejectProposal.operation_id,
    lamport: 25,
    dependencies: [rejectProposal.operation_id],
    parentIds: [rejectProposal.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const archiveProposalResult = await postDap("/api/districts/operations", archiveProposal);
  assert.equal(archiveProposalResult.response.status, 202, JSON.stringify(archiveProposalResult.body));

  const revokeMemberAuthority = laterOperation({
    operationType: "AUTHORITY_REVOKE",
    resourceType: "authority",
    resourceId: memberAuthorityId,
    payload: { authority_id: memberAuthorityId, reason: "The delegated task is complete." },
    capability: "authority.revoke",
    sequence: 18,
    previous: archiveProposal.operation_id,
    lamport: 26,
    dependencies: [archiveProposal.operation_id],
    parentIds: [delegateMemberAuthority.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const revokeAuthorityResult = await postDap("/api/districts/operations", revokeMemberAuthority);
  assert.equal(revokeAuthorityResult.response.status, 202, JSON.stringify(revokeAuthorityResult.body));

  const unauthorizedMemberVote = laterOperation({
    operationType: "VOTE_CAST",
    resourceType: "proposal",
    resourceId: proposalId,
    payload: {
      proposal_id: proposalId,
      proposal_version: 1,
      choice: "approve",
      decision_rule_id: "rule:test-vote",
      weight: 1,
    },
    capability: "proposal.vote",
    sequence: 4,
    previous: replacementVote.operation_id,
    lamport: 27,
    dependencies: [revokeMemberAuthority.operation_id],
    authorityIds: [memberAuthorityId],
    delegationChain: [authorityId, memberAuthorityId],
    authorIdentity: memberIdentityId,
    authorKey: memberKeyId,
    signingKey: memberPrivateKey,
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const unauthorizedVoteResult = await postDap("/api/districts/operations", unauthorizedMemberVote);
  assert.equal(unauthorizedVoteResult.response.status, 422, JSON.stringify(unauthorizedVoteResult.body));
  assert.ok(unauthorizedVoteResult.body.result.reason_codes.includes("ERR_AUTHORITY"));

  const suspendMember = laterOperation({
    operationType: "MEMBERSHIP_SUSPEND",
    resourceType: "membership",
    resourceId: memberIdentityId,
    payload: { identity_id: memberIdentityId, reason: "Suspend after the delegated task completes." },
    capability: "membership.suspend",
    sequence: 19,
    previous: revokeMemberAuthority.operation_id,
    lamport: 28,
    dependencies: [revokeMemberAuthority.operation_id],
    parentIds: [activateMember.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const suspendMemberResult = await postDap("/api/districts/operations", suspendMember);
  assert.equal(suspendMemberResult.response.status, 202, JSON.stringify(suspendMemberResult.body));

  const revokeMemberKey = laterOperation({
    operationType: "KEY_REVOKE",
    resourceType: "key",
    resourceId: memberKeyId,
    payload: {
      key_id: memberKeyId,
      revocation_reason: "End delegated key use after suspension.",
      effective_time: "2026-07-20T19:00:00Z",
    },
    capability: "key.revoke",
    sequence: 20,
    previous: suspendMember.operation_id,
    lamport: 29,
    dependencies: [suspendMember.operation_id],
    parentIds: [delegateMemberKey.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const revokeKeyResult = await postDap("/api/districts/operations", revokeMemberKey);
  assert.equal(revokeKeyResult.response.status, 202, JSON.stringify(revokeKeyResult.body));

  const revokedKeyVote = laterOperation({
    operationType: "VOTE_CAST",
    resourceType: "proposal",
    resourceId: proposalId,
    payload: {
      proposal_id: proposalId,
      proposal_version: 1,
      choice: "approve",
      decision_rule_id: "rule:test-vote",
      weight: 1,
    },
    capability: "proposal.vote",
    sequence: 4,
    previous: replacementVote.operation_id,
    lamport: 30,
    dependencies: [revokeMemberKey.operation_id],
    authorityIds: [memberAuthorityId],
    delegationChain: [authorityId, memberAuthorityId],
    authorIdentity: memberIdentityId,
    authorKey: memberKeyId,
    signingKey: memberPrivateKey,
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const revokedKeyVoteResult = await postDap("/api/districts/operations", revokedKeyVote);
  assert.equal(revokedKeyVoteResult.response.status, 422, JSON.stringify(revokedKeyVoteResult.body));
  assert.ok(revokedKeyVoteResult.body.result.reason_codes.includes("ERR_REVOKED_KEY"));

  const createAcceptedProposal = laterOperation({
    operationType: "PROPOSAL_CREATE",
    resourceType: "proposal",
    resourceId: acceptedProposalId,
    payload: {
      proposal_id: acceptedProposalId,
      proposal_version: 1,
      title: "Approved operational path",
      body: "Proves tally-bound acceptance and activation.",
      decision_rule_id: null,
      review_period_seconds: 0,
    },
    capability: "proposal.create",
    sequence: 21,
    previous: revokeMemberKey.operation_id,
    lamport: 31,
    dependencies: [revokeMemberKey.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const createAcceptedResult = await postDap("/api/districts/operations", createAcceptedProposal);
  assert.equal(createAcceptedResult.response.status, 202, JSON.stringify(createAcceptedResult.body));

  const submitAcceptedProposal = laterOperation({
    operationType: "PROPOSAL_SUBMIT",
    resourceType: "proposal",
    resourceId: acceptedProposalId,
    payload: {
      proposal_id: acceptedProposalId,
      proposal_version: 1,
      decision_rule_id: "rule:test-vote",
      review_period_seconds: 86400,
    },
    capability: "proposal.submit",
    sequence: 22,
    previous: createAcceptedProposal.operation_id,
    lamport: 32,
    dependencies: [createAcceptedProposal.operation_id],
    parentIds: [createAcceptedProposal.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const submitAcceptedResult = await postDap("/api/districts/operations", submitAcceptedProposal);
  assert.equal(submitAcceptedResult.response.status, 202, JSON.stringify(submitAcceptedResult.body));
  assert.equal(submitAcceptedResult.body.result.disposition, "ACCEPTED_PENDING");

  const founderApproveVote = laterOperation({
    operationType: "VOTE_CAST",
    resourceType: "proposal",
    resourceId: acceptedProposalId,
    payload: {
      proposal_id: acceptedProposalId,
      proposal_version: 1,
      choice: "approve",
      decision_rule_id: "rule:test-vote",
      weight: 1,
    },
    capability: "proposal.vote",
    sequence: 23,
    previous: submitAcceptedProposal.operation_id,
    lamport: 33,
    dependencies: [submitAcceptedProposal.operation_id],
    parentIds: [submitAcceptedProposal.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const founderVoteResult = await postDap("/api/districts/operations", founderApproveVote);
  assert.equal(founderVoteResult.response.status, 202, JSON.stringify(founderVoteResult.body));

  const beginAcceptedReview = laterOperation({
    operationType: "PROPOSAL_REVIEW_BEGIN",
    resourceType: "proposal",
    resourceId: acceptedProposalId,
    payload: {
      proposal_id: acceptedProposalId,
      proposal_version: 1,
      submission_operation_id: submitAcceptedProposal.operation_id,
      decision_rule_id: "rule:test-vote",
      review_period_seconds: 86400,
    },
    capability: "proposal.review",
    sequence: 24,
    previous: founderApproveVote.operation_id,
    lamport: 34,
    dependencies: [submitAcceptedProposal.operation_id, founderApproveVote.operation_id],
    parentIds: [submitAcceptedProposal.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const beginAcceptedReviewResult = await postDap("/api/districts/operations", beginAcceptedReview);
  assert.equal(beginAcceptedReviewResult.response.status, 202, JSON.stringify(beginAcceptedReviewResult.body));

  const acceptProposal = laterOperation({
    operationType: "PROPOSAL_ACCEPT",
    resourceType: "proposal",
    resourceId: acceptedProposalId,
    payload: { proposal_id: acceptedProposalId, proposal_version: 1, decision_rule_id: "rule:test-vote" },
    capability: "proposal.accept",
    sequence: 25,
    previous: beginAcceptedReview.operation_id,
    lamport: 35,
    dependencies: [beginAcceptedReview.operation_id, founderApproveVote.operation_id],
    parentIds: [founderApproveVote.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const acceptProposalResult = await postDap("/api/districts/operations", acceptProposal);
  assert.equal(acceptProposalResult.response.status, 202, JSON.stringify(acceptProposalResult.body));

  const activateProposal = laterOperation({
    operationType: "PROPOSAL_ACTIVATE",
    resourceType: "proposal",
    resourceId: acceptedProposalId,
    payload: { proposal_id: acceptedProposalId, proposal_version: 1 },
    capability: "proposal.activate",
    sequence: 26,
    previous: acceptProposal.operation_id,
    lamport: 36,
    dependencies: [acceptProposal.operation_id],
    parentIds: [acceptProposal.operation_id],
    boundRulesetId: rulesetV2.ruleset_id,
  });
  const activateProposalResult = await postDap("/api/districts/operations", activateProposal);
  assert.equal(activateProposalResult.response.status, 202, JSON.stringify(activateProposalResult.body));

  const proofResponse = await fetch(
    `${baseUrl}/api/districts/state?district_id=${encodeURIComponent(districtId)}&reconstruct=true`,
  );
  assert.equal(proofResponse.status, 200);
  const proof = await proofResponse.json();
  assert.equal(proof.accepted_operation_count, 29);
  assert.equal(proof.history_root_matches, true);
  assert.equal(proof.state_root_matches, true);
  assert.equal(proof.state.proposals[proposalId].state, "archived");
  assert.equal(proof.state.proposals[acceptedProposalId].state, "active");
  assert.equal(proof.state.memberships[memberIdentityId].status, "suspended");
  assert.equal(proof.state.keys[memberKeyId].status, "revoked");
  assert.equal(proof.state.authorities[memberAuthorityId].recipient_id, memberIdentityId);
  assert.equal(proof.state.authorities[memberAuthorityId].status, "revoked");
  assert.equal(proof.state.votes[castVote.operation_id], undefined);
  assert.equal(proof.state.votes[replacementVote.operation_id].choice, "reject");
  assert.equal(proof.state.reversals[castVote.operation_id].operation_id, reverseVote.operation_id);
  assert.equal(proof.state.vetoes[attachVeto.operation_id].status, "resolved");
  assert.equal(proof.state.district.current_checkpoint_id, checkpointId);
  assert.equal(proof.state.district.district_time, "2026-07-20T19:00:00Z");
  assert.equal(proof.state.district.active_ruleset_id, rulesetV2.ruleset_id);

  const history = await fetch(
    `${baseUrl}/api/districts/operations?district_id=${encodeURIComponent(districtId)}`,
  ).then((result) => result.json());
  assert.equal(history.count, 29);
  assert.ok(history.operations.some((operation) => operation.operation_id === castVote.operation_id));
  assert.ok(history.operations.some((operation) => operation.operation_id === reverseVote.operation_id));
  assert.ok(history.operations.some((operation) => operation.operation_id === replacementVote.operation_id));
  assert.deepEqual(
    history.operations.filter((operation) => operation.disposition === "ACCEPTED_PENDING").map((operation) => operation.operation_id),
    [submitProposal.operation_id, submitAcceptedProposal.operation_id],
  );

  const mcpReconstruction = await callMcp(
    "tools/call",
    { name: "reconstruct_dap_district", arguments: { districtId } },
    20,
  );
  assert.equal(mcpReconstruction.structuredContent.history_root_matches, true);
  assert.equal(mcpReconstruction.structuredContent.state_root_matches, true);
  assert.equal(mcpReconstruction.structuredContent.accepted_operation_count, 29);

  const mcpDisposition = await callMcp(
    "tools/call",
    { name: "get_dap_operation_disposition", arguments: { operationId: activateProposal.operation_id } },
    21,
  );
  assert.equal(mcpDisposition.structuredContent.accepted, true);
  assert.equal(mcpDisposition.structuredContent.last_disposition, "ACCEPTED_EFFECTIVE");

  const districtDialogueResponse = await fetch(`${baseUrl}/api/respond`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      prompt: "Show me the current authority, proposal, pending, and reconstruction status for this district.",
      district_id: districtId,
      sources: [],
    }),
  });
  assert.equal(districtDialogueResponse.status, 200);
  const districtDialogue = await districtDialogueResponse.json();
  assert.match(districtDialogue.row.commons, /29 accepted operations/);
  assert.match(districtDialogue.row.legal, /active scoped authority/);
  assert.match(districtDialogue.row.verification, /history root MATCH.*state root MATCH/);
  assert.match(districtDialogue.row.provenance, /Accepted-history root history:z/);
});

test("exposes the machine-readable protocols and healthy D1 binding", async () => {
  const [protocolResponse, healthResponse, dapResponse] = await Promise.all([
    fetch(`${baseUrl}/api/protocol`),
    fetch(`${baseUrl}/api/health`),
    fetch(`${baseUrl}/api/dap`),
  ]);
  assert.equal(protocolResponse.status, 200);
  assert.equal(healthResponse.status, 200);
  assert.equal(dapResponse.status, 200);
  const protocol = await protocolResponse.json();
  const health = await healthResponse.json();
  const dap = await dapResponse.json();
  assert.equal(protocol.version, "1.1.0");
  assert.equal(protocol.categories.length, 11);
  assert.ok(protocol.endpoints.some((endpoint) => endpoint.path === "/api/events"));
  assert.ok(protocol.endpoints.some((endpoint) => endpoint.path === "/api/graph"));
  assert.ok(protocol.endpoints.some((endpoint) => endpoint.path === "/mcp"));
  assert.ok(protocol.endpoints.some((endpoint) => endpoint.path === "/api/knowledge/coverage"));
  assert.ok(protocol.endpoints.some((endpoint) => endpoint.path === "/api/dap"));
  assert.equal(health.storage, "d1");
  assert.equal(health.invariants.appendOnlyEventEnvelope, true);
  assert.equal(health.invariants.contentAddressedDeduplication, true);
  assert.equal(health.invariants.remoteMcpEndpoint, true);
  assert.equal(health.invariants.groundedStatementRejection, true);
  assert.equal(health.invariants.districtOperationsAreContentAddressed, true);
  assert.equal(health.invariants.districtRulesetsAreVersionBound, true);
  assert.equal(health.invariants.districtTimeIsCheckpointDerived, true);
  assert.equal(health.invariants.signedDistrictGenesis, true);
  assert.equal(health.invariants.stagedDistrictValidation, true);
  assert.equal(health.invariants.deterministicDistrictReconstruction, true);
  assert.equal(health.invariants.acceptedHistorySeparatedFromProjection, true);
  assert.equal(dap.protocol_version, "dap/0.2");
  assert.equal(dap.language_version, "dap-rules/0.2");
  assert.equal(dap.operation_envelope_schema.title, "DAP v0.2 Operation Envelope");
  assert.equal(dap.ruleset_schema.title, "DAP v0.2 District Ruleset");
  assert.equal(dap.operational_surface.submit_operation.path, "/api/districts/operations");
  assert.equal(dap.authoritative_storage.persistence, "Cloudflare D1");
  assert.match(dap.examples.ruleset.ruleset_id, /^ruleset:z/);
  assert.match(dap.examples.operation.operation_id, /^op:z/);
});
