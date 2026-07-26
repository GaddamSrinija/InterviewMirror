from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.user import User
from app.models.repository import Repository
from app.models.analysis import AnalysisJob, CodeChunk, Embedding
from app.models.interview import InterviewSession, Question, Answer, Evaluation, AgentToolCall
from app.models.report import PerformanceReport

__all__ = [
    "Base", "User", "Repository", "AnalysisJob", "CodeChunk", "Embedding",
    "InterviewSession", "Question", "Answer", "Evaluation", "AgentToolCall",
    "PerformanceReport",
]