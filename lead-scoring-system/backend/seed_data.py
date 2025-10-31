"""Seed script to populate the database with representative leads."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Lead, LeadActivity, LeadScoreHistory
from app.services.scoring_service import ScoringService


def _create_lead(
    db: Session,
    *,
    name: str,
    email: str,
    phone: str,
    source: str,
    location: str,
    activities: list[tuple[str, int]],
) -> Lead:
    lead = Lead(
        name=name,
        email=email.lower(),
        phone=phone,
        source=source,
        location=location,
        metadata={},
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    now = datetime.utcnow()

    for index, (activity_type, count) in enumerate(activities):
        for occurrence in range(count):
            activity = LeadActivity(
                lead_id=lead.id,
                activity_type=activity_type,
                timestamp=now - timedelta(days=index, hours=occurrence),
                metadata={},
                points_awarded=ScoringService.activity_base_points(activity_type),
            )
            db.add(activity)

    db.commit()

    ScoringService.update_lead_score(db, lead.id)
    db.refresh(lead)

    return lead


def create_test_leads(db: Session) -> None:
    """Create three test leads with distinct score profiles."""

    print("Creating Lead 1: Jane Smith (HOT)...")
    jane = _create_lead(
        db,
        name="Jane Smith",
        email="jane@example.com",
        phone="+1234567890",
        source="autotrader",
        location="New York, NY",
        activities=[
            ("email_open", 5),
            ("email_click", 4),
            ("website_visit", 3),
            ("pricing_page_view", 5),
            ("trade_in_inquiry", 1),
            ("test_drive_request", 1),
            ("financing_calculator_use", 2),
        ],
    )
    print(f"[OK] Lead 1 score: {jane.current_score} ({jane.classification.upper()})")

    print("\nCreating Lead 2: Bob Johnson (WARM)...")
    bob = _create_lead(
        db,
        name="Bob Johnson",
        email="bob@example.com",
        phone="+1234567891",
        source="website",
        location="Los Angeles, CA",
        activities=[
            ("email_open", 3),
            ("email_click", 2),
            ("website_visit", 2),
            ("pricing_page_view", 3),
            ("financing_calculator_use", 1),
        ],
    )
    print(f"[OK] Lead 2 score: {bob.current_score} ({bob.classification.upper()})")

    print("\nCreating Lead 3: Alice Brown (COLD)...")
    alice = _create_lead(
        db,
        name="Alice Brown",
        email="alice@example.com",
        phone="+1234567892",
        source="cargurus",
        location="Chicago, IL",
        activities=[
            ("email_open", 1),
            ("website_visit", 1),
        ],
    )
    print(f"[OK] Lead 3 score: {alice.current_score} ({alice.classification.upper()})")

    total = db.query(Lead).count()
    print(f"\n[OK] Seed complete. Total leads in database: {total}")


def clear_existing_data(db: Session) -> None:
    """Remove existing data to ensure deterministic seed runs."""

    print("Clearing existing data...")
    db.query(LeadScoreHistory).delete()
    db.query(LeadActivity).delete()
    db.query(Lead).delete()
    db.commit()


if __name__ == "__main__":
    session = SessionLocal()
    try:
        clear_existing_data(session)
        create_test_leads(session)
    finally:
        session.close()
