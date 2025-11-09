"""Routes for managing API keys."""

from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...config import get_settings
from ...database import get_db
from ...models.api_key import APIKey
from ...models.user import User
from ...schemas import (
    APIKeyCreate,
    APIKeyListResponse,
    APIKeyRead,
    APIKeySecretResponse,
    APIKeyUpdate,
    APIKeyUsageResponse,
    APIKeyUsageSample,
)
from ...services.api_keys import generate_api_key, mask_api_key
from ...services.rate_limiter import rate_limiter
from ...utils.auth import get_current_active_user

router = APIRouter(tags=["api_keys"])
settings = get_settings()


def _serialize_api_key(api_key: APIKey) -> APIKeyRead:
    return APIKeyRead(
        id=api_key.id,
        name=api_key.name,
        key_preview=api_key.key_preview,
        permissions=list(api_key.permissions or []),
        rate_limit=api_key.rate_limit,
        created_at=api_key.created_at,
        last_used=api_key.last_used,
        active=api_key.active,
    )


def _get_api_key(db: Session, current_user: User, key_id: int) -> APIKey:
    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id)
        .filter(APIKey.user_id == current_user.id)
        .first()
    )
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    return api_key


@router.get("/api-keys", response_model=APIKeyListResponse)
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> APIKeyListResponse:
    keys: List[APIKey] = (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id)
        .order_by(APIKey.created_at.desc())
        .all()
    )
    return APIKeyListResponse(items=[_serialize_api_key(key) for key in keys])


@router.post("/api-keys", response_model=APIKeySecretResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> APIKeySecretResponse:
    plain_key, hashed_key = generate_api_key()
    key_hint = mask_api_key(plain_key)
    rate_limit = payload.rate_limit or settings.public_api_default_rate_limit

    api_key = APIKey(
        user_id=current_user.id,
        name=payload.name,
        key=hashed_key,
        key_hint=key_hint,
        permissions=list(payload.permissions or []),
        rate_limit=rate_limit,
        created_at=datetime.utcnow(),
        active=True,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return APIKeySecretResponse(
        id=api_key.id,
        name=api_key.name,
        api_key=plain_key,
        key_preview=api_key.key_preview,
        permissions=list(api_key.permissions or []),
        rate_limit=api_key.rate_limit,
    )


@router.put("/api-keys/{key_id}", response_model=APIKeyRead)
def update_api_key(
    key_id: int,
    payload: APIKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> APIKeyRead:
    api_key = _get_api_key(db, current_user, key_id)

    if payload.name is not None:
        api_key.name = payload.name
    if payload.permissions is not None:
        api_key.permissions = list(payload.permissions)
    if payload.rate_limit is not None:
        api_key.rate_limit = payload.rate_limit
    if payload.active is not None:
        api_key.active = payload.active

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return _serialize_api_key(api_key)


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    api_key = _get_api_key(db, current_user, key_id)
    db.delete(api_key)
    db.commit()


@router.post("/api-keys/{key_id}/revoke", response_model=APIKeyRead)
def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> APIKeyRead:
    api_key = _get_api_key(db, current_user, key_id)
    api_key.active = False
    api_key.last_used = datetime.utcnow()
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return _serialize_api_key(api_key)


@router.get("/api-keys/{key_id}/usage", response_model=APIKeyUsageResponse)
def get_api_key_usage(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> APIKeyUsageResponse:
    api_key = _get_api_key(db, current_user, key_id)
    status_snapshot = rate_limiter.peek(api_key.key, api_key.rate_limit)
    history = rate_limiter.history(api_key.key)
    samples = [
        APIKeyUsageSample(timestamp=datetime.utcfromtimestamp(ts), requests=count)
        for ts, count in history
    ]
    return APIKeyUsageResponse(
        key_id=api_key.id,
        key_preview=api_key.key_preview,
        hourly_limit=api_key.rate_limit,
        remaining=status_snapshot.remaining,
        reset_epoch=status_snapshot.reset_epoch,
        samples=samples,
    )


@router.get("/api-keys/usage", response_model=List[APIKeyUsageResponse])
def list_api_key_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[APIKeyUsageResponse]:
    keys: List[APIKey] = (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id)
        .all()
    )
    responses: List[APIKeyUsageResponse] = []
    for api_key in keys:
        status_snapshot = rate_limiter.peek(api_key.key, api_key.rate_limit)
        history = rate_limiter.history(api_key.key)
        samples = [
            APIKeyUsageSample(timestamp=datetime.utcfromtimestamp(ts), requests=count)
            for ts, count in history
        ]
        responses.append(
            APIKeyUsageResponse(
                key_id=api_key.id,
                key_preview=api_key.key_preview,
                hourly_limit=api_key.rate_limit,
                remaining=status_snapshot.remaining,
                reset_epoch=status_snapshot.reset_epoch,
                samples=samples,
            )
        )
    return responses

