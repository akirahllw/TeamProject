from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from .issue import Issue
    from .user import User


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign keys
    issue_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True
    )
    uploader_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # File information
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # Size in bytes
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # --- Relationships ---

    issue: Mapped["Issue"] = relationship("Issue", back_populates="attachments")
    uploader: Mapped["User"] = relationship("User", back_populates="attachments")

    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.filename}', issue_id={self.issue_id})>"

    @property
    def file_size_mb(self) -> float:
        """Return file size in megabytes"""
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def file_extension(self) -> str:
        """Return file extension"""
        return self.filename.split(".")[-1].lower() if "." in self.filename else ""
