from __future__ import annotations

import json
from collections import deque
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

from .manifest import load_manifest, load_schema, sha256_record, validate_manifest
from .memory import MemoryQueryError, RecallRequest, _bounded_int, _normalise_labels


class RepositoryMemory:
    """Read-only memory projection built directly from repository manifests.

    This backend requires no Neo4j server, Docker runtime, Codex session, or network
    service. It reconstructs the same entity and relationship topology that the
    Neo4j ingestion runtime materializes from validated repository files. Neo4j
    remains the preferred persistent runtime for mutation receipts, database
    indexes, and larger traversals; this backend is the durable repository fallback.
    """

    def __init__(self, manifest_directory: str | Path, schema_path: str | Path):
        self.manifest_directory = Path(manifest_directory)
        self.schema_path = Path(schema_path)
        self._entities: dict[str, dict[str, Any]] = {}
        self._relationships: list[dict[str, Any]] = []
        self._adjacency: dict[str, list[dict[str, Any]]] = {}
        self._manifest_count = 0
        self._load()

    def _manifest_paths(self) -> list[Path]:
        return sorted(
            {
                *self.manifest_directory.glob("*.json"),
                *self.manifest_directory.glob("*.json.gz.b64"),
            }
        )

    @staticmethod
    def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": source["source_id"],
            "title": source["title"],
            "uri": source.get("uri"),
            "source_type": source["source_type"],
            "captured_at": source["captured_at"],
            "authority": source.get("authority"),
        }

    def _put_entity(self, entity: dict[str, Any]) -> None:
        existing = self._entities.get(entity["id"])
        if existing is None:
            self._entities[entity["id"]] = entity
            return
        comparable_existing = {
            "labels": existing["labels"],
            "properties": existing["properties"],
        }
        comparable_new = {
            "labels": entity["labels"],
            "properties": entity["properties"],
        }
        if comparable_existing != comparable_new:
            raise MemoryQueryError(
                f"repository entity {entity['id']} resolves to conflicting content"
            )
        for source in entity.get("provenance", []):
            if source not in existing["provenance"]:
                existing["provenance"].append(source)
        existing["captured_at"] = max(
            existing.get("captured_at", ""), entity.get("captured_at", "")
        )

    def _put_relationship(
        self,
        *,
        relationship_id: str,
        relationship_type: str,
        from_id: str,
        to_id: str,
        properties: dict[str, Any] | None = None,
        source_id: str | None = None,
    ) -> None:
        if from_id not in self._entities or to_id not in self._entities:
            raise MemoryQueryError(
                f"repository relationship {relationship_id} has an unresolved endpoint"
            )
        relationship = {
            "id": relationship_id,
            "type": relationship_type,
            "from": from_id,
            "to": to_id,
            "properties": deepcopy(properties or {}),
            "source_id": source_id,
        }
        self._relationships.append(relationship)
        self._adjacency.setdefault(from_id, []).append(
            {
                "neighbor_id": to_id,
                "direction": "outgoing",
                "type": relationship_type,
                "relationship_id": relationship_id,
            }
        )
        self._adjacency.setdefault(to_id, []).append(
            {
                "neighbor_id": from_id,
                "direction": "incoming",
                "type": relationship_type,
                "relationship_id": relationship_id,
            }
        )

    def _load(self) -> None:
        schema = load_schema(self.schema_path)
        manifests: list[dict[str, Any]] = []
        for path in self._manifest_paths():
            manifests.append(validate_manifest(load_manifest(path), schema))
        self._manifest_count = len(manifests)

        for manifest in manifests:
            source = manifest["source"]
            source_summary = self._source_summary(source)
            captured_at = source["captured_at"]
            source_id = source["source_id"]
            ingest_id = manifest["ingest_id"]

            self._put_entity(
                {
                    "id": source_id,
                    "labels": ["Entity", "Source"],
                    "properties": {
                        "source_type": source["source_type"],
                        "title": source["title"],
                        "uri": source.get("uri"),
                        "authority": source.get("authority"),
                        "content_hash": source["content_hash"],
                        "captured_at": captured_at,
                    },
                    "provenance": [],
                    "captured_at": captured_at,
                }
            )
            self._put_entity(
                {
                    "id": ingest_id,
                    "labels": ["Entity", "IngestEvent"],
                    "properties": {
                        "manifest_version": manifest["manifest_version"],
                        "manifest_hash": sha256_record(manifest),
                        "source_id": source_id,
                    },
                    "provenance": [],
                    "captured_at": captured_at,
                }
            )
            for node in manifest["nodes"]:
                self._put_entity(
                    {
                        "id": node["id"],
                        "labels": ["Entity", *node["labels"]],
                        "properties": deepcopy(node.get("properties", {})),
                        "provenance": [source_summary],
                        "captured_at": captured_at,
                    }
                )
            for relationship in manifest["relationships"]:
                self._put_entity(
                    {
                        "id": relationship["id"],
                        "labels": ["Entity", "RelationAssertion"],
                        "properties": {
                            "relationship_type": relationship["type"],
                            "from_id": relationship["from"],
                            "to_id": relationship["to"],
                            **deepcopy(relationship.get("properties", {})),
                        },
                        "provenance": [source_summary],
                        "captured_at": captured_at,
                    }
                )

        for manifest in manifests:
            source_id = manifest["source"]["source_id"]
            ingest_id = manifest["ingest_id"]
            self._put_relationship(
                relationship_id=f"{ingest_id}:INGESTED_SOURCE",
                relationship_type="INGESTED_SOURCE",
                from_id=ingest_id,
                to_id=source_id,
                source_id=source_id,
            )
            for node in manifest["nodes"]:
                self._put_relationship(
                    relationship_id=f"{ingest_id}:INGESTED_ENTITY:{node['id']}",
                    relationship_type="INGESTED_ENTITY",
                    from_id=ingest_id,
                    to_id=node["id"],
                    source_id=source_id,
                )
                self._put_relationship(
                    relationship_id=f"{node['id']}:HAS_PROVENANCE:{source_id}",
                    relationship_type="HAS_PROVENANCE",
                    from_id=node["id"],
                    to_id=source_id,
                    source_id=source_id,
                )
            for relationship in manifest["relationships"]:
                assertion_id = relationship["id"]
                self._put_relationship(
                    relationship_id=assertion_id,
                    relationship_type=relationship["type"],
                    from_id=relationship["from"],
                    to_id=relationship["to"],
                    properties=relationship.get("properties", {}),
                    source_id=source_id,
                )
                self._put_relationship(
                    relationship_id=f"{assertion_id}:FROM_ENTITY",
                    relationship_type="FROM_ENTITY",
                    from_id=assertion_id,
                    to_id=relationship["from"],
                    source_id=source_id,
                )
                self._put_relationship(
                    relationship_id=f"{assertion_id}:TO_ENTITY",
                    relationship_type="TO_ENTITY",
                    from_id=assertion_id,
                    to_id=relationship["to"],
                    source_id=source_id,
                )
                self._put_relationship(
                    relationship_id=f"{assertion_id}:HAS_PROVENANCE:{source_id}",
                    relationship_type="HAS_PROVENANCE",
                    from_id=assertion_id,
                    to_id=source_id,
                    source_id=source_id,
                )
                self._put_relationship(
                    relationship_id=f"{ingest_id}:INGESTED_ENTITY:{assertion_id}",
                    relationship_type="INGESTED_ENTITY",
                    from_id=ingest_id,
                    to_id=assertion_id,
                    source_id=source_id,
                )

        for edges in self._adjacency.values():
            edges.sort(
                key=lambda edge: (
                    edge["neighbor_id"],
                    edge["type"],
                    edge["direction"],
                    edge["relationship_id"],
                )
            )

    def stats(self) -> dict[str, int]:
        return {
            "entities": len(self._entities),
            "relationships": len(self._relationships),
            "manifests": self._manifest_count,
        }

    def entity(self, entity_id: str) -> dict[str, Any] | None:
        entity_id = entity_id.strip()
        if not entity_id:
            raise MemoryQueryError("entity_id must not be empty")
        entity = self._entities.get(entity_id)
        if entity is None:
            return None
        outgoing: list[dict[str, Any]] = []
        incoming: list[dict[str, Any]] = []
        for edge in self._adjacency.get(entity_id, []):
            related = self._entities[edge["neighbor_id"]]
            item = {
                "direction": edge["direction"],
                "type": edge["type"],
                "id": related["id"],
                "labels": related["labels"],
                "relationship_id": edge["relationship_id"],
            }
            if edge["direction"] == "outgoing":
                outgoing.append(item)
            else:
                incoming.append(item)
        return {
            "id": entity["id"],
            "labels": deepcopy(entity["labels"]),
            "properties": deepcopy(entity["properties"]),
            "provenance": deepcopy(entity["provenance"]),
            "outgoing": outgoing[:100],
            "incoming": incoming[:100],
        }

    def search(
        self,
        text: str,
        *,
        limit: int = 20,
        labels: Iterable[str] | None = None,
    ) -> list[dict[str, Any]]:
        limit = _bounded_int(limit, name="limit", minimum=1, maximum=100)
        query_text = text.strip().casefold()
        label_filter = set(_normalise_labels(labels))
        matches: list[dict[str, Any]] = []
        for entity in self._entities.values():
            if label_filter and not label_filter.intersection(entity["labels"]):
                continue
            searchable = "\n".join(
                [
                    entity["id"],
                    " ".join(entity["labels"]),
                    json.dumps(
                        entity["properties"],
                        ensure_ascii=False,
                        sort_keys=True,
                        default=str,
                    ),
                    json.dumps(
                        entity["provenance"],
                        ensure_ascii=False,
                        sort_keys=True,
                        default=str,
                    ),
                ]
            ).casefold()
            if query_text and query_text not in searchable:
                continue
            matches.append(
                {
                    "id": entity["id"],
                    "labels": deepcopy(entity["labels"]),
                    "properties": deepcopy(entity["properties"]),
                    "provenance": deepcopy(entity["provenance"]),
                    "captured_at": entity.get("captured_at"),
                }
            )
        matches.sort(key=lambda item: (item.get("captured_at") or "", item["id"]), reverse=True)
        return matches[:limit]

    def neighbors(
        self,
        entity_id: str,
        *,
        depth: int = 1,
        limit: int = 50,
    ) -> dict[str, Any] | None:
        entity_id = entity_id.strip()
        if not entity_id:
            raise MemoryQueryError("entity_id must not be empty")
        depth = _bounded_int(depth, name="depth", minimum=1, maximum=3)
        limit = _bounded_int(limit, name="limit", minimum=1, maximum=200)
        root = self._entities.get(entity_id)
        if root is None:
            return None

        queue: deque[tuple[str, int, tuple[str, ...]]] = deque(
            [(entity_id, 0, tuple())]
        )
        visited = {entity_id}
        neighbors: list[dict[str, Any]] = []
        while queue and len(neighbors) < limit:
            current_id, distance, path_types = queue.popleft()
            if distance >= depth:
                continue
            for edge in self._adjacency.get(current_id, []):
                neighbor_id = edge["neighbor_id"]
                if neighbor_id in visited:
                    continue
                visited.add(neighbor_id)
                related = self._entities[neighbor_id]
                relationship_types = (*path_types, edge["type"])
                neighbors.append(
                    {
                        "id": neighbor_id,
                        "labels": deepcopy(related["labels"]),
                        "properties": deepcopy(related["properties"]),
                        "distance": distance + 1,
                        "relationship_types": list(relationship_types),
                    }
                )
                if len(neighbors) >= limit:
                    break
                queue.append((neighbor_id, distance + 1, relationship_types))

        return {
            "id": root["id"],
            "labels": deepcopy(root["labels"]),
            "properties": deepcopy(root["properties"]),
            "neighbors": neighbors,
        }

    def timeline(self, *, limit: int = 20) -> list[dict[str, Any]]:
        limit = _bounded_int(limit, name="limit", minimum=1, maximum=100)
        items = [
            {
                "id": entity["id"],
                "labels": deepcopy(entity["labels"]),
                "properties": deepcopy(entity["properties"]),
                "graph_time": entity.get("captured_at"),
            }
            for entity in self._entities.values()
        ]
        items.sort(key=lambda item: (item.get("graph_time") or "", item["id"]), reverse=True)
        return items[:limit]

    def recall(self, request: RecallRequest) -> dict[str, Any]:
        request = request.validated()
        matches = self.search(
            request.text,
            limit=request.limit,
            labels=request.labels,
        )
        if request.depth > 0 and request.context_limit > 0:
            for match in matches:
                neighborhood = self.neighbors(
                    match["id"],
                    depth=request.depth,
                    limit=request.context_limit,
                )
                match["context"] = [] if neighborhood is None else neighborhood["neighbors"]
        else:
            for match in matches:
                match["context"] = []
        return {
            "backend": "repository",
            "query": request.text,
            "labels": list(request.labels),
            "limit": request.limit,
            "depth": request.depth,
            "match_count": len(matches),
            "stats": self.stats(),
            "matches": matches,
        }
