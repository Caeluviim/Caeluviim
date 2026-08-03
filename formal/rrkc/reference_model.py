"""Executable reference model for the RRKC R2 core calculus.

This module implements the closed syntax needed to test formation,
capture-avoiding substitution, governed revision, canonical quotation and
evaluation, and provenance replay. It is an executable reference, not a
replacement for the Lean metatheory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping


class RRKCError(ValueError):
    """Base error for malformed RRKC terms or states."""


class TypeErrorRRKC(RRKCError):
    """Raised when a term is not well sorted."""


class ProvenanceError(RRKCError):
    """Raised when a provenance structure violates its invariants."""


@dataclass(frozen=True, order=True)
class Sort:
    name: str
    args: tuple["Sort", ...] = ()

    def __str__(self) -> str:
        if self.name == "Code":
            return f"Code({self.args[0]})"
        if self.name == "Arrow":
            return f"({self.args[0]} -> {self.args[1]})"
        return self.name


def Code(inner: Sort) -> Sort:
    return Sort("Code", (inner,))


def Arrow(domain: Sort, codomain: Sort) -> Sort:
    return Sort("Arrow", (domain, codomain))


ENTITY = Sort("Entity")
CLAIM = Sort("Claim")
EVIDENCE = Sort("Evidence")
RELATION = Sort("Relation")
ACTIVITY = Sort("Activity")
AGENT = Sort("Agent")
POLICY = Sort("Policy")
PROVENANCE = Sort("Provenance")


class Term:
    """Marker base class for R0/RE/RR terms."""


@dataclass(frozen=True)
class Var(Term):
    name: str
    sort: Sort


@dataclass(frozen=True)
class Id(Term):
    value: str


@dataclass(frozen=True)
class ClaimEntity(Term):
    claim: Term


@dataclass(frozen=True)
class EvidenceEntity(Term):
    evidence: Term


@dataclass(frozen=True)
class Rel(Term):
    relation: str
    left: Term
    right: Term


@dataclass(frozen=True)
class Act(Term):
    operation: str
    arguments: tuple[Term, ...]


@dataclass(frozen=True)
class Stamp(Term):
    term: Term
    provenance: Term


@dataclass(frozen=True)
class Revise(Term):
    source: Term
    target: Term


@dataclass(frozen=True)
class Version(Term):
    term: Term
    version: str


@dataclass(frozen=True)
class Lam(Term):
    variable: Var
    body: Term


@dataclass(frozen=True)
class App(Term):
    function: Term
    argument: Term


@dataclass(frozen=True)
class Let(Term):
    variable: Var
    value: Term
    body: Term


@dataclass(frozen=True)
class Quote(Term):
    term: Term


@dataclass(frozen=True)
class Eval(Term):
    code: Term


@dataclass(frozen=True)
class RelationProfile:
    left: Sort
    right: Sort


@dataclass(frozen=True)
class OperationProfile:
    inputs: tuple[Sort, ...]
    output: Sort


@dataclass(frozen=True)
class Signature:
    relations: Mapping[str, RelationProfile] = field(default_factory=dict)
    operations: Mapping[str, OperationProfile] = field(default_factory=dict)


Context = Mapping[str, Sort]


def free_vars(term: Term) -> frozenset[str]:
    match term:
        case Var(name, _):
            return frozenset({name})
        case Id():
            return frozenset()
        case ClaimEntity(inner) | EvidenceEntity(inner) | Version(inner, _) | Quote(inner) | Eval(inner):
            return free_vars(inner)
        case Stamp(inner, provenance):
            return free_vars(inner) | free_vars(provenance)
        case Rel(_, left, right) | Revise(left, right) | App(left, right):
            return free_vars(left) | free_vars(right)
        case Act(_, arguments):
            return frozenset().union(*(free_vars(arg) for arg in arguments))
        case Lam(variable, body):
            return free_vars(body) - {variable.name}
        case Let(variable, value, body):
            return free_vars(value) | (free_vars(body) - {variable.name})
        case _:
            raise RRKCError(f"Unknown term: {term!r}")


def bound_vars(term: Term) -> frozenset[str]:
    match term:
        case Var() | Id():
            return frozenset()
        case ClaimEntity(inner) | EvidenceEntity(inner) | Version(inner, _) | Quote(inner) | Eval(inner):
            return bound_vars(inner)
        case Stamp(inner, provenance):
            return bound_vars(inner) | bound_vars(provenance)
        case Rel(_, left, right) | Revise(left, right) | App(left, right):
            return bound_vars(left) | bound_vars(right)
        case Act(_, arguments):
            return frozenset().union(*(bound_vars(arg) for arg in arguments))
        case Lam(variable, body):
            return bound_vars(body) | {variable.name}
        case Let(variable, value, body):
            return bound_vars(value) | bound_vars(body) | {variable.name}
        case _:
            raise RRKCError(f"Unknown term: {term!r}")


def _fresh_name(base: str, forbidden: Iterable[str]) -> str:
    used = set(forbidden)
    if base not in used:
        return base
    index = 1
    while f"{base}_{index}" in used:
        index += 1
    return f"{base}_{index}"


def _rename_bound_occurrences(term: Term, old: str, new: str) -> Term:
    """Rename occurrences bound by the immediately surrounding binder."""
    match term:
        case Var(name, sort):
            return Var(new if name == old else name, sort)
        case Id():
            return term
        case ClaimEntity(inner):
            return ClaimEntity(_rename_bound_occurrences(inner, old, new))
        case EvidenceEntity(inner):
            return EvidenceEntity(_rename_bound_occurrences(inner, old, new))
        case Rel(relation, left, right):
            return Rel(
                relation,
                _rename_bound_occurrences(left, old, new),
                _rename_bound_occurrences(right, old, new),
            )
        case Act(operation, arguments):
            return Act(
                operation,
                tuple(_rename_bound_occurrences(arg, old, new) for arg in arguments),
            )
        case Stamp(inner, provenance):
            return Stamp(
                _rename_bound_occurrences(inner, old, new),
                _rename_bound_occurrences(provenance, old, new),
            )
        case Revise(source, target):
            return Revise(
                _rename_bound_occurrences(source, old, new),
                _rename_bound_occurrences(target, old, new),
            )
        case Version(inner, version):
            return Version(_rename_bound_occurrences(inner, old, new), version)
        case Quote(inner):
            return Quote(_rename_bound_occurrences(inner, old, new))
        case Eval(code):
            return Eval(_rename_bound_occurrences(code, old, new))
        case App(function, argument):
            return App(
                _rename_bound_occurrences(function, old, new),
                _rename_bound_occurrences(argument, old, new),
            )
        case Lam(variable, body):
            if variable.name == old:
                return term
            return Lam(variable, _rename_bound_occurrences(body, old, new))
        case Let(variable, value, body):
            renamed_value = _rename_bound_occurrences(value, old, new)
            if variable.name == old:
                return Let(variable, renamed_value, body)
            return Let(
                variable,
                renamed_value,
                _rename_bound_occurrences(body, old, new),
            )
        case _:
            raise RRKCError(f"Unknown term: {term!r}")


def substitute(term: Term, variable: str, replacement: Term) -> Term:
    """Capture-avoiding substitution term[replacement/variable]."""
    replacement_fv = free_vars(replacement)
    match term:
        case Var(name, _):
            return replacement if name == variable else term
        case Id():
            return term
        case ClaimEntity(inner):
            return ClaimEntity(substitute(inner, variable, replacement))
        case EvidenceEntity(inner):
            return EvidenceEntity(substitute(inner, variable, replacement))
        case Rel(relation, left, right):
            return Rel(
                relation,
                substitute(left, variable, replacement),
                substitute(right, variable, replacement),
            )
        case Act(operation, arguments):
            return Act(
                operation,
                tuple(substitute(arg, variable, replacement) for arg in arguments),
            )
        case Stamp(inner, provenance):
            return Stamp(
                substitute(inner, variable, replacement),
                substitute(provenance, variable, replacement),
            )
        case Revise(source, target):
            return Revise(
                substitute(source, variable, replacement),
                substitute(target, variable, replacement),
            )
        case Version(inner, version):
            return Version(substitute(inner, variable, replacement), version)
        case Quote(inner):
            return Quote(substitute(inner, variable, replacement))
        case Eval(code):
            return Eval(substitute(code, variable, replacement))
        case App(function, argument):
            return App(
                substitute(function, variable, replacement),
                substitute(argument, variable, replacement),
            )
        case Lam(bound, body):
            if bound.name == variable:
                return term
            if bound.name in replacement_fv:
                fresh = _fresh_name(
                    bound.name,
                    free_vars(body) | replacement_fv | {variable},
                )
                renamed = _rename_bound_occurrences(body, bound.name, fresh)
                return Lam(
                    Var(fresh, bound.sort),
                    substitute(renamed, variable, replacement),
                )
            return Lam(bound, substitute(body, variable, replacement))
        case Let(bound, value, body):
            new_value = substitute(value, variable, replacement)
            if bound.name == variable:
                return Let(bound, new_value, body)
            if bound.name in replacement_fv:
                fresh = _fresh_name(
                    bound.name,
                    free_vars(body) | replacement_fv | {variable},
                )
                renamed = _rename_bound_occurrences(body, bound.name, fresh)
                return Let(
                    Var(fresh, bound.sort),
                    new_value,
                    substitute(renamed, variable, replacement),
                )
            return Let(
                bound,
                new_value,
                substitute(body, variable, replacement),
            )
        case _:
            raise RRKCError(f"Unknown term: {term!r}")


def type_of(context: Context, term: Term, signature: Signature) -> Sort:
    match term:
        case Var(name, declared):
            actual = context.get(name)
            if actual is None:
                raise TypeErrorRRKC(f"Unbound variable {name}")
            if actual != declared:
                raise TypeErrorRRKC(
                    f"Variable {name} declared {declared}, context requires {actual}"
                )
            return declared
        case Id():
            return ENTITY
        case ClaimEntity(claim):
            if type_of(context, claim, signature) != CLAIM:
                raise TypeErrorRRKC("claim(...) requires Claim content")
            return ENTITY
        case EvidenceEntity(evidence):
            if type_of(context, evidence, signature) != EVIDENCE:
                raise TypeErrorRRKC("evidence(...) requires Evidence content")
            return ENTITY
        case Rel(relation, left, right):
            profile = signature.relations.get(relation)
            if profile is None:
                raise TypeErrorRRKC(f"Unknown relation symbol {relation}")
            actual = (
                type_of(context, left, signature),
                type_of(context, right, signature),
            )
            expected = (profile.left, profile.right)
            if actual != expected:
                raise TypeErrorRRKC(
                    f"Relation {relation} expected {expected}, got {actual}"
                )
            return RELATION
        case Act(operation, arguments):
            profile = signature.operations.get(operation)
            if profile is None:
                raise TypeErrorRRKC(f"Unknown operation symbol {operation}")
            actual = tuple(type_of(context, arg, signature) for arg in arguments)
            if actual != profile.inputs:
                raise TypeErrorRRKC(
                    f"Operation {operation} expected {profile.inputs}, got {actual}"
                )
            return profile.output
        case Stamp(inner, provenance):
            inner_sort = type_of(context, inner, signature)
            if type_of(context, provenance, signature) != PROVENANCE:
                raise TypeErrorRRKC("stamp provenance must have sort Provenance")
            return inner_sort
        case Revise(source, target):
            source_sort = type_of(context, source, signature)
            target_sort = type_of(context, target, signature)
            if source_sort != target_sort:
                raise TypeErrorRRKC(
                    f"Revision changes sort from {source_sort} to {target_sort}"
                )
            return source_sort
        case Version(inner, _):
            return type_of(context, inner, signature)
        case Lam(variable, body):
            extended = dict(context)
            extended[variable.name] = variable.sort
            return Arrow(
                variable.sort,
                type_of(extended, body, signature),
            )
        case App(function, argument):
            function_sort = type_of(context, function, signature)
            argument_sort = type_of(context, argument, signature)
            if function_sort.name != "Arrow":
                raise TypeErrorRRKC(
                    f"Application requires function sort, got {function_sort}"
                )
            domain, codomain = function_sort.args
            if argument_sort != domain:
                raise TypeErrorRRKC(
                    f"Application expected {domain}, got {argument_sort}"
                )
            return codomain
        case Let(variable, value, body):
            value_sort = type_of(context, value, signature)
            if value_sort != variable.sort:
                raise TypeErrorRRKC(
                    f"Let binder declares {variable.sort}, value has {value_sort}"
                )
            extended = dict(context)
            extended[variable.name] = variable.sort
            return type_of(extended, body, signature)
        case Quote(inner):
            return Code(type_of(context, inner, signature))
        case Eval(code):
            code_sort = type_of(context, code, signature)
            if code_sort.name != "Code":
                raise TypeErrorRRKC(f"eval requires Code sort, got {code_sort}")
            return code_sort.args[0]
        case _:
            raise TypeErrorRRKC(f"Unknown term: {term!r}")


@dataclass(frozen=True)
class GovernanceState:
    admissible_revisions: frozenset[tuple[Term, Term]] = frozenset()
    blocked_transitions: frozenset[tuple[Term, Term]] = frozenset()

    def admits(self, source: Term, target: Term) -> bool:
        transition = (source, target)
        return (
            transition in self.admissible_revisions
            and transition not in self.blocked_transitions
        )


class StepKind(str, Enum):
    REDUCED = "reduced"
    VALUE = "value"
    BLOCKED = "blocked"
    STUCK = "stuck"


@dataclass(frozen=True)
class StepResult:
    kind: StepKind
    term: Term
    reason: str | None = None


def is_value(term: Term) -> bool:
    return isinstance(term, (Var, Id, Lam, Quote))


def step(term: Term, governance: GovernanceState) -> StepResult:
    match term:
        case App(Lam(variable, body), argument) if is_value(argument):
            return StepResult(
                StepKind.REDUCED,
                substitute(body, variable.name, argument),
                "beta",
            )
        case App(function, argument) if not is_value(function):
            function_step = step(function, governance)
            if function_step.kind == StepKind.REDUCED:
                return StepResult(
                    StepKind.REDUCED,
                    App(function_step.term, argument),
                    "app-left",
                )
            return StepResult(function_step.kind, term, function_step.reason)
        case App(function, argument) if is_value(function) and not is_value(argument):
            argument_step = step(argument, governance)
            if argument_step.kind == StepKind.REDUCED:
                return StepResult(
                    StepKind.REDUCED,
                    App(function, argument_step.term),
                    "app-right",
                )
            return StepResult(argument_step.kind, term, argument_step.reason)
        case Let(variable, value, body) if is_value(value):
            return StepResult(
                StepKind.REDUCED,
                substitute(body, variable.name, value),
                "let",
            )
        case Let(variable, value, body):
            value_step = step(value, governance)
            if value_step.kind == StepKind.REDUCED:
                return StepResult(
                    StepKind.REDUCED,
                    Let(variable, value_step.term, body),
                    "let-value",
                )
            return StepResult(value_step.kind, term, value_step.reason)
        case Eval(Quote(inner)):
            return StepResult(StepKind.REDUCED, inner, "eval-quote")
        case Revise(source, target):
            if governance.admits(source, target):
                return StepResult(
                    StepKind.REDUCED,
                    target,
                    "governed-revision",
                )
            return StepResult(
                StepKind.BLOCKED,
                term,
                "revision-not-admissible",
            )
        case _ if is_value(term):
            return StepResult(StepKind.VALUE, term)
        case _:
            return StepResult(StepKind.STUCK, term, "no-reduction-rule")


def normalize(
    term: Term,
    governance: GovernanceState,
    *,
    fuel: int = 1000,
) -> Term:
    current = term
    for _ in range(fuel):
        result = step(current, governance)
        if result.kind in {StepKind.VALUE, StepKind.BLOCKED}:
            return current
        if result.kind == StepKind.STUCK:
            raise RRKCError(result.reason or "stuck")
        current = result.term
    raise RRKCError("normalization fuel exhausted; term may be outside K_SN")


@dataclass(frozen=True)
class ProvenanceEvent:
    event_id: str
    label: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProvenanceGraph:
    events: tuple[ProvenanceEvent, ...]
    precedence: frozenset[tuple[str, str]]

    def event_map(self) -> dict[str, ProvenanceEvent]:
        result = {event.event_id: event for event in self.events}
        if len(result) != len(self.events):
            raise ProvenanceError("Event identifiers must be unique")
        return result

    def validate(self) -> None:
        events = self.event_map()
        for left, right in self.precedence:
            if left not in events or right not in events:
                raise ProvenanceError(
                    "Precedence endpoint is not a recorded event"
                )
            if left == right:
                raise ProvenanceError("Strict precedence is irreflexive")

        adjacency: dict[str, set[str]] = {
            event_id: set() for event_id in events
        }
        indegree: dict[str, int] = {
            event_id: 0 for event_id in events
        }
        for left, right in self.precedence:
            if right not in adjacency[left]:
                adjacency[left].add(right)
                indegree[right] += 1
        frontier = [
            event_id
            for event_id, degree in indegree.items()
            if degree == 0
        ]
        visited = 0
        while frontier:
            current = frontier.pop()
            visited += 1
            for target in adjacency[current]:
                indegree[target] -= 1
                if indegree[target] == 0:
                    frontier.append(target)
        if visited != len(events):
            raise ProvenanceError("Strict precedence must be acyclic")

    def replay(self) -> "ProvenanceGraph":
        self.validate()
        reconstructed = tuple(
            ProvenanceEvent(
                event.event_id,
                event.label,
                tuple(event.inputs),
                tuple(event.outputs),
            )
            for event in self.events
        )
        return ProvenanceGraph(
            reconstructed,
            frozenset(self.precedence),
        )

    def isomorphic_to(self, other: "ProvenanceGraph") -> bool:
        self.validate()
        other.validate()
        return (
            self.event_map() == other.event_map()
            and self.precedence == other.precedence
        )


def substitution_preserves_sort(
    context: Context,
    body: Term,
    variable: Var,
    replacement: Term,
    signature: Signature,
) -> bool:
    """Executable T2 checker for a concrete derivation instance."""
    extended = dict(context)
    extended[variable.name] = variable.sort
    body_sort = type_of(extended, body, signature)
    replacement_sort = type_of(context, replacement, signature)
    if replacement_sort != variable.sort:
        return False
    return (
        type_of(
            context,
            substitute(body, variable.name, replacement),
            signature,
        )
        == body_sort
    )


def preservation_holds(
    context: Context,
    term: Term,
    signature: Signature,
    governance: GovernanceState,
) -> bool:
    source_sort = type_of(context, term, signature)
    result = step(term, governance)
    if result.kind != StepKind.REDUCED:
        return True
    return type_of(context, result.term, signature) == source_sort


def governed_progress_holds(
    context: Context,
    term: Term,
    signature: Signature,
    governance: GovernanceState,
) -> bool:
    type_of(context, term, signature)
    result = step(term, governance)
    return result.kind in {
        StepKind.VALUE,
        StepKind.REDUCED,
        StepKind.BLOCKED,
    }
