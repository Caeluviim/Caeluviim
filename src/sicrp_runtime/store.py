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
    evaluate_record,
    load_json,
    validate_json_record,
    validate_rdf_record,
    verify_cross_format_alignment,
)

RUNTIME = Namespace("https://caeluviim.org/ontology/sicrp/runtime#")
PROV = Namespace("http://www.w3.org/ns/prov#")


class GraphCollisionError(EvaluationError):
    pass


def _term(value: Any) -> dict[str, Any]:
    if value is None:
        return {"type": "unbound", "value": None}
    if isinstance(value, URIRef):
        return {"type": "uri", "value": str(value)}
    datatype = str(value.datatype) if getattr(value, "datatype", None) else None
    language = getattr(value, "language", None)
    result = {"type": "literal", "value": value.toPython()}
    if datatype:
        result["datatype"] = datatype
    if language:
        result["language"] = language
    return result


class LocalSICRPStore:
    """Atomic append-only named-graph store for validated SICRP records."""

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
            # fdopen owns and closes descriptor on the normal and exceptional paths.
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
    def _metadata_graph_uri(graph_uri: str) -> URIRef:
        return URIRef(graph_uri + "#ingestion")

    @staticmethod
    def _assessment_graph_uri(graph_uri: str, digest: str) -> URIRef:
        return URIRef(graph_uri + f"#assessment/{digest}")

    @staticmethod
    def _add_assessment_projection(
        graph: Graph, assessment: dict[str, Any]
    ) -> None:
        assessment_ref = URIRef(assessment["assessment_id"])
        graph.add((assessment_ref, RDF.type, RUNTIME.ProvisionalAssessment))
        graph.add(
            (
                assessment_ref,
                RUNTIME.assessesRecord,
                URIRef(assessment["record_ref"]),
            )
        )
        graph.add(
            (
                assessment_ref,
                RUNTIME.evaluationSemantics,
                Literal(assessment["evaluation_semantics"]),
            )
        )
        graph.add(
            (
                assessment_ref,
                RUNTIME.inputDigest,
                Literal(assessment["input_digest"]),
            )
        )
        graph.add(
            (
                assessment_ref,
                RUNTIME.assessmentDigest,
                Literal(assessment["assessment_digest"]),
            )
        )
        graph.add(
            (
                assessment_ref,
                RUNTIME.asOf,
                Literal(assessment["as_of"], datatype=XSD.dateTime),
            )
        )
        graph.add(
            (
                assessment_ref,
                RUNTIME.recordConforms,
                Literal(assessment["record_conforms"]),
            )
        )
        graph.add(
            (
                assessment_ref,
                RUNTIME.structuralInsolvencyVerdict,
                Literal(assessment["structural_insolvency"]["verdict"]),
            )
        )
        graph.add(
            (
                assessment_ref,
                RUNTIME.collectiveResolutionVerdict,
                Literal(assessment["collective_resolution"]["verdict"]),
            )
        )
        graph.add(
            (
                assessment_ref,
                RUNTIME.ratificationConferred,
                Literal(False),
            )
        )
        graph.add(
            (
                assessment_ref,
                RUNTIME.assessmentPayload,
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
        for obligation in assessment["obligations"]:
            obligation_ref = URIRef(
                assessment["assessment_id"]
                + "/obligation/"
                + obligation["obligation_id"]
            )
            graph.add(
                (assessment_ref, RUNTIME.hasObligationResult, obligation_ref)
            )
            graph.add((obligation_ref, RDF.type, RUNTIME.ObligationResult))
            graph.add(
                (
                    obligation_ref,
                    RUNTIME.obligationIdentifier,
                    Literal(obligation["obligation_id"]),
                )
            )
            graph.add(
                (
                    obligation_ref,
                    RUNTIME.dimension,
                    Literal(obligation["dimension"]),
                )
            )
            graph.add(
                (
                    obligation_ref,
                    RUNTIME.resultStatus,
                    Literal(obligation["status"]),
                )
            )
            graph.add(
                (obligation_ref, RUNTIME.resultCode, Literal(obligation["code"]))
            )
            graph.add(
                (
                    obligation_ref,
                    RUNTIME.resultMessage,
                    Literal(obligation["message"]),
                )
            )
            for target in obligation["blocking_for"]:
                graph.add(
                    (obligation_ref, RUNTIME.blockingFor, Literal(target))
                )
            for subject in obligation["subject_refs"]:
                if subject:
                    graph.add(
                        (obligation_ref, RUNTIME.subjectRef, URIRef(subject))
                    )
            for evidence in obligation["evidence_refs"]:
                graph.add(
                    (obligation_ref, RUNTIME.evidenceRef, URIRef(evidence))
                )

    def ingest(
        self,
        *,
        record_path: Path | str,
        rdf_path: Path | str,
        graph_uri: str,
        record_schema_path: Path | str,
        assessment_schema_path: Path | str,
        shapes_path: Path | str,
        ontology_path: Path | str,
        assessment_shapes_path: Path | str,
        runtime_ontology_path: Path | str,
        as_of: str | None = None,
    ) -> dict[str, Any]:
        if not graph_uri.startswith(("urn:", "https://", "http://")):
            raise EvaluationError("graph_uri must be an absolute URI")
        record = load_json(record_path)
        record_schema = load_json(record_schema_path)
        assessment_schema = load_json(assessment_schema_path)
        json_validation = validate_json_record(record, record_schema)
        if not json_validation["conforms"]:
            raise EvaluationError(
                "JSON record validation failed: "
                + "; ".join(
                    f"{item['path']}: {item['message']}"
                    for item in json_validation["errors"]
                )
            )
        rdf_validation = validate_rdf_record(
            rdf_path,
            shapes_path=shapes_path,
            ontology_path=ontology_path,
        )
        if not rdf_validation["conforms"]:
            raise EvaluationError(
                "RDF SHACL validation failed: " + rdf_validation["report_text"]
            )
        alignment = verify_cross_format_alignment(record, rdf_path)
        if not alignment["conforms"]:
            raise EvaluationError(
                "JSON/RDF alignment failed: "
                + json.dumps(alignment, sort_keys=True)
            )
        assessment = evaluate_record(record, schema=record_schema, as_of=as_of)
        assessment_validation = validate_json_record(
            assessment, assessment_schema
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
        data_graph_ref = URIRef(graph_uri)
        metadata_ref = self._metadata_graph_uri(graph_uri)
        assessment_graph_ref = self._assessment_graph_uri(
            graph_uri, assessment["assessment_digest"]
        )

        with self._lock(exclusive=True):
            dataset = self._load()
            data_graph = dataset.graph(data_graph_ref)
            metadata_graph = dataset.graph(metadata_ref)
            existing_digest = metadata_graph.value(
                subject=data_graph_ref,
                predicate=RUNTIME.inputDigest,
            )
            existing_assessment_digest = metadata_graph.value(
                subject=data_graph_ref,
                predicate=RUNTIME.assessmentDigest,
            )
            if len(data_graph):
                if (
                    existing_digest is not None
                    and str(existing_digest) == assessment["input_digest"]
                    and existing_assessment_digest is not None
                    and str(existing_assessment_digest)
                    == assessment["assessment_digest"]
                ):
                    return {
                        "status": "already_present",
                        "store": str(self.path),
                        "graph_uri": graph_uri,
                        "record_ref": assessment["record_ref"],
                        "input_digest": assessment["input_digest"],
                        "assessment_digest": assessment["assessment_digest"],
                        "record_triples": len(data_graph),
                        "assessment_triples": len(
                            dataset.graph(assessment_graph_ref)
                        ),
                        "record_conforms": assessment["record_conforms"],
                        "collective_resolution_verdict": assessment[
                            "collective_resolution"
                        ]["verdict"],
                        "ratification_conferred": False,
                    }
                raise GraphCollisionError(
                    f"named graph already exists with different content: {graph_uri}"
                )

            for triple in source_graph:
                data_graph.add(triple)
            metadata_graph.add((data_graph_ref, RDF.type, RUNTIME.IngestedRecordGraph))
            metadata_graph.add(
                (
                    data_graph_ref,
                    RUNTIME.inputDigest,
                    Literal(assessment["input_digest"]),
                )
            )
            metadata_graph.add(
                (
                    data_graph_ref,
                    RUNTIME.recordRef,
                    URIRef(assessment["record_ref"]),
                )
            )
            metadata_graph.add(
                (
                    data_graph_ref,
                    RUNTIME.assessmentDigest,
                    Literal(assessment["assessment_digest"]),
                )
            )
            metadata_graph.add(
                (
                    data_graph_ref,
                    RUNTIME.hasAssessmentGraph,
                    assessment_graph_ref,
                )
            )
            metadata_graph.add(
                (
                    assessment_graph_ref,
                    PROV.wasDerivedFrom,
                    data_graph_ref,
                )
            )
            assessment_graph = dataset.graph(assessment_graph_ref)
            self._add_assessment_projection(assessment_graph, assessment)
            assessment_shapes = Graph().parse(
                str(assessment_shapes_path), format="turtle"
            )
            runtime_ontology = Graph().parse(
                str(runtime_ontology_path), format="turtle"
            )
            assessment_conforms, _, assessment_report = shacl_validate(
                data_graph=assessment_graph,
                shacl_graph=assessment_shapes,
                ont_graph=runtime_ontology,
                inference="rdfs",
                advanced=True,
            )
            if not assessment_conforms:
                raise EvaluationError(
                    "generated RDF assessment projection does not conform: "
                    + str(assessment_report)
                )
            self._write_atomic(dataset)

        return {
            "status": "ingested",
            "store": str(self.path),
            "graph_uri": graph_uri,
            "metadata_graph_uri": str(metadata_ref),
            "assessment_graph_uri": str(assessment_graph_ref),
            "record_ref": assessment["record_ref"],
            "input_digest": assessment["input_digest"],
            "assessment_digest": assessment["assessment_digest"],
            "record_triples": len(source_graph),
            "assessment_triples": len(assessment_graph),
            "assessment_graph_conforms": True,
            "record_conforms": assessment["record_conforms"],
            "structural_insolvency_verdict": assessment[
                "structural_insolvency"
            ]["verdict"],
            "collective_resolution_verdict": assessment[
                "collective_resolution"
            ]["verdict"],
            "blocking_obligation_codes": assessment["collective_resolution"][
                "blocking_obligation_codes"
            ],
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
                    "only SELECT and ASK queries are permitted by this CLI"
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
