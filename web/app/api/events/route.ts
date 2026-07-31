import {
  createResponseEvent,
  validatesProtocolResponse,
  type ConsentScope,
} from "../../../lib/protocol";
import { listResponseEvents, saveResponseEvent } from "../../../lib/store";
import { requireWriteAuthorization } from "../../../lib/write-auth";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, POST, OPTIONS",
  "access-control-allow-headers": "content-type",
};

export async function GET(request: Request) {
  const url = new URL(request.url);
  const requested = Number(url.searchParams.get("limit") ?? "25");
  try {
    const events = await listResponseEvents(Number.isFinite(requested) ? requested : 25);
    return Response.json({ events }, { headers: cors });
  } catch {
    return Response.json({ error: "The event log is unavailable." }, { status: 503, headers: cors });
  }
}

export async function POST(request: Request) {
  const authorizationFailure = requireWriteAuthorization(request, cors);
  if (authorizationFailure) return authorizationFailure;

  try {
    const payload = (await request.json()) as {
      response?: unknown;
      consentScope?: unknown;
    };
    if (!validatesProtocolResponse(payload.response)) {
      return Response.json(
        { error: "The response does not satisfy the complete Caeluviim protocol schema." },
        { status: 422, headers: cors },
      );
    }
    const allowedScopes: ConsentScope[] = ["collective", "group", "private"];
    const consentScope = allowedScopes.includes(payload.consentScope as ConsentScope)
      ? (payload.consentScope as ConsentScope)
      : "collective";
    const event = await createResponseEvent(payload.response, consentScope);
    const persisted = await saveResponseEvent(event);
    if (!persisted) {
      return Response.json({ error: "The authoritative event log is unavailable." }, { status: 503, headers: cors });
    }
    return Response.json(event, { status: 201, headers: cors });
  } catch {
    return Response.json({ error: "Request body must be valid JSON." }, { status: 400, headers: cors });
  }
}

export function OPTIONS() {
  return new Response(null, { status: 204, headers: cors });
}
