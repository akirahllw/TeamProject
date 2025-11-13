import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base  # Import Base from new location

# This block is only processed by type-checkers, not at runtime
if TYPE_CHECKING:
    from .issue import Issue
    from .user import User


# Enum for Project-level roles
class ProjectRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


class ProjectMember(Base):
    __tablename__ = "project_members"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole), default=ProjectRole.MEMBER
    )

    user: Mapped["User"] = relationship(back_populates="project_associations")
    project: Mapped["Project"] = relationship(back_populates="member_associations")

    def __repr__(self):
        return f"<ProjectMember(user_id={self.user_id}, project_id={self.project_id}, role={self.role})>"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(
        String(10), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # --- Relationships ---

    owner: Mapped["User"] = relationship("User", back_populates="owned_projects")

    issues: Mapped[list["Issue"]] = relationship(
        "Issue", back_populates="project", cascade="all, delete-orphan"
    )

    member_associations: Mapped[list["ProjectMember"]] = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', key='{self.key}')>"
