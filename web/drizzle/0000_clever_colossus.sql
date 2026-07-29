CREATE TABLE `graph_edges` (
	`response_id` text NOT NULL,
	`edge_id` text NOT NULL,
	`subject_id` text NOT NULL,
	`predicate` text NOT NULL,
	`object_id` text NOT NULL,
	PRIMARY KEY(`response_id`, `edge_id`)
);
--> statement-breakpoint
CREATE TABLE `graph_nodes` (
	`response_id` text NOT NULL,
	`node_id` text NOT NULL,
	`node_type` text NOT NULL,
	`label` text NOT NULL,
	`value` text,
	`is_empty` integer DEFAULT 0 NOT NULL,
	PRIMARY KEY(`response_id`, `node_id`)
);
--> statement-breakpoint
CREATE TABLE `protocol_events` (
	`event_id` text PRIMARY KEY NOT NULL,
	`response_id` text NOT NULL,
	`event_type` text NOT NULL,
	`protocol_version` text NOT NULL,
	`content_hash` text NOT NULL,
	`consent_scope` text NOT NULL,
	`partition_key` text NOT NULL,
	`ingestion_status` text NOT NULL,
	`payload_json` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `protocol_events_response_id_unique` ON `protocol_events` (`response_id`);--> statement-breakpoint
CREATE INDEX `protocol_events_partition_idx` ON `protocol_events` (`partition_key`,`created_at`);--> statement-breakpoint
CREATE INDEX `protocol_events_scope_idx` ON `protocol_events` (`consent_scope`,`created_at`);--> statement-breakpoint
CREATE TABLE `protocol_responses` (
	`id` text PRIMARY KEY NOT NULL,
	`prompt` text NOT NULL,
	`schema_version` text NOT NULL,
	`column_order_json` text NOT NULL,
	`row_json` text NOT NULL,
	`csv_text` text NOT NULL,
	`payload_json` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `protocol_responses_created_at_idx` ON `protocol_responses` (`created_at`);