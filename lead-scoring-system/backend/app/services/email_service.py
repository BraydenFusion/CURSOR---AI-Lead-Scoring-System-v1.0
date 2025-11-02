"""Email service for sending notifications."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings

settings = get_settings()


class EmailService:
    """Service for sending emails."""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email

    def send_email(self, to_email: str, subject: str, body: str, html_body: str | None = None) -> bool:
        """Send an email."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            # Plain text version
            text_part = MIMEText(body, "plain")
            msg.attach(text_part)

            # HTML version if provided
            if html_body:
                html_part = MIMEText(html_body, "html")
                msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_lead_assignment_email(
        self, to_email: str, user_name: str, lead_name: str, lead_score: int, lead_classification: str
    ):
        """Send lead assignment notification email."""
        subject = f"New Lead Assigned: {lead_name}"

        body = f"""
Hi {user_name},

You have been assigned a new lead:

Lead: {lead_name}
Score: {lead_score}/100
Classification: {lead_classification.upper()}

Please review and follow up as soon as possible.

Best regards,
Lead Scoring System
        """

        classification_color = (
            "red" if lead_classification == "hot" else "orange" if lead_classification == "warm" else "blue"
        )

        html_body = f"""
<html>
<body>
    <h2>New Lead Assignment</h2>
    <p>Hi {user_name},</p>
    <p>You have been assigned a new lead:</p>
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
        <p><strong>Lead:</strong> {lead_name}</p>
        <p><strong>Score:</strong> {lead_score}/100</p>
        <p><strong>Classification:</strong> <span style="color: {classification_color};">{lead_classification.upper()}</span></p>
    </div>
    <p>Please review and follow up as soon as possible.</p>
    <p>Best regards,<br>Lead Scoring System</p>
</body>
</html>
        """

        return self.send_email(to_email, subject, body, html_body)

    def send_hot_lead_alert(self, to_email: str, user_name: str, lead_name: str, lead_score: int):
        """Send alert for hot lead."""
        subject = f"🔥 HOT LEAD ALERT: {lead_name}"

        body = f"""
Hi {user_name},

URGENT: A lead has become HOT!

Lead: {lead_name}
Score: {lead_score}/100

This lead requires immediate attention. Please reach out as soon as possible.

Best regards,
Lead Scoring System
        """

        html_body = f"""
<html>
<body>
    <h2 style="color: red;">🔥 HOT LEAD ALERT</h2>
    <p>Hi {user_name},</p>
    <p><strong>URGENT:</strong> A lead has become HOT!</p>
    <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; border-left: 4px solid red;">
        <p><strong>Lead:</strong> {lead_name}</p>
        <p><strong>Score:</strong> {lead_score}/100</p>
    </div>
    <p><strong>This lead requires immediate attention.</strong> Please reach out as soon as possible.</p>
    <p>Best regards,<br>Lead Scoring System</p>
</body>
</html>
        """

        return self.send_email(to_email, subject, body, html_body)


# Singleton instance
email_service = EmailService()

