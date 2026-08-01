from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .evaluator import (
    EvaluationError,
    evaluate_record,
    load_json,
    validate_json_record,
    validate_rdf_record,
    verify_cross_format_alignment,
)
from .store import GraphCollisionError, LocalSICRPStore


def _write_json(value: Any, output: str) -> None:
    content = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if output == "-":
        sys.stdout.write(content)
    else:
        Path(output).write_text(content, encoding="utf-8")


def _paths(args: argparse.Namespace) -> dict[str, Path]:
    root = Path(args.project_root).resolve()
    return {
        "root": root,
        "record_schema": root / "schemas" / "sicrp-record.schema.json",
        "assessment_schema": root / "schemas" / "sicrp-assessment.schema.json",
        "shapes": root / "shapes" / "sicrp.shacl.ttl",
        "ontology": root / "ontology" / "sicrp.ttl",
        "assessment_shapes": root
        / "shapes"
        / "sicrp-assessment.shacl.ttl",
        "runtime_ontology": root / "ontology" / "sicrp-runtime.ttl",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sicrp-runtime",
        description=(
            "Deterministic SICRP validation, provisional evaluation, and "
            "atomic local named-graph ingestion"
        ),
    )
    parser.add_argument("--project-root", default=".")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate")
    validate.add_argument("--record", required=True)
    validate.add_argument("--rdf", required=True)
    validate.add_argument("--output", default="-")

    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--record", required=True)
    evaluate.add_argument("--as-of")
    evaluate.add_argument("--output", default="-")

    ingest = commands.add_parser("ingest")
    ingest.add_argument("--record", required=True)
    ingest.add_argument("--rdf", required=True)
    ingest.add_argument("--store", required=True)
    ingest.add_argument("--graph", required=True)
    ingest.add_argument("--as-of")
    ingest.add_argument("--output", default="-")

    inspect = commands.add_parser("inspect")
    inspect.add_argument("--store", required=True)
    inspect.add_argument("--output", default="-")

    query = commands.add_parser("query")
    query.add_argument("--store", required=True)
    query.add_argument("--sparql-file", required=True)
    query.add_argument("--output", default="-")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = _paths(args)
    try:
        if args.command == "validate":
            record = load_json(args.record)
            schema = load_json(paths["record_schema"])
            json_result = validate_json_record(record, schema)
            rdf_result = validate_rdf_record(
                args.rdf,
                shapes_path=paths["shapes"],
                ontology_path=paths["ontology"],
            )
            alignment = verify_cross_format_alignment(record, args.rdf)
            result = {
                "conforms": (
                    json_result["conforms"]
                    and rdf_result["conforms"]
                    and alignment["conforms"]
                ),
                "json_schema": json_result,
                "rdf_shacl": rdf_result,
                "cross_format_alignment": alignment,
            }
            _write_json(result, args.output)
            return 0 if result["conforms"] else 1

        if args.command == "evaluate":
            record = load_json(args.record)
            schema = load_json(paths["record_schema"])
            assessment = evaluate_record(
                record, schema=schema, as_of=args.as_of
            )
            assessment_schema = load_json(paths["assessment_schema"])
            assessment_validation = validate_json_record(
                assessment, assessment_schema
            )
            if not assessment_validation["conforms"]:
                raise EvaluationError(
                    "generated assessment does not conform: "
                    + json.dumps(assessment_validation, sort_keys=True)
                )
            _write_json(assessment, args.output)
            return 0 if assessment["record_conforms"] else 1

        store = LocalSICRPStore(args.store)
        if args.command == "ingest":
            result = store.ingest(
                record_path=args.record,
                rdf_path=args.rdf,
                graph_uri=args.graph,
                record_schema_path=paths["record_schema"],
                assessment_schema_path=paths["assessment_schema"],
                shapes_path=paths["shapes"],
                ontology_path=paths["ontology"],
                assessment_shapes_path=paths["assessment_shapes"],
                runtime_ontology_path=paths["runtime_ontology"],
                as_of=args.as_of,
            )
        elif args.command == "inspect":
            result = store.inspect()
        else:
            sparql = Path(args.sparql_file).read_text("utf-8")
            result = store.query(sparql)
        _write_json(result, args.output)
        return 0
    except (EvaluationError, GraphCollisionError, OSError, ValueError) as error:
        _write_json(
            {
                "conforms": False,
                "error": type(error).__name__,
                "message": str(error),
            },
            getattr(args, "output", "-"),
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
