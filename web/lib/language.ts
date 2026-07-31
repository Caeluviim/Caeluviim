export const LANGUAGE_FORCE_PROTOCOL_VERSION = "caeluviim-language-force/1.0" as const;

export const LANGUAGE_MEDIA = [
  "spoken",
  "written",
  "signed",
  "glyphic",
  "code",
  "multimodal",
  "other",
] as const;

export const LANGUAGE_ACT_TYPES = [
  "assertive",
  "directive",
  "commissive",
  "expressive",
  "declarative",
  "interrogative",
  "constitutive",
  "procedural",
  "evidentiary",
  "interpretive",
  "metalinguistic",
  "symbolic",
] as const;

export const LANGUAGE_ACT_STATUSES = [
  "recorded",
  "claimed",
  "verified",
  "disputed",
  "retracted",
  "superseded",
] as const;

export const AUTHORITY_STATUSES = [
  "none",
  "claimed",
  "verified",
  "disputed",
  "revoked",
] as const;

export const DEONTIC_OPERATORS = [
  "none",
  "obligation",
  "prohibition",
  "permission",
  "right",
  "power",
  "liability",
  "immunity",
  "disability",
] as const;

export const EFFECT_KINDS = [
  "communicative",
  "interpretive",
  "causal",
  "institutional",
  "normative",
  "procedural",
  "evidentiary",
  "computational",
  "symbolic",
] as const;

export const EFFECT_OPERATORS = [
  "creates",
  "modifies",
  "terminates",
  "authorizes",
  "obligates",
  "prohibits",
  "permits",
  "waives",
  "revokes",
  "suspends",
  "triggers",
  "notifies",
  "records",
  "counts_as",
  "defines",
  "classifies",
  "causes",
  "prevents",
  "contests",
  "supersedes",
  "nullifies",
  "no_effect",
] as const;

export const EFFECT_STATUSES = [
  "proposed",
  "claimed",
  "pending",
  "effective",
  "contested",
  "superseded",
  "void",
  "expired",
  "reversed",
  "no_effect",
] as const;

export type LanguageMedium = (typeof LANGUAGE_MEDIA)[number];
export type LanguageActType = (typeof LANGUAGE_ACT_TYPES)[number];
export type LanguageActStatus = (typeof LANGUAGE_ACT_STATUSES)[number];
export type AuthorityStatus = (typeof AUTHORITY_STATUSES)[number];
export type DeonticOperator = (typeof DEONTIC_OPERATORS)[number];
export type EffectKind = (typeof EFFECT_KINDS)[number];
export type EffectOperator = (typeof EFFECT_OPERATORS)[number];
export type EffectStatus = (typeof EFFECT_STATUSES)[number];

export type LanguageActInput = {
  label: string;
  expressionRecordId: string;
  contentRecordIds: string[];
  interpretationRecordIds?: string[];
  speakerRecordId: string;
  addresseeRecordIds?: string[];
  contextRecordIds?: string[];
  sourceRecordId: string;
  evidenceRecordIds: string[];
  authorityRecordIds?: string[];
  actType: LanguageActType;
  force: string;
  medium: LanguageMedium;
  language: string;
  script?: string;
  polarity: "affirmative" | "negative";
  deonticOperator: DeonticOperator;
  status: LanguageActStatus;
  authorityStatus: AuthorityStatus;
  conditions?: string[];
  scopePath?: string[];
  jurisdiction?: string;
  occurredAt?: string;
  districtId?: string;
};

export type LanguageAct = LanguageActInput & {
  id: string;
  contentHash: string;
  createdAt: string;
  referenceComplete: true;
};

export type OperativeEffectInput = {
  label: string;
  languageActId: string;
  effectKind: EffectKind;
  operator: EffectOperator;
  status: EffectStatus;
  description: string;
  targetRecordIds: string[];
  bearerRecordIds?: string[];
  beneficiaryRecordIds?: string[];
  basisRecordIds: string[];
  authorityRecordIds?: string[];
  evidenceRecordIds: string[];
  conditions?: string[];
  scopePath?: string[];
  jurisdiction?: string;
  effectiveFrom?: string;
  effectiveUntil?: string;
  realizedByOperationId?: string;
};

export type OperativeEffect = OperativeEffectInput & {
  id: string;
  contentHash: string;
  createdAt: string;
  referenceComplete: true;
};

export type LanguageForceQuery = {
  query?: string;
  actTypes?: LanguageActType[];
  forces?: string[];
  effectKinds?: EffectKind[];
  effectStatuses?: EffectStatus[];
  recordId?: string;
  districtId?: string;
  jurisdiction?: string;
  limit?: number;
};

export type LanguageGraphNode = {
  id: string;
  type: string;
  label: string;
  status?: string;
  properties?: Record<string, unknown>;
};

export type LanguageGraphEdge = {
  id: string;
  subject: string;
  predicate: string;
  object: string;
  evidenceRecordIds: string[];
};

function clean(value: string, maximum: number) {
  return value.replace(/\s+/g, " ").trim().slice(0, maximum);
}

function cleanList(values: string[] | undefined, maximumItems: number, maximumLength: number) {
  return [...new Set((values ?? []).map((value) => clean(value, maximumLength)).filter(Boolean))].slice(
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

function normalizeDate(value: string | undefined) {
  if (!value) return undefined;
  const cleanValue = clean(value, 80);
  if (!cleanValue || Number.isNaN(Date.parse(cleanValue))) {
    throw new Error(`Invalid date-time: ${value}`);
  }
  return new Date(cleanValue).toISOString();
}

export async function createLanguageAct(input: LanguageActInput): Promise<LanguageAct> {
  const normalized: LanguageActInput = {
    label: clean(input.label, 240),
    expressionRecordId: clean(input.expressionRecordId, 500),
    contentRecordIds: cleanList(input.contentRecordIds, 40, 500),
    interpretationRecordIds: cleanList(input.interpretationRecordIds, 40, 500),
    speakerRecordId: clean(input.speakerRecordId, 500),
    addresseeRecordIds: cleanList(input.addresseeRecordIds, 40, 500),
    contextRecordIds: cleanList(input.contextRecordIds, 40, 500),
    sourceRecordId: clean(input.sourceRecordId, 500),
    evidenceRecordIds: cleanList(input.evidenceRecordIds, 40, 500),
    authorityRecordIds: cleanList(input.authorityRecordIds, 40, 500),
    actType: input.actType,
    force: clean(input.force, 180),
    medium: input.medium,
    language: clean(input.language, 80),
    script: input.script ? clean(input.script, 80) : undefined,
    polarity: input.polarity,
    deonticOperator: input.deonticOperator,
    status: input.status,
    authorityStatus: input.authorityStatus,
    conditions: cleanList(input.conditions, 40, 1_000),
    scopePath: cleanList(input.scopePath, 40, 240),
    jurisdiction: input.jurisdiction ? clean(input.jurisdiction, 180) : undefined,
    occurredAt: normalizeDate(input.occurredAt),
    districtId: input.districtId ? clean(input.districtId, 500) : undefined,
  };
  if (
    !normalized.label ||
    !normalized.expressionRecordId ||
    !normalized.contentRecordIds.length ||
    !normalized.speakerRecordId ||
    !normalized.sourceRecordId ||
    !normalized.evidenceRecordIds.length ||
    !normalized.force ||
    !normalized.language
  ) {
    throw new Error(
      "Language acts require an expression, content, speaker, source, evidence, language, and explicit force.",
    );
  }
  if (
    normalized.authorityStatus === "verified" &&
    !normalized.authorityRecordIds?.length
  ) {
    throw new Error("Verified language authority requires at least one authority record.");
  }
  const semanticContent = JSON.stringify(normalized);
  const hash = await sha256(semanticContent);
  return {
    ...normalized,
    id: `urn:caeluviim:language-act:sha256:${hash}`,
    contentHash: `sha256:${hash}`,
    createdAt: new Date().toISOString(),
    referenceComplete: true,
  };
}

export async function createOperativeEffect(
  input: OperativeEffectInput,
): Promise<OperativeEffect> {
  const normalized: OperativeEffectInput = {
    label: clean(input.label, 240),
    languageActId: clean(input.languageActId, 500),
    effectKind: input.effectKind,
    operator: input.operator,
    status: input.status,
    description: clean(input.description, 10_000),
    targetRecordIds: cleanList(input.targetRecordIds, 40, 500),
    bearerRecordIds: cleanList(input.bearerRecordIds, 40, 500),
    beneficiaryRecordIds: cleanList(input.beneficiaryRecordIds, 40, 500),
    basisRecordIds: cleanList(input.basisRecordIds, 40, 500),
    authorityRecordIds: cleanList(input.authorityRecordIds, 40, 500),
    evidenceRecordIds: cleanList(input.evidenceRecordIds, 40, 500),
    conditions: cleanList(input.conditions, 40, 1_000),
    scopePath: cleanList(input.scopePath, 40, 240),
    jurisdiction: input.jurisdiction ? clean(input.jurisdiction, 180) : undefined,
    effectiveFrom: normalizeDate(input.effectiveFrom),
    effectiveUntil: normalizeDate(input.effectiveUntil),
    realizedByOperationId: input.realizedByOperationId
      ? clean(input.realizedByOperationId, 500)
      : undefined,
  };
  if (
    !normalized.label ||
    !normalized.languageActId ||
    !normalized.description ||
    !normalized.targetRecordIds.length ||
    !normalized.basisRecordIds.length ||
    !normalized.evidenceRecordIds.length
  ) {
    throw new Error(
      "Operative effects require a language act, description, target, basis, and evidence.",
    );
  }
  if (
    normalized.status === "effective" &&
    ["institutional", "normative", "procedural"].includes(normalized.effectKind) &&
    !normalized.authorityRecordIds?.length &&
    !normalized.realizedByOperationId
  ) {
    throw new Error(
      "An effective institutional, normative, or procedural effect requires authority records or a realized signed operation.",
    );
  }
  if (
    normalized.effectiveFrom &&
    normalized.effectiveUntil &&
    normalized.effectiveFrom > normalized.effectiveUntil
  ) {
    throw new Error("effectiveFrom must not be later than effectiveUntil.");
  }
  const semanticContent = JSON.stringify(normalized);
  const hash = await sha256(semanticContent);
  return {
    ...normalized,
    id: `urn:caeluviim:operative-effect:sha256:${hash}`,
    contentHash: `sha256:${hash}`,
    createdAt: new Date().toISOString(),
    referenceComplete: true,
  };
}

export function referencedRecordIds(act: LanguageAct) {
  return [
    act.expressionRecordId,
    ...act.contentRecordIds,
    ...(act.interpretationRecordIds ?? []),
    act.speakerRecordId,
    ...(act.addresseeRecordIds ?? []),
    ...(act.contextRecordIds ?? []),
    act.sourceRecordId,
    ...act.evidenceRecordIds,
    ...(act.authorityRecordIds ?? []),
  ];
}

export function effectReferencedRecordIds(effect: OperativeEffect) {
  return [
    ...effect.targetRecordIds,
    ...(effect.bearerRecordIds ?? []),
    ...(effect.beneficiaryRecordIds ?? []),
    ...effect.basisRecordIds,
    ...(effect.authorityRecordIds ?? []),
    ...effect.evidenceRecordIds,
  ];
}

async function graphEdge(
  subject: string,
  predicate: string,
  object: string,
  evidenceRecordIds: string[],
): Promise<LanguageGraphEdge> {
  const hash = await sha256(JSON.stringify({ subject, predicate, object, evidenceRecordIds }));
  return {
    id: `urn:caeluviim:language-edge:sha256:${hash}`,
    subject,
    predicate,
    object,
    evidenceRecordIds,
  };
}

export async function buildLanguageGraph(
  acts: LanguageAct[],
  effects: OperativeEffect[],
  recordNodes: LanguageGraphNode[],
) {
  const nodes = new Map<string, LanguageGraphNode>(
    recordNodes.map((node) => [node.id, node]),
  );
  const edgePromises: Array<Promise<LanguageGraphEdge>> = [];
  acts.forEach((act) => {
    nodes.set(act.id, {
      id: act.id,
      type: "LanguageAct",
      label: act.label,
      status: act.status,
      properties: {
        protocolVersion: LANGUAGE_FORCE_PROTOCOL_VERSION,
        actType: act.actType,
        force: act.force,
        medium: act.medium,
        language: act.language,
        script: act.script ?? null,
        polarity: act.polarity,
        deonticOperator: act.deonticOperator,
        authorityStatus: act.authorityStatus,
        conditions: act.conditions ?? [],
        scopePath: act.scopePath ?? [],
        jurisdiction: act.jurisdiction ?? null,
        occurredAt: act.occurredAt ?? null,
        districtId: act.districtId ?? null,
        contentHash: act.contentHash,
      },
    });
    edgePromises.push(graphEdge(act.id, "expressedAs", act.expressionRecordId, act.evidenceRecordIds));
    act.contentRecordIds.forEach((id) =>
      edgePromises.push(graphEdge(act.id, "hasContent", id, act.evidenceRecordIds)),
    );
    (act.interpretationRecordIds ?? []).forEach((id) =>
      edgePromises.push(graphEdge(act.id, "hasInterpretation", id, act.evidenceRecordIds)),
    );
    edgePromises.push(graphEdge(act.id, "performedBy", act.speakerRecordId, act.evidenceRecordIds));
    (act.addresseeRecordIds ?? []).forEach((id) =>
      edgePromises.push(graphEdge(act.id, "addressedTo", id, act.evidenceRecordIds)),
    );
    (act.contextRecordIds ?? []).forEach((id) =>
      edgePromises.push(graphEdge(act.id, "hasContext", id, act.evidenceRecordIds)),
    );
    edgePromises.push(graphEdge(act.id, "documentedBy", act.sourceRecordId, act.evidenceRecordIds));
    act.evidenceRecordIds.forEach((id) =>
      edgePromises.push(graphEdge(act.id, "supportedBy", id, act.evidenceRecordIds)),
    );
    (act.authorityRecordIds ?? []).forEach((id) =>
      edgePromises.push(graphEdge(act.id, "claimsAuthorityFrom", id, act.evidenceRecordIds)),
    );
  });
  effects.forEach((effect) => {
    nodes.set(effect.id, {
      id: effect.id,
      type: "OperativeEffect",
      label: effect.label,
      status: effect.status,
      properties: {
        effectKind: effect.effectKind,
        operator: effect.operator,
        description: effect.description,
        conditions: effect.conditions ?? [],
        scopePath: effect.scopePath ?? [],
        jurisdiction: effect.jurisdiction ?? null,
        effectiveFrom: effect.effectiveFrom ?? null,
        effectiveUntil: effect.effectiveUntil ?? null,
        realizedByOperationId: effect.realizedByOperationId ?? null,
        contentHash: effect.contentHash,
      },
    });
    edgePromises.push(
      graphEdge(effect.id, "arisesFrom", effect.languageActId, effect.evidenceRecordIds),
    );
    effect.targetRecordIds.forEach((id) =>
      edgePromises.push(graphEdge(effect.id, "affects", id, effect.evidenceRecordIds)),
    );
    (effect.bearerRecordIds ?? []).forEach((id) =>
      edgePromises.push(graphEdge(effect.id, "binds", id, effect.evidenceRecordIds)),
    );
    (effect.beneficiaryRecordIds ?? []).forEach((id) =>
      edgePromises.push(graphEdge(effect.id, "benefits", id, effect.evidenceRecordIds)),
    );
    effect.basisRecordIds.forEach((id) =>
      edgePromises.push(graphEdge(effect.id, "basedOn", id, effect.evidenceRecordIds)),
    );
    (effect.authorityRecordIds ?? []).forEach((id) =>
      edgePromises.push(graphEdge(effect.id, "authorizedBy", id, effect.evidenceRecordIds)),
    );
    effect.evidenceRecordIds.forEach((id) =>
      edgePromises.push(graphEdge(effect.id, "supportedBy", id, effect.evidenceRecordIds)),
    );
    if (effect.realizedByOperationId) {
      const operationId = effect.realizedByOperationId;
      nodes.set(operationId, {
        id: operationId,
        type: "DapOperation",
        label: operationId,
      });
      edgePromises.push(
        graphEdge(effect.id, "realizedBy", operationId, effect.evidenceRecordIds),
      );
    }
  });
  const edges = await Promise.all(edgePromises);
  return {
    protocolVersion: LANGUAGE_FORCE_PROTOCOL_VERSION,
    nodes: [...nodes.values()],
    edges,
  };
}

function iri(value: string) {
  return `<${value.replace(/[<>"{}|^`\\]/g, "")}>`;
}

function literal(value: string) {
  return `"${value
    .replace(/\\/g, "\\\\")
    .replace(/"/g, '\\"')
    .replace(/\r/g, "\\r")
    .replace(/\n/g, "\\n")}"`;
}

export function languageGraphToNQuads(graph: {
  nodes: LanguageGraphNode[];
  edges: LanguageGraphEdge[];
}) {
  const core = "https://caeluviim.org/ontology/core#";
  const rdfType = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type";
  const label = "http://www.w3.org/2000/01/rdf-schema#label";
  const lines: string[] = [];
  graph.nodes.forEach((node) => {
    lines.push(`${iri(node.id)} ${iri(rdfType)} ${iri(`${core}${node.type}`)} .`);
    lines.push(`${iri(node.id)} ${iri(label)} ${literal(node.label)} .`);
    if (node.status) {
      lines.push(`${iri(node.id)} ${iri(`${core}status`)} ${literal(node.status)} .`);
    }
    Object.entries(node.properties ?? {}).forEach(([key, value]) => {
      if (value === null || value === undefined || value === "") return;
      const values = Array.isArray(value) ? value : [value];
      values.forEach((item) => {
        if (item === null || item === undefined || item === "") return;
        const encoded = typeof item === "object" ? JSON.stringify(item) : String(item);
        lines.push(`${iri(node.id)} ${iri(`${core}${key}`)} ${literal(encoded)} .`);
      });
    });
  });
  graph.edges.forEach((edge) => {
    const predicate = edge.predicate.includes("://")
      ? edge.predicate
      : `${core}${edge.predicate}`;
    lines.push(`${iri(edge.subject)} ${iri(predicate)} ${iri(edge.object)} .`);
    lines.push(`${iri(edge.id)} ${iri(rdfType)} ${iri(`${core}EvidenceBoundRelation`)} .`);
    lines.push(`${iri(edge.id)} ${iri(`${core}subject`)} ${iri(edge.subject)} .`);
    lines.push(`${iri(edge.id)} ${iri(`${core}predicate`)} ${iri(predicate)} .`);
    lines.push(`${iri(edge.id)} ${iri(`${core}object`)} ${iri(edge.object)} .`);
    edge.evidenceRecordIds.forEach((evidenceId) => {
      lines.push(`${iri(edge.id)} ${iri(`${core}supportedBy`)} ${iri(evidenceId)} .`);
    });
  });
  return `${lines.join("\n")}\n`;
}

export function languageGraphToJsonLd(graph: {
  protocolVersion: string;
  nodes: LanguageGraphNode[];
  edges: LanguageGraphEdge[];
}) {
  const context = {
    cael: "https://caeluviim.org/ontology/core#",
    prov: "http://www.w3.org/ns/prov#",
    label: "http://www.w3.org/2000/01/rdf-schema#label",
    status: "cael:status",
    subject: { "@id": "cael:subject", "@type": "@id" },
    predicate: { "@id": "cael:predicate", "@type": "@id" },
    object: { "@id": "cael:object", "@type": "@id" },
    evidence: { "@id": "cael:supportedBy", "@type": "@id" },
  };
  return {
    "@context": context,
    protocolVersion: graph.protocolVersion,
    "@graph": [
      ...graph.nodes.map((node) => ({
        "@id": node.id,
        "@type": `cael:${node.type}`,
        label: node.label,
        status: node.status,
        ...node.properties,
      })),
      ...graph.edges.map((edge) => ({
        "@id": edge.id,
        "@type": "cael:EvidenceBoundRelation",
        subject: edge.subject,
        predicate: `cael:${edge.predicate}`,
        object: edge.object,
        evidence: edge.evidenceRecordIds,
      })),
    ],
  };
}
