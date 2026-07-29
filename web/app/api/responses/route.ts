import { listProtocolResponses } from "../../../lib/store";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, OPTIONS",
  "access-control-allow-headers": "content-type",
};

export async function GET(request: Request) {
  const url = new URL(request.url);
  const requested = Number(url.searchParams.get("limit") ?? "12");
  try {
    const responses = await listProtocolResponses(Number.isFinite(requested) ? requested : 12);
    return Response.json({ responses }, { headers: cors });
  } catch {
    return Response.json({ responses: [], storage: "unavailable" }, { headers: cors });
  }
}

export function OPTIONS() {
  return new Response(null, { status: 204, headers: cors });
}
