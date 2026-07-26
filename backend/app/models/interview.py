from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, Integer, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE")
    )
    status: Mapped[str] = mapped_column(String(50), server_default="in_progress")
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user = relationship("User", back_populates="interview_sessions")
    repository = relationship("Repository", back_populates="interview_sessions")
    questions = relationship(
        "Question", back_populates="session", cascade="all, delete-orphan",
        order_by="Question.order_index"
    )
    report = relationship(
        "PerformanceReport", back_populates="session", uselist=False,
        cascade="all, delete-orphan"
    )
    tool_calls = relationship(
        "AgentToolCall", back_populates="session", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE")
    )
    question_text: Mapped[str] = mapped_column(Text)
    question_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    related_file: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship(
        "Answer", back_populates="question", uselist=False, cascade="all, delete-orphan"
    )


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), unique=True
    )
    answer_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    question = relationship("Question", back_populates="answer")
    evaluation = relationship(
        "Evaluation", back_populates="answer", uselist=False,
        cascade="all, delete-orphan"
    )


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    answer_id: Mapped[int] = mapped_column(
        ForeignKey("answers.id", ondelete="CASCADE"), unique=True
    )
    score: Mapped[float] = mapped_column(Float)
    technical_correctness: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    code_understanding: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    architecture_understanding: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    communication: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    practical_thinking: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    strengths: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    ideal_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    suggestions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    resources: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    answer = relationship("Answer", back_populates="evaluation")


class AgentToolCall(Base):
    __tablename__ = "agent_tool_calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE")
    )
    tool_name: Mapped[str] = mapped_column(String(100))
    tool_input: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tool_output: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session = relationship("InterviewSession", back_populates="tool_calls")