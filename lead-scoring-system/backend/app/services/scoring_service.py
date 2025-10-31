"""Core lead scoring logic implementation."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Lead, LeadActivity, LeadScoreHistory


class ScoringService:
    """Service for calculating lead scores based on activities and demographics."""

    ENGAGEMENT_MAX = 40
    BUYING_SIGNALS_MAX = 40
    DEMOGRAPHIC_MAX = 20
    TOTAL_MAX = 100

    POINTS_PER_EMAIL_OPEN = 3
    POINTS_PER_EMAIL_CLICK = 3
    POINTS_PER_WEBSITE_VISIT = 2
    POINTS_PER_PRICING_VIEW = 3
    POINTS_PER_FINANCE_CALC = 5

    POINTS_TRADE_IN = 15
    POINTS_TEST_DRIVE = 10

    MAX_EMAIL_OPENS = 5
    MAX_EMAIL_CLICKS = 5
    MAX_WEBSITE_VISITS = 5
    MAX_PRICING_VIEWS = 5
    MAX_FINANCE_CALC = 2

    HOT_THRESHOLD = 80
    WARM_THRESHOLD = 50

    ACTIVITY_POINT_LOOKUP: Dict[str, int] = {
        "email_open": POINTS_PER_EMAIL_OPEN,
        "email_click": POINTS_PER_EMAIL_CLICK,
        "website_visit": POINTS_PER_WEBSITE_VISIT,
        "pricing_page_view": POINTS_PER_PRICING_VIEW,
        "trade_in_inquiry": POINTS_TRADE_IN,
        "test_drive_request": POINTS_TEST_DRIVE,
        "financing_calculator_use": POINTS_PER_FINANCE_CALC,
    }

    @staticmethod
    def calculate_lead_score(db: Session, lead_id: UUID) -> Dict[str, object]:
        """Calculate comprehensive lead score based on all activities and demographics."""

        lead: Optional[Lead] = db.query(Lead).filter(Lead.id == lead_id).first()
        if lead is None:
            raise ValueError(f"Lead {lead_id} not found")

        activities: List[LeadActivity] = (
            db.query(LeadActivity)
            .filter(LeadActivity.lead_id == lead_id)
            .order_by(LeadActivity.timestamp.asc())
            .all()
        )

        engagement_result = ScoringService._calculate_engagement(activities)
        buying_result = ScoringService._calculate_buying_signals(activities)
        demographic_result = ScoringService._calculate_demographic_fit(lead)

        total_score = min(
            ScoringService.TOTAL_MAX,
            engagement_result["score"] + buying_result["score"] + demographic_result["score"],
        )

        if total_score >= ScoringService.HOT_THRESHOLD:
            classification = "hot"
        elif total_score >= ScoringService.WARM_THRESHOLD:
            classification = "warm"
        else:
            classification = "cold"

        return {
            "total_score": total_score,
            "classification": classification,
            "breakdown": {
                "engagement": engagement_result["score"],
                "buying_signals": buying_result["score"],
                "demographic_fit": demographic_result["score"],
            },
            "details": {
                "engagement_factors": engagement_result["factors"],
                "buying_factors": buying_result["factors"],
                "demographic_factors": demographic_result["factors"],
            },
        }

    @staticmethod
    def update_lead_score(
        db: Session, lead_id: UUID, trigger_activity_id: Optional[UUID] = None
    ) -> Lead:
        """Recalculate lead score, persist updates, and log score history."""

        lead: Optional[Lead] = db.query(Lead).filter(Lead.id == lead_id).first()
        if lead is None:
            raise ValueError(f"Lead {lead_id} not found")

        old_score = lead.current_score or 0
        old_classification = lead.classification or "cold"

        score_result = ScoringService.calculate_lead_score(db, lead_id)

        new_score = score_result["total_score"]
        new_classification = score_result["classification"]

        score_changed = old_score != new_score or old_classification != new_classification

        lead.current_score = new_score
        lead.classification = new_classification
        lead.updated_at = datetime.utcnow()

        if score_changed:
            history = LeadScoreHistory(
                lead_id=lead_id,
                old_score=old_score,
                new_score=new_score,
                old_classification=old_classification,
                new_classification=new_classification,
                trigger_activity_id=trigger_activity_id,
                changed_at=datetime.utcnow(),
            )
            db.add(history)

        db.add(lead)
        db.commit()
        db.refresh(lead)

        return lead

    @staticmethod
    def activity_base_points(activity_type: str) -> int:
        """Return the base point value for a single activity occurrence."""

        return ScoringService.ACTIVITY_POINT_LOOKUP.get(activity_type, 0)

    @staticmethod
    def _calculate_engagement(activities: List[LeadActivity]) -> Dict[str, object]:
        score = 0
        factors = []

        email_opens = sum(1 for a in activities if a.activity_type == "email_open")
        email_clicks = sum(1 for a in activities if a.activity_type == "email_click")
        website_visits = sum(1 for a in activities if a.activity_type == "website_visit")

        email_open_points = min(email_opens, ScoringService.MAX_EMAIL_OPENS) * ScoringService.POINTS_PER_EMAIL_OPEN
        email_click_points = min(email_clicks, ScoringService.MAX_EMAIL_CLICKS) * ScoringService.POINTS_PER_EMAIL_CLICK
        website_points = min(website_visits, ScoringService.MAX_WEBSITE_VISITS) * ScoringService.POINTS_PER_WEBSITE_VISIT

        score += email_open_points + email_click_points + website_points

        factors.extend(
            [
                {
                    "name": "Email Opens",
                    "value": email_opens,
                    "points": email_open_points,
                    "max_points": ScoringService.MAX_EMAIL_OPENS * ScoringService.POINTS_PER_EMAIL_OPEN,
                },
                {
                    "name": "Email Clicks",
                    "value": email_clicks,
                    "points": email_click_points,
                    "max_points": ScoringService.MAX_EMAIL_CLICKS * ScoringService.POINTS_PER_EMAIL_CLICK,
                },
                {
                    "name": "Website Visits",
                    "value": website_visits,
                    "points": website_points,
                    "max_points": ScoringService.MAX_WEBSITE_VISITS * ScoringService.POINTS_PER_WEBSITE_VISIT,
                },
            ]
        )

        return {"score": min(score, ScoringService.ENGAGEMENT_MAX), "factors": factors}

    @staticmethod
    def _calculate_buying_signals(activities: List[LeadActivity]) -> Dict[str, object]:
        score = 0
        factors = []

        pricing_views = sum(1 for a in activities if a.activity_type == "pricing_page_view")
        has_trade_in = any(a.activity_type == "trade_in_inquiry" for a in activities)
        has_test_drive = any(a.activity_type == "test_drive_request" for a in activities)
        finance_calc_uses = sum(1 for a in activities if a.activity_type == "financing_calculator_use")

        pricing_points = min(pricing_views, ScoringService.MAX_PRICING_VIEWS) * ScoringService.POINTS_PER_PRICING_VIEW
        trade_in_points = ScoringService.POINTS_TRADE_IN if has_trade_in else 0
        test_drive_points = ScoringService.POINTS_TEST_DRIVE if has_test_drive else 0
        finance_points = min(finance_calc_uses, ScoringService.MAX_FINANCE_CALC) * ScoringService.POINTS_PER_FINANCE_CALC

        score += pricing_points + trade_in_points + test_drive_points + finance_points

        factors.extend(
            [
                {
                    "name": "Pricing Page Views",
                    "value": pricing_views,
                    "points": pricing_points,
                    "max_points": ScoringService.MAX_PRICING_VIEWS * ScoringService.POINTS_PER_PRICING_VIEW,
                },
                {
                    "name": "Trade-in Inquiry",
                    "value": "Yes" if has_trade_in else "No",
                    "points": trade_in_points,
                    "max_points": ScoringService.POINTS_TRADE_IN,
                },
                {
                    "name": "Test Drive Request",
                    "value": "Yes" if has_test_drive else "No",
                    "points": test_drive_points,
                    "max_points": ScoringService.POINTS_TEST_DRIVE,
                },
                {
                    "name": "Financing Calculator",
                    "value": finance_calc_uses,
                    "points": finance_points,
                    "max_points": ScoringService.MAX_FINANCE_CALC * ScoringService.POINTS_PER_FINANCE_CALC,
                },
            ]
        )

        return {"score": min(score, ScoringService.BUYING_SIGNALS_MAX), "factors": factors}

    @staticmethod
    def _calculate_demographic_fit(lead: Lead) -> Dict[str, object]:
        score = 0
        factors = []

        demographics = lead.metadata if isinstance(lead.metadata, dict) else {}
        location_match = str(demographics.get("location_match", "")).lower()
        if location_match == "same_city":
            location_points = 10
        elif location_match == "nearby":
            location_points = 7
        elif location_match == "same_state":
            location_points = 4
        else:
            location_points = 10 if lead.location else 4

        income_raw = str(demographics.get("income_bracket", "unknown")).lower()
        if income_raw in {"high", "upper"}:
            income_points = 5
            income_label = "High"
        elif income_raw in {"medium", "mid"}:
            income_points = 3
            income_label = "Medium"
        elif income_raw == "low":
            income_points = 1
            income_label = "Low"
        else:
            income_points = 2
            income_label = "Unknown"

        credit_raw = str(demographics.get("credit_score", "not_available")).lower()
        if credit_raw in {"720+", "excellent"}:
            credit_points = 5
            credit_label = "720+"
        elif credit_raw in {"650-719", "good"}:
            credit_points = 3
            credit_label = "650-719"
        elif credit_raw in {"580-649", "fair"}:
            credit_points = 1
            credit_label = "580-649"
        else:
            credit_points = 2
            credit_label = "Not Available"

        if location_match:
            location_label = location_match.replace("_", " ").title()
        elif lead.location:
            location_label = lead.location
        else:
            location_label = "Unknown"

        score = min(location_points + income_points + credit_points, ScoringService.DEMOGRAPHIC_MAX)

        factors.extend(
            [
                {
                    "name": "Location Match",
                    "value": location_label,
                    "points": min(location_points, 10),
                    "max_points": 10,
                },
                {
                    "name": "Income Bracket",
                    "value": income_label,
                    "points": income_points,
                    "max_points": 5,
                },
                {
                    "name": "Credit Score",
                    "value": credit_label,
                    "points": credit_points,
                    "max_points": 5,
                },
            ]
        )

        return {"score": score, "factors": factors}


def recalculate_lead_score(lead_id: UUID, db: Optional[Session] = None) -> Dict[str, object]:
    """Compatibility wrapper for legacy function signature."""

    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        result = ScoringService.calculate_lead_score(db, lead_id)
        return result
    finally:
        if owns_session and db is not None:
            db.close()
