
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pgvector.sqlalchemy import Vector

from app.models.analysis import CodeChunk, Embedding
from app.llm import get_llm_provider

log = structlog.get_logger()

BATCH_SIZE = 20


async def generate_and_store_embeddings(
    db: AsyncSession, chunks: list[CodeChunk]
) -> None:
    llm = get_llm_provider()
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        for chunk in batch:
            try:
                vector = await llm.generate_embedding(chunk.content[:8000])
                embedding = Embedding(
                    code_chunk_id=chunk.id,
                    embedding=vector,
                )
                db.add(embedding)
            except Exception as e:
                log.warning("embedding_failed", chunk_id=chunk.id, error=str(e))
        await db.commit()


async def search_codebase(
    db: AsyncSession, repository_id: int, query: str, limit: int = 5
) -> list[dict]:
    llm = get_llm_provider()
    query_vector = await llm.generate_embedding(query)

    result = await db.execute(
        select(CodeChunk, Embedding)
        .join(Embedding, Embedding.code_chunk_id == CodeChunk.id)
        .where(CodeChunk.repository_id == repository_id)
        .order_by(Embedding.embedding.cosine_distance(query_vector))
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "file_path": chunk.file_path,
            "content": chunk.content,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "language": chunk.language,
        }
        for chunk, _ in rows
    ]
