import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from .project import Project
    from .sprint import Sprint
    from .user import User
    from .attachment import Attachment


class IssueType(str, enum.Enum):
    TASK = "TASK"
    BUG = "BUG"
    STORY = "STORY"
    EPIC = "EPIC"


class IssueStatus(str, enum.Enum):
    TO_DO = "TO_DO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    DONE = "DONE"


class IssuePriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus), default=IssueStatus.TO_DO, nullable=False
    )
    priority: Mapped[IssuePriority] = mapped_column(
        Enum(IssuePriority), default=IssuePriority.MEDIUM, nullable=False
    )
    issue_type: Mapped[IssueType] = mapped_column(
        Enum(IssueType), default=IssueType.TASK, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    parent_issue_id: Mapped[int | None] = mapped_column(ForeignKey("issues.id"))
    sprint_id: Mapped[int | None] = mapped_column(ForeignKey("sprints.id"))

    project: Mapped["Project"] = relationship("Project", back_populates="issues")

    reporter: Mapped["User"] = relationship(
        "User", back_populates="reported_issues", foreign_keys=[reporter_id]
    )

    assignee: Mapped[Optional["User"]] = relationship(
        "User", back_populates="assigned_issues", foreign_keys=[assignee_id]
    )

    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="issue", cascade="all, delete-orphan"
    )

    parent: Mapped[Optional["Issue"]] = relationship(
        "Issue", back_populates="sub_tasks", remote_side=[id]
    )
    sub_tasks: Mapped[list["Issue"]] = relationship(
        "Issue", back_populates="parent", cascade="all, delete-orphan"
    )

    sprint: Mapped[Optional["Sprint"]] = relationship("Sprint", back_populates="issues")

    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment", back_populates="issue", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Issue(id={self.id}, title='{self.title}', status='{self.status}')>"


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    issue: Mapped["Issue"] = relationship("Issue", back_populates="comments")
    author: Mapped["User"] = relationship("User", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, author_id={self.author_id})>"
