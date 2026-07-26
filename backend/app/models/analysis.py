from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.models import Base


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE")
    )
    status: Mapped[str] = mapped_column(String(50), server_default="pending")
    progress: Mapped[int] = mapped_column(Integer, server_default="0")
    current_step: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    snapshot_storage_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    snapshot_storage_backend: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    repository = relationship("Repository", back_populates="analysis_jobs")


class CodeChunk(Base):
    __tablename__ = "code_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE")
    )
    file_path: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    chunk_index: Mapped[int] = mapped_column(Integer)
    language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    start_line: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_line: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    repository = relationship("Repository", back_populates="code_chunks")
    embedding = relationship(
        "Embedding", back_populates="code_chunk", uselist=False,
        cascade="all, delete-orphan"
    )


class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(primary_key=True)
    code_chunk_id: Mapped[int] = mapped_column(
        ForeignKey("code_chunks.id", ondelete="CASCADE"), unique=True
    )
    embedding = mapped_column(Vector(1536))

    code_chunk = relationship("CodeChunk", back_populates="embedding")