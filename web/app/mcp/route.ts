import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { createCaeluviimMcpServer } from "../../lib/mcp";
import { requireWriteAuthorization } from "../../lib/write-auth";

const corsHeaders = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, POST, DELETE, OPTIONS",
  "access-control-allow-headers":
    "Content-Type, mcp-session-id, Last-Event-ID, mcp-protocol-version",
  "access-control-expose-headers": "mcp-session-id, mcp-protocol-version",
};

async function handle(request: Request) {
  const authorizationFailure = requireWriteAuthorization(request, corsHeaders);
  if (authorizationFailure) return authorizationFailure;

  const transport = new WebStandardStreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  });
  const server = createCaeluviimMcpServer();
  await server.connect(transport);
  const result = await transport.handleRequest(request);
  const headers = new Headers(result.headers);
  Object.entries(corsHeaders).forEach(([key, value]) => headers.set(key, value));
  return new Response(result.body, {
    status: result.status,
    statusText: result.statusText,
    headers,
  });
}

export const GET = handle;
export const POST = handle;
export const DELETE = handle;

export function OPTIONS() {
  return new Response(null, { status: 204, headers: corsHeaders });
}
