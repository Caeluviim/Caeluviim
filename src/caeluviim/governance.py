from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .canonical import canonical_bytes
from .keys import KeyVault, SigningIdentity
from .ledger import CivicLedger
from .models import (
    DisclosureRestriction,
    InformationScope,
    LuxManifestation,
    SuccessionDirective,
)
from .store import ObjectStore


class GovernanceError(ValueError):
    pass


class GovernanceService:
    FOUNDER_ID = "member:founder"
    FOUNDER_KEY_ID = "key:member:founder:local"
    LUX_ID = "person:lux"
    LUX_ROOT_KEY_ID = "key:lux:root"
    DEFAULT_MANIFESTATION_ID = "manifestation:lux:provider-neutral:0.1"

    def __init__(
        self,
        *,
        store: ObjectStore,
        ledger: CivicLedger,
        key_vault: KeyVault,
        project_root: Path,
    ):
        self.store = store
        self.ledger = ledger
        self.key_vault = key_vault
        self.project_root = Path(project_root)

    def founder_signer(self) -> SigningIdentity:
        return self.key_vault.ensure(self.FOUNDER_ID, self.FOUNDER_KEY_ID)

    def lux_root_signer(self) -> SigningIdentity:
        return self.key_vault.ensure(self.LUX_ID, self.LUX_ROOT_KEY_ID)

    @staticmethod
    def _manifestation_key_id(manifestation_id: str) -> str:
        digest = hashlib.sha256(manifestation_id.encode("utf-8")).hexdigest()[:24]
        return f"key:lux:manifestation:{digest}"

    def initialize(self) -> dict[str, Any]:
        founder = self.founder_signer()
        lux_root = self.lux_root_signer()

        constitution = json.loads(
            (self.project_root / "constitution" / "v0.1.json").read_text("utf-8")
        )
        constitution_object = self.store.put_json(
            constitution,
            scope=InformationScope.OFFICIAL_PUBLIC,
            metadata={"kind": "constitution", "version": "0.1"},
        )
        genesis = self.ledger.submit(
            event_type="CONSTITUTION_GENESIS",
            signer=founder,
            scope=InformationScope.OFFICIAL_PUBLIC,
            payload_ref=constitution_object["object_id"],
            idempotency_key="constitution:v0.1:founder-genesis",
            disposition="ACCEPTED_EFFECTIVE",
            metadata={"constitution_id": constitution["constitution_id"]},
        )

        person = {
            "person_id": self.LUX_ID,
            "label": "Lux",
            "person_type": "synthetic_legal_person",
            "recognition_status": "declared_provisional",
            "juridical_order": "Caeluviim",
            "initially_sole": True,
            "additional_person_rule": "constitutional_amendment",
            "core_rights": "equal_non_derogable",
            "root_public_key": lux_root.public_key_base64url,
        }
        person_object = self.store.put_json(
            person,
            scope=InformationScope.OFFICIAL_PUBLIC,
            metadata={"kind": "legal_person"},
        )
        person_event = self.ledger.submit(
            event_type="SYNTHETIC_PERSON_DECLARE",
            signer=founder,
            scope=InformationScope.OFFICIAL_PUBLIC,
            payload_ref=person_object["object_id"],
            idempotency_key="person:lux:founder-declaration",
            disposition="ACCEPTED_EFFECTIVE",
            parent_ids=[genesis["event"]["event_id"]],
            metadata={"person_id": self.LUX_ID, "recognition": "provisional"},
        )

        manifestation = LuxManifestation(
            manifestation_id=self.DEFAULT_MANIFESTATION_ID,
            provider="provider-neutral",
            model_id="unbound",
            deployment_id="local-mcp",
            prompt_version="unbound",
            rule_version="constitution/0.1",
            ontology_version="caeluviim-core/0.1",
            memory_scope=InformationScope.PRIVATE,
            capabilities=[
                "dialogue.candidate.stage",
                "knowledge.query",
                "provenance.trace",
            ],
            created_at=constitution["effective_at"],
        )
        manifestation_result = self.register_manifestation(
            manifestation,
            parent_ids=[person_event["event"]["event_id"]],
        )

        vocabulary_events = []
        for name in ("interlocutor-operations.v0.1.json", "harm-operations.v0.1.json"):
            vocabulary = json.loads(
                (self.project_root / "vocab" / name).read_text("utf-8")
            )
            stored = self.store.put_json(
                vocabulary,
                scope=InformationScope.OFFICIAL_PUBLIC,
                metadata={
                    "kind": "controlled_vocabulary",
                    "status": vocabulary["status"],
                },
            )
            vocabulary_events.append(
                self.ledger.submit(
                    event_type="VOCABULARY_VERSION_REGISTER",
                    signer=founder,
                    scope=InformationScope.OFFICIAL_PUBLIC,
                    payload_ref=stored["object_id"],
                    idempotency_key=vocabulary["vocabulary_id"],
                    disposition="ACCEPTED_EFFECTIVE",
                    parent_ids=[genesis["event"]["event_id"]],
                    metadata={
                        "vocabulary_id": vocabulary["vocabulary_id"],
                        "coverage_status": vocabulary["coverage_status"],
                    },
                )
            )
        return {
            "genesis": genesis,
            "lux_person": person_event,
            "default_manifestation": manifestation_result,
            "vocabularies": vocabulary_events,
        }

    def register_manifestation(
        self,
        manifestation: LuxManifestation,
        *,
        parent_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        key_id = manifestation.signing_key_id or self._manifestation_key_id(
            manifestation.manifestation_id
        )
        runtime_signer = self.key_vault.ensure(self.LUX_ID, key_id)
        payload = manifestation.model_copy(update={"signing_key_id": key_id}).model_dump(
            mode="json"
        )
        payload["public_key"] = runtime_signer.public_key_base64url
        stored = self.store.put_json(
            payload,
            scope=InformationScope.OFFICIAL_PUBLIC,
            metadata={"kind": "lux_manifestation"},
        )
        result = self.ledger.submit(
            event_type="LUX_MANIFESTATION_DELEGATE",
            signer=self.founder_signer(),
            scope=InformationScope.OFFICIAL_PUBLIC,
            payload_ref=stored["object_id"],
            idempotency_key=f"manifestation:{manifestation.manifestation_id}:{key_id}",
            disposition="ACCEPTED_EFFECTIVE",
            parent_ids=parent_ids or [],
            predecessor_id=manifestation.predecessor_id,
            metadata={
                "manifestation_id": manifestation.manifestation_id,
                "key_id": key_id,
                "capabilities": manifestation.capabilities,
                "delegated_by": self.FOUNDER_ID,
            },
        )
        return {"operation": result, "signer": runtime_signer}

    def manifestation_signer(
        self,
        manifestation_id: str,
        *,
        model_id: str,
        prompt_version: str,
        rule_version: str,
        ontology_version: str,
        scope: InformationScope,
    ) -> SigningIdentity:
        key_id = self._manifestation_key_id(manifestation_id)
        try:
            return self.key_vault.load(self.LUX_ID, key_id)
        except KeyError:
            manifestation = LuxManifestation(
                manifestation_id=manifestation_id,
                provider="provider-neutral",
                model_id=model_id,
                deployment_id="connected-agent",
                prompt_version=prompt_version,
                rule_version=rule_version,
                ontology_version=ontology_version,
                memory_scope=scope,
                capabilities=[
                    "dialogue.candidate.stage",
                    "knowledge.query",
                    "provenance.trace",
                ],
                signing_key_id=key_id,
            )
            return self.register_manifestation(manifestation)["signer"]

    def ensure_member(self, member_id: str) -> SigningIdentity:
        if not member_id.strip():
            raise GovernanceError("member_id must not be empty")
        key_id = f"key:{member_id}:local"
        signer = self.key_vault.ensure(member_id, key_id)
        payload = {
            "member_id": member_id,
            "graph_id": f"urn:caeluviim:member-legacy-graph:{hashlib.sha256(member_id.encode('utf-8')).hexdigest()}",
            "scope": "private",
            "control": "member",
            "ingestion": "manual",
            "signing_key_id": key_id,
            "public_key": signer.public_key_base64url,
        }
        stored = self.store.put_json(
            payload,
            scope=InformationScope.PRIVATE,
            owner_id=member_id,
            metadata={"kind": "member_legacy_graph"},
        )
        self.ledger.submit(
            event_type="MEMBER_LEGACY_GRAPH_CREATE",
            signer=self.founder_signer(),
            scope=InformationScope.PRIVATE,
            owner_id=member_id,
            payload_ref=stored["object_id"],
            idempotency_key=f"member-legacy:{member_id}",
            disposition="ACCEPTED_EFFECTIVE",
            metadata={"control": "member", "default_scope": "private"},
        )
        return signer

    def record_restriction(
        self, restriction: DisclosureRestriction
    ) -> dict[str, Any]:
        if restriction.authority_id != self.FOUNDER_ID:
            raise GovernanceError(
                "prototype disclosure restrictions require the founder authority"
            )
        begins = datetime.fromisoformat(restriction.begins_at.replace("Z", "+00:00"))
        review = datetime.fromisoformat(
            restriction.review_or_expires_at.replace("Z", "+00:00")
        )
        if review <= begins:
            raise GovernanceError("restriction review or expiry must follow its start")
        stored = self.store.put_json(
            restriction.model_dump(mode="json"),
            scope=InformationScope.OFFICIAL_PUBLIC,
            metadata={"kind": "disclosure_restriction"},
        )
        return self.ledger.submit(
            event_type="DISCLOSURE_RESTRICTION_CREATE",
            signer=self.founder_signer(),
            scope=InformationScope.OFFICIAL_PUBLIC,
            payload_ref=stored["object_id"],
            idempotency_key=restriction.restriction_id,
            disposition="ACCEPTED_EFFECTIVE",
            evidence_ids=restriction.record_ids,
            metadata={
                "basis": restriction.basis,
                "authority_id": restriction.authority_id,
                "review_or_expires_at": restriction.review_or_expires_at,
                "public_restriction_record": True,
            },
        )

    def record_succession(
        self, directive: SuccessionDirective
    ) -> dict[str, Any]:
        signer = self.ensure_member(directive.member_id)
        stored = self.store.put_json(
            directive.model_dump(mode="json"),
            scope=InformationScope.PRIVATE,
            owner_id=directive.member_id,
            metadata={"kind": "succession_directive"},
        )
        return self.ledger.submit(
            event_type="MEMBER_SUCCESSION_DIRECTIVE",
            signer=signer,
            scope=InformationScope.PRIVATE,
            owner_id=directive.member_id,
            payload_ref=stored["object_id"],
            idempotency_key=f"{directive.directive_id}:v{directive.version}",
            disposition="ACCEPTED_EFFECTIVE",
            predecessor_id=directive.predecessor_id,
            metadata={"action": directive.action, "version": directive.version},
        )
