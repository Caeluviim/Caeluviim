import { KNOWLEDGE_DOMAINS, type KnowledgeDomain } from "../../../../lib/knowledge";
import { searchKnowledgeRecords } from "../../../../lib/store";

const cors = { "access-control-allow-origin": "*" };

export async function GET(request: Request) {
  const url = new URL(request.url);
  const query = (url.searchParams.get("q") ?? "").trim();
  if (!query) {
    return Response.json({ error: "Query parameter q is required." }, { status: 400, headers: cors });
  }
  const requestedDomains = (url.searchParams.get("domains") ?? "")
    .split(",")
    .map((value) => value.trim())
    .filter((value): value is KnowledgeDomain =>
      KNOWLEDGE_DOMAINS.includes(value as KnowledgeDomain),
    );
  const limit = Number(url.searchParams.get("limit") ?? 25);
  const records = await searchKnowledgeRecords({ query, domains: requestedDomains, limit });
  return Response.json({ query, count: records.length, records }, { headers: cors });
}
