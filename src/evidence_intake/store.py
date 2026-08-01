from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import fcntl
from pyshacl import validate as shacl_validate
from rdflib import Dataset, Graph, Literal, Namespace, RDF, URIRef, XSD

from .evaluator import (
    EvaluationError,
    evaluate_manifest,
    failure_code_counts,
    load_json,
    validate_json_document,
    validate_rdf_manifest,
    verify_cross_format_alignment,
)

INTAKE = Namespace("https://caeluviim.org/ontology/evidence-intake#")


class GraphCollisionError(EvaluationError):
    pass


def _term(value: Any) -> dict[str, Any]:
    if value is None:
        return {"type": "unbound", "value": None}
    if isinstance(value, URIRef):
        return {"type": "uri", "value": str(value)}
    result = {"type": "literal", "value": value.toPython()}
    datatype = str(value.datatype) if getattr(value, "datatype", None) else None
    language = getattr(value, "language", None)
    if datatype:
        result["datatype"] = datatype
    if language:
        result["language"] = language
    return result


class LocalEvidenceIntakeStore:
    """Atomic append-only store with hard quarantine/asserted separation."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.lock_path = self.path.with_name(self.path.name + ".lock")

    @contextmanager
    def _lock(self, *, exclusive: bool) -> Iterator[None]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            with os.fdopen(descriptor, "r+") as handle:
                fcntl.flock(
                    handle.fileno(),
                    fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH,
                )
                yield
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            pass

    def _load(self) -> Dataset:
        dataset = Dataset(default_union=True)
        if self.path.exists() and self.path.stat().st_size:
            dataset.parse(self.path, format="trig")
        return dataset

    def _write_atomic(self, dataset: Dataset) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=self.path.name + ".",
            suffix=".tmp",
            dir=self.path.parent,
        )
        temporary = Path(temporary_name)
        try:
            os.close(descriptor)
            dataset.serialize(destination=str(temporary), format="trig")
            with temporary.open("rb") as handle:
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
            directory_fd = os.open(self.path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def graph_uris(base_graph_uri: str, assessment_digest: str) -> dict[str, URIRef]:
        base = base_graph_uri.rstrip("/")
        return {
            "intake": URIRef(base + "/intake"),
            "quarantine": URIRef(base + "/quarantine"),
            "asserted": URIRef(base + "/asserted"),
            "metadata": URIRef(base + "/metadata"),
            "assessment": URIRef(
                base + "/assessment/" + assessment_digest
            ),
        }

    @staticmethod
    def _add_claim_result(
        graph: Graph,
        claim: dict[str, Any],
        normalized_text: str,
    ) -> None:
        claim_ref = URIRef(claim["claim_ref"])
        graph.add((claim_ref, RDF.type, INTAKE.ExtractedClaim))
        graph.add(
            (
                claim_ref,
                INTAKE.normalizedClaimText,
                Literal(normalized_text),
            )
        )
        graph.add(
            (
                claim_ref,
                INTAKE.recordedClaimState,
                Literal(claim["recorded_state"]),
            )
        )
        graph.add(
            (
                claim_ref,
                INTAKE.supportState,
                Literal(claim["support_state"]),
            )
        )
        graph.add(
            (
                claim_ref,
                INTAKE.evaluatedClaimState,
                Literal(claim["evaluated_state"]),
            )
        )
        graph.add(
            (
                claim_ref,
                INTAKE.releaseAllowed,
                Literal(claim["release_allowed"]),
            )
        )

    @staticmethod
    def _add_assessment_projection(
        graph: Graph,
        assessment: dict[str, Any],
    ) -> None:
        assessment_ref = URIRef(assessment["assessment_id"])
        graph.add(
            (
                assessment_ref,
                RDF.type,
                INTAKE.EvidenceIntakeAssessment,
            )
        )
        graph.add(
            (
                assessment_ref,
                INTAKE.assessesManifest,
                URIRef(assessment["manifest_ref"]),
            )
        )
        graph.add(
            (
                assessment_ref,
                INTAKE.manifestDigest,
                Literal(assessment["manifest_digest"]),
            )
        )
        graph.add(
            (
                assessment_ref,
                INTAKE.assessmentDigest,
                Literal(assessment["assessment_digest"]),
            )
        )
        graph.add(
            (
                assessment_ref,
                INTAKE.assessmentPayload,
                Literal(
                    json.dumps(
                        assessment,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    datatype=RDF.JSON,
                ),
            )
        )
        for position, failure in enumerate(assessment["failure_facts"]):
            failure_ref = URIRef(
                assessment["assessment_id"] + f"/failure/{position:04d}"
            )
            graph.add(
                (
                    assessment_ref,
                    INTAKE.hasFailureFact,
                    failure_ref,
                )
            )
            graph.add((failure_ref, RDF.type, INTAKE.FailureFact))
            graph.add(
                (
                    failure_ref,
                    INTAKE.failureCode,
                    Literal(failure["code"]),
                )
            )
            graph.add(
                (
                    failure_ref,
                    INTAKE.failureClaim,
                    URIRef(failure["claim_ref"]),
                )
            )
            for related_ref in failure["related_refs"]:
                if related_ref.startswith(("urn:", "https://", "http://")):
                    graph.add(
                        (
                            failure_ref,
                            INTAKE.relatedRef,
                            URIRef(related_ref),
                        )
                    )

    @staticmethod
    def _add_eligible_assertion(
        graph: Graph,
        assertion: dict[str, Any],
    ) -> None:
        assertion_ref = URIRef(assertion["assertion_id"])
        graph.add(
            (
                assertion_ref,
                RDF.type,
                INTAKE.EligibleSICRPAssertion,
            )
        )
        graph.add(
            (
                assertion_ref,
                INTAKE.eligibleClaim,
                URIRef(assertion["claim_ref"]),
            )
        )
        graph.add(
            (
                assertion_ref,
                INTAKE.eligibleFromRequest,
                URIRef(assertion["request_ref"]),
            )
        )
        graph.add(
            (
                assertion_ref,
                INTAKE.targetField,
                Literal(assertion["target_field"]),
            )
        )
        graph.add(
            (
                assertion_ref,
                INTAKE.assertionText,
                Literal(assertion["assertion_text"]),
            )
        )
        graph.add(
            (
                assertion_ref,
                INTAKE.targetsSICRPRecord,
                URIRef(assertion["target_record_ref"]),
            )
        )
        graph.add(
            (
                assertion_ref,
                INTAKE.targetsSICRPEntity,
                URIRef(assertion["target_entity_ref"]),
            )
        )

    def ingest(
        self,
        *,
        manifest_path: Path | str,
        rdf_path: Path | str,
        base_graph_uri: str,
        project_root: Path | str,
        manifest_schema_path: Path | str,
        assessment_schema_path: Path | str,
        shapes_path: Path | str,
        ontology_path: Path | str,
        assessment_shapes_path: Path | str,
    ) -> dict[str, Any]:
        if not base_graph_uri.startswith(("urn:", "https://", "http://")):
            raise EvaluationError("base_graph_uri must be an absolute URI")
        manifest = load_json(manifest_path)
        manifest_schema = load_json(manifest_schema_path)
        assessment_schema = load_json(assessment_schema_path)
        manifest_validation = validate_json_document(
            manifest,
            manifest_schema,
        )
        if not manifest_validation["conforms"]:
            raise EvaluationError(
                "JSON manifest validation failed: "
                + "; ".join(
                    f"{item['path']}: {item['message']}"
                    for item in manifest_validation["errors"]
                )
            )
        rdf_validation = validate_rdf_manifest(
            rdf_path,
            shapes_path=shapes_path,
            ontology_path=ontology_path,
        )
        if not rdf_validation["conforms"]:
            raise EvaluationError(
                "RDF SHACL validation failed: "
                + rdf_validation["report_text"]
            )
        alignment = verify_cross_format_alignment(manifest, rdf_path)
        if not alignment["conforms"]:
            raise EvaluationError(
                "JSON/RDF alignment failed: "
                + json.dumps(alignment, sort_keys=True)
            )
        assessment = evaluate_manifest(
            manifest,
            schema=manifest_schema,
            project_root=project_root,
        )
        assessment_validation = validate_json_document(
            assessment,
            assessment_schema,
        )
        if not assessment_validation["conforms"]:
            raise EvaluationError(
                "generated assessment does not conform: "
                + "; ".join(
                    f"{item['path']}: {item['message']}"
                    for item in assessment_validation["errors"]
                )
            )

        source_graph = Graph().parse(str(rdf_path), format="turtle")
        graph_uris = self.graph_uris(
            base_graph_uri,
            assessment["assessment_digest"],
        )
        claims = {
            item["claim_id"]: item
            for item in manifest["extracted_claims"]
        }

        with self._lock(exclusive=True):
            dataset = self._load()
            metadata = dataset.graph(graph_uris["metadata"])
            base_ref = URIRef(base_graph_uri)
            existing_digest = metadata.value(
                base_ref,
                INTAKE.manifestDigest,
            )
            if existing_digest is not None:
                if str(existing_digest) == assessment["manifest_digest"]:
                    return {
                        "status": "already_present",
                        "store": str(self.path),
                        "base_graph_uri": base_graph_uri,
                        "manifest_ref": assessment["manifest_ref"],
                        "manifest_digest": assessment["manifest_digest"],
                        "assessment_digest": assessment["assessment_digest"],
                        "released_claim_count": len(
                            assessment["released_claim_refs"]
                        ),
                        "quarantined_claim_count": len(
                            assessment["quarantined_claim_refs"]
                        ),
                        "graphs_disjoint": True,
                    }
                raise GraphCollisionError(
                    "graph set already exists with different content: "
                    + base_graph_uri
                )
            if any(len(dataset.graph(ref)) for ref in graph_uris.values()):
                raise GraphCollisionError(
                    "one or more target graph URIs already contain data"
                )

            intake_graph = dataset.graph(graph_uris["intake"])
            for triple in source_graph:
                intake_graph.add(triple)

            asserted_graph = dataset.graph(graph_uris["asserted"])
            quarantine_graph = dataset.graph(graph_uris["quarantine"])
            assessment_graph = dataset.graph(graph_uris["assessment"])

            for claim_result in assessment["claim_results"]:
                claim_ref = claim_result["claim_ref"]
                target = (
                    asserted_graph
                    if claim_result["evaluated_state"] == "released"
                    else quarantine_graph
                )
                self._add_claim_result(
                    target,
                    claim_result,
                    claims[claim_ref]["normalized_text"],
                )
                predicate = (
                    INTAKE.releasedClaim
                    if claim_result["evaluated_state"] == "released"
                    else INTAKE.quarantinedClaim
                )
                assessment_graph.add(
                    (
                        URIRef(assessment["assessment_id"]),
                        predicate,
                        URIRef(claim_ref),
                    )
                )

            for assertion in assessment["eligible_sicrp_assertions"]:
                self._add_eligible_assertion(asserted_graph, assertion)
                assessment_graph.add(
                    (
                        URIRef(assessment["assessment_id"]),
                        INTAKE.hasEligibleAssertion,
                        URIRef(assertion["assertion_id"]),
                    )
                )

            self._add_assessment_projection(
                assessment_graph,
                assessment,
            )

            graph_set_ref = URIRef(base_graph_uri + "/graph-set")
            metadata.add(
                (
                    graph_set_ref,
                    RDF.type,
                    INTAKE.IngestedGraphSet,
                )
            )
            metadata.add(
                (
                    graph_set_ref,
                    INTAKE.intakeGraph,
                    graph_uris["intake"],
                )
            )
            metadata.add(
                (
                    graph_set_ref,
                    INTAKE.quarantineGraph,
                    graph_uris["quarantine"],
                )
            )
            metadata.add(
                (
                    graph_set_ref,
                    INTAKE.assertedGraph,
                    graph_uris["asserted"],
                )
            )
            metadata.add(
                (
                    graph_set_ref,
                    INTAKE.graphsDisjoint,
                    Literal(True),
                )
            )
            metadata.add(
                (
                    base_ref,
                    INTAKE.manifestDigest,
                    Literal(assessment["manifest_digest"]),
                )
            )
            metadata.add(
                (
                    base_ref,
                    INTAKE.assessmentDigest,
                    Literal(assessment["assessment_digest"]),
                )
            )

            asserted_triples = set(asserted_graph)
            quarantine_triples = set(quarantine_graph)
            asserted_subjects = {
                subject
                for subject, _, _ in asserted_graph.triples(
                    (None, INTAKE.evaluatedClaimState, Literal("released"))
                )
            }
            quarantine_subjects = {
                subject
                for subject, _, _ in quarantine_graph.triples(
                    (
                        None,
                        INTAKE.evaluatedClaimState,
                        Literal("quarantined"),
                    )
                )
            }
            if not asserted_triples.isdisjoint(quarantine_triples):
                raise EvaluationError(
                    "G_quarantine and G_asserted share one or more triples"
                )
            if not asserted_subjects.isdisjoint(quarantine_subjects):
                raise EvaluationError(
                    "a claim subject occurs in both quarantine and asserted graphs"
                )

            generated = Graph()
            for graph in (
                asserted_graph,
                quarantine_graph,
                assessment_graph,
                metadata,
            ):
                for triple in graph:
                    generated.add(triple)
            assessment_shapes = Graph().parse(
                str(assessment_shapes_path),
                format="turtle",
            )
            ontology = Graph().parse(
                str(ontology_path),
                format="turtle",
            )
            conforms, _, report = shacl_validate(
                data_graph=generated,
                shacl_graph=assessment_shapes,
                ont_graph=ontology,
                inference="rdfs",
                advanced=True,
            )
            if not conforms:
                raise EvaluationError(
                    "generated graph projections do not conform: "
                    + str(report)
                )
            self._write_atomic(dataset)

        return {
            "status": "ingested",
            "store": str(self.path),
            "base_graph_uri": base_graph_uri,
            "graph_uris": {
                role: str(reference)
                for role, reference in graph_uris.items()
            },
            "manifest_ref": assessment["manifest_ref"],
            "manifest_digest": assessment["manifest_digest"],
            "assessment_digest": assessment["assessment_digest"],
            "intake_triples": len(source_graph),
            "asserted_triples": len(asserted_graph),
            "quarantine_triples": len(quarantine_graph),
            "released_claim_count": len(assessment["released_claim_refs"]),
            "quarantined_claim_count": len(
                assessment["quarantined_claim_refs"]
            ),
            "eligible_sicrp_assertion_count": len(
                assessment["eligible_sicrp_assertions"]
            ),
            "failure_code_counts": failure_code_counts(assessment),
            "graphs_disjoint": True,
            "sicrp_validation_conferred": False,
            "ratification_conferred": False,
        }

    def inspect(self) -> dict[str, Any]:
        with self._lock(exclusive=False):
            dataset = self._load()
            default_identifier = dataset.default_graph.identifier
            graphs = [
                {
                    "graph_uri": str(graph.identifier),
                    "triple_count": len(graph),
                }
                for graph in dataset.graphs()
                if graph.identifier != default_identifier and len(graph)
            ]
        graphs.sort(key=lambda item: item["graph_uri"])
        return {
            "store": str(self.path),
            "exists": self.path.exists(),
            "named_graph_count": len(graphs),
            "total_named_graph_triples": sum(
                item["triple_count"] for item in graphs
            ),
            "graphs": graphs,
        }

    def query(self, sparql: str) -> dict[str, Any]:
        with self._lock(exclusive=False):
            dataset = self._load()
            result = dataset.query(sparql)
            result_type = str(result.type)
            if result_type == "ASK":
                return {"type": "ASK", "boolean": bool(result.askAnswer)}
            if result_type != "SELECT":
                raise EvaluationError(
                    "only SELECT and ASK queries are permitted"
                )
            variables = [str(item) for item in result.vars]
            rows = []
            for row in result:
                values = row.asdict()
                rows.append(
                    {
                        variable: _term(values.get(variable))
                        for variable in variables
                    }
                )
        return {"type": "SELECT", "variables": variables, "rows": rows}
