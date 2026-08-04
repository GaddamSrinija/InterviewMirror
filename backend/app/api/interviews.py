from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.interview import InterviewSession, Question
from app.models.repository import Repository
from app.schemas.interview import (
    StartInterviewRequest, AnswerRequest, InterviewSessionResponse,
    InterviewStepResponse, QuestionResponse, EvaluationResponse,
    AgentStatusMessage,
)
from app.services.interview_service import (
    create_session, get_session, add_answer,
)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.interview import InterviewSession, Question
from app.models.repository import Repository
from app.schemas.interview import (
  StartInterviewRequest, AnswerRequest, InterviewSessionResponse,
  InterviewStepResponse, QuestionResponse, EvaluationResponse,
  AgentStatusMessage,
)
from app.services.interview_service import (
  create_session, get_session, add_answer,
)
from app.services.agent_service import run_agent_step

router = APIRouter()


@router.post("/start", response_model=InterviewStepResponse)
async def start_interview(
  data: StartInterviewRequest,
  db: AsyncSession = Depends(get_db),
  user: User = Depends(get_current_user),
):
  repo = await db.get(Repository, data.repository_id)
  if not repo or repo.user_id != user.id:
      raise HTTPException(status_code=404, detail="Repository not found")

  session = await create_session(db, user.id, data.repository_id)

  result = await run_agent_step(db, session.id, data.repository_id)

  return _build_step_response(result, session.id)


@router.post("/{session_id}/answer", response_model=InterviewStepResponse)
async def submit_answer(
  session_id: int,
  data: AnswerRequest,
  db: AsyncSession = Depends(get_db),
  user: User = Depends(get_current_user),
):
  session = await get_session(db, session_id)
  if not session or session.user_id != user.id:
      raise HTTPException(status_code=404, detail="Session not found")
  if session.status == "completed":
      raise HTTPException(status_code=400, detail="Interview already completed")

  unanswered = [q for q in session.questions if not q.answer]
  pending_answer_id = None
  if unanswered:
      latest_q = unanswered[-1]
      new_answer = await add_answer(db, latest_q.id, data.answer_text)
      pending_answer_id = new_answer.id

  result = await run_agent_step(
      db, session_id, session.repository_id, data.answer_text,
      pending_answer_id=pending_answer_id,
  )

  return _build_step_response(result, session.id)


@router.get("/{session_id}", response_model=InterviewSessionResponse)
async def get_interview(
  session_id: int,
  db: AsyncSession = Depends(get_db),
  user: User = Depends(get_current_user),
):
  session = await get_session(db, session_id)
  if not session or session.user_id != user.id:
      raise HTTPException(status_code=404, detail="Session not found")
  return InterviewSessionResponse.model_validate(session)


def _build_step_response(result: dict, session_id: int) -> InterviewStepResponse:
  question = None
  if result.get("question"):
      question = QuestionResponse.model_validate(result["question"])

  evaluation = None
  if result.get("evaluation"):
      evaluation = EvaluationResponse.model_validate(result["evaluation"])

  return InterviewStepResponse(
      session_id=session_id,
      question=question,
      evaluation=evaluation,
      agent_messages=result.get("agent_messages", []),
      interview_ended=result.get("interview_ended", False),
      summary=result.get("end_data", {}).get("overall_summary") if result.get("end_data") else None,
      overall_score=result.get("end_data", {}).get("overall_score") if result.get("end_data") else None,
  )
