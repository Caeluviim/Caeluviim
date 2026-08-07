from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException

from .client import GraphRuntime, Neo4jConfig

app = FastAPI(title="Caeluviim Runtime", version="0.1.0")
runtime = GraphRuntime(Neo4jConfig.from_env())


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
        result: dict[str, Any] = runtime.stats()
        result["runtime_id"] = os.getenv("CAELUVIIM_RUNTIME_ID", "caeluviim-local")
        result["source_commit"] = os.getenv("CAELUVIIM_SOURCE_COMMIT", "unresolved")
        return result
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
