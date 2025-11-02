"""Seed script to populate database with test data."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models import Lead, LeadActivity, LeadScoreHistory
from app.services.scoring_service import calculate_lead_score
from uuid import uuid4


def clear_existing_data(db):
    """Clear all existing data."""
    print("Clearing existing data...")
    db.query(LeadScoreHistory).delete()
    db.query(LeadActivity).delete()
    db.query(Lead).delete()
    db.commit()


def create_lead_with_activities(db, name, email, source, activities_data, metadata_data, expected_score):
    """Create a lead with activities and calculate score."""
    # Create lead
    lead = Lead(
        id=uuid4(),
        name=name,
        email=email,
        source=source,
        location=metadata_data.get("location", "New York, NY"),
        metadata=metadata_data,
        current_score=0,
        classification=None,
    )
    db.add(lead)
    db.flush()

    # Create activities
    for activity_type, count in activities_data.items():
        for _ in range(count):
            activity = LeadActivity(
                lead_id=lead.id,
                activity_type=activity_type,
                points_awarded=0,  # Will be calculated by scoring service
                metadata={},
            )
            db.add(activity)

    db.commit()

    # Calculate score
    result = calculate_lead_score(lead.id, db)
    
    print(f"✓ {name} created: Score={result['total_score']}, Classification={result['classification']}")
    return lead


def main():
    """Main seed function."""
    db = SessionLocal()

    try:
        clear_existing_data(db)

        # Lead 1: Jane Smith (HOT) - Score 92
        print("\nCreating Lead 1: Jane Smith (HOT)...")
        create_lead_with_activities(
            db,
            name="Jane Smith",
            email="jane@example.com",
            source="website",
            activities_data={
                "email_open": 5,
                "email_click": 5,
                "website_visit": 5,
                "pricing_page_view": 5,
                "test_drive_request": 1,
                "financing_calculator": 2,
            },
            metadata_data={
                "demographics": {
                    "location_score": "same_city",
                    "income_bracket": "high",
                    "credit_score": "720+",
                }
            },
            expected_score=92,
        )

        # Lead 2: Bob Johnson (WARM) - Score 67
        print("\nCreating Lead 2: Bob Johnson (WARM)...")
        create_lead_with_activities(
            db,
            name="Bob Johnson",
            email="bob@example.com",
            source="referral",
            activities_data={
                "email_open": 3,
                "email_click": 3,
                "website_visit": 4,
                "pricing_page_view": 3,
                "financing_calculator": 1,
            },
            metadata_data={
                "demographics": {
                    "location_score": "nearby",
                    "income_bracket": "medium",
                    "credit_score": "650-719",
                }
            },
            expected_score=67,
        )

        # Lead 3: Alice Brown (COLD) - Score 35
        print("\nCreating Lead 3: Alice Brown (COLD)...")
        create_lead_with_activities(
            db,
            name="Alice Brown",
            email="alice@example.com",
            source="social_media",
            activities_data={
                "email_open": 2,
                "website_visit": 2,
            },
            metadata_data={
                "demographics": {
                    "location_score": "other",
                    "income_bracket": "low",
                    "credit_score": "not_available",
                }
            },
            expected_score=35,
        )

        # Verify
        total_leads = db.query(Lead).count()
        print(f"\n✅ Seed data created successfully!")
        print(f"Total leads: {total_leads}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

