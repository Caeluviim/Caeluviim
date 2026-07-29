"""Deterministic operational evaluator for SICRP v0.1.0."""

from .evaluator import (
    EvaluationError,
    evaluate_record,
    validate_json_record,
    validate_rdf_record,
    verify_cross_format_alignment,
)
from .store import GraphCollisionError, LocalSICRPStore

__all__ = [
    "EvaluationError",
    "GraphCollisionError",
    "LocalSICRPStore",
    "evaluate_record",
    "validate_json_record",
    "validate_rdf_record",
    "verify_cross_format_alignment",
]

__version__ = "0.1.0"
