"""Core lead scoring logic implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Lead, LeadActivity, LeadScoreHistory


@dataclass
class ScoreComponents:
    engagement: int = 0
    buying_signals: int = 0
    demographic_fit: int = 0

    @property
    def total(self) -> int:
        return self.engagement + self.buying_signals + self.demographic_fit


ENGAGEMENT_CAPS: Dict[str, Tuple[int, int]] = {
    "email_open": (3, 5),
    "email_click": (3, 5),
    "website_visit": (2, 5),
}

BUYING_CAPS: Dict[str, Tuple[int, int]] = {
    "pricing_page_view": (3, 5),
    "trade_in_inquiry": (15, 1),
    "test_drive_request": (10, 1),
    "financing_calculator": (5, 2),
}

CLASSIFICATION_THRESHOLDS = {
    "hot": 80,
    "warm": 50,
}


def _compute_activity_points(activity_type: str, count: int, caps: Dict[str, Tuple[int, int]]) -> int:
    if activity_type not in caps:
        return 0
    per_unit, max_units = caps[activity_type]
    applied_units = min(count, max_units)
    return per_unit * applied_units


def _calculate_engagement(activities: Dict[str, int]) -> int:
    return sum(_compute_activity_points(activity, count, ENGAGEMENT_CAPS) for activity, count in activities.items())


def _calculate_buying_signals(activities: Dict[str, int]) -> int:
    return sum(_compute_activity_points(activity, count, BUYING_CAPS) for activity, count in activities.items())


def _calculate_demographic_fit(lead: Lead) -> int:
    demographics = lead._metadata.get("demographics", {}) if isinstance(lead._metadata, dict) else {}

    location_score = demographics.get("location_score", 0)
    income = demographics.get("income_bracket", "unknown")
    credit = demographics.get("credit_score", "not_available")

    location_points_map = {"same_city": 10, "nearby": 7, "same_state": 4, "other": 0}
    income_points_map = {"high": 5, "medium": 3, "low": 1, "unknown": 2}
    credit_points_map = {"720+": 5, "650-719": 3, "580-649": 1, "not_available": 2}

    location_points = location_points_map.get(location_score, 0)
    income_points = income_points_map.get(income, 2)
    credit_points = credit_points_map.get(credit, 2)

    return min(location_points + income_points + credit_points, 20)


def _classify(score: int) -> str:
    if score >= CLASSIFICATION_THRESHOLDS["hot"]:
        return "hot"
    if score >= CLASSIFICATION_THRESHOLDS["warm"]:
        return "warm"
    return "cold"


def _aggregate_activity_counts(activities: Iterable[LeadActivity]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for activity in activities:
        counts[activity.activity_type] = counts.get(activity.activity_type, 0) + 1
    return counts


def calculate_lead_score(lead_id: UUID, db: Session | None = None) -> Dict[str, object]:
    """Calculate comprehensive lead score based on activities."""

    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        lead: Lead | None = db.query(Lead).filter(Lead.id == lead_id).one_or_none()
        if lead is None:
            raise ValueError(f"Lead {lead_id} not found")

        activities = db.query(LeadActivity).filter(LeadActivity.lead_id == lead_id).all()

        counts = _aggregate_activity_counts(activities)

        engagement_points = _calculate_engagement(counts)
        buying_points = _calculate_buying_signals(counts)
        demographic_points = _calculate_demographic_fit(lead)

        components = ScoreComponents(
            engagement=min(engagement_points, 40),
            buying_signals=min(buying_points, 40),
            demographic_fit=min(demographic_points, 20),
        )

        total_score = min(max(components.total, 0), 100)
        classification = _classify(total_score)

        breakdown = {
            "engagement": components.engagement,
            "buying_signals": components.buying_signals,
            "demographic_fit": components.demographic_fit,
        }

        details = {activity: points for activity, points in counts.items()}

        previous_score = lead.current_score
        previous_classification = lead.classification

        lead.current_score = total_score
        lead.classification = classification

        if previous_score != total_score or previous_classification != classification:
            history = LeadScoreHistory(
                lead_id=lead.id,
                old_score=previous_score,
                new_score=total_score,
                old_classification=previous_classification,
                new_classification=classification,
            )
            db.add(history)

        db.add(lead)
        db.commit()

        return {
            "total_score": total_score,
            "classification": classification,
            "breakdown": breakdown,
            "details": details,
        }
    finally:
        if owns_session:
            db.close()
