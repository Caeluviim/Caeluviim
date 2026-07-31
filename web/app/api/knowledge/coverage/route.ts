import { KNOWLEDGE_DOMAINS, type KnowledgeDomain } from "../../../../lib/knowledge";
import { buildTopicCoverage } from "../../../../lib/store";

const cors = { "access-control-allow-origin": "*" };

export async function GET(request: Request) {
  const url = new URL(request.url);
  const topic = (url.searchParams.get("topic") ?? "").trim();
  if (!topic) {
    return Response.json({ error: "Query parameter topic is required." }, { status: 400, headers: cors });
  }
  const requestedDomains = (url.searchParams.get("domains") ?? "")
    .split(",")
    .map((value) => value.trim())
    .filter((value): value is KnowledgeDomain =>
      KNOWLEDGE_DOMAINS.includes(value as KnowledgeDomain),
    );
  const domains = requestedDomains.length
    ? requestedDomains
    : ([...KNOWLEDGE_DOMAINS] as KnowledgeDomain[]);
  const facets = (url.searchParams.get("facets") ?? "")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
  return Response.json(await buildTopicCoverage(topic, domains, facets), { headers: cors });
}
