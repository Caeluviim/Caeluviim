CREATE TABLE `language_acts_v1` (
	`id` text PRIMARY KEY NOT NULL,
	`act_type` text NOT NULL,
	`force` text NOT NULL,
	`status` text NOT NULL,
	`authority_status` text NOT NULL,
	`medium` text NOT NULL,
	`language` text NOT NULL,
	`jurisdiction` text,
	`district_id` text,
	`source_record_id` text NOT NULL,
	`speaker_record_id` text NOT NULL,
	`payload_json` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `language_acts_v1_type_idx` ON `language_acts_v1` (`act_type`,`created_at`);--> statement-breakpoint
CREATE INDEX `language_acts_v1_force_idx` ON `language_acts_v1` (`force`,`created_at`);--> statement-breakpoint
CREATE INDEX `language_acts_v1_status_idx` ON `language_acts_v1` (`status`,`created_at`);--> statement-breakpoint
CREATE INDEX `language_acts_v1_source_idx` ON `language_acts_v1` (`source_record_id`,`created_at`);--> statement-breakpoint
CREATE INDEX `language_acts_v1_speaker_idx` ON `language_acts_v1` (`speaker_record_id`,`created_at`);--> statement-breakpoint
CREATE INDEX `language_acts_v1_district_idx` ON `language_acts_v1` (`district_id`,`created_at`);--> statement-breakpoint
CREATE TABLE `operative_effects_v1` (
	`id` text PRIMARY KEY NOT NULL,
	`language_act_id` text NOT NULL,
	`effect_kind` text NOT NULL,
	`operator` text NOT NULL,
	`status` text NOT NULL,
	`jurisdiction` text,
	`realized_by_operation_id` text,
	`payload_json` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `operative_effects_v1_act_idx` ON `operative_effects_v1` (`language_act_id`,`created_at`);--> statement-breakpoint
CREATE INDEX `operative_effects_v1_kind_idx` ON `operative_effects_v1` (`effect_kind`,`created_at`);--> statement-breakpoint
CREATE INDEX `operative_effects_v1_operator_idx` ON `operative_effects_v1` (`operator`,`created_at`);--> statement-breakpoint
CREATE INDEX `operative_effects_v1_status_idx` ON `operative_effects_v1` (`status`,`created_at`);--> statement-breakpoint
CREATE INDEX `operative_effects_v1_operation_idx` ON `operative_effects_v1` (`realized_by_operation_id`,`created_at`);