from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from .status import Status


class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    workflow_statuses: Mapped[list["WorkflowStatus"]] = relationship(
        "WorkflowStatus", back_populates="workflow", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Workflow(id={self.id}, name='{self.name}')>"


class WorkflowStatus(Base):
    """Association table linking workflows to statuses with ordering"""

    __tablename__ = "workflow_statuses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0)
    workflow: Mapped["Workflow"] = relationship(
        "Workflow", back_populates="workflow_statuses"
    )
    status: Mapped["Status"] = relationship(
        "Status", back_populates="workflow_statuses"
    )

    def __repr__(self):
        return f"<WorkflowStatus(workflow_id={self.workflow_id}, status_id={self.status_id}, position={self.position})>"


class WorkflowTransition(Base):
    """Defines allowed transitions between statuses in a workflow"""

    __tablename__ = "workflow_transitions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), nullable=False)
    from_status_id: Mapped[int] = mapped_column(
        ForeignKey("statuses.id"), nullable=False
    )
    to_status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"), nullable=False)

    def __repr__(self):
        return f"<WorkflowTransition(id={self.id}, from={self.from_status_id}, to={self.to_status_id})>"
