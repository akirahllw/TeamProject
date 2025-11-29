import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from .issue import Issue
    from .workflow import WorkflowStatus


class StatusCategory(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class Status(Base):
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    color: Mapped[str | None] = mapped_column(String(7))
    category: Mapped[StatusCategory] = mapped_column(
        Enum(StatusCategory), default=StatusCategory.TODO, nullable=False
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    workflow_statuses: Mapped[list["WorkflowStatus"]] = relationship(
        "WorkflowStatus", back_populates="status"
    )

    def __repr__(self):
        return f"<Status(id={self.id}, name='{self.name}', category='{self.category}')>"
