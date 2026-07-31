from __future__ import annotations

import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterator

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .canonical import canonical_bytes, domain_digest, verify_digest
from .keys import SigningIdentity
from .models import InformationScope, utc_now


class LedgerIntegrityError(ValueError):
    pass


class AppendOnlyLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.path.with_suffix(self.path.suffix + ".lock")
        self.lock_path.touch(exist_ok=True)

    def _records_unlocked(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records = []
        with self.path.open("r", encoding="utf-8") as handle:
            for number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise LedgerIntegrityError(
                        f"invalid JSON in {self.path} line {number}"
                    ) from exc
        return records

    @staticmethod
    def _hash_record(sequence: int, previous_hash: str | None, entry: Any) -> str:
        return hashlib.sha256(
            b"CAELUVIIM-APPEND-LOG-0.1\x00"
            + canonical_bytes(
                {
                    "sequence": sequence,
                    "previous_entry_hash": previous_hash,
                    "entry": entry,
                }
            )
        ).hexdigest()

    def append(self, entry: dict[str, Any], id_field: str) -> dict[str, Any]:
        with self.lock_path.open("r+") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            records = self._records_unlocked()
            identifier = entry[id_field]
            for record in records:
                if record["entry"].get(id_field) == identifier:
                    return record
            previous_hash = records[-1]["entry_hash"] if records else None
            sequence = len(records) + 1
            wrapper = {
                "sequence": sequence,
                "previous_entry_hash": previous_hash,
                "entry": entry,
                "entry_hash": self._hash_record(sequence, previous_hash, entry),
            }
            with self.path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(canonical_bytes(wrapper).decode("utf-8") + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            return wrapper

    def records(self) -> list[dict[str, Any]]:
        with self.lock_path.open("r") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_SH)
            return self._records_unlocked()

    def verify(self) -> dict[str, Any]:
        records = self.records()
        previous_hash = None
        for expected_sequence, record in enumerate(records, start=1):
            if record.get("sequence") != expected_sequence:
                raise LedgerIntegrityError(f"sequence mismatch in {self.path}")
            if record.get("previous_entry_hash") != previous_hash:
                raise LedgerIntegrityError(f"chain mismatch in {self.path}")
            expected_hash = self._hash_record(
                expected_sequence, previous_hash, record["entry"]
            )
            if record.get("entry_hash") != expected_hash:
                raise LedgerIntegrityError(f"entry hash mismatch in {self.path}")
            previous_hash = expected_hash
        return {
            "path": str(self.path),
            "count": len(records),
            "root": previous_hash,
        }


class CivicLedger:
    def __init__(self, root: Path):
        root = Path(root)
        self.submissions = AppendOnlyLog(root / "submissions.jsonl")
        self.dispositions = AppendOnlyLog(root / "dispositions.jsonl")
        self.accepted = AppendOnlyLog(root / "accepted.jsonl")

    @staticmethod
    def _event_body(
        *,
        event_type: str,
        actor_id: str,
        signing_key_id: str,
        public_key: str,
        scope: InformationScope,
        owner_token: str | None,
        payload_ref: str,
        evidence_ids: list[str],
        parent_ids: list[str],
        predecessor_id: str | None,
        supersedes_ids: list[str],
        idempotency_key: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "event_version": "caeluviim-event/0.1",
            "event_type": event_type,
            "actor_id": actor_id,
            "signing_key_id": signing_key_id,
            "public_key": public_key,
            "scope": scope.value,
            "owner_token": owner_token,
            "payload_ref": payload_ref,
            "evidence_ids": sorted(set(evidence_ids), key=lambda value: value.encode("utf-8")),
            "parent_ids": sorted(set(parent_ids), key=lambda value: value.encode("utf-8")),
            "predecessor_id": predecessor_id,
            "supersedes_ids": sorted(
                set(supersedes_ids), key=lambda value: value.encode("utf-8")
            ),
            "idempotency_key": idempotency_key,
            "metadata": metadata,
        }

    def submit(
        self,
        *,
        event_type: str,
        signer: SigningIdentity,
        scope: InformationScope,
        payload_ref: str,
        idempotency_key: str,
        disposition: str,
        owner_id: str | None = None,
        evidence_ids: list[str] | None = None,
        parent_ids: list[str] | None = None,
        predecessor_id: str | None = None,
        supersedes_ids: list[str] | None = None,
        reason_codes: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        existing_event = next(
            (
                event
                for event in self.events()
                if event["idempotency_key"] == idempotency_key
            ),
            None,
        )
        owner_token = (
            hashlib.sha256(owner_id.encode("utf-8")).hexdigest() if owner_id else None
        )
        body = self._event_body(
            event_type=event_type,
            actor_id=signer.identity_id,
            signing_key_id=signer.key_id,
            public_key=signer.public_key_base64url,
            scope=scope,
            owner_token=owner_token,
            payload_ref=payload_ref,
            evidence_ids=evidence_ids or [],
            parent_ids=parent_ids or [],
            predecessor_id=predecessor_id,
            supersedes_ids=supersedes_ids or [],
            idempotency_key=idempotency_key,
            metadata=metadata or {},
        )
        if existing_event is not None:
            existing_body = {
                key: value
                for key, value in existing_event.items()
                if key not in {"event_id", "signature", "recorded_at"}
            }
            if existing_body != body:
                raise LedgerIntegrityError(
                    f"idempotency key reused with different event body: {idempotency_key}"
                )
            dispositions = self.dispositions_by_event().get(
                existing_event["event_id"], []
            )
            if not dispositions:
                raise LedgerIntegrityError(
                    f"idempotent event has no disposition: {existing_event['event_id']}"
                )
            existing_disposition = dispositions[-1]
            acceptance = next(
                (
                    record["entry"]
                    for record in self.accepted.records()
                    if record["entry"]["event_id"] == existing_event["event_id"]
                ),
                None,
            )
            return {
                "event": existing_event,
                "disposition": existing_disposition,
                "acceptance": acceptance,
                "accepted": acceptance is not None,
                "idempotent_replay": True,
            }
        digest = domain_digest("CAELUVIIM-EVENT-0.1", body)
        event_id = f"urn:caeluviim:event:sha256:{digest.hex()}"
        event = {
            **body,
            "event_id": event_id,
            "signature": {
                "algorithm": "Ed25519",
                "value": signer.sign(digest),
            },
            "recorded_at": utc_now(),
        }
        submission_record = self.submissions.append(event, "event_id")
        event = submission_record["entry"]
        disposition_body = {
            "disposition_id": f"urn:caeluviim:disposition:sha256:{hashlib.sha256(canonical_bytes({'event_id': event_id, 'disposition': disposition, 'reason_codes': reason_codes or []})).hexdigest()}",
            "event_id": event_id,
            "disposition": disposition,
            "reason_codes": reason_codes or [],
            "recorded_at": utc_now(),
        }
        disposition_record = self.dispositions.append(
            disposition_body, "disposition_id"
        )
        disposition_body = disposition_record["entry"]
        if disposition.startswith("ACCEPTED"):
            acceptance_record = self.accepted.append(
                {
                    "acceptance_id": f"urn:caeluviim:acceptance:{event_id.rsplit(':', 1)[-1]}",
                    "event_id": event_id,
                    "disposition_id": disposition_body["disposition_id"],
                    "recorded_at": utc_now(),
                },
                "acceptance_id",
            )
        else:
            acceptance_record = None
        return {
            "event": event,
            "disposition": disposition_body,
            "acceptance": acceptance_record["entry"] if acceptance_record else None,
            "accepted": disposition_body["disposition"].startswith("ACCEPTED"),
            "idempotent_replay": False,
        }

    def events(self, accepted_only: bool = False) -> list[dict[str, Any]]:
        submissions = {
            record["entry"]["event_id"]: record["entry"]
            for record in self.submissions.records()
        }
        if not accepted_only:
            return list(submissions.values())
        accepted_ids = [
            record["entry"]["event_id"] for record in self.accepted.records()
        ]
        return [submissions[event_id] for event_id in accepted_ids]

    def dispositions_by_event(self) -> dict[str, list[dict[str, Any]]]:
        result: dict[str, list[dict[str, Any]]] = {}
        for record in self.dispositions.records():
            entry = record["entry"]
            result.setdefault(entry["event_id"], []).append(entry)
        return result

    def event(self, event_id: str) -> dict[str, Any]:
        for event in self.events():
            if event["event_id"] == event_id:
                return event
        raise KeyError(event_id)

    @staticmethod
    def _verify_event(event: dict[str, Any]) -> None:
        body = {
            key: value
            for key, value in event.items()
            if key not in {"event_id", "signature", "recorded_at"}
        }
        digest = domain_digest("CAELUVIIM-EVENT-0.1", body)
        expected_id = f"urn:caeluviim:event:sha256:{digest.hex()}"
        if event["event_id"] != expected_id:
            raise LedgerIntegrityError(f"event identifier mismatch: {event['event_id']}")
        padding = "=" * ((4 - len(event["public_key"]) % 4) % 4)
        public_key = Ed25519PublicKey.from_public_bytes(
            base64.urlsafe_b64decode(event["public_key"] + padding)
        )
        if not verify_digest(public_key, digest, event["signature"]["value"]):
            raise LedgerIntegrityError(f"event signature mismatch: {event['event_id']}")

    def verify(self) -> dict[str, Any]:
        logs = {
            "submissions": self.submissions.verify(),
            "dispositions": self.dispositions.verify(),
            "accepted": self.accepted.verify(),
        }
        for event in self.events():
            self._verify_event(event)
        events_by_id = {event["event_id"]: event for event in self.events()}
        dispositions = [
            record["entry"] for record in self.dispositions.records()
        ]
        dispositions_by_id = {
            disposition["disposition_id"]: disposition
            for disposition in dispositions
        }
        for disposition in dispositions:
            if disposition["event_id"] not in events_by_id:
                raise LedgerIntegrityError(
                    f"disposition references missing event: {disposition['event_id']}"
                )
        for record in self.accepted.records():
            acceptance = record["entry"]
            if acceptance["event_id"] not in events_by_id:
                raise LedgerIntegrityError(
                    f"acceptance references missing event: {acceptance['event_id']}"
                )
            disposition = dispositions_by_id.get(acceptance["disposition_id"])
            if not disposition:
                raise LedgerIntegrityError(
                    "acceptance references missing disposition: "
                    + acceptance["disposition_id"]
                )
            if disposition["event_id"] != acceptance["event_id"]:
                raise LedgerIntegrityError(
                    f"acceptance/disposition event mismatch: {acceptance['event_id']}"
                )
            if not disposition["disposition"].startswith("ACCEPTED"):
                raise LedgerIntegrityError(
                    f"acceptance uses non-accepting disposition: {acceptance['event_id']}"
                )
        accepted_ids = [event["event_id"] for event in self.events(accepted_only=True)]
        state_root = hashlib.sha256(canonical_bytes(accepted_ids)).hexdigest()
        return {
            "logs": logs,
            "event_signatures": len(self.events()),
            "accepted_event_count": len(accepted_ids),
            "state_root": f"sha256:{state_root}",
        }
