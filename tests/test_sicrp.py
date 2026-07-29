import copy
import hashlib
import json
import unittest
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from pyshacl import validate
from rdflib import Graph, Namespace, RDF

ROOT = Path(__file__).resolve().parents[1]
SICRP = Namespace("https://caeluviim.org/ontology/sicrp#")
EMGN = Namespace("https://caeluviim.org/ontology/emgn#")


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def ids(items, field):
    values = [item[field] for item in items]
    if len(values) != len(set(values)):
        raise AssertionError(f"duplicate identifiers in {field}")
    return set(values)


def require_refs(items, field, targets):
    for item in items:
        values = item.get(field, [])
        if isinstance(values, str):
            values = [values]
        if values is None:
            continue
        missing = set(values) - targets
        if missing:
            raise AssertionError(f"{field} has unresolved references: {sorted(missing)}")


def verify_reference_integrity(record):
    maps = {
        "condition": ids(record["structural_insolvency_conditions"], "condition_id"),
        "mechanism": ids(record["producing_mechanisms"], "mechanism_id"),
        "constituency": ids(record["affected_constituencies"], "constituency_id"),
        "deficit": ids(record["material_deficits"], "deficit_id"),
        "obligation": ids(record["institutional_obligations"], "obligation_id"),
        "flow": ids(record["resource_flows"], "flow_id"),
        "exclusion": ids(record["exclusion_events"], "exclusion_id"),
        "capacity": ids(record["capacity_evidence"], "capacity_id"),
        "right": ids(record["intervention_rights"], "right_id"),
        "intervention": ids(record["interventions"], "intervention_id"),
        "plan": ids(record["collective_resolution_plans"], "plan_id"),
        "metric": ids(record["resolution_metrics"], "metric_id"),
        "observation": ids(record["resolution_observations"], "observation_id"),
        "residual": ids(record["residual_insolvency"], "residual_id"),
        "effect": ids(record["distributional_effects"], "effect_id"),
        "assessment": ids(record["validator_assessments"], "assessment_id"),
        "claim": {record["collective_resolution_claim"]["claim_id"]},
    }
    all_ids = [value for group in maps.values() for value in group]
    if len(all_ids) != len(set(all_ids)):
        raise AssertionError("identifiers must be globally unique")

    rules = [
        ("structural_insolvency_conditions", "mechanism_refs", "mechanism"),
        ("structural_insolvency_conditions", "constituency_refs", "constituency"),
        ("structural_insolvency_conditions", "material_deficit_refs", "deficit"),
        ("structural_insolvency_conditions", "obligation_refs", "obligation"),
        ("structural_insolvency_conditions", "resource_flow_refs", "flow"),
        ("structural_insolvency_conditions", "exclusion_event_refs", "exclusion"),
        ("structural_insolvency_conditions", "capacity_evidence_refs", "capacity"),
        ("producing_mechanisms", "affected_flow_refs", "flow"),
        ("producing_mechanisms", "affected_constituency_refs", "constituency"),
        ("producing_mechanisms", "material_deficit_refs", "deficit"),
        ("material_deficits", "constituency_ref", "constituency"),
        ("material_deficits", "obligation_ref", "obligation"),
        ("material_deficits", "mechanism_refs", "mechanism"),
        ("material_deficits", "resource_flow_refs", "flow"),
        ("institutional_obligations", "beneficiary_constituency_ref", "constituency"),
        ("resource_flows", "constrained_by_mechanism_refs", "mechanism"),
        ("exclusion_events", "mechanism_ref", "mechanism"),
        ("exclusion_events", "constituency_ref", "constituency"),
        ("exclusion_events", "material_deficit_ref", "deficit"),
        ("capacity_evidence", "obligation_refs", "obligation"),
        ("intervention_rights", "holder_constituency_ref", "constituency"),
        ("intervention_rights", "target_mechanism_refs", "mechanism"),
        ("interventions", "exercised_right_refs", "right"),
        ("interventions", "target_mechanism_refs", "mechanism"),
        ("interventions", "target_exclusion_refs", "exclusion"),
        ("interventions", "participant_constituency_refs", "constituency"),
        ("interventions", "input_flow_refs", "flow"),
        ("interventions", "output_flow_refs", "flow"),
        ("collective_resolution_plans", "affected_constituency_refs", "constituency"),
        ("collective_resolution_plans", "target_condition_refs", "condition"),
        ("collective_resolution_plans", "target_mechanism_refs", "mechanism"),
        ("collective_resolution_plans", "intervention_refs", "intervention"),
        ("collective_resolution_plans", "resolution_metric_refs", "metric"),
        ("resolution_metrics", "constituency_ref", "constituency"),
        ("resolution_metrics", "obligation_ref", "obligation"),
        ("resolution_observations", "metric_ref", "metric"),
        ("resolution_observations", "constituency_ref", "constituency"),
        ("residual_insolvency", "condition_ref", "condition"),
        ("residual_insolvency", "affected_constituency_refs", "constituency"),
        ("distributional_effects", "metric_ref", "metric"),
        ("distributional_effects", "constituency_ref", "constituency"),
        ("distributional_effects", "initiating_observation_ref", "observation"),
        ("distributional_effects", "non_initiating_observation_refs", "observation"),
        ("validator_assessments", "assessed_ref", "claim"),
    ]
    for collection, field, target in rules:
        require_refs(record[collection], field, maps[target])

    claim = record["collective_resolution_claim"]
    claim_rules = [
        ("affected_constituency_refs", "constituency"),
        ("condition_refs", "condition"),
        ("resolution_plan_refs", "plan"),
        ("before_observation_refs", "observation"),
        ("after_observation_refs", "observation"),
        ("distributional_effect_refs", "effect"),
        ("residual_insolvency_refs", "residual"),
        ("validator_assessment_refs", "assessment"),
    ]
    for field, target in claim_rules:
        require_refs([claim], field, maps[target])

    require_refs(
        [{"remediation_refs": record["emgn_trace"]["remediation_refs"]}],
        "remediation_refs",
        maps["intervention"],
    )
    return maps


def verify_measurements(record):
    obligations = {
        item["obligation_id"]: item for item in record["institutional_obligations"]
    }
    metrics = {item["metric_id"]: item for item in record["resolution_metrics"]}
    for deficit in record["material_deficits"]:
        expected = max(0, deficit["required_quantity"] - deficit["observed_quantity"])
        if abs(deficit["shortfall_quantity"] - expected) > 1e-9:
            raise AssertionError("material deficit arithmetic is inconsistent")
        obligation = obligations[deficit["obligation_ref"]]
        if deficit["resource_type"] != obligation["resource_type"]:
            raise AssertionError("deficit and obligation resource types differ")
        if deficit["unit"] != obligation["unit"]:
            raise AssertionError("deficit and obligation units differ")
        if deficit["required_quantity"] != obligation["threshold_value"]:
            raise AssertionError("deficit requirement and obligation threshold differ")

    window_fields = [
        ("material_deficits", "measurement_window"),
        ("institutional_obligations", "evaluation_period"),
        ("resource_flows", "time_window"),
        ("capacity_evidence", "time_window"),
        ("resolution_observations", "measurement_window"),
    ]
    for collection, field in window_fields:
        for item in record[collection]:
            window = item[field]
            if parse_time(window["start"]) >= parse_time(window["end"]):
                raise AssertionError(f"invalid time window in {collection}")
    for intervention in record["interventions"]:
        if parse_time(intervention["start_at"]) >= parse_time(intervention["end_at"]):
            raise AssertionError("invalid intervention interval")

    for observation in record["resolution_observations"]:
        metric = metrics[observation["metric_ref"]]
        if observation["unit"] != metric["unit"]:
            raise AssertionError("observation and metric units differ")
        value = observation["observed_value"]
        threshold = metric["threshold_value"]
        comparison = metric["comparison"]
        expected = {
            "greater_than_or_equal": value >= threshold,
            "less_than_or_equal": value <= threshold,
            "equal": value == threshold,
            "boolean_true": bool(value) is True,
        }[comparison]
        if observation["threshold_met"] is not expected:
            raise AssertionError("threshold_met does not match metric decision rule")


def verify_independence(record):
    governance = record["governance"]
    proposer = governance["proposer_id"]
    implementers = {
        actor
        for intervention in record["interventions"]
        for actor in intervention["responsible_actor_refs"]
    }
    if proposer in governance["validators"] or governance["proposer_is_validator"]:
        raise AssertionError("the proposer may not validate")
    for observation in record["resolution_observations"]:
        assessor = observation["assessor_ref"]
        if assessor == proposer or assessor in implementers:
            raise AssertionError("resolution observation is not independent")
    for assessment in record["validator_assessments"]:
        validator = assessment["validator_ref"]
        if validator == proposer or validator in implementers:
            raise AssertionError("validator assessment is not independent")
        if not assessment["independent_from_proposer"]:
            raise AssertionError("proposer independence must be recorded")
        if not assessment["independent_from_implementers"]:
            raise AssertionError("implementer independence must be recorded")


def verify_collective_resolution_boundary(record):
    claim = record["collective_resolution_claim"]
    if claim["individual_improvement_only"]:
        raise AssertionError("individual improvement cannot establish collective resolution")
    observations = {
        item["observation_id"]: item for item in record["resolution_observations"]
    }
    for effect in record["distributional_effects"]:
        initiating = observations[effect["initiating_observation_ref"]]
        if initiating["population_scope"] != "initiating_claimant":
            raise AssertionError("initiating observation has the wrong population scope")
        if effect["coverage_count"] < 2:
            raise AssertionError("distributional coverage must include more than one claimant")
        for reference in effect["non_initiating_observation_refs"]:
            if observations[reference]["population_scope"] != "non_initiating_members":
                raise AssertionError("generalization lacks non-initiating population evidence")
        if not effect["generalized_beyond_initiating_claimant"]:
            raise AssertionError("distributional effect is not population-generalized")
        if not effect["non_regression_passed"]:
            raise AssertionError("distributional effect regresses")

    residuals = {
        item["residual_id"]: item for item in record["residual_insolvency"]
    }
    for reference in claim["residual_insolvency_refs"]:
        if not residuals[reference]["disclosed"]:
            raise AssertionError("claim contains undisclosed residual insolvency")

    if claim["status"] == "validated":
        if not all(claim["criteria"].values()):
            raise AssertionError("validated claim has an unsatisfied decisive criterion")
        plans = {item["plan_id"]: item for item in record["collective_resolution_plans"]}
        interventions = {
            item["intervention_id"]: item for item in record["interventions"]
        }
        for plan_ref in claim["resolution_plan_refs"]:
            for intervention_ref in plans[plan_ref]["intervention_refs"]:
                if interventions[intervention_ref]["status"] != "verified":
                    raise AssertionError("validated claim uses an unverified intervention")
        governance = record["governance"]
        validators = set(governance["validators"])
        if governance["status"] != "ratified" or not governance["ratification_claimed"]:
            raise AssertionError("validated claim lacks ratified governance")
        if len(validators) < governance["required_independent_validator_count"]:
            raise AssertionError("validated claim lacks independent validators")
        supporting = {
            item["validator_ref"]
            for item in record["validator_assessments"]
            if item["assessment_id"] in claim["validator_assessment_refs"]
            and item["decision"] == "supports"
            and item["independent_from_proposer"]
            and item["independent_from_implementers"]
        }
        if len(supporting) < governance["required_independent_validator_count"]:
            raise AssertionError("validated claim lacks supporting independent assessments")
        if not supporting.issubset(validators):
            raise AssertionError("supporting assessors are not governance validators")


class TestSICRPArtifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record_schema = json.loads(
            (ROOT / "schemas/sicrp-record.schema.json").read_text()
        )
        cls.status_schema = json.loads(
            (ROOT / "schemas/sicrp-module-status.schema.json").read_text()
        )
        cls.record = json.loads(
            (ROOT / "examples/sicrp-record.valid.json").read_text()
        )
        cls.status = json.loads(
            (ROOT / "governance/sicrp-v0.1.0.status.json").read_text()
        )
        cls.validator = Draft202012Validator(
            cls.record_schema, format_checker=FormatChecker()
        )
        cls.status_validator = Draft202012Validator(
            cls.status_schema, format_checker=FormatChecker()
        )

    def test_schemas_are_valid_draft_2020_12(self):
        Draft202012Validator.check_schema(self.record_schema)
        Draft202012Validator.check_schema(self.status_schema)

    def test_json_record_conforms(self):
        errors = sorted(
            self.validator.iter_errors(self.record), key=lambda error: list(error.path)
        )
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def test_module_status_conforms_and_is_not_self_ratified(self):
        errors = sorted(
            self.status_validator.iter_errors(self.status),
            key=lambda error: list(error.path),
        )
        self.assertEqual([], errors, "\n".join(error.message for error in errors))
        self.assertEqual("implemented", self.status["implementation_status"])
        self.assertEqual("proposed", self.status["governance_status"])
        self.assertFalse(self.status["proposer_may_validate"])
        self.assertFalse(self.status["ratification_claimed"])
        self.assertNotIn(self.status["proposer_id"], self.status["independent_validators"])

    def test_artifact_manifest_hashes(self):
        manifest = self.status["artifact_manifest"]
        self.assertGreaterEqual(len(manifest), 8)
        for item in manifest:
            path = ROOT / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(item["sha256"], digest, item["path"])

    def test_reference_integrity(self):
        maps = verify_reference_integrity(self.record)
        self.assertEqual(1, len(maps["claim"]))

    def test_measurement_arithmetic_units_and_time(self):
        verify_measurements(self.record)

    def test_collective_resolution_boundary(self):
        verify_collective_resolution_boundary(self.record)
        claim = self.record["collective_resolution_claim"]
        self.assertEqual("supported", claim["status"])
        self.assertFalse(claim["criteria"]["coverage_complete"])
        self.assertFalse(self.record["governance"]["ratification_claimed"])

    def test_population_generalization_is_witnessed(self):
        observations = {
            item["observation_id"]: item
            for item in self.record["resolution_observations"]
        }
        effect = self.record["distributional_effects"][0]
        self.assertEqual(
            "initiating_claimant",
            observations[effect["initiating_observation_ref"]]["population_scope"],
        )
        self.assertTrue(
            all(
                observations[reference]["population_scope"]
                == "non_initiating_members"
                for reference in effect["non_initiating_observation_refs"]
            )
        )
        self.assertTrue(effect["generalized_beyond_initiating_claimant"])

    def test_independent_measurement_and_validation(self):
        verify_independence(self.record)

    def test_emgn_bridge_is_explicit_without_false_novelty(self):
        trace = self.record["emgn_trace"]
        self.assertTrue(trace["discrepancy_refs"])
        self.assertTrue(trace["retained_residue_refs"])
        self.assertTrue(trace["remediation_refs"])
        self.assertNotEqual(
            trace["before_transition_regime_ref"],
            trace["after_transition_regime_ref"],
        )
        self.assertNotEqual(
            trace["before_reachability_ref"],
            trace["after_reachability_ref"],
        )
        self.assertEqual([], trace["novelty_witness_refs"])
        self.assertEqual("supported", trace["alignment_status"])

    def test_negative_validated_claim_with_incomplete_coverage_fails_schema(self):
        candidate = copy.deepcopy(self.record)
        candidate["collective_resolution_claim"]["status"] = "validated"
        errors = list(self.validator.iter_errors(candidate))
        self.assertTrue(errors)

    def test_negative_ratification_with_one_validator_fails_schema(self):
        candidate = copy.deepcopy(self.record)
        candidate["governance"]["status"] = "ratified"
        candidate["governance"]["ratification_claimed"] = True
        errors = list(self.validator.iter_errors(candidate))
        self.assertTrue(errors)

    def test_negative_individual_improvement_only_fails_schema(self):
        candidate = copy.deepcopy(self.record)
        candidate["collective_resolution_claim"]["individual_improvement_only"] = True
        errors = list(self.validator.iter_errors(candidate))
        self.assertTrue(errors)

    def test_negative_broken_reference_is_rejected(self):
        candidate = copy.deepcopy(self.record)
        candidate["interventions"][0]["target_mechanism_refs"][0] = (
            "urn:caeluviim:mechanism:missing"
        )
        with self.assertRaises(AssertionError):
            verify_reference_integrity(candidate)

    def test_negative_arithmetic_mismatch_is_rejected(self):
        candidate = copy.deepcopy(self.record)
        candidate["material_deficits"][0]["shortfall_quantity"] = 59
        with self.assertRaises(AssertionError):
            verify_measurements(candidate)

    def test_negative_proposer_or_implementer_assessment_is_rejected(self):
        candidate = copy.deepcopy(self.record)
        candidate["validator_assessments"][0]["validator_ref"] = candidate[
            "governance"
        ]["proposer_id"]
        with self.assertRaises(AssertionError):
            verify_independence(candidate)
        candidate = copy.deepcopy(self.record)
        candidate["resolution_observations"][0]["assessor_ref"] = candidate[
            "interventions"
        ][0]["responsible_actor_refs"][0]
        with self.assertRaises(AssertionError):
            verify_independence(candidate)

    def test_rdf_ontology_shapes_and_example_parse(self):
        ontology = Graph().parse(ROOT / "ontology/sicrp.ttl", format="turtle")
        shapes = Graph().parse(ROOT / "shapes/sicrp.shacl.ttl", format="turtle")
        data = Graph().parse(ROOT / "examples/sicrp-record.valid.ttl", format="turtle")
        self.assertGreater(len(ontology), 0)
        self.assertGreater(len(shapes), 0)
        self.assertGreater(len(data), 0)

    def test_rdf_contains_all_normative_core_classes(self):
        graph = Graph().parse(ROOT / "examples/sicrp-record.valid.ttl", format="turtle")
        names = [
            "StructuralInsolvencyCondition",
            "ProducingMechanism",
            "AffectedConstituency",
            "MaterialDeficit",
            "InstitutionalObligation",
            "ResourceFlow",
            "ExclusionEvent",
            "Intervention",
            "CollectiveResolutionPlan",
            "ResolutionMetric",
            "ResolutionObservation",
            "ResidualInsolvency",
            "DistributionalEffect",
            "ValidatorAssessment",
        ]
        for name in names:
            self.assertTrue(any(graph.subjects(RDF.type, SICRP[name])), name)

    def test_rdf_emgn_bridge_types_and_governance_boundary(self):
        graph = Graph().parse(ROOT / "examples/sicrp-record.valid.ttl", format="turtle")
        trace = next(graph.subjects(RDF.type, SICRP.EMGNTrace))
        self.assertTrue(
            any(graph.objects(trace, SICRP.observedInstitutionalFailure))
        )
        self.assertTrue(any(graph.objects(trace, SICRP.retainedStructuralResidue)))
        self.assertTrue(any(graph.objects(trace, SICRP.collectiveRemediation)))
        self.assertFalse(any(graph.objects(trace, SICRP.noveltyWitness)))
        governance = next(graph.subjects(RDF.type, SICRP.GovernanceRecord))
        proposers = set(graph.objects(governance, SICRP.proposer))
        validators = set(graph.objects(governance, SICRP.validator))
        self.assertEqual(1, len(proposers))
        self.assertTrue(proposers.isdisjoint(validators))
        self.assertIs(
            graph.value(governance, SICRP.ratificationClaimed).toPython(), False
        )

    def test_full_shacl_validation(self):
        conforms, _, report = validate(
            data_graph=str(ROOT / "examples/sicrp-record.valid.ttl"),
            shacl_graph=str(ROOT / "shapes/sicrp.shacl.ttl"),
            ont_graph=str(ROOT / "ontology/sicrp.ttl"),
            inference="rdfs",
            advanced=True,
        )
        self.assertTrue(conforms, report)


if __name__ == "__main__":
    unittest.main()
