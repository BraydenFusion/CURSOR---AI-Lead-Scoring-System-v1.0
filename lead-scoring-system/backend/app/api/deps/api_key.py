"""Dependencies for API key authenticated endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Set

from fastapi import Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from ...config import get_settings
from ...database import get_db
from ...models.api_key import APIKey
from ...models.user import User
from ...services.api_keys import hash_api_key
from ...services.rate_limiter import RateLimitExceeded, rate_limiter

settings = get_settings()


@dataclass
class APIKeyContext:
    api_key: APIKey
    user: User
    permissions: Set[str]
    limit: int
    remaining: int
    reset_epoch: int


def get_api_key_context(
    response: Response,
    api_key_header: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> APIKeyContext:
    if not api_key_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key header")

    hashed_key = hash_api_key(api_key_header.strip())
    api_key: APIKey | None = (
        db.query(APIKey)
        .filter(APIKey.key == hashed_key)
        .filter(APIKey.active.is_(True))
        .first()
    )
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    user: User | None = db.query(User).filter(User.id == api_key.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="API key is not associated with an active user")

    limit = api_key.rate_limit or settings.public_api_default_rate_limit or 100
    try:
        rate_status = rate_limiter.check(api_key.key, limit)
    except RateLimitExceeded as exc:
        response.headers["X-RateLimit-Limit"] = str(exc.limit)
        response.headers["X-RateLimit-Remaining"] = "0"
        response.headers["X-RateLimit-Reset"] = str(exc.reset_epoch)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    api_key.last_used = datetime.utcnow()
    db.add(api_key)
    db.commit()

    response.headers["X-RateLimit-Limit"] = str(rate_status.limit)
    response.headers["X-RateLimit-Remaining"] = str(rate_status.remaining)
    response.headers["X-RateLimit-Reset"] = str(rate_status.reset_epoch)

    permissions = set(api_key.permissions or [])
    return APIKeyContext(
        api_key=api_key,
        user=user,
        permissions=permissions,
        limit=rate_status.limit,
        remaining=rate_status.remaining,
        reset_epoch=rate_status.reset_epoch,
    )


def ensure_permissions(context: APIKeyContext, required: Iterable[str]) -> None:
    missing = {perm for perm in required if perm not in context.permissions}
    if missing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"API key missing required permissions: {', '.join(sorted(missing))}",
        )

