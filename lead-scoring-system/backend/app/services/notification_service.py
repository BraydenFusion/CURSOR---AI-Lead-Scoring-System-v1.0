"""Notification service for creating and managing notifications."""

from sqlalchemy.orm import Session
from uuid import UUID

from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.lead import Lead
from app.services.email_service import email_service


class NotificationService:
    """Service for creating notifications."""

    @staticmethod
    def create_notification(
        db: Session,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        link: str | None = None,
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def notify_lead_assigned(db: Session, user: User, lead: Lead, send_email: bool = True):
        """Send notification when lead is assigned."""
        # Create in-app notification
        NotificationService.create_notification(
            db=db,
            user_id=user.id,
            notification_type=NotificationType.LEAD_ASSIGNED,
            title=f"New Lead Assigned: {lead.name}",
            message=f"You have been assigned {lead.name} (Score: {lead.current_score})",
            link=f"/leads/{lead.id}",
        )

        # Send email if enabled
        if send_email:
            classification = lead.classification or "cold"
            email_service.send_lead_assignment_email(
                to_email=user.email,
                user_name=user.full_name,
                lead_name=lead.name,
                lead_score=lead.current_score,
                lead_classification=classification,
            )

    @staticmethod
    def notify_lead_hot(db: Session, user: User, lead: Lead, send_email: bool = True):
        """Send notification when lead becomes hot."""
        # Create in-app notification
        NotificationService.create_notification(
            db=db,
            user_id=user.id,
            notification_type=NotificationType.LEAD_HOT,
            title=f"🔥 HOT LEAD: {lead.name}",
            message=f"{lead.name} is now a HOT lead (Score: {lead.current_score})",
            link=f"/leads/{lead.id}",
        )

        # Send email if enabled
        if send_email:
            email_service.send_hot_lead_alert(
                to_email=user.email,
                user_name=user.full_name,
                lead_name=lead.name,
                lead_score=lead.current_score,
            )


notification_service = NotificationService()

