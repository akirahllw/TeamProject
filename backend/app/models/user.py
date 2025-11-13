from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base  # Import Base from new location

# This block is only processed by type-checkers, not at runtime
# This avoids circular import errors while keeping linters happy
if TYPE_CHECKING:
    from .issue import Comment, Issue
    from .project import Project, ProjectMember


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # --- Relationships ---

    owned_projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="owner"
    )

    project_associations: Mapped[list["ProjectMember"]] = relationship(
        "ProjectMember", back_populates="user", cascade="all, delete-orphan"
    )

    reported_issues: Mapped[list["Issue"]] = relationship(
        "Issue", back_populates="reporter", foreign_keys="Issue.reporter_id"
    )

    assigned_issues: Mapped[list["Issue"]] = relationship(
        "Issue", back_populates="assignee", foreign_keys="Issue.assignee_id"
    )

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="author")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
