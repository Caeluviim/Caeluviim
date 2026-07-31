from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .canonical import (
    generate_ed25519_private_key,
    load_private_key,
    private_key_bytes,
    public_key_bytes,
    sign_digest,
)


def _safe_token(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SigningIdentity:
    identity_id: str
    key_id: str
    private_key: Ed25519PrivateKey

    @property
    def public_key_base64url(self) -> str:
        return base64.urlsafe_b64encode(
            public_key_bytes(self.private_key.public_key())
        ).rstrip(b"=").decode("ascii")

    def sign(self, digest: bytes) -> str:
        return sign_digest(self.private_key, digest)


class KeyVault:
    """Local key custody.

    Runtime keys are stored separately from the object store so crypto-shredding
    member content never affects the civic signing history. Files are excluded
    from version control by the data-root ignore rule.
    """

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key_id: str) -> Path:
        return self.root / f"{_safe_token(key_id)}.pem"

    def ensure(self, identity_id: str, key_id: str) -> SigningIdentity:
        path = self._path(key_id)
        if path.exists():
            key = load_private_key(path.read_bytes())
        else:
            key = generate_ed25519_private_key()
            temporary = path.with_suffix(".tmp")
            with temporary.open("wb") as handle:
                handle.write(private_key_bytes(key))
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.chmod(temporary, 0o600)
            except OSError:
                pass
            os.replace(temporary, path)
        return SigningIdentity(identity_id=identity_id, key_id=key_id, private_key=key)

    def load(self, identity_id: str, key_id: str) -> SigningIdentity:
        path = self._path(key_id)
        if not path.exists():
            raise KeyError(f"signing key is not available: {key_id}")
        return SigningIdentity(
            identity_id=identity_id,
            key_id=key_id,
            private_key=load_private_key(path.read_bytes()),
        )

    def revoke_local_copy(self, key_id: str) -> bool:
        path = self._path(key_id)
        if not path.exists():
            return False
        path.unlink()
        return True

