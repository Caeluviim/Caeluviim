import { index, integer, primaryKey, sqliteTable, text, uniqueIndex } from "drizzle-orm/sqlite-core";

export const knowledgeRecords = sqliteTable(
  "knowledge_records_v2",
  {
    id: text("id").primaryKey(),
    recordType: text("record_type").notNull(),
    label: text("label").notNull(),
    content: text("content").notNull(),
    domainsJson: text("domains_json").notNull(),
    topicsJson: text("topics_json").notNull(),
    sourceTitle: text("source_title").notNull(),
    sourceUrl: text("source_url").notNull(),
    sourceLocator: text("source_locator").notNull(),
    sourceExcerpt: text("source_excerpt").notNull(),
    contentHash: text("content_hash").notNull(),
    sourceHash: text("source_hash").notNull(),
    constructionRule: text("construction_rule").notNull(),
    conflictGroup: text("conflict_group"),
    language: text("language").notNull(),
    jurisdiction: text("jurisdiction"),
    sourcePublishedAt: text("source_published_at"),
    sourceRetrievedAt: text("source_retrieved_at").notNull(),
    payloadJson: text("payload_json").notNull(),
    createdAt: text("created_at").notNull(),
  },
  (table) => [
    index("knowledge_records_v2_type_idx").on(table.recordType, table.createdAt),
    index("knowledge_records_v2_conflict_idx").on(table.conflictGroup, table.createdAt),
  ],
);

export const knowledgeEdges = sqliteTable(
  "knowledge_edges_v2",
  {
    edgeId: text("edge_id").primaryKey(),
    subjectId: text("subject_id").notNull(),
    predicate: text("predicate").notNull(),
    objectId: text("object_id").notNull(),
    evidenceRecordIdsJson: text("evidence_record_ids_json").notNull(),
    payloadJson: text("payload_json").notNull(),
    createdAt: text("created_at").notNull(),
  },
  (table) => [
    index("knowledge_edges_v2_subject_idx").on(table.subjectId, table.createdAt),
    index("knowledge_edges_v2_object_idx").on(table.objectId, table.createdAt),
  ],
);

export const languageActs = sqliteTable(
  "language_acts_v1",
  {
    id: text("id").primaryKey(),
    actType: text("act_type").notNull(),
    force: text("force").notNull(),
    status: text("status").notNull(),
    authorityStatus: text("authority_status").notNull(),
    medium: text("medium").notNull(),
    language: text("language").notNull(),
    jurisdiction: text("jurisdiction"),
    districtId: text("district_id"),
    sourceRecordId: text("source_record_id").notNull(),
    speakerRecordId: text("speaker_record_id").notNull(),
    payloadJson: text("payload_json").notNull(),
    createdAt: text("created_at").notNull(),
  },
  (table) => [
    index("language_acts_v1_type_idx").on(table.actType, table.createdAt),
    index("language_acts_v1_force_idx").on(table.force, table.createdAt),
    index("language_acts_v1_status_idx").on(table.status, table.createdAt),
    index("language_acts_v1_source_idx").on(table.sourceRecordId, table.createdAt),
    index("language_acts_v1_speaker_idx").on(table.speakerRecordId, table.createdAt),
    index("language_acts_v1_district_idx").on(table.districtId, table.createdAt),
  ],
);

export const operativeEffects = sqliteTable(
  "operative_effects_v1",
  {
    id: text("id").primaryKey(),
    languageActId: text("language_act_id").notNull(),
    effectKind: text("effect_kind").notNull(),
    operator: text("operator").notNull(),
    status: text("status").notNull(),
    jurisdiction: text("jurisdiction"),
    realizedByOperationId: text("realized_by_operation_id"),
    payloadJson: text("payload_json").notNull(),
    createdAt: text("created_at").notNull(),
  },
  (table) => [
    index("operative_effects_v1_act_idx").on(table.languageActId, table.createdAt),
    index("operative_effects_v1_kind_idx").on(table.effectKind, table.createdAt),
    index("operative_effects_v1_operator_idx").on(table.operator, table.createdAt),
    index("operative_effects_v1_status_idx").on(table.status, table.createdAt),
    index("operative_effects_v1_operation_idx").on(table.realizedByOperationId, table.createdAt),
  ],
);

export const protocolEvents = sqliteTable(
  "protocol_events",
  {
    eventId: text("event_id").primaryKey(),
    responseId: text("response_id").notNull().unique(),
    eventType: text("event_type").notNull(),
    protocolVersion: text("protocol_version").notNull(),
    contentHash: text("content_hash").notNull(),
    consentScope: text("consent_scope").notNull(),
    partitionKey: text("partition_key").notNull(),
    ingestionStatus: text("ingestion_status").notNull(),
    payloadJson: text("payload_json").notNull(),
    createdAt: text("created_at").notNull(),
  },
  (table) => [
    index("protocol_events_partition_idx").on(table.partitionKey, table.createdAt),
    index("protocol_events_scope_idx").on(table.consentScope, table.createdAt),
  ],
);

export const protocolResponses = sqliteTable(
  "protocol_responses",
  {
    id: text("id").primaryKey(),
    prompt: text("prompt").notNull(),
    schemaVersion: text("schema_version").notNull(),
    columnOrderJson: text("column_order_json").notNull(),
    rowJson: text("row_json").notNull(),
    csvText: text("csv_text").notNull(),
    payloadJson: text("payload_json").notNull(),
    createdAt: text("created_at").notNull(),
  },
  (table) => [index("protocol_responses_created_at_idx").on(table.createdAt)],
);

export const graphNodes = sqliteTable(
  "graph_nodes",
  {
    responseId: text("response_id").notNull(),
    nodeId: text("node_id").notNull(),
    nodeType: text("node_type").notNull(),
    label: text("label").notNull(),
    value: text("value"),
    isEmpty: integer("is_empty").notNull().default(0),
  },
  (table) => [primaryKey({ columns: [table.responseId, table.nodeId] })],
);

export const graphEdges = sqliteTable(
  "graph_edges",
  {
    responseId: text("response_id").notNull(),
    edgeId: text("edge_id").notNull(),
    subjectId: text("subject_id").notNull(),
    predicate: text("predicate").notNull(),
    objectId: text("object_id").notNull(),
  },
  (table) => [primaryKey({ columns: [table.responseId, table.edgeId] })],
);

export const dapDistricts = sqliteTable(
  "dap_districts",
  {
    districtId: text("district_id").primaryKey(),
    name: text("name").notNull(),
    protocolVersion: text("protocol_version").notNull(),
    activeRulesetId: text("active_ruleset_id").notNull(),
    genesisOperationId: text("genesis_operation_id").notNull().unique(),
    status: text("status").notNull(),
    payloadJson: text("payload_json").notNull(),
    createdAt: text("created_at").notNull(),
  },
  (table) => [index("dap_districts_status_idx").on(table.status, table.createdAt)],
);

export const dapRulesets = sqliteTable(
  "dap_rulesets",
  {
    rulesetId: text("ruleset_id").primaryKey(),
    districtId: text("district_id").notNull(),
    rulesetVersion: integer("ruleset_version").notNull(),
    status: text("status").notNull(),
    proposedByOperationId: text("proposed_by_operation_id").notNull(),
    activatedByOperationId: text("activated_by_operation_id"),
    payloadJson: text("payload_json").notNull(),
    createdAt: text("created_at").notNull(),
  },
  (table) => [
    uniqueIndex("dap_rulesets_district_version_uidx").on(table.districtId, table.rulesetVersion),
    index("dap_rulesets_district_status_idx").on(table.districtId, table.status),
  ],
);

export const dapSubmissions = sqliteTable(
  "dap_submissions",
  {
    operationId: text("operation_id").primaryKey(),
    districtId: text("district_id").notNull(),
    contentHash: text("content_hash").notNull(),
    lastDisposition: text("last_disposition").notNull(),
    reasonCodesJson: text("reason_codes_json").notNull(),
    payloadJson: text("payload_json").notNull(),
    receivedAt: text("received_at").notNull(),
  },
  (table) => [index("dap_submissions_district_idx").on(table.districtId, table.receivedAt)],
);

export const dapOperations = sqliteTable(
  "dap_operations",
  {
    operationId: text("operation_id").primaryKey(),
    districtId: text("district_id").notNull(),
    operationType: text("operation_type").notNull(),
    authorIdentityId: text("author_identity_id").notNull(),
    signingKeyId: text("signing_key_id").notNull(),
    authorSequence: integer("author_sequence").notNull(),
    lamport: integer("lamport").notNull(),
    disposition: text("disposition").notNull(),
    payloadJson: text("payload_json").notNull(),
    acceptedAt: text("accepted_at").notNull(),
  },
  (table) => [
    uniqueIndex("dap_operations_author_sequence_uidx").on(table.districtId, table.signingKeyId, table.authorSequence),
    index("dap_operations_district_lamport_idx").on(table.districtId, table.lamport, table.operationId),
    index("dap_operations_target_type_idx").on(table.districtId, table.operationType),
  ],
);

export const dapDistrictState = sqliteTable("dap_district_state", {
  districtId: text("district_id").primaryKey(),
  historyRoot: text("history_root").notNull(),
  stateRoot: text("state_root").notNull(),
  acceptedCount: integer("accepted_count").notNull(),
  stateJson: text("state_json").notNull(),
  updatedAt: text("updated_at").notNull(),
});

export const dapDispositions = sqliteTable(
  "dap_dispositions",
  {
    dispositionId: text("disposition_id").primaryKey(),
    operationId: text("operation_id").notNull(),
    districtId: text("district_id").notNull(),
    disposition: text("disposition").notNull(),
    rulesetId: text("ruleset_id").notNull(),
    historyRootBefore: text("history_root_before"),
    stateRootBefore: text("state_root_before"),
    historyRootAfter: text("history_root_after"),
    stateRootAfter: text("state_root_after"),
    payloadJson: text("payload_json").notNull(),
    createdAt: text("created_at").notNull(),
  },
  (table) => [
    uniqueIndex("dap_dispositions_operation_context_uidx").on(table.operationId, table.historyRootBefore),
    index("dap_dispositions_district_idx").on(table.districtId, table.createdAt),
  ],
);

export const dapCheckpoints = sqliteTable(
  "dap_checkpoints",
  {
    checkpointId: text("checkpoint_id").primaryKey(),
    districtId: text("district_id").notNull(),
    operationId: text("operation_id").notNull().unique(),
    historyRoot: text("history_root").notNull(),
    stateRoot: text("state_root").notNull(),
    districtTime: text("district_time").notNull(),
    payloadJson: text("payload_json").notNull(),
    finalizedAt: text("finalized_at").notNull(),
  },
  (table) => [index("dap_checkpoints_district_idx").on(table.districtId, table.finalizedAt)],
);
