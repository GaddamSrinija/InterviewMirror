from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interview import InterviewSession, Question, Answer, Evaluation
from app.models.repository import Repository
from app.models.analysis import AnalysisJob


async def create_session(
    db: AsyncSession, user_id: int, repository_id: int
) -> InterviewSession:
    result = await db.execute(
        select(AnalysisJob)
        .where(AnalysisJob.repository_id == repository_id)
        .where(AnalysisJob.status == "completed")
        .order_by(AnalysisJob.completed_at.desc())
        .limit(1)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise ValueError("Repository analysis not completed yet")

    session = InterviewSession(
        user_id=user_id,
        repository_id=repository_id,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(db: AsyncSession, session_id: int) -> InterviewSession | None:
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .options(
            selectinload(InterviewSession.questions)
            .selectinload(Question.answer)
            .selectinload(Answer.evaluation)
        )
    )
    return result.scalar_one_or_none()


async def add_question(
    db: AsyncSession,
    session_id: int,
    question_text: str,
    question_type: str | None = None,
    difficulty: str | None = None,
    related_file: str | None = None,
) -> Question:
    result = await db.execute(
        select(Question)
        .where(Question.session_id == session_id)
        .order_by(Question.order_index.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    order_index = (last.order_index + 1) if last else 0

    question = Question(
        session_id=session_id,
        question_text=question_text,
        question_type=question_type,
        difficulty=difficulty,
        related_file=related_file,
        order_index=order_index,
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


async def add_answer(
    db: AsyncSession, question_id: int, answer_text: str
) -> Answer:
    answer = Answer(question_id=question_id, answer_text=answer_text)
    db.add(answer)
    await db.commit()
    await db.refresh(answer)
    return answer


async def add_evaluation(db: AsyncSession, answer_id: int, data: dict) -> Evaluation:
    evaluation = Evaluation(
        answer_id=answer_id,
        score=data.get("score", 0),
        technical_correctness=data.get("technical_correctness"),
        code_understanding=data.get("code_understanding"),
        architecture_understanding=data.get("architecture_understanding"),
        communication=data.get("communication"),
        practical_thinking=data.get("practical_thinking"),
        strengths=data.get("strengths"),
        weaknesses=data.get("weaknesses"),
        ideal_answer=data.get("ideal_answer"),
        suggestions=data.get("suggestions"),
        resources=data.get("resources"),
    )
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)
    return evaluation


async def end_session(
    db: AsyncSession,
    session_id: int,
    overall_score: float,
    summary: str,
) -> InterviewSession:
    session = await db.get(InterviewSession, session_id)
    if session:
        session.status = "completed"
        session.overall_score = overall_score
        session.summary = summary
        session.ended_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(session)
    return session


async def get_user_sessions(
    db: AsyncSession, user_id: int
) -> list[InterviewSession]:
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.user_id == user_id)
        .options(selectinload(InterviewSession.repository))
        .order_by(InterviewSession.started_at.desc())
    )
    return list(result.scalars().all())