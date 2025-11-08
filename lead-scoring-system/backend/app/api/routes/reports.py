"""Routes for managing saved analytics reports."""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...config import get_settings
from ...database import get_db
from ...models.lead import Lead, LeadStatus
from ...models.report import SavedReport
from ...models.user import User, UserRole
from ...schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportRunRequest,
    ReportRunResult,
    ReportUpdate,
)
from ...services.email_service import email_service
from ...utils.auth import require_role
from .analytics import (
    _filtered_lead_ids_subquery,
    _normalize_period,
    _normalize_rep,
    _normalize_source,
    _query_filtered_leads,
    _count_filtered_leads,
)
from .analytics import get_lead_sources as analytics_lead_sources
from .analytics import get_overview as analytics_overview
from .analytics import get_conversion_funnel as analytics_funnel
from .analytics import get_rep_performance as analytics_rep_performance
from .analytics import get_score_distribution as analytics_score_distribution
from .analytics import get_timeline as analytics_timeline

router = APIRouter()

ALLOWED_ROLES = [UserRole.ADMIN, UserRole.MANAGER]


def _merge_filters(base_filters: Dict[str, Any], override: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge base filters with overrides, overriding keys when provided."""
    merged = {**base_filters}
    if override:
        merged.update(override)
    return merged


def _prepare_filter_payload(filters: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize filters into analytics-friendly payload."""
    normalized = filters.copy()
    normalized.setdefault("date_range", filters.get("date_range", "30days"))
    source_value = filters.get("source") or filters.get("sources") or None
    if isinstance(source_value, list):
        source_value = source_value[0] if source_value else None
    rep_value = filters.get("rep_id") or filters.get("rep") or None
    if isinstance(rep_value, list):
        rep_value = rep_value[0] if rep_value else None
    status_value = filters.get("status") or filters.get("statuses") or None
    if isinstance(status_value, list):
        status_value = ",".join(status_value)

    normalized["source"] = source_value
    normalized["rep_id"] = rep_value
    normalized["status"] = status_value
    normalized.setdefault("start_date", filters.get("start_date"))
    normalized.setdefault("end_date", filters.get("end_date"))
    return normalized


def _ensure_report_owner(report: SavedReport, user: User) -> None:
    """Ensure the user owns the report."""
    if report.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this report.")


def _generate_pdf(report_name: str, dataframes: Dict[str, pd.DataFrame]) -> bytes:
    """Generate a simple PDF summary using reportlab."""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setTitle(report_name)
    margin = 40
    y = height - margin

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(margin, y, report_name)
    y -= 30

    pdf.setFont("Helvetica", 10)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    pdf.drawString(margin, y, f"Generated at {timestamp}")
    y -= 20

    for sheet_name, df in dataframes.items():
        if y < 120:
            pdf.showPage()
            y = height - margin
            pdf.setFont("Helvetica-Bold", 14)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(margin, y, sheet_name)
        y -= 18
        pdf.setFont("Helvetica", 9)
        if df.empty:
            pdf.drawString(margin, y, "No data for this section.")
            y -= 18
            continue

        # Draw table
        col_width = (width - 2 * margin) / max(len(df.columns), 1)
        # Header
        for idx, column in enumerate(df.columns):
            pdf.drawString(margin + idx * col_width, y, str(column))
        y -= 14

        for _, row in df.iterrows():
            for idx, value in enumerate(row):
                pdf.drawString(margin + idx * col_width, y, str(value))
            y -= 12
            if y < 80:
                pdf.showPage()
                y = height - margin
                pdf.setFont("Helvetica", 9)

        y -= 20

    pdf.save()
    buffer.seek(0)
    return buffer.read()


def _prepare_dataframes(report_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """Convert report data into Pandas DataFrames for export."""
    frames: Dict[str, pd.DataFrame] = {}
    for key, payload in report_data.items():
        if isinstance(payload, dict):
            if any(isinstance(v, (list, tuple)) for v in payload.values()):
                long_rows = []
                for sub_key, items in payload.items():
                    if isinstance(items, list):
                        for item in items:
                            if isinstance(item, dict):
                                row = {"section": sub_key, **item}
                            else:
                                row = {"section": sub_key, "value": item}
                            long_rows.append(row)
                    else:
                        long_rows.append({"section": sub_key, "value": items})
                frames[key.title()] = pd.DataFrame(long_rows)
            else:
                frames[key.title()] = pd.DataFrame([payload])
        elif isinstance(payload, list):
            frames[key.title()] = pd.DataFrame(payload)
        else:
            frames[key.title()] = pd.DataFrame([{"value": payload}])
    return frames


def _send_report_email(user: User, report: SavedReport, data: Dict[str, Any]) -> None:
    """Send summary email if SMTP is configured."""
    settings = get_settings()
    if not settings.smtp_host or not settings.from_email:
        return

    summary_lines = []
    for metric, payload in data.items():
        if isinstance(payload, dict):
            for sub_key, value in payload.items():
                summary_lines.append(f"{metric.title()} - {sub_key}: {value}")
        else:
            summary_lines.append(f"{metric.title()}: {payload}")

    text_body = f"""Hi {user.full_name},

Your scheduled report "{report.name}" has been generated.

Highlights:
{chr(10).join(f"- {line}" for line in summary_lines[:10])}

You can download the full report from the platform.

Best,
Lead Scoring System
"""

    html_body = f"""
<html>
  <body>
    <p>Hi {user.full_name},</p>
    <p>Your scheduled report <strong>{report.name}</strong> has been generated.</p>
    <p><strong>Highlights:</strong></p>
    <ul>
      {''.join(f'<li>{line}</li>' for line in summary_lines[:10])}
    </ul>
    <p>You can download the full report from the platform.</p>
    <p>Best regards,<br/>Lead Scoring System</p>
  </body>
</html>
"""

    email_service.send_email(
        to_email=user.email,
        subject=f"Report Ready: {report.name}",
        body=text_body,
        html_body=html_body,
    )


def _generate_report_payload(
    db: Session,
    user: User,
    report: SavedReport,
    filters_override: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate report data based on selected metrics."""
    filters_raw = _merge_filters(report.filters or {}, filters_override)
    filter_payload = _prepare_filter_payload(filters_raw)
    metrics = report.metrics or []

    # We re-use analytics endpoints internally to ensure consistent data
    overview_data = None
    payload: Dict[str, Any] = {}

    if any(metric in metrics for metric in ["total_leads", "conversion_rate"]):
        overview_data = analytics_overview(
            period=filter_payload.get("date_range", "30days"),
            start_date=filter_payload.get("start_date"),
            end_date=filter_payload.get("end_date"),
            source=filter_payload.get("source"),
            rep_id=filter_payload.get("rep_id"),
            status=filter_payload.get("status"),
            db=db,
            _=user,  # type: ignore[arg-type]
        )
        payload["overview"] = overview_data

    if "lead_sources_breakdown" in metrics:
        payload["lead_sources"] = analytics_lead_sources(
            period=filter_payload.get("date_range", "30days"),
            start_date=filter_payload.get("start_date"),
            end_date=filter_payload.get("end_date"),
            rep_id=filter_payload.get("rep_id"),
            status=filter_payload.get("status"),
            db=db,
            _=user,  # type: ignore[arg-type]
        )

    if "conversion_rate" in metrics or "conversion_funnel" in metrics:
        payload["conversion_funnel"] = analytics_funnel(
            period=filter_payload.get("date_range", "30days"),
            start_date=filter_payload.get("start_date"),
            end_date=filter_payload.get("end_date"),
            source=filter_payload.get("source"),
            rep_id=filter_payload.get("rep_id"),
            status=filter_payload.get("status"),
            db=db,
            _=user,  # type: ignore[arg-type]
        )

    if "rep_performance" in metrics:
        payload["rep_performance"] = analytics_rep_performance(
            period=filter_payload.get("date_range", "30days"),
            start_date=filter_payload.get("start_date"),
            end_date=filter_payload.get("end_date"),
            source=filter_payload.get("source"),
            rep_id=filter_payload.get("rep_id"),
            status=filter_payload.get("status"),
            db=db,
            _=user,  # type: ignore[arg-type]
        )

    if "score_distribution" in metrics:
        payload["score_distribution"] = analytics_score_distribution(
            period=filter_payload.get("date_range", "30days"),
            start_date=filter_payload.get("start_date"),
            end_date=filter_payload.get("end_date"),
            source=filter_payload.get("source"),
            rep_id=filter_payload.get("rep_id"),
            status=filter_payload.get("status"),
            db=db,
            _=user,  # type: ignore[arg-type]
        )

    if "timeline_analysis" in metrics:
        payload["timeline"] = analytics_timeline(
            period=filter_payload.get("date_range", "30days"),
            start_date=filter_payload.get("start_date"),
            end_date=filter_payload.get("end_date"),
            source=filter_payload.get("source"),
            rep_id=filter_payload.get("rep_id"),
            status=filter_payload.get("status"),
            db=db,
            _=user,  # type: ignore[arg-type]
        )

    if overview_data and "total_leads" in metrics:
        payload.setdefault("summary", {})["total_leads"] = overview_data.get("total_leads", 0)
    if overview_data and "conversion_rate" in metrics:
        payload.setdefault("summary", {})["conversion_rate"] = overview_data.get("conversion_rate", 0.0)
    if overview_data and "hot_leads" in metrics:
        payload.setdefault("summary", {})["hot_leads"] = overview_data.get("hot_leads", 0)
    if overview_data and "avg_score" in metrics:
        payload.setdefault("summary", {})["avg_score"] = overview_data.get("avg_score", 0.0)

    return payload


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
) -> ReportResponse:
    """Create a saved report."""
    new_report = SavedReport(
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        report_type=payload.report_type.lower(),
        filters=payload.filters or {},
        metrics=payload.metrics,
        schedule=payload.schedule.lower() if payload.schedule else None,
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return ReportResponse.model_validate(new_report)


@router.get("", response_model=List[ReportResponse])
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
) -> List[ReportResponse]:
    """List reports for the current user."""
    reports = (
        db.query(SavedReport)
        .filter(SavedReport.user_id == current_user.id)
        .order_by(SavedReport.created_at.desc())
        .all()
    )
    return [ReportResponse.model_validate(report) for report in reports]


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
) -> ReportResponse:
    """Get a specific saved report."""
    report = db.query(SavedReport).filter(SavedReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    _ensure_report_owner(report, current_user)
    return ReportResponse.model_validate(report)


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    payload: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
) -> ReportResponse:
    """Update a saved report."""
    report = db.query(SavedReport).filter(SavedReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    _ensure_report_owner(report, current_user)

    if payload.name is not None:
        report.name = payload.name
    if payload.description is not None:
        report.description = payload.description
    if payload.report_type is not None:
        report.report_type = payload.report_type.lower()
    if payload.filters is not None:
        report.filters = payload.filters
    if payload.metrics is not None:
        report.metrics = payload.metrics
    if payload.schedule is not None:
        report.schedule = payload.schedule.lower() if payload.schedule else None

    db.commit()
    db.refresh(report)
    return ReportResponse.model_validate(report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
) -> Response:
    """Delete a saved report."""
    report = db.query(SavedReport).filter(SavedReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    _ensure_report_owner(report, current_user)

    db.delete(report)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{report_id}/run", response_model=ReportRunResult)
def run_report(
    report_id: int,
    run_request: ReportRunRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
) -> ReportRunResult:
    """Generate report data immediately."""
    report = db.query(SavedReport).filter(SavedReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    _ensure_report_owner(report, current_user)

    data = _generate_report_payload(db, current_user, report, run_request.filters if run_request else None)

    report.last_run = datetime.utcnow()
    db.commit()

    if report.requires_email_delivery():
        _send_report_email(current_user, report, data)

    return ReportRunResult(
        report_id=report.id,
        generated_at=report.last_run,
        metrics=report.metrics,
        data=data,
    )


@router.get("/{report_id}/export")
def export_report(
    report_id: int,
    format: str = Query(default="csv", pattern="^(csv|pdf|xlsx)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
):
    """Export report to CSV, PDF, or XLSX."""
    report = db.query(SavedReport).filter(SavedReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    _ensure_report_owner(report, current_user)

    data = _generate_report_payload(db, current_user, report)
    frames = _prepare_dataframes(data)
    filename_base = report.name.replace(" ", "_").lower()

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        for sheet_name, df in frames.items():
            writer.writerow([sheet_name])
            if df.empty:
                writer.writerow(["No data"])
            else:
                writer.writerow(df.columns.tolist())
                for row in df.itertuples(index=False):
                    writer.writerow(list(row))
            writer.writerow([])
        response = StreamingResponse(
            iter([output.getvalue()]), media_type="text/csv"
        )
        response.headers["Content-Disposition"] = f'attachment; filename="{filename_base}.csv"'
        return response

    if format == "xlsx":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            for sheet_name, df in frames.items():
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        output.seek(0)
        response = StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response.headers["Content-Disposition"] = f'attachment; filename="{filename_base}.xlsx"'
        return response

    # PDF
    pdf_bytes = _generate_pdf(report.name, frames)
    response = StreamingResponse(
        iter([pdf_bytes]), media_type="application/pdf"
    )
    response.headers["Content-Disposition"] = f'attachment; filename="{filename_base}.pdf"'
    return response


