from __future__ import annotations

import base64
import binascii
import gzip
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

ALLOWED_LABELS = frozenset(
    {
        "Claim",
        "Evidence",
        "Assessment",
        "Prediction",
        "Agent",
        "Institution",
        "VetoEvent",
        "Authority",
        "Provenance",
        "Project",
        "Task",
        "Decision",
        "Artifact",
        "LanguageAnchor",
        "Rule",
        "Schema",
        "Dataset",
        "Projection",
        "ValidationResult",
        "Source",
        "Event",
        "Utterance",
        "SourceSpan",
        "Quotation",
        "Interpretation",
        "Proposition",
        "TruthAssessment",
        "ContextSnapshot",
        "EvidenceSet",
        "AssessmentStandard",
        "JurisdictionOrDomain",
        "CanonicalOperation",
        "OperationDefinitionOccurrence",
        "TransformationEvent",
        "ContestationEvent",
        "RepairEvent",
        "CorrectionEvent",
        "ForceAssignment",
        "OperationOccurrence",
        "PresuppositionAssertion",
        "EntailmentAssertion",
        "ImplicatureAssertion",
        "Frame",
        "FrameAssignment",
        "ConceptualDomain",
        "ConceptualMapping",
        "Turn",
        "TurnConstructionUnit",
        "ReferringExpression",
        "CoreferenceAssertion",
        "AdjacencyPair",
        "SocialIndexicalityAssertion",
    }
)

ALLOWED_RELATIONSHIP_TYPES = frozenset(
    {
        "SUPPORTS",
        "EXTENDS",
        "CONFLICTS_WITH",
        "EVIDENCED_BY",
        "ASSESSES",
        "PREDICTS",
        "ISSUED_BY",
        "GOVERNED_BY",
        "HAS_PROVENANCE",
        "DERIVED_FROM",
        "REVISES",
        "SUPERSEDES",
        "VALIDATED_BY",
        "CONTESTED_BY",
        "TARGETS",
        "PARTICIPATES_IN",
        "PART_OF",
        "DEPENDS_ON",
        "ASSIGNED_TO",
        "IMPLEMENTS",
        "PROJECTS_TO",
        "HAS_ANCHOR",
        "ANALOG_OF",
        "ORIGINATED",
        "MATERIALIZED",
        "PARTICIPATED_IN",
        "AUTHORIZED",
        "HAS_SOURCE_SPAN",
        "SPAN_OF",
        "QUOTED_FROM",
        "TRANSFORMED_BY",
        "USED_CONTEXT",
        "ASSESSES_PROPOSITION",
        "USED_EVIDENCE_SET",
        "EVALUATED_UNDER_STANDARD",
        "EVALUATED_WITHIN_DOMAIN",
        "HAS_REASON",
        "HAS_ALTERNATIVE",
        "ASSIGNED_FORCE",
        "PRESUPPOSES",
        "ENTAILS",
        "IMPLICATES",
        "EVOKES_FRAME",
        "HAS_SOURCE_DOMAIN",
        "HAS_TARGET_DOMAIN",
        "COREFERS_WITH",
        "HAS_FIRST_PAIR_PART",
        "HAS_SECOND_PAIR_PART",
        "REPAIRS_TROUBLE_SOURCE",
        "INDEXES_SOCIAL_MEANING",
        "DEFINES_OPERATION",
        "DETECTED_OPERATION",
        "TARGETS_ENTITY",
        "CONTRASTS_WITH",
        "REVISES_CONCEPT",
    }
)

RESERVED_PROPERTIES = frozenset(
    {
        "id",
        "record_hash",
        "content_hash",
        "created_at",
        "updated_at",
        "ingest_id",
        "source_id",
        "manifest_hash",
        "assertion_id",
    }
)

_IDENTIFIER = re.compile(r"^[A-Z][A-Z0-9_]*$")


class ManifestValidationError(ValueError):
    """Raised when an ingestion manifest violates structural or graph invariants."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("Manifest validation failed:\n- " + "\n- ".join(errors))


class ManifestEncodingError(ValueError):
    """Raised when a manifest file cannot be decoded into JSON."""


def canonical_json(value: Any) -> str:
    """Return deterministic JSON suitable for hashing and audit comparison."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_record(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_manifest(path: str | Path) -> dict[str, Any]:
    """Load plain JSON or deterministic base64-encoded gzip JSON manifests."""

    manifest_path = Path(path)
    try:
        encoded_text = manifest_path.read_text(encoding="utf-8")
        if manifest_path.name.endswith(".json.gz.b64"):
            encoded_text = "".join(encoded_text.split())
            compressed = base64.b64decode(encoded_text, validate=True)
            decoded_text = gzip.decompress(compressed).decode("utf-8")
            return json.loads(decoded_text)
        return json.loads(encoded_text)
    except (
        OSError,
        binascii.Error,
        EOFError,
        gzip.BadGzipFile,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise ManifestEncodingError(
            f"Unable to decode manifest {manifest_path}: {exc}"
        ) from exc


def load_schema(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_manifest(
    manifest: Mapping[str, Any], schema: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate JSON structure plus graph-level reference and append-only invariants."""

    candidate = deepcopy(dict(manifest))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(
            validator.iter_errors(candidate), key=lambda item: list(item.absolute_path)
        )
    ]

    if errors:
        raise ManifestValidationError(errors)

    node_ids = [node["id"] for node in candidate["nodes"]]
    relationship_ids = [relationship["id"] for relationship in candidate["relationships"]]
    source_id = candidate["source"]["source_id"]
    ingest_id = candidate["ingest_id"]

    _append_duplicate_errors(errors, "node", node_ids)
    _append_duplicate_errors(errors, "relationship", relationship_ids)

    all_entity_ids = node_ids + relationship_ids + [source_id, ingest_id]
    _append_duplicate_errors(errors, "entity", all_entity_ids)

    node_id_set = set(node_ids)
    for relationship in candidate["relationships"]:
        if relationship["from"] not in node_id_set:
            errors.append(
                f"relationship {relationship['id']} references missing from node {relationship['from']}"
            )
        if relationship["to"] not in node_id_set:
            errors.append(
                f"relationship {relationship['id']} references missing to node {relationship['to']}"
            )

    for node in candidate["nodes"]:
        invalid = sorted(set(node.get("properties", {})).intersection(RESERVED_PROPERTIES))
        if invalid:
            errors.append(f"node {node['id']} uses reserved properties: {', '.join(invalid)}")
        for label in node["labels"]:
            if label not in ALLOWED_LABELS:
                errors.append(f"node {node['id']} uses unsupported label {label}")

    for relationship in candidate["relationships"]:
        invalid = sorted(
            set(relationship.get("properties", {})).intersection(RESERVED_PROPERTIES)
        )
        if invalid:
            errors.append(
                f"relationship {relationship['id']} uses reserved properties: {', '.join(invalid)}"
            )
        relationship_type = relationship["type"]
        if relationship_type not in ALLOWED_RELATIONSHIP_TYPES:
            errors.append(
                f"relationship {relationship['id']} uses unsupported type {relationship_type}"
            )
        if not _IDENTIFIER.fullmatch(relationship_type):
            errors.append(
                f"relationship {relationship['id']} has unsafe relationship identifier {relationship_type}"
            )

    if errors:
        raise ManifestValidationError(errors)

    return candidate


def _append_duplicate_errors(errors: list[str], kind: str, identifiers: list[str]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for identifier in identifiers:
        if identifier in seen:
            duplicates.add(identifier)
        seen.add(identifier)
    if duplicates:
        errors.append(f"duplicate {kind} identifiers: {', '.join(sorted(duplicates))}")


def safe_label_clause(labels: list[str]) -> str:
    invalid = [label for label in labels if label not in ALLOWED_LABELS]
    if invalid:
        raise ValueError(f"Unsupported labels: {', '.join(invalid)}")
    return ":".join(["Entity", *labels])


def safe_relationship_type(relationship_type: str) -> str:
    if relationship_type not in ALLOWED_RELATIONSHIP_TYPES:
        raise ValueError(f"Unsupported relationship type: {relationship_type}")
    if not _IDENTIFIER.fullmatch(relationship_type):
        raise ValueError(f"Unsafe relationship type: {relationship_type}")
    return relationship_type
