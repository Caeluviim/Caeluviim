import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import * as z from "zod/v4";
import {
  CATEGORY_DEFINITIONS,
  CATEGORY_KEYS,
  PROTOCOL_DESCRIPTOR,
  PROTOCOL_VERSION,
  type CategoryKey,
} from "./protocol";
import {
  KNOWLEDGE_DOMAINS,
  KNOWLEDGE_RECORD_TYPES,
  createKnowledgeEdge,
  createKnowledgeRecord,
  type KnowledgeDomain,
} from "./knowledge";
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
  createLanguageAct,
  createOperativeEffect,
} from "./language";
import {
  buildTopicCoverage,
  getKnowledgeNeighborhood,
  getKnowledgeRecord,
  saveKnowledgeEdge,
  saveKnowledgeRecord,
  saveLanguageAct,
  saveOperativeEffect,
  searchKnowledgeRecords,
  queryLanguageForce,
} from "./store";
import { getDapOperationStatus, reconstructDapDistrict, submitDapOperation } from "./dap/kernel";
import { listDapDistricts, listDapHistory } from "./dap/store";

const readonlyAnnotations = {
  readOnlyHint: true,
  destructiveHint: false,
  openWorldHint: false,
} as const;

const writeAnnotations = {
  readOnlyHint: false,
  destructiveHint: false,
  openWorldHint: false,
} as const;

function jsonResult(value: Record<string, unknown>) {
  return {
    content: [{ type: "text" as const, text: JSON.stringify(value, null, 2) }],
    structuredContent: value,
  };
}

function errorResult(message: string, details?: unknown) {
  return {
    isError: true,
    content: [
      {
        type: "text" as const,
        text: JSON.stringify({ error: message, details }, null, 2),
      },
    ],
  };
}

function csvCell(value: string) {
  return `"${value.replace(/"/g, '""')}"`;
}

export function createCaeluviimMcpServer() {
  const server = new McpServer({
    name: "caeluviim-source-bound-knowledge-graph",
    version: PROTOCOL_VERSION,
  });

  server.registerTool(
    "get_protocol_schema",
    {
      title: "Get Caeluviim protocol schema",
      description:
        "Returns the mandatory graph/table response categories, provenance contract, knowledge domains, and MCP operations.",
      annotations: readonlyAnnotations,
    },
    async () =>
      jsonResult({
        protocol: PROTOCOL_DESCRIPTOR,
        knowledgeDomains: KNOWLEDGE_DOMAINS,
        knowledgeRecordTypes: KNOWLEDGE_RECORD_TYPES,
        languageForce: {
          version: LANGUAGE_FORCE_PROTOCOL_VERSION,
          media: LANGUAGE_MEDIA,
          actTypes: LANGUAGE_ACT_TYPES,
          actStatuses: LANGUAGE_ACT_STATUSES,
          authorityStatuses: AUTHORITY_STATUSES,
          deonticOperators: DEONTIC_OPERATORS,
          effectKinds: EFFECT_KINDS,
          effectOperators: EFFECT_OPERATORS,
          effectStatuses: EFFECT_STATUSES,
        },
        groundingRule:
          "Every answer statement, language act, and operative-effect claim must cite existing provenance-complete knowledge record IDs. Never silently fill a coverage gap or promote claimed force to effective force.",
      }),
  );

  server.registerTool(
    "ingest_knowledge_record",
    {
      title: "Ingest a provenance-complete knowledge record",
      description:
        "Adds a content-addressed source, topic, entity, process, substance, claim, authority, definition, observation, event, rule, theory, or protocol record. Exact source locator and excerpt are mandatory.",
      inputSchema: {
        recordType: z.enum(KNOWLEDGE_RECORD_TYPES),
        label: z.string().min(1).max(240),
        content: z.string().min(1).max(50_000),
        domains: z.array(z.enum(KNOWLEDGE_DOMAINS)).min(1).max(12),
        topics: z.array(z.string().min(1).max(180)).min(1).max(40),
        sourceTitle: z.string().min(1).max(500),
        sourceUrl: z.string().min(1).max(2_000),
        sourceLocator: z.string().min(1).max(500),
        sourceExcerpt: z.string().min(1).max(5_000),
        constructionRule: z.string().min(1).max(2_000),
        conflictGroup: z.string().max(240).optional(),
        language: z.string().max(80).optional(),
        jurisdiction: z.string().max(180).optional(),
        sourcePublishedAt: z.string().max(80).optional(),
      },
      annotations: writeAnnotations,
    },
    async (input) => {
      try {
        const record = await createKnowledgeRecord(input);
        const persisted = await saveKnowledgeRecord(record);
        return jsonResult({ record, persisted });
      } catch (error) {
        return errorResult(error instanceof Error ? error.message : "Knowledge ingestion failed.");
      }
    },
  );

  server.registerTool(
    "link_knowledge_records",
    {
      title: "Create an evidence-bound graph relationship",
      description:
        "Links two existing knowledge records with a typed predicate. The relationship is rejected unless every cited evidence record exists.",
      inputSchema: {
        subjectId: z.string().min(1).max(500),
        predicate: z.string().min(1).max(180),
        objectId: z.string().min(1).max(500),
        evidenceRecordIds: z.array(z.string().min(1).max(500)).min(1).max(40),
      },
      annotations: writeAnnotations,
    },
    async (input) => {
      try {
        const edge = await createKnowledgeEdge(input);
        const persisted = await saveKnowledgeEdge(edge);
        return jsonResult({ edge, persisted });
      } catch (error) {
        return errorResult(error instanceof Error ? error.message : "Knowledge linking failed.");
      }
    },
  );

  server.registerTool(
    "record_language_act",
    {
      title: "Record a source-bound language act",
      description:
        "Records an expression, its propositional content and interpretations, speaker/addressees, illocutionary force, modality, authority status, scope, and evidence without treating the words alone as proof of operative effect.",
      inputSchema: {
        label: z.string().min(1).max(240),
        expressionRecordId: z.string().min(1).max(500),
        contentRecordIds: z.array(z.string().min(1).max(500)).min(1).max(40),
        interpretationRecordIds: z.array(z.string().min(1).max(500)).max(40).optional(),
        speakerRecordId: z.string().min(1).max(500),
        addresseeRecordIds: z.array(z.string().min(1).max(500)).max(40).optional(),
        contextRecordIds: z.array(z.string().min(1).max(500)).max(40).optional(),
        sourceRecordId: z.string().min(1).max(500),
        evidenceRecordIds: z.array(z.string().min(1).max(500)).min(1).max(40),
        authorityRecordIds: z.array(z.string().min(1).max(500)).max(40).optional(),
        actType: z.enum(LANGUAGE_ACT_TYPES),
        force: z.string().min(1).max(180),
        medium: z.enum(LANGUAGE_MEDIA),
        language: z.string().min(1).max(80),
        script: z.string().max(80).optional(),
        polarity: z.enum(["affirmative", "negative"]),
        deonticOperator: z.enum(DEONTIC_OPERATORS),
        status: z.enum(LANGUAGE_ACT_STATUSES),
        authorityStatus: z.enum(AUTHORITY_STATUSES),
        conditions: z.array(z.string().min(1).max(1_000)).max(40).optional(),
        scopePath: z.array(z.string().min(1).max(240)).max(40).optional(),
        jurisdiction: z.string().max(180).optional(),
        occurredAt: z.string().max(80).optional(),
        districtId: z.string().max(500).optional(),
      },
      annotations: writeAnnotations,
    },
    async (input) => {
      try {
        const act = await createLanguageAct(input);
        const persisted = await saveLanguageAct(act);
        return jsonResult({ act, persisted });
      } catch (error) {
        return errorResult(error instanceof Error ? error.message : "Language act ingestion failed.");
      }
    },
  );

  server.registerTool(
    "record_operative_effect",
    {
      title: "Record a grounded operative effect",
      description:
        "Records a claimed or actual communicative, causal, institutional, normative, procedural, evidentiary, computational, interpretive, or symbolic effect. Effective institutional/normative/procedural force requires authority or an accepted signed operation.",
      inputSchema: {
        label: z.string().min(1).max(240),
        languageActId: z.string().min(1).max(500),
        effectKind: z.enum(EFFECT_KINDS),
        operator: z.enum(EFFECT_OPERATORS),
        status: z.enum(EFFECT_STATUSES),
        description: z.string().min(1).max(10_000),
        targetRecordIds: z.array(z.string().min(1).max(500)).min(1).max(40),
        bearerRecordIds: z.array(z.string().min(1).max(500)).max(40).optional(),
        beneficiaryRecordIds: z.array(z.string().min(1).max(500)).max(40).optional(),
        basisRecordIds: z.array(z.string().min(1).max(500)).min(1).max(40),
        authorityRecordIds: z.array(z.string().min(1).max(500)).max(40).optional(),
        evidenceRecordIds: z.array(z.string().min(1).max(500)).min(1).max(40),
        conditions: z.array(z.string().min(1).max(1_000)).max(40).optional(),
        scopePath: z.array(z.string().min(1).max(240)).max(40).optional(),
        jurisdiction: z.string().max(180).optional(),
        effectiveFrom: z.string().max(80).optional(),
        effectiveUntil: z.string().max(80).optional(),
        realizedByOperationId: z.string().max(500).optional(),
      },
      annotations: writeAnnotations,
    },
    async (input) => {
      try {
        const effect = await createOperativeEffect(input);
        const persisted = await saveOperativeEffect(effect);
        return jsonResult({ effect, persisted });
      } catch (error) {
        return errorResult(error instanceof Error ? error.message : "Operative effect ingestion failed.");
      }
    },
  );

  server.registerTool(
    "query_language_force",
    {
      title: "Query language, force, content, and effects",
      description:
        "Returns the joined graph of language acts, contents, interpretations, actors, authority, evidence, targets, and operative effects. Claimed, contested, void, and effective states remain distinct.",
      inputSchema: {
        query: z.string().min(1).max(1_000).optional(),
        actTypes: z.array(z.enum(LANGUAGE_ACT_TYPES)).max(LANGUAGE_ACT_TYPES.length).optional(),
        forces: z.array(z.string().min(1).max(180)).max(40).optional(),
        effectKinds: z.array(z.enum(EFFECT_KINDS)).max(EFFECT_KINDS.length).optional(),
        effectStatuses: z.array(z.enum(EFFECT_STATUSES)).max(EFFECT_STATUSES.length).optional(),
        recordId: z.string().max(500).optional(),
        districtId: z.string().max(500).optional(),
        jurisdiction: z.string().max(180).optional(),
        limit: z.number().int().min(1).max(100).optional(),
      },
      annotations: readonlyAnnotations,
    },
    async (input) => jsonResult(await queryLanguageForce(input)),
  );

  server.registerTool(
    "search_knowledge",
    {
      title: "Search source-bound knowledge",
      description:
        "Searches records by topic/text and optionally filters by domain or record type. Returns source locators, hashes, excerpts, and construction rules with every result.",
      inputSchema: {
        query: z.string().min(1).max(1_000),
        domains: z.array(z.enum(KNOWLEDGE_DOMAINS)).max(12).optional(),
        recordTypes: z.array(z.enum(KNOWLEDGE_RECORD_TYPES)).max(KNOWLEDGE_RECORD_TYPES.length).optional(),
        topics: z.array(z.string().min(1).max(180)).max(20).optional(),
        limit: z.number().int().min(1).max(100).optional(),
      },
      annotations: readonlyAnnotations,
    },
    async (input) => {
      const records = await searchKnowledgeRecords(input);
      return jsonResult({ query: input.query, count: records.length, records });
    },
  );

  server.registerTool(
    "fetch_knowledge_record",
    {
      title: "Fetch one source-bound record",
      description: "Fetches a knowledge record by its immutable Caeluviim identifier.",
      inputSchema: { id: z.string().min(1).max(500) },
      annotations: readonlyAnnotations,
    },
    async ({ id }) => {
      const record = await getKnowledgeRecord(id);
      return record ? jsonResult({ record }) : errorResult("Knowledge record not found.", { id });
    },
  );

  server.registerTool(
    "get_knowledge_neighborhood",
    {
      title: "Traverse a knowledge neighborhood",
      description:
        "Returns records and evidence-bound edges connected to one or more seed records, up to three hops.",
      inputSchema: {
        seedIds: z.array(z.string().min(1).max(500)).min(1).max(50),
        depth: z.number().int().min(1).max(3).optional(),
        limit: z.number().int().min(1).max(300).optional(),
      },
      annotations: readonlyAnnotations,
    },
    async ({ seedIds, depth, limit }) =>
      jsonResult(await getKnowledgeNeighborhood(seedIds, depth, limit)),
  );

  server.registerTool(
    "explore_topic_coverage",
    {
      title: "Map a topic across domains and facets",
      description:
        "Builds a coverage matrix for a topic. Required domains and facets remain explicit and missing areas are returned as gaps rather than invented content.",
      inputSchema: {
        topic: z.string().min(1).max(500),
        requiredDomains: z.array(z.enum(KNOWLEDGE_DOMAINS)).min(1).max(12),
        requiredFacets: z.array(z.string().min(1).max(180)).max(60).optional(),
      },
      annotations: readonlyAnnotations,
    },
    async ({ topic, requiredDomains, requiredFacets }) => {
      const coverage = await buildTopicCoverage(
        topic,
        requiredDomains as KnowledgeDomain[],
        requiredFacets ?? [],
      );
      return jsonResult({
        ...coverage,
        coverageTable: requiredDomains.map((domain) => ({
          domain,
          records: coverage.counts[domain],
          status: coverage.counts[domain] > 0 ? "covered" : "gap",
        })),
        facetTable: (requiredFacets ?? []).map((facet) => ({
          facet,
          records: coverage.facetCounts[facet],
          status: coverage.facetCounts[facet] > 0 ? "covered" : "gap",
        })),
      });
    },
  );

  server.registerTool(
    "map_grounded_response",
    {
      title: "Map a fully grounded graph/table response",
      description:
        "Validates every proposed answer statement against cited Caeluviim records and returns the complete dynamically ordered response table plus exact citations. Missing records reject the mapping.",
      inputSchema: {
        prompt: z.string().min(1).max(10_000),
        statements: z
          .array(
            z.object({
              text: z.string().min(1).max(10_000),
              categories: z.array(z.enum(CATEGORY_KEYS)).min(1).max(CATEGORY_KEYS.length),
              knowledgeRecordIds: z.array(z.string().min(1).max(500)).min(1).max(40),
            }),
          )
          .min(1)
          .max(100),
      },
      annotations: readonlyAnnotations,
    },
    async ({ prompt, statements }) => {
      const citedIds = [...new Set(statements.flatMap((statement) => statement.knowledgeRecordIds))];
      const records = await Promise.all(citedIds.map((id) => getKnowledgeRecord(id)));
      const missingRecordIds = citedIds.filter((_, index) => !records[index]);
      if (missingRecordIds.length) {
        return errorResult("Grounded response rejected because cited knowledge records are missing.", {
          missingRecordIds,
        });
      }
      const citations = records.flatMap((record) =>
        record
          ? [
              {
                id: record.id,
                label: record.label,
                sourceTitle: record.sourceTitle,
                sourceUrl: record.sourceUrl,
                sourceLocator: record.sourceLocator,
                sourceHash: record.sourceHash,
                contentHash: record.contentHash,
                constructionRule: record.constructionRule,
              },
            ]
          : [],
      );
      const row = Object.fromEntries(CATEGORY_KEYS.map((key) => [key, ""])) as Record<
        CategoryKey,
        string
      >;
      statements.forEach((statement, index) => {
        const suffix = statement.knowledgeRecordIds.map((id) => `[${id}]`).join(" ");
        const mapped = `${index + 1}. ${statement.text} ${suffix}`;
        statement.categories.forEach((category) => {
          row[category] = [row[category], mapped].filter(Boolean).join(" | ");
        });
      });
      row.response_control = statements
        .map(
          (statement, index) =>
            `${index + 1}. ${statement.text} ${statement.knowledgeRecordIds
              .map((id) => `[${id}]`)
              .join(" ")}`,
        )
        .join(" | ");
      row.provenance = citations
        .map(
          (citation) =>
            `${citation.id} — ${citation.sourceTitle} — ${citation.sourceUrl} — ${citation.sourceLocator} — ${citation.sourceHash}`,
        )
        .join(" | ");
      row.ai_protocol =
        "Response mapped through the provider-independent Caeluviim MCP endpoint; no model-generated assertion is accepted without stored graph provenance.";
      row.verification = `${statements.length}/${statements.length} statements mapped to ${citations.length} existing provenance-complete records.`;
      row.risk_limits =
        "This mapping proves citation presence and record identity; it does not by itself prove source truth, topic completeness, or legal/medical validity.";
      const columns = [...CATEGORY_DEFINITIONS].sort((left, right) => {
        const filled = Number(Boolean(row[right.key])) - Number(Boolean(row[left.key]));
        return filled || CATEGORY_KEYS.indexOf(left.key) - CATEGORY_KEYS.indexOf(right.key);
      });
      const csv = `${columns.map((column) => csvCell(column.label)).join(",")}\n${columns
        .map((column) => csvCell(row[column.key]))
        .join(",")}`;
      return jsonResult({
        prompt,
        protocolVersion: PROTOCOL_VERSION,
        columns,
        row,
        citations,
        statementMappings: statements,
        csv,
        provenanceComplete: true,
        renderingInstruction:
          "Render every returned category as one visible table column. Keep empty categories visible as □. Put populated columns first in the returned order.",
      });
    },
  );

  server.registerTool(
    "list_dap_districts",
    {
      title: "List operational DAP districts",
      description:
        "Lists signed DAP district histories with their active rulesets, accepted-operation counts, history roots, and state roots.",
      inputSchema: { limit: z.number().int().min(1).max(100).optional() },
      annotations: readonlyAnnotations,
    },
    async ({ limit }) => {
      const districts = await listDapDistricts(limit);
      return jsonResult({ count: districts.length, districts });
    },
  );

  server.registerTool(
    "reconstruct_dap_district",
    {
      title: "Reconstruct and verify a DAP district",
      description:
        "Replays the accepted operation history and returns independently recomputed history/state roots plus the complete derived district state.",
      inputSchema: { districtId: z.string().min(1).max(512) },
      annotations: readonlyAnnotations,
    },
    async ({ districtId }) => {
      const district = await reconstructDapDistrict(districtId);
      return district ? jsonResult(district) : errorResult("DAP district not found.", { districtId });
    },
  );

  server.registerTool(
    "get_dap_history",
    {
      title: "Read accepted DAP operation history",
      description:
        "Returns accepted effective, pending, contested, and superseded operations for one district in deterministic order.",
      inputSchema: {
        districtId: z.string().min(1).max(512),
        limit: z.number().int().min(1).max(500).optional(),
      },
      annotations: readonlyAnnotations,
    },
    async ({ districtId, limit }) => {
      const operations = await listDapHistory(districtId, limit);
      return jsonResult({ district_id: districtId, count: operations.length, operations });
    },
  );

  server.registerTool(
    "get_dap_operation_disposition",
    {
      title: "Read a DAP submission disposition",
      description:
        "Returns the submitted signed envelope, latest validation result, reasons, and whether it entered accepted history.",
      inputSchema: { operationId: z.string().min(1).max(512) },
      annotations: readonlyAnnotations,
    },
    async ({ operationId }) => {
      const operation = await getDapOperationStatus(operationId);
      return operation ? jsonResult(operation) : errorResult("DAP operation submission not found.", { operationId });
    },
  );

  server.registerTool(
    "submit_signed_dap_operation",
    {
      title: "Submit a signed DAP operation",
      description:
        "Submits an already signed DAP v0.2 operation envelope to the staged validator. The tool never fabricates or bypasses the author's signature.",
      inputSchema: { operation: z.record(z.string(), z.unknown()) },
      annotations: writeAnnotations,
    },
    async ({ operation }) => {
      const outcome = await submitDapOperation(operation);
      return outcome.result || outcome.ok
        ? jsonResult(outcome as unknown as Record<string, unknown>)
        : errorResult("DAP envelope failed protocol parsing.", outcome.errors);
    },
  );

  return server;
}
