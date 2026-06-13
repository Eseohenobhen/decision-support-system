from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_property_manager, get_db
from app.models.user import User
from app.services.report_service import (
    build_report_file,
    get_fund_allocation_report,
    get_maintenance_history,
    get_monthly_financial_report,
    get_property_summary,
)

router = APIRouter()


def _validate_format(format: str) -> str:
    normalized = format.lower()
    if normalized not in {"pdf", "xlsx"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="format must be pdf or xlsx",
        )
    return normalized


def _make_response(file_obj, filename: str, format: str) -> StreamingResponse:
    content_type = "application/pdf" if format == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return StreamingResponse(
        file_obj,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
        },
    )


@router.get("/property-summary")
def export_property_summary(
    format: str = Query("pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> StreamingResponse:
    format = _validate_format(format)
    rows = get_property_summary(db, current_user)
    file_obj = build_report_file("Property Summary", rows, format)
    return _make_response(file_obj, f"property-summary.{format}", format)


@router.get("/fund-allocation")
def export_fund_allocation(
    format: str = Query("pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> StreamingResponse:
    format = _validate_format(format)
    rows = get_fund_allocation_report(db, current_user)
    file_obj = build_report_file("Fund Allocation Report", rows, format)
    return _make_response(file_obj, f"fund-allocation-report.{format}", format)


@router.get("/maintenance-history")
def export_maintenance_history(
    format: str = Query("pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> StreamingResponse:
    format = _validate_format(format)
    rows = get_maintenance_history(db, current_user)
    file_obj = build_report_file("Maintenance History", rows, format)
    return _make_response(file_obj, f"maintenance-history.{format}", format)


@router.get("/monthly-financial")
def export_monthly_financial(
    format: str = Query("pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_property_manager),
) -> StreamingResponse:
    format = _validate_format(format)
    rows = get_monthly_financial_report(db, current_user)
    file_obj = build_report_file("Monthly Financial Report", rows, format)
    return _make_response(file_obj, f"monthly-financial-report.{format}", format)
