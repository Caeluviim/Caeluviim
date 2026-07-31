// Caeluviim core graph schema v0.1.0
// Community-compatible constraints and indexes only.

CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (n:Entity) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT migration_id_unique IF NOT EXISTS
FOR (m:Migration) REQUIRE m.id IS UNIQUE;

CREATE INDEX entity_record_hash IF NOT EXISTS
FOR (n:Entity) ON (n.record_hash);

CREATE INDEX entity_content_hash IF NOT EXISTS
FOR (n:Entity) ON (n.content_hash);

CREATE INDEX entity_source_id IF NOT EXISTS
FOR (n:Entity) ON (n.source_id);

CREATE INDEX entity_ingest_id IF NOT EXISTS
FOR (n:Entity) ON (n.ingest_id);

CREATE INDEX entity_created_at IF NOT EXISTS
FOR (n:Entity) ON (n.created_at);

CREATE INDEX source_uri IF NOT EXISTS
FOR (n:Source) ON (n.uri);

CREATE INDEX ingest_manifest_hash IF NOT EXISTS
FOR (n:IngestEvent) ON (n.manifest_hash);

CREATE INDEX relation_assertion_type IF NOT EXISTS
FOR (n:RelationAssertion) ON (n.relationship_type);
