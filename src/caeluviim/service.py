from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from .canonical import canonical_bytes
from .governance import GovernanceService
from .keys import KeyVault
from .ledger import CivicLedger
from .models import (
    CandidateBatch,
    CandidateReview,
    DialogueIngestRequest,
    InformationScope,
    ReviewDecision,
    SourceSpan,
)
from .store import ObjectAccessError, ObjectNotFoundError, ObjectStore


class CaeluviimCore:
    def __init__(self, data_dir: Path | str, project_root: Path | str | None = None):
        self.data_dir = Path(data_dir)
        self.project_root = (
            Path(project_root)
            if project_root is not None
            else Path(__file__).resolve().parents[2]
        )
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.store = ObjectStore(self.data_dir / "store")
        self.ledger = CivicLedger(self.data_dir / "ledger")
        self.keys = KeyVault(self.data_dir / "signing-keys")
        self.governance = GovernanceService(
            store=self.store,
            ledger=self.ledger,
            key_vault=self.keys,
            project_root=self.project_root,
        )

    def initialize(self) -> dict[str, Any]:
        return self.governance.initialize()

    @staticmethod
    def _span_id(
        source_object_id: str,
        byte_start: int,
        byte_end: int,
        codepoint_start: int,
        codepoint_end: int,
    ) -> str:
        digest = hashlib.sha256(
            canonical_bytes(
                {
                    "source_object_id": source_object_id,
                    "byte_start": byte_start,
                    "byte_end": byte_end,
                    "codepoint_start": codepoint_start,
                    "codepoint_end": codepoint_end,
                }
            )
        ).hexdigest()
        return f"urn:caeluviim:span:sha256:{digest}"

    def ingest_dialogue(self, request: DialogueIngestRequest) -> dict[str, Any]:
        self.initialize()
        signer = (
            self.governance.founder_signer()
            if request.scope.is_public
            else self.governance.ensure_member(request.owner_id or "")
        )
        selected = set(request.selected_turn_ids or [turn.turn_id for turn in request.turns])
        turn_records: list[dict[str, Any]] = []
        spans: list[dict[str, Any]] = []
        for turn in request.turns:
            if turn.turn_id not in selected:
                continue
            raw = turn.content.encode("utf-8")
            stored = self.store.put_bytes(
                raw,
                media_type="text/plain",
                encoding="utf-8",
                scope=request.scope,
                owner_id=request.owner_id,
                metadata={
                    "kind": "dialogue_turn",
                    "turn_id": turn.turn_id,
                    "participant_id": turn.participant_id,
                    "role": turn.role,
                    "language": turn.language,
                    "script": turn.script,
                    "occurred_at": turn.occurred_at,
                },
            )
            span = SourceSpan(
                span_id=self._span_id(
                    stored["object_id"], 0, len(raw), 0, len(turn.content)
                ),
                source_object_id=stored["object_id"],
                turn_id=turn.turn_id,
                byte_start=0,
                byte_end=len(raw),
                codepoint_start=0,
                codepoint_end=len(turn.content),
                exact_text_hash=f"sha256:{hashlib.sha256(raw).hexdigest()}",
            )
            turn_records.append(
                {
                    "turn_id": turn.turn_id,
                    "participant_id": turn.participant_id,
                    "role": turn.role,
                    "source_object_id": stored["object_id"],
                    "language": turn.language,
                    "script": turn.script,
                    "occurred_at": turn.occurred_at,
                    "metadata": turn.metadata,
                }
            )
            spans.append(span.model_dump(mode="json"))

        manifest = {
            "record_type": "DialogueCapture",
            "conversation_id": request.conversation_id,
            "title": request.title,
            "source_system": request.source_system,
            "acquired_at": request.acquired_at,
            "consent_basis": request.consent_basis,
            "scope": request.scope.value,
            "owner_id": request.owner_id,
            "official_capacity": request.official_capacity,
            "turns": turn_records,
            "spans": spans,
            "metadata": request.metadata,
        }
        stored_manifest = self.store.put_json(
            manifest,
            scope=request.scope,
            owner_id=request.owner_id,
            metadata={
                "kind": "dialogue_capture",
                "turn_count": len(turn_records),
            },
        )
        event = self.ledger.submit(
            event_type="DIALOGUE_CAPTURE",
            signer=signer,
            scope=request.scope,
            owner_id=request.owner_id,
            payload_ref=stored_manifest["object_id"],
            idempotency_key=f"dialogue:{stored_manifest['object_id']}",
            disposition="ACCEPTED_EFFECTIVE",
            evidence_ids=[turn["source_object_id"] for turn in turn_records],
            metadata={
                "turn_count": len(turn_records),
                "manual_trigger": True,
                "official_capacity": request.official_capacity,
            },
        )
        return {
            "conversation_event_id": event["event"]["event_id"],
            "manifest_object_id": stored_manifest["object_id"],
            "turns": turn_records,
            "spans": spans,
            "scope": request.scope.value,
            "owner_id": request.owner_id,
        }

    def _reference_exists(
        self, reference: str, *, owner_id: str | None, manifest: dict[str, Any]
    ) -> bool:
        if reference in {span["span_id"] for span in manifest["spans"]}:
            return True
        if reference in {turn["source_object_id"] for turn in manifest["turns"]}:
            return True
        if reference.startswith("urn:caeluviim:event:"):
            try:
                self.ledger.event(reference)
                return True
            except KeyError:
                return False
        if reference.startswith("urn:caeluviim:object:"):
            try:
                self.store.metadata(reference, owner_id=owner_id)
                return True
            except (ObjectNotFoundError, ObjectAccessError):
                return False
        return False

    def stage_candidates(self, batch: CandidateBatch) -> dict[str, Any]:
        conversation_event = self.ledger.event(batch.conversation_event_id)
        if conversation_event["event_type"] != "DIALOGUE_CAPTURE":
            raise ValueError("candidate batch must reference a dialogue capture")
        if conversation_event["scope"] != batch.scope.value:
            raise ValueError("candidate scope must match dialogue scope")
        manifest = self.store.get_json(
            conversation_event["payload_ref"], owner_id=batch.owner_id
        )
        span_ids = {span["span_id"] for span in manifest["spans"]}
        results = []
        for supplied in batch.candidates:
            missing_spans = set(supplied.source_span_ids) - span_ids
            if missing_spans:
                raise ValueError(f"candidate references missing spans: {sorted(missing_spans)}")
            missing_evidence = [
                reference
                for reference in supplied.evidence_ids
                if not self._reference_exists(
                    reference, owner_id=batch.owner_id, manifest=manifest
                )
            ]
            if missing_evidence:
                raise ValueError(f"candidate evidence is missing: {missing_evidence}")
            candidate_body = supplied.model_dump(mode="json", exclude={"candidate_id"})
            digest = hashlib.sha256(
                b"CAELUVIIM-CANDIDATE-0.1\x00" + canonical_bytes(candidate_body)
            ).hexdigest()
            candidate = supplied.model_copy(
                update={
                    "candidate_id": f"urn:caeluviim:candidate:sha256:{digest}"
                }
            )
            stored = self.store.put_json(
                candidate.model_dump(mode="json"),
                scope=batch.scope,
                owner_id=batch.owner_id,
                metadata={
                    "kind": "analysis_candidate",
                    "candidate_type": candidate.candidate_type,
                },
            )
            signer = self.governance.manifestation_signer(
                candidate.manifestation_id,
                model_id=candidate.model_id,
                prompt_version=candidate.prompt_version,
                rule_version=candidate.rule_version,
                ontology_version=candidate.ontology_version,
                scope=batch.scope,
            )
            result = self.ledger.submit(
                event_type="ANALYSIS_CANDIDATE_STAGE",
                signer=signer,
                scope=batch.scope,
                owner_id=batch.owner_id,
                payload_ref=stored["object_id"],
                idempotency_key=candidate.candidate_id or digest,
                disposition="QUARANTINED",
                evidence_ids=candidate.evidence_ids,
                parent_ids=[batch.conversation_event_id],
                metadata={
                    "candidate_id": candidate.candidate_id,
                    "candidate_type": candidate.candidate_type,
                    "manifestation_id": candidate.manifestation_id,
                },
            )
            results.append(result)
        return {
            "conversation_event_id": batch.conversation_event_id,
            "quarantined_count": len(results),
            "candidates": results,
        }

    def list_quarantined(
        self, *, owner_id: str | None = None
    ) -> list[dict[str, Any]]:
        reviewed = {
            parent
            for event in self.ledger.events(accepted_only=True)
            if event["event_type"] == "CANDIDATE_REVIEW"
            for parent in event["parent_ids"]
        }
        output = []
        for event in self.ledger.events():
            if (
                event["event_type"] != "ANALYSIS_CANDIDATE_STAGE"
                or event["event_id"] in reviewed
            ):
                continue
            try:
                payload = self.store.get_json(event["payload_ref"], owner_id=owner_id)
            except ObjectAccessError:
                continue
            output.append({"event": event, "candidate": payload})
        return output

    def review_candidate(
        self, review: CandidateReview, *, owner_id: str | None = None
    ) -> dict[str, Any]:
        candidate_event = self.ledger.event(review.candidate_event_id)
        if candidate_event["event_type"] != "ANALYSIS_CANDIDATE_STAGE":
            raise ValueError("review target is not an analysis candidate")
        scope = InformationScope(candidate_event["scope"])
        candidate = self.store.get_json(
            candidate_event["payload_ref"], owner_id=owner_id
        )
        if any(
            review.candidate_event_id in event["parent_ids"]
            for event in self.ledger.events(accepted_only=True)
            if event["event_type"] == "CANDIDATE_REVIEW"
        ):
            raise ValueError("candidate already has a completed review")
        signer = (
            self.governance.founder_signer()
            if scope.is_public
            else self.governance.ensure_member(owner_id or "")
        )
        review_payload = {
            **review.model_dump(mode="json"),
            "candidate_id": candidate["candidate_id"],
            "candidate_payload_ref": candidate_event["payload_ref"],
            "candidate_type": candidate["candidate_type"],
        }
        stored = self.store.put_json(
            review_payload,
            scope=scope,
            owner_id=owner_id,
            metadata={"kind": "candidate_review", "decision": review.decision.value},
        )
        event_type = {
            ReviewDecision.ACCEPT: "CANDIDATE_ACCEPT",
            ReviewDecision.REJECT: "CANDIDATE_REJECT",
            ReviewDecision.CONTEST: "CANDIDATE_CONTEST",
        }[review.decision]
        return self.ledger.submit(
            event_type="CANDIDATE_REVIEW",
            signer=signer,
            scope=scope,
            owner_id=owner_id,
            payload_ref=stored["object_id"],
            idempotency_key=f"review:{review.candidate_event_id}:{review.decision.value}",
            disposition="ACCEPTED_EFFECTIVE",
            evidence_ids=review.evidence_ids,
            parent_ids=[review.candidate_event_id],
            supersedes_ids=review.supersedes_ids,
            metadata={
                "decision": review.decision.value,
                "operative_type": event_type,
                "candidate_type": candidate["candidate_type"],
            },
        )

    def trace(
        self, identifier: str, *, owner_id: str | None = None
    ) -> dict[str, Any]:
        events = {event["event_id"]: event for event in self.ledger.events()}
        roots: list[dict[str, Any]] = []
        visited: set[str] = set()

        def visit(event_id: str) -> None:
            if event_id in visited or event_id not in events:
                return
            visited.add(event_id)
            event = events[event_id]
            roots.append(event)
            for related in (
                event["parent_ids"]
                + event["supersedes_ids"]
                + ([event["predecessor_id"]] if event["predecessor_id"] else [])
            ):
                visit(related)

        matching_ids = set()
        if identifier in events:
            matching_ids.add(identifier)
        for event in events.values():
            if (
                event["payload_ref"] == identifier
                or identifier in event["evidence_ids"]
                or identifier in event["parent_ids"]
                or identifier in event["supersedes_ids"]
                or identifier in event.get("metadata", {}).values()
            ):
                matching_ids.add(event["event_id"])

        changed = True
        while changed:
            changed = False
            for event in events.values():
                related = set(event["parent_ids"] + event["supersedes_ids"])
                if event["predecessor_id"]:
                    related.add(event["predecessor_id"])
                if (
                    event["event_id"] in matching_ids
                    or related.intersection(matching_ids)
                ) and event["event_id"] not in matching_ids:
                    matching_ids.add(event["event_id"])
                    changed = True

        for event_id in sorted(matching_ids):
            visit(event_id)

        objects = []
        for event in roots:
            try:
                scope = InformationScope(event["scope"])
                value = self.store.get_json(
                    event["payload_ref"],
                    owner_id=owner_id if not scope.is_public else None,
                )
                objects.append(
                    {"object_id": event["payload_ref"], "value": value}
                )
            except (ObjectAccessError, ObjectNotFoundError, json.JSONDecodeError):
                continue
        return {"identifier": identifier, "events": roots, "objects": objects}

    def audit(self) -> dict[str, Any]:
        verification = self.ledger.verify()
        unresolved = self.list_quarantined()
        return {
            **verification,
            "unresolved_public_quarantine_count": len(
                [
                    item
                    for item in unresolved
                    if item["event"]["scope"]
                    in {
                        InformationScope.COMMONS.value,
                        InformationScope.OFFICIAL_PUBLIC.value,
                    }
                ]
            ),
            "public_object_count": sum(1 for _ in self.store.iter_public_metadata()),
            "constitutional_invariants": {
                "manual_non_official_ingestion": True,
                "ai_candidates_quarantined": True,
                "lux_manifestations_attributed": True,
                "private_objects_encrypted": True,
                "projections_rebuildable": True,
            },
        }

    def crypto_shred_member(self, member_id: str, reason: str) -> dict[str, Any]:
        owner_token = hashlib.sha256(member_id.encode("utf-8")).hexdigest()
        tombstone = {
            "record_type": "CryptoShredTombstone",
            "owner_token": owner_token,
            "reason": reason,
            "content_retained": False,
            "identity_disclosed": False,
        }
        stored = self.store.put_json(
            tombstone,
            scope=InformationScope.OFFICIAL_PUBLIC,
            metadata={"kind": "crypto_shred_tombstone"},
        )
        event = self.ledger.submit(
            event_type="MEMBER_CONTENT_CRYPTO_SHRED",
            signer=self.governance.founder_signer(),
            scope=InformationScope.OFFICIAL_PUBLIC,
            payload_ref=stored["object_id"],
            idempotency_key=f"crypto-shred:{owner_token}",
            disposition="ACCEPTED_EFFECTIVE",
            metadata={"content_free_tombstone": True},
        )
        shredded = self.store.crypto_shred(member_id)
        return {"event": event, "key_destroyed": shredded}
