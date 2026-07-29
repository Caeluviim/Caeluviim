from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .evaluator import (
    EvaluationError,
    evaluate_manifest,
    load_json,
    released_payload,
    validate_json_document,
    validate_rdf_manifest,
    verify_cross_format_alignment,
)
from .store import GraphCollisionError, LocalEvidenceIntakeStore


def _write_json(value: Any, output: str) -> None:
    content = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    content += "\n"
    if output == "-":
        sys.stdout.write(content)
    else:
        Path(output).write_text(content, encoding="utf-8")


def _paths(args: argparse.Namespace) -> dict[str, Path]:
    root = Path(args.project_root).resolve()
    return {
        "root": root,
        "manifest_schema": (
            root / "schemas" / "evidence-intake-manifest.schema.json"
        ),
        "assessment_schema": (
            root / "schemas" / "evidence-intake-assessment.schema.json"
        ),
        "ontology": root / "ontology" / "evidence-intake.ttl",
        "shapes": root / "shapes" / "evidence-intake.shacl.ttl",
        "assessment_shapes": (
            root / "shapes" / "evidence-intake-assessment.shacl.ttl"
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evidence-intake",
        description=(
            "Source capture, claim support evaluation, fail-closed "
            "quarantine, and released-only SICRP assertion export"
        ),
    )
    parser.add_argument("--project-root", default=".")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate")
    validate.add_argument("--manifest", required=True)
    validate.add_argument("--rdf", required=True)
    validate.add_argument("--output", default="-")

    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--manifest", required=True)
    evaluate.add_argument("--output", default="-")

    release = commands.add_parser("release")
    release.add_argument("--manifest", required=True)
    release.add_argument("--output", default="-")

    ingest = commands.add_parser("ingest")
    ingest.add_argument("--manifest", required=True)
    ingest.add_argument("--rdf", required=True)
    ingest.add_argument("--store", required=True)
    ingest.add_argument("--graph-base", required=True)
    ingest.add_argument("--output", default="-")

    inspect = commands.add_parser("inspect")
    inspect.add_argument("--store", required=True)
    inspect.add_argument("--output", default="-")

    query = commands.add_parser("query")
    query.add_argument("--store", required=True)
    query.add_argument("--sparql-file", required=True)
    query.add_argument("--output", default="-")
    return parser


def _evaluate(
    manifest_path: str,
    paths: dict[str, Path],
) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load_json(manifest_path)
    manifest_schema = load_json(paths["manifest_schema"])
    assessment = evaluate_manifest(
        manifest,
        schema=manifest_schema,
        project_root=paths["root"],
    )
    assessment_schema = load_json(paths["assessment_schema"])
    assessment_validation = validate_json_document(
        assessment,
        assessment_schema,
    )
    if not assessment_validation["conforms"]:
        raise EvaluationError(
            "generated assessment does not conform: "
            + json.dumps(assessment_validation, sort_keys=True)
        )
    return manifest, assessment


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = _paths(args)
    try:
        if args.command == "validate":
            manifest = load_json(args.manifest)
            manifest_schema = load_json(paths["manifest_schema"])
            json_result = validate_json_document(
                manifest,
                manifest_schema,
            )
            rdf_result = validate_rdf_manifest(
                args.rdf,
                shapes_path=paths["shapes"],
                ontology_path=paths["ontology"],
            )
            alignment = verify_cross_format_alignment(
                manifest,
                args.rdf,
            )
            _, assessment = _evaluate(args.manifest, paths)
            assessment_schema = load_json(paths["assessment_schema"])
            assessment_result = validate_json_document(
                assessment,
                assessment_schema,
            )
            result = {
                "conforms": (
                    json_result["conforms"]
                    and rdf_result["conforms"]
                    and alignment["conforms"]
                    and assessment_result["conforms"]
                ),
                "json_schema": json_result,
                "rdf_shacl": rdf_result,
                "cross_format_alignment": alignment,
                "deterministic_assessment": assessment_result,
                "released_claim_refs": assessment["released_claim_refs"],
                "quarantined_claim_refs": assessment[
                    "quarantined_claim_refs"
                ],
            }
            _write_json(result, args.output)
            return 0 if result["conforms"] else 1

        if args.command == "evaluate":
            _, assessment = _evaluate(args.manifest, paths)
            _write_json(assessment, args.output)
            return 0

        if args.command == "release":
            manifest, assessment = _evaluate(args.manifest, paths)
            _write_json(
                released_payload(manifest, assessment),
                args.output,
            )
            return 0

        store = LocalEvidenceIntakeStore(args.store)
        if args.command == "ingest":
            result = store.ingest(
                manifest_path=args.manifest,
                rdf_path=args.rdf,
                base_graph_uri=args.graph_base,
                project_root=paths["root"],
                manifest_schema_path=paths["manifest_schema"],
                assessment_schema_path=paths["assessment_schema"],
                shapes_path=paths["shapes"],
                ontology_path=paths["ontology"],
                assessment_shapes_path=paths["assessment_shapes"],
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
