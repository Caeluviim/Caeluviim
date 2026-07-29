import operationExample from "../../../spec/dap/0.2/examples/proposal-submit.operation.json";
import rulesetExample from "../../../spec/dap/0.2/examples/alpha-12.ruleset.json";
import operationEnvelopeSchema from "../../../spec/dap/0.2/schemas/operation-envelope.schema.json";
import rulesetSchema from "../../../spec/dap/0.2/schemas/ruleset.schema.json";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, OPTIONS",
  "access-control-allow-headers": "content-type",
};

const descriptor = {
  name: "Districted Authority Protocol",
  protocol_version: "dap/0.2",
  language_version: "dap-rules/0.2",
  status: "working-draft",
  invariant: "Authoritative state is the deterministic reduction of valid accepted operations.",
  distinctions: [
    "structurally_valid",
    "cryptographically_valid",
    "admissible",
    "accepted",
    "effective",
  ],
  canonicalization: {
    operation_domain: "DAP-OPERATION-0.2",
    ruleset_domain: "DAP-RULESET-0.2",
    string_normalization: "NFC",
    object_key_order: "lexicographic UTF-8 byte order",
    signed_numbers: "safe integers or fixed-point decimal strings",
    binary_floating_point: "forbidden",
  },
  validator_disposition: {
    domain: "DAP-DISPOSITION-0.2",
    algorithm: "Ed25519",
    private_key_binding: "DAP_VALIDATOR_PRIVATE_KEY_PKCS8",
    public_verification_metadata: true,
  },
  operational_surface: {
    submit_genesis: { method: "POST", path: "/api/districts" },
    submit_operation: { method: "POST", path: "/api/districts/operations" },
    read_history: { method: "GET", path: "/api/districts/operations?district_id=..." },
    read_submission: { method: "GET", path: "/api/districts/operations?operation_id=..." },
    read_state: { method: "GET", path: "/api/districts/state?district_id=..." },
    reconstruct_state: { method: "GET", path: "/api/districts/state?district_id=...&reconstruct=true" },
    mcp: {
      method: "POST",
      path: "/mcp",
      tools: [
        "list_dap_districts",
        "reconstruct_dap_district",
        "get_dap_history",
        "get_dap_operation_disposition",
        "submit_signed_dap_operation",
      ],
    },
  },
  authoritative_storage: {
    submissions: "retained separately from accepted history",
    accepted_history: "only accepted operation envelopes",
    derived_state: "reconstructable projection with independent history and state roots",
    persistence: "Cloudflare D1",
  },
  operation_envelope_schema: operationEnvelopeSchema,
  ruleset_schema: rulesetSchema,
  examples: {
    ruleset: rulesetExample,
    operation: operationExample,
  },
};

export function GET() {
  return Response.json(descriptor, { headers: cors });
}

export function OPTIONS() {
  return new Response(null, { status: 204, headers: cors });
}
