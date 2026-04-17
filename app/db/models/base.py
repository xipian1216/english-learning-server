from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def utc_timestamp_column(*, onupdate: Any | None = None) -> Column:
    return Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=onupdate,
    )


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=utcnow, sa_column_kwargs={"nullable": False})
    updated_at: datetime = Field(default_factory=utcnow, sa_column_kwargs={"nullable": False})
