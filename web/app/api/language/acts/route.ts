import {
  LANGUAGE_ACT_TYPES,
  createLanguageAct,
  type LanguageActType,
} from "../../../../lib/language";
import {
  getLanguageAct,
  queryLanguageForce,
  saveLanguageAct,
} from "../../../../lib/store";
import { requireWriteAuthorization } from "../../../../lib/write-auth";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, POST, OPTIONS",
  "access-control-allow-headers": "content-type",
};

function actTypes(value: string | null) {
  return (value ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter((item): item is LanguageActType =>
      LANGUAGE_ACT_TYPES.includes(item as LanguageActType),
    );
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const id = url.searchParams.get("id");
  if (id) {
    const act = await getLanguageAct(id);
    return act
      ? Response.json({ act }, { headers: cors })
      : Response.json({ error: "Language act not found." }, { status: 404, headers: cors });
  }
  const result = await queryLanguageForce({
    query: url.searchParams.get("q") ?? undefined,
    actTypes: actTypes(url.searchParams.get("act_types")),
    forces: (url.searchParams.get("forces") ?? "").split(",").map((item) => item.trim()).filter(Boolean),
    recordId: url.searchParams.get("record_id") ?? undefined,
    districtId: url.searchParams.get("district_id") ?? undefined,
    jurisdiction: url.searchParams.get("jurisdiction") ?? undefined,
    limit: Number(url.searchParams.get("limit") ?? 50),
  });
  return Response.json(
    {
      protocolVersion: result.protocolVersion,
      count: result.actCount,
      acts: result.acts,
    },
    { headers: cors },
  );
}

export async function POST(request: Request) {
  const authorizationFailure = requireWriteAuthorization(request, cors);
  if (authorizationFailure) return authorizationFailure;

  const contentLength = Number(request.headers.get("content-length") ?? 0);
  if (contentLength > 1_000_000) {
    return Response.json({ error: "Language act exceeds the 1 MB limit." }, { status: 413, headers: cors });
  }
  try {
    const act = await createLanguageAct(await request.json());
    const persisted = await saveLanguageAct(act);
    return persisted
      ? Response.json({ act, persisted }, { status: 201, headers: cors })
      : Response.json({ error: "The authoritative graph store is unavailable." }, { status: 503, headers: cors });
  } catch (error) {
    return Response.json(
      { error: error instanceof Error ? error.message : "Language act ingestion failed." },
      { status: 400, headers: cors },
    );
  }
}

export function OPTIONS() {
  return new Response(null, { status: 204, headers: cors });
}
