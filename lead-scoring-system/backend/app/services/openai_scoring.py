"""OpenAI-powered AI lead scoring service.

This service uses GPT-4 to analyze leads and provide intelligent scoring,
classification, and insights based on lead data, engagement patterns, and context.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from openai import OpenAI
from sqlalchemy.orm import Session

from ..models import Lead, LeadActivity, LeadEngagementEvent, LeadInsight, LeadScore


# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY", "")
openai_client = OpenAI(api_key=api_key) if api_key else None


def get_lead_context(lead_id: UUID, db: Session) -> Dict:
    """Gather all context about a lead for AI analysis."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return {}
    
    # Get recent activities
    activities = (
        db.query(LeadActivity)
        .filter(LeadActivity.lead_id == lead_id)
        .order_by(LeadActivity.timestamp.desc())
        .limit(10)
        .all()
    )
    
    # Get engagement events
    engagement_events = (
        db.query(LeadEngagementEvent)
        .filter(LeadEngagementEvent.lead_id == lead_id)
        .order_by(LeadEngagementEvent.created_at.desc())
        .limit(20)
        .all()
    )
    
    # Build context
    context = {
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "source": lead.source,
        "location": lead.location,
        "current_score": lead.current_score,
        "classification": lead.classification,
        "status": lead.status.value if lead.status else None,
        "metadata": lead._metadata if hasattr(lead, '_metadata') else {},
        "activities": [
            {
                "type": act.activity_type,
                "points": act.points_awarded,
                "timestamp": act.timestamp.isoformat(),
            }
            for act in activities
        ],
        "engagement_events": [
            {
                "type": event.event_type,
                "data": event.event_data,
                "created_at": event.created_at.isoformat(),
            }
            for event in engagement_events
        ],
    }
    
    return context


def analyze_lead_with_openai(lead_context: Dict) -> Dict:
    """Use OpenAI GPT-4 to analyze and score a lead."""
    
    if not openai_client:
        raise ValueError("OPENAI_API_KEY not set")
    
    # Build prompt for OpenAI
    prompt = f"""You are an expert AI lead scoring analyst for a sales CRM system. 
Analyze the following lead information and provide a comprehensive scoring assessment.

LEAD INFORMATION:
- Name: {lead_context.get('name', 'N/A')}
- Email: {lead_context.get('email', 'N/A')}
- Phone: {lead_context.get('phone', 'N/A')}
- Source: {lead_context.get('source', 'N/A')}
- Location: {lead_context.get('location', 'N/A')}
- Current Status: {lead_context.get('status', 'N/A')}
- Metadata: {json.dumps(lead_context.get('metadata', {}), indent=2)}

RECENT ACTIVITIES ({len(lead_context.get('activities', []))} activities):
{json.dumps(lead_context.get('activities', [])[:5], indent=2)}

ENGAGEMENT EVENTS ({len(lead_context.get('engagement_events', []))} events):
{json.dumps(lead_context.get('engagement_events', [])[:10], indent=2)}

Based on this information, provide a JSON response with the following structure:
{{
    "overall_score": <integer 0-100>,
    "engagement_score": <integer 0-100>,
    "buying_signal_score": <integer 0-100>,
    "demographic_score": <integer 0-100>,
    "priority_tier": "<HOT|WARM|COLD>",
    "confidence_level": <float 0.0-1.0>,
    "reasoning": "<detailed explanation of the scoring>",
    "insights": [
        {{
            "type": "<talking_point|concern|opportunity>",
            "content": "<insight text>",
            "confidence": <float 0.0-1.0>
        }}
    ],
    "scoring_metadata": {{
        "key_factors": ["<factor1>", "<factor2>", ...],
        "strengths": ["<strength1>", "<strength2>", ...],
        "weaknesses": ["<weakness1>", "<weakness2>", ...],
        "recommended_actions": ["<action1>", "<action2>", ...]
    }}
}}

SCORING CRITERIA:
1. Engagement Score (0-100): Based on recent activity, email opens, website visits, time spent
2. Buying Signal Score (0-100): Based on specific actions like requesting demo, pricing inquiry, form submissions
3. Demographic Score (0-100): Based on location, source quality, company fit, industry alignment
4. Overall Score: Weighted average (Engagement 35%, Buying Signals 40%, Demographic 25%)
5. Priority Tier: HOT (80+), WARM (50-79), COLD (<50)
6. Confidence Level: How confident you are in the scoring (0.0-1.0)

Be thorough and analytical. Consider:
- Lead source quality (referrals > organic > paid > cold)
- Engagement patterns (frequency, recency, depth)
- Buying signals (demo requests, pricing questions, feature interest)
- Demographic fit (location, industry, company size if available)
- Activity recency (more recent = higher score)

Respond ONLY with valid JSON, no additional text."""

    try:
        # Use GPT-4 for best results, fallback to GPT-3.5-turbo if needed
        model = "gpt-4-turbo-preview"  # or "gpt-4" or "gpt-3.5-turbo"
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert AI lead scoring analyst. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # Use new OpenAI API format
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,  # Lower temperature for more consistent scoring
            max_tokens=2000,
            response_format={"type": "json_object"} if "gpt-4" in model else None,
        )
        
        # Parse response
        content = response.choices[0].message.content
        result = json.loads(content)
        
        return result
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, try to extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError(f"Failed to parse OpenAI response as JSON: {e}")
    
    except Exception as e:
        raise ValueError(f"OpenAI API error: {str(e)}")


def score_lead_with_openai(lead_id: UUID, db: Session) -> Tuple[Dict, List[Dict]]:
    """Score a lead using OpenAI and return score data and insights."""
    
    # Get lead context
    context = get_lead_context(lead_id, db)
    
    if not context:
        raise ValueError(f"Lead {lead_id} not found")
    
    # Analyze with OpenAI
    ai_result = analyze_lead_with_openai(context)
    
        # Extract scores
    score_data = {
        "overall_score": int(ai_result.get("overall_score", 0)),
        "engagement_score": int(ai_result.get("engagement_score", 0)),
        "buying_signal_score": int(ai_result.get("buying_signal_score", 0)),
        "demographic_score": int(ai_result.get("demographic_score", 0)),
        "priority_tier": ai_result.get("priority_tier", "COLD"),
        "confidence_level": float(ai_result.get("confidence_level", 0.5)),
        "scoring_metadata": {
            **ai_result.get("scoring_metadata", {}),
            "openai_model": "gpt-4-turbo-preview",
            "scoring_method": "openai",
            "reasoning": ai_result.get("reasoning", ""),
        },
        "reasoning": ai_result.get("reasoning", ""),
    }
    
    # Extract insights
    insights = ai_result.get("insights", [])
    
    return score_data, insights


def save_openai_score(lead_id: UUID, db: Session, score_data: Dict, insights: List[Dict]) -> LeadScore:
    """Save OpenAI-generated score to database."""
    
    # Create LeadScore record
    lead_score = LeadScore(
        lead_id=lead_id,
        overall_score=score_data["overall_score"],
        engagement_score=score_data["engagement_score"],
        buying_signal_score=score_data["buying_signal_score"],
        demographic_score=score_data["demographic_score"],
        priority_tier=score_data["priority_tier"],
        confidence_level=score_data["confidence_level"],
        scoring_metadata=score_data.get("scoring_metadata", {}),
    )
    
    db.add(lead_score)
    db.flush()
    
    # Save insights
    for insight_data in insights:
        insight = LeadInsight(
            lead_id=lead_id,
            insight_type=insight_data.get("type", "talking_point"),
            content=insight_data.get("content", ""),
            confidence=float(insight_data.get("confidence", 0.5)),
        )
        db.add(insight)
    
    # Update lead's current score and classification
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if lead:
        lead.current_score = score_data["overall_score"]
        lead.classification = score_data["priority_tier"].lower()
    
    db.commit()
    db.refresh(lead_score)
    
    return lead_score

