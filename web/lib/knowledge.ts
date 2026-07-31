export const KNOWLEDGE_RECORD_TYPES = [
  "Source",
  "Document",
  "Conversation",
  "Message",
  "AgentRun",
  "Topic",
  "Entity",
  "Actor",
  "Context",
  "Process",
  "Substance",
  "Claim",
  "Definition",
  "LanguageExpression",
  "Proposition",
  "Interpretation",
  "LanguageAct",
  "OperativeEffect",
  "Condition",
  "Authority",
  "Rule",
  "Theory",
  "Observation",
  "Event",
  "Protocol",
] as const;

export const KNOWLEDGE_DOMAINS = [
  "biology",
  "medicine",
  "law",
  "regulation",
  "economics",
  "international",
  "history",
  "academia",
  "technology",
  "ethics",
  "social",
] as const;

export type KnowledgeRecordType = (typeof KNOWLEDGE_RECORD_TYPES)[number];
export type KnowledgeDomain = (typeof KNOWLEDGE_DOMAINS)[number];

export type KnowledgeRecordInput = {
  recordType: KnowledgeRecordType;
  label: string;
  content: string;
  domains: KnowledgeDomain[];
  topics: string[];
  sourceTitle: string;
  sourceUrl: string;
  sourceLocator: string;
  sourceExcerpt: string;
  constructionRule: string;
  conflictGroup?: string;
  language?: string;
  jurisdiction?: string;
  sourcePublishedAt?: string;
};

export type KnowledgeRecord = KnowledgeRecordInput & {
  id: string;
  contentHash: string;
  sourceHash: string;
  sourceRetrievedAt: string;
  createdAt: string;
  provenanceComplete: true;
};

export type KnowledgeEdgeInput = {
  subjectId: string;
  predicate: string;
  objectId: string;
  evidenceRecordIds: string[];
};

export type KnowledgeEdge = KnowledgeEdgeInput & {
  id: string;
  createdAt: string;
};

function clean(value: string, maximum: number) {
  return value.replace(/\s+/g, " ").trim().slice(0, maximum);
}

function cleanList(values: string[], maximumItems: number, maximumLength: number) {
  return [...new Set(values.map((value) => clean(value, maximumLength)).filter(Boolean))].slice(
    0,
    maximumItems,
  );
}

function bytesToHex(bytes: ArrayBuffer) {
  return Array.from(new Uint8Array(bytes), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

async function sha256(value: string) {
  const digest = await globalThis.crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(value),
  );
  return bytesToHex(digest);
}

export async function createKnowledgeRecord(input: KnowledgeRecordInput): Promise<KnowledgeRecord> {
  const normalized: KnowledgeRecordInput = {
    recordType: input.recordType,
    label: clean(input.label, 240),
    content: clean(input.content, 50_000),
    domains: cleanList(input.domains, 12, 80) as KnowledgeDomain[],
    topics: cleanList(input.topics, 40, 180),
    sourceTitle: clean(input.sourceTitle, 500),
    sourceUrl: clean(input.sourceUrl, 2_000),
    sourceLocator: clean(input.sourceLocator, 500),
    sourceExcerpt: clean(input.sourceExcerpt, 5_000),
    constructionRule: clean(input.constructionRule, 2_000),
    conflictGroup: input.conflictGroup ? clean(input.conflictGroup, 240) : undefined,
    language: input.language ? clean(input.language, 80) : "en",
    jurisdiction: input.jurisdiction ? clean(input.jurisdiction, 180) : undefined,
    sourcePublishedAt: input.sourcePublishedAt
      ? clean(input.sourcePublishedAt, 80)
      : undefined,
  };
  if (
    !normalized.label ||
    !normalized.content ||
    !normalized.domains.length ||
    !normalized.topics.length ||
    !normalized.sourceTitle ||
    !normalized.sourceUrl ||
    !normalized.sourceLocator ||
    !normalized.sourceExcerpt ||
    !normalized.constructionRule
  ) {
    throw new Error(
      "Knowledge records require content, domain/topic classification, an exact source locator and excerpt, and a construction rule.",
    );
  }
  const invalidDomain = normalized.domains.find(
    (domain) => !KNOWLEDGE_DOMAINS.includes(domain),
  );
  if (invalidDomain) {
    throw new Error(`Unsupported knowledge domain: ${invalidDomain}`);
  }

  const semanticContent = JSON.stringify(normalized);
  const [recordHash, sourceHash] = await Promise.all([
    sha256(semanticContent),
    sha256(
      JSON.stringify({
        title: normalized.sourceTitle,
        url: normalized.sourceUrl,
        locator: normalized.sourceLocator,
        excerpt: normalized.sourceExcerpt,
      }),
    ),
  ]);
  const now = new Date().toISOString();
  return {
    ...normalized,
    id: `urn:caeluviim:knowledge:sha256:${recordHash}`,
    contentHash: `sha256:${recordHash}`,
    sourceHash: `sha256:${sourceHash}`,
    sourceRetrievedAt: now,
    createdAt: now,
    provenanceComplete: true,
  };
}

export async function createKnowledgeEdge(input: KnowledgeEdgeInput): Promise<KnowledgeEdge> {
  const normalized: KnowledgeEdgeInput = {
    subjectId: clean(input.subjectId, 500),
    predicate: clean(input.predicate, 180),
    objectId: clean(input.objectId, 500),
    evidenceRecordIds: cleanList(input.evidenceRecordIds, 40, 500),
  };
  if (
    !normalized.subjectId ||
    !normalized.predicate ||
    !normalized.objectId ||
    !normalized.evidenceRecordIds.length
  ) {
    throw new Error("Knowledge edges require subject, predicate, object, and evidence records.");
  }
  const hash = await sha256(JSON.stringify(normalized));
  return {
    ...normalized,
    id: `urn:caeluviim:edge:sha256:${hash}`,
    createdAt: new Date().toISOString(),
  };
}
