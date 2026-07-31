from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from pyshacl import validate as shacl_validate
from rdflib import Dataset, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import DCTERMS, PROV, RDFS, XSD

from .models import InformationScope
from .service import CaeluviimCore
from .store import ObjectAccessError

CAEL = Namespace("https://caeluviim.org/ontology/core#")
COMMONS_GRAPH = URIRef("https://caeluviim.org/graph/commons")
PRIVATE_GRAPH_BASE = "https://caeluviim.org/graph/member/"


@dataclass(frozen=True)
class ProjectionResult:
    event_count: int
    triple_count: int
    scope: str
    output: str | None = None


class GraphProjector:
    def __init__(self, core: CaeluviimCore):
        self.core = core

    def _included_events(
        self, *, owner_id: str | None = None
    ) -> list[dict[str, Any]]:
        events = self.core.ledger.events(accepted_only=True)
        if owner_id:
            owner_token = __import__("hashlib").sha256(owner_id.encode("utf-8")).hexdigest()
            return [
                event
                for event in events
                if InformationScope(event["scope"]).is_public
                or event.get("owner_token") == owner_token
            ]
        return [
            event
            for event in events
            if InformationScope(event["scope"]).is_public
        ]

    @staticmethod
    def _uri(identifier: str) -> URIRef:
        return URIRef(identifier)

    @staticmethod
    def _property_graph(
        dataset: Dataset,
    ) -> tuple[dict[str, dict[str, Any]], set[tuple[str, str, str]]]:
        nodes: dict[str, dict[str, Any]] = {}
        edges: set[tuple[str, str, str]] = set()
        for subject, predicate, obj, _graph_name in dataset.quads(
            (None, None, None, None)
        ):
            if not isinstance(subject, URIRef):
                continue
            node = nodes.setdefault(str(subject), {"types": [], "properties": {}})
            if predicate == RDF.type and isinstance(obj, URIRef):
                node["types"].append(str(obj))
            elif isinstance(obj, Literal):
                node["properties"].setdefault(str(predicate), []).append(str(obj))
            elif isinstance(obj, URIRef):
                nodes.setdefault(str(obj), {"types": [], "properties": {}})
                edges.add((str(subject), str(predicate), str(obj)))
        for value in nodes.values():
            value["types"] = sorted(set(value["types"]))
            value["properties"] = {
                key: sorted(set(items))
                for key, items in sorted(value["properties"].items())
            }
        return nodes, edges

    def build_dataset(self, *, owner_id: str | None = None) -> Dataset:
        dataset = Dataset()
        dataset.bind("cael", CAEL)
        dataset.bind("prov", PROV)
        dataset.bind("dct", DCTERMS)
        private_graph_uri = (
            URIRef(
                PRIVATE_GRAPH_BASE
                + __import__("hashlib").sha256(owner_id.encode("utf-8")).hexdigest()
            )
            if owner_id
            else COMMONS_GRAPH
        )
        events = self._included_events(owner_id=owner_id)
        event_index = {event["event_id"]: event for event in self.core.ledger.events()}

        for event in events:
            scope = InformationScope(event["scope"])
            graph = dataset.graph(
                COMMONS_GRAPH if scope.is_public else private_graph_uri
            )
            event_node = self._uri(event["event_id"])
            graph.add((event_node, RDF.type, CAEL.LedgerEvent))
            graph.add((event_node, CAEL.eventType, Literal(event["event_type"])))
            graph.add((event_node, CAEL.payloadRef, self._uri(event["payload_ref"])))
            graph.add((event_node, CAEL.informationScope, Literal(event["scope"])))
            graph.add(
                (
                    event_node,
                    PROV.wasAssociatedWith,
                    self._uri(event["actor_id"]),
                )
            )
            graph.add(
                (
                    event_node,
                    PROV.generatedAtTime,
                    Literal(event["recorded_at"], datatype=XSD.dateTime),
                )
            )
            graph.add(
                (
                    event_node,
                    CAEL.contentHash,
                    Literal("sha256:" + event["event_id"].rsplit(":", 1)[-1]),
                )
            )
            if event["predecessor_id"]:
                graph.add(
                    (
                        event_node,
                        CAEL.predecessor,
                        self._uri(event["predecessor_id"]),
                    )
                )
            for parent in event["parent_ids"]:
                graph.add((event_node, PROV.wasDerivedFrom, self._uri(parent)))
            for superseded in event["supersedes_ids"]:
                graph.add((event_node, CAEL.supersedes, self._uri(superseded)))

            try:
                payload = self.core.store.get_json(
                    event["payload_ref"],
                    owner_id=owner_id if not InformationScope(event["scope"]).is_public else None,
                )
            except ObjectAccessError:
                continue
            self._project_payload(graph, event, payload, event_index, owner_id)
        return dataset

    def _project_payload(
        self,
        graph: Graph,
        event: dict[str, Any],
        payload: dict[str, Any],
        event_index: dict[str, dict[str, Any]],
        owner_id: str | None,
    ) -> None:
        event_node = self._uri(event["event_id"])
        if event["event_type"] == "CONSTITUTION_GENESIS":
            graph.add((self._uri(payload["constitution_id"]), RDF.type, CAEL.Constitution))
            graph.add(
                (
                    self._uri(payload["constitution_id"]),
                    PROV.wasGeneratedBy,
                    event_node,
                )
            )
        elif event["event_type"] == "SYNTHETIC_PERSON_DECLARE":
            person = self._uri(payload["person_id"])
            graph.add((person, RDF.type, CAEL.LegalPerson))
            graph.add((person, RDFS.label, Literal(payload["label"])))
            graph.add((person, PROV.wasGeneratedBy, event_node))
        elif event["event_type"] == "LUX_MANIFESTATION_DELEGATE":
            manifestation = self._uri(payload["manifestation_id"])
            graph.add((manifestation, RDF.type, CAEL.LuxManifestation))
            graph.add((manifestation, PROV.actedOnBehalfOf, self._uri("person:lux")))
            graph.add((manifestation, CAEL.manifestationId, Literal(payload["manifestation_id"])))
            graph.add((manifestation, PROV.wasGeneratedBy, event_node))
        elif event["event_type"] == "DIALOGUE_CAPTURE":
            conversation = self._uri(event["payload_ref"])
            graph.add((conversation, RDF.type, CAEL.CommunicativeEvent))
            graph.add((conversation, PROV.wasGeneratedBy, event_node))
            for turn in payload.get("turns", []):
                source = self._uri(turn["source_object_id"])
                graph.add((source, RDF.type, CAEL.SourceArtifact))
                graph.add((source, DCTERMS.language, Literal(turn["language"])))
                graph.add(
                    (
                        source,
                        PROV.wasAttributedTo,
                        self._uri(turn["participant_id"]),
                    )
                )
                try:
                    text = self.core.store.get_bytes(
                        turn["source_object_id"],
                        owner_id=owner_id
                        if not InformationScope(event["scope"]).is_public
                        else None,
                    ).decode("utf-8")
                    graph.add((source, CAEL.exactText, Literal(text)))
                except ObjectAccessError:
                    pass
            for span in payload.get("spans", []):
                source = self._uri(span["source_object_id"])
                span_node = self._uri(span["span_id"])
                graph.add((span_node, RDF.type, CAEL.SourceSpan))
                graph.add((source, CAEL.containsSpan, span_node))
                graph.add((span_node, PROV.wasDerivedFrom, source))
                graph.add((span_node, CAEL.contentHash, Literal(span["exact_text_hash"])))
        elif event["event_type"] == "CANDIDATE_REVIEW" and payload["decision"] == "accept":
            candidate_event = event_index[payload["candidate_event_id"]]
            candidate = self.core.store.get_json(
                candidate_event["payload_ref"],
                owner_id=owner_id
                if not InformationScope(candidate_event["scope"]).is_public
                else None,
            )
            node = self._uri(candidate["candidate_id"])
            node_type = {
                "interpretation": CAEL.Interpretation,
                "force_assignment": CAEL.ForceAssignment,
                "linguistic_operation": CAEL.LinguisticOperation,
                "harm_assessment": CAEL.HarmAssessment,
                "proposition": CAEL.Proposition,
                "context_state": CAEL.ContextState,
                "evidence_assessment": CAEL.Assessment,
                "personhood_profile": CAEL.Assessment,
                "other": CAEL.Assessment,
            }[candidate["candidate_type"]]
            graph.add((node, RDF.type, node_type))
            graph.add((node, RDFS.label, Literal(candidate["label"])))
            graph.add((node, DCTERMS.description, Literal(candidate["content"])))
            graph.add(
                (
                    node,
                    CAEL.confidence,
                    Literal(Decimal(str(candidate["confidence"])), datatype=XSD.decimal),
                )
            )
            graph.add((node, PROV.wasAttributedTo, self._uri(candidate["manifestation_id"])))
            graph.add((node, PROV.wasGeneratedBy, event_node))
            for span_id in candidate["source_span_ids"]:
                graph.add((node, PROV.wasDerivedFrom, self._uri(span_id)))
        elif event["event_type"] == "DISCLOSURE_RESTRICTION_CREATE":
            node = self._uri(payload["restriction_id"])
            graph.add((node, RDF.type, CAEL.DisclosureRestriction))
            graph.add((node, PROV.wasGeneratedBy, event_node))
        elif event["event_type"] == "MEMBER_SUCCESSION_DIRECTIVE":
            node = self._uri(payload["directive_id"])
            graph.add((node, RDF.type, CAEL.SuccessionDirective))
            graph.add((node, PROV.wasGeneratedBy, event_node))

    def serialize_rdf(
        self,
        output: Path,
        *,
        owner_id: str | None = None,
        format: str = "trig",
    ) -> ProjectionResult:
        dataset = self.build_dataset(owner_id=owner_id)
        output.parent.mkdir(parents=True, exist_ok=True)
        dataset.serialize(destination=str(output), format=format)
        return ProjectionResult(
            event_count=len(self._included_events(owner_id=owner_id)),
            triple_count=sum(1 for _ in dataset.quads()),
            scope="member_private_plus_public" if owner_id else "public",
            output=str(output),
        )

    def validate_shacl(self, *, owner_id: str | None = None) -> dict[str, Any]:
        dataset = self.build_dataset(owner_id=owner_id)
        ontology = Graph()
        ontology.parse(self.core.project_root / "ontology" / "caeluviim-core.ttl")
        shapes = Graph()
        shapes.parse(self.core.project_root / "ontology" / "shapes" / "core-shapes.ttl")
        conforms, report_graph, report_text = shacl_validate(
            data_graph=dataset,
            shacl_graph=shapes,
            ont_graph=ontology,
            inference="rdfs",
            advanced=True,
        )
        return {
            "conforms": bool(conforms),
            "report_text": report_text,
            "report_triples": len(report_graph),
        }

    def project_neo4j(
        self,
        *,
        uri: str,
        user: str,
        password: str,
        owner_id: str | None = None,
    ) -> ProjectionResult:
        try:
            from neo4j import GraphDatabase
        except ImportError as exc:
            raise RuntimeError(
                "The Neo4j Python driver is required for live Neo4j projection."
            ) from exc

        dataset = self.build_dataset(owner_id=owner_id)
        partition = (
            "public"
            if owner_id is None
            else "member:"
            + __import__("hashlib").sha256(owner_id.encode("utf-8")).hexdigest()
        )
        nodes, edges = self._property_graph(dataset)
        driver = GraphDatabase.driver(uri, auth=(user, password))
        try:
            with driver.session() as session:
                session.run(
                    "CREATE CONSTRAINT caeluviim_resource_partition_id IF NOT EXISTS "
                    "FOR (n:CaeluviimResource) REQUIRE (n.partition, n.id) IS UNIQUE"
                ).consume()

                def replace_partition(transaction):
                    transaction.run(
                        "MATCH (n:CaeluviimResource {partition: $partition}) "
                        "DETACH DELETE n",
                        partition=partition,
                    ).consume()
                    for identifier, value in nodes.items():
                        transaction.run(
                            "CREATE (n:CaeluviimResource "
                            "{partition: $partition, id: $id, types: $types, "
                            "propertiesJson: $properties})",
                            partition=partition,
                            id=identifier,
                            types=value["types"],
                            properties=json.dumps(
                                value["properties"], sort_keys=True
                            ),
                        ).consume()
                    for subject, predicate, obj in edges:
                        transaction.run(
                            "MATCH (s:CaeluviimResource "
                            "{partition: $partition, id: $subject}) "
                            "MATCH (o:CaeluviimResource "
                            "{partition: $partition, id: $object}) "
                            "CREATE (s)-[:CAELUVIIM_RELATION "
                            "{partition: $partition, predicate: $predicate}]->(o)",
                            partition=partition,
                            subject=subject,
                            object=obj,
                            predicate=predicate,
                        ).consume()

                session.execute_write(replace_partition)
        finally:
            driver.close()
        return ProjectionResult(
            event_count=len(self._included_events(owner_id=owner_id)),
            triple_count=sum(1 for _ in dataset.quads()),
            scope="member_private_plus_public" if owner_id else "public",
        )

    def validate_neo4j(
        self,
        *,
        uri: str,
        user: str,
        password: str,
        owner_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            from neo4j import GraphDatabase
        except ImportError as exc:
            raise RuntimeError(
                "The Neo4j Python driver is required for live Neo4j validation."
            ) from exc

        partition = (
            "public"
            if owner_id is None
            else "member:"
            + __import__("hashlib").sha256(owner_id.encode("utf-8")).hexdigest()
        )
        expected_nodes, expected_edges = self._property_graph(
            self.build_dataset(owner_id=owner_id)
        )
        driver = GraphDatabase.driver(uri, auth=(user, password))
        try:
            driver.verify_connectivity()
            with driver.session() as session:
                node_rows = session.run(
                    "MATCH (n:CaeluviimResource {partition: $partition}) "
                    "RETURN n.id AS id, n.types AS types, "
                    "n.propertiesJson AS propertiesJson ORDER BY n.id",
                    partition=partition,
                ).data()
                edge_rows = session.run(
                    "MATCH (s:CaeluviimResource)-[r:CAELUVIIM_RELATION "
                    "{partition: $partition}]->(o:CaeluviimResource) "
                    "WHERE s.partition = $partition AND o.partition = $partition "
                    "RETURN s.id AS subject, r.predicate AS predicate, "
                    "o.id AS object",
                    partition=partition,
                ).data()
                constraints = session.run(
                    "SHOW CONSTRAINTS YIELD name RETURN collect(name) AS names"
                ).single()["names"]
                partitions = session.run(
                    "MATCH (n:CaeluviimResource) "
                    "RETURN DISTINCT n.partition AS partition ORDER BY partition"
                ).value()
        finally:
            driver.close()

        actual_nodes = {
            row["id"]: {
                "types": sorted(row["types"] or []),
                "properties": json.loads(row["propertiesJson"] or "{}"),
            }
            for row in node_rows
        }
        actual_edges = {
            (row["subject"], row["predicate"], row["object"])
            for row in edge_rows
        }
        missing_nodes = sorted(set(expected_nodes) - set(actual_nodes))
        unexpected_nodes = sorted(set(actual_nodes) - set(expected_nodes))
        changed_nodes = sorted(
            identifier
            for identifier in set(expected_nodes).intersection(actual_nodes)
            if expected_nodes[identifier] != actual_nodes[identifier]
        )
        missing_edges = sorted(expected_edges - actual_edges)
        unexpected_edges = sorted(actual_edges - expected_edges)
        constraint_name = "caeluviim_resource_partition_id"
        conforms = not any(
            (
                missing_nodes,
                unexpected_nodes,
                changed_nodes,
                missing_edges,
                unexpected_edges,
            )
        ) and constraint_name in constraints
        return {
            "conforms": conforms,
            "uri": uri,
            "partition": partition,
            "partitions_present": partitions,
            "expected_node_count": len(expected_nodes),
            "actual_node_count": len(actual_nodes),
            "expected_edge_count": len(expected_edges),
            "actual_edge_count": len(actual_edges),
            "missing_nodes": missing_nodes,
            "unexpected_nodes": unexpected_nodes,
            "changed_nodes": changed_nodes,
            "missing_edges": missing_edges,
            "unexpected_edges": unexpected_edges,
            "constraint_present": constraint_name in constraints,
        }
