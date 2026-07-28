from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.repository import Repository
from app.models.analysis import AnalysisJob
from app.schemas.repository import RepositoryImport, RepositoryResponse, AnalysisJobResponse
from app.services.github_service import parse_github_url, validate_repository
from app.services.analyzer_service import run_analysis

router = APIRouter()


@router.post("/", response_model=RepositoryResponse)
async def import_repository(
    body: RepositoryImport,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    owner, name = parse_github_url(str(body.github_url))
    repo_info = await validate_repository(owner, name)

    repo = Repository(
        user_id=user.id,
        github_url=str(body.github_url),
        owner=owner,
        name=name,
        description=repo_info.get("description"),
        language=repo_info.get("language"),
        default_branch=repo_info.get("default_branch", "main"),
    )
    db.add(repo)
    await db.commit()
    await db.refresh(repo)

    job = AnalysisJob(repository_id=repo.id, status="pending", progress=0)
    db.add(job)
    await db.commit()
    await db.refresh(job)

    background_tasks.add_task(run_analysis, job.id, repo.id)

    return repo


@router.get("/", response_model=list[RepositoryResponse])
async def list_repositories(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Repository)
        .where(Repository.user_id == user.id)
        .order_by(Repository.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(
    repo_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Repository)
        .where(Repository.id == repo_id, Repository.user_id == user.id)
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo


@router.get("/{repo_id}/analysis", response_model=AnalysisJobResponse)
async def get_analysis_status(
    repo_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Repository)
        .where(Repository.id == repo_id, Repository.user_id == user.id)
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    result = await db.execute(
        select(AnalysisJob)
        .where(AnalysisJob.repository_id == repo_id)
        .order_by(AnalysisJob.created_at.desc())
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="No analysis found")
    return job
