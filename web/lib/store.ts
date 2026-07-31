import { env } from "cloudflare:workers";
import type { ProtocolResponse, ResponseEvent } from "./protocol";
import type { KnowledgeDomain, KnowledgeEdge, KnowledgeRecord } from "./knowledge";
import { getPlasmapheresisSeedRecords } from "./plasmapheresis-seed";
import {
  buildLanguageGraph,
  effectReferencedRecordIds,
  referencedRecordIds,
  type EffectKind,
  type EffectStatus,
  type LanguageAct,
  type LanguageActType,
  type LanguageForceQuery,
  type LanguageGraphNode,
  type OperativeEffect,
} from "./language";

const schemaStatements = [
  `CREATE TABLE IF NOT EXISTS knowledge_records_v2 (
    id TEXT PRIMARY KEY,
    record_type TEXT NOT NULL,
    label TEXT NOT NULL,
    content TEXT NOT NULL,
    domains_json TEXT NOT NULL,
    topics_json TEXT NOT NULL,
    source_title TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    source_excerpt TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    construction_rule TEXT NOT NULL,
    conflict_group TEXT,
    language TEXT NOT NULL,
    jurisdiction TEXT,
    source_published_at TEXT,
    source_retrieved_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
  )`,
  `CREATE INDEX IF NOT EXISTS knowledge_records_v2_type_idx
    ON knowledge_records_v2(record_type, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS knowledge_records_v2_conflict_idx
    ON knowledge_records_v2(conflict_group, created_at DESC)`,
  `CREATE TABLE IF NOT EXISTS knowledge_edges_v2 (
    edge_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_id TEXT NOT NULL,
    evidence_record_ids_json TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
  )`,
  `CREATE INDEX IF NOT EXISTS knowledge_edges_v2_subject_idx
    ON knowledge_edges_v2(subject_id, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS knowledge_edges_v2_object_idx
    ON knowledge_edges_v2(object_id, created_at DESC)`,
  `CREATE TABLE IF NOT EXISTS language_acts_v1 (
    id TEXT PRIMARY KEY,
    act_type TEXT NOT NULL,
    force TEXT NOT NULL,
    status TEXT NOT NULL,
    authority_status TEXT NOT NULL,
    medium TEXT NOT NULL,
    language TEXT NOT NULL,
    jurisdiction TEXT,
    district_id TEXT,
    source_record_id TEXT NOT NULL,
    speaker_record_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
  )`,
  `CREATE INDEX IF NOT EXISTS language_acts_v1_type_idx
    ON language_acts_v1(act_type, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS language_acts_v1_force_idx
    ON language_acts_v1(force, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS language_acts_v1_status_idx
    ON language_acts_v1(status, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS language_acts_v1_source_idx
    ON language_acts_v1(source_record_id, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS language_acts_v1_speaker_idx
    ON language_acts_v1(speaker_record_id, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS language_acts_v1_district_idx
    ON language_acts_v1(district_id, created_at DESC)`,
  `CREATE TABLE IF NOT EXISTS operative_effects_v1 (
    id TEXT PRIMARY KEY,
    language_act_id TEXT NOT NULL,
    effect_kind TEXT NOT NULL,
    operator TEXT NOT NULL,
    status TEXT NOT NULL,
    jurisdiction TEXT,
    realized_by_operation_id TEXT,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
  )`,
  `CREATE INDEX IF NOT EXISTS operative_effects_v1_act_idx
    ON operative_effects_v1(language_act_id, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS operative_effects_v1_kind_idx
    ON operative_effects_v1(effect_kind, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS operative_effects_v1_operator_idx
    ON operative_effects_v1(operator, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS operative_effects_v1_status_idx
    ON operative_effects_v1(status, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS operative_effects_v1_operation_idx
    ON operative_effects_v1(realized_by_operation_id, created_at DESC)`,
  `CREATE TABLE IF NOT EXISTS protocol_events (
    event_id TEXT PRIMARY KEY,
    response_id TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL,
    protocol_version TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    consent_scope TEXT NOT NULL,
    partition_key TEXT NOT NULL,
    ingestion_status TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
  )`,
  `CREATE INDEX IF NOT EXISTS protocol_events_partition_idx
    ON protocol_events(partition_key, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS protocol_events_scope_idx
    ON protocol_events(consent_scope, created_at DESC)`,
  `CREATE TABLE IF NOT EXISTS protocol_responses (
    id TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    column_order_json TEXT NOT NULL,
    row_json TEXT NOT NULL,
    csv_text TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
  )`,
  `CREATE INDEX IF NOT EXISTS protocol_responses_created_at_idx
    ON protocol_responses(created_at DESC)`,
  `CREATE TABLE IF NOT EXISTS graph_nodes (
    response_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    node_type TEXT NOT NULL,
    label TEXT NOT NULL,
    value TEXT,
    is_empty INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (response_id, node_id)
  )`,
  `CREATE TABLE IF NOT EXISTS graph_edges (
    response_id TEXT NOT NULL,
    edge_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_id TEXT NOT NULL,
    PRIMARY KEY (response_id, edge_id)
  )`,
];

function getOptionalDb(): D1Database | null {
  try {
    return (env as unknown as { DB?: D1Database }).DB ?? null;
  } catch {
    return null;
  }
}

async function ensureSchema(db: D1Database) {
  await db.batch(schemaStatements.map((statement) => db.prepare(statement)));
}

export function hasDatabaseBinding() {
  return Boolean(getOptionalDb());
}

export async function saveResponseEvent(event: ResponseEvent) {
  const db = getOptionalDb();
  if (!db) {
    return false;
  }

  await ensureSchema(db);
  const response = event.response;
  const operations = [
    db
      .prepare(
        `INSERT OR IGNORE INTO protocol_events
          (event_id, response_id, event_type, protocol_version, content_hash, consent_scope,
           partition_key, ingestion_status, payload_json, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      )
      .bind(
        event.eventId,
        event.responseId,
        event.eventType,
        event.protocolVersion,
        event.contentHash,
        event.consentScope,
        event.partitionKey,
        event.ingestionStatus,
        JSON.stringify(event),
        event.createdAt,
      ),
    db
      .prepare(
        `INSERT OR IGNORE INTO protocol_responses
          (id, prompt, schema_version, column_order_json, row_json, csv_text, payload_json, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      )
      .bind(
        response.id,
        response.prompt,
        response.schemaVersion,
        JSON.stringify(response.columns.map((column) => column.key)),
        JSON.stringify(response.row),
        response.csv,
        JSON.stringify(response),
        response.createdAt,
      ),
    ...response.graph.nodes.map((node) =>
      db
        .prepare(
          `INSERT OR REPLACE INTO graph_nodes
            (response_id, node_id, node_type, label, value, is_empty)
           VALUES (?, ?, ?, ?, ?, ?)`,
        )
        .bind(
          response.id,
          node.id,
          node.type,
          node.label,
          node.value ?? null,
          node.empty ? 1 : 0,
        ),
    ),
    ...response.graph.edges.map((edge) =>
      db
        .prepare(
          `INSERT OR REPLACE INTO graph_edges
            (response_id, edge_id, subject_id, predicate, object_id)
           VALUES (?, ?, ?, ?, ?)`,
        )
        .bind(response.id, edge.id, edge.subject, edge.predicate, edge.object),
    ),
  ];

  await db.batch(operations);
  return true;
}

export async function listProtocolResponses(limit = 12) {
  const db = getOptionalDb();
  if (!db) {
    return [] as ProtocolResponse[];
  }

  await ensureSchema(db);
  const safeLimit = Math.min(Math.max(Math.trunc(limit), 1), 50);
  const result = await db
    .prepare(
      `SELECT r.payload_json
       FROM protocol_responses r
       JOIN protocol_events e ON e.response_id = r.id
       WHERE e.consent_scope = 'collective'
       ORDER BY r.created_at DESC LIMIT ?`,
    )
    .bind(safeLimit)
    .all<{ payload_json: string }>();

  return result.results.flatMap((record) => {
    try {
      return [JSON.parse(record.payload_json) as ProtocolResponse];
    } catch {
      return [];
    }
  });
}

export async function listResponseEvents(limit = 25) {
  const db = getOptionalDb();
  if (!db) {
    return [] as ResponseEvent[];
  }

  await ensureSchema(db);
  const safeLimit = Math.min(Math.max(Math.trunc(limit), 1), 100);
  const result = await db
    .prepare(
      `SELECT payload_json FROM protocol_events
       WHERE consent_scope = 'collective'
       ORDER BY created_at DESC LIMIT ?`,
    )
    .bind(safeLimit)
    .all<{ payload_json: string }>();

  return result.results.flatMap((record) => {
    try {
      return [JSON.parse(record.payload_json) as ResponseEvent];
    } catch {
      return [];
    }
  });
}

export async function saveKnowledgeRecord(record: KnowledgeRecord) {
  const db = getOptionalDb();
  if (!db) return false;
  await ensureSchema(db);
  await db
    .prepare(
      `INSERT OR IGNORE INTO knowledge_records_v2
        (id, record_type, label, content, domains_json, topics_json, source_title,
         source_url, source_locator, source_excerpt, content_hash, source_hash,
         construction_rule, conflict_group, language, jurisdiction, source_published_at,
         source_retrieved_at, payload_json, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    )
    .bind(
      record.id,
      record.recordType,
      record.label,
      record.content,
      JSON.stringify(record.domains),
      JSON.stringify(record.topics),
      record.sourceTitle,
      record.sourceUrl,
      record.sourceLocator,
      record.sourceExcerpt,
      record.contentHash,
      record.sourceHash,
      record.constructionRule,
      record.conflictGroup ?? null,
      record.language ?? "en",
      record.jurisdiction ?? null,
      record.sourcePublishedAt ?? null,
      record.sourceRetrievedAt,
      JSON.stringify(record),
      record.createdAt,
    )
    .run();
  return true;
}

export async function getKnowledgeRecord(id: string) {
  const db = getOptionalDb();
  if (db) {
    await ensureSchema(db);
    const result = await db
      .prepare(`SELECT payload_json FROM knowledge_records_v2 WHERE id = ? LIMIT 1`)
      .bind(id)
      .all<{ payload_json: string }>();
    const value = result.results[0];
    if (value) return JSON.parse(value.payload_json) as KnowledgeRecord;
  }
  const seeds = await getPlasmapheresisSeedRecords();
  return seeds.find((record) => record.id === id) ?? null;
}

async function missingKnowledgeRecordIds(ids: string[]) {
  const uniqueIds = [...new Set(ids.filter(Boolean))];
  const records = await Promise.all(uniqueIds.map((id) => getKnowledgeRecord(id)));
  return uniqueIds.filter((_, index) => !records[index]);
}

async function requireKnowledgeRecordTypes(
  ids: string[],
  allowedTypes: readonly KnowledgeRecord["recordType"][],
  role: string,
) {
  const uniqueIds = [...new Set(ids.filter(Boolean))];
  const records = await Promise.all(uniqueIds.map((id) => getKnowledgeRecord(id)));
  const invalid = records.flatMap((record, index) =>
    record && !allowedTypes.includes(record.recordType)
      ? [`${uniqueIds[index]} (${record.recordType})`]
      : [],
  );
  if (invalid.length) {
    throw new Error(
      `${role} must use ${allowedTypes.join(" or ")} records; received ${invalid.join(", ")}`,
    );
  }
}

export async function saveLanguageAct(act: LanguageAct) {
  const db = getOptionalDb();
  if (!db) return false;
  await ensureSchema(db);
  const missing = await missingKnowledgeRecordIds(referencedRecordIds(act));
  if (missing.length) {
    throw new Error(`Language act references missing knowledge records: ${missing.join(", ")}`);
  }
  await Promise.all([
    requireKnowledgeRecordTypes(
      [act.expressionRecordId],
      ["LanguageExpression"],
      "Language expression",
    ),
    requireKnowledgeRecordTypes(
      act.contentRecordIds,
      ["Proposition", "Claim", "Definition", "Rule", "Theory"],
      "Language content",
    ),
    requireKnowledgeRecordTypes(
      act.interpretationRecordIds ?? [],
      ["Interpretation", "Definition", "Claim", "Theory"],
      "Language interpretation",
    ),
    requireKnowledgeRecordTypes(
      [act.speakerRecordId, ...(act.addresseeRecordIds ?? [])],
      ["Actor", "Entity", "AgentRun"],
      "Language actor",
    ),
    requireKnowledgeRecordTypes(
      act.contextRecordIds ?? [],
      ["Context", "Event", "Process", "Protocol"],
      "Language context",
    ),
    requireKnowledgeRecordTypes(
      [act.sourceRecordId],
      ["Source", "Document", "Conversation", "Message"],
      "Language source",
    ),
    requireKnowledgeRecordTypes(
      act.authorityRecordIds ?? [],
      ["Authority", "Rule", "Protocol"],
      "Language authority",
    ),
  ]);
  await db
    .prepare(
      `INSERT OR IGNORE INTO language_acts_v1
       (id, act_type, force, status, authority_status, medium, language, jurisdiction,
        district_id, source_record_id, speaker_record_id, payload_json, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    )
    .bind(
      act.id,
      act.actType,
      act.force,
      act.status,
      act.authorityStatus,
      act.medium,
      act.language,
      act.jurisdiction ?? null,
      act.districtId ?? null,
      act.sourceRecordId,
      act.speakerRecordId,
      JSON.stringify(act),
      act.createdAt,
    )
    .run();
  return true;
}

export async function getLanguageAct(id: string) {
  const db = getOptionalDb();
  if (!db) return null;
  await ensureSchema(db);
  const result = await db
    .prepare(`SELECT payload_json FROM language_acts_v1 WHERE id = ? LIMIT 1`)
    .bind(id)
    .all<{ payload_json: string }>();
  const value = result.results[0];
  return value ? (JSON.parse(value.payload_json) as LanguageAct) : null;
}

export async function saveOperativeEffect(effect: OperativeEffect) {
  const db = getOptionalDb();
  if (!db) return false;
  await ensureSchema(db);
  if (!(await getLanguageAct(effect.languageActId))) {
    throw new Error(`Operative effect references missing language act: ${effect.languageActId}`);
  }
  const missing = await missingKnowledgeRecordIds(effectReferencedRecordIds(effect));
  if (missing.length) {
    throw new Error(`Operative effect references missing knowledge records: ${missing.join(", ")}`);
  }
  await requireKnowledgeRecordTypes(
    effect.authorityRecordIds ?? [],
    ["Authority", "Rule", "Protocol"],
    "Operative-effect authority",
  );
  if (effect.realizedByOperationId) {
    const operation = await db
      .prepare(`SELECT operation_id FROM dap_operations WHERE operation_id = ? LIMIT 1`)
      .bind(effect.realizedByOperationId)
      .all<{ operation_id: string }>();
    if (!operation.results.length) {
      throw new Error(
        `Operative effect references a signed operation that is not in accepted history: ${effect.realizedByOperationId}`,
      );
    }
  }
  await db
    .prepare(
      `INSERT OR IGNORE INTO operative_effects_v1
       (id, language_act_id, effect_kind, operator, status, jurisdiction,
        realized_by_operation_id, payload_json, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    )
    .bind(
      effect.id,
      effect.languageActId,
      effect.effectKind,
      effect.operator,
      effect.status,
      effect.jurisdiction ?? null,
      effect.realizedByOperationId ?? null,
      JSON.stringify(effect),
      effect.createdAt,
    )
    .run();
  return true;
}

export async function getOperativeEffect(id: string) {
  const db = getOptionalDb();
  if (!db) return null;
  await ensureSchema(db);
  const result = await db
    .prepare(`SELECT payload_json FROM operative_effects_v1 WHERE id = ? LIMIT 1`)
    .bind(id)
    .all<{ payload_json: string }>();
  const value = result.results[0];
  return value ? (JSON.parse(value.payload_json) as OperativeEffect) : null;
}

function inClause(column: string, values: readonly string[], clauses: string[], bindings: string[]) {
  if (!values.length) return;
  clauses.push(`${column} IN (${values.map(() => "?").join(",")})`);
  bindings.push(...values);
}

function languageSearchTerms(value: string | undefined) {
  return [
    ...new Set(
      (value ?? "")
        .toLocaleLowerCase()
        .split(/[^\p{L}\p{N}_-]+/u)
        .map((term) => term.trim())
        .filter((term) => term.length > 1)
        .slice(0, 8),
    ),
  ];
}

function addPayloadSearch(
  terms: string[],
  clauses: string[],
  bindings: string[],
) {
  if (!terms.length) return;
  clauses.push(
    `(${terms.map(() => "lower(payload_json) LIKE ? ESCAPE '\\'").join(" OR ")})`,
  );
  bindings.push(
    ...terms.map(
      (term) => `%${term.replace(/[\\%_]/g, (value) => `\\${value}`)}%`,
    ),
  );
}

async function selectPayloads<T>(
  db: D1Database,
  table: string,
  clauses: string[],
  bindings: Array<string | number>,
  limit: number,
) {
  const where = clauses.length ? `WHERE ${clauses.join(" AND ")}` : "";
  const result = await db
    .prepare(`SELECT payload_json FROM ${table} ${where} ORDER BY created_at DESC LIMIT ?`)
    .bind(...bindings, limit)
    .all<{ payload_json: string }>();
  return result.results.map((row) => JSON.parse(row.payload_json) as T);
}

export async function queryLanguageForce(options: LanguageForceQuery = {}) {
  const db = getOptionalDb();
  const safeLimit = Math.min(Math.max(Math.trunc(options.limit ?? 50), 1), 100);
  if (!db) {
    return {
      protocolVersion: "caeluviim-language-force/1.0",
      query: options,
      actCount: 0,
      effectCount: 0,
      recordCount: 0,
      acts: [] as LanguageAct[],
      effects: [] as OperativeEffect[],
      records: [] as KnowledgeRecord[],
      graph: await buildLanguageGraph([], [], []),
    };
  }
  await ensureSchema(db);
  const terms = languageSearchTerms(options.query?.slice(0, 1_000));
  const recordId = options.recordId?.trim().slice(0, 500);

  const actClauses: string[] = [];
  const actBindings: string[] = [];
  addPayloadSearch(terms, actClauses, actBindings);
  if (recordId) {
    actClauses.push("payload_json LIKE ?");
    actBindings.push(`%${recordId}%`);
  }
  inClause("act_type", options.actTypes ?? [], actClauses, actBindings);
  if (options.forces?.length) {
    actClauses.push(`lower(force) IN (${options.forces.map(() => "?").join(",")})`);
    actBindings.push(...options.forces.map((force) => force.toLocaleLowerCase()));
  }
  if (options.districtId) {
    actClauses.push("district_id = ?");
    actBindings.push(options.districtId);
  }
  if (options.jurisdiction) {
    actClauses.push("lower(jurisdiction) = ?");
    actBindings.push(options.jurisdiction.toLocaleLowerCase());
  }

  const effectClauses: string[] = [];
  const effectBindings: string[] = [];
  addPayloadSearch(terms, effectClauses, effectBindings);
  if (recordId) {
    effectClauses.push("payload_json LIKE ?");
    effectBindings.push(`%${recordId}%`);
  }
  inClause("effect_kind", options.effectKinds ?? [], effectClauses, effectBindings);
  inClause("status", options.effectStatuses ?? [], effectClauses, effectBindings);
  if (options.jurisdiction) {
    effectClauses.push("lower(jurisdiction) = ?");
    effectBindings.push(options.jurisdiction.toLocaleLowerCase());
  }

  const acts = new Map<string, LanguageAct>();
  const effects = new Map<string, OperativeEffect>();
  const hasActFilter = Boolean(
    terms.length ||
      recordId ||
      options.actTypes?.length ||
      options.forces?.length ||
      options.districtId ||
      options.jurisdiction,
  );
  const hasEffectFilter = Boolean(
    terms.length ||
      recordId ||
      options.effectKinds?.length ||
      options.effectStatuses?.length ||
      options.jurisdiction,
  );

  if (hasActFilter || !hasEffectFilter) {
    (await selectPayloads<LanguageAct>(
      db,
      "language_acts_v1",
      actClauses,
      actBindings,
      safeLimit,
    )).forEach((act) => acts.set(act.id, act));
  }
  if (hasEffectFilter || !hasActFilter) {
    (await selectPayloads<OperativeEffect>(
      db,
      "operative_effects_v1",
      effectClauses,
      effectBindings,
      safeLimit,
    )).forEach((effect) => effects.set(effect.id, effect));
  }

  const matchedActIds = [...acts.keys()];
  if (matchedActIds.length) {
    const linkedClauses = [
      `language_act_id IN (${matchedActIds.map(() => "?").join(",")})`,
    ];
    const linkedBindings = [...matchedActIds];
    inClause("effect_kind", options.effectKinds ?? [], linkedClauses, linkedBindings);
    inClause("status", options.effectStatuses ?? [], linkedClauses, linkedBindings);
    if (options.jurisdiction) {
      linkedClauses.push("lower(jurisdiction) = ?");
      linkedBindings.push(options.jurisdiction.toLocaleLowerCase());
    }
    (await selectPayloads<OperativeEffect>(
      db,
      "operative_effects_v1",
      linkedClauses,
      linkedBindings,
      safeLimit,
    )).forEach((effect) => effects.set(effect.id, effect));
  }

  const missingActIds = [...new Set([...effects.values()].map((effect) => effect.languageActId))]
    .filter((id) => !acts.has(id))
    .slice(0, safeLimit);
  if (missingActIds.length) {
    const linkedActs = await selectPayloads<LanguageAct>(
      db,
      "language_acts_v1",
      [`id IN (${missingActIds.map(() => "?").join(",")})`],
      missingActIds,
      safeLimit,
    );
    linkedActs.forEach((act) => acts.set(act.id, act));
  }

  const orderedActs = [...acts.values()]
    .sort((left, right) => right.createdAt.localeCompare(left.createdAt))
    .slice(0, safeLimit);
  const orderedEffects = [...effects.values()]
    .sort((left, right) => right.createdAt.localeCompare(left.createdAt))
    .slice(0, safeLimit);
  const referencedIds = [
    ...orderedActs.flatMap(referencedRecordIds),
    ...orderedEffects.flatMap(effectReferencedRecordIds),
  ];
  const records = (
    await Promise.all([...new Set(referencedIds)].map((id) => getKnowledgeRecord(id)))
  ).filter((record): record is KnowledgeRecord => Boolean(record));
  const recordNodes: LanguageGraphNode[] = records.map((record) => ({
    id: record.id,
    type: record.recordType,
    label: record.label,
    properties: {
      content: record.content,
      domains: record.domains,
      topics: record.topics,
      language: record.language,
      jurisdiction: record.jurisdiction ?? null,
      sourceTitle: record.sourceTitle,
      sourceUrl: record.sourceUrl,
      sourceLocator: record.sourceLocator,
      sourceHash: record.sourceHash,
      contentHash: record.contentHash,
      constructionRule: record.constructionRule,
      conflictGroup: record.conflictGroup ?? null,
    },
  }));
  const graph = await buildLanguageGraph(orderedActs, orderedEffects, recordNodes);
  return {
    protocolVersion: graph.protocolVersion,
    query: options,
    actCount: orderedActs.length,
    effectCount: orderedEffects.length,
    recordCount: records.length,
    acts: orderedActs,
    effects: orderedEffects,
    records,
    graph,
  };
}

export type KnowledgeSearchOptions = {
  query: string;
  limit?: number;
  domains?: KnowledgeDomain[];
  recordTypes?: string[];
  topics?: string[];
};

function parseSearchOptions(options: KnowledgeSearchOptions | string, legacyLimit = 12) {
  return typeof options === "string" ? { query: options, limit: legacyLimit } : options;
}

function searchTerms(normalized: KnowledgeSearchOptions) {
  const terms = normalized.query
    .toLocaleLowerCase()
    .split(/[^\p{L}\p{N}_-]+/u)
    .filter((term) => term.length > 1)
    .slice(0, 8);
  const topicTerms = (normalized.topics ?? [])
    .flatMap((topic) => topic.toLocaleLowerCase().split(/[^\p{L}\p{N}_-]+/u))
    .filter((term) => term.length > 1)
    .slice(0, 8);
  return [...new Set([...terms, ...topicTerms])];
}

function filterSeedRecords(records: KnowledgeRecord[], normalized: KnowledgeSearchOptions) {
  const terms = searchTerms(normalized);
  const safeLimit = Math.min(Math.max(Math.trunc(normalized.limit ?? 12), 1), 100);
  return records
    .filter((record) => {
      if (normalized.domains?.length && !record.domains.some((domain) => normalized.domains?.includes(domain))) {
        return false;
      }
      if (normalized.recordTypes?.length && !normalized.recordTypes.includes(record.recordType)) {
        return false;
      }
      if (!terms.length) return Boolean(normalized.domains?.length || normalized.recordTypes?.length);
      const searchable = [
        record.label,
        record.content,
        record.sourceTitle,
        record.sourceLocator,
        ...record.topics,
      ]
        .join(" ")
        .toLocaleLowerCase();
      return terms.some((term) => searchable.includes(term));
    })
    .slice(0, safeLimit);
}

export async function searchKnowledgeRecords(options: KnowledgeSearchOptions | string, legacyLimit = 12) {
  const normalized = parseSearchOptions(options, legacyLimit);
  const seedMatches = filterSeedRecords(await getPlasmapheresisSeedRecords(), normalized);
  const db = getOptionalDb();
  if (!db) return seedMatches;
  await ensureSchema(db);
  const allTerms = searchTerms(normalized);
  const clauses: string[] = [];
  const bindings: Array<string | number> = [];
  if (allTerms.length) {
    clauses.push(
      `(${allTerms
        .map(() => `(lower(label) LIKE ? OR lower(content) LIKE ? OR lower(source_title) LIKE ? OR lower(topics_json) LIKE ?)`)
        .join(" OR ")})`,
    );
    allTerms.forEach((term) => {
      bindings.push(`%${term}%`, `%${term}%`, `%${term}%`, `%${term}%`);
    });
  }
  if (normalized.domains?.length) {
    clauses.push(`(${normalized.domains.map(() => "lower(domains_json) LIKE ?").join(" OR ")})`);
    normalized.domains.forEach((domain) => bindings.push(`%\"${domain.toLocaleLowerCase()}\"%`));
  }
  if (normalized.recordTypes?.length) {
    clauses.push(`record_type IN (${normalized.recordTypes.map(() => "?").join(",")})`);
    normalized.recordTypes.forEach((recordType) => bindings.push(recordType));
  }
  if (!clauses.length) return seedMatches;
  const safeLimit = Math.min(Math.max(Math.trunc(normalized.limit ?? 12), 1), 100);
  const result = await db
    .prepare(
      `SELECT payload_json FROM knowledge_records_v2
       WHERE ${clauses.join(" AND ")}
       ORDER BY created_at DESC LIMIT ?`,
    )
    .bind(...bindings, safeLimit)
    .all<{ payload_json: string }>();
  const databaseMatches = result.results.map((value) => JSON.parse(value.payload_json) as KnowledgeRecord);
  const merged = new Map<string, KnowledgeRecord>();
  [...databaseMatches, ...seedMatches].forEach((record) => merged.set(record.id, record));
  return [...merged.values()].slice(0, safeLimit);
}

export async function saveKnowledgeEdge(edge: KnowledgeEdge) {
  const db = getOptionalDb();
  if (!db) return false;
  await ensureSchema(db);
  const requiredIds = [...new Set([edge.subjectId, edge.objectId, ...edge.evidenceRecordIds])];
  const placeholders = requiredIds.map(() => "?").join(",");
  const known = await db
    .prepare(`SELECT id FROM knowledge_records_v2 WHERE id IN (${placeholders})`)
    .bind(...requiredIds)
    .all<{ id: string }>();
  const knownIds = new Set(known.results.map((item) => item.id));
  const missing = requiredIds.filter((id) => !knownIds.has(id));
  if (missing.length) {
    throw new Error(`Knowledge edge references missing records: ${missing.join(", ")}`);
  }
  await db
    .prepare(
      `INSERT OR IGNORE INTO knowledge_edges_v2
       (edge_id, subject_id, predicate, object_id, evidence_record_ids_json, payload_json, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
    )
    .bind(
      edge.id,
      edge.subjectId,
      edge.predicate,
      edge.objectId,
      JSON.stringify(edge.evidenceRecordIds),
      JSON.stringify(edge),
      edge.createdAt,
    )
    .run();
  return true;
}

export async function getKnowledgeNeighborhood(seedIds: string[], depth = 1, limit = 100) {
  const db = getOptionalDb();
  if (!db || !seedIds.length) return { records: [] as KnowledgeRecord[], edges: [] as KnowledgeEdge[] };
  await ensureSchema(db);
  const safeDepth = Math.min(Math.max(Math.trunc(depth), 1), 3);
  const safeLimit = Math.min(Math.max(Math.trunc(limit), 1), 300);
  const visited = new Set(seedIds.slice(0, 50));
  let frontier = [...visited];
  const edges = new Map<string, KnowledgeEdge>();
  for (let hop = 0; hop < safeDepth && frontier.length && edges.size < safeLimit; hop += 1) {
    const placeholders = frontier.map(() => "?").join(",");
    const result = await db
      .prepare(
        `SELECT payload_json FROM knowledge_edges_v2
         WHERE subject_id IN (${placeholders}) OR object_id IN (${placeholders})
         ORDER BY created_at DESC LIMIT ?`,
      )
      .bind(...frontier, ...frontier, safeLimit - edges.size)
      .all<{ payload_json: string }>();
    const next = new Set<string>();
    result.results.forEach((row) => {
      const edge = JSON.parse(row.payload_json) as KnowledgeEdge;
      edges.set(edge.id, edge);
      [edge.subjectId, edge.objectId, ...edge.evidenceRecordIds].forEach((id) => {
        if (!visited.has(id)) next.add(id);
        visited.add(id);
      });
    });
    frontier = [...next];
  }
  const recordIds = [...visited].slice(0, safeLimit);
  const placeholders = recordIds.map(() => "?").join(",");
  const recordResult = await db
    .prepare(`SELECT payload_json FROM knowledge_records_v2 WHERE id IN (${placeholders})`)
    .bind(...recordIds)
    .all<{ payload_json: string }>();
  return {
    records: recordResult.results.map((row) => JSON.parse(row.payload_json) as KnowledgeRecord),
    edges: [...edges.values()],
  };
}

export async function buildTopicCoverage(
  topic: string,
  requiredDomains: KnowledgeDomain[],
  requiredFacets: string[] = [],
) {
  const records = await searchKnowledgeRecords({ query: topic, topics: [topic], limit: 100 });
  const counts = Object.fromEntries(requiredDomains.map((domain) => [domain, 0])) as Record<string, number>;
  records.forEach((record) => {
    record.domains.forEach((domain) => {
      if (domain in counts) counts[domain] += 1;
    });
  });
  const facetCounts = Object.fromEntries(requiredFacets.map((facet) => [facet, 0])) as Record<string, number>;
  records.forEach((record) => {
    const searchable = [record.label, record.content, ...record.topics].join(" ").toLocaleLowerCase();
    requiredFacets.forEach((facet) => {
      if (searchable.includes(facet.toLocaleLowerCase())) facetCounts[facet] += 1;
    });
  });
  const missingFacets = requiredFacets.filter((facet) => facetCounts[facet] === 0);
  return {
    topic,
    requiredDomains,
    coveredDomains: requiredDomains.filter((domain) => counts[domain] > 0),
    missingDomains: requiredDomains.filter((domain) => counts[domain] === 0),
    counts,
    requiredFacets,
    coveredFacets: requiredFacets.filter((facet) => facetCounts[facet] > 0),
    missingFacets,
    facetCounts,
    recordCount: records.length,
    complete:
      requiredDomains.every((domain) => counts[domain] > 0) && missingFacets.length === 0,
    records,
  };
}
