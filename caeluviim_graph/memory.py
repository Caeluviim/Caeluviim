from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .client import Neo4jConfig, _driver


class MemoryQueryError(ValueError):
    """Raised when a memory query exceeds the bounded retrieval contract."""


def _bounded_int(value: int, *, name: str, minimum: int, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise MemoryQueryError(f"{name} must be an integer")
    if value < minimum or value > maximum:
        raise MemoryQueryError(f"{name} must be between {minimum} and {maximum}")
    return value


def _normalise_labels(labels: Iterable[str] | None) -> list[str]:
    if labels is None:
        return []
    normalised: list[str] = []
    for label in labels:
        value = label.strip()
        if value and value not in normalised:
            normalised.append(value)
    return normalised


@dataclass(frozen=True)
class RecallRequest:
    text: str
    limit: int = 10
    depth: int = 1
    context_limit: int = 8
    labels: tuple[str, ...] = ()

    def validated(self) -> "RecallRequest":
        return RecallRequest(
            text=self.text.strip(),
            limit=_bounded_int(self.limit, name="limit", minimum=1, maximum=50),
            depth=_bounded_int(self.depth, name="depth", minimum=0, maximum=3),
            context_limit=_bounded_int(
                self.context_limit,
                name="context_limit",
                minimum=0,
                maximum=50,
            ),
            labels=tuple(_normalise_labels(self.labels)),
        )


class GraphMemory:
    """Bounded semantic retrieval over the persistent Caeluviim Neo4j graph.

    This layer does not infer truth or ratification. It retrieves ingested records,
    their provenance, and nearby graph context so prior material can become
    operationally available to later reasoning.
    """

    def __init__(self, config: Neo4jConfig):
        self.config = config

    def _execute(self, query: str, **parameters: Any) -> list[dict[str, Any]]:
        with _driver(self.config) as driver:
            records, _, _ = driver.execute_query(
                query,
                database_=self.config.database,
                **parameters,
            )
            return [dict(record) for record in records]

    def entity(self, entity_id: str) -> dict[str, Any] | None:
        entity_id = entity_id.strip()
        if not entity_id:
            raise MemoryQueryError("entity_id must not be empty")
        rows = self._execute(
            """
            MATCH (n:Entity {id: $entity_id})
            OPTIONAL MATCH (n)-[:HAS_PROVENANCE]->(source:Source)
            OPTIONAL MATCH (n)-[outgoing]->(target:Entity)
            OPTIONAL MATCH (origin:Entity)-[incoming]->(n)
            WITH n,
                 [item IN collect(DISTINCT CASE
                     WHEN source IS NULL THEN null
                     ELSE {id: source.id, title: source.title, uri: source.uri,
                           source_type: source.source_type, captured_at: source.captured_at}
                 END) WHERE item IS NOT NULL] AS provenance,
                 [item IN collect(DISTINCT CASE
                     WHEN target IS NULL THEN null
                     ELSE {direction: 'outgoing', type: type(outgoing), id: target.id,
                           labels: labels(target)}
                 END) WHERE item IS NOT NULL][0..100] AS outgoing,
                 [item IN collect(DISTINCT CASE
                     WHEN origin IS NULL THEN null
                     ELSE {direction: 'incoming', type: type(incoming), id: origin.id,
                           labels: labels(origin)}
                 END) WHERE item IS NOT NULL][0..100] AS incoming
            RETURN n.id AS id,
                   labels(n) AS labels,
                   properties(n) AS properties,
                   provenance,
                   outgoing,
                   incoming
            """,
            entity_id=entity_id,
        )
        return rows[0] if rows else None

    def search(
        self,
        text: str,
        *,
        limit: int = 20,
        labels: Iterable[str] | None = None,
    ) -> list[dict[str, Any]]:
        limit = _bounded_int(limit, name="limit", minimum=1, maximum=100)
        query_text = text.strip().lower()
        label_filter = _normalise_labels(labels)
        return self._execute(
            """
            MATCH (n:Entity)
            WHERE ($labels = [] OR any(label IN labels(n) WHERE label IN $labels))
              AND (
                $query = ''
                OR toLower(n.id) CONTAINS $query
                OR any(key IN keys(n)
                       WHERE toLower(coalesce(toString(n[key]), '')) CONTAINS $query)
              )
            OPTIONAL MATCH (n)-[:HAS_PROVENANCE]->(source:Source)
            WITH n,
                 [item IN collect(DISTINCT CASE
                     WHEN source IS NULL THEN null
                     ELSE {id: source.id, title: source.title, uri: source.uri,
                           source_type: source.source_type, captured_at: source.captured_at}
                 END) WHERE item IS NOT NULL] AS provenance
            RETURN n.id AS id,
                   labels(n) AS labels,
                   properties(n) AS properties,
                   provenance
            ORDER BY coalesce(n.updated_at, n.created_at) DESC, n.id
            LIMIT $limit
            """,
            query=query_text,
            labels=label_filter,
            limit=limit,
        )

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
        rows = self._execute(
            f"""
            MATCH (root:Entity {{id: $entity_id}})
            OPTIONAL MATCH path=(root)-[*1..{depth}]-(related:Entity)
            WHERE related <> root
            WITH root, related, path
            ORDER BY CASE WHEN path IS NULL THEN 0 ELSE length(path) END, related.id
            WITH root,
                 [item IN collect(DISTINCT CASE
                     WHEN related IS NULL THEN null
                     ELSE {{
                         id: related.id,
                         labels: labels(related),
                         properties: properties(related),
                         distance: length(path),
                         relationship_types: [relationship IN relationships(path) | type(relationship)]
                     }}
                 END) WHERE item IS NOT NULL][0..$limit] AS neighbors
            RETURN root.id AS id,
                   labels(root) AS labels,
                   properties(root) AS properties,
                   neighbors
            """,
            entity_id=entity_id,
            limit=limit,
        )
        return rows[0] if rows else None

    def timeline(self, *, limit: int = 20) -> list[dict[str, Any]]:
        limit = _bounded_int(limit, name="limit", minimum=1, maximum=100)
        return self._execute(
            """
            MATCH (n:Entity)
            RETURN n.id AS id,
                   labels(n) AS labels,
                   properties(n) AS properties,
                   coalesce(n.updated_at, n.created_at) AS graph_time
            ORDER BY graph_time DESC, n.id
            LIMIT $limit
            """,
            limit=limit,
        )

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
            "query": request.text,
            "labels": list(request.labels),
            "limit": request.limit,
            "depth": request.depth,
            "match_count": len(matches),
            "matches": matches,
        }
