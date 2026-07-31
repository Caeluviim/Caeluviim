from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import CandidateBatch, CandidateReview, DialogueIngestRequest
from .projection import GraphProjector
from .service import CaeluviimCore
from .validator import validate_core


def create_mcp_server(data_dir: Path, project_root: Path | None = None):
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "The MCP SDK is not installed. Install the project dependencies first."
        ) from exc

    core = CaeluviimCore(data_dir=data_dir, project_root=project_root)
    core.initialize()
    mcp = FastMCP("caeluviim-local-civic-graph")

    @mcp.tool()
    def get_ingestion_schema() -> dict[str, Any]:
        """Return the exact manual-ingestion, quarantine, and scope contract."""
        return {
            "dialogue": DialogueIngestRequest.model_json_schema(),
            "candidate_batch": CandidateBatch.model_json_schema(),
            "candidate_review": CandidateReview.model_json_schema(),
            "rules": {
                "manual_trigger_required": True,
                "non_official_default": "private",
                "official_default": "official_public",
                "ai_candidate_disposition": "QUARANTINED",
                "private_to_public_use": "explicit_member_grant_required",
            },
        }

    @mcp.tool()
    def ingest_dialogue_source(payload: dict[str, Any]) -> dict[str, Any]:
        """Manually ingest exact selected dialogue. Call only on explicit user instruction."""
        return core.ingest_dialogue(DialogueIngestRequest.model_validate(payload))

    @mcp.tool()
    def stage_analysis_candidates(payload: dict[str, Any]) -> dict[str, Any]:
        """Stage source-bound AI analysis in quarantine; never makes it authoritative."""
        return core.stage_candidates(CandidateBatch.model_validate(payload))

    @mcp.tool()
    def list_quarantined_candidates(
        owner_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """List unresolved candidates visible in the requested member scope."""
        return core.list_quarantined(owner_id=owner_id)

    @mcp.tool()
    def review_candidate(
        payload: dict[str, Any], owner_id: str | None = None
    ) -> dict[str, Any]:
        """Accept, reject, or contest one quarantined candidate through signed history."""
        return core.review_candidate(
            CandidateReview.model_validate(payload), owner_id=owner_id
        )

    @mcp.tool()
    def trace_provenance(
        identifier: str, owner_id: str | None = None
    ) -> dict[str, Any]:
        """Trace event, derivation, predecessor, and supersession history."""
        return core.trace(identifier, owner_id=owner_id)

    @mcp.tool()
    def query_knowledge(
        query: str = "", owner_id: str | None = None
    ) -> dict[str, Any]:
        """Query accepted graph resources without promoting quarantined analysis."""
        dataset = GraphProjector(core).build_dataset(owner_id=owner_id)
        query_lower = query.casefold()
        matches = []
        for subject, predicate, obj, graph in dataset.quads():
            row = {
                "subject": str(subject),
                "predicate": str(predicate),
                "object": str(obj),
                "graph": str(graph),
            }
            if not query_lower or query_lower in " ".join(row.values()).casefold():
                matches.append(row)
            if len(matches) >= 200:
                break
        return {"query": query, "matches": matches}

    @mcp.tool()
    def validate_replay() -> dict[str, Any]:
        """Verify signed logs, replay roots, SHACL, vocabularies, and DAP fixtures."""
        return validate_core(core)

    return mcp


def run_mcp(data_dir: Path, project_root: Path | None = None) -> None:
    mcp = create_mcp_server(data_dir, project_root)
    mcp.run(transport="stdio")
