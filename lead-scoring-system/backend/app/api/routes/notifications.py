"""Notification routes for managing user notifications."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.note import NotificationResponse
from app.utils.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=list[NotificationResponse])
def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get notifications for current user."""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()

    return notifications


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark notification as read."""
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()
    db.refresh(notification)

    return notification


@router.put("/read-all", status_code=200)
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark all notifications as read."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})

    db.commit()

    return {"message": "All notifications marked as read"}


@router.get("/unread-count", response_model=dict)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get count of unread notifications."""
    count = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)
        .count()
    )

    return {"count": count}

