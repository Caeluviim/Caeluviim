import assert from "node:assert/strict";
import { createPrivateKey, createPublicKey, sign, verify } from "node:crypto";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import {
  UNKNOWN,
  aggregateAuthority,
  canonicalEncode,
  evaluateExpression,
  operationIdentifiers,
  ratioSatisfied,
  rulesetIdentifier,
  scopeContains,
} from "../lib/dap/reference.mjs";

const root = new URL("../spec/dap/0.2/", import.meta.url);
const loadJson = async (relativePath) => JSON.parse(await readFile(new URL(relativePath, root), "utf8"));
const [operationSchema, rulesetSchema, operation, ruleset] = await Promise.all([
  loadJson("schemas/operation-envelope.schema.json"),
  loadJson("schemas/ruleset.schema.json"),
  loadJson("examples/proposal-submit.operation.json"),
  loadJson("examples/alpha-12.ruleset.json"),
]);

const ajv = new Ajv2020({ allErrors: true, strict: true, allowUnionTypes: true });
addFormats(ajv);
const validateOperation = ajv.compile(operationSchema);
const validateRuleset = ajv.compile(rulesetSchema);

assert.equal(validateOperation(operation), true, JSON.stringify(validateOperation.errors, null, 2));
assert.equal(validateRuleset(ruleset), true, JSON.stringify(validateRuleset.errors, null, 2));

const expectedRulesetId = rulesetIdentifier(ruleset);
const operationIdentity = operationIdentifiers(operation);
const privateSeed = Buffer.from("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60", "hex");
const privateKey = createPrivateKey({
  key: Buffer.concat([Buffer.from("302e020100300506032b657004220420", "hex"), privateSeed]),
  format: "der",
  type: "pkcs8",
});
const publicKey = createPublicKey(privateKey);
const expectedSignature = sign(null, operationIdentity.digest, privateKey).toString("base64url");
const publicKeyRaw = publicKey.export({ format: "der", type: "spki" }).subarray(-32).toString("base64url");

if (process.argv.includes("--print-fixture-values")) {
  process.stdout.write(`${JSON.stringify({
    ruleset_id: expectedRulesetId,
    operation_id: operationIdentity.operationId,
    content_hash: operationIdentity.contentHash,
    signature: expectedSignature,
    public_key: publicKeyRaw,
  }, null, 2)}\n`);
  process.exit(0);
}

assert.equal(ruleset.ruleset_id, expectedRulesetId, "ruleset_id does not match canonical ruleset body");
assert.equal(operation.ruleset_id, ruleset.ruleset_id, "operation is not bound to the example ruleset");
assert.equal(operation.operation_id, operationIdentity.operationId, "operation_id does not match canonical operation body");
assert.equal(operation.content_hash, operationIdentity.contentHash, "content_hash does not match canonical operation body");
assert.equal(operation.signature.value, expectedSignature, "signature fixture does not cover the operation digest");
assert.equal(verify(null, operationIdentity.digest, publicKey, Buffer.from(operation.signature.value, "base64url")), true);

const utf8Compare = (left, right) => Buffer.compare(Buffer.from(left), Buffer.from(right));
const assertSortedUnique = (values, label) => {
  assert.equal(new Set(values).size, values.length, `${label} contains duplicates`);
  assert.deepEqual(values, [...values].sort(utf8Compare), `${label} is not UTF-8 sorted`);
};

assertSortedUnique(operation.evidence_ids, "operation.evidence_ids");
assertSortedUnique(operation.parent_ids, "operation.parent_ids");
assertSortedUnique(operation.dependencies, "operation.dependencies");
assertSortedUnique(operation.authorization.authority_ids, "operation.authorization.authority_ids");
assertSortedUnique(ruleset.capabilities.map((item) => item.capability_id), "ruleset.capabilities");
assertSortedUnique(ruleset.decision_rules.map((item) => item.decision_rule_id), "ruleset.decision_rules");
assertSortedUnique(ruleset.operation_rules.map((item) => item.operation_type), "ruleset.operation_rules");
assertSortedUnique(ruleset.reason_catalog.map((item) => item.code), "ruleset.reason_catalog");

const capabilities = new Map(ruleset.capabilities.map((item) => [item.capability_id, item]));
const decisions = new Set(ruleset.decision_rules.map((item) => item.decision_rule_id));
const operationTypes = new Set(ruleset.operation_rules.map((item) => item.operation_type));
const reasons = new Set(ruleset.reason_catalog.map((item) => item.code));

const visitCapability = (capabilityId, visiting = new Set(), visited = new Set()) => {
  if (visiting.has(capabilityId)) throw new Error(`Capability implication cycle at ${capabilityId}`);
  if (visited.has(capabilityId)) return;
  assert.ok(capabilities.has(capabilityId), `Unknown capability ${capabilityId}`);
  visiting.add(capabilityId);
  for (const implied of capabilities.get(capabilityId).implies) visitCapability(implied, visiting, visited);
  visiting.delete(capabilityId);
  visited.add(capabilityId);
};
for (const capabilityId of capabilities.keys()) visitCapability(capabilityId);

const gcd = (left, right) => (right === 0 ? left : gcd(right, left % right));
for (const decision of ruleset.decision_rules) {
  for (const ratio of [decision.quorum, decision.approval.ratio]) {
    assert.equal(gcd(ratio.numerator, ratio.denominator), 1, `${decision.decision_rule_id} contains an unreduced ratio`);
  }
}

for (const rule of ruleset.operation_rules) {
  assert.ok(capabilities.has(rule.required_capability), `${rule.operation_type} references an unknown capability`);
  for (const guard of [...rule.guards, ...rule.effect_gates]) {
    assert.ok(reasons.has(guard.reason_code), `${guard.guard_id} references an unknown reason`);
  }
  if (rule.veto?.enabled) {
    assert.ok(capabilities.has(rule.veto.required_capability), `${rule.operation_type} veto capability is unknown`);
    assert.ok(decisions.has(rule.veto.resolution_decision_rule_id), `${rule.operation_type} veto decision rule is unknown`);
    assert.ok(operationTypes.has(rule.veto.resolution_operation_type), `${rule.operation_type} veto resolution operation is absent`);
    assert.ok(rule.veto.review_period_seconds > 0, `${rule.operation_type} veto is not time bounded`);
  }
}

const context = {
  operation: { author: { actor_class: "human_direct" } },
  candidate: { wildcard_scope: true },
};
assert.equal(evaluateExpression({ all: [true, { path: "/missing/value" }] }, context), UNKNOWN);
assert.equal(evaluateExpression({ all: [false, { path: "/missing/value" }] }, context), false);
assert.equal(evaluateExpression({ any: [true, { path: "/missing/value" }] }, context), true);
assert.equal(evaluateExpression({ eq: [{ path: "/operation/author/actor_class" }, "human_direct"] }, context), true);
assert.equal(evaluateExpression({ eq: [{ path: "/operation/missing" }, null] }, context), UNKNOWN);

assert.equal(canonicalEncode({ b: "e\u0301", a: 1 }), canonicalEncode({ a: 1, b: "é" }));
assert.throws(() => canonicalEncode({ "e\u0301": 1, "é": 2 }), /collide/);
assert.throws(() => canonicalEncode({ weight: 0.85 }), /safe integers/);
assert.throws(() => canonicalEncode(new Date("2026-07-19T18:00:00Z")), /plain records/);
assert.equal(ratioSatisfied(2, 3, { numerator: 2, denominator: 3 }), true);
assert.equal(ratioSatisfied(1, 3, { numerator: 2, denominator: 3 }), false);
assert.equal(ratioSatisfied(0, 0, { numerator: 0, denominator: 1 }), false);
assert.equal(scopeContains(["district:alpha", "repository:legal"], ["district:alpha", "repository:legal", "document:1"]), true);
assert.equal(scopeContains(["district:alpha", "repository:legal"], ["district:alpha", "repository:biology"]), false);
assert.equal(scopeContains(["district:alpha", "**"], ["district:alpha", "repository:legal"], false), false);
assert.equal(scopeContains(["district:alpha", "**"], ["district:alpha", "repository:legal"], true), true);

const aggregated = aggregateAuthority([
  { rootIssuer: "identity:genesis-a", weight: 600000 },
  { rootIssuer: "identity:genesis-a", weight: 500000 },
  { rootIssuer: "identity:genesis-b", weight: 250000 },
], "sum_capped", 1000000);
assert.deepEqual(aggregated, { weight: 850000, rootIssuers: 2, qualifyingRootIssuers: 2 });

const signatureChanged = structuredClone(operation);
signatureChanged.signature.value = "B".repeat(86);
assert.equal(operationIdentifiers(signatureChanged).operationId, operation.operation_id, "signature must not change operation_id");

const proof = {
  status: "PASS",
  schema_validation: ["operation-envelope.schema.json", "ruleset.schema.json"],
  ruleset_id: ruleset.ruleset_id,
  operation_id: operation.operation_id,
  content_hash: operation.content_hash,
  ed25519_public_key_base64url: publicKeyRaw,
  checks: {
    canonical_nfc: true,
    normalization_collision_rejected: true,
    floating_point_rejected: true,
    exact_ratio_boundary: true,
    same_root_authority_not_stacked: true,
    scope_containment: true,
    three_valued_logic: true,
    veto_resolution_cross_references: true
  },
  verifier: fileURLToPath(import.meta.url)
};
process.stdout.write(`${JSON.stringify(proof, null, 2)}\n`);
