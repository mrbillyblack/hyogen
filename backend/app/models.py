"""ORM models. A single table caches kanjiapi.dev responses."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Kanji(Base):
    """One row per character we've looked up on kanjiapi.dev.

    `not_found` rows record characters kanjiapi has no data for (e.g. a CJK
    character outside the ~13k set) so we don't re-fetch them on every request.
    """

    __tablename__ = "kanji"

    character: Mapped[str] = mapped_column(String(8), primary_key=True)

    not_found: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    jlpt: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stroke_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unicode: Mapped[str | None] = mapped_column(String(16), nullable=True)
    heisig_en: Mapped[str | None] = mapped_column(String(128), nullable=True)

    meanings: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    kun_readings: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    on_readings: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    name_readings: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Raw kanjiapi payload, kept for forward-compat / debugging.
    raw: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
