import {
  composeProtocolResponse,
  createResponseEvent,
  type DistrictResponseContext,
  type ProtocolSource,
} from "../../../lib/protocol";
import { reconstructDapDistrict } from "../../../lib/dap/kernel";
import { listDapHistory } from "../../../lib/dap/store";
import { saveResponseEvent } from "../../../lib/store";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "POST, OPTIONS",
  "access-control-allow-headers": "content-type",
};

export async function POST(request: Request) {
  try {
    const payload = (await request.json()) as {
      prompt?: unknown;
      sources?: unknown;
      district_id?: unknown;
    };
    if (typeof payload.prompt !== "string" || !payload.prompt.trim()) {
      return Response.json(
        { error: "A non-empty prompt string is required." },
        { status: 400, headers: cors },
      );
    }
    if (payload.prompt.length > 10_000) {
      return Response.json(
        { error: "Prompt exceeds the 10,000 character limit." },
        { status: 413, headers: cors },
      );
    }

    const sources = Array.isArray(payload.sources)
      ? payload.sources.filter(
          (source): source is ProtocolSource =>
            Boolean(source) && typeof source === "object" && "title" in source,
        )
      : [];
    let districtContext: DistrictResponseContext | undefined;
    if (typeof payload.district_id === "string" && payload.district_id) {
      const proof = await reconstructDapDistrict(payload.district_id);
      if (!proof) {
        return Response.json({ error: "District not found." }, { status: 404, headers: cors });
      }
      const history = await listDapHistory(payload.district_id, 500);
      districtContext = {
        districtId: proof.district_id,
        name: proof.state.district.name,
        status: proof.state.district.status,
        activeRulesetId: proof.state.district.active_ruleset_id,
        districtTime: proof.state.district.district_time,
        acceptedOperationCount: proof.accepted_operation_count,
        pendingOperationCount: history.filter((operation) => operation.disposition === "ACCEPTED_PENDING").length,
        activeMemberCount: Object.values(proof.state.memberships).filter((membership) => membership.status === "active").length,
        activeAuthorityCount: Object.values(proof.state.authorities).filter((authority) => authority.status === "active").length,
        unresolvedConflictCount: Object.keys(proof.state.unresolved_conflicts).length,
        proposalStates: Object.values(proof.state.proposals).map((proposal) => `${proposal.title}: ${proposal.state}`),
        historyRoot: proof.reconstructed_history_root,
        stateRoot: proof.reconstructed_state_root,
        historyRootMatches: proof.history_root_matches,
        stateRootMatches: proof.state_root_matches,
      };
      sources.push({
        title: `Accepted DAP history for ${proof.district_id}`,
        url: `/api/districts/state?district_id=${encodeURIComponent(proof.district_id)}&reconstruct=true`,
        kind: "dap-reconstruction",
      });
    }
    const response = composeProtocolResponse(payload.prompt, sources, districtContext);

    try {
      const event = await createResponseEvent(response, "collective");
      event.response.persisted = await saveResponseEvent(event);
      if (!event.response.persisted) {
        return Response.json(
          { error: "The authoritative event log and graph store are unavailable." },
          { status: 503, headers: cors },
        );
      }
      return Response.json(event.response, { headers: cors });
    } catch {
      return Response.json(
        { error: "The authoritative event log and graph store are unavailable." },
        { status: 503, headers: cors },
      );
    }
  } catch {
    return Response.json(
      { error: "Request body must be valid JSON." },
      { status: 400, headers: cors },
    );
  }
}

export function OPTIONS() {
  return new Response(null, { status: 204, headers: cors });
}
