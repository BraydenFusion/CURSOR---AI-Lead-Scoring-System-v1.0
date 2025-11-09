"""Public API user routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ....schemas import PublicUserInfo
from ...deps.api_key import APIKeyContext, get_api_key_context

router = APIRouter()


@router.get("/me", response_model=PublicUserInfo)
def get_me(context: APIKeyContext = Depends(get_api_key_context)) -> PublicUserInfo:
    user = context.user
    return PublicUserInfo(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        api_key_permissions=sorted(context.permissions),
        api_key_rate_limit=context.limit,
        api_key_remaining=context.remaining,
        api_key_reset_epoch=context.reset_epoch,
    )

