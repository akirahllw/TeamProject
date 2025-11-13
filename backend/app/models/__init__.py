# This file makes the 'models' directory a Python package
# and conveniently exports all the models.

from app.db.base import Base

from .issue import Comment, Issue, IssuePriority, IssueStatus, IssueType
from .project import Project, ProjectMember, ProjectRole
from .user import User

# You can add all models to __all__ for cleaner wildcard imports
__all__ = [
    "Base",
    "User",
    "Project",
    "ProjectMember",
    "ProjectRole",
    "Issue",
    "Comment",
    "IssueType",
    "IssueStatus",
    "IssuePriority",
]
