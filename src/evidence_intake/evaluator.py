from __future__ import annotations

import copy
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from pyshacl import validate as shacl_validate
from rdflib import Graph, Namespace, RDF, URIRef

from .canonical import sha256_bytes, sha256_json

INTAKE = Namespace("https://caeluviim.org/ontology/evidence-intake#")

ASSESSMENT_SCHEMA = (
    "https://caeluviim.org/schema/evidence-intake-assessment.schema.json"
)
SEMANTICS_VERSION = "evidence-intake/0.1.0"

ENTITY_COLLECTIONS = {
    "source_artifacts": ("artifact_id", "SourceArtifact"),
    "source_snapshots": ("snapshot_id", "SourceSnapshot"),
    "source_locators": ("locator_id", "SourceLocator"),
    "material_claim_segments": ("segment_id", "MaterialClaimSegment"),
    "extracted_claims": ("claim_id", "ExtractedClaim"),
    "claim_spans": ("span_id", "ClaimSpan"),
    "support_relations": ("support_id", "SupportRelation"),
    "contradiction_relations": (
        "contradiction_id",
        "ContradictionRelation",
    ),
    "source_authority_assessments": (
        "assessment_id",
        "SourceAuthorityAssessment",
    ),
    "evidence_bundles": ("bundle_id", "EvidenceBundle"),
    "unsupported_claims": ("unsupported_id", "UnsupportedClaim"),
    "quarantine_records": ("quarantine_id", "QuarantineRecord"),
    "release_decisions": ("decision_id", "ReleaseDecision"),
    "sicrp_assertion_requests": ("request_id", "SICRPAssertionRequest"),
}

UNVERIFIABLE_CODES = {
    "ACQUISITION_RECORD_MISSING",
    "ACQUISITION_RECORD_DIGEST_MISMATCH",
    "ACQUISITION_ASSESSMENT_DIGEST_MISMATCH",
    "ACQUISITION_REFERENCE_MISMATCH",
    "ACQUISITION_FIXATION_MISMATCH",
    "ACQUISITION_AUTHORITY_BOUNDARY_FAILED",
    "SNAPSHOT_NOT_ACQUISITION_ELIGIBLE",
    "REFERENCE_INTEGRITY_FAILED",
    "SNAPSHOT_MISSING",
    "SNAPSHOT_PATH_INVALID",
    "SNAPSHOT_NOT_IMMUTABLE",
    "SNAPSHOT_DIGEST_MISMATCH",
    "SNAPSHOT_LENGTH_MISMATCH",
    "LOCATOR_MISSING",
    "LOCATOR_UNSTABLE",
    "LOCATOR_RANGE_INVALID",
    "QUOTE_SNAPSHOT_MISMATCH",
    "QUOTE_DIGEST_MISMATCH",
    "CLAIM_TRACE_MISSING",
    "CLAIM_TEXT_NOT_TRACEABLE",
    "SPAN_DIGEST_MISMATCH",
    "GENERATED_TEXT_AS_EXTERNAL_SOURCE",
}


class EvaluationError(RuntimeError):
    pass


def load_json(path: Path | str) -> dict[str, Any]:
    try:
        return json.loads(Path(path).read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvaluationError(f"cannot load JSON from {path}: {error}") from error


def _schema_errors(
    document: dict[str, Any], schema: dict[str, Any]
) -> list[dict[str, Any]]:
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    return [
        {
            "path": "/" + "/".join(str(part) for part in error.absolute_path),
            "message": error.message,
            "validator": error.validator,
        }
        for error in sorted(
            validator.iter_errors(document),
            key=lambda item: (list(item.absolute_path), item.message),
        )
    ]


def validate_json_document(
    document: dict[str, Any], schema: dict[str, Any]
) -> dict[str, Any]:
    errors = _schema_errors(document, schema)
    return {"conforms": not errors, "errors": errors}


def validate_rdf_manifest(
    rdf_path: Path | str,
    *,
    shapes_path: Path | str,
    ontology_path: Path | str,
) -> dict[str, Any]:
    data = Graph().parse(str(rdf_path), format="turtle")
    shapes = Graph().parse(str(shapes_path), format="turtle")
    ontology = Graph().parse(str(ontology_path), format="turtle")
    conforms, _, report = shacl_validate(
        data_graph=data,
        shacl_graph=shapes,
        ont_graph=ontology,
        inference="rdfs",
        advanced=True,
    )
    return {
        "conforms": bool(conforms),
        "rdf_triples": len(data),
        "report_text": str(report),
    }


def verify_cross_format_alignment(
    manifest: dict[str, Any], rdf_path: Path | str
) -> dict[str, Any]:
    graph = Graph().parse(str(rdf_path), format="turtle")
    missing: list[dict[str, str]] = []
    manifest_ref = URIRef(manifest["manifest_id"])
    if (manifest_ref, RDF.type, INTAKE.IntakeManifest) not in graph:
        missing.append(
            {
                "json_ref": str(manifest_ref),
                "expected_rdf_type": str(INTAKE.IntakeManifest),
            }
        )
    for collection, (field, class_name) in ENTITY_COLLECTIONS.items():
        for item in manifest.get(collection, []):
            identifier = item[field]
            expected = INTAKE[class_name]
            if (URIRef(identifier), RDF.type, expected) not in graph:
                missing.append(
                    {
                        "json_ref": identifier,
                        "expected_rdf_type": str(expected),
                    }
                )

    state_mismatches = []
    for claim in manifest.get("extracted_claims", []):
        claim_ref = URIRef(claim["claim_id"])
        expected_state = INTAKE[claim["claim_state"]]
        actual_states = set(graph.objects(claim_ref, INTAKE.claimState))
        if expected_state not in actual_states:
            state_mismatches.append(
                {
                    "claim_ref": str(claim_ref),
                    "expected_state": str(expected_state),
                    "actual_states": sorted(str(item) for item in actual_states),
                }
            )
    return {
        "conforms": not missing and not state_mismatches,
        "rdf_triples": len(graph),
        "missing_typed_entities": missing,
        "claim_state_mismatches": state_mismatches,
    }


def _indexes(
    manifest: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    index: dict[str, dict[str, Any]] = {}
    duplicate_locations: dict[str, list[str]] = defaultdict(list)
    for collection, (field, _) in ENTITY_COLLECTIONS.items():
        for item in manifest.get(collection, []):
            identifier = item[field]
            duplicate_locations[identifier].append(collection)
            index.setdefault(identifier, item)
    duplicates = {
        identifier: locations
        for identifier, locations in duplicate_locations.items()
        if len(locations) > 1
    }
    return index, duplicates


def _claim_ref_for_entity(
    item: dict[str, Any], collection: str
) -> str | None:
    fields = {
        "material_claim_segments": "claim_ref",
        "claim_spans": "claim_ref",
        "support_relations": "claim_ref",
        "contradiction_relations": "claim_ref",
        "evidence_bundles": "claim_ref",
        "unsupported_claims": "claim_ref",
        "quarantine_records": "claim_ref",
        "release_decisions": "claim_ref",
        "sicrp_assertion_requests": "claim_ref",
    }
    field = fields.get(collection)
    return item.get(field) if field else None


def _reference_failures(
    manifest: dict[str, Any],
) -> tuple[dict[str, list[tuple[str, list[str], str]]], bool]:
    index, duplicates = _indexes(manifest)
    claims = {
        item["claim_id"] for item in manifest.get("extracted_claims", [])
    }
    by_claim: dict[str, list[tuple[str, list[str], str]]] = defaultdict(list)
    global_messages: list[str] = []

    for identifier, locations in sorted(duplicates.items()):
        global_messages.append(
            f"duplicate identifier {identifier} in {', '.join(locations)}"
        )

    def require(
        claim_ref: str | None,
        owner_ref: str,
        referenced: Iterable[str],
        expected_collection: str,
    ) -> None:
        expected_field = ENTITY_COLLECTIONS[expected_collection][0]
        expected_ids = {
            item[expected_field]
            for item in manifest.get(expected_collection, [])
        }
        for reference in referenced:
            if reference not in expected_ids:
                message = (
                    f"{owner_ref} references missing {expected_collection} "
                    f"entity {reference}"
                )
                if claim_ref in claims:
                    by_claim[claim_ref].append(
                        (
                            "REFERENCE_INTEGRITY_FAILED",
                            [owner_ref, reference],
                            message,
                        )
                    )
                else:
                    global_messages.append(message)

    rules: dict[str, list[tuple[str, str]]] = {
        "source_snapshots": [("artifact_ref", "source_artifacts")],
        "source_locators": [("snapshot_ref", "source_snapshots")],
        "material_claim_segments": [("claim_ref", "extracted_claims")],
        "claim_spans": [
            ("claim_ref", "extracted_claims"),
            ("segment_ref", "material_claim_segments"),
            ("locator_ref", "source_locators"),
        ],
        "support_relations": [
            ("claim_ref", "extracted_claims"),
            ("locator_ref", "source_locators"),
            ("claim_span_refs", "claim_spans"),
            ("supported_segment_refs", "material_claim_segments"),
        ],
        "contradiction_relations": [
            ("claim_ref", "extracted_claims"),
            ("locator_ref", "source_locators"),
            ("contradicted_segment_refs", "material_claim_segments"),
        ],
        "source_authority_assessments": [
            ("artifact_ref", "source_artifacts")
        ],
        "evidence_bundles": [
            ("claim_ref", "extracted_claims"),
            ("support_relation_refs", "support_relations"),
            ("contradiction_relation_refs", "contradiction_relations"),
            (
                "authority_assessment_refs",
                "source_authority_assessments",
            ),
        ],
        "unsupported_claims": [
            ("claim_ref", "extracted_claims"),
            ("unsupported_segment_refs", "material_claim_segments"),
        ],
        "quarantine_records": [("claim_ref", "extracted_claims")],
        "release_decisions": [
            ("claim_ref", "extracted_claims"),
            ("basis_support_relation_refs", "support_relations"),
            (
                "disclosed_contradiction_refs",
                "contradiction_relations",
            ),
        ],
        "sicrp_assertion_requests": [("claim_ref", "extracted_claims")],
    }

    for collection, collection_rules in rules.items():
        identifier_field = ENTITY_COLLECTIONS[collection][0]
        for item in manifest.get(collection, []):
            owner_ref = item[identifier_field]
            claim_ref = _claim_ref_for_entity(item, collection)
            for field, expected_collection in collection_rules:
                value = item.get(field, [])
                values = [value] if isinstance(value, str) else value
                require(
                    claim_ref,
                    owner_ref,
                    values,
                    expected_collection,
                )

    for claim in manifest.get("extracted_claims", []):
        claim_ref = claim["claim_id"]
        require(
            claim_ref,
            claim_ref,
            claim["material_segment_refs"],
            "material_claim_segments",
        )
        require(
            claim_ref,
            claim_ref,
            claim["claim_span_refs"],
            "claim_spans",
        )
        require(
            claim_ref,
            claim_ref,
            [claim["evidence_bundle_ref"]],
            "evidence_bundles",
        )

    if global_messages:
        for claim_ref in claims:
            for message in global_messages:
                by_claim[claim_ref].append(
                    (
                        "REFERENCE_INTEGRITY_FAILED",
                        [],
                        message,
                    )
                )
    return by_claim, not global_messages and not any(by_claim.values())


def _acquisition_record_failures(
    manifest: dict[str, Any],
    *,
    project_root: Path,
) -> dict[str, list[tuple[str, list[str], str]]]:
    failures: dict[
        str, list[tuple[str, list[str], str]]
    ] = defaultdict(list)
    snapshots = manifest.get("source_snapshots", [])
    record = manifest.get("acquisition_record")
    snapshot_refs = [item["snapshot_id"] for item in snapshots]

    def fail_all(code: str, message: str) -> None:
        for snapshot_ref in snapshot_refs:
            failures[snapshot_ref].append(
                (code, [snapshot_ref], message)
            )

    if not record:
        fail_all(
            "ACQUISITION_RECORD_MISSING",
            "Intake requires an immutable acquisition record.",
        )
        return failures

    loaded: dict[str, dict[str, Any]] = {}
    for label, path_field, digest_field, mismatch_code in (
        (
            "manifest",
            "acquisition_manifest_path",
            "acquisition_manifest_sha256",
            "ACQUISITION_RECORD_DIGEST_MISMATCH",
        ),
        (
            "assessment",
            "acquisition_assessment_path",
            "acquisition_assessment_sha256",
            "ACQUISITION_ASSESSMENT_DIGEST_MISMATCH",
        ),
    ):
        candidate = project_root / record[path_field]
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(project_root)
            if candidate.is_symlink() or not resolved.is_file():
                raise OSError("not a regular non-symlink file")
            content = resolved.read_bytes()
            if sha256_bytes(content) != record[digest_field]:
                fail_all(
                    mismatch_code,
                    f"Immutable acquisition {label} digest does not verify.",
                )
            value = json.loads(content.decode("utf-8"))
            if not isinstance(value, dict):
                raise ValueError("record is not a JSON object")
            loaded[label] = value
        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
            fail_all(
                "ACQUISITION_RECORD_MISSING",
                f"Immutable acquisition {label} is unavailable or invalid.",
            )

    acquisition = loaded.get("manifest")
    assessment = loaded.get("assessment")
    if acquisition is None or assessment is None:
        return failures
    if acquisition.get("manifest_id") != record["acquisition_manifest_ref"]:
        fail_all(
            "ACQUISITION_REFERENCE_MISMATCH",
            "Acquisition manifest identifier does not match the intake reference.",
        )
    if assessment.get("assessment_id") != record[
        "acquisition_assessment_ref"
    ]:
        fail_all(
            "ACQUISITION_REFERENCE_MISMATCH",
            "Acquisition assessment identifier does not match the intake reference.",
        )
    if assessment.get("manifest_ref") != acquisition.get("manifest_id"):
        fail_all(
            "ACQUISITION_REFERENCE_MISMATCH",
            "Acquisition assessment does not bind the referenced manifest.",
        )
    if assessment.get("manifest_digest") != sha256_json(acquisition):
        fail_all(
            "ACQUISITION_REFERENCE_MISMATCH",
            "Acquisition assessment manifest digest does not verify.",
        )
    assessment_source = copy.deepcopy(assessment)
    assessment_source.pop("assessment_id", None)
    recorded_assessment_digest = assessment_source.pop(
        "assessment_digest", None
    )
    if (
        recorded_assessment_digest != sha256_json(assessment_source)
        or not str(assessment.get("assessment_id", "")).endswith(
            ":" + str(recorded_assessment_digest)
        )
    ):
        fail_all(
            "ACQUISITION_REFERENCE_MISMATCH",
            "Acquisition assessment content address does not verify.",
        )
    boundary = acquisition.get("authority_boundary", {})
    if (
        any(boundary.values())
        or assessment.get("authority_boundary_preserved") is not True
    ):
        fail_all(
            "ACQUISITION_AUTHORITY_BOUNDARY_FAILED",
            "Acquisition must not assess source authority, claim support, or truth.",
        )

    fixations_by_id = {
        item.get("fixation_id"): item
        for item in acquisition.get("snapshot_fixations", [])
    }
    eligible = set(assessment.get("eligible_snapshot_refs", []))
    for snapshot in snapshots:
        snapshot_ref = snapshot["snapshot_id"]
        fixation_ref = snapshot["acquisition_fixation_ref"]
        fixation = fixations_by_id.get(fixation_ref)
        if snapshot_ref not in eligible:
            failures[snapshot_ref].append(
                (
                    "SNAPSHOT_NOT_ACQUISITION_ELIGIBLE",
                    [snapshot_ref, fixation_ref],
                    "The acquisition assessment did not mark this snapshot intake-eligible.",
                )
            )
        if (
            fixation is None
            or fixation.get("snapshot_id") != snapshot_ref
            or fixation.get("content_path") != snapshot["content_path"]
            or fixation.get("sha256") != snapshot["sha256"]
            or fixation.get("byte_length") != snapshot["byte_length"]
            or fixation.get("immutable") is not True
        ):
            failures[snapshot_ref].append(
                (
                    "ACQUISITION_FIXATION_MISMATCH",
                    [snapshot_ref, fixation_ref],
                    "Intake snapshot does not exactly match its acquisition fixation.",
                )
            )
    return failures


def _snapshot_and_locator_failures(
    manifest: dict[str, Any],
    *,
    project_root: Path,
) -> tuple[
    dict[str, list[tuple[str, list[str], str]]],
    dict[str, list[tuple[str, list[str], str]]],
    dict[str, bytes],
]:
    snapshot_failures: dict[
        str, list[tuple[str, list[str], str]]
    ] = defaultdict(list)
    locator_failures: dict[
        str, list[tuple[str, list[str], str]]
    ] = defaultdict(list)
    snapshot_bytes: dict[str, bytes] = {}
    snapshots = {
        item["snapshot_id"]: item
        for item in manifest.get("source_snapshots", [])
    }
    root = project_root.resolve()
    acquisition_failures = _acquisition_record_failures(
        manifest,
        project_root=root,
    )
    for snapshot_ref, items in acquisition_failures.items():
        snapshot_failures[snapshot_ref].extend(items)

    for snapshot_ref, snapshot in snapshots.items():
        if not snapshot["immutable"]:
            snapshot_failures[snapshot_ref].append(
                (
                    "SNAPSHOT_NOT_IMMUTABLE",
                    [snapshot_ref],
                    "The source snapshot is not marked immutable.",
                )
            )
        candidate = (root / snapshot["content_path"]).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            snapshot_failures[snapshot_ref].append(
                (
                    "SNAPSHOT_PATH_INVALID",
                    [snapshot_ref],
                    "The snapshot path escapes the project root.",
                )
            )
            continue
        if not candidate.is_file() or candidate.is_symlink():
            snapshot_failures[snapshot_ref].append(
                (
                    "SNAPSHOT_MISSING",
                    [snapshot_ref],
                    "The immutable snapshot file is missing or not a regular file.",
                )
            )
            continue
        content = candidate.read_bytes()
        snapshot_bytes[snapshot_ref] = content
        if len(content) != snapshot["byte_length"]:
            snapshot_failures[snapshot_ref].append(
                (
                    "SNAPSHOT_LENGTH_MISMATCH",
                    [snapshot_ref],
                    "The captured byte length no longer matches the snapshot.",
                )
            )
        if sha256_bytes(content) != snapshot["sha256"]:
            snapshot_failures[snapshot_ref].append(
                (
                    "SNAPSHOT_DIGEST_MISMATCH",
                    [snapshot_ref],
                    "The source content changed after intake.",
                )
            )

    for locator in manifest.get("source_locators", []):
        locator_ref = locator["locator_id"]
        snapshot_ref = locator["snapshot_ref"]
        if not locator["snapshot_bound"] or not locator["exact"]:
            locator_failures[locator_ref].append(
                (
                    "LOCATOR_UNSTABLE",
                    [locator_ref, snapshot_ref],
                    "The locator is not exact and snapshot-bound.",
                )
            )
        content = snapshot_bytes.get(snapshot_ref)
        if content is None:
            locator_failures[locator_ref].append(
                (
                    "LOCATOR_MISSING",
                    [locator_ref, snapshot_ref],
                    "The locator cannot resolve an available snapshot.",
                )
            )
            continue
        start = locator["byte_start"]
        end = locator["byte_end"]
        if start < 0 or end <= start or end > len(content):
            locator_failures[locator_ref].append(
                (
                    "LOCATOR_RANGE_INVALID",
                    [locator_ref, snapshot_ref],
                    "The UTF-8 byte range is outside the captured snapshot.",
                )
            )
            continue
        quoted_bytes = content[start:end]
        try:
            quoted_text = quoted_bytes.decode("utf-8")
        except UnicodeDecodeError:
            quoted_text = ""
        if quoted_text != locator["quoted_text"]:
            locator_failures[locator_ref].append(
                (
                    "QUOTE_SNAPSHOT_MISMATCH",
                    [locator_ref, snapshot_ref],
                    "Quoted text differs from the captured snapshot range.",
                )
            )
        if sha256_bytes(quoted_bytes) != locator["quote_sha256"]:
            locator_failures[locator_ref].append(
                (
                    "QUOTE_DIGEST_MISMATCH",
                    [locator_ref, snapshot_ref],
                    "The quote digest does not verify against captured bytes.",
                )
            )
    return snapshot_failures, locator_failures, snapshot_bytes


def _claim_failures(
    manifest: dict[str, Any],
    *,
    project_root: Path,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    bool,
]:
    reference_failures, reference_integrity = _reference_failures(manifest)
    (
        snapshot_failures,
        locator_failures,
        _,
    ) = _snapshot_and_locator_failures(
        manifest,
        project_root=project_root,
    )

    artifacts = {
        item["artifact_id"]: item
        for item in manifest.get("source_artifacts", [])
    }
    snapshots = {
        item["snapshot_id"]: item
        for item in manifest.get("source_snapshots", [])
    }
    locators = {
        item["locator_id"]: item
        for item in manifest.get("source_locators", [])
    }
    segments = {
        item["segment_id"]: item
        for item in manifest.get("material_claim_segments", [])
    }
    spans = {
        item["span_id"]: item for item in manifest.get("claim_spans", [])
    }
    supports = {
        item["support_id"]: item
        for item in manifest.get("support_relations", [])
    }
    contradictions = {
        item["contradiction_id"]: item
        for item in manifest.get("contradiction_relations", [])
    }
    bundles = {
        item["bundle_id"]: item
        for item in manifest.get("evidence_bundles", [])
    }
    decisions_by_claim: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in manifest.get("release_decisions", []):
        decisions_by_claim[item["claim_ref"]].append(item)
    quarantines_by_claim: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in manifest.get("quarantine_records", []):
        quarantines_by_claim[item["claim_ref"]].append(item)
    requests_by_claim: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in manifest.get("sicrp_assertion_requests", []):
        requests_by_claim[item["claim_ref"]].append(item)
    contradictions_by_claim: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in contradictions.values():
        contradictions_by_claim[item["claim_ref"]].append(item)

    claim_results: list[dict[str, Any]] = []
    failure_facts: list[dict[str, Any]] = []

    for claim in sorted(
        manifest["extracted_claims"],
        key=lambda item: item["claim_id"],
    ):
        claim_ref = claim["claim_id"]
        failures: list[tuple[str, list[str], str]] = list(
            reference_failures.get(claim_ref, [])
        )
        material_refs = set(claim["material_segment_refs"])
        covered: set[str] = set()
        bundle = bundles.get(claim["evidence_bundle_ref"])
        bundle_support_refs = set(
            bundle.get("support_relation_refs", []) if bundle else []
        )
        claim_supports = [
            item
            for item in supports.values()
            if item["claim_ref"] == claim_ref
            and item["support_id"] in bundle_support_refs
        ]
        claim_contradictions = contradictions_by_claim.get(claim_ref, [])

        if bundle is None or bundle.get("claim_ref") != claim_ref:
            failures.append(
                (
                    "EVIDENCE_BUNDLE_MISSING",
                    [claim["evidence_bundle_ref"]],
                    "The claim lacks its claim-bound evidence bundle.",
                )
            )
        if not claim_supports:
            if bundle and bundle.get("authority_assessment_refs"):
                failures.append(
                    (
                        "AUTHORITY_SUBSTITUTED_FOR_SUPPORT",
                        list(bundle["authority_assessment_refs"]),
                        "A source authority assessment cannot replace evidentiary support.",
                    )
                )
            failures.append(
                (
                    "SUPPORT_RELATION_MISSING",
                    [claim_ref],
                    "No explicit supporting relation is available for the claim.",
                )
            )

        span_refs = set(claim["claim_span_refs"])
        for span_ref in span_refs:
            span = spans.get(span_ref)
            if span is None or span.get("claim_ref") != claim_ref:
                failures.append(
                    (
                        "CLAIM_TRACE_MISSING",
                        [span_ref],
                        "A declared claim span is missing or belongs to another claim.",
                    )
                )
                continue
            locator = locators.get(span["locator_ref"])
            if locator is None:
                failures.append(
                    (
                        "CLAIM_TRACE_MISSING",
                        [span_ref, span["locator_ref"]],
                        "A claim span has no resolvable exact source locator.",
                    )
                )
                continue
            if (
                span["extracted_text"] != locator["quoted_text"]
                or span["segment_ref"] not in material_refs
            ):
                failures.append(
                    (
                        "CLAIM_TEXT_NOT_TRACEABLE",
                        [span_ref, span["locator_ref"]],
                        "Normalized claim material is not traceable through its declared span.",
                    )
                )
            if (
                sha256_bytes(span["extracted_text"].encode("utf-8"))
                != span["extracted_text_sha256"]
            ):
                failures.append(
                    (
                        "SPAN_DIGEST_MISMATCH",
                        [span_ref],
                        "The extracted claim span digest does not verify.",
                    )
                )

        used_locator_refs: set[str] = set()
        for relation in claim_supports:
            relation_ref = relation["support_id"]
            locator_ref = relation["locator_ref"]
            used_locator_refs.add(locator_ref)
            locator = locators.get(locator_ref)
            if relation["support_verdict"] == "does_not_support":
                failures.append(
                    (
                        "CITATION_DOES_NOT_SUPPORT_CLAIM",
                        [relation_ref, locator_ref],
                        "A cited source locator is explicitly assessed as not supporting the claim.",
                    )
                )
                continue
            if relation["support_verdict"] == "partially_supports":
                failures.append(
                    (
                        "CITATION_PARTIAL_SUPPORT",
                        [relation_ref, locator_ref],
                        "A cited source covers only part of the stated support relation.",
                    )
                )
                continue
            if claim["claim_mode"] == "observation" and relation[
                "support_mode"
            ] != "direct":
                failures.append(
                    (
                        "UNSUPPORTED_INFERENCE_AS_OBSERVATION",
                        [relation_ref, claim_ref],
                        "Inferential support is presented as direct observation.",
                    )
                )
            if locator is None:
                failures.append(
                    (
                        "LOCATOR_MISSING",
                        [relation_ref, locator_ref],
                        "The support relation has no exact source locator.",
                    )
                )
                continue
            if claim_ref not in locator["support_scope_claim_refs"]:
                failures.append(
                    (
                        "SUPPORT_SCOPE_EXCEEDED",
                        [relation_ref, locator_ref],
                        "Evidence was reused beyond its stated claim support scope.",
                    )
                )
            snapshot_ref = locator["snapshot_ref"]
            for failure in snapshot_failures.get(snapshot_ref, []):
                failures.append(failure)
            for failure in locator_failures.get(locator_ref, []):
                failures.append(failure)
            snapshot = snapshots.get(snapshot_ref)
            artifact = (
                artifacts.get(snapshot["artifact_ref"]) if snapshot else None
            )
            if (
                artifact
                and artifact["generated_content"]
                and artifact["source_class"] != "generated_output"
            ):
                failures.append(
                    (
                        "GENERATED_TEXT_AS_EXTERNAL_SOURCE",
                        [artifact["artifact_id"], relation_ref],
                        "Generated text is classified as an external source.",
                    )
                )
            relation_span_refs = set(relation["claim_span_refs"])
            if not relation_span_refs or not relation_span_refs <= span_refs:
                failures.append(
                    (
                        "CLAIM_TRACE_MISSING",
                        [relation_ref, *sorted(relation_span_refs)],
                        "A support relation is not bound to this claim's exact spans.",
                    )
                )
            valid_segments = set(relation["supported_segment_refs"])
            if not valid_segments <= material_refs:
                failures.append(
                    (
                        "SUPPORT_SCOPE_EXCEEDED",
                        [relation_ref, *sorted(valid_segments - material_refs)],
                        "A support relation claims segments outside the material claim.",
                    )
                )
            elif not locator_failures.get(locator_ref) and not snapshot_failures.get(
                snapshot_ref
            ):
                covered.update(valid_segments)

        uncovered = material_refs - covered
        if uncovered:
            code = (
                "PARTIAL_COMPOUND_SUPPORT"
                if covered
                else "COMPLETE_SUPPORT_MISSING"
            )
            failures.append(
                (
                    code,
                    sorted(uncovered),
                    "Every material claim segment must have valid explicit support.",
                )
            )

        bundle_contradiction_refs = set(
            bundle.get("contradiction_relation_refs", []) if bundle else []
        )
        all_contradiction_refs = {
            item["contradiction_id"] for item in claim_contradictions
        }
        if (
            not bundle
            or not bundle.get("contradiction_search_completed")
            or bundle_contradiction_refs != all_contradiction_refs
        ):
            failures.append(
                (
                    "CONTRADICTORY_EVIDENCE_OMITTED",
                    sorted(all_contradiction_refs - bundle_contradiction_refs),
                    "Contradictory evidence within the intake scope is not completely disclosed.",
                )
            )
        unresolved_refs = []
        for contradiction in claim_contradictions:
            contradiction_ref = contradiction["contradiction_id"]
            locator_ref = contradiction["locator_ref"]
            if not contradiction["disclosed"]:
                failures.append(
                    (
                        "CONTRADICTORY_EVIDENCE_OMITTED",
                        [contradiction_ref],
                        "A recorded contradiction is not disclosed.",
                    )
                )
            if contradiction["resolution_status"] == "unresolved":
                unresolved_refs.append(contradiction_ref)
            for failure in locator_failures.get(locator_ref, []):
                failures.append(failure)
        if unresolved_refs:
            failures.append(
                (
                    "UNRESOLVED_CONTRADICTION",
                    sorted(unresolved_refs),
                    "Material contradictory evidence remains unresolved.",
                )
            )

        if bundle:
            if not bundle["declared_complete_support"] and not uncovered:
                failures.append(
                    (
                        "COMPLETE_SUPPORT_NOT_DECLARED",
                        [bundle["bundle_id"]],
                        "Complete support was not declared by the evidence bundle.",
                    )
                )
            if not bundle["content_digests_verified"]:
                failures.append(
                    (
                        "CONTENT_DIGEST_ATTESTATION_MISSING",
                        [bundle["bundle_id"]],
                        "The evidence bundle does not attest verified content digests.",
                    )
                )

        decisions = decisions_by_claim.get(claim_ref, [])
        release_decision = decisions[0] if len(decisions) == 1 else None
        if release_decision is None:
            failures.append(
                (
                    "RELEASE_AUTHORITY_MISSING",
                    [item["decision_id"] for item in decisions],
                    "Exactly one release decision with authority must be recorded.",
                )
            )
        else:
            if release_decision["decision"] != "approved":
                failures.append(
                    (
                        "RELEASE_DECISION_DENIED",
                        [release_decision["decision_id"]],
                        "The recorded release authority denied release.",
                    )
                )
            if not release_decision["release_authority_ref"]:
                failures.append(
                    (
                        "RELEASE_AUTHORITY_MISSING",
                        [release_decision["decision_id"]],
                        "The release decision has no release authority.",
                    )
                )
            if not release_decision["content_digests_verified"]:
                failures.append(
                    (
                        "CONTENT_DIGEST_ATTESTATION_MISSING",
                        [release_decision["decision_id"]],
                        "The release decision does not attest verified content digests.",
                    )
                )
            if not release_decision["complete_support_declared"]:
                failures.append(
                    (
                        "COMPLETE_SUPPORT_NOT_DECLARED",
                        [release_decision["decision_id"]],
                        "The release authority did not declare complete support.",
                    )
                )
            decision_support_refs = set(
                release_decision["basis_support_relation_refs"]
            )
            if not bundle_support_refs <= decision_support_refs:
                failures.append(
                    (
                        "RELEASE_SUPPORT_BASIS_INCOMPLETE",
                        sorted(bundle_support_refs - decision_support_refs),
                        "The release decision omits a support relation in the evidence bundle.",
                    )
                )
            disclosed = set(
                release_decision["disclosed_contradiction_refs"]
            )
            if disclosed != all_contradiction_refs:
                failures.append(
                    (
                        "CONTRADICTORY_EVIDENCE_OMITTED",
                        sorted(all_contradiction_refs - disclosed),
                        "The release decision does not disclose every recorded contradiction.",
                    )
                )

        active_quarantine_refs = [
            item["quarantine_id"]
            for item in quarantines_by_claim.get(claim_ref, [])
            if item["active"]
        ]
        if active_quarantine_refs:
            failures.append(
                (
                    "ACTIVE_QUARANTINE",
                    sorted(active_quarantine_refs),
                    "An active quarantine record blocks release.",
                )
            )

        for request in requests_by_claim.get(claim_ref, []):
            if request["assertion_text"] != claim["normalized_text"]:
                failures.append(
                    (
                        "ASSERTION_TEXT_MISMATCH",
                        [request["request_id"], claim_ref],
                        "The downstream SICRP assertion text differs from the normalized claim.",
                    )
                )

        deduplicated = {
            (code, tuple(sorted(refs)), message): (code, sorted(refs), message)
            for code, refs, message in failures
        }
        failures = sorted(
            deduplicated.values(),
            key=lambda item: (item[0], item[1], item[2]),
        )
        candidate_release = not failures and covered == material_refs
        expected_recorded_state = (
            "released" if candidate_release else "quarantined"
        )
        if claim["claim_state"] != expected_recorded_state:
            failures.append(
                (
                    "CLAIM_STATE_MISMATCH",
                    [claim_ref],
                    "The recorded claim state does not match deterministic admissibility.",
                )
            )
            failures.sort(key=lambda item: (item[0], item[1], item[2]))

        release_allowed = not failures and covered == material_refs
        failure_codes = sorted({item[0] for item in failures})
        if any(code in UNVERIFIABLE_CODES for code in failure_codes):
            support_state = "unverifiable"
        elif "UNRESOLVED_CONTRADICTION" in failure_codes:
            support_state = "contradicted"
        elif covered == material_refs:
            support_state = "supported"
        elif covered:
            support_state = "partially_supported"
        else:
            support_state = "unverifiable"

        result = {
            "claim_ref": claim_ref,
            "recorded_state": claim["claim_state"],
            "support_state": support_state,
            "evaluated_state": (
                "released" if release_allowed else "quarantined"
            ),
            "material_segment_refs": sorted(material_refs),
            "covered_segment_refs": sorted(covered),
            "uncovered_segment_refs": sorted(uncovered),
            "support_relation_refs": sorted(
                item["support_id"] for item in claim_supports
            ),
            "contradiction_relation_refs": sorted(all_contradiction_refs),
            "release_decision_ref": (
                release_decision["decision_id"] if release_decision else None
            ),
            "release_allowed": release_allowed,
            "failure_codes": failure_codes,
        }
        claim_results.append(result)
        for code, related_refs, message in failures:
            failure_facts.append(
                {
                    "code": code,
                    "claim_ref": claim_ref,
                    "related_refs": related_refs,
                    "message": message,
                }
            )

    return claim_results, failure_facts, reference_integrity


def _eligible_assertions(
    manifest: dict[str, Any],
    released_claim_refs: set[str],
) -> list[dict[str, Any]]:
    claims = {
        item["claim_id"]: item for item in manifest["extracted_claims"]
    }
    assertions = []
    for request in sorted(
        manifest["sicrp_assertion_requests"],
        key=lambda item: item["request_id"],
    ):
        claim_ref = request["claim_ref"]
        if claim_ref not in released_claim_refs:
            continue
        claim = claims[claim_ref]
        payload = {
            "request_ref": request["request_id"],
            "claim_ref": claim_ref,
            "evidence_bundle_ref": claim["evidence_bundle_ref"],
            "target_record_ref": request["target_record_ref"],
            "target_entity_ref": request["target_entity_ref"],
            "target_field": request["target_field"],
            "assertion_text": request["assertion_text"],
        }
        payload["assertion_id"] = (
            "urn:caeluviim:assertion:eligible-sicrp:"
            + sha256_json(payload)
        )
        assertions.append(payload)
    return assertions


def evaluate_manifest(
    manifest: dict[str, Any],
    *,
    schema: dict[str, Any],
    project_root: Path | str,
) -> dict[str, Any]:
    manifest_copy = copy.deepcopy(manifest)
    schema_result = validate_json_document(manifest_copy, schema)
    if not schema_result["conforms"]:
        raise EvaluationError(
            "manifest does not conform: "
            + "; ".join(
                f"{item['path']}: {item['message']}"
                for item in schema_result["errors"]
            )
        )
    claim_results, failure_facts, reference_integrity = _claim_failures(
        manifest_copy,
        project_root=Path(project_root),
    )
    released = sorted(
        item["claim_ref"]
        for item in claim_results
        if item["evaluated_state"] == "released"
    )
    quarantined = sorted(
        item["claim_ref"]
        for item in claim_results
        if item["evaluated_state"] == "quarantined"
    )
    released_set = set(released)
    quarantined_set = set(quarantined)
    if released_set & quarantined_set:
        raise EvaluationError(
            "deterministic claim partitions are not disjoint"
        )
    if released and quarantined:
        pipeline_result = "released_with_quarantine"
    elif released:
        pipeline_result = "all_released"
    else:
        pipeline_result = "all_quarantined"

    assessment: dict[str, Any] = {
        "$schema": ASSESSMENT_SCHEMA,
        "pipeline_version": "0.1.0",
        "manifest_ref": manifest_copy["manifest_id"],
        "manifest_digest": sha256_json(manifest_copy),
        "evaluation_as_of": manifest_copy["evaluation_as_of"],
        "manifest_conforms": True,
        "reference_integrity": reference_integrity,
        "pipeline_result": pipeline_result,
        "claim_results": claim_results,
        "failure_facts": sorted(
            failure_facts,
            key=lambda item: (
                item["claim_ref"],
                item["code"],
                item["related_refs"],
                item["message"],
            ),
        ),
        "released_claim_refs": released,
        "quarantined_claim_refs": quarantined,
        "eligible_sicrp_assertions": _eligible_assertions(
            manifest_copy,
            released_set,
        ),
        "graph_separation": {
            "asserted_claim_refs": released,
            "quarantined_claim_refs": quarantined,
            "claim_sets_disjoint": True,
            "quarantined_claims_excluded_from_release_payload": True,
        },
        "governance": {
            "evaluation_semantics": SEMANTICS_VERSION,
            "release_authority_evaluated": True,
            "independent_validation_conferred": False,
            "sicrp_validation_conferred": False,
            "ratification_conferred": False,
        },
    }
    digest = sha256_json(assessment)
    assessment["assessment_id"] = (
        f"urn:caeluviim:assessment:evidence-intake:{digest}"
    )
    assessment["assessment_digest"] = digest
    return assessment


def released_payload(
    manifest: dict[str, Any],
    assessment: dict[str, Any],
) -> dict[str, Any]:
    released_refs = set(assessment["released_claim_refs"])
    claims = {
        item["claim_id"]: item for item in manifest["extracted_claims"]
    }
    segments = {
        item["segment_id"]: item
        for item in manifest["material_claim_segments"]
    }
    released_claims = []
    for claim_ref in sorted(released_refs):
        claim = claims[claim_ref]
        released_claims.append(
            {
                "claim_ref": claim_ref,
                "normalized_text": claim["normalized_text"],
                "claim_mode": claim["claim_mode"],
                "evidence_bundle_ref": claim["evidence_bundle_ref"],
                "material_segments": [
                    {
                        "segment_ref": segment_ref,
                        "text": segments[segment_ref]["text"],
                    }
                    for segment_ref in sorted(
                        claim["material_segment_refs"]
                    )
                ],
            }
        )
    payload = {
        "interface_version": "evidence-intake-release/0.1.0",
        "manifest_ref": manifest["manifest_id"],
        "assessment_ref": assessment["assessment_id"],
        "assessment_digest": assessment["assessment_digest"],
        "released_claims": released_claims,
        "eligible_sicrp_assertions": assessment[
            "eligible_sicrp_assertions"
        ],
    }
    payload["payload_digest"] = sha256_json(payload)
    return payload


def failure_code_counts(
    assessment: dict[str, Any],
) -> dict[str, int]:
    return dict(
        sorted(Counter(item["code"] for item in assessment["failure_facts"]).items())
    )
