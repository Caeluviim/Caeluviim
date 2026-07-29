from __future__ import annotations

import copy
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from pyshacl import validate as shacl_validate
from rdflib import Graph, Namespace, RDF, URIRef

from .canonical import sha256_json

SICRP = Namespace("https://caeluviim.org/ontology/sicrp#")
EMGN = Namespace("https://caeluviim.org/ontology/emgn#")

SEMANTICS_VERSION = "sicrp-runtime/0.1.0"
ASSESSMENT_SCHEMA = "https://caeluviim.org/schema/sicrp-assessment.schema.json"

COLLECTION_IDS = {
    "structural_insolvency_conditions": ("condition_id", "StructuralInsolvencyCondition"),
    "producing_mechanisms": ("mechanism_id", "ProducingMechanism"),
    "affected_constituencies": ("constituency_id", "AffectedConstituency"),
    "material_deficits": ("deficit_id", "MaterialDeficit"),
    "institutional_obligations": ("obligation_id", "InstitutionalObligation"),
    "resource_flows": ("flow_id", "ResourceFlow"),
    "exclusion_events": ("exclusion_id", "ExclusionEvent"),
    "capacity_evidence": ("capacity_id", "CapacityEvidence"),
    "intervention_rights": ("right_id", "InterventionRight"),
    "interventions": ("intervention_id", "Intervention"),
    "collective_resolution_plans": ("plan_id", "CollectiveResolutionPlan"),
    "resolution_metrics": ("metric_id", "ResolutionMetric"),
    "resolution_observations": ("observation_id", "ResolutionObservation"),
    "residual_insolvency": ("residual_id", "ResidualInsolvency"),
    "distributional_effects": ("effect_id", "DistributionalEffect"),
    "validator_assessments": ("assessment_id", "ValidatorAssessment"),
}

REFERENCE_RULES = [
    ("structural_insolvency_conditions", "mechanism_refs", "producing_mechanisms"),
    ("structural_insolvency_conditions", "constituency_refs", "affected_constituencies"),
    ("structural_insolvency_conditions", "material_deficit_refs", "material_deficits"),
    ("structural_insolvency_conditions", "obligation_refs", "institutional_obligations"),
    ("structural_insolvency_conditions", "resource_flow_refs", "resource_flows"),
    ("structural_insolvency_conditions", "exclusion_event_refs", "exclusion_events"),
    ("structural_insolvency_conditions", "capacity_evidence_refs", "capacity_evidence"),
    ("producing_mechanisms", "affected_flow_refs", "resource_flows"),
    ("producing_mechanisms", "affected_constituency_refs", "affected_constituencies"),
    ("producing_mechanisms", "material_deficit_refs", "material_deficits"),
    ("material_deficits", "constituency_ref", "affected_constituencies"),
    ("material_deficits", "obligation_ref", "institutional_obligations"),
    ("material_deficits", "mechanism_refs", "producing_mechanisms"),
    ("material_deficits", "resource_flow_refs", "resource_flows"),
    ("institutional_obligations", "beneficiary_constituency_ref", "affected_constituencies"),
    ("resource_flows", "constrained_by_mechanism_refs", "producing_mechanisms"),
    ("exclusion_events", "mechanism_ref", "producing_mechanisms"),
    ("exclusion_events", "constituency_ref", "affected_constituencies"),
    ("exclusion_events", "material_deficit_ref", "material_deficits"),
    ("capacity_evidence", "obligation_refs", "institutional_obligations"),
    ("intervention_rights", "holder_constituency_ref", "affected_constituencies"),
    ("intervention_rights", "target_mechanism_refs", "producing_mechanisms"),
    ("interventions", "exercised_right_refs", "intervention_rights"),
    ("interventions", "target_mechanism_refs", "producing_mechanisms"),
    ("interventions", "target_exclusion_refs", "exclusion_events"),
    ("interventions", "participant_constituency_refs", "affected_constituencies"),
    ("interventions", "input_flow_refs", "resource_flows"),
    ("interventions", "output_flow_refs", "resource_flows"),
    ("collective_resolution_plans", "affected_constituency_refs", "affected_constituencies"),
    ("collective_resolution_plans", "target_condition_refs", "structural_insolvency_conditions"),
    ("collective_resolution_plans", "target_mechanism_refs", "producing_mechanisms"),
    ("collective_resolution_plans", "intervention_refs", "interventions"),
    ("collective_resolution_plans", "resolution_metric_refs", "resolution_metrics"),
    ("resolution_metrics", "constituency_ref", "affected_constituencies"),
    ("resolution_metrics", "obligation_ref", "institutional_obligations"),
    ("resolution_observations", "metric_ref", "resolution_metrics"),
    ("resolution_observations", "constituency_ref", "affected_constituencies"),
    ("residual_insolvency", "condition_ref", "structural_insolvency_conditions"),
    ("residual_insolvency", "affected_constituency_refs", "affected_constituencies"),
    ("distributional_effects", "metric_ref", "resolution_metrics"),
    ("distributional_effects", "constituency_ref", "affected_constituencies"),
    ("distributional_effects", "initiating_observation_ref", "resolution_observations"),
    ("distributional_effects", "non_initiating_observation_refs", "resolution_observations"),
]

CLAIM_REFERENCE_RULES = [
    ("affected_constituency_refs", "affected_constituencies"),
    ("condition_refs", "structural_insolvency_conditions"),
    ("resolution_plan_refs", "collective_resolution_plans"),
    ("before_observation_refs", "resolution_observations"),
    ("after_observation_refs", "resolution_observations"),
    ("distributional_effect_refs", "distributional_effects"),
    ("residual_insolvency_refs", "residual_insolvency"),
    ("validator_assessment_refs", "validator_assessments"),
]

RESOLUTION_CRITERIA = [
    "mechanism_altered",
    "affected_population_defined",
    "resource_or_right_restored",
    "distributional_effect_measured",
    "residual_insolvency_disclosed",
    "population_generalization_demonstrated",
    "rights_exercisable",
    "coverage_complete",
    "non_regression_passed",
    "independent_validation_recorded",
]


class EvaluationError(RuntimeError):
    pass


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _refs(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def _obligation(
    *,
    obligation_id: str,
    dimension: str,
    status: str,
    code: str,
    message: str,
    blocking_for: Iterable[str] = (),
    subject_refs: Iterable[str] = (),
    evidence_refs: Iterable[str] = (),
) -> dict[str, Any]:
    return {
        "obligation_id": obligation_id,
        "dimension": dimension,
        "status": status,
        "code": code,
        "message": message,
        "blocking_for": sorted(set(blocking_for)),
        "subject_refs": sorted(set(subject_refs)),
        "evidence_refs": sorted(set(evidence_refs)),
    }


def _schema_errors(record: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        {
            "path": "/" + "/".join(str(part) for part in error.absolute_path),
            "message": error.message,
            "validator": error.validator,
        }
        for error in sorted(
            validator.iter_errors(record),
            key=lambda item: (list(item.absolute_path), item.message),
        )
    ]


def validate_json_record(
    record: dict[str, Any], schema: dict[str, Any]
) -> dict[str, Any]:
    errors = _schema_errors(record, schema)
    return {"conforms": not errors, "errors": errors}


def validate_rdf_record(
    rdf_path: Path | str,
    *,
    shapes_path: Path | str,
    ontology_path: Path | str,
) -> dict[str, Any]:
    data = Graph().parse(str(rdf_path), format="turtle")
    shapes = Graph().parse(str(shapes_path), format="turtle")
    ontology = Graph().parse(str(ontology_path), format="turtle")
    conforms, report_graph, report_text = shacl_validate(
        data_graph=data,
        shacl_graph=shapes,
        ont_graph=ontology,
        inference="rdfs",
        advanced=True,
    )
    return {
        "conforms": bool(conforms),
        "data_triples": len(data),
        "shape_triples": len(shapes),
        "ontology_triples": len(ontology),
        "report_text": str(report_text),
        "report_triples": len(report_graph),
    }


def _identifier_maps(record: dict[str, Any]) -> tuple[dict[str, set[str]], list[str]]:
    maps: dict[str, set[str]] = {}
    duplicates: list[str] = []
    all_values: list[str] = []
    for collection, (field, _) in COLLECTION_IDS.items():
        values = [item[field] for item in record.get(collection, []) if field in item]
        duplicates.extend(value for value, count in Counter(values).items() if count > 1)
        maps[collection] = set(values)
        all_values.extend(values)
    claim = record.get("collective_resolution_claim", {})
    maps["collective_resolution_claim"] = (
        {claim["claim_id"]} if "claim_id" in claim else set()
    )
    all_values.extend(maps["collective_resolution_claim"])
    duplicates.extend(
        value for value, count in Counter(all_values).items() if count > 1
    )
    return maps, sorted(set(duplicates))


def _reference_failures(
    record: dict[str, Any], maps: dict[str, set[str]]
) -> list[tuple[str, str, str]]:
    failures: list[tuple[str, str, str]] = []
    for collection, field, target in REFERENCE_RULES:
        for item in record.get(collection, []):
            subject = next(
                (
                    item.get(id_field)
                    for id_field, _ in COLLECTION_IDS.values()
                    if id_field in item
                ),
                collection,
            )
            for reference in _refs(item.get(field)):
                if reference not in maps[target]:
                    failures.append((str(subject), field, reference))
    claim = record.get("collective_resolution_claim", {})
    for field, target in CLAIM_REFERENCE_RULES:
        for reference in _refs(claim.get(field)):
            if reference not in maps[target]:
                failures.append((claim.get("claim_id", "claim"), field, reference))
    assessment_ids = maps.get("validator_assessments", set())
    claim_ids = maps.get("collective_resolution_claim", set())
    for assessment in record.get("validator_assessments", []):
        if assessment.get("assessment_id") in assessment_ids:
            reference = assessment.get("assessed_ref")
            if reference not in claim_ids:
                failures.append(
                    (assessment["assessment_id"], "assessed_ref", str(reference))
                )
    intervention_ids = maps.get("interventions", set())
    for reference in record.get("emgn_trace", {}).get("remediation_refs", []):
        if reference not in intervention_ids:
            failures.append(("emgn_trace", "remediation_refs", reference))
    return sorted(failures)


def _record_evidence(record: dict[str, Any], *collections: str) -> list[str]:
    values: set[str] = set()
    for collection in collections:
        for item in record.get(collection, []):
            values.update(item.get("evidence_refs", []))
    return sorted(values)


def _evaluate_record_obligations(
    record: dict[str, Any], schema: dict[str, Any]
) -> list[dict[str, Any]]:
    obligations: list[dict[str, Any]] = []
    schema_result = validate_json_record(record, schema)
    if schema_result["conforms"]:
        obligations.append(
            _obligation(
                obligation_id="O-JSON-SCHEMA",
                dimension="syntax",
                status="pass",
                code="RECORD_SCHEMA_CONFORMS",
                message="The record conforms to the SICRP Draft 2020-12 schema.",
                blocking_for=["record_conformance"],
                subject_refs=[record.get("record_id", "")],
            )
        )
    else:
        obligations.append(
            _obligation(
                obligation_id="O-JSON-SCHEMA",
                dimension="syntax",
                status="error",
                code="RECORD_SCHEMA_INVALID",
                message="; ".join(
                    f"{item['path']}: {item['message']}"
                    for item in schema_result["errors"]
                ),
                blocking_for=["record_conformance", "collective_resolution"],
                subject_refs=[record.get("record_id", "")],
            )
        )
        return obligations

    maps, duplicates = _identifier_maps(record)
    failures = _reference_failures(record, maps)
    if duplicates:
        failures.extend(("record", "duplicate_id", value) for value in duplicates)
    if failures:
        obligations.append(
            _obligation(
                obligation_id="O-REFERENCE-INTEGRITY",
                dimension="reference_integrity",
                status="fail",
                code="REFERENCE_INTEGRITY_FAILED",
                message="; ".join(
                    f"{subject}.{field} -> {reference}"
                    for subject, field, reference in failures
                ),
                blocking_for=["record_conformance", "collective_resolution"],
                subject_refs=[item[0] for item in failures],
            )
        )
    else:
        obligations.append(
            _obligation(
                obligation_id="O-REFERENCE-INTEGRITY",
                dimension="reference_integrity",
                status="pass",
                code="REFERENCE_INTEGRITY_PASSES",
                message="All SICRP internal references resolve to uniquely identified records.",
                blocking_for=["record_conformance"],
                subject_refs=[record["record_id"]],
            )
        )

    obligations_by_id = {
        item["obligation_id"]: item for item in record["institutional_obligations"]
    }
    arithmetic_failures = []
    for deficit in record["material_deficits"]:
        expected = max(
            0, deficit["required_quantity"] - deficit["observed_quantity"]
        )
        obligation = obligations_by_id.get(deficit["obligation_ref"])
        if abs(deficit["shortfall_quantity"] - expected) > 1e-9:
            arithmetic_failures.append(f"{deficit['deficit_id']}:shortfall")
        if obligation and (
            deficit["resource_type"] != obligation["resource_type"]
            or deficit["unit"] != obligation["unit"]
            or deficit["required_quantity"] != obligation["threshold_value"]
        ):
            arithmetic_failures.append(f"{deficit['deficit_id']}:obligation")
    obligations.append(
        _obligation(
            obligation_id="O-DEFICIT-ARITHMETIC",
            dimension="arithmetic",
            status="fail" if arithmetic_failures else "pass",
            code=(
                "DEFICIT_ARITHMETIC_FAILED"
                if arithmetic_failures
                else "DEFICIT_ARITHMETIC_PASSES"
            ),
            message=(
                "Deficit arithmetic or units failed for "
                + ", ".join(arithmetic_failures)
                if arithmetic_failures
                else "Every shortfall equals max(0, required - observed) with matching obligation units."
            ),
            blocking_for=["record_conformance", "collective_resolution"],
            subject_refs=[
                item["deficit_id"] for item in record["material_deficits"]
            ],
            evidence_refs=_record_evidence(record, "material_deficits"),
        )
    )

    temporal_failures: list[str] = []
    window_fields = [
        ("material_deficits", "measurement_window"),
        ("institutional_obligations", "evaluation_period"),
        ("resource_flows", "time_window"),
        ("capacity_evidence", "time_window"),
        ("resolution_observations", "measurement_window"),
    ]
    for collection, field in window_fields:
        id_field = COLLECTION_IDS[collection][0]
        for item in record[collection]:
            window = item[field]
            try:
                if _parse_time(window["start"]) >= _parse_time(window["end"]):
                    temporal_failures.append(item[id_field])
            except (TypeError, ValueError):
                temporal_failures.append(item[id_field])
    for intervention in record["interventions"]:
        try:
            if _parse_time(intervention["start_at"]) >= _parse_time(
                intervention["end_at"]
            ):
                temporal_failures.append(intervention["intervention_id"])
        except (TypeError, ValueError):
            temporal_failures.append(intervention["intervention_id"])
    obligations.append(
        _obligation(
            obligation_id="O-TEMPORAL-ORDER",
            dimension="temporal_integrity",
            status="fail" if temporal_failures else "pass",
            code=(
                "TEMPORAL_ORDER_FAILED"
                if temporal_failures
                else "TEMPORAL_ORDER_PASSES"
            ),
            message=(
                "Invalid temporal intervals: " + ", ".join(temporal_failures)
                if temporal_failures
                else "Every declared interval has a start strictly before its end."
            ),
            blocking_for=["record_conformance"],
            subject_refs=temporal_failures or [record["record_id"]],
        )
    )

    governance = record["governance"]
    proposer = governance["proposer_id"]
    implementers = {
        actor
        for intervention in record["interventions"]
        for actor in intervention["responsible_actor_refs"]
    }
    independence_failures: list[str] = []
    if proposer in governance["validators"] or governance["proposer_is_validator"]:
        independence_failures.append(proposer)
    for observation in record["resolution_observations"]:
        if observation["assessor_ref"] == proposer or observation[
            "assessor_ref"
        ] in implementers:
            independence_failures.append(observation["observation_id"])
    for assessment in record["validator_assessments"]:
        if (
            assessment["validator_ref"] == proposer
            or assessment["validator_ref"] in implementers
            or not assessment["independent_from_proposer"]
            or not assessment["independent_from_implementers"]
        ):
            independence_failures.append(assessment["assessment_id"])
    obligations.append(
        _obligation(
            obligation_id="O-VALIDATOR-INDEPENDENCE",
            dimension="validator_independence",
            status="fail" if independence_failures else "pass",
            code=(
                "VALIDATOR_INDEPENDENCE_FAILED"
                if independence_failures
                else "VALIDATOR_INDEPENDENCE_PASSES"
            ),
            message=(
                "Non-independent proposer, assessor, or validator references: "
                + ", ".join(sorted(set(independence_failures)))
                if independence_failures
                else "Recorded assessors and validators are distinct from the proposer and intervention implementers."
            ),
            blocking_for=["record_conformance", "collective_resolution"],
            subject_refs=independence_failures or governance["validators"],
        )
    )

    condition_refs = [
        item["condition_id"] for item in record["structural_insolvency_conditions"]
    ]
    structural_supported = (
        all(item["shortfall_quantity"] > 0 for item in record["material_deficits"])
        and all(item["mechanism_refs"] for item in record["structural_insolvency_conditions"])
        and all(item["capacity_evidence_refs"] for item in record["structural_insolvency_conditions"])
        and not failures
        and not arithmetic_failures
    )
    obligations.append(
        _obligation(
            obligation_id="O-STRUCTURAL-INSOLVENCY",
            dimension="structural_insolvency",
            status="pass" if structural_supported else "fail",
            code=(
                "STRUCTURAL_INSOLVENCY_SUPPORTED"
                if structural_supported
                else "STRUCTURAL_INSOLVENCY_NOT_SUPPORTED"
            ),
            message=(
                "Positive, obligation-scoped deficits are linked through producing mechanisms, resource flows, exclusions, constituencies, and capacity evidence."
                if structural_supported
                else "The record does not complete the evidence path required to support structural insolvency."
            ),
            blocking_for=["structural_insolvency"],
            subject_refs=condition_refs,
            evidence_refs=_record_evidence(
                record,
                "structural_insolvency_conditions",
                "material_deficits",
                "producing_mechanisms",
                "capacity_evidence",
            ),
        )
    )

    claim = record["collective_resolution_claim"]
    criteria = claim["criteria"]
    observations = {
        item["observation_id"]: item for item in record["resolution_observations"]
    }
    effects = {
        item["effect_id"]: item for item in record["distributional_effects"]
    }

    coverage_observations = [
        item
        for item in record["resolution_observations"]
        if item["phase"] == "after"
        and item["population_scope"] == "affected_constituency"
        and item["metric_ref"]
        in {
            metric["metric_id"]
            for metric in record["resolution_metrics"]
            if metric["metric_type"] == "distributional_coverage"
        }
    ]
    effect_generalization = all(
        effects[reference]["generalized_beyond_initiating_claimant"]
        and effects[reference]["coverage_count"] >= 2
        and observations[
            effects[reference]["initiating_observation_ref"]
        ]["population_scope"]
        == "initiating_claimant"
        and all(
            observations[item]["population_scope"] == "non_initiating_members"
            for item in effects[reference]["non_initiating_observation_refs"]
        )
        for reference in claim["distributional_effect_refs"]
    )
    coverage_passes = (
        bool(coverage_observations)
        and all(item["threshold_met"] for item in coverage_observations)
        and effect_generalization
        and criteria["coverage_complete"]
    )
    obligations.append(
        _obligation(
            obligation_id="O-COLLECTIVE-COVERAGE",
            dimension="coverage",
            status="pass" if coverage_passes else "fail",
            code="COVERAGE_COMPLETE" if coverage_passes else "COVERAGE_INCOMPLETE",
            message=(
                "Affected-constituency coverage meets the declared threshold and generalizes beyond the initiating claimant."
                if coverage_passes
                else "Collective coverage is incomplete even though some after-observations may show improvement."
            ),
            blocking_for=["collective_resolution"],
            subject_refs=[
                item["observation_id"] for item in coverage_observations
            ]
            + claim["distributional_effect_refs"],
            evidence_refs=_record_evidence(
                record, "resolution_observations", "distributional_effects"
            ),
        )
    )

    residuals = [
        item
        for item in record["residual_insolvency"]
        if item["residual_id"] in claim["residual_insolvency_refs"]
    ]
    undisclosed = [item for item in residuals if not item["disclosed"]]
    obligations.append(
        _obligation(
            obligation_id="O-RESIDUAL-DISCLOSURE",
            dimension="residual_insolvency",
            status="fail" if undisclosed else "pass",
            code=(
                "RESIDUAL_DISCLOSURE_FAILED"
                if undisclosed
                else "RESIDUAL_DISCLOSURE_PASSES"
            ),
            message=(
                "Residual insolvency is not fully disclosed."
                if undisclosed
                else "Every referenced residual-insolvency record is explicitly disclosed."
            ),
            blocking_for=["record_conformance", "collective_resolution"],
            subject_refs=[item["residual_id"] for item in residuals],
            evidence_refs=_record_evidence(record, "residual_insolvency"),
        )
    )
    active_residuals = [
        item
        for item in residuals
        if item["status"] not in {"resolved", "closed", "eliminated"}
    ]
    obligations.append(
        _obligation(
            obligation_id="O-RESIDUAL-RESOLUTION",
            dimension="residual_insolvency",
            status="fail" if active_residuals else "pass",
            code=(
                "RESIDUAL_INSOLVENCY_REMAINS"
                if active_residuals
                else "NO_ACTIVE_RESIDUAL_INSOLVENCY"
            ),
            message=(
                "Disclosed residual insolvency remains active: "
                + ", ".join(item["residual_id"] for item in active_residuals)
                if active_residuals
                else "No active residual insolvency remains in the claim scope."
            ),
            blocking_for=["collective_resolution"],
            subject_refs=[item["residual_id"] for item in active_residuals],
            evidence_refs=_record_evidence(record, "residual_insolvency"),
        )
    )

    supporting_assessments = [
        item
        for item in record["validator_assessments"]
        if item["assessment_id"] in claim["validator_assessment_refs"]
        and item["decision"] == "supports"
        and item["independent_from_proposer"]
        and item["independent_from_implementers"]
        and item["validator_ref"] != proposer
        and item["validator_ref"] not in implementers
    ]
    supporting_validators = {
        item["validator_ref"] for item in supporting_assessments
    }
    required_validators = governance["required_independent_validator_count"]
    quorum = (
        len(set(governance["validators"])) >= required_validators
        and len(supporting_validators) >= required_validators
        and supporting_validators.issubset(set(governance["validators"]))
    )
    obligations.append(
        _obligation(
            obligation_id="O-VALIDATOR-QUORUM",
            dimension="validator_independence",
            status="pass" if quorum else "fail",
            code="VALIDATOR_QUORUM_MET" if quorum else "VALIDATOR_QUORUM_MISSING",
            message=(
                "The required independent governance validators supplied supporting assessments."
                if quorum
                else f"{len(supporting_validators)} supporting independent validator(s) are recorded; {required_validators} are required."
            ),
            blocking_for=["collective_resolution"],
            subject_refs=sorted(supporting_validators),
            evidence_refs=[
                evidence
                for item in supporting_assessments
                for evidence in item["evidence_refs"]
            ],
        )
    )

    unverified = [
        item["intervention_id"]
        for item in record["interventions"]
        if item["status"] != "verified"
    ]
    obligations.append(
        _obligation(
            obligation_id="O-INTERVENTION-VERIFICATION",
            dimension="intervention_verification",
            status="fail" if unverified else "pass",
            code=(
                "INTERVENTION_UNVERIFIED"
                if unverified
                else "INTERVENTIONS_VERIFIED"
            ),
            message=(
                "Completed activity is not outcome verification: "
                + ", ".join(unverified)
                if unverified
                else "All claim-scope interventions are independently verified."
            ),
            blocking_for=["collective_resolution"],
            subject_refs=unverified,
            evidence_refs=_record_evidence(record, "interventions"),
        )
    )

    unvalidated_conditions = [
        item["condition_id"]
        for item in record["structural_insolvency_conditions"]
        if item["condition_id"] in claim["condition_refs"]
        and item["status"] != "validated"
    ]
    obligations.append(
        _obligation(
            obligation_id="O-CONDITION-VALIDATION",
            dimension="structural_insolvency",
            status="fail" if unvalidated_conditions else "pass",
            code=(
                "CONDITION_UNVALIDATED"
                if unvalidated_conditions
                else "CONDITIONS_VALIDATED"
            ),
            message=(
                "Claim-scope structural-insolvency conditions remain below validated status."
                if unvalidated_conditions
                else "Every claim-scope structural-insolvency condition is validated."
            ),
            blocking_for=["collective_resolution"],
            subject_refs=unvalidated_conditions,
        )
    )

    failed_asserted_criteria = [
        name for name in RESOLUTION_CRITERIA if not criteria[name]
    ]
    obligations.append(
        _obligation(
            obligation_id="O-DECLARED-RESOLUTION-CRITERIA",
            dimension="collective_resolution",
            status="fail" if failed_asserted_criteria else "pass",
            code=(
                "DECLARED_CRITERIA_INCOMPLETE"
                if failed_asserted_criteria
                else "DECLARED_CRITERIA_COMPLETE"
            ),
            message=(
                "Unsatisfied declared criteria: " + ", ".join(failed_asserted_criteria)
                if failed_asserted_criteria
                else "Every declared collective-resolution criterion is true."
            ),
            blocking_for=["collective_resolution"],
            subject_refs=[claim["claim_id"]],
        )
    )

    trace = record["emgn_trace"]
    emgn_passes = (
        bool(trace["discrepancy_refs"])
        and bool(trace["retained_residue_refs"])
        and bool(trace["remediation_refs"])
        and trace["before_transition_regime_ref"]
        != trace["after_transition_regime_ref"]
        and trace["before_reachability_ref"] != trace["after_reachability_ref"]
    )
    obligations.append(
        _obligation(
            obligation_id="O-EMGN-ALIGNMENT",
            dimension="emgn_alignment",
            status="pass" if emgn_passes else "fail",
            code=(
                "EMGN_BRIDGE_PRESERVED"
                if emgn_passes
                else "EMGN_BRIDGE_INCOMPLETE"
            ),
            message=(
                "The record preserves discrepancy, retained residue, remediation, regime, and reachability references without inferring novelty."
                if emgn_passes
                else "The EMGN bridge is missing a required causal reference or distinct before/after resource."
            ),
            blocking_for=["record_conformance"],
            subject_refs=(
                trace["discrepancy_refs"]
                + trace["retained_residue_refs"]
                + trace["remediation_refs"]
                + [
                    trace["before_transition_regime_ref"],
                    trace["after_transition_regime_ref"],
                    trace["before_reachability_ref"],
                    trace["after_reachability_ref"],
                ]
            ),
        )
    )
    return obligations


def evaluate_record(
    record: dict[str, Any],
    *,
    schema: dict[str, Any],
    as_of: str | None = None,
) -> dict[str, Any]:
    """Evaluate a SICRP record without conferring validation or ratification."""

    record_copy = copy.deepcopy(record)
    input_digest = sha256_json(record_copy)
    basis_time = as_of or record_copy.get("provenance", {}).get("generated_at")
    if not basis_time:
        raise EvaluationError("as_of or provenance.generated_at is required")
    _parse_time(basis_time)

    obligations = _evaluate_record_obligations(record_copy, schema)
    record_blockers = [
        item
        for item in obligations
        if "record_conformance" in item["blocking_for"]
        and item["status"] != "pass"
    ]
    structural = next(
        (
            item
            for item in obligations
            if item["obligation_id"] == "O-STRUCTURAL-INSOLVENCY"
        ),
        None,
    )
    resolution_blockers = [
        item
        for item in obligations
        if "collective_resolution" in item["blocking_for"]
        and item["status"] != "pass"
    ]
    claim = record_copy.get("collective_resolution_claim", {})
    governance = record_copy.get("governance", {})
    trace = record_copy.get("emgn_trace", {})
    criteria = claim.get("criteria", {})

    assessment: dict[str, Any] = {
        "$schema": ASSESSMENT_SCHEMA,
        "evaluation_semantics": SEMANTICS_VERSION,
        "record_ref": record_copy.get("record_id", "urn:caeluviim:record:invalid"),
        "as_of": basis_time,
        "input_digest": input_digest,
        "deterministic": True,
        "record_conforms": not record_blockers,
        "structural_insolvency": {
            "verdict": (
                "supported"
                if structural and structural["status"] == "pass"
                else "not_supported"
            ),
            "condition_refs": sorted(
                item.get("condition_id", "")
                for item in record_copy.get(
                    "structural_insolvency_conditions", []
                )
            ),
        },
        "collective_resolution": {
            "verdict": (
                "requirements_satisfied"
                if not resolution_blockers
                else "not_established"
            ),
            "claim_ref": claim.get(
                "claim_id", "urn:caeluviim:claim:invalid"
            ),
            "passed_criteria": sorted(
                name for name, value in criteria.items() if value is True
            ),
            "failed_criteria": sorted(
                name for name, value in criteria.items() if value is False
            ),
            "blocking_obligation_codes": sorted(
                item["code"] for item in resolution_blockers
            ),
            "individual_improvement_sufficient": False,
            "ratification_conferred": False,
        },
        "emgn_alignment": {
            "status": (
                "supported"
                if any(
                    item["obligation_id"] == "O-EMGN-ALIGNMENT"
                    and item["status"] == "pass"
                    for item in obligations
                )
                else "not_supported"
            ),
            "discrepancy_refs": sorted(trace.get("discrepancy_refs", [])),
            "retained_residue_refs": sorted(
                trace.get("retained_residue_refs", [])
            ),
            "remediation_refs": sorted(trace.get("remediation_refs", [])),
            "before_transition_regime_ref": trace.get(
                "before_transition_regime_ref"
            ),
            "after_transition_regime_ref": trace.get(
                "after_transition_regime_ref"
            ),
            "before_reachability_ref": trace.get("before_reachability_ref"),
            "after_reachability_ref": trace.get("after_reachability_ref"),
            "novelty_witness_refs": sorted(
                trace.get("novelty_witness_refs", [])
            ),
            "novelty_validated": False,
        },
        "governance": {
            "input_record_status": record_copy.get("record_status", "proposed"),
            "input_governance_status": governance.get("status", "proposed"),
            "assessment_status": "provisional",
            "proposer_ref": governance.get(
                "proposer_id", "urn:caeluviim:agent:unknown"
            ),
            "validator_refs": sorted(governance.get("validators", [])),
            "required_independent_validator_count": governance.get(
                "required_independent_validator_count", 2
            ),
            "self_ratification_permitted": False,
            "ratification_conferred": False,
        },
        "obligations": obligations,
    }
    counts = Counter(item["status"] for item in obligations)
    assessment["summary"] = {
        "pass": counts["pass"],
        "fail": counts["fail"],
        "unknown": counts["unknown"],
        "error": counts["error"],
        "record_blocker_count": len(record_blockers),
        "collective_resolution_blocker_count": len(resolution_blockers),
    }
    digest_source = copy.deepcopy(assessment)
    digest = sha256_json(digest_source)
    assessment["assessment_id"] = (
        f"urn:caeluviim:assessment:sicrp-runtime:{digest}"
    )
    assessment["assessment_digest"] = digest
    return assessment


def verify_cross_format_alignment(
    record: dict[str, Any], rdf_path: Path | str
) -> dict[str, Any]:
    graph = Graph().parse(str(rdf_path), format="turtle")
    missing: list[dict[str, str]] = []
    for collection, (field, class_name) in COLLECTION_IDS.items():
        for item in record.get(collection, []):
            identifier = item[field]
            if (URIRef(identifier), RDF.type, SICRP[class_name]) not in graph:
                missing.append(
                    {
                        "json_ref": identifier,
                        "expected_rdf_type": str(SICRP[class_name]),
                    }
                )
    claim = record.get("collective_resolution_claim", {})
    if claim and (
        URIRef(claim["claim_id"]),
        RDF.type,
        SICRP.CollectiveResolutionClaim,
    ) not in graph:
        missing.append(
            {
                "json_ref": claim["claim_id"],
                "expected_rdf_type": str(SICRP.CollectiveResolutionClaim),
            }
        )

    traces = list(graph.subjects(RDF.type, SICRP.EMGNTrace))
    bridge_mismatches: list[str] = []
    if len(traces) != 1:
        bridge_mismatches.append(
            f"expected exactly one sicrp:EMGNTrace, found {len(traces)}"
        )
    else:
        trace_node = traces[0]
        json_trace = record["emgn_trace"]
        checks = [
            (
                SICRP.observedInstitutionalFailure,
                set(json_trace["discrepancy_refs"]),
            ),
            (
                SICRP.retainedStructuralResidue,
                set(json_trace["retained_residue_refs"]),
            ),
            (SICRP.collectiveRemediation, set(json_trace["remediation_refs"])),
            (
                SICRP.beforeAllocationRegime,
                {json_trace["before_transition_regime_ref"]},
            ),
            (
                SICRP.afterAllocationRegime,
                {json_trace["after_transition_regime_ref"]},
            ),
            (
                SICRP.beforeMaterialReachability,
                {json_trace["before_reachability_ref"]},
            ),
            (
                SICRP.afterMaterialReachability,
                {json_trace["after_reachability_ref"]},
            ),
            (SICRP.noveltyWitness, set(json_trace["novelty_witness_refs"])),
        ]
        for predicate, expected in checks:
            actual = {str(value) for value in graph.objects(trace_node, predicate)}
            if actual != expected:
                bridge_mismatches.append(
                    f"{predicate}: expected {sorted(expected)}, found {sorted(actual)}"
                )
    return {
        "conforms": not missing and not bridge_mismatches,
        "rdf_triples": len(graph),
        "missing_typed_entities": missing,
        "emgn_bridge_mismatches": bridge_mismatches,
    }


def load_json(path: Path | str) -> dict[str, Any]:
    try:
        return json.loads(Path(path).read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvaluationError(f"cannot load JSON from {path}: {error}") from error
