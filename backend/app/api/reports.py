from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.interview import InterviewSession
from app.models.report import PerformanceReport
from app.schemas.report import ReportResponse
from app.services.report_service import generate_report
from app.services.storage_service import get_file_path

router = APIRouter()


@router.post("/{session_id}/generate", response_model=ReportResponse)
async def create_report(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = await db.get(InterviewSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Interview not completed")

    existing = await db.execute(
        select(PerformanceReport).where(PerformanceReport.session_id == session_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Report already exists")

    report = await generate_report(db, session_id)
    return ReportResponse.model_validate(report)


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = await db.get(PerformanceReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    session = await db.get(InterviewSession, report.session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        file_path = get_file_path(report.storage_key)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=f"interview_report_{report.session_id}.pdf",
    )
