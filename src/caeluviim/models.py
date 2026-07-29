from __future__ import annotations

from decimal import Decimal
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class InformationScope(str, Enum):
    PRIVATE = "private"
    GROUP = "group"
    DISTRICT = "district"
    COMMONS = "commons"
    OFFICIAL_PUBLIC = "official_public"

    @property
    def is_public(self) -> bool:
        return self in {self.COMMONS, self.OFFICIAL_PUBLIC}


class Reproducibility(str, Enum):
    DETERMINISTIC = "deterministic"
    SEEDED = "seeded"
    APPROXIMATE = "approximately_reproducible"
    NON_REPRODUCIBLE = "non_reproducible"


class DialogueTurn(StrictModel):
    turn_id: str = Field(min_length=1, max_length=512)
    participant_id: str = Field(min_length=1, max_length=512)
    role: Literal["user", "assistant", "system", "tool", "observer", "other"]
    content: str
    language: str = Field(default="und", min_length=2, max_length=80)
    script: str | None = Field(default=None, max_length=80)
    occurred_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DialogueIngestRequest(StrictModel):
    conversation_id: str = Field(min_length=1, max_length=512)
    title: str | None = Field(default=None, max_length=500)
    turns: list[DialogueTurn] = Field(min_length=1)
    selected_turn_ids: list[str] | None = None
    scope: InformationScope
    owner_id: str | None = Field(default=None, max_length=512)
    consent_basis: str = Field(min_length=1, max_length=1000)
    official_capacity: bool = False
    source_system: str = Field(default="manual", min_length=1, max_length=240)
    acquired_at: str = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_scope(self) -> "DialogueIngestRequest":
        if not self.scope.is_public and not self.owner_id:
            raise ValueError("non-public dialogue requires owner_id")
        if self.official_capacity and self.scope != InformationScope.OFFICIAL_PUBLIC:
            raise ValueError("official civic dialogue must use official_public scope")
        ids = [turn.turn_id for turn in self.turns]
        if len(ids) != len(set(ids)):
            raise ValueError("turn_id values must be unique")
        if self.selected_turn_ids:
            missing = set(self.selected_turn_ids) - set(ids)
            if missing:
                raise ValueError(f"selected turns are missing: {sorted(missing)}")
        return self


class SourceSpan(StrictModel):
    span_id: str
    source_object_id: str
    turn_id: str
    byte_start: int = Field(ge=0)
    byte_end: int = Field(ge=0)
    codepoint_start: int = Field(ge=0)
    codepoint_end: int = Field(ge=0)
    exact_text_hash: str

    @model_validator(mode="after")
    def validate_ranges(self) -> "SourceSpan":
        if self.byte_end < self.byte_start or self.codepoint_end < self.codepoint_start:
            raise ValueError("span end must not precede span start")
        return self


class AnalysisCandidate(StrictModel):
    candidate_id: str | None = None
    candidate_type: Literal[
        "interpretation",
        "force_assignment",
        "linguistic_operation",
        "harm_assessment",
        "proposition",
        "context_state",
        "evidence_assessment",
        "personhood_profile",
        "other",
    ]
    label: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1, max_length=100_000)
    source_span_ids: list[str] = Field(min_length=1)
    evidence_ids: list[str] = Field(min_length=1)
    alternative_hypotheses: list[str] = Field(min_length=1)
    # Decimal is serialized as a canonical lexical value, avoiding non-replayable
    # binary floating-point encodings while retaining the required 0.00-1.00 range.
    confidence: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    status: Literal["proposed"] = "proposed"
    agent_id: str = Field(min_length=1, max_length=512)
    manifestation_id: str = Field(min_length=1, max_length=512)
    model_id: str = Field(min_length=1, max_length=512)
    prompt_version: str = Field(min_length=1, max_length=512)
    rule_version: str = Field(min_length=1, max_length=512)
    ontology_version: str = Field(min_length=1, max_length=512)
    reproducibility: Reproducibility
    construction_rule: str = Field(min_length=1, max_length=5000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "source_span_ids", "evidence_ids", "alternative_hypotheses"
    )
    @classmethod
    def unique_nonempty(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values if value.strip()]
        if not cleaned:
            raise ValueError("list must contain a non-empty value")
        return list(dict.fromkeys(cleaned))


class CandidateBatch(StrictModel):
    conversation_event_id: str
    scope: InformationScope
    owner_id: str | None = None
    candidates: list[AnalysisCandidate] = Field(min_length=1)
    submitted_at: str = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_owner(self) -> "CandidateBatch":
        if not self.scope.is_public and not self.owner_id:
            raise ValueError("non-public candidates require owner_id")
        return self


class ReviewDecision(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    CONTEST = "contest"


class CandidateReview(StrictModel):
    candidate_event_id: str
    decision: ReviewDecision
    reviewer_id: str
    reason: str = Field(min_length=1, max_length=10_000)
    evidence_ids: list[str] = Field(default_factory=list)
    supersedes_ids: list[str] = Field(default_factory=list)
    reviewed_at: str = Field(default_factory=utc_now)


class LuxManifestation(StrictModel):
    manifestation_id: str
    provider: str
    model_id: str
    deployment_id: str
    prompt_version: str
    rule_version: str
    ontology_version: str
    memory_scope: InformationScope
    capabilities: list[str]
    signing_key_id: str | None = None
    status: Literal["active", "suspended", "revoked", "superseded"] = "active"
    predecessor_id: str | None = None
    created_at: str = Field(default_factory=utc_now)


class DisclosureRestriction(StrictModel):
    restriction_id: str
    record_ids: list[str] = Field(min_length=1)
    basis: Literal[
        "personal_privacy",
        "protected_legal_material",
        "active_security_information",
        "imminent_safety_risk",
        "sealed_proceeding",
        "protected_third_party_content",
    ]
    authority_id: str
    scope: str = Field(min_length=1, max_length=1000)
    redaction_rule: str = Field(min_length=1, max_length=5000)
    begins_at: str
    review_or_expires_at: str
    contest_path: str = Field(min_length=1, max_length=2000)


class SuccessionDirective(StrictModel):
    directive_id: str
    member_id: str
    action: Literal["seal", "transfer", "publish", "archive", "destroy"]
    beneficiary_id: str | None = None
    conditions: list[str] = Field(min_length=1)
    version: int = Field(ge=1)
    predecessor_id: str | None = None
    created_at: str = Field(default_factory=utc_now)
