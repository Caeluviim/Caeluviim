from __future__ import annotations

import base64
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterator

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .canonical import canonical_bytes, content_urn, sha256_hex
from .models import InformationScope, utc_now


class ObjectNotFoundError(FileNotFoundError):
    pass


class ObjectAccessError(PermissionError):
    pass


def _owner_token(owner_id: str) -> str:
    return hashlib.sha256(owner_id.encode("utf-8")).hexdigest()


def _atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.chmod(temporary, mode)
        except OSError:
            pass
        os.replace(temporary, path)
        try:
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            pass
    finally:
        if temporary.exists():
            temporary.unlink()


class ObjectStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.objects = self.root / "objects"
        self.keys = self.root / "member-content-keys"
        self.objects.mkdir(parents=True, exist_ok=True)
        self.keys.mkdir(parents=True, exist_ok=True)

    def _member_key_path(self, owner_id: str) -> Path:
        return self.keys / f"{_owner_token(owner_id)}.key"

    def _member_key(self, owner_id: str, create: bool) -> bytes:
        path = self._member_key_path(owner_id)
        if path.exists():
            data = path.read_bytes()
            if len(data) != 32:
                raise ObjectAccessError("member content key is invalid")
            return data
        if not create:
            raise ObjectAccessError("member content has been sealed or crypto-shredded")
        data = AESGCM.generate_key(bit_length=256)
        _atomic_write(path, data)
        return data

    def _digest(self, data: bytes, scope: InformationScope, owner_id: str | None) -> str:
        if scope.is_public:
            return sha256_hex(data)
        if not owner_id:
            raise ValueError("non-public objects require owner_id")
        return sha256_hex(
            b"CAELUVIIM-PRIVATE-OBJECT-0.1\x00"
            + owner_id.encode("utf-8")
            + b"\x00"
            + data
        )

    def _paths(self, object_id: str) -> tuple[Path, Path]:
        digest = object_id.rsplit(":", 1)[-1]
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError(f"invalid object identifier: {object_id}")
        directory = self.objects / digest[:2]
        return directory / f"{digest}.blob", directory / f"{digest}.meta.json"

    def put_bytes(
        self,
        data: bytes,
        *,
        media_type: str,
        encoding: str | None,
        scope: InformationScope,
        owner_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        digest = self._digest(data, scope, owner_id)
        object_id = content_urn("object", digest)
        blob_path, metadata_path = self._paths(object_id)
        if blob_path.exists() and metadata_path.exists():
            return self.metadata(object_id, owner_id=owner_id)

        public_metadata = {
            "object_id": object_id,
            "content_hash": f"sha256:{digest}",
            "media_type": media_type,
            "encoding": encoding,
            "scope": scope.value,
            "created_at": utc_now(),
            "size": len(data),
            "encrypted": not scope.is_public,
        }
        if scope.is_public:
            _atomic_write(blob_path, data, mode=0o644)
            _atomic_write(
                metadata_path,
                canonical_bytes({**public_metadata, "metadata": metadata or {}}),
                mode=0o644,
            )
            return {**public_metadata, "metadata": metadata or {}}

        if not owner_id:
            raise ValueError("private object requires owner_id")
        key = self._member_key(owner_id, create=True)
        cipher = AESGCM(key)
        blob_nonce = os.urandom(12)
        meta_nonce = os.urandom(12)
        owner = _owner_token(owner_id)
        encrypted_blob = cipher.encrypt(blob_nonce, data, object_id.encode("utf-8"))
        private_metadata = {
            **public_metadata,
            "owner_id": owner_id,
            "metadata": metadata or {},
        }
        encrypted_metadata = cipher.encrypt(
            meta_nonce,
            canonical_bytes(private_metadata),
            f"{object_id}:metadata".encode("utf-8"),
        )
        wrapper = {
            **public_metadata,
            "owner_token": owner,
            "blob_nonce": base64.urlsafe_b64encode(blob_nonce).decode("ascii"),
            "metadata_nonce": base64.urlsafe_b64encode(meta_nonce).decode("ascii"),
            "metadata_ciphertext": base64.urlsafe_b64encode(encrypted_metadata).decode(
                "ascii"
            ),
        }
        _atomic_write(blob_path, encrypted_blob)
        _atomic_write(metadata_path, canonical_bytes(wrapper))
        return private_metadata

    def put_json(
        self,
        value: Any,
        *,
        scope: InformationScope,
        owner_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.put_bytes(
            canonical_bytes(value),
            media_type="application/json",
            encoding="utf-8",
            scope=scope,
            owner_id=owner_id,
            metadata=metadata,
        )

    def _wrapper(self, object_id: str) -> dict[str, Any]:
        _, metadata_path = self._paths(object_id)
        if not metadata_path.exists():
            raise ObjectNotFoundError(object_id)
        return json.loads(metadata_path.read_text("utf-8"))

    def metadata(self, object_id: str, owner_id: str | None = None) -> dict[str, Any]:
        wrapper = self._wrapper(object_id)
        if not wrapper.get("encrypted"):
            return wrapper
        if not owner_id or wrapper.get("owner_token") != _owner_token(owner_id):
            raise ObjectAccessError("private object owner authorization is required")
        key = self._member_key(owner_id, create=False)
        nonce = base64.urlsafe_b64decode(wrapper["metadata_nonce"])
        ciphertext = base64.urlsafe_b64decode(wrapper["metadata_ciphertext"])
        data = AESGCM(key).decrypt(
            nonce,
            ciphertext,
            f"{object_id}:metadata".encode("utf-8"),
        )
        return json.loads(data)

    def get_bytes(self, object_id: str, owner_id: str | None = None) -> bytes:
        blob_path, _ = self._paths(object_id)
        if not blob_path.exists():
            raise ObjectNotFoundError(object_id)
        wrapper = self._wrapper(object_id)
        data = blob_path.read_bytes()
        if not wrapper.get("encrypted"):
            expected = object_id.rsplit(":", 1)[-1]
            if sha256_hex(data) != expected:
                raise ValueError(f"public object hash mismatch: {object_id}")
            return data
        if not owner_id or wrapper.get("owner_token") != _owner_token(owner_id):
            raise ObjectAccessError("private object owner authorization is required")
        key = self._member_key(owner_id, create=False)
        nonce = base64.urlsafe_b64decode(wrapper["blob_nonce"])
        plaintext = AESGCM(key).decrypt(nonce, data, object_id.encode("utf-8"))
        expected = self._digest(plaintext, InformationScope(wrapper["scope"]), owner_id)
        if object_id != content_urn("object", expected):
            raise ValueError(f"private object hash mismatch: {object_id}")
        return plaintext

    def get_json(self, object_id: str, owner_id: str | None = None) -> Any:
        return json.loads(self.get_bytes(object_id, owner_id=owner_id))

    def iter_public_metadata(self) -> Iterator[dict[str, Any]]:
        for path in sorted(self.objects.glob("*/*.meta.json")):
            wrapper = json.loads(path.read_text("utf-8"))
            if not wrapper.get("encrypted"):
                yield wrapper

    def crypto_shred(self, owner_id: str) -> bool:
        path = self._member_key_path(owner_id)
        if not path.exists():
            return False
        path.unlink()
        return True
