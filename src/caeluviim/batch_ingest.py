from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import Field, model_validator

from .canonical import canonical_bytes
from .governance import GovernanceService
from .models import (
    AnalysisCandidate,
    CandidateBatch,
    CandidateReview,
    DialogueIngestRequest,
    DialogueTurn,
    InformationScope,
    Reproducibility,
    ReviewDecision,
    StrictModel,
    utc_now,
)
from .projection import GraphProjector
from .service import CaeluviimCore


class BatchSource(StrictModel):
    source_id: str = Field(min_length=1, max_length=512)
    title: str | None = Field(default=None, max_length=500)
    participant_id: str = Field(min_length=1, max_length=512)
    content: str = Field(min_length=1, max_length=1_000_000)
    language: str = Field(default="und", min_length=2, max_length=80)
    script: str | None = Field(default=None, max_length=80)
    occurred_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BatchReview(StrictModel):
    decision: ReviewDecision
    reviewer_id: str = Field(min_length=1, max_length=512)
    reason: str = Field(min_length=1, max_length=10_000)
    evidence_ids: list[str] = Field(default_factory=list)
    supersedes_ids: list[str] = Field(default_factory=list)


class BatchMapping(StrictModel):
    mapping_id: str = Field(min_length=1, max_length=512)
    source_id: str = Field(min_length=1, max_length=512)
    candidate_type: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1, max_length=100_000)
    alternative_hypotheses: list[str] = Field(min_length=1)
    confidence: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    agent_id: str = GovernanceService.LUX_ID
    manifestation_id: str = GovernanceService.DEFAULT_MANIFESTATION_ID
    model_id: str = "caeluviim-batch-ingest/0.1"
    prompt_version: str = "manifest-supplied"
    rule_version: str = "constitution/0.1"
    ontology_version: str = "caeluviim-core/0.1"
    reproducibility: Reproducibility = Reproducibility.DETERMINISTIC
    construction_rule: str = (
        "Mapped from the complete cited source artifact by an explicit batch manifest."
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    review: BatchReview | None = None


class IngestionBatch(StrictModel):
    batch_id: str = Field(min_length=1, max_length=512)
    title: str | None = Field(default=None, max_length=500)
    scope: InformationScope
    owner_id: str | None = Field(default=None, max_length=512)
    consent_basis: str = Field(min_length=1, max_length=1000)
    official_capacity: bool = False
    started_at: str = Field(default_factory=utc_now)
    sources: list[BatchSource] = Field(min_length=1)
    mappings: list[BatchMapping] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_batch(self) -> "IngestionBatch":
        if not self.scope.is_public and not self.owner_id:
            raise ValueError("non-public ingestion batches require owner_id")
        if self.official_capacity and self.scope != InformationScope.OFFICIAL_PUBLIC:
            raise ValueError("official-capacity ingestion must use official_public scope")

        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source_id values must be unique within a batch")
        mapping_ids = [mapping.mapping_id for mapping in self.mappings]
        if len(mapping_ids) != len(set(mapping_ids)):
            raise ValueError("mapping_id values must be unique within a batch")

        available_sources = set(source_ids)
        expected_reviewer = (
            GovernanceService.FOUNDER_ID if self.scope.is_public else self.owner_id
        )
        for mapping in self.mappings:
            if mapping.source_id not in available_sources:
                raise ValueError(
                    f"mapping {mapping.mapping_id} references missing source "
                    f"{mapping.source_id}"
                )
            if mapping.review and mapping.review.reviewer_id != expected_reviewer:
                raise ValueError(
                    "batch review identity must match the ledger signing identity: "
                    f"expected {expected_reviewer}, received "
                    f"{mapping.review.reviewer_id}"
                )
        return self


def _triple_count(projector: GraphProjector, *, owner_id: str | None) -> int:
    return sum(1 for _ in projector.build_dataset(owner_id=owner_id).quads())


def _submit_or_replay_review(
    core: CaeluviimCore,
    *,
    batch: IngestionBatch,
    mapping: BatchMapping,
    candidate_event_id: str,
) -> dict[str, Any]:
    if mapping.review is None:
        raise ValueError("review replay requested without a review declaration")

    expected = CandidateReview(
        candidate_event_id=candidate_event_id,
        decision=mapping.review.decision,
        reviewer_id=mapping.review.reviewer_id,
        reason=mapping.review.reason,
        evidence_ids=mapping.review.evidence_ids,
        supersedes_ids=mapping.review.supersedes_ids,
        reviewed_at=batch.started_at,
    )
    existing = next(
        (
            event
            for event in core.ledger.events(accepted_only=True)
            if event["event_type"] == "CANDIDATE_REVIEW"
            and candidate_event_id in event["parent_ids"]
        ),
        None,
    )
    if existing is None:
        return core.review_candidate(expected, owner_id=batch.owner_id)

    payload = core.store.get_json(existing["payload_ref"], owner_id=batch.owner_id)
    expected_payload = expected.model_dump(mode="json")
    mismatches = {
        key: {"expected": value, "actual": payload.get(key)}
        for key, value in expected_payload.items()
        if payload.get(key) != value
    }
    if mismatches:
        raise ValueError(
            "candidate already has a different completed review: " + str(mismatches)
        )
    return {
        "event": existing,
        "accepted": True,
        "idempotent_replay": True,
    }


def ingest_batch(core: CaeluviimCore, batch: IngestionBatch) -> dict[str, Any]:
    """Ingest source artifacts and explicit mappings as one replayable activation batch.

    The accepted activation event is an internal operations timestamp. It records
    when this repository began processing the declared batch; it does not by
    itself establish an external payment, settlement, or legal deadline.
    """

    core.initialize()
    source_results: dict[str, dict[str, Any]] = {}
    source_event_ids: list[str] = []

    for source in batch.sources:
        result = core.ingest_dialogue(
            DialogueIngestRequest(
                conversation_id=f"{batch.batch_id}:source:{source.source_id}",
                title=source.title or batch.title,
                turns=[
                    DialogueTurn(
                        turn_id=f"{batch.batch_id}:{source.source_id}:turn:1",
                        participant_id=source.participant_id,
                        role="user",
                        content=source.content,
                        language=source.language,
                        script=source.script,
                        occurred_at=source.occurred_at,
                        metadata=source.metadata,
                    )
                ],
                scope=batch.scope,
                owner_id=batch.owner_id,
                consent_basis=batch.consent_basis,
                official_capacity=batch.official_capacity,
                source_system="caeluviim.ingestion-batch/0.1",
                acquired_at=batch.started_at,
                metadata={
                    "batch_id": batch.batch_id,
                    "batch_source_id": source.source_id,
                    **batch.metadata,
                },
            )
        )
        source_results[source.source_id] = result
        source_event_ids.append(result["conversation_event_id"])

    mapping_results: list[dict[str, Any]] = []
    stage_event_ids: list[str] = []
    review_event_ids: list[str] = []

    for mapping in batch.mappings:
        source_result = source_results[mapping.source_id]
        source_span = source_result["spans"][0]
        source_record = source_result["turns"][0]
        candidate = AnalysisCandidate(
            candidate_type=mapping.candidate_type,
            label=mapping.label,
            content=mapping.content,
            source_span_ids=[source_span["span_id"]],
            evidence_ids=[source_record["source_object_id"]],
            alternative_hypotheses=mapping.alternative_hypotheses,
            confidence=mapping.confidence,
            agent_id=mapping.agent_id,
            manifestation_id=mapping.manifestation_id,
            model_id=mapping.model_id,
            prompt_version=mapping.prompt_version,
            rule_version=mapping.rule_version,
            ontology_version=mapping.ontology_version,
            reproducibility=mapping.reproducibility,
            construction_rule=mapping.construction_rule,
            metadata={
                "batch_id": batch.batch_id,
                "mapping_id": mapping.mapping_id,
                **mapping.metadata,
            },
        )
        staged = core.stage_candidates(
            CandidateBatch(
                conversation_event_id=source_result["conversation_event_id"],
                scope=batch.scope,
                owner_id=batch.owner_id,
                candidates=[candidate],
                submitted_at=batch.started_at,
            )
        )
        stage_event = staged["candidates"][0]["event"]
        stage_event_ids.append(stage_event["event_id"])

        reviewed: dict[str, Any] | None = None
        if mapping.review:
            reviewed = _submit_or_replay_review(
                core,
                batch=batch,
                mapping=mapping,
                candidate_event_id=stage_event["event_id"],
            )
            review_event_ids.append(reviewed["event"]["event_id"])

        mapping_results.append(
            {
                "mapping_id": mapping.mapping_id,
                "source_id": mapping.source_id,
                "candidate_event_id": stage_event["event_id"],
                "candidate_id": stage_event["metadata"]["candidate_id"],
                "decision": mapping.review.decision.value if mapping.review else None,
                "review_event_id": reviewed["event"]["event_id"] if reviewed else None,
            }
        )

    accepted_mappings = sum(
        1
        for mapping in batch.mappings
        if mapping.review and mapping.review.decision == ReviewDecision.ACCEPT
    )
    receipt = {
        "record_type": "IngestionActivationReceipt",
        "receipt_version": "caeluviim-ingestion-activation/0.1",
        "batch_id": batch.batch_id,
        "title": batch.title,
        "started_at": batch.started_at,
        "scope": batch.scope.value,
        "owner_id": batch.owner_id,
        "source_count": len(batch.sources),
        "mapping_count": len(batch.mappings),
        "accepted_mapping_count": accepted_mappings,
        "unreviewed_mapping_count": sum(
            1 for mapping in batch.mappings if mapping.review is None
        ),
        "source_event_ids": source_event_ids,
        "mapping_results": mapping_results,
        "activation_semantics": (
            "Internal evidence of graph-ingestion operations. This receipt does not "
            "by itself establish an external payment, settlement, or legal deadline."
        ),
        "metadata": batch.metadata,
    }
    receipt_digest = __import__("hashlib").sha256(canonical_bytes(receipt)).hexdigest()
    receipt["receipt_id"] = f"urn:caeluviim:ingestion-receipt:sha256:{receipt_digest}"
    stored_receipt = core.store.put_json(
        receipt,
        scope=batch.scope,
        owner_id=batch.owner_id,
        metadata={
            "kind": "ingestion_activation_receipt",
            "batch_id": batch.batch_id,
        },
    )

    signer = (
        core.governance.founder_signer()
        if batch.scope.is_public
        else core.governance.ensure_member(batch.owner_id or "")
    )
    activation = core.ledger.submit(
        event_type="INGESTION_BATCH_ACTIVATE",
        signer=signer,
        scope=batch.scope,
        owner_id=batch.owner_id,
        payload_ref=stored_receipt["object_id"],
        idempotency_key=f"ingestion-batch:{batch.batch_id}:{receipt['receipt_id']}",
        disposition="ACCEPTED_EFFECTIVE",
        parent_ids=source_event_ids + stage_event_ids + review_event_ids,
        metadata={
            "batch_id": batch.batch_id,
            "receipt_id": receipt["receipt_id"],
            "source_count": len(batch.sources),
            "mapping_count": len(batch.mappings),
            "accepted_mapping_count": accepted_mappings,
            "operational_start_marker": True,
        },
    )

    projector = GraphProjector(core)
    projection_owner = batch.owner_id if not batch.scope.is_public else None
    shacl = projector.validate_shacl(owner_id=projection_owner)
    audit = core.audit()
    return {
        "batch_id": batch.batch_id,
        "receipt_id": receipt["receipt_id"],
        "receipt_object_id": stored_receipt["object_id"],
        "activation_event_id": activation["event"]["event_id"],
        "activation_started_at": activation["event"]["recorded_at"],
        "idempotent_replay": activation["idempotent_replay"],
        "source_count": len(batch.sources),
        "mapping_count": len(batch.mappings),
        "accepted_mapping_count": accepted_mappings,
        "quarantined_mapping_count": sum(
            1 for mapping in batch.mappings if mapping.review is None
        ),
        "projection": {
            "scope": "public" if projection_owner is None else "member_private_plus_public",
            "triple_count": _triple_count(projector, owner_id=projection_owner),
            "shacl_conforms": shacl["conforms"],
            "shacl_report": shacl["report_text"],
        },
        "ledger_state_root": audit["state_root"],
        "event_signature_count": audit["event_signatures"],
    }
