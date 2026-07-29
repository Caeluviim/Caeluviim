import {
  AUTHORITY_STATUSES,
  DEONTIC_OPERATORS,
  EFFECT_KINDS,
  EFFECT_OPERATORS,
  EFFECT_STATUSES,
  LANGUAGE_ACT_STATUSES,
  LANGUAGE_ACT_TYPES,
  LANGUAGE_FORCE_PROTOCOL_VERSION,
  LANGUAGE_MEDIA,
} from "../../../lib/language";

const cors = { "access-control-allow-origin": "*" };

export function GET() {
  return Response.json(
    {
      name: "Caeluviim Language Force and Operative Effect Protocol",
      version: LANGUAGE_FORCE_PROTOCOL_VERSION,
      separationRule:
        "Expression, propositional content, interpretation, illocutionary force, authority, and operative effect are separate graph resources.",
      groundingRule:
        "Every language act and effect must reference existing provenance-complete knowledge records. Effective institutional, normative, or procedural effects additionally require authority records or a realized signed DAP operation.",
      vocabularies: {
        media: LANGUAGE_MEDIA,
        actTypes: LANGUAGE_ACT_TYPES,
        actStatuses: LANGUAGE_ACT_STATUSES,
        authorityStatuses: AUTHORITY_STATUSES,
        deonticOperators: DEONTIC_OPERATORS,
        effectKinds: EFFECT_KINDS,
        effectOperators: EFFECT_OPERATORS,
        effectStatuses: EFFECT_STATUSES,
      },
      endpoints: [
        { method: "POST", path: "/api/language/acts", purpose: "Record a source-bound language act" },
        { method: "GET", path: "/api/language/acts", purpose: "Query language acts" },
        { method: "POST", path: "/api/language/effects", purpose: "Record an evidence-bound operative effect" },
        { method: "GET", path: "/api/language/effects", purpose: "Query operative effects" },
        { method: "GET", path: "/api/language/graph", purpose: "Query or export the joined language/effect graph" },
      ],
      exports: ["application/json", "application/ld+json", "application/n-quads"],
    },
    { headers: cors },
  );
}
