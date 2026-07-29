CREATE TABLE `dap_checkpoints` (
	`checkpoint_id` text PRIMARY KEY NOT NULL,
	`district_id` text NOT NULL,
	`operation_id` text NOT NULL,
	`history_root` text NOT NULL,
	`state_root` text NOT NULL,
	`district_time` text NOT NULL,
	`payload_json` text NOT NULL,
	`finalized_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `dap_checkpoints_operation_id_unique` ON `dap_checkpoints` (`operation_id`);--> statement-breakpoint
CREATE INDEX `dap_checkpoints_district_idx` ON `dap_checkpoints` (`district_id`,`finalized_at`);--> statement-breakpoint
CREATE TABLE `dap_dispositions` (
	`disposition_id` text PRIMARY KEY NOT NULL,
	`operation_id` text NOT NULL,
	`district_id` text NOT NULL,
	`disposition` text NOT NULL,
	`ruleset_id` text NOT NULL,
	`history_root_before` text,
	`state_root_before` text,
	`history_root_after` text,
	`state_root_after` text,
	`payload_json` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `dap_dispositions_operation_context_uidx` ON `dap_dispositions` (`operation_id`,`history_root_before`);--> statement-breakpoint
CREATE INDEX `dap_dispositions_district_idx` ON `dap_dispositions` (`district_id`,`created_at`);--> statement-breakpoint
CREATE TABLE `dap_district_state` (
	`district_id` text PRIMARY KEY NOT NULL,
	`history_root` text NOT NULL,
	`state_root` text NOT NULL,
	`accepted_count` integer NOT NULL,
	`state_json` text NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `dap_districts` (
	`district_id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`protocol_version` text NOT NULL,
	`active_ruleset_id` text NOT NULL,
	`genesis_operation_id` text NOT NULL,
	`status` text NOT NULL,
	`payload_json` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `dap_districts_genesis_operation_id_unique` ON `dap_districts` (`genesis_operation_id`);--> statement-breakpoint
CREATE INDEX `dap_districts_status_idx` ON `dap_districts` (`status`,`created_at`);--> statement-breakpoint
CREATE TABLE `dap_operations` (
	`operation_id` text PRIMARY KEY NOT NULL,
	`district_id` text NOT NULL,
	`operation_type` text NOT NULL,
	`author_identity_id` text NOT NULL,
	`signing_key_id` text NOT NULL,
	`author_sequence` integer NOT NULL,
	`lamport` integer NOT NULL,
	`disposition` text NOT NULL,
	`payload_json` text NOT NULL,
	`accepted_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `dap_operations_author_sequence_uidx` ON `dap_operations` (`district_id`,`signing_key_id`,`author_sequence`);--> statement-breakpoint
CREATE INDEX `dap_operations_district_lamport_idx` ON `dap_operations` (`district_id`,`lamport`,`operation_id`);--> statement-breakpoint
CREATE INDEX `dap_operations_target_type_idx` ON `dap_operations` (`district_id`,`operation_type`);--> statement-breakpoint
CREATE TABLE `dap_rulesets` (
	`ruleset_id` text PRIMARY KEY NOT NULL,
	`district_id` text NOT NULL,
	`ruleset_version` integer NOT NULL,
	`status` text NOT NULL,
	`proposed_by_operation_id` text NOT NULL,
	`activated_by_operation_id` text,
	`payload_json` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `dap_rulesets_district_version_uidx` ON `dap_rulesets` (`district_id`,`ruleset_version`);--> statement-breakpoint
CREATE INDEX `dap_rulesets_district_status_idx` ON `dap_rulesets` (`district_id`,`status`);--> statement-breakpoint
CREATE TABLE `dap_submissions` (
	`operation_id` text PRIMARY KEY NOT NULL,
	`district_id` text NOT NULL,
	`content_hash` text NOT NULL,
	`last_disposition` text NOT NULL,
	`reason_codes_json` text NOT NULL,
	`payload_json` text NOT NULL,
	`received_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `dap_submissions_district_idx` ON `dap_submissions` (`district_id`,`received_at`);