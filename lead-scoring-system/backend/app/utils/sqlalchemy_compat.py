"""Compatibility helpers for SQLAlchemy on newer Python versions."""

from __future__ import annotations

import sys
from types import UnionType
from typing import Any, Iterable

_PATCHED = False


def _build_union(types: Iterable[Any]) -> Any:
    iterator = iter(types)
    try:
        first = next(iterator)
    except StopIteration:
        raise TypeError("make_union_type() requires at least one type")

    union = first
    for t in iterator:
        union = union | t  # type: ignore[operator]
    return union


def apply_sqlalchemy_typing_compat() -> None:
    """
    Patch SQLAlchemy's typing helpers to support Python 3.13+ Union changes.

    SQLAlchemy 2.0.x still assumes ``typing.Union`` implements ``__getitem__``,
    which is no longer true on Python 3.13+. This shim rebuilds ``make_union_type``
    so SQLAlchemy can synthesise unions using the native ``types.UnionType``.
    """
    global _PATCHED
    if _PATCHED or sys.version_info < (3, 13):
        return

    try:
        from sqlalchemy.util import typing as sqla_typing  # type: ignore
    except Exception:  # pragma: no cover
        return

    def make_union_type(*types: Any) -> Any:
        if len(types) == 1 and isinstance(types[0], tuple):
            types = types[0]  # pragma: no cover - legacy call pattern
        # Use native union syntax to construct the union chain.
        return _build_union(types)

    # Replace SQLAlchemy helper with union-type aware implementation.
    sqla_typing.make_union_type = make_union_type  # type: ignore[attr-defined]
    _PATCHED = True


