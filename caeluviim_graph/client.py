from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .manifest import (
    safe_label_clause,
    safe_relationship_type,
    sha256_record,
)


class GraphConflictError(RuntimeError):
    """Raised when an existing graph identifier is reused with different content."""


@dataclass(frozen=True)
class Neo4jConfig:
    uri: str = "neo4j://localhost:7687"
    user: str = "neo4j"
    password: str = "caeluviim-local"
    database: str = "neo4j"

    @classmethod
    def from_env(cls) -> "Neo4jConfig":
        return cls(
            uri=os.getenv("NEO4J_URI", cls.uri),
            user=os.getenv("NEO4J_USER", cls.user),
            password=os.getenv("NEO4J_PASSWORD", cls.password),
            database=os.getenv("NEO4J_DATABASE", cls.database),
        )


def _driver(config: Neo4jConfig):
    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        raise RuntimeError(
            "The Neo4j Python driver is not installed. Run: pip install -r requirements-dev.txt"
        ) from exc
    return GraphDatabase.driver(config.uri, auth=(config.user, config.password))


def read_cypher_statements(path: str | Path) -> list[str]:
    text = Path(path).read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    lines = [line for line in text.splitlines() if not line.lstrip().startswith("//")]
    return [statement.strip() for statement in "\n".join(lines).split(";") if statement.strip()]


def iter_migration_files(directory: str | Path) -> Iterable[Path]:
    yield from sorted(Path(directory).glob("*.cypher"))


class GraphRuntime:
    def __init__(self, config: Neo4jConfig):
        self.config = config

    def health(self) -> dict[str, Any]:
        with _driver(self.config) as driver:
            driver.verify_connectivity()
            records, summary, _ = driver.execute_query(
                "CALL dbms.components() YIELD versions RETURN 1 AS ok, versions[0] AS version",
                database_=self.config.database,
            )
            return {
                "ok": records[0]["ok"] == 1,
                "version": records[0]["version"],
                "database": self.config.database,
                "server_address": str(summary.server.address),
            }

    def migrate(self, directory: str | Path) -> list[dict[str, Any]]:
        applied: list[dict[str, Any]] = []
        with _driver(self.config) as driver:
            for migration_file in iter_migration_files(directory):
                migration_id = migration_file.name
                migration_hash = sha256_record(migration_file.read_text(encoding="utf-8"))
                records, _, _ = driver.execute_query(
                    "MATCH (m:Migration {id: $id}) RETURN m.migration_hash AS migration_hash",
                    id=migration_id,
                    database_=self.config.database,
                )
                if records:
                    if records[0]["migration_hash"] != migration_hash:
                        raise GraphConflictError(
                            f"Migration {migration_id} already exists with a different hash"
                        )
                    applied.append({"migration_id": migration_id, "status": "already_applied"})
                    continue

                for statement in read_cypher_statements(migration_file):
                    driver.execute_query(statement, database_=self.config.database)

                driver.execute_query(
                    """
                    CREATE (m:Migration {
                        id: $id,
                        migration_hash: $migration_hash,
                        applied_at: datetime()
                    })
                    """,
                    id=migration_id,
                    migration_hash=migration_hash,
                    database_=self.config.database,
                )
                applied.append({"migration_id": migration_id, "status": "applied"})
        return applied

    def ingest(self, manifest: Mapping[str, Any]) -> dict[str, Any]:
        with _driver(self.config) as driver:
            with driver.session(database=self.config.database) as session:
                return session.execute_write(self._ingest_transaction, dict(manifest))

    @classmethod
    def _ingest_transaction(cls, tx, manifest: dict[str, Any]) -> dict[str, Any]:
        manifest_hash = sha256_record(manifest)
        ingest_id = manifest["ingest_id"]
        source = manifest["source"]

        existing = tx.run(
            "MATCH (i:IngestEvent {id: $id}) RETURN i.manifest_hash AS manifest_hash",
            id=ingest_id,
        ).single()
        if existing:
            if existing["manifest_hash"] != manifest_hash:
                raise GraphConflictError(
                    f"Ingest identifier {ingest_id} already exists with different content"
                )
            return {
                "ingest_id": ingest_id,
                "status": "already_ingested",
                "manifest_hash": manifest_hash,
                "nodes": 0,
                "relationships": 0,
            }

        cls._create_entity(
            tx,
            entity_id=source["source_id"],
            labels=["Source"],
            properties={
                "source_type": source["source_type"],
                "title": source["title"],
                "uri": source.get("uri"),
                "authority": source.get("authority"),
                "captured_at": source["captured_at"],
            },
            record_hash=sha256_record(source),
            content_hash=source["content_hash"],
            ingest_id=ingest_id,
            source_id=source["source_id"],
            allow_internal_label=True,
        )

        cls._create_entity(
            tx,
            entity_id=ingest_id,
            labels=["IngestEvent"],
            properties={
                "manifest_version": manifest["manifest_version"],
                "manifest_hash": manifest_hash,
                "source_id": source["source_id"],
            },
            record_hash=manifest_hash,
            content_hash=source["content_hash"],
            ingest_id=ingest_id,
            source_id=source["source_id"],
            allow_internal_label=True,
        )

        tx.run(
            """
            MATCH (i:IngestEvent {id: $ingest_id}), (s:Source {id: $source_id})
            MERGE (i)-[:INGESTED_SOURCE]->(s)
            """,
            ingest_id=ingest_id,
            source_id=source["source_id"],
        ).consume()

        for node in manifest["nodes"]:
            cls._create_entity(
                tx,
                entity_id=node["id"],
                labels=node["labels"],
                properties=node.get("properties", {}),
                record_hash=sha256_record(node),
                content_hash=source["content_hash"],
                ingest_id=ingest_id,
                source_id=source["source_id"],
            )
            cls._link_provenance(tx, ingest_id, source["source_id"], node["id"])

        for relationship in manifest["relationships"]:
            cls._create_relationship_assertion(
                tx,
                relationship=relationship,
                ingest_id=ingest_id,
                source_id=source["source_id"],
                content_hash=source["content_hash"],
            )

        tx.run(
            "MATCH (i:IngestEvent {id: $id}) SET i.completed_at = datetime()",
            id=ingest_id,
        ).consume()

        return {
            "ingest_id": ingest_id,
            "status": "ingested",
            "manifest_hash": manifest_hash,
            "nodes": len(manifest["nodes"]),
            "relationships": len(manifest["relationships"]),
        }

    @classmethod
    def _create_entity(
        cls,
        tx,
        *,
        entity_id: str,
        labels: list[str],
        properties: Mapping[str, Any],
        record_hash: str,
        content_hash: str,
        ingest_id: str,
        source_id: str,
        allow_internal_label: bool = False,
    ) -> None:
        existing = tx.run(
            "MATCH (n:Entity {id: $id}) RETURN n.record_hash AS record_hash",
            id=entity_id,
        ).single()
        if existing:
            if existing["record_hash"] != record_hash:
                raise GraphConflictError(
                    f"Entity {entity_id} already exists with different content"
                )
            return

        if allow_internal_label:
            label_clause = ":".join(["Entity", *labels])
        else:
            label_clause = safe_label_clause(labels)

        query = f"""
        CREATE (n:{label_clause} {{id: $id}})
        SET n += $properties,
            n.record_hash = $record_hash,
            n.content_hash = $content_hash,
            n.ingest_id = $ingest_id,
            n.source_id = $source_id,
            n.created_at = datetime(),
            n.updated_at = datetime()
        """
        tx.run(
            query,
            id=entity_id,
            properties={key: value for key, value in properties.items() if value is not None},
            record_hash=record_hash,
            content_hash=content_hash,
            ingest_id=ingest_id,
            source_id=source_id,
        ).consume()

    @classmethod
    def _create_relationship_assertion(
        cls,
        tx,
        *,
        relationship: Mapping[str, Any],
        ingest_id: str,
        source_id: str,
        content_hash: str,
    ) -> None:
        relationship_type = safe_relationship_type(relationship["type"])
        assertion_id = relationship["id"]
        record_hash = sha256_record(relationship)

        cls._create_entity(
            tx,
            entity_id=assertion_id,
            labels=["RelationAssertion"],
            properties={
                "relationship_type": relationship_type,
                "from_id": relationship["from"],
                "to_id": relationship["to"],
                **relationship.get("properties", {}),
            },
            record_hash=record_hash,
            content_hash=content_hash,
            ingest_id=ingest_id,
            source_id=source_id,
            allow_internal_label=True,
        )

        query = f"""
        MATCH (a:Entity {{id: $from_id}}),
              (b:Entity {{id: $to_id}}),
              (ra:RelationAssertion {{id: $assertion_id}})
        MERGE (a)-[r:{relationship_type} {{assertion_id: $assertion_id}}]->(b)
        ON CREATE SET r += $properties,
                      r.record_hash = $record_hash,
                      r.content_hash = $content_hash,
                      r.ingest_id = $ingest_id,
                      r.source_id = $source_id,
                      r.created_at = datetime()
        MERGE (ra)-[:FROM_ENTITY]->(a)
        MERGE (ra)-[:TO_ENTITY]->(b)
        """
        tx.run(
            query,
            from_id=relationship["from"],
            to_id=relationship["to"],
            assertion_id=assertion_id,
            properties=relationship.get("properties", {}),
            record_hash=record_hash,
            content_hash=content_hash,
            ingest_id=ingest_id,
            source_id=source_id,
        ).consume()
        cls._link_provenance(tx, ingest_id, source_id, assertion_id)

    @staticmethod
    def _link_provenance(tx, ingest_id: str, source_id: str, entity_id: str) -> None:
        tx.run(
            """
            MATCH (i:IngestEvent {id: $ingest_id}),
                  (s:Source {id: $source_id}),
                  (n:Entity {id: $entity_id})
            MERGE (n)-[:HAS_PROVENANCE {ingest_id: $ingest_id}]->(s)
            MERGE (i)-[:INGESTED_ENTITY]->(n)
            """,
            ingest_id=ingest_id,
            source_id=source_id,
            entity_id=entity_id,
        ).consume()

    def stats(self) -> dict[str, int]:
        with _driver(self.config) as driver:
            records, _, _ = driver.execute_query(
                """
                CALL {
                    MATCH (n:Entity) RETURN count(n) AS entities
                }
                CALL {
                    MATCH (i:IngestEvent) RETURN count(i) AS ingests
                }
                CALL {
                    MATCH (r:RelationAssertion) RETURN count(r) AS assertions
                }
                CALL {
                    MATCH ()-[r]->() RETURN count(r) AS relationships
                }
                RETURN entities, ingests, assertions, relationships
                """,
                database_=self.config.database,
            )
            return dict(records[0])
