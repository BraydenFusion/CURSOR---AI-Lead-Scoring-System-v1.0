"""Advanced analytics endpoints for admins and managers."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, Iterable, List, Optional, Tuple
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.assignment import LeadAssignment
from ...models.lead import Lead, LeadStatus
from ...models.user import User, UserRole
from ...utils.auth import require_role


router = APIRouter()


ALLOWED_ROLES = [UserRole.ADMIN, UserRole.MANAGER]


def _parse_iso_date(value: str, field: str) -> date:
    try:
        return datetime.fromisoformat(value).date()
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field}. Expected ISO date (YYYY-MM-DD).",
        ) from exc


def _normalize_period(
    period: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
) -> Tuple[datetime, datetime, str]:
    today = datetime.utcnow().date()
    normalized_period = (period or "30days").lower()

    if start_date and end_date:
        start = _parse_iso_date(start_date, "start_date")
        finish = _parse_iso_date(end_date, "end_date")
    else:
        if normalized_period not in {"7days", "30days", "90days"}:
            normalized_period = "30days"
        offset = int(normalized_period.replace("days", ""))
        finish = today
        start = today - timedelta(days=offset - 1)

    if start > finish:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")

    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(finish, datetime.max.time())
    return start_dt, end_dt, normalized_period


def _normalize_source(source: Optional[str]) -> Optional[str]:
    if not source or source.lower() in {"all", "any"}:
        return None
    return source


def _normalize_rep(rep_id: Optional[str]) -> Optional[UUID]:
    if not rep_id or rep_id.lower() in {"all", "any"}:
        return None
    try:
        return UUID(rep_id)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(
            status_code=400,
            detail="Invalid rep_id. Expected UUID string.",
        ) from exc


def _normalize_statuses(status: Optional[str]) -> Optional[List[str]]:
    if not status:
        return None
    if isinstance(status, list):  # type: ignore[unreachable]
        items = status
    else:
        items = [part.strip() for part in status.split(",") if part.strip()]

    normalized: List[str] = []
    for item in items:
        try:
            normalized.append(LeadStatus(item.lower()).value)
        except ValueError:
            continue
    return normalized or None


def _filtered_lead_ids_subquery(
    db: Session,
    start_dt: datetime,
    end_dt: datetime,
    source: Optional[str],
    rep_uuid: Optional[UUID],
    statuses: Optional[List[str]] = None,
):
    query = db.query(Lead.id)

    if rep_uuid:
        query = query.join(LeadAssignment, LeadAssignment.lead_id == Lead.id)
        query = query.filter(LeadAssignment.user_id == rep_uuid)

    if source:
        query = query.filter(func.lower(Lead.source) == source.lower())

    if statuses:
        query = query.filter(Lead.status.in_(statuses))

    query = query.filter(Lead.created_at >= start_dt, Lead.created_at <= end_dt)
    return query.distinct().subquery()


def _query_filtered_leads(
    db: Session,
    lead_ids_subquery,
):
    return (
        db.query(Lead)
        .join(lead_ids_subquery, Lead.id == lead_ids_subquery.c.id)
        .all()
    )


def _count_filtered_leads(
    db: Session,
    lead_ids_subquery,
) -> int:
    return db.query(func.count()).select_from(lead_ids_subquery).scalar() or 0


def _get_sales_reps(db: Session, rep_uuid: Optional[UUID]) -> List[User]:
    query = db.query(User).filter(User.role == UserRole.SALES_REP.value)
    if rep_uuid:
        query = query.filter(User.id == rep_uuid)
    return query.all()


@router.get("/overview")
def get_overview(
    period: Optional[str] = Query(default="30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: Optional[str] = Query(default=None),
    rep_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role(ALLOWED_ROLES)),
):
    """High-level analytics for admins/managers."""
    start_dt, end_dt, normalized_period = _normalize_period(period, start_date, end_date)
    normalized_source = _normalize_source(source)
    rep_uuid = _normalize_rep(rep_id)
    statuses = _normalize_statuses(status)

    lead_ids_subquery = _filtered_lead_ids_subquery(
        db, start_dt, end_dt, normalized_source, rep_uuid, statuses
    )
    total_leads = _count_filtered_leads(db, lead_ids_subquery)

    hot_leads = (
        db.query(func.count())
        .select_from(Lead)
        .join(lead_ids_subquery, Lead.id == lead_ids_subquery.c.id)
        .filter(Lead.classification == "hot")
        .scalar()
        or 0
    )

    warm_leads = (
        db.query(func.count())
        .select_from(Lead)
        .join(lead_ids_subquery, Lead.id == lead_ids_subquery.c.id)
        .filter(Lead.classification == "warm")
        .scalar()
        or 0
    )

    cold_leads = (
        db.query(func.count())
        .select_from(Lead)
        .join(lead_ids_subquery, Lead.id == lead_ids_subquery.c.id)
        .filter(Lead.classification == "cold")
        .scalar()
        or 0
    )

    converted_leads = (
        db.query(func.count())
        .select_from(Lead)
        .join(lead_ids_subquery, Lead.id == lead_ids_subquery.c.id)
        .filter(Lead.status == LeadStatus.WON)
        .scalar()
        or 0
    )

    conversion_rate = round((converted_leads / total_leads) * 100, 2) if total_leads else 0.0

    avg_score = (
        db.query(func.avg(Lead.current_score))
        .join(lead_ids_subquery, Lead.id == lead_ids_subquery.c.id)
        .scalar()
    )

    avg_score_value = round(float(avg_score), 2) if avg_score is not None else 0.0

    # Month-over-month growth
    today = datetime.utcnow()
    current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    previous_month_end = current_month_start - timedelta(seconds=1)
    previous_month_start = previous_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    leads_this_month = (
        db.query(func.count(Lead.id))
        .filter(Lead.created_at >= current_month_start, Lead.created_at <= today)
    )
    leads_last_month = (
        db.query(func.count(Lead.id))
        .filter(Lead.created_at >= previous_month_start, Lead.created_at <= previous_month_end)
    )

    if normalized_source:
        leads_this_month = leads_this_month.filter(func.lower(Lead.source) == normalized_source.lower())
        leads_last_month = leads_last_month.filter(func.lower(Lead.source) == normalized_source.lower())

    if rep_uuid:
        leads_this_month = leads_this_month.join(LeadAssignment, LeadAssignment.lead_id == Lead.id).filter(
            LeadAssignment.user_id == rep_uuid
        )
        leads_last_month = leads_last_month.join(LeadAssignment, LeadAssignment.lead_id == Lead.id).filter(
            LeadAssignment.user_id == rep_uuid
        )

    leads_this_month_value = leads_this_month.scalar() or 0
    leads_last_month_value = leads_last_month.scalar() or 0

    if leads_last_month_value:
        growth_rate = round(((leads_this_month_value - leads_last_month_value) / leads_last_month_value) * 100, 2)
    else:
        growth_rate = 100.0 if leads_this_month_value > 0 else 0.0

    return {
        "total_leads": total_leads,
        "hot_leads": hot_leads,
        "warm_leads": warm_leads,
        "cold_leads": cold_leads,
        "conversion_rate": conversion_rate,
        "avg_score": avg_score_value,
        "leads_this_month": leads_this_month_value,
        "leads_last_month": leads_last_month_value,
        "growth_rate": growth_rate,
        "period": normalized_period,
        "filters": {
            "source": normalized_source,
            "rep_id": str(rep_uuid) if rep_uuid else None,
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
        },
    }


@router.get("/conversion-funnel")
def get_conversion_funnel(
    period: Optional[str] = Query(default="30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: Optional[str] = Query(default=None),
    rep_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role(ALLOWED_ROLES)),
):
    start_dt, end_dt, _ = _normalize_period(period, start_date, end_date)
    normalized_source = _normalize_source(source)
    rep_uuid = _normalize_rep(rep_id)
    statuses = _normalize_statuses(status)

    lead_ids_subquery = _filtered_lead_ids_subquery(
        db, start_dt, end_dt, normalized_source, rep_uuid, statuses
    )
    total_leads = _count_filtered_leads(db, lead_ids_subquery)

    stages = [
        ("New", LeadStatus.NEW),
        ("Contacted", LeadStatus.CONTACTED),
        ("Qualified", LeadStatus.QUALIFIED),
        ("Won", LeadStatus.WON),
    ]

    stage_data = []
    for label, status in stages:
        count = (
            db.query(func.count())
            .select_from(Lead)
            .join(lead_ids_subquery, Lead.id == lead_ids_subquery.c.id)
            .filter(Lead.status == status)
            .scalar()
            or 0
        )
        percentage = round((count / total_leads) * 100, 1) if total_leads else 0.0
        stage_data.append({"name": label, "count": count, "percentage": percentage})

    return {"stages": stage_data}


@router.get("/lead-sources")
def get_lead_sources(
    period: Optional[str] = Query(default="30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    rep_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role(ALLOWED_ROLES)),
):
    start_dt, end_dt, _ = _normalize_period(period, start_date, end_date)
    rep_uuid = _normalize_rep(rep_id)
    statuses = _normalize_statuses(status)

    query = (
        db.query(
            func.lower(Lead.source).label("source"),
            func.count(Lead.id).label("total"),
            func.sum(
                case((Lead.status == LeadStatus.WON, 1), else_=0)
            ).label("converted"),
        )
        .filter(Lead.created_at >= start_dt, Lead.created_at <= end_dt)
    )

    if rep_uuid:
        query = query.join(LeadAssignment, LeadAssignment.lead_id == Lead.id).filter(
            LeadAssignment.user_id == rep_uuid
        )

    if statuses:
        query = query.filter(Lead.status.in_(statuses))

    query = query.group_by(func.lower(Lead.source))

    results = []
    for row in query:
        total = row.total or 0
        converted = row.converted or 0
        conversion_rate = round((converted / total) * 100, 2) if total else 0.0
        results.append(
            {
                "source": row.source.title() if row.source else "Unknown",
                "count": total,
                "converted": converted,
                "conversion_rate": conversion_rate,
            }
        )

    return {"sources": sorted(results, key=lambda x: x["count"], reverse=True)}


@router.get("/rep-performance")
def get_rep_performance(
    period: Optional[str] = Query(default="30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: Optional[str] = Query(default=None),
    rep_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role(ALLOWED_ROLES)),
):
    start_dt, end_dt, _ = _normalize_period(period, start_date, end_date)
    normalized_source = _normalize_source(source)
    rep_uuid = _normalize_rep(rep_id)
    statuses = _normalize_statuses(status)

    reps = _get_sales_reps(db, rep_uuid)
    performance = []

    for rep in reps:
        assignment_query = (
            db.query(LeadAssignment, Lead)
            .join(Lead, Lead.id == LeadAssignment.lead_id)
            .filter(LeadAssignment.user_id == rep.id)
            .filter(LeadAssignment.assigned_at >= start_dt, LeadAssignment.assigned_at <= end_dt)
        )

        if normalized_source:
            assignment_query = assignment_query.filter(func.lower(Lead.source) == normalized_source.lower())

        if statuses:
            assignment_query = assignment_query.filter(Lead.status.in_(statuses))

        assignments = assignment_query.all()

        if not assignments:
            continue

        leads_assigned = len(assignments)
        leads_contacted = sum(
            1
            for assignment, lead in assignments
            if lead.contacted_at and start_dt <= lead.contacted_at <= end_dt
        )
        leads_converted = sum(
            1
            for assignment, lead in assignments
            if lead.status == LeadStatus.WON and lead.closed_at and start_dt <= lead.closed_at <= end_dt
        )

        response_times = []
        for assignment, lead in assignments:
            if lead.contacted_at:
                response_delta = lead.contacted_at - assignment.assigned_at
                response_times.append(response_delta.total_seconds() / 3600)

        avg_response_time = round(sum(response_times) / len(response_times), 2) if response_times else 0.0
        conversion_rate = round((leads_converted / leads_assigned) * 100, 2) if leads_assigned else 0.0

        performance.append(
            {
                "rep_id": str(rep.id),
                "rep_name": rep.full_name,
                "leads_assigned": leads_assigned,
                "leads_contacted": leads_contacted,
                "leads_converted": leads_converted,
                "conversion_rate": conversion_rate,
                "avg_response_time_hours": avg_response_time,
            }
        )

    return {"reps": performance}


@router.get("/score-distribution")
def get_score_distribution(
    period: Optional[str] = Query(default="30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: Optional[str] = Query(default=None),
    rep_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role(ALLOWED_ROLES)),
):
    start_dt, end_dt, _ = _normalize_period(period, start_date, end_date)
    normalized_source = _normalize_source(source)
    rep_uuid = _normalize_rep(rep_id)
    statuses = _normalize_statuses(status)

    lead_ids_subquery = _filtered_lead_ids_subquery(
        db, start_dt, end_dt, normalized_source, rep_uuid, statuses
    )

    buckets = [
        ("0-20", 0, 20),
        ("21-40", 21, 40),
        ("41-60", 41, 60),
        ("61-80", 61, 80),
        ("81-100", 81, 100),
    ]

    distribution = []
    for label, lower, upper in buckets:
        count = (
            db.query(func.count())
            .select_from(Lead)
            .join(lead_ids_subquery, Lead.id == lead_ids_subquery.c.id)
            .filter(Lead.current_score >= lower, Lead.current_score <= upper)
            .scalar()
            or 0
        )
        distribution.append({"range": label, "count": count})

    return {"distribution": distribution}


@router.get("/timeline")
def get_timeline(
    period: Optional[str] = Query(default="30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: Optional[str] = Query(default=None),
    rep_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role(ALLOWED_ROLES)),
):
    start_dt, end_dt, normalized_period = _normalize_period(period, start_date, end_date)
    normalized_source = _normalize_source(source)
    rep_uuid = _normalize_rep(rep_id)
    statuses = _normalize_statuses(status)

    lead_ids_subquery = _filtered_lead_ids_subquery(
        db, start_dt, end_dt, normalized_source, rep_uuid, statuses
    )
    leads = _query_filtered_leads(db, lead_ids_subquery)

    contacted_leads = [
        lead
        for lead in leads
        if lead.contacted_at and start_dt <= lead.contacted_at <= end_dt
    ]
    converted_leads = [
        lead
        for lead in leads
        if lead.status == LeadStatus.WON and lead.closed_at and start_dt <= lead.closed_at <= end_dt
    ]

    num_days = (end_dt.date() - start_dt.date()).days + 1

    new_counts: Dict[date, int] = defaultdict(int)
    contacted_counts: Dict[date, int] = defaultdict(int)
    converted_counts: Dict[date, int] = defaultdict(int)
    score_totals: Dict[date, int] = defaultdict(int)
    score_counts: Dict[date, int] = defaultdict(int)

    for lead in leads:
        created_day = lead.created_at.date()
        new_counts[created_day] += 1
        score_totals[created_day] += lead.current_score
        score_counts[created_day] += 1

    for lead in contacted_leads:
        contacted_counts[lead.contacted_at.date()] += 1

    for lead in converted_leads:
        converted_counts[lead.closed_at.date()] += 1

    daily_stats = []
    for index in range(num_days):
        day = start_dt.date() + timedelta(days=index)
        avg_score = 0.0
        if score_counts[day]:
            avg_score = round(score_totals[day] / score_counts[day], 1)

        daily_stats.append(
            {
                "date": day.isoformat(),
                "new_leads": new_counts[day],
                "contacted": contacted_counts[day],
                "converted": converted_counts[day],
                "avg_score": avg_score,
            }
        )

    return {
        "period": normalized_period,
        "daily_stats": daily_stats,
    }



