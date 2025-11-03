"""AI-powered lead scoring engine following PRD specifications.

This module implements the enhanced scoring algorithm with:
- Engagement Signals (35 points)
- Buying Signals (40 points)  
- Demographic Fit (25 points)
Total: 100 points
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..models import Lead, LeadActivity, LeadEngagementEvent, LeadInsight, LeadScore


def get_hours_since_last_activity(lead_id: UUID, db: Session) -> float:
    """Get hours since last activity for engagement scoring."""
    last_activity = (
        db.query(LeadActivity)
        .filter(LeadActivity.lead_id == lead_id)
        .order_by(LeadActivity.created_at.desc())
        .first()
    )
    
    if not last_activity:
        return 999.0  # No activity = very old
    
    hours = (datetime.utcnow() - last_activity.created_at).total_seconds() / 3600
    return hours


def count_email_opens(lead_id: UUID, db: Session, days: int = 7) -> int:
    """Count email opens in last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(LeadEngagementEvent)
        .filter(
            LeadEngagementEvent.lead_id == lead_id,
            LeadEngagementEvent.event_type == "email_open",
            LeadEngagementEvent.created_at >= cutoff,
        )
        .count()
    )


def count_email_clicks(lead_id: UUID, db: Session, days: int = 7) -> int:
    """Count email clicks in last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(LeadEngagementEvent)
        .filter(
            LeadEngagementEvent.lead_id == lead_id,
            LeadEngagementEvent.event_type == "email_click",
            LeadEngagementEvent.created_at >= cutoff,
        )
        .count()
    )


def count_page_views(lead_id: UUID, db: Session, days: int = 7) -> int:
    """Count website page views in last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(LeadEngagementEvent)
        .filter(
            LeadEngagementEvent.lead_id == lead_id,
            LeadEngagementEvent.event_type == "website_visit",
            LeadEngagementEvent.created_at >= cutoff,
        )
        .count()
    )


def get_total_time_on_site(lead_id: UUID, db: Session, days: int = 7) -> int:
    """Get total time on site in minutes for last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    events = (
        db.query(LeadEngagementEvent)
        .filter(
            LeadEngagementEvent.lead_id == lead_id,
            LeadEngagementEvent.event_type == "website_visit",
            LeadEngagementEvent.created_at >= cutoff,
        )
        .all()
    )
    
    # Sum up time_on_site from event_data if available
    total_minutes = 0
    for event in events:
        if event.event_data and isinstance(event.event_data, dict):
            total_minutes += event.event_data.get("time_on_site_minutes", 0)
    
    return total_minutes


def calculate_engagement_score(lead_id: UUID, db: Session) -> int:
    """Calculate engagement score (0-35 points) per PRD."""
    score = 0
    
    # Recent activity (0-15 points)
    hours_since_last_activity = get_hours_since_last_activity(lead_id, db)
    if hours_since_last_activity < 1:
        score += 15
    elif hours_since_last_activity < 24:
        score += 10
    elif hours_since_last_activity < 72:
        score += 5
    
    # Email engagement (0-10 points)
    email_opens = count_email_opens(lead_id, db, days=7)
    email_clicks = count_email_clicks(lead_id, db, days=7)
    email_points = min(email_opens * 2 + email_clicks * 3, 10)
    score += email_points
    
    # Website behavior (0-10 points)
    page_views = count_page_views(lead_id, db, days=7)
    time_on_site = get_total_time_on_site(lead_id, db, days=7)
    website_points = min(page_views * 1 + (time_on_site // 60), 10)
    score += website_points
    
    return min(score, 35)


def has_viewed_page(lead_id: UUID, db: Session, page_type: str, days: int = 7) -> bool:
    """Check if lead viewed a specific page type."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    events = (
        db.query(LeadEngagementEvent)
        .filter(
            LeadEngagementEvent.lead_id == lead_id,
            LeadEngagementEvent.event_type == "website_visit",
            LeadEngagementEvent.created_at >= cutoff,
        )
        .all()
    )
    # Check event_data JSONB for page type
    for event in events:
        if event.event_data and isinstance(event.event_data, dict):
            if event.event_data.get("page") == page_type:
                return True
    return False


def has_used_feature(lead_id: UUID, db: Session, feature: str, days: int = 7) -> bool:
    """Check if lead used a specific feature."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    count = (
        db.query(LeadEngagementEvent)
        .filter(
            LeadEngagementEvent.lead_id == lead_id,
            LeadEngagementEvent.event_type == feature,
            LeadEngagementEvent.created_at >= cutoff,
        )
        .count()
    )
    return count > 0


def has_requested_test_drive(lead_id: UUID, db: Session) -> bool:
    """Check if lead requested a test drive."""
    activities = (
        db.query(LeadActivity)
        .filter(
            LeadActivity.lead_id == lead_id,
            LeadActivity.activity_type.in_(["test_drive_request", "test_drive"]),
        )
        .count()
    )
    return activities > 0


def calculate_buying_signal_score(lead: Lead, lead_id: UUID, db: Session) -> int:
    """Calculate buying signal score (0-40 points) per PRD."""
    score = 0
    
    # High-intent page views (0-15 points)
    viewed_pricing = has_viewed_page(lead_id, db, "pricing", days=7)
    used_trade_in_calc = has_used_feature(lead_id, db, "trade_in_calculator", days=7)
    used_finance_calc = has_used_feature(lead_id, db, "finance_calculator", days=7)
    
    if viewed_pricing:
        score += 5
    if used_trade_in_calc:
        score += 6
    if used_finance_calc:
        score += 4
    
    # Budget clarity (0-10 points)
    metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
    budget_min = metadata.get("budget_min") or metadata.get("budgetMin")
    budget_max = metadata.get("budget_max") or metadata.get("budgetMax")
    
    if budget_min and budget_max:
        score += 10  # Clear budget = serious buyer
    elif budget_max:
        score += 5
    
    # Urgency indicators (0-10 points)
    urgency_keywords = ["today", "asap", "urgent", "now", "immediately", "this week"]
    
    # Check notes for urgency
    notes_text = " ".join([note.content.lower() for note in lead.notes]) if lead.notes else ""
    
    # Check activities for urgency
    activities = db.query(LeadActivity).filter(LeadActivity.lead_id == lead_id).all()
    activities_text = " ".join([act.notes.lower() for act in activities if act.notes]) if activities else ""
    
    # Check metadata for initial message
    initial_message = metadata.get("initial_message", "").lower() if isinstance(metadata, dict) else ""
    
    combined_text = f"{notes_text} {activities_text} {initial_message}".lower()
    urgency_count = sum(1 for keyword in urgency_keywords if keyword in combined_text)
    score += min(urgency_count * 3, 10)
    
    # Test drive request (0-5 points)
    if has_requested_test_drive(lead_id, db):
        score += 5
    
    return min(score, 40)


def count_matching_vehicles(vehicle_type: Optional[str], price_min: Optional[float], price_max: Optional[float]) -> int:
    """Mock function - would query inventory database.
    For now, returns mock count based on provided data."""
    # TODO: Integrate with actual inventory system
    if not vehicle_type:
        return 0
    # Mock: assume some vehicles match
    return 3 if price_max and price_max > 20000 else 0


def get_average_inventory_price() -> float:
    """Mock function - would query inventory for average price."""
    # TODO: Integrate with actual inventory system
    return 30000.0  # Mock average


def is_previous_customer(email: str, phone: Optional[str], db: Session) -> bool:
    """Check if lead is a previous customer."""
    # TODO: Check against customer database
    # For now, return False
    return False


def is_referral(source: str) -> bool:
    """Check if lead source indicates a referral."""
    referral_sources = ["referral", "friend", "family", "word_of_mouth"]
    return source.lower() in referral_sources


def calculate_demographic_score(lead: Lead, db: Session) -> int:
    """Calculate demographic fit score (0-25 points) per PRD."""
    score = 0
    
    metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
    vehicle_interest = metadata.get("vehicle_interest") or metadata.get("vehicleInterest")
    budget_min = metadata.get("budget_min") or metadata.get("budgetMin")
    budget_max = metadata.get("budget_max") or metadata.get("budgetMax")
    
    # Inventory match (0-10 points)
    if vehicle_interest:
        matching_inventory = count_matching_vehicles(vehicle_interest, budget_min, budget_max)
        if matching_inventory > 0:
            if matching_inventory > 3:
                score += 7  # Multiple options available
            else:
                score += 10
    
    # Budget-inventory alignment (0-8 points)
    if budget_max:
        avg_inventory_price = get_average_inventory_price()
        if avg_inventory_price > 0:
            ratio = budget_max / avg_inventory_price
            if 0.8 <= ratio <= 1.2:
                score += 8  # Budget is realistic
            elif budget_max > avg_inventory_price:
                score += 5  # Can afford inventory
    
    # Repeat/referral customer (0-7 points)
    if is_previous_customer(lead.email, lead.phone, db):
        score += 7
    elif is_referral(lead.source):
        score += 4
    
    return min(score, 25)


def assign_priority_tier(overall_score: int) -> str:
    """Assign priority tier based on score per PRD.
    
    HOT: 80-100 (call within 5 minutes)
    WARM: 50-79 (call within 2 hours)
    COLD: 0-49 (nurture campaign)
    """
    if overall_score >= 80:
        return "HOT"
    elif overall_score >= 50:
        return "WARM"
    else:
        return "COLD"


def calculate_confidence(lead: Lead, lead_id: UUID, db: Session) -> float:
    """Calculate confidence level (0.00-1.00) based on data completeness per PRD."""
    data_points_available = 0
    total_possible_data_points = 15
    
    # Check what data we have
    if lead.email:
        data_points_available += 1
    if lead.phone:
        data_points_available += 1
    
    metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
    if metadata.get("budget_max") or metadata.get("budgetMax"):
        data_points_available += 2
    
    engagement_events_count = (
        db.query(LeadEngagementEvent)
        .filter(LeadEngagementEvent.lead_id == lead_id)
        .count()
    )
    if engagement_events_count > 0:
        data_points_available += 3
    
    if metadata.get("vehicle_interest") or metadata.get("vehicleInterest"):
        data_points_available += 2
    
    notes_count = len(lead.notes) if lead.notes else 0
    if notes_count > 0:
        notes_length = sum(len(note.content) for note in lead.notes)
        if notes_length > 50:
            data_points_available += 2
    
    confidence = data_points_available / total_possible_data_points
    return round(min(max(confidence, 0.0), 1.0), 2)


def generate_insights(lead: Lead, lead_id: UUID, db: Session, score_data: Dict) -> List[Dict[str, any]]:
    """Generate AI insights and talking points for the lead."""
    insights = []
    
    engagement_score = score_data.get("engagement_score", 0)
    buying_score = score_data.get("buying_signal_score", 0)
    demographic_score = score_data.get("demographic_score", 0)
    
    # Engagement insights
    if engagement_score >= 25:
        hours_since = get_hours_since_last_activity(lead_id, db)
        if hours_since < 1:
            insights.append({
                "type": "talking_point",
                "content": f"Very recent activity ({int(hours_since * 60)} minutes ago) - high engagement, call now for best response",
                "confidence": 0.95
            })
    
    # Buying signal insights
    if buying_score >= 30:
        metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
        if has_used_feature(lead_id, db, "trade_in_calculator", days=7):
            insights.append({
                "type": "talking_point",
                "content": "Used trade-in calculator - mention their trade-in value and how it applies to their purchase",
                "confidence": 0.90
            })
        
        if has_viewed_page(lead_id, db, "pricing", days=7):
            insights.append({
                "type": "talking_point",
                "content": "Viewed pricing page multiple times - price is important, emphasize value and competitive pricing",
                "confidence": 0.85
            })
        
        # Check for urgency
        urgency_keywords = ["today", "asap", "urgent", "now", "immediately", "this week"]
        notes_text = " ".join([note.content.lower() for note in lead.notes]) if lead.notes else ""
        if any(keyword in notes_text for keyword in urgency_keywords):
            insights.append({
                "type": "opportunity",
                "content": "Time-sensitive request detected - emphasize quick delivery and fast turnaround",
                "confidence": 0.88
            })
    
    # Demographic insights
    metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
    vehicle_interest = metadata.get("vehicle_interest") or metadata.get("vehicleInterest")
    budget_max = metadata.get("budget_max") or metadata.get("budgetMax")
    
    if vehicle_interest and budget_max:
        insights.append({
            "type": "talking_point",
            "content": f"Interested in {vehicle_interest} with budget up to ${budget_max:,.0f} - we have matching vehicles available",
            "confidence": 0.75
        })
    
    # Risk factors
    if engagement_score >= 30:
        insights.append({
            "type": "concern",
            "content": "High engagement suggests shopping multiple dealers - act quickly to secure the sale",
            "confidence": 0.70
        })
    
    return insights


def calculate_overall_score(lead_id: UUID, db: Session) -> Dict[str, any]:
    """Calculate comprehensive AI score for a lead following PRD specifications.
    
    Returns:
        Dict with overall_score, engagement_score, buying_signal_score, 
        demographic_score, priority_tier, confidence_level, insights
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise ValueError(f"Lead {lead_id} not found")
    
    # Calculate component scores
    engagement_score = calculate_engagement_score(lead_id, db)
    buying_score = calculate_buying_signal_score(lead, lead_id, db)
    demographic_score = calculate_demographic_score(lead, db)
    
    # Overall score (total of all components)
    overall_score = engagement_score + buying_score + demographic_score
    overall_score = min(max(overall_score, 0), 100)
    
    # Priority tier
    priority_tier = assign_priority_tier(overall_score)
    
    # Confidence level
    confidence_level = calculate_confidence(lead, lead_id, db)
    
    # Generate insights
    score_data = {
        "engagement_score": engagement_score,
        "buying_signal_score": buying_score,
        "demographic_score": demographic_score,
        "overall_score": overall_score,
    }
    insights_list = generate_insights(lead, lead_id, db, score_data)
    
    # Store in lead_scores table
    lead_score = LeadScore(
        lead_id=lead_id,
        overall_score=overall_score,
        engagement_score=engagement_score,
        buying_signal_score=buying_score,
        demographic_score=demographic_score,
        priority_tier=priority_tier,
        confidence_level=confidence_level,
        scoring_metadata={
            "algorithm_version": "1.0",
            "calculated_at": datetime.utcnow().isoformat(),
        },
        scored_at=datetime.utcnow(),
    )
    db.add(lead_score)
    
    # Store insights
    for insight_data in insights_list:
        insight = LeadInsight(
            lead_id=lead_id,
            insight_type=insight_data["type"],
            content=insight_data["content"],
            confidence=insight_data["confidence"],
        )
        db.add(insight)
    
    # Update lead's current_score and classification for backward compatibility
    lead.current_score = overall_score
    lead.classification = priority_tier.lower()
    
    db.commit()
    db.refresh(lead_score)
    
    return {
        "lead_id": str(lead_id),
        "overall_score": overall_score,
        "engagement_score": engagement_score,
        "buying_signal_score": buying_score,
        "demographic_score": demographic_score,
        "priority_tier": priority_tier,
        "confidence_level": float(confidence_level),
        "scored_at": lead_score.scored_at,
        "insights": insights_list,
        "scoring_metadata": lead_score.scoring_metadata,
    }

