import {
  EFFECT_KINDS,
  EFFECT_STATUSES,
  createOperativeEffect,
  type EffectKind,
  type EffectStatus,
} from "../../../../lib/language";
import {
  getOperativeEffect,
  queryLanguageForce,
  saveOperativeEffect,
} from "../../../../lib/store";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, POST, OPTIONS",
  "access-control-allow-headers": "content-type",
};

function effectKinds(value: string | null) {
  return (value ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter((item): item is EffectKind => EFFECT_KINDS.includes(item as EffectKind));
}

function effectStatuses(value: string | null) {
  return (value ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter((item): item is EffectStatus => EFFECT_STATUSES.includes(item as EffectStatus));
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const id = url.searchParams.get("id");
  if (id) {
    const effect = await getOperativeEffect(id);
    return effect
      ? Response.json({ effect }, { headers: cors })
      : Response.json({ error: "Operative effect not found." }, { status: 404, headers: cors });
  }
  const result = await queryLanguageForce({
    query: url.searchParams.get("q") ?? undefined,
    effectKinds: effectKinds(url.searchParams.get("effect_kinds")),
    effectStatuses: effectStatuses(url.searchParams.get("statuses")),
    recordId: url.searchParams.get("record_id") ?? undefined,
    jurisdiction: url.searchParams.get("jurisdiction") ?? undefined,
    limit: Number(url.searchParams.get("limit") ?? 50),
  });
  return Response.json(
    {
      protocolVersion: result.protocolVersion,
      count: result.effectCount,
      effects: result.effects,
    },
    { headers: cors },
  );
}

export async function POST(request: Request) {
  const contentLength = Number(request.headers.get("content-length") ?? 0);
  if (contentLength > 1_000_000) {
    return Response.json({ error: "Operative effect exceeds the 1 MB limit." }, { status: 413, headers: cors });
  }
  try {
    const effect = await createOperativeEffect(await request.json());
    const persisted = await saveOperativeEffect(effect);
    return persisted
      ? Response.json({ effect, persisted }, { status: 201, headers: cors })
      : Response.json({ error: "The authoritative graph store is unavailable." }, { status: 503, headers: cors });
  } catch (error) {
    return Response.json(
      { error: error instanceof Error ? error.message : "Operative effect ingestion failed." },
      { status: 400, headers: cors },
    );
  }
}

export function OPTIONS() {
  return new Response(null, { status: 204, headers: cors });
}
