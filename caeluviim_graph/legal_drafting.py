from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class LegalDraftError(ValueError):
    """Raised when a legal-case record cannot be rendered safely."""


REQUIRED_TOP_LEVEL = (
    "case_id",
    "court",
    "caption",
    "jurisdiction_and_venue",
    "parties",
    "facts",
    "causes_of_action",
    "requested_relief",
    "provenance",
)


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LegalDraftError(f"{field} must be a non-empty string")
    return value.strip()


def _require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise LegalDraftError(f"{field} must be a non-empty array")
    return value


def validate_case_record(record: Mapping[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_TOP_LEVEL if field not in record]
    if missing:
        raise LegalDraftError("missing required fields: " + ", ".join(missing))

    case_id = _require_text(record["case_id"], "case_id")
    court = _require_text(record["court"], "court")
    caption = record["caption"]
    if not isinstance(caption, Mapping):
        raise LegalDraftError("caption must be an object")
    plaintiff = _require_text(caption.get("plaintiff"), "caption.plaintiff")
    defendants = [
        _require_text(value, f"caption.defendants[{index}]")
        for index, value in enumerate(_require_list(caption.get("defendants"), "caption.defendants"))
    ]

    facts = _require_list(record["facts"], "facts")
    fact_ids: set[str] = set()
    normalized_facts: list[dict[str, Any]] = []
    for index, fact in enumerate(facts):
        if not isinstance(fact, Mapping):
            raise LegalDraftError(f"facts[{index}] must be an object")
        fact_id = _require_text(fact.get("id"), f"facts[{index}].id")
        if fact_id in fact_ids:
            raise LegalDraftError(f"duplicate fact id: {fact_id}")
        fact_ids.add(fact_id)
        normalized_facts.append(
            {
                "id": fact_id,
                "text": _require_text(fact.get("text"), f"facts[{index}].text"),
                "source_ids": [
                    _require_text(value, f"facts[{index}].source_ids[{source_index}]")
                    for source_index, value in enumerate(
                        _require_list(fact.get("source_ids"), f"facts[{index}].source_ids")
                    )
                ],
            }
        )

    causes = _require_list(record["causes_of_action"], "causes_of_action")
    normalized_causes: list[dict[str, Any]] = []
    for index, cause in enumerate(causes):
        if not isinstance(cause, Mapping):
            raise LegalDraftError(f"causes_of_action[{index}] must be an object")
        incorporated = [
            _require_text(value, f"causes_of_action[{index}].incorporates[{j}]")
            for j, value in enumerate(
                _require_list(cause.get("incorporates"), f"causes_of_action[{index}].incorporates")
            )
        ]
        unknown = sorted(set(incorporated) - fact_ids)
        if unknown:
            raise LegalDraftError(
                f"causes_of_action[{index}] references unknown facts: {', '.join(unknown)}"
            )
        normalized_causes.append(
            {
                "title": _require_text(cause.get("title"), f"causes_of_action[{index}].title"),
                "authority": _require_text(cause.get("authority"), f"causes_of_action[{index}].authority"),
                "elements": [
                    _require_text(value, f"causes_of_action[{index}].elements[{j}]")
                    for j, value in enumerate(
                        _require_list(cause.get("elements"), f"causes_of_action[{index}].elements")
                    )
                ],
                "incorporates": incorporated,
            }
        )

    provenance = record["provenance"]
    if not isinstance(provenance, Mapping):
        raise LegalDraftError("provenance must be an object")
    source_commit = _require_text(provenance.get("source_commit"), "provenance.source_commit")
    manifest_id = _require_text(provenance.get("manifest_id"), "provenance.manifest_id")
    generated_at = _require_text(provenance.get("generated_at"), "provenance.generated_at")

    return {
        "case_id": case_id,
        "court": court,
        "caption": {"plaintiff": plaintiff, "defendants": defendants},
        "jurisdiction_and_venue": [
            _require_text(value, f"jurisdiction_and_venue[{index}]")
            for index, value in enumerate(
                _require_list(record["jurisdiction_and_venue"], "jurisdiction_and_venue")
            )
        ],
        "parties": [
            _require_text(value, f"parties[{index}]")
            for index, value in enumerate(_require_list(record["parties"], "parties"))
        ],
        "facts": normalized_facts,
        "causes_of_action": normalized_causes,
        "requested_relief": [
            _require_text(value, f"requested_relief[{index}]")
            for index, value in enumerate(
                _require_list(record["requested_relief"], "requested_relief")
            )
        ],
        "provenance": {
            "source_commit": source_commit,
            "manifest_id": manifest_id,
            "generated_at": generated_at,
        },
        "verification": record.get("verification"),
    }


def render_complaint(record: Mapping[str, Any]) -> str:
    case = validate_case_record(record)
    defendants = ", ".join(case["caption"]["defendants"])
    lines = [
        case["court"].upper(),
        "",
        f'{case["caption"]["plaintiff"]}, Plaintiff,',
        "v.",
        f"{defendants}, Defendants.",
        "",
        "COMPLAINT",
        "",
        "JURISDICTION AND VENUE",
    ]

    paragraph = 1
    for statement in case["jurisdiction_and_venue"]:
        lines.append(f"{paragraph}. {statement}")
        paragraph += 1

    lines.extend(["", "PARTIES"])
    for statement in case["parties"]:
        lines.append(f"{paragraph}. {statement}")
        paragraph += 1

    lines.extend(["", "FACTUAL ALLEGATIONS"])
    for fact in case["facts"]:
        sources = ", ".join(fact["source_ids"])
        lines.append(f'{paragraph}. {fact["text"]} [Sources: {sources}]')
        paragraph += 1

    for count, cause in enumerate(case["causes_of_action"], start=1):
        lines.extend(["", f"COUNT {count}", cause["title"], f'Authority: {cause["authority"]}'])
        incorporated = ", ".join(cause["incorporates"])
        lines.append(f"{paragraph}. Plaintiff incorporates factual claims {incorporated}.")
        paragraph += 1
        for element in cause["elements"]:
            lines.append(f"{paragraph}. {element}")
            paragraph += 1

    lines.extend(["", "PRAYER FOR RELIEF"])
    for index, relief in enumerate(case["requested_relief"], start=1):
        lines.append(f"{index}. {relief}")

    lines.extend(
        [
            "",
            "DRAFTING PROVENANCE",
            f'Case record: {case["case_id"]}',
            f'Source commit: {case["provenance"]["source_commit"]}',
            f'Manifest: {case["provenance"]["manifest_id"]}',
            f'Generated at: {case["provenance"]["generated_at"]}',
            "Status: machine-generated draft; not filed; legal sufficiency and factual truth not adjudicated.",
        ]
    )

    if case["verification"]:
        lines.extend(["", "VERIFICATION", _require_text(case["verification"], "verification")])

    return "\n".join(lines) + "\n"
