from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from pyshacl import validate as shacl_validate
from rdflib import Graph, Namespace, RDF, URIRef

from .canonical import sha256_bytes, sha256_json

ACQ = Namespace("https://caeluviim.org/ontology/source-acquisition#")
ASSESSMENT_SCHEMA = (
    "https://caeluviim.org/schema/source-acquisition-assessment.schema.json"
)
SNAPSHOT_PREFIX = "urn:caeluviim:snapshot:sha256:"
VERSION_DIGEST_MARKER = ":sha256:"


class AcquisitionEvaluationError(ValueError):
    """Raised when a manifest cannot be safely evaluated."""


def load_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text("utf-8"))
    if not isinstance(value, dict):
        raise AcquisitionEvaluationError("JSON document must be an object")
    return value


def validate_json_document(
    document: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    errors = sorted(
        validator.iter_errors(document),
        key=lambda item: list(item.absolute_path),
    )
    return {
        "conforms": not errors,
        "errors": [
            {
                "path": "/".join(str(part) for part in error.absolute_path),
                "message": error.message,
            }
            for error in errors
        ],
    }


def validate_rdf_manifest(
    rdf_path: str | Path,
    *,
    shapes_path: str | Path,
    ontology_path: str | Path,
) -> dict[str, Any]:
    data = Graph().parse(rdf_path, format="turtle")
    shapes = Graph().parse(shapes_path, format="turtle")
    ontology = Graph().parse(ontology_path, format="turtle")
    conforms, report_graph, report_text = shacl_validate(
        data_graph=data,
        shacl_graph=shapes,
        ont_graph=ontology,
        inference="rdfs",
        advanced=True,
    )
    return {
        "conforms": bool(conforms),
        "report_text": str(report_text),
        "report_triple_count": len(report_graph),
    }


ENTITY_TYPES = {
    "source_requests": "SourceRequest",
    "retrieval_attempts": "RetrievalAttempt",
    "retrieved_representations": "RetrievedRepresentation",
    "canonical_source_identities": "CanonicalSourceIdentity",
    "source_versions": "SourceVersion",
    "snapshot_fixations": "SnapshotFixation",
    "acquisition_failures": "AcquisitionFailure",
    "change_events": "ChangeEvent",
    "supersession_relations": "SupersessionRelation",
    "source_availability_observations": "SourceAvailabilityObservation",
}

ENTITY_ID_FIELDS = {
    "source_requests": "request_id",
    "retrieval_attempts": "attempt_id",
    "retrieved_representations": "representation_id",
    "canonical_source_identities": "identity_id",
    "source_versions": "version_id",
    "snapshot_fixations": "fixation_id",
    "acquisition_failures": "failure_id",
    "change_events": "change_id",
    "supersession_relations": "relation_id",
    "source_availability_observations": "observation_id",
}


def verify_cross_format_alignment(
    manifest: dict[str, Any],
    rdf_path: str | Path,
) -> dict[str, Any]:
    graph = Graph().parse(rdf_path, format="turtle")
    missing: list[dict[str, str]] = []
    for collection, class_name in ENTITY_TYPES.items():
        field = ENTITY_ID_FIELDS[collection]
        for item in manifest.get(collection, []):
            ref = item[field]
            if (
                URIRef(ref),
                RDF.type,
                ACQ[class_name],
            ) not in graph:
                missing.append(
                    {
                        "collection": collection,
                        "json_ref": ref,
                        "expected_rdf_type": str(ACQ[class_name]),
                    }
                )
    manifest_ref = URIRef(manifest["manifest_id"])
    if (manifest_ref, RDF.type, ACQ.AcquisitionManifest) not in graph:
        missing.append(
            {
                "collection": "manifest",
                "json_ref": manifest["manifest_id"],
                "expected_rdf_type": str(ACQ.AcquisitionManifest),
            }
        )
    return {
        "conforms": not missing,
        "missing_typed_entities": missing,
    }


def _index(
    items: Iterable[dict[str, Any]],
    key: str,
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    result: dict[str, dict[str, Any]] = {}
    duplicates: set[str] = set()
    for item in items:
        value = item[key]
        if value in result:
            duplicates.add(value)
        result[value] = item
    return result, duplicates


def _safe_content_bytes(project_root: Path, relative: str) -> bytes:
    candidate = project_root / relative
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise AcquisitionEvaluationError(
            f"captured representation is unavailable: {relative}"
        ) from error
    try:
        resolved.relative_to(project_root)
    except ValueError as error:
        raise AcquisitionEvaluationError(
            f"content path escapes project root: {relative}"
        ) from error
    if candidate.is_symlink() or not resolved.is_file():
        raise AcquisitionEvaluationError(
            f"content path must be a regular non-symlink file: {relative}"
        )
    return resolved.read_bytes()


def _fact(
    subject_ref: str,
    code: str,
    message: str,
) -> dict[str, str]:
    token = sha256_json(
        {
            "subject_ref": subject_ref,
            "code": code,
            "message": message,
        }
    )
    return {
        "fact_id": f"urn:caeluviim:acquisition-failure-fact:{token}",
        "subject_ref": subject_ref,
        "code": code,
        "message": message,
    }


def _add(
    facts: list[dict[str, str]],
    subject_ref: str,
    code: str,
    message: str,
) -> None:
    facts.append(_fact(subject_ref, code, message))


def evaluate_manifest(
    manifest: dict[str, Any],
    *,
    schema: dict[str, Any],
    project_root: str | Path,
) -> dict[str, Any]:
    validation = validate_json_document(manifest, schema)
    if not validation["conforms"]:
        raise AcquisitionEvaluationError(
            "manifest does not conform: "
            + json.dumps(validation["errors"], sort_keys=True)
        )

    root = Path(project_root).resolve()
    requests, duplicate_requests = _index(
        manifest["source_requests"], "request_id"
    )
    attempts, duplicate_attempts = _index(
        manifest["retrieval_attempts"], "attempt_id"
    )
    representations, duplicate_representations = _index(
        manifest["retrieved_representations"], "representation_id"
    )
    identities, duplicate_identities = _index(
        manifest["canonical_source_identities"], "identity_id"
    )
    versions, duplicate_versions = _index(
        manifest["source_versions"], "version_id"
    )
    fixations, duplicate_fixations = _index(
        manifest["snapshot_fixations"], "fixation_id"
    )
    failures, duplicate_failures = _index(
        manifest["acquisition_failures"], "failure_id"
    )
    availability, duplicate_availability = _index(
        manifest["source_availability_observations"], "observation_id"
    )
    changes, duplicate_changes = _index(
        manifest["change_events"], "change_id"
    )
    supersessions, duplicate_supersessions = _index(
        manifest["supersession_relations"], "relation_id"
    )

    facts: list[dict[str, str]] = []
    duplicate_sets = [
        duplicate_requests,
        duplicate_attempts,
        duplicate_representations,
        duplicate_identities,
        duplicate_versions,
        duplicate_fixations,
        duplicate_failures,
        duplicate_availability,
        duplicate_changes,
        duplicate_supersessions,
    ]
    for duplicate in sorted(set().union(*duplicate_sets)):
        _add(
            facts,
            duplicate,
            "DUPLICATE_IDENTIFIER",
            "Every acquisition entity identifier must be unique.",
        )

    boundary = manifest["authority_boundary"]
    if any(boundary.values()):
        _add(
            facts,
            manifest["manifest_id"],
            "ACQUISITION_AUTHORITY_EXCEEDED",
            "Acquisition cannot assess source authority, claim support, or truth.",
        )

    observations_by_attempt = {
        item["attempt_ref"]: item
        for item in manifest["source_availability_observations"]
    }
    failures_by_attempt = {
        item["attempt_ref"]: item
        for item in manifest["acquisition_failures"]
    }
    representations_by_attempt = {
        item["attempt_ref"]: item
        for item in manifest["retrieved_representations"]
    }
    fixations_by_representation = {
        item["representation_ref"]: item
        for item in manifest["snapshot_fixations"]
    }
    versions_by_representation = {
        item["representation_ref"]: item
        for item in manifest["source_versions"]
    }

    attempt_results: list[dict[str, Any]] = []
    for attempt in manifest["retrieval_attempts"]:
        ref = attempt["attempt_id"]
        before = len(facts)
        request = requests.get(attempt["request_ref"])
        if request is None:
            _add(
                facts,
                ref,
                "SOURCE_REQUEST_MISSING",
                "Retrieval attempt must reference a source request.",
            )
        elif request["requested_uri"] != attempt["requested_uri"]:
            _add(
                facts,
                ref,
                "REQUEST_URI_MISMATCH",
                "Attempt URI must equal the source request URI.",
            )

        chain = attempt["redirect_chain"]
        if [hop["sequence"] for hop in chain] != list(range(len(chain))):
            _add(
                facts,
                ref,
                "REDIRECT_CHAIN_INVALID",
                "Redirect hop sequence must be contiguous from zero.",
            )
        if chain and chain[0]["uri"] != attempt["requested_uri"]:
            _add(
                facts,
                ref,
                "REDIRECT_CHAIN_ORIGIN_MISMATCH",
                "First redirect-chain URI must equal the requested URI.",
            )
        for left, right in zip(chain, chain[1:]):
            if left.get("location_uri") != right["uri"]:
                _add(
                    facts,
                    ref,
                    "REDIRECT_CHAIN_BROKEN",
                    "Each redirect Location must equal the next hop URI.",
                )
        observation = observations_by_attempt.get(ref)
        if observation is None:
            _add(
                facts,
                ref,
                "AVAILABILITY_OBSERVATION_MISSING",
                "Every attempt must have an availability observation.",
            )

        if attempt["outcome"] == "successful":
            representation = representations.get(
                attempt.get("representation_ref", "")
            )
            if representation is None:
                _add(
                    facts,
                    ref,
                    "REPRESENTATION_MISSING",
                    "Successful retrieval must reference a representation.",
                )
            if not chain or attempt.get("final_uri") != chain[-1]["uri"]:
                _add(
                    facts,
                    ref,
                    "FINAL_URI_MISMATCH",
                    "Final URI must equal the final redirect-chain URI.",
                )
            if observation and observation["status"] != "available":
                _add(
                    facts,
                    ref,
                    "AVAILABILITY_STATUS_MISMATCH",
                    "Successful retrieval must be observed as available.",
                )
        else:
            failure = failures.get(attempt.get("failure_ref", ""))
            if failure is None or failure.get("attempt_ref") != ref:
                _add(
                    facts,
                    ref,
                    "ACQUISITION_FAILURE_MISSING",
                    "Failed or blocked retrieval must record an acquisition failure.",
                )
            if ref in representations_by_attempt:
                _add(
                    facts,
                    ref,
                    "FAILED_ATTEMPT_HAS_REPRESENTATION",
                    "Failed retrieval cannot produce a captured representation.",
                )
            if observation and observation["status"] == "available":
                _add(
                    facts,
                    ref,
                    "AVAILABILITY_STATUS_MISMATCH",
                    "Failed retrieval cannot be observed as available.",
                )
            _add(
                facts,
                ref,
                "RETRIEVAL_NOT_SUCCESSFUL",
                "Retrieval failure is an acquisition fact, not evidentiary absence.",
            )
        codes = sorted(
            item["code"] for item in facts[before:] if item["subject_ref"] == ref
        )
        attempt_results.append(
            {
                "attempt_ref": ref,
                "outcome": attempt["outcome"],
                "intake_eligible": (
                    attempt["outcome"] == "successful" and not codes
                ),
                "failure_codes": codes,
            }
        )

    for failure in manifest["acquisition_failures"]:
        if failure["attempt_ref"] not in attempts:
            _add(
                facts,
                failure["failure_id"],
                "RETRIEVAL_ATTEMPT_MISSING",
                "Acquisition failure must reference a retrieval attempt.",
            )
        if failure["evidentiary_absence_inferred"]:
            _add(
                facts,
                failure["failure_id"],
                "FAILURE_MISCAST_AS_EVIDENTIARY_ABSENCE",
                "Retrieval failure cannot establish evidentiary absence.",
            )

    for observation in manifest["source_availability_observations"]:
        if observation["attempt_ref"] not in attempts:
            _add(
                facts,
                observation["observation_id"],
                "RETRIEVAL_ATTEMPT_MISSING",
                "Availability observation must reference an attempt.",
            )
        if observation["request_ref"] not in requests:
            _add(
                facts,
                observation["observation_id"],
                "SOURCE_REQUEST_MISSING",
                "Availability observation must reference a source request.",
            )
        if observation["evidentiary_absence_inferred"]:
            _add(
                facts,
                observation["observation_id"],
                "FAILURE_MISCAST_AS_EVIDENTIARY_ABSENCE",
                "Availability observation cannot establish evidentiary absence.",
            )

    version_results: list[dict[str, Any]] = []
    for version in manifest["source_versions"]:
        version_ref = version["version_id"]
        snapshot_ref = version["snapshot_ref"]
        before = len(facts)
        representation = representations.get(version["representation_ref"])
        if representation is None:
            _add(
                facts,
                version_ref,
                "REPRESENTATION_MISSING",
                "Source version must reference a retrieved representation.",
            )
        if version["canonical_identity_ref"] not in identities:
            _add(
                facts,
                version_ref,
                "CANONICAL_IDENTITY_MISSING",
                "Source version must reference a canonical source identity.",
            )
        if VERSION_DIGEST_MARKER + version["sha256"] not in version_ref:
            _add(
                facts,
                version_ref,
                "VERSION_ID_NOT_CONTENT_BOUND",
                "Source version identity must include its content digest.",
            )
        fixation = (
            fixations_by_representation.get(version["representation_ref"])
            if representation
            else None
        )
        if fixation is None:
            _add(
                facts,
                version_ref,
                "SNAPSHOT_FIXATION_MISSING",
                "Source version requires a snapshot fixation.",
            )
        else:
            if fixation["snapshot_id"] != snapshot_ref:
                _add(
                    facts,
                    version_ref,
                    "SNAPSHOT_REFERENCE_MISMATCH",
                    "Version snapshot reference must equal its fixation snapshot.",
                )
            expected_snapshot = SNAPSHOT_PREFIX + fixation["sha256"]
            if fixation["snapshot_id"] != expected_snapshot:
                _add(
                    facts,
                    version_ref,
                    "SNAPSHOT_ID_NOT_CONTENT_ADDRESS",
                    "Snapshot ID must equal SHA-256 of the exact bytes.",
                )
            try:
                content = _safe_content_bytes(root, fixation["content_path"])
            except AcquisitionEvaluationError:
                content = None
                _add(
                    facts,
                    version_ref,
                    "FIXED_CONTENT_UNAVAILABLE",
                    "Fixed bytes must remain recoverable beneath the project root.",
                )
            if content is not None:
                digest = sha256_bytes(content)
                if len(content) != fixation["byte_length"]:
                    _add(
                        facts,
                        version_ref,
                        "SNAPSHOT_LENGTH_MISMATCH",
                        "Fixed byte length differs from the exact content.",
                    )
                if digest != fixation["sha256"]:
                    _add(
                        facts,
                        version_ref,
                        "SNAPSHOT_DIGEST_MISMATCH",
                        "Fixed digest differs from the exact content.",
                    )
                if representation:
                    if representation["content_path"] != fixation["content_path"]:
                        _add(
                            facts,
                            version_ref,
                            "FIXATION_PATH_MISMATCH",
                            "Representation and fixation must address the same bytes.",
                        )
                    if representation["sha256"] != digest:
                        _add(
                            facts,
                            version_ref,
                            "REPRESENTATION_DIGEST_MISMATCH",
                            "Representation digest differs from retrieved bytes.",
                        )
                    if representation["byte_length"] != len(content):
                        _add(
                            facts,
                            version_ref,
                            "REPRESENTATION_LENGTH_MISMATCH",
                            "Representation length differs from retrieved bytes.",
                        )
                if version["sha256"] != digest:
                    _add(
                        facts,
                        version_ref,
                        "VERSION_DIGEST_MISMATCH",
                        "Version digest differs from fixed bytes.",
                    )
        codes = sorted(
            item["code"]
            for item in facts[before:]
            if item["subject_ref"] == version_ref
        )
        version_results.append(
            {
                "version_ref": version_ref,
                "snapshot_ref": snapshot_ref,
                "intake_eligible": not codes,
                "failure_codes": codes,
            }
        )

    versions_by_identity: dict[str, list[dict[str, Any]]] = {}
    for version in manifest["source_versions"]:
        versions_by_identity.setdefault(
            version["canonical_identity_ref"], []
        ).append(version)
    change_pairs = {
        (item["previous_version_ref"], item["next_version_ref"]): item
        for item in manifest["change_events"]
    }
    supersession_pairs = {
        (
            item["superseded_version_ref"],
            item["superseding_version_ref"],
        ): item
        for item in manifest["supersession_relations"]
    }
    for identity_ref, identity_versions in versions_by_identity.items():
        ordered = sorted(identity_versions, key=lambda item: item["observed_at"])
        for previous, next_version in zip(ordered, ordered[1:]):
            if previous["sha256"] == next_version["sha256"]:
                continue
            pair = (previous["version_id"], next_version["version_id"])
            change = change_pairs.get(pair)
            supersession = supersession_pairs.get(pair)
            if change is None:
                _add(
                    facts,
                    next_version["version_id"],
                    "CHANGE_EVENT_MISSING",
                    "Changed bytes for one canonical identity require a ChangeEvent.",
                )
            else:
                if (
                    change["canonical_identity_ref"] != identity_ref
                    or change["previous_sha256"] != previous["sha256"]
                    or change["next_sha256"] != next_version["sha256"]
                ):
                    _add(
                        facts,
                        next_version["version_id"],
                        "CHANGE_EVENT_MISMATCH",
                        "ChangeEvent must bind the compared identity and digests.",
                    )
            if supersession is None:
                _add(
                    facts,
                    next_version["version_id"],
                    "SUPERSESSION_RELATION_MISSING",
                    "Changed mutable source versions require explicit supersession.",
                )

    version_fact_codes: dict[str, list[str]] = {}
    for fact in facts:
        version_fact_codes.setdefault(fact["subject_ref"], []).append(
            fact["code"]
        )
    for result in version_results:
        codes = sorted(
            set(
                result["failure_codes"]
                + version_fact_codes.get(result["version_ref"], [])
            )
        )
        result["failure_codes"] = codes
        result["intake_eligible"] = not codes

    attempt_results_by_ref = {
        item["attempt_ref"]: item for item in attempt_results
    }
    for result in version_results:
        if result["intake_eligible"]:
            continue
        version = versions[result["version_ref"]]
        representation = representations.get(version["representation_ref"])
        if representation is None:
            continue
        attempt_ref = representation["attempt_ref"]
        attempt_result = attempt_results_by_ref.get(attempt_ref)
        if attempt_result is None:
            continue
        attempt_result["intake_eligible"] = False
        attempt_result["failure_codes"] = sorted(
            set(
                attempt_result["failure_codes"]
                + ["VERSION_NOT_INTAKE_ELIGIBLE"]
            )
        )
        _add(
            facts,
            attempt_ref,
            "VERSION_NOT_INTAKE_ELIGIBLE",
            "The attempt's captured version failed an acquisition eligibility gate.",
        )

    eligible_snapshots = sorted(
        result["snapshot_ref"]
        for result in version_results
        if result["intake_eligible"]
    )
    ineligible_attempts = sorted(
        result["attempt_ref"]
        for result in attempt_results
        if not result["intake_eligible"]
    )
    facts = sorted(
        {item["fact_id"]: item for item in facts}.values(),
        key=lambda item: (item["subject_ref"], item["code"], item["fact_id"]),
    )
    if eligible_snapshots and ineligible_attempts:
        pipeline_result = "eligible_with_failures"
    elif eligible_snapshots:
        pipeline_result = "eligible"
    else:
        pipeline_result = "ineligible"

    assessment: dict[str, Any] = {
        "$schema": ASSESSMENT_SCHEMA,
        "manifest_ref": manifest["manifest_id"],
        "manifest_digest": sha256_json(manifest),
        "pipeline_version": manifest["pipeline_version"],
        "pipeline_result": pipeline_result,
        "authority_boundary_preserved": not any(boundary.values()),
        "eligible_snapshot_refs": eligible_snapshots,
        "ineligible_attempt_refs": ineligible_attempts,
        "version_results": sorted(
            version_results, key=lambda item: item["version_ref"]
        ),
        "attempt_results": sorted(
            attempt_results, key=lambda item: item["attempt_ref"]
        ),
        "failure_facts": facts,
    }
    digest = sha256_json(assessment)
    assessment["assessment_digest"] = digest
    assessment["assessment_id"] = (
        f"urn:caeluviim:assessment:source-acquisition:{digest}"
    )
    return assessment


def intake_eligible_payload(
    manifest: dict[str, Any],
    assessment: dict[str, Any],
) -> dict[str, Any]:
    eligible = set(assessment["eligible_snapshot_refs"])
    fixations = {
        item["snapshot_id"]: item for item in manifest["snapshot_fixations"]
    }
    representations = {
        item["representation_id"]: item
        for item in manifest["retrieved_representations"]
    }
    versions = {
        item["snapshot_ref"]: item for item in manifest["source_versions"]
    }
    attempts = {
        item["attempt_id"]: item for item in manifest["retrieval_attempts"]
    }
    records: list[dict[str, Any]] = []
    for snapshot_ref in sorted(eligible):
        fixation = fixations[snapshot_ref]
        representation = representations[fixation["representation_ref"]]
        version = versions[snapshot_ref]
        attempt = attempts[representation["attempt_ref"]]
        records.append(
            {
                "snapshot_id": snapshot_ref,
                "snapshot_fixation_ref": fixation["fixation_id"],
                "source_version_ref": version["version_id"],
                "canonical_identity_ref": version[
                    "canonical_identity_ref"
                ],
                "retrieval_attempt_ref": attempt["attempt_id"],
                "requested_uri": attempt["requested_uri"],
                "final_uri": representation["final_uri"],
                "retrieved_at": representation["retrieved_at"],
                "media_type": representation["media_type"],
                "content_path": fixation["content_path"],
                "byte_length": fixation["byte_length"],
                "sha256": fixation["sha256"],
            }
        )
    return {
        "acquisition_manifest_ref": manifest["manifest_id"],
        "acquisition_manifest_digest": assessment["manifest_digest"],
        "acquisition_assessment_ref": assessment["assessment_id"],
        "acquisition_assessment_digest": assessment["assessment_digest"],
        "authority_boundary_preserved": assessment[
            "authority_boundary_preserved"
        ],
        "eligible_snapshots": records,
    }
