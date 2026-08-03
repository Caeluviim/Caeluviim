from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Iterable, Mapping


class ClosureCheckError(ValueError):
    """Raised when a requested claim cannot be checked."""


DEFAULT_BACKNEST_TYPES = frozenset(
    {
        "DEPENDS_ON",
        "DERIVED_FROM",
        "EVIDENCED_BY",
        "PART_OF",
        "USED_CONTEXT",
        "USED_EVIDENCE_SET",
        "EVALUATED_UNDER_STANDARD",
        "EVALUATED_WITHIN_DOMAIN",
        "HAS_REASON",
        "HAS_ALTERNATIVE",
        "PRESUPPOSES",
    }
)

DEFAULT_FORWARD_TYPES = frozenset(
    {
        "EXTENDS",
        "REVISES",
        "SUPERSEDES",
        "IMPLEMENTS",
        "PROJECTS_TO",
        "PREDICTS",
        "PARTICIPATES_IN",
        "MATERIALIZED",
        "ENTAILS",
    }
)


def _walk(seed: str, adjacency: Mapping[str, set[str]]) -> set[str]:
    visited: set[str] = {seed}
    queue: deque[str] = deque([seed])
    while queue:
        current = queue.popleft()
        for target in sorted(adjacency.get(current, set())):
            if target not in visited:
                visited.add(target)
                queue.append(target)
    return visited


def _string_list(value: Any, property_name: str, claim_id: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ClosureCheckError(
            f"Claim {claim_id} property {property_name} must be an array of strings"
        )
    return value


def check_claim_closure(
    manifest: Mapping[str, Any],
    claim_id: str,
    *,
    backnest_types: Iterable[str] = DEFAULT_BACKNEST_TYPES,
    forward_types: Iterable[str] = DEFAULT_FORWARD_TYPES,
) -> dict[str, Any]:
    """Compute recursive claim closure and report representational necessities.

    Closure is a graph-completeness result. It does not establish substantive truth,
    legal sufficiency, or governance ratification.
    """

    node_by_id = {node["id"]: node for node in manifest.get("nodes", [])}
    if claim_id not in node_by_id:
        raise ClosureCheckError(f"Claim {claim_id} is not present in the manifest")

    claim = node_by_id[claim_id]
    if "Claim" not in claim.get("labels", []):
        raise ClosureCheckError(f"Entity {claim_id} is not labeled Claim")

    backnest_type_set = frozenset(backnest_types)
    forward_type_set = frozenset(forward_types)
    backnest_adjacency: dict[str, set[str]] = defaultdict(set)
    forward_adjacency: dict[str, set[str]] = defaultdict(set)
    outgoing_types: dict[str, set[str]] = defaultdict(set)
    outgoing_targets: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    incoming_supports: dict[str, set[str]] = defaultdict(set)

    for relationship in manifest.get("relationships", []):
        source = relationship["from"]
        target = relationship["to"]
        relationship_type = relationship["type"]
        outgoing_types[source].add(relationship_type)
        outgoing_targets[source][relationship_type].add(target)

        if relationship_type in backnest_type_set:
            backnest_adjacency[source].add(target)
            forward_adjacency[target].add(source)

        if relationship_type in forward_type_set:
            forward_adjacency[source].add(target)

        if relationship_type == "SUPPORTS":
            backnest_adjacency[target].add(source)
            incoming_supports[target].add(source)

    backnest = _walk(claim_id, backnest_adjacency)
    forwardnest = _walk(claim_id, forward_adjacency)
    closure = backnest | forwardnest

    properties = claim.get("properties", {})
    required_relation_types = _string_list(
        properties.get("required_relation_types"),
        "required_relation_types",
        claim_id,
    )
    required_target_ids = _string_list(
        properties.get("required_target_ids"),
        "required_target_ids",
        claim_id,
    )

    missing_relation_types = sorted(
        relationship_type
        for relationship_type in required_relation_types
        if relationship_type not in outgoing_types.get(claim_id, set())
    )
    missing_target_ids = sorted(
        target_id for target_id in required_target_ids if target_id not in closure
    )

    evidence_ids = set(outgoing_targets[claim_id].get("EVIDENCED_BY", set()))
    evidence_ids.update(incoming_supports.get(claim_id, set()))
    evidence_ids = {
        evidence_id
        for evidence_id in evidence_ids
        if "Evidence" in node_by_id.get(evidence_id, {}).get("labels", [])
    }

    minimum_evidence_count = properties.get("minimum_evidence_count", 0)
    if (
        isinstance(minimum_evidence_count, bool)
        or not isinstance(minimum_evidence_count, int)
        or minimum_evidence_count < 0
    ):
        raise ClosureCheckError(
            f"Claim {claim_id} property minimum_evidence_count must be a non-negative integer"
        )

    require_provenance = properties.get("require_provenance", False)
    if not isinstance(require_provenance, bool):
        raise ClosureCheckError(
            f"Claim {claim_id} property require_provenance must be boolean"
        )

    source = manifest.get("source", {})
    provenance_present = bool(
        source.get("source_id")
        and source.get("content_hash")
        and source.get("captured_at")
    )
    evidence_requirement_met = len(evidence_ids) >= minimum_evidence_count
    provenance_requirement_met = not require_provenance or provenance_present

    closure_complete = not (
        missing_relation_types
        or missing_target_ids
        or not evidence_requirement_met
        or not provenance_requirement_met
    )

    return {
        "claim_id": claim_id,
        "backnest": sorted(backnest),
        "forwardnest": sorted(forwardnest),
        "closure": sorted(closure),
        "backnest_count": len(backnest),
        "forwardnest_count": len(forwardnest),
        "closure_count": len(closure),
        "required_relation_types": sorted(required_relation_types),
        "missing_relation_types": missing_relation_types,
        "required_target_ids": sorted(required_target_ids),
        "missing_target_ids": missing_target_ids,
        "evidence_ids": sorted(evidence_ids),
        "evidence_count": len(evidence_ids),
        "minimum_evidence_count": minimum_evidence_count,
        "evidence_requirement_met": evidence_requirement_met,
        "require_provenance": require_provenance,
        "provenance_present": provenance_present,
        "provenance_requirement_met": provenance_requirement_met,
        "closure_complete": closure_complete,
        "truth_assessed": False,
        "ratification_assessed": False,
        "boundary": (
            "Closure reports representational reachability and declared necessities; "
            "it does not establish truth, legal sufficiency, or ratification."
        ),
    }
