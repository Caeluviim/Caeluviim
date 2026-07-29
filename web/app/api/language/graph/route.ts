import {
  EFFECT_KINDS,
  EFFECT_STATUSES,
  LANGUAGE_ACT_TYPES,
  languageGraphToJsonLd,
  languageGraphToNQuads,
  type EffectKind,
  type EffectStatus,
  type LanguageActType,
} from "../../../../lib/language";
import { queryLanguageForce } from "../../../../lib/store";

const cors = { "access-control-allow-origin": "*" };

function enumList<T extends string>(value: string | null, allowed: readonly T[]) {
  return (value ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter((item): item is T => allowed.includes(item as T));
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const result = await queryLanguageForce({
    query: url.searchParams.get("q") ?? undefined,
    actTypes: enumList<LanguageActType>(url.searchParams.get("act_types"), LANGUAGE_ACT_TYPES),
    forces: (url.searchParams.get("forces") ?? "").split(",").map((item) => item.trim()).filter(Boolean),
    effectKinds: enumList<EffectKind>(url.searchParams.get("effect_kinds"), EFFECT_KINDS),
    effectStatuses: enumList<EffectStatus>(url.searchParams.get("statuses"), EFFECT_STATUSES),
    recordId: url.searchParams.get("record_id") ?? undefined,
    districtId: url.searchParams.get("district_id") ?? undefined,
    jurisdiction: url.searchParams.get("jurisdiction") ?? undefined,
    limit: Number(url.searchParams.get("limit") ?? 50),
  });
  const format = (url.searchParams.get("format") ?? "json").toLocaleLowerCase();
  if (format === "nquads" || format === "nq") {
    return new Response(languageGraphToNQuads(result.graph), {
      headers: { ...cors, "content-type": "application/n-quads; charset=utf-8" },
    });
  }
  if (format === "jsonld" || format === "json-ld") {
    return Response.json(languageGraphToJsonLd(result.graph), {
      headers: { ...cors, "content-type": "application/ld+json; charset=utf-8" },
    });
  }
  return Response.json(result, { headers: cors });
}

export function OPTIONS() {
  return new Response(null, { status: 204, headers: cors });
}
