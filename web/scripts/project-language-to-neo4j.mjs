import { readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { resolve } from "node:path";

const CORE = "https://caeluviim.org/ontology/core#";
const DEFAULT_GRAPH_URL = "http://127.0.0.1:8080/api/language/graph?limit=100";
const DEFAULT_NEO4J_URL = "http://127.0.0.1:7474";
const DEFAULT_CREDENTIALS = resolve(
  homedir(),
  ".local/share/caeluviim/neo4j/credentials.json",
);

function option(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
}

function requiredString(value, label) {
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`${label} must be a non-empty string.`);
  }
  return value.trim();
}

function normalizeGraph(value) {
  if (!value || typeof value !== "object" || !value.graph) {
    throw new Error("The language graph endpoint did not return a graph.");
  }
  const nodes = Array.isArray(value.graph.nodes) ? value.graph.nodes : [];
  const edges = Array.isArray(value.graph.edges) ? value.graph.edges : [];
  const normalizedNodes = nodes.map((node) => ({
    id: requiredString(node.id, "node.id"),
    types: [`${CORE}${requiredString(node.type, "node.type")}`],
    label: requiredString(node.label, "node.label"),
    status: typeof node.status === "string" && node.status ? node.status : null,
    propertiesJson: JSON.stringify(node.properties ?? {}),
  }));
  const knownIds = new Set(normalizedNodes.map((node) => node.id));
  const normalizedEdges = edges.map((edge) => {
    const subject = requiredString(edge.subject, "edge.subject");
    const object = requiredString(edge.object, "edge.object");
    if (!knownIds.has(subject) || !knownIds.has(object)) {
      throw new Error(`Edge ${edge.id ?? "(missing id)"} references a node absent from the export.`);
    }
    const predicate = requiredString(edge.predicate, "edge.predicate");
    return {
      id: requiredString(edge.id, "edge.id"),
      subject,
      predicate: predicate.includes("://") ? predicate : `${CORE}${predicate}`,
      object,
      evidenceRecordIds: Array.isArray(edge.evidenceRecordIds)
        ? [...new Set(edge.evidenceRecordIds.filter((id) => typeof id === "string" && id))]
        : [],
    };
  });
  return {
    protocolVersion: requiredString(value.protocolVersion, "protocolVersion"),
    nodes: normalizedNodes,
    edges: normalizedEdges,
  };
}

async function neo4jQuery(endpoint, authorization, statement, parameters = {}) {
  const response = await fetch(`${endpoint}/db/neo4j/tx/commit`, {
    method: "POST",
    headers: {
      authorization,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      statements: [
        {
          statement,
          parameters,
          resultDataContents: ["row"],
        },
      ],
    }),
  });
  const payload = await response.json();
  if (!response.ok || payload.errors?.length) {
    const detail = payload.errors?.map((error) => `${error.code}: ${error.message}`).join(" | ");
    throw new Error(detail || `Neo4j returned HTTP ${response.status}.`);
  }
  return payload.results?.[0]?.data?.map((item) => item.row) ?? [];
}

const graphUrl = option("--graph-url", DEFAULT_GRAPH_URL);
const neo4jUrl = option("--neo4j-url", DEFAULT_NEO4J_URL);
const credentialsPath = option("--credentials", DEFAULT_CREDENTIALS);
const partition = option("--partition", "language-force/1.0");
const dryRun = process.argv.includes("--dry-run");

const [graphResponse, credentialsText] = await Promise.all([
  fetch(graphUrl),
  readFile(credentialsPath, "utf8"),
]);
if (!graphResponse.ok) {
  throw new Error(`Language graph returned HTTP ${graphResponse.status}.`);
}
const graph = normalizeGraph(await graphResponse.json());
const credentials = JSON.parse(credentialsText);
const user = requiredString(credentials.user, "Neo4j credential user");
const password = requiredString(credentials.password, "Neo4j credential password");
const authorization = `Basic ${Buffer.from(`${user}:${password}`).toString("base64")}`;
const projectedAt = new Date().toISOString();

if (!dryRun) {
  await neo4jQuery(
    neo4jUrl,
    authorization,
    `UNWIND $nodes AS row
     MERGE (node:CaeluviimResource {id: row.id})
     SET node.types = reduce(
       values = [],
       value IN coalesce(node.types, []) + row.types |
       CASE WHEN value IN values THEN values ELSE values + value END
     ),
     node.label = row.label,
     node.status = row.status,
     node.propertiesJson = row.propertiesJson,
     node.partition = $partition,
     node.projectionSource = $projectionSource,
     node.projectedAt = $projectedAt
     RETURN count(node) AS projectedNodes`,
    {
      nodes: graph.nodes,
      partition,
      projectionSource: graphUrl,
      projectedAt,
    },
  );
  await neo4jQuery(
    neo4jUrl,
    authorization,
    `UNWIND $edges AS row
     MATCH (subject:CaeluviimResource {id: row.subject})
     MATCH (object:CaeluviimResource {id: row.object})
     MERGE (subject)-[relation:CAELUVIIM_RELATION {edgeId: row.id}]->(object)
     SET relation.predicate = row.predicate,
     relation.partition = $partition,
     relation.evidenceRecordIds = row.evidenceRecordIds,
     relation.projectionSource = $projectionSource,
     relation.projectedAt = $projectedAt
     RETURN count(relation) AS projectedEdges`,
    {
      edges: graph.edges,
      partition,
      projectionSource: graphUrl,
      projectedAt,
    },
  );
}

const nodeRows = dryRun
  ? [[0]]
  : await neo4jQuery(
      neo4jUrl,
      authorization,
      `MATCH (node:CaeluviimResource)
       WHERE node.id IN $ids AND node.partition = $partition
       RETURN count(node) AS nodes`,
      { ids: graph.nodes.map((node) => node.id), partition },
    );
const edgeRows = dryRun
  ? [[0]]
  : await neo4jQuery(
      neo4jUrl,
      authorization,
      `MATCH ()-[relation:CAELUVIIM_RELATION]->()
       WHERE relation.edgeId IN $ids AND relation.partition = $partition
       RETURN count(relation) AS edges`,
      { ids: graph.edges.map((edge) => edge.id), partition },
    );
const verifiedNodes = Number(nodeRows[0]?.[0] ?? 0);
const verifiedEdges = Number(edgeRows[0]?.[0] ?? 0);
const status = dryRun
  ? "DRY_RUN"
  : verifiedNodes === graph.nodes.length && verifiedEdges === graph.edges.length
    ? "PASS"
    : "FAIL";

process.stdout.write(
  `${JSON.stringify(
    {
      status,
      protocolVersion: graph.protocolVersion,
      source: {
        nodes: graph.nodes.length,
        edges: graph.edges.length,
      },
      neo4j: {
        verifiedNodes,
        verifiedEdges,
        partition,
      },
    },
    null,
    2,
  )}\n`,
);

if (status === "FAIL") process.exitCode = 1;
