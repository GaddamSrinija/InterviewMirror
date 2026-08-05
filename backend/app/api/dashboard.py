from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.repository import Repository
from app.models.interview import InterviewSession
from app.models.analysis import AnalysisJob

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    repos = await db.execute(
        select(func.count(Repository.id)).where(Repository.user_id == user.id)
    )
    interviews = await db.execute(
        select(func.count(InterviewSession.id)).where(InterviewSession.user_id == user.id)
    )
    completed = await db.execute(
        select(func.count(InterviewSession.id))
        .where(InterviewSession.user_id == user.id)
        .where(InterviewSession.status == "completed")
    )
    avg_score = await db.execute(
        select(func.avg(InterviewSession.overall_score))
        .where(InterviewSession.user_id == user.id)
        .where(InterviewSession.overall_score.isnot(None))
    )

    return {
        "total_repositories": repos.scalar() or 0,
        "total_interviews": interviews.scalar() or 0,
        "completed_interviews": completed.scalar() or 0,
        "average_score": round(avg_score.scalar() or 0, 1),
    }
