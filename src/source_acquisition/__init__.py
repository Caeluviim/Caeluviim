"""Deterministic source acquisition and lifecycle boundary."""

from .evaluator import (
    AcquisitionEvaluationError,
    evaluate_manifest,
    intake_eligible_payload,
    load_json,
    validate_json_document,
    validate_rdf_manifest,
    verify_cross_format_alignment,
)
from .store import AcquisitionGraphCollisionError, LocalSourceAcquisitionStore

__all__ = [
    "AcquisitionEvaluationError",
    "AcquisitionGraphCollisionError",
    "LocalSourceAcquisitionStore",
    "evaluate_manifest",
    "intake_eligible_payload",
    "load_json",
    "validate_json_document",
    "validate_rdf_manifest",
    "verify_cross_format_alignment",
]
