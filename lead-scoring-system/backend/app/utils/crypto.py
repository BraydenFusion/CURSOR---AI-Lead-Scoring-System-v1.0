"""Utility helpers for encrypting/decrypting sensitive tokens."""

from __future__ import annotations

import logging
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings

logger = logging.getLogger(__name__)


class EncryptionUnavailable(RuntimeError):
    """Raised when encryption key is not configured."""


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    settings = get_settings()
    if not settings.email_encryption_key:
        raise EncryptionUnavailable(
            "EMAIL_ENCRYPTION_KEY is not configured. Generate a Fernet key with "
            "`python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"` "
            "and set it as an environment variable."
        )
    try:
        return Fernet(settings.email_encryption_key)
    except ValueError as exc:  # pragma: no cover - configuration error
        raise EncryptionUnavailable("Invalid EMAIL_ENCRYPTION_KEY provided. Must be a valid base64 Fernet key.") from exc


def encrypt_string(value: str) -> str:
    """Encrypt a string value using Fernet."""
    if value is None:
        raise ValueError("Cannot encrypt None value.")
    fernet = _get_fernet()
    token = fernet.encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_string(value: str) -> str:
    """Decrypt a previously encrypted string."""
    if value is None:
        raise ValueError("Cannot decrypt None value.")
    fernet = _get_fernet()
    try:
        decrypted = fernet.decrypt(value.encode("utf-8"))
        return decrypted.decode("utf-8")
    except InvalidToken as exc:  # pragma: no cover - indicates tampering or key rotation
        logger.error("Failed to decrypt token: %s", exc)
        raise ValueError("Unable to decrypt token with current encryption key.") from exc

