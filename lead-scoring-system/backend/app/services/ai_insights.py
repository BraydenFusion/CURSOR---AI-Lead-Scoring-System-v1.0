"""AI-powered lead insights and content generation helpers."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from openai import OpenAI
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.models import Lead, LeadActivity, LeadNote

logger = logging.getLogger(__name__)

INSIGHTS_CACHE_KEY = "ai_insights_cache"
INSIGHTS_RATE_KEY = "ai_insights_requests"
EMAIL_RATE_KEY = "ai_email_requests"
COST_LOG_KEY = "ai_cost_tracking"
CACHE_TTL_HOURS = 24
RATE_LIMIT_MAX_CALLS = 3
RATE_LIMIT_WINDOW = timedelta(minutes=30)

# Pricing for gpt-4-turbo-preview (USD per 1K tokens)
PROMPT_COST_PER_1K = 0.01
COMPLETION_COST_PER_1K = 0.03

settings = get_settings()


class OpenAIUnavailableError(RuntimeError):
    """Raised when OpenAI is not configured."""


def _require_api_key() -> None:
    if not settings.openai_api_key:
        raise OpenAIUnavailableError("OpenAI API key is not configured.")


def _get_client() -> OpenAI:
    _require_api_key()
    return OpenAI(api_key=settings.openai_api_key)


def _ensure_metadata(lead: Lead) -> Dict[str, Any]:
    metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
    lead._metadata = metadata
    return metadata


def _iso_to_datetime(value: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    prompt_cost = (prompt_tokens / 1000) * PROMPT_COST_PER_1K
    completion_cost = (completion_tokens / 1000) * COMPLETION_COST_PER_1K
    return round(prompt_cost + completion_cost, 6)


def _enforce_rate_limit(lead: Lead, key: str) -> None:
    metadata = _ensure_metadata(lead)
    now = datetime.utcnow()
    history: List[str] = metadata.get(key, [])
    recent = [
        entry for entry in history if _iso_to_datetime(entry) and now - _iso_to_datetime(entry) <= RATE_LIMIT_WINDOW
    ]
    if len(recent) >= RATE_LIMIT_MAX_CALLS:
        raise ValueError("Rate limit exceeded for this lead. Please try again later.")
    recent.append(now.isoformat())
    metadata[key] = recent


def _format_activities(activities: List[LeadActivity]) -> str:
    if not activities:
        return "No recorded activities."
    sorted_activities = sorted(activities, key=lambda act: act.timestamp, reverse=True)[:15]
    lines = []
    for activity in sorted_activities:
        description = activity.activity_type.replace("_", " ").title()
        timestamp = activity.timestamp.strftime("%Y-%m-%d %H:%M UTC")
        details = activity._metadata or {}
        detail_snippet = ""
        if details:
            detail_parts = [f"{k}: {v}" for k, v in details.items() if isinstance(v, (str, int, float))]
            if detail_parts:
                detail_snippet = f" ({', '.join(detail_parts[:3])})"
        lines.append(f"- {timestamp}: {description}{detail_snippet}")
    return "\n".join(lines)


def _format_notes(notes: List[LeadNote]) -> str:
    if not notes:
        return "No notes available."
    sorted_notes = sorted(notes, key=lambda note: note.created_at, reverse=True)[:10]
    lines = []
    for note in sorted_notes:
        timestamp = note.created_at.strftime("%Y-%m-%d %H:%M UTC")
        preview = (note.content[:180] + "...") if len(note.content) > 180 else note.content
        lines.append(f"- {timestamp} [{note.note_type.title()}] {preview}")
    return "\n".join(lines)


def _build_lead_context(lead: Lead) -> Dict[str, Any]:
    metadata = lead._metadata or {}
    engagement = metadata.get("engagement_metrics", {})
    return {
        "name": lead.name,
        "company": metadata.get("company_name") or metadata.get("company") or "Unknown Company",
        "score": lead.current_score,
        "classification": lead.classification or "unknown",
        "source": lead.source,
        "status": lead.status.value if hasattr(lead.status, "value") else lead.status,
        "location": lead.location or metadata.get("region"),
        "industry": metadata.get("industry", "Unknown"),
        "website_visits": engagement.get("website_visits", metadata.get("website_visits", 0)),
        "email_opens": engagement.get("email_opens", metadata.get("email_opens", 0)),
        "email_clicks": engagement.get("email_clicks", metadata.get("email_clicks", 0)),
        "demo_requests": engagement.get("demo_requests", metadata.get("demo_requests", 0)),
        "pricing_page_views": engagement.get("pricing_page_views", metadata.get("pricing_page_views", 0)),
        "recent_activities": metadata.get("recent_activity_summary"),
    }


def _summarize_activities_counts(activities: List[LeadActivity]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for activity in activities:
        counts[activity.activity_type] = counts.get(activity.activity_type, 0) + 1
    return counts


def _prepare_system_prompt() -> str:
    return (
        "You are a sales intelligence assistant. Analyze leads and provide actionable insights. "
        "Always respond with valid JSON matching the provided schema."
    )


def _prepare_insight_user_prompt(lead: Lead, activities: List[LeadActivity], notes: List[LeadNote]) -> str:
    context = _build_lead_context(lead)
    activity_counts = _summarize_activities_counts(activities)
    return (
        "Lead Information:\n"
        f"- Name: {context['name']}\n"
        f"- Company: {context['company']}\n"
        f"- Score: {context['score']} ({context['classification']})\n"
        f"- Source: {context['source']}\n"
        f"- Status: {context['status']}\n"
        f"- Industry: {context['industry']}\n"
        f"- Location: {context.get('location')}\n\n"
        "Engagement Metrics:\n"
        f"- Website visits: {context['website_visits']}\n"
        f"- Email engagement: {context['email_opens']} opens, {context['email_clicks']} clicks\n"
        f"- Demo requests: {context['demo_requests']}\n"
        f"- Pricing page views: {context['pricing_page_views']}\n"
        f"- Activity breakdown: {activity_counts}\n\n"
        "Activity History:\n"
        f"{_format_activities(activities)}\n\n"
        "Notes:\n"
        f"{_format_notes(notes)}\n\n"
        "Provide insights as instructed."
    )


def _insights_response_schema() -> Dict[str, Any]:
    return {
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "summary_confidence": {"type": "number"},
                "recommended_actions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {"type": "integer"},
                            "time_estimate": {"type": "string"},
                        },
                        "required": ["title", "description"],
                    },
                },
                "conversion_probability": {
                    "type": "object",
                    "properties": {
                        "level": {"type": "string"},
                        "confidence": {"type": "number"},
                        "reasoning": {"type": "array", "items": {"type": "string"}},
                        "comparison_to_similar": {"type": "string"},
                    },
                },
                "talking_points": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "details": {"type": "string"},
                        },
                        "required": ["title", "details"],
                    },
                },
            },
            "required": ["summary", "recommended_actions", "conversion_probability", "talking_points"],
        },
    }


async def _create_chat_completion(messages: List[Dict[str, str]], *, max_tokens: int = 600) -> Any:
    client = _get_client()

    def _call():
        return client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens,
            response_format=_insights_response_schema(),
        )

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _call)


def _update_cost_tracking(metadata: Dict[str, Any], prompt_tokens: int, completion_tokens: int) -> float:
    cost = _calculate_cost(prompt_tokens, completion_tokens)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost": cost,
    }
    history: List[Dict[str, Any]] = metadata.get(COST_LOG_KEY, [])
    history.append(entry)
    metadata[COST_LOG_KEY] = history[-50:]  # keep last 50 entries
    return cost


def _serialize_insight_payload(lead_id: UUID, raw: Dict[str, Any], cost: float) -> Dict[str, Any]:
    actions = raw.get("recommended_actions") or []
    normalized_actions = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        normalized_actions.append(
            {
                "title": action.get("title", "Action"),
                "description": action.get("description", ""),
                "priority": action.get("priority", 3),
                "time_estimate": action.get("time_estimate", "30 minutes"),
                "done": False,
            }
        )

    probability = raw.get("conversion_probability") or {}
    talking_points = raw.get("talking_points") or []

    normalized_points = []
    for point in talking_points:
        if not isinstance(point, dict):
            continue
        normalized_points.append(
            {
                "title": point.get("title", "Talking Point"),
                "details": point.get("details", ""),
            }
        )

    return {
        "lead_id": str(lead_id),
        "summary": raw.get("summary", "No summary available."),
        "summary_confidence": raw.get("summary_confidence"),
        "recommended_actions": normalized_actions,
        "conversion_probability": {
            "level": probability.get("level", "unknown"),
            "confidence": probability.get("confidence"),
            "reasoning": probability.get("reasoning", []),
            "comparison_to_similar": probability.get("comparison_to_similar"),
        },
        "talking_points": normalized_points,
        "generated_at": datetime.utcnow().isoformat(),
        "estimated_cost": cost,
    }


def _serialize_email_payload(raw: Dict[str, Any], cost: float) -> Dict[str, Any]:
    return {
        "subject": raw.get("subject", "Follow-up from our team"),
        "body": raw.get("body", ""),
        "call_to_action": raw.get("call_to_action", ""),
        "estimated_cost": cost,
        "generated_at": datetime.utcnow().isoformat(),
    }


def _insights_from_cache(metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    cache: Dict[str, Any] = metadata.get(INSIGHTS_CACHE_KEY) or {}
    generated_at = cache.get("generated_at")
    if not generated_at:
        return None
    timestamp = _iso_to_datetime(generated_at)
    if not timestamp or datetime.utcnow() - timestamp > timedelta(hours=CACHE_TTL_HOURS):
        return None
    return cache.get("data")


def _store_insights_cache(metadata: Dict[str, Any], payload: Dict[str, Any]) -> None:
    metadata[INSIGHTS_CACHE_KEY] = {
        "generated_at": payload["generated_at"],
        "data": payload,
    }


def get_lead_with_full_history(db: Session, lead_id: UUID) -> Optional[Lead]:
    return (
        db.query(Lead)
        .options(
            joinedload(Lead.activities),
            joinedload(Lead.notes),
        )
        .filter(Lead.id == lead_id)
        .one_or_none()
    )


async def generate_lead_insights(db: Session, lead_id: UUID) -> Dict[str, Any]:
    lead = get_lead_with_full_history(db, lead_id)
    if not lead:
        raise ValueError("Lead not found.")

    metadata = _ensure_metadata(lead)

    cached = _insights_from_cache(metadata)
    if cached:
        logger.debug("Returning cached AI insights for lead %s", lead_id)
        return cached

    _enforce_rate_limit(lead, INSIGHTS_RATE_KEY)

    user_prompt = _prepare_insight_user_prompt(lead, lead.activities, lead.notes)
    messages = [
        {"role": "system", "content": _prepare_system_prompt()},
        {
            "role": "user",
            "content": (
                f"{user_prompt}\n\n"
                "Respond strictly with JSON containing the keys: "
                "summary, summary_confidence, recommended_actions, conversion_probability, talking_points."
            ),
        },
    ]

    response = await _create_chat_completion(messages)
    content = response.choices[0].message.content if response.choices else "{}"

    try:
        parsed: Dict[str, Any] = response.choices[0].message.parsed if hasattr(response.choices[0].message, "parsed") else {}
    except Exception:  # pragma: no cover - fallback to manual parsing
        import json

        parsed = json.loads(content or "{}")

    usage = response.usage or None
    prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
    completion_tokens = getattr(usage, "completion_tokens", 0) if usage else 0

    cost = _update_cost_tracking(metadata, prompt_tokens, completion_tokens)
    logger.info(
        "AI insights generated for lead %s (prompt tokens=%s, completion tokens=%s, cost=$%.5f)",
        lead_id,
        prompt_tokens,
        completion_tokens,
        cost,
    )
    payload = _serialize_insight_payload(lead_id, parsed, cost)

    _store_insights_cache(metadata, payload)
    db.add(lead)
    db.commit()

    return payload


def _email_schema() -> Dict[str, Any]:
    return {
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "call_to_action": {"type": "string"},
            },
            "required": ["subject", "body"],
        },
    }


async def generate_email_template(db: Session, lead_id: UUID, email_type: str) -> Dict[str, Any]:
    lead = get_lead_with_full_history(db, lead_id)
    if not lead:
        raise ValueError("Lead not found.")

    _enforce_rate_limit(lead, EMAIL_RATE_KEY)
    metadata = _ensure_metadata(lead)

    context = _build_lead_context(lead)
    prompt = (
        f"Create a personalized {email_type} email for:\n"
        f"- Lead: {context['name']} from {context['company']}\n"
        f"- Industry: {context['industry']}\n"
        f"- Current engagement score: {context['score']}\n"
        f"- Recent activity summary: {context.get('recent_activities') or 'No recent summary available.'}\n"
        "The email should be professional, personalized, and action-oriented. "
        "Return JSON with the keys 'subject', 'body', and 'call_to_action'."
    )

    messages = [
        {"role": "system", "content": _prepare_system_prompt()},
        {"role": "user", "content": prompt},
    ]

    client = _get_client()

    def _call():
        return client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.6,
            max_tokens=400,
            response_format=_email_schema(),
        )

    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, _call)

    content = response.choices[0].message.content if response.choices else "{}"
    try:
        parsed: Dict[str, Any] = response.choices[0].message.parsed if hasattr(response.choices[0].message, "parsed") else {}
    except Exception:  # pragma: no cover
        import json

        parsed = json.loads(content or "{}")

    usage = response.usage or None
    prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
    completion_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
    cost = _update_cost_tracking(metadata, prompt_tokens, completion_tokens)
    logger.info(
        "AI email generated for lead %s (type=%s, prompt tokens=%s, completion tokens=%s, cost=$%.5f)",
        lead_id,
        email_type,
        prompt_tokens,
        completion_tokens,
        cost,
    )

    payload = _serialize_email_payload(parsed, cost)
    db.add(lead)
    db.commit()
    return payload


async def get_next_best_actions(db: Session, lead_id: UUID) -> Dict[str, Any]:
    """Derive the next best action list (leveraging cached insights when available)."""
    insights = await generate_lead_insights(db, lead_id)
    return {
        "lead_id": insights["lead_id"],
        "recommended_actions": insights["recommended_actions"],
        "generated_at": insights["generated_at"],
    }

