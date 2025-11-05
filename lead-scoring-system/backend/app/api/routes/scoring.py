"""Scoring endpoints for leads."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Lead, LeadScore, LeadInsight, LeadAssignment
from ...models.user import User
from ...schemas import ScoreResponse
from ...schemas.score import AIScoreResponse, InsightResponse, PrioritizedLeadItem, PrioritizedLeadsResponse
from ...services.scoring_service import calculate_lead_score
from ...services.ai_scoring import calculate_overall_score
from ...utils.auth import get_current_active_user


router = APIRouter()


@router.get("/{lead_id}/score", response_model=ScoreResponse)
def get_lead_score(lead_id: UUID, db: Session = Depends(get_db)) -> ScoreResponse:
    """Return the calculated score for a lead (legacy endpoint)."""

    try:
        # Check if lead exists
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead with id {lead_id} not found"
            )

        # Calculate score (this will update the lead if needed)
        score_data = calculate_lead_score(lead_id, db)

        # Return score response
        return ScoreResponse(
            total_score=score_data["total_score"],
            classification=score_data["classification"],
            breakdown=score_data["breakdown"],
            details=score_data["details"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating score: {str(e)}"
        )


@router.post("/{lead_id}/score", response_model=AIScoreResponse, status_code=status.HTTP_200_OK)
def score_lead_ai(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AIScoreResponse:
    """Score a single lead using AI scoring engine (PRD endpoint)."""
    try:
        # Check if lead exists
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead with id {lead_id} not found"
            )

        # Calculate AI score
        score_data = calculate_overall_score(lead_id, db)

        # Format insights
        insights = [
            InsightResponse(
                type=insight["type"],
                content=insight["content"],
                confidence=insight["confidence"]
            )
            for insight in score_data["insights"]
        ]

        return AIScoreResponse(
            lead_id=UUID(score_data["lead_id"]),
            overall_score=score_data["overall_score"],
            engagement_score=score_data["engagement_score"],
            buying_signal_score=score_data["buying_signal_score"],
            demographic_score=score_data["demographic_score"],
            priority_tier=score_data["priority_tier"],
            confidence_level=score_data["confidence_level"],
            scored_at=score_data["scored_at"],
            insights=insights,
            scoring_metadata=score_data.get("scoring_metadata"),
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating AI score: {str(e)}"
        )


@router.get("/prioritized", response_model=PrioritizedLeadsResponse)
def get_prioritized_leads(
    limit: int = Query(5, ge=1, le=50, description="Number of leads to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PrioritizedLeadsResponse:
    """Get prioritized lead list for current user (PRD endpoint)."""
    try:
        # Get latest scores for all leads
        latest_scores = (
            db.query(
                LeadScore.lead_id,
                func.max(LeadScore.scored_at).label("latest_scored_at")
            )
            .group_by(LeadScore.lead_id)
            .subquery()
        )

        # Build base query with latest scores
        base_query = (
            db.query(Lead, LeadScore)
            .join(LeadScore, Lead.id == LeadScore.lead_id)
            .join(
                latest_scores,
                (LeadScore.lead_id == latest_scores.c.lead_id) &
                (LeadScore.scored_at == latest_scores.c.latest_scored_at)
            )
        )

        # Filter by user role
        if current_user.get_role_enum().value not in ["admin", "manager"]:
            # Sales reps see only their assigned leads
            assigned_lead_ids = db.query(LeadAssignment.lead_id).filter(
                LeadAssignment.user_id == current_user.id,
                LeadAssignment.status == "active"
            )
            base_query = base_query.filter(Lead.id.in_(assigned_lead_ids))

        # Order and limit
        scored_leads = (
            base_query
            .order_by(desc(LeadScore.overall_score))
            .limit(limit)
            .all()
        )

        # Get insights for these leads
        lead_ids = [lead.id for lead, _ in scored_leads]
        insights_map = {}
        if lead_ids:
            insights = (
                db.query(LeadInsight)
                .filter(LeadInsight.lead_id.in_(lead_ids))
                .all()
            )
            for insight in insights:
                if insight.lead_id not in insights_map:
                    insights_map[insight.lead_id] = []
                insights_map[insight.lead_id].append(
                    InsightResponse(
                        type=insight.insight_type,
                        content=insight.content,
                        confidence=float(insight.confidence)
                    )
                )

        # Format response
        prioritized_leads = []
        for lead, score in scored_leads:
            # Calculate time since inquiry
            time_delta = datetime.utcnow() - lead.created_at
            if time_delta.total_seconds() < 60:
                time_str = f"{int(time_delta.total_seconds())} seconds"
            elif time_delta.total_seconds() < 3600:
                time_str = f"{int(time_delta.total_seconds() / 60)} minutes"
            else:
                time_str = f"{int(time_delta.total_seconds() / 3600)} hours"

            # Get metadata
            metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
            vehicle_interest = metadata.get("vehicle_interest") or metadata.get("vehicleInterest")
            budget_min = metadata.get("budget_min") or metadata.get("budgetMin")
            budget_max = metadata.get("budget_max") or metadata.get("budgetMax")
            
            budget_range = None
            if budget_min and budget_max:
                budget_range = f"${budget_min:,.0f}-${budget_max:,.0f}"
            elif budget_max:
                budget_range = f"Up to ${budget_max:,.0f}"

            # Get suggested actions based on insights
            suggested_actions = []
            lead_insights = insights_map.get(lead.id, [])
            for insight in lead_insights:
                if insight.type == "talking_point":
                    suggested_actions.append(f"💡 {insight.content}")

            prioritized_leads.append(
                PrioritizedLeadItem(
                    id=lead.id,
                    name=lead.name,
                    email=lead.email,
                    phone=lead.phone,
                    score=score.overall_score,
                    priority_tier=score.priority_tier,
                    vehicle_interest=vehicle_interest,
                    budget_range=budget_range,
                    time_since_inquiry=time_str,
                    insights=lead_insights,
                    suggested_actions=suggested_actions[:3],  # Top 3 actions
                )
            )

        # Count by tier
        tier_counts = (
            db.query(LeadScore.priority_tier, func.count(LeadScore.id))
            .join(
                latest_scores,
                (LeadScore.lead_id == latest_scores.c.lead_id) &
                (LeadScore.scored_at == latest_scores.c.latest_scored_at)
            )
            .group_by(LeadScore.priority_tier)
            .all()
        )

        count_dict = {tier: count for tier, count in tier_counts}
        total_hot = count_dict.get("HOT", 0)
        total_warm = count_dict.get("WARM", 0)
        total_cold = count_dict.get("COLD", 0)

        return PrioritizedLeadsResponse(
            leads=prioritized_leads,
            total_hot=total_hot,
            total_warm=total_warm,
            total_cold=total_cold,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting prioritized leads: {str(e)}"
        )
