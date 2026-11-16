"""
SQLAlchemy models for Resume and Analysis entities.
Module 1 (Resume) + Module 5 (Dashboard/History) data layer.
Uses SQLAlchemy 2.0 Mapped[] declarative style.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, Float, DateTime, JSON, ForeignKey

from app.extensions import db


def _uuid() -> str:
    return uuid.uuid4().hex


class Resume(db.Model):
    """Stores metadata and extracted text for each uploaded resume."""

    __tablename__ = "resumes"
    __allow_unmapped__ = True

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)

    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    linkedin: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github: Mapped[str | None] = mapped_column(String(500), nullable=True)

    word_count: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    analyses = relationship(
        "Analysis", backref="resume", cascade="all, delete-orphan", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<Resume {self.original_filename} [{self.id[:8]}]>"


class Analysis(db.Model):
    """Stores the full analysis result for one resume + target_role pair."""

    __tablename__ = "analyses"
    __allow_unmapped__ = True

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    resume_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    target_role: Mapped[str] = mapped_column(String(100), nullable=False)

    resume_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ats_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    category_scores: Mapped[Any] = mapped_column(JSON, nullable=False, default=list)
    matched_skills: Mapped[Any] = mapped_column(JSON, nullable=False, default=list)
    missing_skills: Mapped[Any] = mapped_column(JSON, nullable=False, default=list)
    suggestions: Mapped[Any] = mapped_column(JSON, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Analysis {self.target_role} score={self.resume_score} [{self.id[:8]}]>"
