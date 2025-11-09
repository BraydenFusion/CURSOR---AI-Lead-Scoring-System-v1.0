"""OAuth and email integration routes for Gmail and Outlook."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID
from urllib.parse import urlencode

import requests
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import EmailAccount, EmailMessage
from app.schemas import (
    EmailAccountRead,
    EmailMessageRead,
    SendEmailRequest,
    OAuthConnectResponse,
    OAuthCallbackResponse,
)
from app.services.email_sync import (
    send_email_via_integration,
    sync_all_email_accounts,
    sync_gmail_emails,
    sync_outlook_emails,
)
from app.utils.auth import get_current_active_user

settings = get_settings()
router = APIRouter()

OAUTH_STATE_TTL = timedelta(minutes=10)
_OAUTH_STATE_STORE: Dict[str, Dict[str, Any]] = {}


def _store_oauth_state(state: str, user_id: Any, provider: str) -> None:
    _OAUTH_STATE_STORE[state] = {
        "user_id": user_id,
        "provider": provider,
        "created_at": datetime.utcnow(),
    }


def _pop_oauth_state(state: str, provider: str) -> Optional[Any]:
    data = _OAUTH_STATE_STORE.pop(state, None)
    if not data:
        return None
    if data["provider"] != provider:
        return None
    if datetime.utcnow() - data["created_at"] > OAUTH_STATE_TTL:
        return None
    return data["user_id"]


def _build_google_flow(state: Optional[str] = None) -> Flow:
    if not settings.google_client_id or not settings.google_client_secret or not settings.google_oauth_redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google integration is not configured. Set GOOGLE_CLIENT_ID/SECRET and GOOGLE_OAUTH_REDIRECT_URI.",
        )
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=[
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid",
        ],
        state=state,
    )
    flow.redirect_uri = settings.google_oauth_redirect_uri
    return flow


def _ensure_outlook_config() -> None:
    if not settings.outlook_client_id or not settings.outlook_client_secret or not settings.outlook_oauth_redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Outlook integration is not configured. Set OUTLOOK_CLIENT_ID/SECRET and OUTLOOK_OAUTH_REDIRECT_URI.",
        )


@router.get("/gmail/connect", response_model=OAuthConnectResponse)
async def gmail_connect(
    current_user=Depends(get_current_active_user),
) -> OAuthConnectResponse:
    flow = _build_google_flow()
    state = secrets.token_urlsafe(32)
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=state,
        prompt="consent",
    )
    _store_oauth_state(state, current_user.id, provider="gmail")
    return OAuthConnectResponse(authorization_url=auth_url, state=state)


@router.get("/gmail/callback", response_model=OAuthCallbackResponse)
async def gmail_callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
) -> OAuthCallbackResponse:
    user_id = _pop_oauth_state(state, provider="gmail")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OAuth state.")

    flow = _build_google_flow(state=state)
    flow.fetch_token(code=code)
    credentials: Credentials = flow.credentials

    # Fetch email address via Google OAuth2 API
    try:
        oauth2_client = build("oauth2", "v2", credentials=credentials, cache_discovery=False)
        userinfo = oauth2_client.userinfo().get().execute()
        email_address = userinfo.get("email")
    except Exception as exc:  # pragma: no cover - network failure
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch Gmail profile.") from exc

    if not email_address:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to determine Gmail address from profile.")

    account = (
        db.query(EmailAccount)
        .filter(EmailAccount.user_id == user_id, EmailAccount.provider == "gmail")
        .one_or_none()
    )
    if not account:
        account = EmailAccount(
            user_id=user_id,
            provider="gmail",
            email_address=email_address,
            token_expires_at=credentials.expiry or datetime.utcnow(),
        )
    else:
        account.email_address = email_address
        account.token_expires_at = credentials.expiry or datetime.utcnow()

    account.access_token = credentials.token
    if credentials.refresh_token:
        account.refresh_token = credentials.refresh_token
    account.connected_at = account.connected_at or datetime.utcnow()
    account.last_sync = datetime.utcnow()

    db.add(account)
    db.commit()
    db.refresh(account)
    return OAuthCallbackResponse(success=True, email_account=EmailAccountRead.model_validate(account))


@router.post("/gmail/disconnect", status_code=status.HTTP_204_NO_CONTENT)
async def gmail_disconnect(
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> None:
    account = (
        db.query(EmailAccount)
        .filter(EmailAccount.user_id == current_user.id, EmailAccount.provider == "gmail")
        .one_or_none()
    )
    if account:
        db.delete(account)
        db.commit()


@router.get("/outlook/connect", response_model=OAuthConnectResponse)
async def outlook_connect(
    current_user=Depends(get_current_active_user),
) -> OAuthConnectResponse:
    _ensure_outlook_config()
    state = secrets.token_urlsafe(32)
    params = {
        "client_id": settings.outlook_client_id,
        "response_type": "code",
        "redirect_uri": settings.outlook_oauth_redirect_uri,
        "response_mode": "query",
        "scope": "offline_access Mail.ReadWrite Mail.Send User.Read email openid profile",
        "state": state,
        "prompt": "consent",
    }
    auth_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{urlencode(params)}"
    _store_oauth_state(state, current_user.id, provider="outlook")
    return OAuthConnectResponse(authorization_url=auth_url, state=state)


@router.get("/outlook/callback", response_model=OAuthCallbackResponse)
async def outlook_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
) -> OAuthCallbackResponse:
    user_id = _pop_oauth_state(state, provider="outlook")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OAuth state.")

    _ensure_outlook_config()
    data = {
        "client_id": settings.outlook_client_id,
        "client_secret": settings.outlook_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.outlook_oauth_redirect_uri,
    }
    token_resp = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token", data=data, timeout=30)
    if not token_resp.ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to exchange Outlook authorization code.")
    token_payload = token_resp.json()
    access_token = token_payload.get("access_token")
    refresh_token = token_payload.get("refresh_token")
    expires_in = token_payload.get("expires_in")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Outlook token response missing access token.")

    # Fetch profile for email address
    profile_resp = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    if not profile_resp.ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch Outlook profile.")
    profile_data = profile_resp.json()
    email_address = profile_data.get("mail") or profile_data.get("userPrincipalName")
    if not email_address:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to determine Outlook email address.")

    account = (
        db.query(EmailAccount)
        .filter(EmailAccount.user_id == user_id, EmailAccount.provider == "outlook")
        .one_or_none()
    )
    expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in or 3600))
    if not account:
        account = EmailAccount(
            user_id=user_id,
            provider="outlook",
            email_address=email_address,
            token_expires_at=expires_at,
        )
    else:
        account.email_address = email_address
        account.token_expires_at = expires_at

    account.access_token = access_token
    if refresh_token:
        account.refresh_token = refresh_token
    account.connected_at = account.connected_at or datetime.utcnow()
    account.last_sync = datetime.utcnow()

    db.add(account)
    db.commit()
    db.refresh(account)
    return OAuthCallbackResponse(success=True, email_account=EmailAccountRead.model_validate(account))


@router.post("/outlook/disconnect", status_code=status.HTTP_204_NO_CONTENT)
async def outlook_disconnect(
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> None:
    account = (
        db.query(EmailAccount)
        .filter(EmailAccount.user_id == current_user.id, EmailAccount.provider == "outlook")
        .one_or_none()
    )
    if account:
        db.delete(account)
        db.commit()


@router.get("/accounts", response_model=list[EmailAccountRead])
async def list_email_accounts(
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> list[EmailAccountRead]:
    accounts = (
        db.query(EmailAccount)
        .filter(EmailAccount.user_id == current_user.id)
        .order_by(EmailAccount.provider.asc())
        .all()
    )
    return [EmailAccountRead.model_validate(account) for account in accounts]


@router.post("/sync/{provider}", response_model=dict)
async def manual_sync(
    provider: str,
    current_user=Depends(get_current_active_user),
) -> Dict[str, Any]:
    provider = provider.lower()
    if provider not in {"gmail", "outlook", "all"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported provider.")

    if provider == "gmail":
        processed = await sync_gmail_emails(current_user.id)
    elif provider == "outlook":
        processed = await sync_outlook_emails(current_user.id)
    else:
        await sync_all_email_accounts()
        processed = -1  # indicates global sync

    return {"status": "ok", "processed": processed}


@router.patch("/accounts/{account_id}/auto-sync", response_model=EmailAccountRead)
async def toggle_auto_sync(
    account_id: int,
    enabled: bool,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> EmailAccountRead:
    account = (
        db.query(EmailAccount)
        .filter(EmailAccount.id == account_id, EmailAccount.user_id == current_user.id)
        .one_or_none()
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email account not found.")

    account.auto_sync_enabled = enabled
    db.add(account)
    db.commit()
    db.refresh(account)
    return EmailAccountRead.model_validate(account)


@router.get("/emails/{lead_id}", response_model=list[EmailMessageRead])
async def list_lead_emails(
    lead_id: UUID,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> list[EmailMessageRead]:
    messages = (
        db.query(EmailMessage)
        .join(EmailAccount, EmailAccount.id == EmailMessage.email_account_id)
        .filter(
            EmailMessage.lead_id == lead_id,
            EmailAccount.user_id == current_user.id,
        )
        .order_by(EmailMessage.sent_at.desc())
        .all()
    )
    return [EmailMessageRead.model_validate(message) for message in messages]


@router.post("/send-email", response_model=EmailMessageRead)
async def send_email(
    payload: SendEmailRequest,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> EmailMessageRead:
    account = (
        db.query(EmailAccount)
        .filter(EmailAccount.id == payload.email_account_id, EmailAccount.user_id == current_user.id)
        .one_or_none()
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email account not found.")

    message = await send_email_via_integration(
        email_account_id=payload.email_account_id,
        lead_id=payload.lead_id,
        subject=payload.subject,
        body=payload.body,
        recipients=payload.recipients,
    )
    return EmailMessageRead.model_validate(message)

