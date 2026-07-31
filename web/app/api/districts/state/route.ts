import { reconstructDapDistrict } from "../../../../lib/dap/kernel";
import { getDapState } from "../../../../lib/dap/store";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, OPTIONS",
  "access-control-allow-headers": "content-type",
};

export async function GET(request: Request) {
  const url = new URL(request.url);
  const districtId = url.searchParams.get("district_id");
  if (!districtId) return Response.json({ error: "district_id is required." }, { status: 400, headers: cors });
  if (url.searchParams.get("reconstruct") === "true") {
    const proof = await reconstructDapDistrict(districtId);
    return proof
      ? Response.json(proof, { headers: cors })
      : Response.json({ error: "District not found." }, { status: 404, headers: cors });
  }
  const state = await getDapState(districtId);
  return state
    ? Response.json(state, { headers: cors })
    : Response.json({ error: "District not found." }, { status: 404, headers: cors });
}

export function OPTIONS() {
  return new Response(null, { status: 204, headers: cors });
}
