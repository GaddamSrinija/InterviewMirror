from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.interview import InterviewSessionResponse
from app.services.interview_service import get_user_sessions

router = APIRouter()


@router.get("/", response_model=list[InterviewSessionResponse])
async def get_history(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sessions = await get_user_sessions(db, user.id)
    return [InterviewSessionResponse.model_validate(s) for s in sessions]