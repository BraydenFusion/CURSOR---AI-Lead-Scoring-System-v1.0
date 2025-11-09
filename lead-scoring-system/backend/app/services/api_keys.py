"""Utility helpers for API key management."""

from __future__ import annotations

import hashlib
import secrets
import string
from dataclasses import dataclass

API_KEY_PREFIX = "lss_"
API_KEY_LENGTH = 40  # characters after prefix


def _random_key(length: int) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_api_key() -> tuple[str, str]:
    """
    Generate a new API key and its hashed representation.

    Returns a tuple of (plain_key, hashed_key).
    """
    plain_key = f"{API_KEY_PREFIX}{_random_key(API_KEY_LENGTH)}"
    return plain_key, hash_api_key(plain_key)


def hash_api_key(key: str) -> str:
    """Hash an API key using SHA-256."""
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return digest


def mask_api_key(key: str) -> str:
    """Return a masked representation of the key."""
    if len(key) <= 10:
        return key
    return f"{key[:6]}…{key[-4:]}"

