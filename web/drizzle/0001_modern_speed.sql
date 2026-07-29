CREATE TABLE `knowledge_edges_v2` (
	`edge_id` text PRIMARY KEY NOT NULL,
	`subject_id` text NOT NULL,
	`predicate` text NOT NULL,
	`object_id` text NOT NULL,
	`evidence_record_ids_json` text NOT NULL,
	`payload_json` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `knowledge_edges_v2_subject_idx` ON `knowledge_edges_v2` (`subject_id`,`created_at`);--> statement-breakpoint
CREATE INDEX `knowledge_edges_v2_object_idx` ON `knowledge_edges_v2` (`object_id`,`created_at`);--> statement-breakpoint
CREATE TABLE `knowledge_records_v2` (
	`id` text PRIMARY KEY NOT NULL,
	`record_type` text NOT NULL,
	`label` text NOT NULL,
	`content` text NOT NULL,
	`domains_json` text NOT NULL,
	`topics_json` text NOT NULL,
	`source_title` text NOT NULL,
	`source_url` text NOT NULL,
	`source_locator` text NOT NULL,
	`source_excerpt` text NOT NULL,
	`content_hash` text NOT NULL,
	`source_hash` text NOT NULL,
	`construction_rule` text NOT NULL,
	`conflict_group` text,
	`language` text NOT NULL,
	`jurisdiction` text,
	`source_published_at` text,
	`source_retrieved_at` text NOT NULL,
	`payload_json` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `knowledge_records_v2_type_idx` ON `knowledge_records_v2` (`record_type`,`created_at`);--> statement-breakpoint
CREATE INDEX `knowledge_records_v2_conflict_idx` ON `knowledge_records_v2` (`conflict_group`,`created_at`);