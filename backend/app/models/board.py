import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from .project import Project


class BoardType(str, enum.Enum):
    SCRUM = "scrum"
    KANBAN = "kanban"


class Board(Base):
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    board_type: Mapped[BoardType] = mapped_column(
        Enum(BoardType), default=BoardType.KANBAN, nullable=False
    )
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Project"] = relationship("Project", back_populates="boards")
    columns: Mapped[list["BoardColumn"]] = relationship(
        "BoardColumn", back_populates="board", cascade="all, delete-orphan", order_by="BoardColumn.position"
    )

    def __repr__(self):
        return f"<Board(id={self.id}, name='{self.name}', board_type='{self.board_type}')>"


class BoardColumn(Base):
    __tablename__ = "board_columns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    board: Mapped["Board"] = relationship("Board", back_populates="columns")

    def __repr__(self):
        return f"<BoardColumn(id={self.id}, name='{self.name}', board_id={self.board_id}, position={self.position})>"

