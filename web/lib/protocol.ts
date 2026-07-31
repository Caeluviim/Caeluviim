export const PROTOCOL_VERSION = "1.1.0";

export const CATEGORY_KEYS = [
  "response_control",
  "provenance",
  "legal",
  "standing",
  "commons",
  "social_contract",
  "ai_protocol",
  "linguistic",
  "emoji_rider",
  "risk_limits",
  "verification",
] as const;

export type CategoryKey = (typeof CATEGORY_KEYS)[number];

export type ProtocolSource = {
  title: string;
  url?: string;
  kind?: string;
};

export type DistrictResponseContext = {
  districtId: string;
  name: string;
  status: string;
  activeRulesetId: string;
  districtTime: string;
  acceptedOperationCount: number;
  pendingOperationCount: number;
  activeMemberCount: number;
  activeAuthorityCount: number;
  unresolvedConflictCount: number;
  proposalStates: string[];
  historyRoot: string;
  stateRoot: string;
  historyRootMatches: boolean;
  stateRootMatches: boolean;
};

export type CategoryDefinition = {
  key: CategoryKey;
  label: string;
  group: string;
  description: string;
  keywords: string[];
};

export type GraphNode = {
  id: string;
  type: "Prompt" | "Response" | "Category" | "Source";
  label: string;
  value?: string;
  empty?: boolean;
};

export type GraphEdge = {
  id: string;
  subject: string;
  predicate: string;
  object: string;
};

export type ProtocolResponse = {
  id: string;
  schemaVersion: string;
  prompt: string;
  createdAt: string;
  columns: CategoryDefinition[];
  row: Record<CategoryKey, string>;
  csv: string;
  graph: {
    nodes: GraphNode[];
    edges: GraphEdge[];
  };
  sourceCount: number;
  persisted?: boolean;
  event?: ResponseEventMetadata;
};

export type ConsentScope = "collective" | "group" | "private";

export type ResponseEventMetadata = {
  eventId: string;
  eventType: "caeluviim.response.created";
  responseId: string;
  protocolVersion: string;
  contentHash: string;
  consentScope: ConsentScope;
  partitionKey: string;
  ingestionStatus: "projected";
  createdAt: string;
};

export type ResponseEvent = ResponseEventMetadata & {
  response: ProtocolResponse;
};

export const CATEGORY_DEFINITIONS: CategoryDefinition[] = [
  {
    key: "response_control",
    label: "Response control",
    group: "Control",
    description: "Intent, status, requested action, and response identity.",
    keywords: ["request", "need", "want", "goal", "build", "make", "answer"],
  },
  {
    key: "provenance",
    label: "Provenance",
    group: "Evidence",
    description: "The origin of every asserted or supplied item.",
    keywords: ["source", "citation", "evidence", "record", "document", "data"],
  },
  {
    key: "legal",
    label: "Legal",
    group: "Authority",
    description: "Authority, rule, application, procedure, and remedy.",
    keywords: ["law", "legal", "statute", "case", "court", "rule", "claim", "remedy", "right"],
  },
  {
    key: "standing",
    label: "Standing",
    group: "Authority",
    description: "Injury, causation, redressability, and representative capacity.",
    keywords: ["standing", "injury", "causation", "redress", "representative", "jurisdiction"],
  },
  {
    key: "commons",
    label: "Global commons",
    group: "Commons",
    description: "Shared resource, beneficiaries, access, and stewardship.",
    keywords: ["commons", "public", "collective", "shared", "community", "humanity", "access"],
  },
  {
    key: "social_contract",
    label: "Social contract",
    group: "Commons",
    description: "Reciprocal rights, duties, legitimacy, breach, and remedy.",
    keywords: ["social contract", "obligation", "duty", "consent", "legitimacy", "society", "breach"],
  },
  {
    key: "ai_protocol",
    label: "AI protocol",
    group: "System",
    description: "Construction rule, provider boundary, and machine behavior.",
    keywords: ["ai", "model", "agent", "prompt", "protocol", "algorithm", "machine", "http", "api"],
  },
  {
    key: "linguistic",
    label: "Linguistic",
    group: "Language",
    description: "Term, definition, language layer, ambiguity, and interpretation.",
    keywords: ["language", "word", "term", "definition", "meaning", "semantic", "ambiguity", "interpret"],
  },
  {
    key: "emoji_rider",
    label: "Emoji rider",
    group: "Language",
    description: "Glyph, universal-language syntax, structure, and semantics.",
    keywords: ["emoji", "glyph", "symbol", "syntax", "unicode", "pictograph"],
  },
  {
    key: "risk_limits",
    label: "Risk / limits",
    group: "Assurance",
    description: "Uncertainty, unresolved matters, limits, and failure modes.",
    keywords: ["risk", "limit", "uncertain", "unknown", "failure", "harm", "blocked"],
  },
  {
    key: "verification",
    label: "Verification",
    group: "Assurance",
    description: "Checks, proof state, method, and machine-readable result.",
    keywords: ["verify", "proof", "test", "check", "validate", "status", "operational"],
  },
];

export const PROTOCOL_DESCRIPTOR = {
  name: "Caeluviim Graph/Table Response Protocol",
  version: PROTOCOL_VERSION,
  rule:
    "Every response contains every category. Populated categories move forward by relevance; non-applicable categories remain visible as empty cells.",
  transport: "HTTP JSON",
  export: "CSV",
  persistence:
    "A source-bound knowledge graph is primary. Append-only response events preserve an audit projection of mapped answers.",
  grounding:
    "Every answer statement must cite existing provenance-complete knowledge records. Topic coverage gaps remain explicit.",
  categories: CATEGORY_DEFINITIONS,
  endpoints: [
    { method: "GET", path: "/api/health", purpose: "Runtime and schema status" },
    { method: "GET", path: "/api/protocol", purpose: "Machine-readable protocol schema" },
    { method: "GET", path: "/api/dap", purpose: "DAP v0.2 operation and ruleset schemas with signed vectors" },
    { method: "GET", path: "/api/districts", purpose: "List operational DAP districts and committed roots" },
    { method: "POST", path: "/api/districts", purpose: "Submit a signed district genesis operation" },
    { method: "GET", path: "/api/districts/operations", purpose: "Read accepted history or a submission disposition" },
    { method: "POST", path: "/api/districts/operations", purpose: "Validate and submit a signed district operation" },
    { method: "GET", path: "/api/districts/state", purpose: "Read or independently reconstruct derived district state" },
    { method: "POST", path: "/mcp", purpose: "Remote AI-platform knowledge and grounding tools" },
    { method: "GET", path: "/api/knowledge/search", purpose: "Search source-bound knowledge records" },
    { method: "GET", path: "/api/knowledge/coverage", purpose: "Topic domain/facet coverage and gap map" },
    { method: "GET", path: "/api/language", purpose: "Language-force and operative-effect schema" },
    { method: "GET", path: "/api/language/acts", purpose: "Query source-bound language acts" },
    { method: "POST", path: "/api/language/acts", purpose: "Record a source-bound language act" },
    { method: "GET", path: "/api/language/effects", purpose: "Query operative effects" },
    { method: "POST", path: "/api/language/effects", purpose: "Record an evidence-bound operative effect" },
    { method: "GET", path: "/api/language/graph", purpose: "Query or export the joined language/effect graph" },
    { method: "POST", path: "/api/respond", purpose: "Natural-language input to graph/table response" },
    { method: "POST", path: "/api/events", purpose: "Mapped-response audit event ingestion" },
    { method: "GET", path: "/api/responses", purpose: "Recent persisted responses" },
    { method: "GET", path: "/api/graph", purpose: "Collective graph nodes and typed edges" },
  ],
} as const;

function clean(value: string, maximum = 10_000) {
  return value.replace(/\s+/g, " ").trim().slice(0, maximum);
}

function countKeywordMatches(text: string, keywords: string[]) {
  return keywords.reduce((count, keyword) => {
    return count + (text.includes(keyword) ? 1 : 0);
  }, 0);
}

function makeId(prefix: string) {
  const random = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `${prefix}:${random}`;
}

function csvCell(value: string) {
  return `"${value.replace(/"/g, '""')}"`;
}

function buildCsv(columns: CategoryDefinition[], row: Record<CategoryKey, string>) {
  const header = columns.map((column) => csvCell(column.label)).join(",");
  const values = columns.map((column) => csvCell(row[column.key])).join(",");
  return `${header}\n${values}`;
}

function compactPrompt(prompt: string) {
  return prompt.length > 260 ? `${prompt.slice(0, 257)}…` : prompt;
}

function describeSources(sources: ProtocolSource[]) {
  if (!sources.length) {
    return "User-supplied prompt • no external source attached";
  }
  return sources
    .map((source) => {
      const title = clean(source.title, 180) || "Untitled source";
      return source.url ? `${title} — ${clean(source.url, 500)}` : title;
    })
    .join(" | ");
}

function contentForCategory(
  key: CategoryKey,
  prompt: string,
  sources: ProtocolSource[],
  matches: number,
) {
  if (key === "response_control") {
    return `Operational • natural-language request captured • ${compactPrompt(prompt)}`;
  }
  if (key === "provenance") {
    return describeSources(sources);
  }
  if (key === "ai_protocol") {
    return "Provider-independent web service • append-only response event • graph/table/CSV representations emitted together";
  }
  if (key === "verification") {
    return `Schema v${PROTOCOL_VERSION} • all ${CATEGORY_KEYS.length} categories present • dynamic ordering check applied • ${sources.length} attached source${sources.length === 1 ? "" : "s"}`;
  }
  if (key === "risk_limits") {
    return "Blank cells mean not asserted, not omitted • deterministic mode structures the request but does not invent external facts";
  }
  if (!matches) {
    return "";
  }

  const detected: Record<Exclude<CategoryKey, "response_control" | "provenance" | "ai_protocol" | "verification" | "risk_limits">, string> = {
    legal:
      "Legal signal detected • authority, rule, application, procedure, and requested remedy remain separately provable fields",
    standing:
      "Standing signal detected • injury, causation, redressability, jurisdiction, and representative capacity require explicit support",
    commons:
      "Commons signal detected • shared resource, access conditions, beneficiaries, and stewardship are active dimensions",
    social_contract:
      "Social-contract signal detected • asserted right, reciprocal duty, legitimacy, breach, and remedy remain distinct",
    linguistic:
      "Language signal detected • term, source-bound definition, ambiguity, interpretation, and language layer must remain distinguishable",
    emoji_rider:
      "Glyph signal detected • symbol, syntax, structure, intended semantics, and Unicode form remain separately addressable",
  };
  return detected[key as keyof typeof detected] ?? "";
}

function buildGraph(
  id: string,
  prompt: string,
  columns: CategoryDefinition[],
  row: Record<CategoryKey, string>,
  sources: ProtocolSource[],
) {
  const promptId = `${id}:prompt`;
  const nodes: GraphNode[] = [
    { id: promptId, type: "Prompt", label: "Natural-language input", value: prompt },
    { id, type: "Response", label: "High-dimensional response", value: PROTOCOL_VERSION },
  ];
  const edges: GraphEdge[] = [
    { id: `${id}:edge:answers`, subject: promptId, predicate: "answeredBy", object: id },
  ];

  columns.forEach((column) => {
    const nodeId = `${id}:category:${column.key}`;
    nodes.push({
      id: nodeId,
      type: "Category",
      label: column.label,
      value: row[column.key],
      empty: !row[column.key],
    });
    edges.push({
      id: `${id}:edge:${column.key}`,
      subject: id,
      predicate: "hasCategory",
      object: nodeId,
    });
  });

  sources.forEach((source, index) => {
    const sourceId = `${id}:source:${index + 1}`;
    nodes.push({
      id: sourceId,
      type: "Source",
      label: clean(source.title, 180) || `Source ${index + 1}`,
      value: source.url ? clean(source.url, 500) : undefined,
    });
    edges.push({
      id: `${id}:edge:source:${index + 1}`,
      subject: id,
      predicate: "derivesFrom",
      object: sourceId,
    });
  });

  return { nodes, edges };
}

export function composeProtocolResponse(
  rawPrompt: string,
  rawSources: ProtocolSource[] = [],
  districtContext?: DistrictResponseContext,
): ProtocolResponse {
  const prompt = clean(rawPrompt);
  if (!prompt) {
    throw new Error("A natural-language request is required.");
  }

  const sources = rawSources
    .map((source) => ({
      title: clean(source.title ?? "", 180),
      url: source.url ? clean(source.url, 500) : undefined,
      kind: source.kind ? clean(source.kind, 80) : undefined,
    }))
    .filter((source) => source.title || source.url)
    .slice(0, 12);
  const lower = prompt.toLocaleLowerCase();
  const matchCounts = new Map<CategoryKey, number>();

  CATEGORY_DEFINITIONS.forEach((category) => {
    matchCounts.set(category.key, countKeywordMatches(lower, category.keywords));
  });

  const row = Object.fromEntries(
    CATEGORY_DEFINITIONS.map((category) => [
      category.key,
      contentForCategory(category.key, prompt, sources, matchCounts.get(category.key) ?? 0),
    ]),
  ) as Record<CategoryKey, string>;

  if (districtContext) {
    row.response_control = `Operational district query • ${districtContext.districtId} • ${compactPrompt(prompt)}`;
    row.provenance = [
      `Accepted-history root ${districtContext.historyRoot}`,
      `derived-state root ${districtContext.stateRoot}`,
      `active ruleset ${districtContext.activeRulesetId}`,
      describeSources(sources),
    ].join(" • ");
    row.commons = `${districtContext.name} • ${districtContext.status} • ${districtContext.acceptedOperationCount} accepted operations • ${districtContext.activeMemberCount} active members • ${districtContext.proposalStates.length ? districtContext.proposalStates.join(" | ") : "no proposals"}`;
    row.legal = `${districtContext.activeAuthorityCount} active scoped authority grant${districtContext.activeAuthorityCount === 1 ? "" : "s"} • authority is derived from accepted operations under ${districtContext.activeRulesetId}`;
    row.ai_protocol = `Same signed dap/0.2 envelopes cross HTTP and MCP • district time ${districtContext.districtTime} • no client or validator-side direct state mutation`;
    row.verification = `Independent replay • history root ${districtContext.historyRootMatches ? "MATCH" : "MISMATCH"} • state root ${districtContext.stateRootMatches ? "MATCH" : "MISMATCH"}`;
    row.risk_limits = `${districtContext.pendingOperationCount} accepted pending • ${districtContext.unresolvedConflictCount} unresolved conflicts • a matching root proves deterministic reconstruction, not the truth of submitted evidence`;
  }

  const fixedScores: Partial<Record<CategoryKey, number>> = {
    response_control: 150,
    provenance: sources.length ? 145 : 92,
    verification: 120,
    ai_protocol: 110,
    risk_limits: 100,
  };

  const columns = [...CATEGORY_DEFINITIONS].sort((a, b) => {
    const score = (category: CategoryDefinition) => {
      const matchScore = (matchCounts.get(category.key) ?? 0) * 220;
      return (row[category.key] ? 10_000 : 0) + matchScore + (fixedScores[category.key] ?? 0);
    };
    const difference = score(b) - score(a);
    return difference || CATEGORY_KEYS.indexOf(a.key) - CATEGORY_KEYS.indexOf(b.key);
  });

  const id = makeId("response");
  return {
    id,
    schemaVersion: PROTOCOL_VERSION,
    prompt,
    createdAt: new Date().toISOString(),
    columns,
    row,
    csv: buildCsv(columns, row),
    graph: buildGraph(id, prompt, columns, row, sources),
    sourceCount: sources.length,
  };
}

function bytesToHex(bytes: ArrayBuffer) {
  return Array.from(new Uint8Array(bytes), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function semanticEventContent(response: ProtocolResponse) {
  return {
    protocolVersion: response.schemaVersion,
    prompt: response.prompt,
    columns: response.columns.map((column) => column.key),
    row: response.row,
    sources: response.graph.nodes
      .filter((node) => node.type === "Source")
      .map((node) => ({ label: node.label, value: node.value ?? "" })),
  };
}

export async function createResponseEvent(
  response: ProtocolResponse,
  consentScope: ConsentScope = "collective",
): Promise<ResponseEvent> {
  const semanticContent = JSON.stringify(semanticEventContent(response));
  const digest = await globalThis.crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(semanticContent),
  );
  const hash = bytesToHex(digest);
  const originalResponseId = response.id;
  const stableResponseId = `response:sha256:${hash}`;
  const replaceResponseId = (value: string) =>
    value.startsWith(originalResponseId)
      ? `${stableResponseId}${value.slice(originalResponseId.length)}`
      : value;
  const stableResponse: ProtocolResponse = {
    ...response,
    id: stableResponseId,
    graph: {
      nodes: response.graph.nodes.map((node) => ({
        ...node,
        id: replaceResponseId(node.id),
      })),
      edges: response.graph.edges.map((edge) => ({
        ...edge,
        id: replaceResponseId(edge.id),
        subject: replaceResponseId(edge.subject),
        object: replaceResponseId(edge.object),
      })),
    },
  };
  const category = response.columns.find(
    (column) =>
      response.row[column.key] &&
      !["response_control", "provenance", "verification", "ai_protocol", "risk_limits"].includes(column.key),
  )?.key ?? "general";
  const month = response.createdAt.slice(0, 7);
  const metadata: ResponseEventMetadata = {
    eventId: `urn:caeluviim:event:sha256:${hash}`,
    eventType: "caeluviim.response.created",
    responseId: stableResponseId,
    protocolVersion: response.schemaVersion,
    contentHash: `sha256:${hash}`,
    consentScope,
    partitionKey: `${category}/${month}`,
    ingestionStatus: "projected",
    createdAt: response.createdAt,
  };

  return {
    ...metadata,
    response: { ...stableResponse, event: metadata },
  };
}

export function validatesProtocolResponse(value: unknown): value is ProtocolResponse {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<ProtocolResponse>;
  if (
    typeof candidate.id !== "string" ||
    candidate.schemaVersion !== PROTOCOL_VERSION ||
    typeof candidate.prompt !== "string" ||
    !candidate.row ||
    !Array.isArray(candidate.columns) ||
    !candidate.graph
  ) {
    return false;
  }
  const columnKeys = new Set(candidate.columns.map((column) => column.key));
  return CATEGORY_KEYS.every(
    (key) => columnKeys.has(key) && typeof candidate.row?.[key] === "string",
  );
}
