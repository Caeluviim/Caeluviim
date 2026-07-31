from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from .batch_ingest import IngestionBatch, ingest_batch
from .mcp_server import run_mcp
from .native_graph import NativeNeo4j
from .models import (
    CandidateBatch,
    CandidateReview,
    DialogueIngestRequest,
    InformationScope,
    ReviewDecision,
)
from .projection import GraphProjector
from .service import CaeluviimCore
from .validator import validate_core


def _json(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))


def _read_json(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text("utf-8"))


def _core(args: argparse.Namespace) -> CaeluviimCore:
    return CaeluviimCore(
        data_dir=Path(args.data_dir),
        project_root=Path(args.project_root) if args.project_root else None,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="caeluviim",
        description="Local-first, operation-sourced civic graph core",
    )
    parser.add_argument("--data-dir", default=".caeluviim")
    parser.add_argument("--project-root")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    commands.add_parser("audit")
    commands.add_parser("validate")
    commands.add_parser("replay")
    commands.add_parser("mcp")

    graph = commands.add_parser("graph")
    graph_commands = graph.add_subparsers(dest="graph_command", required=True)
    for command in ("install", "start", "status", "stop"):
        graph_commands.add_parser(command)
    graph_project = graph_commands.add_parser("project")
    graph_project.add_argument("--owner")
    graph_validate = graph_commands.add_parser("validate")
    graph_validate.add_argument("--owner")

    ingest = commands.add_parser("ingest")
    ingest_commands = ingest.add_subparsers(dest="ingest_command", required=True)
    dialogue = ingest_commands.add_parser("dialogue")
    dialogue.add_argument("--input", required=True)
    dialogue.add_argument(
        "--scope",
        choices=[scope.value for scope in InformationScope],
        required=True,
    )
    dialogue.add_argument("--owner")
    dialogue.add_argument("--official", action="store_true")
    dialogue.add_argument("--consent-basis")
    batch = ingest_commands.add_parser("batch")
    batch.add_argument("--input", required=True)
    batch.add_argument(
        "--project-native",
        action="store_true",
        help=(
            "Start the repository-managed Neo4j runtime, replace the batch scope "
            "partition, and validate the live projection."
        ),
    )

    stage = commands.add_parser("stage-candidates")
    stage.add_argument("--input", required=True)

    quarantine = commands.add_parser("quarantine")
    quarantine_commands = quarantine.add_subparsers(
        dest="quarantine_command", required=True
    )
    quarantine_list = quarantine_commands.add_parser("list")
    quarantine_list.add_argument("--owner")
    quarantine_show = quarantine_commands.add_parser("show")
    quarantine_show.add_argument("event_id")
    quarantine_show.add_argument("--owner")
    for decision in ("accept", "reject", "contest"):
        review = quarantine_commands.add_parser(decision)
        review.add_argument("event_id")
        review.add_argument("--owner")
        review.add_argument("--reviewer", default="member:founder")
        review.add_argument("--reason", required=True)
        review.add_argument("--evidence", action="append", default=[])
        review.add_argument("--supersedes", action="append", default=[])

    trace = commands.add_parser("trace")
    trace.add_argument("identifier")
    trace.add_argument("--owner")

    project = commands.add_parser("project")
    project_commands = project.add_subparsers(dest="project_command", required=True)
    rdf = project_commands.add_parser("rdf")
    rdf.add_argument("--output", required=True)
    rdf.add_argument("--format", choices=["trig", "nquads"], default="trig")
    rdf.add_argument("--owner")
    neo4j = project_commands.add_parser("neo4j")
    neo4j.add_argument("--uri", default="bolt://127.0.0.1:7687")
    neo4j.add_argument("--user", default="neo4j")
    neo4j.add_argument("--password-env", default="NEO4J_PASSWORD")
    neo4j.add_argument("--owner")

    shred = commands.add_parser("crypto-shred-member")
    shred.add_argument("member_id")
    shred.add_argument("--reason", required=True)
    shred.add_argument(
        "--confirm",
        action="store_true",
        help="Required because this irreversibly destroys the local content key.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "mcp":
        run_mcp(
            Path(args.data_dir),
            Path(args.project_root) if args.project_root else None,
        )
        return 0

    core = _core(args)
    if args.command == "init":
        _json(core.initialize())
    elif args.command == "audit":
        _json(core.audit())
    elif args.command in {"validate", "replay"}:
        core.initialize()
        result = validate_core(core)
        _json(result)
        return 0 if result["conforms"] else 1
    elif args.command == "ingest":
        if args.ingest_command == "dialogue":
            payload = _read_json(args.input)
            payload["scope"] = args.scope
            payload["owner_id"] = args.owner
            payload["official_capacity"] = args.official
            if args.consent_basis:
                payload["consent_basis"] = args.consent_basis
            _json(core.ingest_dialogue(DialogueIngestRequest.model_validate(payload)))
        else:
            batch = IngestionBatch.model_validate(_read_json(args.input))
            result = ingest_batch(core, batch)
            exit_code = 0 if result["projection"]["shacl_conforms"] else 1
            if args.project_native:
                native = NativeNeo4j()
                status = native.start()
                user, password = native.credentials()
                projector = GraphProjector(core)
                projection_owner = batch.owner_id if not batch.scope.is_public else None
                projected = projector.project_neo4j(
                    uri="bolt://127.0.0.1:7687",
                    user=user,
                    password=password,
                    owner_id=projection_owner,
                )
                validation = projector.validate_neo4j(
                    uri="bolt://127.0.0.1:7687",
                    user=user,
                    password=password,
                    owner_id=projection_owner,
                )
                result["native_graph"] = {
                    "status": status,
                    "projection": projected.__dict__,
                    "validation": validation,
                }
                if not validation["conforms"]:
                    exit_code = 1
            _json(result)
            return exit_code
    elif args.command == "stage-candidates":
        _json(core.stage_candidates(CandidateBatch.model_validate(_read_json(args.input))))
    elif args.command == "quarantine":
        if args.quarantine_command == "list":
            _json(core.list_quarantined(owner_id=args.owner))
        elif args.quarantine_command == "show":
            entries = core.list_quarantined(owner_id=args.owner)
            match = next(
                (
                    entry
                    for entry in entries
                    if entry["event"]["event_id"] == args.event_id
                ),
                None,
            )
            if not match:
                raise SystemExit("quarantined candidate is not visible or does not exist")
            _json(match)
        else:
            decision = ReviewDecision(args.quarantine_command)
            review = CandidateReview(
                candidate_event_id=args.event_id,
                decision=decision,
                reviewer_id=args.reviewer,
                reason=args.reason,
                evidence_ids=args.evidence,
                supersedes_ids=args.supersedes,
            )
            _json(core.review_candidate(review, owner_id=args.owner))
    elif args.command == "trace":
        _json(core.trace(args.identifier, owner_id=args.owner))
    elif args.command == "project":
        projector = GraphProjector(core)
        if args.project_command == "rdf":
            result = projector.serialize_rdf(
                Path(args.output), owner_id=args.owner, format=args.format
            )
            _json(result.__dict__)
        else:
            password = os.environ.get(args.password_env)
            if not password:
                raise SystemExit(
                    f"Neo4j password is missing from environment variable {args.password_env}"
                )
            _json(
                projector.project_neo4j(
                    uri=args.uri,
                    user=args.user,
                    password=password,
                    owner_id=args.owner,
                ).__dict__
            )
    elif args.command == "crypto-shred-member":
        if not args.confirm:
            raise SystemExit(
                "Refusing irreversible key destruction without --confirm"
            )
        _json(core.crypto_shred_member(args.member_id, args.reason))
    elif args.command == "graph":
        native = NativeNeo4j()
        if args.graph_command == "install":
            _json(native.install())
        elif args.graph_command == "start":
            _json(native.start())
        elif args.graph_command == "status":
            _json(native.status())
        elif args.graph_command == "stop":
            _json(native.stop())
        else:
            user, password = native.credentials()
            projector = GraphProjector(core)
            if args.graph_command == "project":
                core.initialize()
                _json(
                    projector.project_neo4j(
                        uri="bolt://127.0.0.1:7687",
                        user=user,
                        password=password,
                        owner_id=args.owner,
                    ).__dict__
                )
            else:
                result = projector.validate_neo4j(
                    uri="bolt://127.0.0.1:7687",
                    user=user,
                    password=password,
                    owner_id=args.owner,
                )
                _json(result)
                return 0 if result["conforms"] else 1
    return 0
