from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .evaluator import (
    AcquisitionEvaluationError,
    evaluate_manifest,
    intake_eligible_payload,
    load_json,
    validate_json_document,
    validate_rdf_manifest,
    verify_cross_format_alignment,
)
from .store import (
    AcquisitionGraphCollisionError,
    LocalSourceAcquisitionStore,
)


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
            root / "schemas" / "source-acquisition-manifest.schema.json"
        ),
        "assessment_schema": (
            root / "schemas" / "source-acquisition-assessment.schema.json"
        ),
        "ontology": root / "ontology" / "source-acquisition.ttl",
        "shapes": root / "shapes" / "source-acquisition.shacl.ttl",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="source-acquisition",
        description=(
            "Faithful source retrieval records, content-addressed fixation, "
            "version comparison, and intake-eligible export"
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
    export = commands.add_parser("intake")
    export.add_argument("--manifest", required=True)
    export.add_argument("--output", default="-")
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
    result = validate_json_document(
        assessment, load_json(paths["assessment_schema"])
    )
    if not result["conforms"]:
        raise AcquisitionEvaluationError(
            "generated assessment does not conform: "
            + json.dumps(result, sort_keys=True)
        )
    return manifest, assessment


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = _paths(args)
    try:
        if args.command == "validate":
            manifest = load_json(args.manifest)
            json_result = validate_json_document(
                manifest, load_json(paths["manifest_schema"])
            )
            rdf_result = validate_rdf_manifest(
                args.rdf,
                shapes_path=paths["shapes"],
                ontology_path=paths["ontology"],
            )
            alignment = verify_cross_format_alignment(
                manifest, args.rdf
            )
            _, assessment = _evaluate(args.manifest, paths)
            assessment_result = validate_json_document(
                assessment, load_json(paths["assessment_schema"])
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
                "pipeline_result": assessment["pipeline_result"],
                "eligible_snapshot_refs": assessment[
                    "eligible_snapshot_refs"
                ],
                "ineligible_attempt_refs": assessment[
                    "ineligible_attempt_refs"
                ],
            }
            _write_json(result, args.output)
            return 0 if result["conforms"] else 1
        if args.command == "evaluate":
            _, assessment = _evaluate(args.manifest, paths)
            _write_json(assessment, args.output)
            return 0
        if args.command == "intake":
            manifest, assessment = _evaluate(args.manifest, paths)
            _write_json(
                intake_eligible_payload(manifest, assessment), args.output
            )
            return 0

        store = LocalSourceAcquisitionStore(args.store)
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
            )
        elif args.command == "inspect":
            result = store.inspect()
        else:
            sparql = Path(args.sparql_file).read_text("utf-8")
            result = store.query(sparql)
        _write_json(result, args.output)
        return 0
    except (
        AcquisitionEvaluationError,
        AcquisitionGraphCollisionError,
        OSError,
        ValueError,
    ) as error:
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
