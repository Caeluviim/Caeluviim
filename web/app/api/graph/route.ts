import { listProtocolResponses, queryLanguageForce } from "../../../lib/store";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, OPTIONS",
  "access-control-allow-headers": "content-type",
};

export async function GET(request: Request) {
  const url = new URL(request.url);
  const requested = Number(url.searchParams.get("limit") ?? "25");
  try {
    const limit = Number.isFinite(requested) ? requested : 25;
    const [responses, language] = await Promise.all([
      listProtocolResponses(limit),
      queryLanguageForce({
        query: url.searchParams.get("q") ?? undefined,
        recordId: url.searchParams.get("record_id") ?? undefined,
        districtId: url.searchParams.get("district_id") ?? undefined,
        jurisdiction: url.searchParams.get("jurisdiction") ?? undefined,
        limit,
      }),
    ]);
    return Response.json(
      {
        schema: "caeluviim-unified-graph/1.0",
        responseCount: responses.length,
        languageActCount: language.actCount,
        operativeEffectCount: language.effectCount,
        knowledgeRecordCount: language.recordCount,
        nodes: [
          ...language.graph.nodes,
          ...responses.flatMap((response) => response.graph.nodes),
        ],
        edges: [
          ...language.graph.edges,
          ...responses.flatMap((response) => response.graph.edges),
        ],
      },
      { headers: cors },
    );
  } catch {
    return Response.json(
      { error: "The collective graph is unavailable." },
      { status: 503, headers: cors },
    );
  }
}

export function OPTIONS() {
  return new Response(null, { status: 204, headers: cors });
}
