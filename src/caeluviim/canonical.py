from __future__ import annotations

import base64
import hashlib
import json
import math
import unicodedata
from copy import deepcopy
from typing import Any, Mapping

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
MAX_SAFE_INTEGER = 9_007_199_254_740_991


class CanonicalizationError(ValueError):
    pass


def _normalize(value: Any, stack: set[int]) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            raise CanonicalizationError("canonical JSON permits safe integers only")
        return value
    if isinstance(value, float):
        raise CanonicalizationError("canonical JSON forbids binary floating point")
    if isinstance(value, (bytes, bytearray, memoryview)):
        raise CanonicalizationError("binary values must be stored as content-addressed objects")

    marker = id(value)
    if marker in stack:
        raise CanonicalizationError("cyclic input is not canonical JSON")
    stack.add(marker)
    try:
        if isinstance(value, (list, tuple)):
            return [_normalize(item, stack) for item in value]
        if isinstance(value, Mapping):
            normalized: dict[str, Any] = {}
            for key, item in value.items():
                if not isinstance(key, str):
                    raise CanonicalizationError("canonical JSON object keys must be strings")
                normalized_key = unicodedata.normalize("NFC", key)
                if normalized_key in normalized:
                    raise CanonicalizationError("object keys collide after NFC normalization")
                normalized[normalized_key] = _normalize(item, stack)
            return dict(
                sorted(normalized.items(), key=lambda pair: pair[0].encode("utf-8"))
            )
        raise CanonicalizationError(
            f"unsupported canonical JSON value: {type(value).__name__}"
        )
    finally:
        stack.remove(marker)


def canonical_encode(value: Any) -> str:
    normalized = _normalize(value, set())
    return json.dumps(
        normalized,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )


def canonical_bytes(value: Any) -> bytes:
    return canonical_encode(value).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def domain_digest(domain: str, value: Any) -> bytes:
    return hashlib.sha256(domain.encode("utf-8") + b"\x00" + canonical_bytes(value)).digest()


def base58btc(data: bytes) -> str:
    leading_zeroes = len(data) - len(data.lstrip(b"\x00"))
    number = int.from_bytes(data, "big")
    encoded = ""
    while number:
        number, remainder = divmod(number, 58)
        encoded = BASE58_ALPHABET[remainder] + encoded
    return "z" + ("1" * leading_zeroes) + encoded


def content_urn(kind: str, digest_hex: str) -> str:
    return f"urn:caeluviim:{kind}:sha256:{digest_hex}"


def operation_body(operation: Mapping[str, Any]) -> dict[str, Any]:
    body = deepcopy(dict(operation))
    body.pop("operation_id", None)
    body.pop("content_hash", None)
    body.pop("signature", None)
    return body


def _validate_utf8_string_set(values: Any, label: str) -> None:
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise CanonicalizationError(f"{label} must be a string set")
    sorted_values = sorted(values, key=lambda value: value.encode("utf-8"))
    if len(set(values)) != len(values) or values != sorted_values:
        raise CanonicalizationError(f"{label} must be unique and UTF-8 sorted")


def operation_digest(operation: Mapping[str, Any]) -> bytes:
    authorization = operation.get("authorization")
    authority_ids = authorization.get("authority_ids") if isinstance(authorization, Mapping) else None
    for values, label in (
        (operation.get("evidence_ids"), "evidence_ids"),
        (operation.get("parent_ids"), "parent_ids"),
        (operation.get("dependencies"), "dependencies"),
        (authority_ids, "authorization.authority_ids"),
    ):
        _validate_utf8_string_set(values, label)
    return domain_digest("DAP-OPERATION-0.2", operation_body(operation))


def operation_identifiers(operation: Mapping[str, Any]) -> tuple[str, str, bytes]:
    digest = operation_digest(operation)
    return (
        f"op:{base58btc(digest)}",
        f"sha256:{digest.hex()}",
        digest,
    )


def ruleset_identifier(ruleset: Mapping[str, Any]) -> str:
    body = deepcopy(dict(ruleset))
    body.pop("ruleset_id", None)
    return f"ruleset:{base58btc(domain_digest('DAP-RULESET-0.2', body))}"


def generate_ed25519_private_key() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.generate()


def private_key_bytes(key: Ed25519PrivateKey) -> bytes:
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def public_key_bytes(key: Ed25519PublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def load_private_key(data: bytes) -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(data, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("expected an Ed25519 private key")
    return key


def sign_digest(key: Ed25519PrivateKey, digest: bytes) -> str:
    return base64.urlsafe_b64encode(key.sign(digest)).rstrip(b"=").decode("ascii")


def verify_digest(key: Ed25519PublicKey, digest: bytes, signature: str) -> bool:
    padding = "=" * ((4 - len(signature) % 4) % 4)
    try:
        key.verify(base64.urlsafe_b64decode(signature + padding), digest)
        return True
    except Exception:
        return False

