from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from app.db.base import Base
from app.db.base import get_db, Base

router = APIRouter()


# Database Models (you'll need to create these in app/models/ directory)
class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    board_type = Column(String(50), nullable=False)  # "scrum" or "kanban"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BoardColumn(Base):
    __tablename__ = "board_columns"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    position = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Pydantic schemas
class BoardBase(BaseModel):
    name: str
    project_id: int
    board_type: str
    description: Optional[str] = None


class BoardCreate(BoardBase):
    pass


class BoardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    board_type: Optional[str] = None


class BoardResponse(BoardBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ColumnBase(BaseModel):
    name: str
    position: int


class ColumnCreate(ColumnBase):
    pass


class ColumnResponse(ColumnBase):
    id: int
    board_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Routes
@router.get("/", response_model=List[BoardResponse])
async def get_boards(
    project_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all boards with optional filtering"""
    query = db.query(Board)

    if project_id is not None:
        query = query.filter(Board.project_id == project_id)

    boards = query.offset(skip).limit(limit).all()
    return boards


@router.get("/{board_id}", response_model=BoardResponse)
async def get_board(board_id: int, db: Session = Depends(get_db)):
    """Get a specific board by ID"""
    board = db.query(Board).filter(Board.id == board_id).first()

    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    return board


@router.post("/", response_model=BoardResponse, status_code=201)
async def create_board(
    board: BoardCreate,
    db: Session = Depends(get_db)
):
    """Create a new board"""
    if board.board_type not in ["scrum", "kanban"]:
        raise HTTPException(
            status_code=400,
            detail="board_type must be 'scrum' or 'kanban'"
        )

    # TODO: Check if project exists
    # from app.models.project import Project
    # project = db.query(Project).filter(Project.id == board.project_id).first()
    # if not project:
    #     raise HTTPException(status_code=404, detail="Project not found")

    db_board = Board(**board.dict())
    db.add(db_board)
    db.commit()
    db.refresh(db_board)

    # Create default columns
    default_columns = [
        {"name": "To Do", "position": 1},
        {"name": "In Progress", "position": 2},
        {"name": "Done", "position": 3}
    ]

    for col in default_columns:
        db_column = BoardColumn(board_id=db_board.id, **col)
        db.add(db_column)

    db.commit()

    return db_board


@router.put("/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: int,
    board: BoardUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing board"""
    db_board = db.query(Board).filter(Board.id == board_id).first()

    if not db_board:
        raise HTTPException(status_code=404, detail="Board not found")

    update_data = board.dict(exclude_unset=True)

    if "board_type" in update_data and update_data["board_type"] not in ["scrum", "kanban"]:
        raise HTTPException(
            status_code=400,
            detail="board_type must be 'scrum' or 'kanban'"
        )

    for field, value in update_data.items():
        setattr(db_board, field, value)

    db.commit()
    db.refresh(db_board)

    return db_board


@router.delete("/{board_id}", status_code=204)
async def delete_board(board_id: int, db: Session = Depends(get_db)):
    """Delete a board"""
    db_board = db.query(Board).filter(Board.id == board_id).first()

    if not db_board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Delete associated columns
    db.query(BoardColumn).filter(BoardColumn.board_id == board_id).delete()

    db.delete(db_board)
    db.commit()

    return None


@router.get("/{board_id}/columns", response_model=List[ColumnResponse])
async def get_board_columns(board_id: int, db: Session = Depends(get_db)):
    """Get all columns for a board"""
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    columns = db.query(BoardColumn).filter(
        BoardColumn.board_id == board_id
    ).order_by(BoardColumn.position).all()

    return columns


@router.post("/{board_id}/columns", response_model=ColumnResponse, status_code=201)
async def create_board_column(
    board_id: int,
    column: ColumnCreate,
    db: Session = Depends(get_db)
):
    """Create a new column for a board"""
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    db_column = BoardColumn(board_id=board_id, **column.dict())
    db.add(db_column)
    db.commit()
    db.refresh(db_column)

    return db_column


@router.get("/{board_id}/issues", response_model=List[dict])
async def get_board_issues(
    board_id: int,
    column_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all issues on a board, optionally filtered by column"""
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # TODO: Implement issue querying when Issue-Board relationship is available
    return []

