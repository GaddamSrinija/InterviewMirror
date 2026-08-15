
import json
from datetime import datetime, timezone
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.analysis import AnalysisJob, CodeChunk
from app.models.repository import Repository
from app.services.github_service import get_repo_tree, get_file_content
from app.services.embedding_service import generate_and_store_embeddings
from app.services.storage_service import upload_snapshot
from app.llm import get_llm_provider

log = structlog.get_logger()

IMPORTANT_FILES = {
    "README.md", "package.json", "requirements.txt", "Dockerfile",
    "docker-compose.yml", "Makefile", ".env.example", "pyproject.toml",
    "setup.py", "tsconfig.json", "vite.config.js", "next.config.js",
    "webpack.config.js", "tailwind.config.js",
}
IMPORTANT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs",
    ".rb", ".php", ".cs", ".swift", ".kt", ".scala", ".sql",
    ".yaml", ".yml", ".toml", ".json", ".graphql",
}
MAX_FILES_TO_ANALYZE = 80
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


def _detect_language(path: str) -> str:
    ext_map = {
        ".py": "python", ".js": "javascript", ".jsx": "javascript",
        ".ts": "typescript", ".tsx": "typescript", ".java": "java",
        ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php",
        ".cs": "csharp", ".swift": "swift", ".kt": "kotlin",
        ".sql": "sql", ".yaml": "yaml", ".yml": "yaml",
        ".json": "json", ".toml": "toml",
    }
    for ext, lang in ext_map.items():
        if path.endswith(ext):
            return lang
    return "text"


def _chunk_content(content: str, file_path: str) -> list[dict]:
    lines = content.split("\n")
    chunks = []
    idx = 0
    start = 0
    while start < len(lines):
        end = min(start + CHUNK_SIZE, len(lines))
        chunk_lines = lines[start:end]
        chunk_text = "\n".join(chunk_lines)
        if chunk_text.strip():
            chunks.append({
                "content": f"# File: {file_path}\n\n{chunk_text}",
                "chunk_index": idx,
                "start_line": start + 1,
                "end_line": end,
                "language": _detect_language(file_path),
            })
            idx += 1
        start = end - CHUNK_OVERLAP if end < len(lines) else end
    return chunks


def _prioritize_files(files: list[dict]) -> list[dict]:
    important = []
    regular = []
    for f in files:
        name = f["path"].split("/")[-1]
        ext = "." + name.rsplit(".", 1)[-1] if "." in name else ""
        if name in IMPORTANT_FILES or ext in IMPORTANT_EXTENSIONS:
            if name in IMPORTANT_FILES:
                important.append(f)
            else:
                regular.append(f)
    regular.sort(key=lambda x: x.get("size", 0), reverse=True)
    combined = important + regular
    return combined[:MAX_FILES_TO_ANALYZE]


async def _extract_metadata(file_contents: dict[str, str]) -> dict:
    llm = get_llm_provider()
    sample_files = list(file_contents.items())[:15]
    file_summaries = ""
    for path, content in sample_files:
        preview = content[:500]
        file_summaries += f"\n--- {path} ---\n{preview}\n"

    prompt = f"""Analyze this repository and extract metadata as JSON:
{{
  "architecture": "description of overall architecture",
  "framework": "primary framework used",
  "language": "primary programming language",
  "apis": ["list of API endpoints or patterns found"],
  "authentication": "authentication method if any",
  "database": "database technology if any",
  "services": ["key services or modules"],
  "middleware": ["middleware used"],
  "components": ["key components"],
  "external_apis": ["external APIs integrated"],
  "deployment": "deployment configuration",
  "security": ["security measures found"]
}}

Files:
{file_summaries}

Return ONLY valid JSON."""

    response = await llm.chat([{"role": "user", "content": prompt}])
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        return json.loads(response[start:end])
    except (json.JSONDecodeError, ValueError):
        return {"architecture": "unknown", "framework": "unknown"}


async def run_analysis(job_id: int, repository_id: int) -> None:
    async with async_session() as db:
        job = None
        try:
            job = await db.get(AnalysisJob, job_id)
            repo = await db.get(Repository, repository_id)
            if not job or not repo:
                return

            job.status = "running"
            job.started_at = datetime.now(timezone.utc)
            job.current_step = "Fetching repository tree"
            job.progress = 5
            await db.commit()

            files = await get_repo_tree(repo.owner, repo.name, repo.default_branch)
            prioritized = _prioritize_files(files)

            job.current_step = "Downloading source files"
            job.progress = 15
            await db.commit()

            file_contents: dict[str, str] = {}
            for i, f in enumerate(prioritized):
                content = await get_file_content(
                    repo.owner, repo.name, f["path"], repo.default_branch
                )
                if content.strip():
                    file_contents[f["path"]] = content
                progress = 15 + int((i / len(prioritized)) * 30) if prioritized else 45
                job.progress = min(progress, 45)
                job.current_step = f"Downloading: {f['path']}"
                await db.commit()

            job.current_step = "Chunking code"
            job.progress = 50
            await db.commit()

            all_chunks = []
            for path, content in file_contents.items():
                chunks = _chunk_content(content, path)
                for chunk in chunks:
                    code_chunk = CodeChunk(
                        repository_id=repository_id,
                        file_path=path,
                        content=chunk["content"],
                        chunk_index=chunk["chunk_index"],
                        language=chunk["language"],
                        start_line=chunk["start_line"],
                        end_line=chunk["end_line"],
                    )
                    db.add(code_chunk)
                    all_chunks.append(code_chunk)
            await db.commit()

            job.current_step = "Generating embeddings"
            job.progress = 60
            await db.commit()

            await generate_and_store_embeddings(db, all_chunks)

            job.current_step = "Extracting metadata"
            job.progress = 85
            await db.commit()

            metadata = await _extract_metadata(file_contents)
            job.metadata_json = metadata

            job.current_step = "Uploading project snapshot"
            job.progress = 95
            await db.commit()

            snapshot_bytes = json.dumps({
                "file_contents": file_contents,
                "metadata": metadata,
            }).encode("utf-8")
            snapshot_key = f"snapshots/{repo.owner}/{repo.name}/{repository_id}.json"
            backend_type = await upload_snapshot(snapshot_bytes, snapshot_key)

            job.snapshot_storage_key = snapshot_key
            job.snapshot_storage_backend = backend_type
            job.status = "completed"
            job.progress = 100
            job.current_step = "Analysis complete"
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()

            log.info("repository_analysis_completed", repo_id=repository_id)
        except Exception as e:
            log.exception("repository_analysis_failed", error=str(e))
            if job:
                job.status = "failed"
                job.error_message = str(e)
                await db.commit()
