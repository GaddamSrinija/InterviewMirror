from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.config import settings
from app.api import auth, repositories, interviews, reports, dashboard, history

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log = structlog.get_logger()
    log.info("interview_mirror_starting")
    yield
    log.info("interview_mirror_shutting_down")


app = FastAPI(title="Interview Mirror", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(repositories.router, prefix="/api/repositories", tags=["Repositories"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["Interviews"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(history.router, prefix="/api/history", tags=["History"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
