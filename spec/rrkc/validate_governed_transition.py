#!/usr/bin/env python3
"""Dependency-free semantic validator for RRKC governed-transition events.

This complements governed-transition-event.schema.json. It intentionally checks
the schema's structural and conditional invariants without claiming RFC 8785
canonicalization, digest verification, governance ratification, or runtime
ingestion.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

OPERATIONS = {"amend", "ratify", "revoke", "delegate", "veto", "suspend", "restore"}
KINDS = {
    "Entity",
    "Claim",
    "Evidence",
    "Relation",
    "Activity",
    "Agent",
    "Policy",
    "Provenance",
    "VetoEvent",
    "State",
}
ADMISSIBILITY_STATUSES = {"admissible", "inadmissible", "contested", "undetermined"}
AUTHORIZATION_STATUSES = {"authorized", "unauthorized", "contested", "undetermined"}
VETO_STATUSES = {"active", "withdrawn", "overridden", "expired"}
EVIDENCE_RELATIONS = {"supports", "rebuts", "contextualizes"}
HASH_ALGORITHMS = {"SHA-256", "SHA-384", "SHA-512"}
EVENT_ID_RE = re.compile(r"^[A-Za-z0-9._:-]+$")
HEX_RE = re.compile(r"^[A-Fa-f0-9]+$")

TOP_LEVEL_KEYS = {
    "event_id",
    "event_version",
    "operation",
    "subject",
    "actor",
    "pre_state",
    "post_state",
    "evidence",
    "admissibility",
    "governance",
    "provenance",
    "integrity",
}
TOP_LEVEL_REQUIRED = TOP_LEVEL_KEYS - {"evidence"}


def _required(obj: dict[str, Any], keys: set[str], path: str, errors: list[str]) -> None:
    missing = sorted(keys - obj.keys())
    for key in missing:
        errors.append(f"{path}.{key}: missing required property")


def _no_extra(obj: dict[str, Any], allowed: set[str], path: str, errors: list[str]) -> None:
    for key in sorted(obj.keys() - allowed):
        errors.append(f"{path}.{key}: additional property is not allowed")


def _nonempty_string(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{path}: expected non-empty string")


def _validate_ref(value: Any, path: str, errors: list[str], *, kind: str | None = None) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object reference")
        return
    allowed = {"id", "kind", "version"}
    required = {"id", "kind"}
    _required(value, required, path, errors)
    _no_extra(value, allowed, path, errors)
    _nonempty_string(value.get("id"), f"{path}.id", errors)
    if value.get("kind") not in KINDS:
        errors.append(f"{path}.kind: invalid kind {value.get('kind')!r}")
    if kind is not None and value.get("kind") != kind:
        errors.append(f"{path}.kind: expected {kind!r}")
    if "version" in value:
        _nonempty_string(value.get("version"), f"{path}.version", errors)


def _validate_ref_list(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}: expected array")
        return
    for i, item in enumerate(value):
        _validate_ref(item, f"{path}[{i}]", errors)


def _validate_recorded_at(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        errors.append(f"{path}: expected date-time string")
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{path}: invalid ISO 8601 date-time")
        return
    if parsed.tzinfo is None:
        errors.append(f"{path}: date-time must include an offset or Z")


def validate_event(event: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(event, dict):
        return ["$: expected JSON object"]

    _required(event, TOP_LEVEL_REQUIRED, "$", errors)
    _no_extra(event, TOP_LEVEL_KEYS, "$", errors)

    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not EVENT_ID_RE.fullmatch(event_id):
        errors.append("$.event_id: must match ^[A-Za-z0-9._:-]+$")

    if event.get("event_version") != "0.1.0":
        errors.append("$.event_version: expected '0.1.0'")

    if event.get("operation") not in OPERATIONS:
        errors.append(f"$.operation: invalid operation {event.get('operation')!r}")

    _validate_ref(event.get("subject"), "$.subject", errors)
    _validate_ref(event.get("actor"), "$.actor", errors)
    _validate_ref(event.get("pre_state"), "$.pre_state", errors, kind="State")
    _validate_ref(event.get("post_state"), "$.post_state", errors, kind="State")

    evidence = event.get("evidence", [])
    if not isinstance(evidence, list):
        errors.append("$.evidence: expected array")
    else:
        seen: set[str] = set()
        for i, item in enumerate(evidence):
            path = f"$.evidence[{i}]"
            if not isinstance(item, dict):
                errors.append(f"{path}: expected object")
                continue
            _required(item, {"evidence", "relation", "claim"}, path, errors)
            _no_extra(item, {"evidence", "relation", "claim"}, path, errors)
            _validate_ref(item.get("evidence"), f"{path}.evidence", errors)
            if item.get("relation") not in EVIDENCE_RELATIONS:
                errors.append(f"{path}.relation: invalid relation {item.get('relation')!r}")
            _validate_ref(item.get("claim"), f"{path}.claim", errors)
            fingerprint = json.dumps(item, sort_keys=True, separators=(",", ":"))
            if fingerprint in seen:
                errors.append(f"{path}: duplicate evidence item")
            seen.add(fingerprint)

    admissibility = event.get("admissibility")
    if not isinstance(admissibility, dict):
        errors.append("$.admissibility: expected object")
    else:
        path = "$.admissibility"
        _required(admissibility, {"status", "ruleset", "reasons"}, path, errors)
        _no_extra(admissibility, {"status", "ruleset", "reasons"}, path, errors)
        status = admissibility.get("status")
        if status not in ADMISSIBILITY_STATUSES:
            errors.append(f"{path}.status: invalid status {status!r}")
        _validate_ref(admissibility.get("ruleset"), f"{path}.ruleset", errors)
        reasons = admissibility.get("reasons")
        if not isinstance(reasons, list):
            errors.append(f"{path}.reasons: expected array")
        else:
            for i, reason in enumerate(reasons):
                _nonempty_string(reason, f"{path}.reasons[{i}]", errors)
            if status == "inadmissible" and not reasons:
                errors.append(f"{path}.reasons: inadmissible status requires at least one reason")

    governance = event.get("governance")
    if not isinstance(governance, dict):
        errors.append("$.governance: expected object")
    else:
        path = "$.governance"
        _required(governance, {"policy", "authorization", "vetoes", "blocked"}, path, errors)
        _no_extra(governance, {"policy", "authorization", "vetoes", "blocked"}, path, errors)
        _validate_ref(governance.get("policy"), f"{path}.policy", errors)

        authorization = governance.get("authorization")
        if not isinstance(authorization, dict):
            errors.append(f"{path}.authorization: expected object")
        else:
            apath = f"{path}.authorization"
            _required(authorization, {"status", "basis"}, apath, errors)
            _no_extra(authorization, {"status", "basis"}, apath, errors)
            if authorization.get("status") not in AUTHORIZATION_STATUSES:
                errors.append(f"{apath}.status: invalid status {authorization.get('status')!r}")
            _validate_ref_list(authorization.get("basis"), f"{apath}.basis", errors)

        vetoes = governance.get("vetoes")
        active_veto = False
        if not isinstance(vetoes, list):
            errors.append(f"{path}.vetoes: expected array")
        else:
            for i, veto in enumerate(vetoes):
                vpath = f"{path}.vetoes[{i}]"
                if not isinstance(veto, dict):
                    errors.append(f"{vpath}: expected object")
                    continue
                _required(veto, {"veto_id", "actor", "status", "basis"}, vpath, errors)
                _no_extra(veto, {"veto_id", "actor", "status", "basis"}, vpath, errors)
                _nonempty_string(veto.get("veto_id"), f"{vpath}.veto_id", errors)
                _validate_ref(veto.get("actor"), f"{vpath}.actor", errors)
                if veto.get("status") not in VETO_STATUSES:
                    errors.append(f"{vpath}.status: invalid status {veto.get('status')!r}")
                if veto.get("status") == "active":
                    active_veto = True
                _nonempty_string(veto.get("basis"), f"{vpath}.basis", errors)

        blocked = governance.get("blocked")
        if not isinstance(blocked, bool):
            errors.append(f"{path}.blocked: expected boolean")
        elif blocked and not active_veto:
            errors.append(f"{path}.blocked: true requires at least one active veto")

    provenance = event.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("$.provenance: expected object")
    else:
        path = "$.provenance"
        _required(provenance, {"derived_from", "witnesses", "recorded_at"}, path, errors)
        _no_extra(provenance, {"derived_from", "witnesses", "recorded_at", "external_anchor"}, path, errors)
        _validate_ref_list(provenance.get("derived_from"), f"{path}.derived_from", errors)
        _validate_ref_list(provenance.get("witnesses"), f"{path}.witnesses", errors)
        _validate_recorded_at(provenance.get("recorded_at"), f"{path}.recorded_at", errors)
        if "external_anchor" in provenance:
            _nonempty_string(provenance.get("external_anchor"), f"{path}.external_anchor", errors)

    integrity = event.get("integrity")
    if not isinstance(integrity, dict):
        errors.append("$.integrity: expected object")
    else:
        path = "$.integrity"
        _required(integrity, {"canonicalization", "hash_algorithm", "event_hash"}, path, errors)
        _no_extra(integrity, {"canonicalization", "hash_algorithm", "prev_hash", "event_hash"}, path, errors)
        if integrity.get("canonicalization") != "RFC8785":
            errors.append(f"{path}.canonicalization: expected 'RFC8785'")
        if integrity.get("hash_algorithm") not in HASH_ALGORITHMS:
            errors.append(f"{path}.hash_algorithm: invalid algorithm {integrity.get('hash_algorithm')!r}")
        if "prev_hash" in integrity and integrity.get("prev_hash") is not None:
            prev_hash = integrity.get("prev_hash")
            if not isinstance(prev_hash, str) or not HEX_RE.fullmatch(prev_hash):
                errors.append(f"{path}.prev_hash: expected non-empty hexadecimal string or null")
        event_hash = integrity.get("event_hash")
        if not isinstance(event_hash, str) or not HEX_RE.fullmatch(event_hash):
            errors.append(f"{path}.event_hash: expected non-empty hexadecimal string")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate RRKC governed-transition event JSON using dependency-free semantic checks."
    )
    parser.add_argument("files", nargs="+", type=Path, help="JSON event files to validate")
    args = parser.parse_args(argv)

    failed = False
    for path in args.files:
        try:
            event = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            failed = True
            print(f"FAIL {path}: {exc}")
            continue

        errors = validate_event(event)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
