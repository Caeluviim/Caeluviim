import { getDapOperationStatus, submitDapOperation } from "../../../../lib/dap/kernel";
import { listDapHistory } from "../../../../lib/dap/store";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, POST, OPTIONS",
  "access-control-allow-headers": "content-type",
};

export async function GET(request: Request) {
  const url = new URL(request.url);
  const operationId = url.searchParams.get("operation_id");
  if (operationId) {
    const operation = await getDapOperationStatus(operationId);
    return operation
      ? Response.json(operation, { headers: cors })
      : Response.json({ error: "Operation submission not found." }, { status: 404, headers: cors });
  }
  const districtId = url.searchParams.get("district_id");
  if (!districtId) {
    return Response.json({ error: "district_id or operation_id is required." }, { status: 400, headers: cors });
  }
  const limit = Number(url.searchParams.get("limit") ?? 100);
  const operations = await listDapHistory(districtId, limit);
  return Response.json({ district_id: districtId, operations, count: operations.length }, { headers: cors });
}

export async function POST(request: Request) {
  const contentLength = Number(request.headers.get("content-length") ?? 0);
  if (contentLength > 1_000_000) {
    return Response.json({ error: "DAP envelope exceeds the 1 MB submission limit." }, { status: 413, headers: cors });
  }
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "Request body must be valid JSON." }, { status: 400, headers: cors });
  }
  const outcome = await submitDapOperation(body);
  return Response.json(outcome, { status: outcome.httpStatus, headers: cors });
}

export function OPTIONS() {
  return new Response(null, { status: 204, headers: cors });
}
