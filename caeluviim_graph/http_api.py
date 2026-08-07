from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .client import GraphRuntime, Neo4jConfig

app = FastAPI(title="Caeluviim Runtime", version="0.1.0")
runtime = GraphRuntime(Neo4jConfig.from_env())


class CypherRequest(BaseModel):
    query: str
    parameters: dict[str, Any] = {}


@app.get("/health")
def health() -> dict[str, Any]:
    try:
        result = runtime.health()
        result["runtime_id"] = os.getenv("CAELUVIIM_RUNTIME_ID", "caeluviim-local")
        result["source_commit"] = os.getenv("CAELUVIIM_SOURCE_COMMIT", "unresolved")
        return result
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/stats")
def stats() -> dict[str, Any]:
    try:
        return runtime.query(
            "MATCH (n) WITH count(n) AS nodes MATCH ()-[r]->() RETURN nodes, count(r) AS relationships"
        )[0]
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/query")
def query(request: CypherRequest) -> dict[str, Any]:
    # Read-only endpoint by construction: reject mutation/admin clauses.
    normalized = " " + " ".join(request.query.upper().split()) + " "
    forbidden = (" CREATE ", " MERGE ", " DELETE ", " DETACH ", " SET ", " REMOVE ", " DROP ", " LOAD CSV ", " CALL DBMS.")
    if any(token in normalized for token in forbidden):
        raise HTTPException(status_code=400, detail="/query accepts read-only Cypher")
    try:
        rows = runtime.query(request.query, request.parameters)
        return {"rows": rows, "count": len(rows)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
