from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StartInterviewRequest(BaseModel):
    repository_id: int

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StartInterviewRequest(BaseModel):
  repository_id: int


class AnswerRequest(BaseModel):
  answer_text: str


class QuestionResponse(BaseModel):
  id: int
  session_id: int
  question_text: str
  question_type: Optional[str] = None
  difficulty: Optional[str] = None
  related_file: Optional[str] = None
  order_index: int

  model_config = {"from_attributes": True}


class EvaluationResponse(BaseModel):
  id: int
  score: float
  technical_correctness: Optional[float] = None
  code_understanding: Optional[float] = None
  architecture_understanding: Optional[float] = None
  communication: Optional[float] = None
  practical_thinking: Optional[float] = None
  strengths: Optional[list] = None
  weaknesses: Optional[list] = None
  ideal_answer: Optional[str] = None
  suggestions: Optional[list] = None
  resources: Optional[list] = None

  model_config = {"from_attributes": True}


class AnswerResponse(BaseModel):
  id: int
  answer_text: str
  evaluation: Optional[EvaluationResponse] = None

  model_config = {"from_attributes": True}


class QuestionWithAnswer(BaseModel):
  id: int
  question_text: str
  question_type: Optional[str] = None
  difficulty: Optional[str] = None
  related_file: Optional[str] = None
  order_index: int
  answer: Optional[AnswerResponse] = None

  model_config = {"from_attributes": True}


class InterviewSessionResponse(BaseModel):
  id: int
  repository_id: int
  status: str
  overall_score: Optional[float] = None
  summary: Optional[str] = None
  started_at: datetime
  ended_at: Optional[datetime] = None
  questions: list[QuestionWithAnswer] = []

  model_config = {"from_attributes": True}


class AgentStatusMessage(BaseModel):
  type: str
  message: str
  tool_name: Optional[str] = None


class InterviewStepResponse(BaseModel):
  session_id: Optional[int] = None
  question: Optional[QuestionResponse] = None
  evaluation: Optional[EvaluationResponse] = None
  agent_messages: list[AgentStatusMessage] = []
  interview_ended: bool = False
  summary: Optional[str] = None
  overall_score: Optional[float] = None
