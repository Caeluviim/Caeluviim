from __future__ import annotations

import re
from typing import Any, Callable

from .canonical import (
    CanonicalizationError,
    canonical_encode,
    operation_identifiers,
    ruleset_identifier,
)

UNKNOWN = object()
TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _pointer_token(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def resolve_path(context: Any, pointer: Any) -> Any:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        return UNKNOWN
    current = context
    for raw_token in pointer[1:].split("/"):
        token = _pointer_token(raw_token)
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdigit() and int(token) < len(current):
            current = current[int(token)]
        else:
            return UNKNOWN
    return current


def _same_scalar_type(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left is None and right is None
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool)
    return type(left) is type(right) and isinstance(left, (int, str))


def _ordered_compare(left: Any, right: Any) -> int | object:
    if (
        isinstance(left, int)
        and not isinstance(left, bool)
        and isinstance(right, int)
        and not isinstance(right, bool)
    ):
        return (left > right) - (left < right)
    if (
        isinstance(left, str)
        and isinstance(right, str)
        and TIMESTAMP_PATTERN.fullmatch(left)
        and TIMESTAMP_PATTERN.fullmatch(right)
    ):
        return (left > right) - (left < right)
    return UNKNOWN


def _value_key(value: Any) -> str | object:
    if not _same_scalar_type(value, value):
        return UNKNOWN
    return canonical_encode(value)


def _safe_integer_binary(
    left: Any, right: Any, operator: Callable[[int, int], int]
) -> int | object:
    if (
        not isinstance(left, int)
        or isinstance(left, bool)
        or not isinstance(right, int)
        or isinstance(right, bool)
    ):
        return UNKNOWN
    result = operator(left, right)
    if abs(result) > 9_007_199_254_740_991:
        return UNKNOWN
    return result


def scope_contains(
    grant_scope: Any, target_scope: Any, wildcard_enabled: bool = False
) -> bool | object:
    if not isinstance(grant_scope, list) or not isinstance(target_scope, list):
        return UNKNOWN
    for index, segment in enumerate(grant_scope):
        if not isinstance(segment, str):
            return UNKNOWN
        if segment == "**":
            return wildcard_enabled and index == len(grant_scope) - 1
        if index >= len(target_scope):
            return False
        if segment == "*":
            if not wildcard_enabled:
                return False
        elif segment != target_scope[index]:
            return False
    return len(grant_scope) <= len(target_scope)


def evaluate_expression(expression: Any, context: dict[str, Any]) -> Any:
    if expression is None or isinstance(expression, (bool, str, int)):
        return expression
    if isinstance(expression, list):
        return [evaluate_expression(item, context) for item in expression]
    if not isinstance(expression, dict) or len(expression) != 1:
        return UNKNOWN
    operator, argument = next(iter(expression.items()))
    if operator == "path":
        return resolve_path(context, argument)
    if operator == "exists":
        return evaluate_expression(argument, context) is not UNKNOWN
    if operator == "not":
        value = evaluate_expression(argument, context)
        return UNKNOWN if value is UNKNOWN or not isinstance(value, bool) else not value
    if operator in {"all", "any"}:
        if not isinstance(argument, list):
            return UNKNOWN
        values = [evaluate_expression(item, context) for item in argument]
        if any(value is not UNKNOWN and not isinstance(value, bool) for value in values):
            return UNKNOWN
        if operator == "all":
            if False in values:
                return False
            return UNKNOWN if UNKNOWN in values else True
        if True in values:
            return True
        return UNKNOWN if UNKNOWN in values else False
    if operator == "count":
        value = evaluate_expression(argument, context)
        return len(value) if isinstance(value, list) else UNKNOWN
    if operator == "distinct_count":
        if not isinstance(argument, list) or len(argument) != 2:
            return UNKNOWN
        collection = evaluate_expression(argument[0], context)
        field = argument[1]
        if not isinstance(collection, list) or not isinstance(field, str):
            return UNKNOWN
        values = [
            _value_key(item[field])
            if isinstance(item, dict) and field in item
            else UNKNOWN
            for item in collection
        ]
        if UNKNOWN in values:
            return UNKNOWN
        return len(set(values))
    if not isinstance(argument, list) or len(argument) != 2:
        return UNKNOWN
    left = evaluate_expression(argument[0], context)
    right = evaluate_expression(argument[1], context)
    if left is UNKNOWN or right is UNKNOWN:
        return UNKNOWN
    if operator in {"eq", "neq"}:
        if not _same_scalar_type(left, right):
            return UNKNOWN
        return left == right if operator == "eq" else left != right
    if operator in {"lt", "lte", "gt", "gte"}:
        comparison = _ordered_compare(left, right)
        if comparison is UNKNOWN:
            return UNKNOWN
        return {
            "lt": comparison < 0,
            "lte": comparison <= 0,
            "gt": comparison > 0,
            "gte": comparison >= 0,
        }[operator]
    if operator == "in":
        if not isinstance(right, list) or not _same_scalar_type(left, left):
            return UNKNOWN
        needle = _value_key(left)
        values = [_value_key(value) for value in right]
        return UNKNOWN if UNKNOWN in values else needle in values
    if operator in {"contains_all", "subset"}:
        if not isinstance(left, list) or not isinstance(right, list):
            return UNKNOWN
        left_keys = [_value_key(value) for value in left]
        right_keys = [_value_key(value) for value in right]
        if UNKNOWN in left_keys or UNKNOWN in right_keys:
            return UNKNOWN
        candidate = right_keys if operator == "contains_all" else left_keys
        container = set(left_keys if operator == "contains_all" else right_keys)
        return all(item in container for item in candidate)
    if operator == "scope_contains":
        wildcard = context.get("candidate", {}).get("wildcard_scope") is True
        return scope_contains(left, right, wildcard)
    if operator == "add":
        return _safe_integer_binary(left, right, lambda a, b: a + b)
    if operator == "sub":
        return _safe_integer_binary(left, right, lambda a, b: a - b)
    if operator == "mul":
        return _safe_integer_binary(left, right, lambda a, b: a * b)
    if operator == "min":
        return _safe_integer_binary(left, right, min)
    if operator == "max":
        return _safe_integer_binary(left, right, max)
    return UNKNOWN


def ratio_satisfied(actual_weight: Any, base_weight: Any, ratio: Any) -> bool | object:
    values = (
        actual_weight,
        base_weight,
        ratio.get("numerator") if isinstance(ratio, dict) else None,
        ratio.get("denominator") if isinstance(ratio, dict) else None,
    )
    if any(not isinstance(value, int) or isinstance(value, bool) for value in values):
        return UNKNOWN
    numerator, denominator = values[2], values[3]
    if (
        actual_weight < 0
        or base_weight < 0
        or numerator < 0
        or denominator <= 0
    ):
        return UNKNOWN
    if base_weight == 0:
        return False
    return actual_weight * denominator >= base_weight * numerator


def aggregate_authority(
    paths: Any, mode: str, numeric_scale: Any, minimum_weight: int = 0
) -> dict[str, int] | object:
    if not isinstance(paths, list) or not isinstance(numeric_scale, int) or numeric_scale < 1:
        return UNKNOWN
    roots: dict[str, int] = {}
    for path in paths:
        if (
            not isinstance(path, dict)
            or not isinstance(path.get("rootIssuer"), str)
            or not isinstance(path.get("weight"), int)
            or path["weight"] < 0
        ):
            return UNKNOWN
        roots[path["rootIssuer"]] = max(
            roots.get(path["rootIssuer"], 0), path["weight"]
        )
    weights = list(roots.values())
    maximum = max(weights, default=0)
    qualifying = [weight for weight in weights if weight >= minimum_weight]
    if mode in {"maximum", "non_aggregating"}:
        weight = maximum
    elif mode in {"sum_capped", "issuer_diversity"}:
        weight = min(sum(weights), numeric_scale)
    elif mode == "independent_threshold":
        weight = min(qualifying) if qualifying else 0
    else:
        return UNKNOWN
    return {
        "weight": weight,
        "rootIssuers": len(roots),
        "qualifyingRootIssuers": len(qualifying),
    }


__all__ = [
    "UNKNOWN",
    "CanonicalizationError",
    "aggregate_authority",
    "canonical_encode",
    "evaluate_expression",
    "operation_identifiers",
    "ratio_satisfied",
    "resolve_path",
    "ruleset_identifier",
    "scope_contains",
]

