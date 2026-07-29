from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jsonschema import Draft202012Validator

from .canonical import operation_identifiers, ruleset_identifier, sign_digest
from .projection import GraphProjector
from .service import CaeluviimCore


def validate_dap_compatibility(project_root: Path) -> dict[str, Any]:
    spec_root = project_root / "web" / "spec" / "dap" / "0.2"
    operation = json.loads(
        (spec_root / "examples" / "proposal-submit.operation.json").read_text("utf-8")
    )
    ruleset = json.loads(
        (spec_root / "examples" / "alpha-12.ruleset.json").read_text("utf-8")
    )
    operation_id, content_hash, digest = operation_identifiers(operation)
    calculated_ruleset_id = ruleset_identifier(ruleset)
    seed = bytes.fromhex(
        "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
    )
    private_key = Ed25519PrivateKey.from_private_bytes(seed)
    calculated_signature = sign_digest(private_key, digest)
    python_checks = {
        "ruleset_id": calculated_ruleset_id == ruleset["ruleset_id"],
        "operation_id": operation_id == operation["operation_id"],
        "content_hash": content_hash == operation["content_hash"],
        "signature": calculated_signature == operation["signature"]["value"],
    }
    node = subprocess.run(
        ["node", "scripts/verify-dap-spec.mjs"],
        cwd=project_root / "web",
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "python_checks": python_checks,
        "python_conforms": all(python_checks.values()),
        "typescript_oracle_exit_code": node.returncode,
        "typescript_oracle_conforms": node.returncode == 0,
        "typescript_oracle_output": (node.stdout + node.stderr).strip(),
    }


def validate_vocabularies(project_root: Path) -> dict[str, Any]:
    results = {}
    for path in sorted((project_root / "vocab").glob("*.json")):
        value = json.loads(path.read_text("utf-8"))
        required = {
            "vocabulary_id",
            "version",
            "status",
            "coverage_status",
            "entries",
        }
        ids = [entry["id"] for entry in value.get("entries", [])]
        results[path.name] = {
            "required_fields": required.issubset(value),
            "nonempty": bool(ids),
            "stable_ids_unique": len(ids) == len(set(ids)),
            "coverage_explicit": value.get("coverage_status") in {
                "incomplete",
                "complete",
            },
        }
    return {
        "files": results,
        "conforms": bool(results)
        and all(all(checks.values()) for checks in results.values()),
    }


def validate_schemas(core: CaeluviimCore) -> dict[str, Any]:
    schema_results: dict[str, dict[str, Any]] = {}
    loaded: dict[str, Any] = {}
    for path in sorted((core.project_root / "schemas").glob("*.schema.json")):
        schema = json.loads(path.read_text("utf-8"))
        Draft202012Validator.check_schema(schema)
        loaded[path.name] = schema
        schema_results[path.name] = {"valid_schema": True}

    event_schema = loaded.get("civic-event.schema.json")
    event_errors: list[dict[str, Any]] = []
    if event_schema:
        validator = Draft202012Validator(event_schema)
        for event in core.ledger.events():
            for error in validator.iter_errors(event):
                event_errors.append(
                    {
                        "event_id": event.get("event_id"),
                        "path": "/".join(str(part) for part in error.path),
                        "message": error.message,
                    }
                )
    return {
        "files": schema_results,
        "event_count": len(core.ledger.events()),
        "event_errors": event_errors,
        "conforms": bool(schema_results) and not event_errors,
    }


def validate_core(core: CaeluviimCore) -> dict[str, Any]:
    ledger = core.ledger.verify()
    shacl = GraphProjector(core).validate_shacl()
    dap = validate_dap_compatibility(core.project_root)
    vocabularies = validate_vocabularies(core.project_root)
    schemas = validate_schemas(core)
    conforms = (
        shacl["conforms"]
        and dap["python_conforms"]
        and dap["typescript_oracle_conforms"]
        and vocabularies["conforms"]
        and schemas["conforms"]
    )
    return {
        "conforms": conforms,
        "ledger": ledger,
        "shacl": shacl,
        "dap_compatibility": dap,
        "vocabularies": vocabularies,
        "schemas": schemas,
    }
