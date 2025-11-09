"""Import/export API routes for lead bulk operations."""

from __future__ import annotations

import io
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from ...models.user import User
from ...services.import_export import (
    export_leads_to_csv,
    export_leads_to_excel,
    generate_import_template,
    import_leads_from_csv,
    import_leads_from_excel,
)
from ...utils.auth import get_current_active_user

router = APIRouter()


def _safe_user_id(user: User) -> UUID | None:
    try:
        return UUID(str(user.id))
    except Exception:  # pragma: no cover - fallback
        return None


@router.post("/import/csv", status_code=status.HTTP_202_ACCEPTED)
async def import_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    if file.content_type not in {"text/csv", "application/vnd.ms-excel", "application/csv"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are supported.")
    summary = await import_leads_from_csv(file, _safe_user_id(current_user))
    return summary


@router.post("/import/excel", status_code=status.HTTP_202_ACCEPTED)
async def import_excel(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    allowed_types = {
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only Excel files are supported.")
    summary = await import_leads_from_excel(file, _safe_user_id(current_user))
    return summary


@router.post("/export/csv")
async def export_csv(
    filters: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
) -> StreamingResponse:
    csv_bytes = await export_leads_to_csv(filters)
    buffer = io.BytesIO(csv_bytes)
    headers = {
        "Content-Disposition": 'attachment; filename="leads_export.csv"',
        "Cache-Control": "no-store",
    }
    return StreamingResponse(buffer, media_type="text/csv", headers=headers)


@router.post("/export/excel")
async def export_excel(
    filters: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
) -> StreamingResponse:
    excel_bytes = await export_leads_to_excel(filters)
    buffer = io.BytesIO(excel_bytes)
    headers = {
        "Content-Disposition": 'attachment; filename="leads_export.xlsx"',
        "Cache-Control": "no-store",
    }
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get("/import/template")
async def download_template(current_user: User = Depends(get_current_active_user)) -> StreamingResponse:
    template_bytes = generate_import_template()
    buffer = io.BytesIO(template_bytes)
    headers = {"Content-Disposition": 'attachment; filename="lead_import_template.xlsx"'}
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )

