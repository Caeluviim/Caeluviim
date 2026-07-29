import { env } from "cloudflare:workers";
import { base58btc, domainDigest } from "./canonical";
import type {
  AcceptedDapOperation,
  DapOperationEnvelope,
  DapRuleset,
  DapValidationResult,
  StoredDapDistrict,
  StoredDapState,
} from "./types";

const schemaStatements = [
  `CREATE TABLE IF NOT EXISTS dap_districts (
    district_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    protocol_version TEXT NOT NULL,
    active_ruleset_id TEXT NOT NULL,
    genesis_operation_id TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
  )`,
  `CREATE INDEX IF NOT EXISTS dap_districts_status_idx
    ON dap_districts(status, created_at DESC)`,
  `CREATE TABLE IF NOT EXISTS dap_rulesets (
    ruleset_id TEXT PRIMARY KEY,
    district_id TEXT NOT NULL,
    ruleset_version INTEGER NOT NULL,
    status TEXT NOT NULL,
    proposed_by_operation_id TEXT NOT NULL,
    activated_by_operation_id TEXT,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(district_id, ruleset_version)
  )`,
  `CREATE INDEX IF NOT EXISTS dap_rulesets_district_status_idx
    ON dap_rulesets(district_id, status)`,
  `CREATE TABLE IF NOT EXISTS dap_submissions (
    operation_id TEXT PRIMARY KEY,
    district_id TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    last_disposition TEXT NOT NULL,
    reason_codes_json TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    received_at TEXT NOT NULL
  )`,
  `CREATE INDEX IF NOT EXISTS dap_submissions_district_idx
    ON dap_submissions(district_id, received_at DESC)`,
  `CREATE TABLE IF NOT EXISTS dap_operations (
    operation_id TEXT PRIMARY KEY,
    district_id TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    author_identity_id TEXT NOT NULL,
    signing_key_id TEXT NOT NULL,
    author_sequence INTEGER NOT NULL,
    lamport INTEGER NOT NULL,
    disposition TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    accepted_at TEXT NOT NULL,
    UNIQUE(district_id, signing_key_id, author_sequence)
  )`,
  `CREATE INDEX IF NOT EXISTS dap_operations_district_lamport_idx
    ON dap_operations(district_id, lamport, operation_id)`,
  `CREATE INDEX IF NOT EXISTS dap_operations_target_type_idx
    ON dap_operations(district_id, operation_type)`,
  `CREATE TABLE IF NOT EXISTS dap_district_state (
    district_id TEXT PRIMARY KEY,
    history_root TEXT NOT NULL,
    state_root TEXT NOT NULL,
    accepted_count INTEGER NOT NULL,
    state_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
  )`,
  `CREATE TABLE IF NOT EXISTS dap_dispositions (
    disposition_id TEXT PRIMARY KEY,
    operation_id TEXT NOT NULL,
    district_id TEXT NOT NULL,
    disposition TEXT NOT NULL,
    ruleset_id TEXT NOT NULL,
    history_root_before TEXT,
    state_root_before TEXT,
    history_root_after TEXT,
    state_root_after TEXT,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(operation_id, history_root_before)
  )`,
  `CREATE INDEX IF NOT EXISTS dap_dispositions_district_idx
    ON dap_dispositions(district_id, created_at DESC)`,
  `CREATE TABLE IF NOT EXISTS dap_checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    district_id TEXT NOT NULL,
    operation_id TEXT NOT NULL UNIQUE,
    history_root TEXT NOT NULL,
    state_root TEXT NOT NULL,
    district_time TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    finalized_at TEXT NOT NULL
  )`,
  `CREATE INDEX IF NOT EXISTS dap_checkpoints_district_idx
    ON dap_checkpoints(district_id, finalized_at DESC)`,
];

function getDb() {
  if (!env.DB) throw new Error("D1 binding `DB` is required for DAP authoritative state");
  return env.DB;
}

export async function ensureDapSchema() {
  const db = getDb();
  await db.batch(schemaStatements.map((statement) => db.prepare(statement)));
  return db;
}

function parseJson<T>(value: string): T {
  return JSON.parse(value) as T;
}

async function dispositionId(result: DapValidationResult) {
  return `disposition:${base58btc(await domainDigest("DAP-DISPOSITION-0.2", result))}`;
}

export async function getDapDistrict(districtId: string) {
  const db = await ensureDapSchema();
  const row = await db
    .prepare(
      `SELECT district_id, name, protocol_version, active_ruleset_id,
              genesis_operation_id, status, created_at
       FROM dap_districts WHERE district_id = ? LIMIT 1`,
    )
    .bind(districtId)
    .all<StoredDapDistrict>();
  return row.results[0] ?? null;
}

export async function listDapDistricts(limit = 50) {
  const db = await ensureDapSchema();
  const safeLimit = Math.min(Math.max(Math.trunc(limit), 1), 100);
  const result = await db
    .prepare(
      `SELECT d.district_id, d.name, d.protocol_version, d.active_ruleset_id,
              d.genesis_operation_id, d.status, d.created_at,
              s.history_root, s.state_root, s.accepted_count, s.updated_at
       FROM dap_districts d
       JOIN dap_district_state s ON s.district_id = d.district_id
       ORDER BY d.created_at DESC LIMIT ?`,
    )
    .bind(safeLimit)
    .all<Record<string, unknown>>();
  return result.results;
}

export async function getDapRuleset(rulesetId: string) {
  const db = await ensureDapSchema();
  const result = await db
    .prepare(`SELECT payload_json FROM dap_rulesets WHERE ruleset_id = ? LIMIT 1`)
    .bind(rulesetId)
    .all<{ payload_json: string }>();
  return result.results[0] ? parseJson<DapRuleset>(result.results[0].payload_json) : null;
}

export async function getDapState(districtId: string) {
  const db = await ensureDapSchema();
  const result = await db
    .prepare(
      `SELECT district_id, history_root, state_root, accepted_count, state_json, updated_at
       FROM dap_district_state WHERE district_id = ? LIMIT 1`,
    )
    .bind(districtId)
    .all<{
      district_id: string;
      history_root: string;
      state_root: string;
      accepted_count: number;
      state_json: string;
      updated_at: string;
    }>();
  const row = result.results[0];
  if (!row) return null;
  return {
    district_id: row.district_id,
    history_root: row.history_root,
    state_root: row.state_root,
    accepted_count: row.accepted_count,
    state: parseJson(row.state_json),
    updated_at: row.updated_at,
  } as StoredDapState;
}

export async function getDapSubmission(operationId: string) {
  const db = await ensureDapSchema();
  const result = await db
    .prepare(
      `SELECT s.payload_json AS operation_json, s.last_disposition,
              s.reason_codes_json, d.payload_json AS validation_json
       FROM dap_submissions s
       LEFT JOIN dap_dispositions d
         ON d.operation_id = s.operation_id AND d.disposition = s.last_disposition
       WHERE s.operation_id = ?
       ORDER BY d.created_at DESC LIMIT 1`,
    )
    .bind(operationId)
    .all<{
      operation_json: string;
      last_disposition: string;
      reason_codes_json: string;
      validation_json: string | null;
    }>();
  const row = result.results[0];
  return row
    ? {
        operation: parseJson<DapOperationEnvelope>(row.operation_json),
        last_disposition: row.last_disposition,
        reason_codes: parseJson<string[]>(row.reason_codes_json),
        validation: row.validation_json ? parseJson<DapValidationResult>(row.validation_json) : null,
      }
    : null;
}

export async function getAcceptedDapOperations(districtId: string) {
  const db = await ensureDapSchema();
  const result = await db
    .prepare(
      `SELECT payload_json, disposition FROM dap_operations
       WHERE district_id = ? ORDER BY lamport, operation_id`,
    )
    .bind(districtId)
    .all<{ payload_json: string; disposition: AcceptedDapOperation["disposition"] }>();
  return result.results.map((row) => ({
    envelope: parseJson<DapOperationEnvelope>(row.payload_json),
    disposition: row.disposition,
  }));
}

export async function getAcceptedDapOperation(operationId: string) {
  const db = await ensureDapSchema();
  const result = await db
    .prepare(`SELECT payload_json, disposition FROM dap_operations WHERE operation_id = ? LIMIT 1`)
    .bind(operationId)
    .all<{ payload_json: string; disposition: AcceptedDapOperation["disposition"] }>();
  const row = result.results[0];
  return row ? { envelope: parseJson<DapOperationEnvelope>(row.payload_json), disposition: row.disposition } : null;
}

export async function getLastKeyOperation(districtId: string, keyId: string) {
  const db = await ensureDapSchema();
  const result = await db
    .prepare(
      `SELECT operation_id, author_sequence FROM dap_operations
       WHERE district_id = ? AND signing_key_id = ?
       ORDER BY author_sequence DESC LIMIT 1`,
    )
    .bind(districtId, keyId)
    .all<{ operation_id: string; author_sequence: number }>();
  return result.results[0] ?? null;
}

export async function listDapHistory(districtId: string, limit = 100) {
  const db = await ensureDapSchema();
  const safeLimit = Math.min(Math.max(Math.trunc(limit), 1), 500);
  const result = await db
    .prepare(
      `SELECT operation_id, operation_type, author_identity_id, signing_key_id,
              author_sequence, lamport, disposition, payload_json, accepted_at
       FROM dap_operations WHERE district_id = ?
       ORDER BY lamport, operation_id LIMIT ?`,
    )
    .bind(districtId, safeLimit)
    .all<{
      operation_id: string;
      operation_type: string;
      author_identity_id: string;
      signing_key_id: string;
      author_sequence: number;
      lamport: number;
      disposition: AcceptedDapOperation["disposition"];
      payload_json: string;
      accepted_at: string;
    }>();
  return result.results.map((row) => ({ ...row, envelope: parseJson(String(row.payload_json)), payload_json: undefined }));
}

export async function saveRejectedDapSubmission(operation: DapOperationEnvelope, result: DapValidationResult) {
  const db = await ensureDapSchema();
  const receivedAt = new Date().toISOString();
  const id = await dispositionId(result);
  await db.batch([
    db
      .prepare(
        `INSERT INTO dap_submissions
          (operation_id, district_id, content_hash, last_disposition, reason_codes_json, payload_json, received_at)
         VALUES (?, ?, ?, ?, ?, ?, ?)
         ON CONFLICT(operation_id) DO NOTHING`,
      )
      .bind(
        operation.operation_id,
        operation.district_id,
        operation.content_hash,
        result.disposition,
        JSON.stringify(result.reason_codes),
        JSON.stringify(operation),
        receivedAt,
      ),
    db
      .prepare(
        `INSERT OR IGNORE INTO dap_dispositions
          (disposition_id, operation_id, district_id, disposition, ruleset_id,
           history_root_before, state_root_before, history_root_after, state_root_after,
           payload_json, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      )
      .bind(
        id,
        operation.operation_id,
        operation.district_id,
        result.disposition,
        operation.ruleset_id,
        result.history_root_before,
        result.state_root_before,
        result.history_root_after,
        result.state_root_after,
        JSON.stringify(result),
        receivedAt,
      ),
  ]);
}

export async function createDapGenesis(
  operation: DapOperationEnvelope,
  ruleset: DapRuleset,
  state: StoredDapState,
  result: DapValidationResult,
) {
  const db = await ensureDapSchema();
  const createdAt = new Date().toISOString();
  const id = await dispositionId(result);
  await db.batch([
    db
      .prepare(
        `INSERT INTO dap_districts
          (district_id, name, protocol_version, active_ruleset_id, genesis_operation_id,
           status, payload_json, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      )
      .bind(
        operation.district_id,
        state.state.district.name,
        operation.protocol_version,
        ruleset.ruleset_id,
        operation.operation_id,
        "active",
        JSON.stringify(state.state.district),
        createdAt,
      ),
    db
      .prepare(
        `INSERT INTO dap_rulesets
          (ruleset_id, district_id, ruleset_version, status, proposed_by_operation_id,
           activated_by_operation_id, payload_json, created_at)
         VALUES (?, ?, ?, 'active', ?, ?, ?, ?)`,
      )
      .bind(
        ruleset.ruleset_id,
        operation.district_id,
        ruleset.ruleset_version,
        operation.operation_id,
        operation.operation_id,
        JSON.stringify(ruleset),
        createdAt,
      ),
    db
      .prepare(
        `INSERT INTO dap_submissions
          (operation_id, district_id, content_hash, last_disposition, reason_codes_json, payload_json, received_at)
         VALUES (?, ?, ?, ?, ?, ?, ?)`,
      )
      .bind(
        operation.operation_id,
        operation.district_id,
        operation.content_hash,
        result.disposition,
        JSON.stringify(result.reason_codes),
        JSON.stringify(operation),
        createdAt,
      ),
    db
      .prepare(
        `INSERT INTO dap_operations
          (operation_id, district_id, operation_type, author_identity_id, signing_key_id,
           author_sequence, lamport, disposition, payload_json, accepted_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      )
      .bind(
        operation.operation_id,
        operation.district_id,
        operation.operation_type,
        operation.author.identity_id,
        operation.author.signing_key_id,
        operation.causal.author_sequence,
        operation.causal.logical_time.lamport,
        result.disposition,
        JSON.stringify(operation),
        createdAt,
      ),
    db
      .prepare(
        `INSERT INTO dap_district_state
          (district_id, history_root, state_root, accepted_count, state_json, updated_at)
         VALUES (?, ?, ?, ?, ?, ?)`,
      )
      .bind(
        state.district_id,
        state.history_root,
        state.state_root,
        state.accepted_count,
        JSON.stringify(state.state),
        createdAt,
      ),
    db
      .prepare(
        `INSERT INTO dap_dispositions
          (disposition_id, operation_id, district_id, disposition, ruleset_id,
           history_root_before, state_root_before, history_root_after, state_root_after,
           payload_json, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      )
      .bind(
        id,
        operation.operation_id,
        operation.district_id,
        result.disposition,
        operation.ruleset_id,
        null,
        null,
        state.history_root,
        state.state_root,
        JSON.stringify(result),
        createdAt,
      ),
  ]);
}

export async function acceptDapOperation(
  operation: DapOperationEnvelope,
  stateBefore: StoredDapState,
  stateAfter: StoredDapState,
  result: DapValidationResult,
) {
  const db = await ensureDapSchema();
  const acceptedAt = new Date().toISOString();
  const id = await dispositionId(result);
  const statements = [
    db
      .prepare(
        `INSERT INTO dap_submissions
          (operation_id, district_id, content_hash, last_disposition, reason_codes_json, payload_json, received_at)
         VALUES (?, ?, ?, ?, ?, ?, ?)
         ON CONFLICT(operation_id) DO UPDATE SET
           last_disposition = excluded.last_disposition,
           reason_codes_json = excluded.reason_codes_json`,
      )
      .bind(
        operation.operation_id,
        operation.district_id,
        operation.content_hash,
        result.disposition,
        JSON.stringify(result.reason_codes),
        JSON.stringify(operation),
        acceptedAt,
      ),
    db
      .prepare(
        `INSERT INTO dap_operations
          (operation_id, district_id, operation_type, author_identity_id, signing_key_id,
           author_sequence, lamport, disposition, payload_json, accepted_at)
         SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
         WHERE EXISTS (
           SELECT 1 FROM dap_district_state WHERE district_id = ? AND history_root = ?
         )`,
      )
      .bind(
        operation.operation_id,
        operation.district_id,
        operation.operation_type,
        operation.author.identity_id,
        operation.author.signing_key_id,
        operation.causal.author_sequence,
        operation.causal.logical_time.lamport,
        result.disposition,
        JSON.stringify(operation),
        acceptedAt,
        operation.district_id,
        stateBefore.history_root,
      ),
    db
      .prepare(
        `UPDATE dap_district_state
         SET history_root = ?, state_root = ?, accepted_count = ?, state_json = ?, updated_at = ?
         WHERE district_id = ? AND history_root = ?
           AND EXISTS (SELECT 1 FROM dap_operations WHERE operation_id = ?)`,
      )
      .bind(
        stateAfter.history_root,
        stateAfter.state_root,
        stateAfter.accepted_count,
        JSON.stringify(stateAfter.state),
        acceptedAt,
        operation.district_id,
        stateBefore.history_root,
        operation.operation_id,
      ),
    db
      .prepare(
        `UPDATE dap_districts SET active_ruleset_id = ?, status = ?, payload_json = ?
         WHERE district_id = ?
           AND EXISTS (SELECT 1 FROM dap_district_state WHERE district_id = ? AND history_root = ?)`,
      )
      .bind(
        stateAfter.state.district.active_ruleset_id,
        stateAfter.state.district.status,
        JSON.stringify(stateAfter.state.district),
        operation.district_id,
        operation.district_id,
        stateAfter.history_root,
      ),
    db
      .prepare(
        `INSERT INTO dap_dispositions
          (disposition_id, operation_id, district_id, disposition, ruleset_id,
           history_root_before, state_root_before, history_root_after, state_root_after,
           payload_json, created_at)
         SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
         WHERE EXISTS (
           SELECT 1 FROM dap_district_state WHERE district_id = ? AND history_root = ?
         )`,
      )
      .bind(
        id,
        operation.operation_id,
        operation.district_id,
        result.disposition,
        operation.ruleset_id,
        stateBefore.history_root,
        stateBefore.state_root,
        stateAfter.history_root,
        stateAfter.state_root,
        JSON.stringify(result),
        acceptedAt,
        operation.district_id,
        stateAfter.history_root,
      ),
  ];
  if (operation.operation_type === "RULESET_PROPOSE" && operation.payload.ruleset) {
    const ruleset = operation.payload.ruleset as DapRuleset;
    statements.push(
      db
        .prepare(
          `INSERT OR IGNORE INTO dap_rulesets
            (ruleset_id, district_id, ruleset_version, status, proposed_by_operation_id,
             activated_by_operation_id, payload_json, created_at)
           VALUES (?, ?, ?, 'proposed', ?, NULL, ?, ?)`,
        )
        .bind(
          ruleset.ruleset_id,
          operation.district_id,
          ruleset.ruleset_version,
          operation.operation_id,
          JSON.stringify(ruleset),
          acceptedAt,
        ),
    );
  }
  if (operation.operation_type === "RULESET_ACTIVATE") {
    statements.push(
      db
        .prepare(
          `UPDATE dap_rulesets SET status = 'superseded'
           WHERE ruleset_id = ? AND district_id = ?`,
        )
        .bind(operation.ruleset_id, operation.district_id),
      db
        .prepare(
          `UPDATE dap_rulesets SET status = 'active', activated_by_operation_id = ?
           WHERE ruleset_id = ? AND district_id = ?`,
        )
        .bind(operation.operation_id, operation.payload.ruleset_id, operation.district_id),
    );
  }
  if (operation.operation_type === "CHECKPOINT_FINALIZE") {
    statements.push(
      db
        .prepare(
          `INSERT OR IGNORE INTO dap_checkpoints
            (checkpoint_id, district_id, operation_id, history_root, state_root,
             district_time, payload_json, finalized_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
        )
        .bind(
          operation.payload.checkpoint_id,
          operation.district_id,
          operation.operation_id,
          stateAfter.history_root,
          stateAfter.state_root,
          stateAfter.state.district.district_time,
          JSON.stringify(operation.payload),
          acceptedAt,
        ),
    );
  }
  await db.batch(statements);
  const persisted = await getDapState(operation.district_id);
  const accepted = persisted?.history_root === stateAfter.history_root;
  if (!accepted) {
    await db
      .prepare(
        `UPDATE dap_submissions
         SET last_disposition = 'QUARANTINED', reason_codes_json = '["ERR_CONCURRENT_STATE"]'
         WHERE operation_id = ?
           AND NOT EXISTS (SELECT 1 FROM dap_operations WHERE operation_id = ?)`,
      )
      .bind(operation.operation_id, operation.operation_id)
      .run();
  }
  return accepted;
}
