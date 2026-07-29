from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from rdflib import Dataset, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from .evaluator import (
    AcquisitionEvaluationError,
    evaluate_manifest,
    intake_eligible_payload,
    load_json,
    validate_json_document,
    validate_rdf_manifest,
    verify_cross_format_alignment,
)

ACQ = Namespace("https://caeluviim.org/ontology/source-acquisition#")


class AcquisitionGraphCollisionError(ValueError):
    """Raised when a graph base is reused for different acquisition input."""


def _add_type(graph: Graph, subject: str, class_name: str) -> URIRef:
    ref = URIRef(subject)
    graph.add((ref, RDF.type, ACQ[class_name]))
    return ref


class LocalSourceAcquisitionStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _load(self) -> Dataset:
        dataset = Dataset()
        if self.path.exists():
            dataset.parse(self.path, format="trig")
        return dataset

    @staticmethod
    def _graph_uris(
        base_graph_uri: str,
        assessment_digest: str,
    ) -> dict[str, str]:
        base = base_graph_uri.rstrip("/")
        return {
            "acquisition": f"{base}/acquisition",
            "eligible": f"{base}/eligible",
            "failures": f"{base}/failures",
            "lifecycle": f"{base}/lifecycle",
            "assessment": f"{base}/assessment/{assessment_digest}",
            "metadata": f"{base}/metadata",
        }

    def _atomic_serialize(self, dataset: Dataset) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(
            prefix=self.path.name + ".",
            suffix=".tmp",
            dir=self.path.parent,
        )
        os.close(handle)
        temporary_path = Path(temporary)
        try:
            dataset.serialize(destination=temporary_path, format="trig")
            os.replace(temporary_path, self.path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()

    def ingest(
        self,
        *,
        manifest_path: str | Path,
        rdf_path: str | Path,
        base_graph_uri: str,
        project_root: str | Path,
        manifest_schema_path: str | Path,
        assessment_schema_path: str | Path,
        shapes_path: str | Path,
        ontology_path: str | Path,
    ) -> dict[str, Any]:
        manifest = load_json(manifest_path)
        manifest_schema = load_json(manifest_schema_path)
        schema_result = validate_json_document(manifest, manifest_schema)
        if not schema_result["conforms"]:
            raise AcquisitionEvaluationError(
                f"manifest schema failed: {schema_result['errors']}"
            )
        rdf_result = validate_rdf_manifest(
            rdf_path,
            shapes_path=shapes_path,
            ontology_path=ontology_path,
        )
        if not rdf_result["conforms"]:
            raise AcquisitionEvaluationError(
                "RDF acquisition manifest does not conform: "
                + rdf_result["report_text"]
            )
        alignment = verify_cross_format_alignment(manifest, rdf_path)
        if not alignment["conforms"]:
            raise AcquisitionEvaluationError(
                f"JSON/RDF alignment failed: {alignment}"
            )
        assessment = evaluate_manifest(
            manifest,
            schema=manifest_schema,
            project_root=project_root,
        )
        assessment_schema = load_json(assessment_schema_path)
        assessment_result = validate_json_document(
            assessment, assessment_schema
        )
        if not assessment_result["conforms"]:
            raise AcquisitionEvaluationError(
                f"assessment schema failed: {assessment_result['errors']}"
            )
        payload = intake_eligible_payload(manifest, assessment)
        graph_uris = self._graph_uris(
            base_graph_uri, assessment["assessment_digest"]
        )
        dataset = self._load()
        metadata = dataset.graph(URIRef(graph_uris["metadata"]))
        graph_set_ref = URIRef(base_graph_uri.rstrip("/") + "/graph-set")
        existing_digest = metadata.value(
            graph_set_ref, ACQ.manifestDigest
        )
        if existing_digest is not None:
            if str(existing_digest) == assessment["manifest_digest"]:
                return {
                    "status": "already_present",
                    "graph_uris": graph_uris,
                    "manifest_digest": assessment["manifest_digest"],
                    "assessment_digest": assessment["assessment_digest"],
                    "eligible_snapshot_count": len(
                        assessment["eligible_snapshot_refs"]
                    ),
                    "failed_attempt_count": len(
                        assessment["ineligible_attempt_refs"]
                    ),
                    "graphs_disjoint": True,
                }
            raise AcquisitionGraphCollisionError(
                "graph base already contains a different acquisition manifest"
            )

        acquisition_graph = dataset.graph(
            URIRef(graph_uris["acquisition"])
        )
        parsed = Graph().parse(rdf_path, format="turtle")
        for triple in parsed:
            acquisition_graph.add(triple)

        eligible_graph = dataset.graph(URIRef(graph_uris["eligible"]))
        for record in payload["eligible_snapshots"]:
            snapshot = _add_type(
                eligible_graph, record["snapshot_id"], "IntakeEligibleSnapshot"
            )
            eligible_graph.add(
                (
                    snapshot,
                    ACQ.fixedBy,
                    URIRef(record["snapshot_fixation_ref"]),
                )
            )
            eligible_graph.add(
                (
                    snapshot,
                    ACQ.sourceVersion,
                    URIRef(record["source_version_ref"]),
                )
            )
            eligible_graph.add(
                (
                    snapshot,
                    ACQ.canonicalIdentity,
                    URIRef(record["canonical_identity_ref"]),
                )
            )
            eligible_graph.add(
                (snapshot, ACQ.sha256, Literal(record["sha256"]))
            )
            eligible_graph.add(
                (
                    snapshot,
                    ACQ.byteLength,
                    Literal(record["byte_length"], datatype=XSD.integer),
                )
            )
            eligible_graph.add(
                (
                    snapshot,
                    ACQ.contentPath,
                    Literal(record["content_path"]),
                )
            )

        failure_graph = dataset.graph(URIRef(graph_uris["failures"]))
        for result in assessment["attempt_results"]:
            if result["intake_eligible"]:
                continue
            attempt = _add_type(
                failure_graph, result["attempt_ref"], "IneligibleAttempt"
            )
            failure_graph.add(
                (attempt, ACQ.retrievalOutcome, Literal(result["outcome"]))
            )
        for fact in assessment["failure_facts"]:
            fact_ref = _add_type(
                failure_graph, fact["fact_id"], "AcquisitionFailureFact"
            )
            failure_graph.add(
                (fact_ref, ACQ.failureSubject, URIRef(fact["subject_ref"]))
            )
            failure_graph.add(
                (fact_ref, ACQ.failureCode, Literal(fact["code"]))
            )
            failure_graph.add(
                (fact_ref, ACQ.failureMessage, Literal(fact["message"]))
            )

        lifecycle_graph = dataset.graph(
            URIRef(graph_uris["lifecycle"])
        )
        for version in manifest["source_versions"]:
            version_ref = _add_type(
                lifecycle_graph, version["version_id"], "SourceVersion"
            )
            lifecycle_graph.add(
                (
                    version_ref,
                    ACQ.canonicalIdentity,
                    URIRef(version["canonical_identity_ref"]),
                )
            )
            lifecycle_graph.add(
                (version_ref, ACQ.sha256, Literal(version["sha256"]))
            )
        for change in manifest["change_events"]:
            change_ref = _add_type(
                lifecycle_graph, change["change_id"], "ChangeEvent"
            )
            lifecycle_graph.add(
                (
                    change_ref,
                    ACQ.previousVersion,
                    URIRef(change["previous_version_ref"]),
                )
            )
            lifecycle_graph.add(
                (
                    change_ref,
                    ACQ.nextVersion,
                    URIRef(change["next_version_ref"]),
                )
            )
        for relation in manifest["supersession_relations"]:
            relation_ref = _add_type(
                lifecycle_graph,
                relation["relation_id"],
                "SupersessionRelation",
            )
            lifecycle_graph.add(
                (
                    relation_ref,
                    ACQ.supersededVersion,
                    URIRef(relation["superseded_version_ref"]),
                )
            )
            lifecycle_graph.add(
                (
                    relation_ref,
                    ACQ.supersedingVersion,
                    URIRef(relation["superseding_version_ref"]),
                )
            )

        assessment_graph = dataset.graph(
            URIRef(graph_uris["assessment"])
        )
        assessment_ref = _add_type(
            assessment_graph,
            assessment["assessment_id"],
            "AcquisitionAssessment",
        )
        assessment_graph.add(
            (
                assessment_ref,
                ACQ.manifestDigest,
                Literal(assessment["manifest_digest"]),
            )
        )
        assessment_graph.add(
            (
                assessment_ref,
                ACQ.assessmentDigest,
                Literal(assessment["assessment_digest"]),
            )
        )
        assessment_graph.add(
            (
                assessment_ref,
                ACQ.pipelineResult,
                Literal(assessment["pipeline_result"]),
            )
        )

        metadata.add((graph_set_ref, RDF.type, ACQ.AcquisitionGraphSet))
        metadata.add(
            (
                graph_set_ref,
                ACQ.manifest,
                URIRef(manifest["manifest_id"]),
            )
        )
        metadata.add(
            (
                graph_set_ref,
                ACQ.manifestDigest,
                Literal(assessment["manifest_digest"]),
            )
        )
        metadata.add(
            (
                graph_set_ref,
                ACQ.assessment,
                URIRef(assessment["assessment_id"]),
            )
        )

        eligible_subjects = set(eligible_graph.subjects())
        failure_subjects = set(failure_graph.subjects())
        graphs_disjoint = (
            set(eligible_graph).isdisjoint(set(failure_graph))
            and eligible_subjects.isdisjoint(failure_subjects)
        )
        if not graphs_disjoint:
            raise AcquisitionEvaluationError(
                "eligible and failure graphs are not physically disjoint"
            )
        self._atomic_serialize(dataset)
        return {
            "status": "ingested",
            "graph_uris": graph_uris,
            "manifest_digest": assessment["manifest_digest"],
            "assessment_digest": assessment["assessment_digest"],
            "eligible_snapshot_count": len(
                assessment["eligible_snapshot_refs"]
            ),
            "failed_attempt_count": len(
                assessment["ineligible_attempt_refs"]
            ),
            "graphs_disjoint": graphs_disjoint,
        }

    def inspect(self) -> dict[str, Any]:
        dataset = self._load()
        contexts = sorted(
            (
                {
                    "graph_uri": str(context.identifier),
                    "triple_count": len(context),
                }
                for context in dataset.contexts()
                if len(context)
            ),
            key=lambda item: item["graph_uri"],
        )
        return {
            "store_path": str(self.path),
            "named_graph_count": len(contexts),
            "named_graphs": contexts,
        }

    def query(self, sparql: str) -> dict[str, Any]:
        dataset = self._load()
        result = dataset.query(sparql)
        variables = [str(item) for item in result.vars]
        rows = []
        for row in result:
            values: dict[str, Any] = {}
            for variable, value in zip(variables, row):
                if value is None:
                    continue
                values[variable] = {
                    "type": (
                        "uri" if isinstance(value, URIRef) else "literal"
                    ),
                    "value": str(value),
                }
            rows.append(values)
        return {
            "variables": variables,
            "row_count": len(rows),
            "rows": rows,
        }
