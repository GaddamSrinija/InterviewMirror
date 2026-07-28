from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


class RepositoryImport(BaseModel):
    github_url: HttpUrl


class RepositoryResponse(BaseModel):
    id: int
    github_url: str
    owner: str
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    default_branch: str = "main"
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisJobResponse(BaseModel):
    id: int
    repository_id: int
    status: str
    progress: int
    current_step: Optional[str] = None
    metadata_json: Optional[dict] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}