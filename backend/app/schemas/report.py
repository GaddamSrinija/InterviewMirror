from datetime import datetime
from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: int
    session_id: int
    storage_key: str
    storage_backend: str
    generated_at: datetime

    model_config = {"from_attributes": True}


class ReportDownloadResponse(BaseModel):
    download_url: str
    expires_in_seconds: int = 900