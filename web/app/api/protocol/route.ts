import { PROTOCOL_DESCRIPTOR } from "../../../lib/protocol";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, OPTIONS",
  "access-control-allow-headers": "content-type",
};

export function GET() {
  return Response.json(PROTOCOL_DESCRIPTOR, { headers: cors });
}

export function OPTIONS() {
  return new Response(null, { status: 204, headers: cors });
}
