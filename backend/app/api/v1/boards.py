from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.board import Board, BoardColumn, BoardType
from app.models.issue import Issue
from app.models.project import Project

router = APIRouter()


# Pydantic schemas
class BoardBase(BaseModel):
    name: str
    project_id: int
    board_type: BoardType
    description: str | None = None


class BoardCreate(BoardBase):
    pass


class BoardUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    board_type: BoardType | None = None


class BoardResponse(BoardBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ColumnCreate(BaseModel):
    name: str
    description: str | None = None
    position: int = 0


class ColumnResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    position: int
    board_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=list[BoardResponse])
async def get_boards(
    project_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get all boards with optional filtering
    """
    query = db.query(Board)

    if project_id is not None:
        query = query.filter(Board.project_id == project_id)

    boards = query.offset(skip).limit(limit).all()
    return boards


@router.get("/{board_id}", response_model=BoardResponse)
async def get_board(board_id: int, db: Session = Depends(get_db)):
    """
    Get a specific board by ID
    """
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.post("/", response_model=BoardResponse, status_code=201)
async def create_board(board: BoardCreate, db: Session = Depends(get_db)):
    """
    Create a new board
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == board.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create new board
    db_board = Board(
        name=board.name,
        project_id=board.project_id,
        board_type=board.board_type,
        description=board.description,
    )
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board


@router.put("/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: int, board: BoardUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing board
    """
    db_board = db.query(Board).filter(Board.id == board_id).first()
    if not db_board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Update fields if provided
    if board.name is not None:
        db_board.name = board.name
    if board.description is not None:
        db_board.description = board.description
    if board.board_type is not None:
        db_board.board_type = board.board_type

    db.commit()
    db.refresh(db_board)
    return db_board


@router.delete("/{board_id}", status_code=204)
async def delete_board(board_id: int, db: Session = Depends(get_db)):
    """
    Delete a board
    """
    db_board = db.query(Board).filter(Board.id == board_id).first()
    if not db_board:
        raise HTTPException(status_code=404, detail="Board not found")

    db.delete(db_board)
    db.commit()
    return None


@router.get("/{board_id}/columns", response_model=list[ColumnResponse])
async def get_board_columns(board_id: int, db: Session = Depends(get_db)):
    """
    Get all columns for a board (e.g., To Do, In Progress, Done)
    """
    # Verify board exists
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    columns = (
        db.query(BoardColumn)
        .filter(BoardColumn.board_id == board_id)
        .order_by(BoardColumn.position)
        .all()
    )
    return columns


@router.post("/{board_id}/columns", response_model=ColumnResponse, status_code=201)
async def create_board_column(
    board_id: int, column: ColumnCreate, db: Session = Depends(get_db)
):
    """
    Create a new column for a board
    """
    # Verify board exists
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Get the maximum position to append at the end if position not specified
    if column.position == 0:
        max_position = (
            db.query(BoardColumn)
            .filter(BoardColumn.board_id == board_id)
            .order_by(BoardColumn.position.desc())
            .first()
        )
        position = (max_position.position + 1) if max_position else 0
    else:
        position = column.position

    # Create new column
    db_column = BoardColumn(
        name=column.name,
        description=column.description,
        position=position,
        board_id=board_id,
    )
    db.add(db_column)
    db.commit()
    db.refresh(db_column)
    return db_column


@router.get("/{board_id}/issues", response_model=list[dict])
async def get_board_issues(
    board_id: int,
    column_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get all issues on a board, optionally filtered by column.
    Note: Issues are filtered by the board's project. If column_id is provided,
    issues are further filtered by matching column name to issue status.
    """
    # Verify board exists
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Get all issues for the board's project
    query = db.query(Issue).filter(Issue.project_id == board.project_id)

    # If column_id is provided, filter by column name matching issue status
    if column_id is not None:
        column = (
            db.query(BoardColumn)
            .filter(BoardColumn.id == column_id, BoardColumn.board_id == board_id)
            .first()
        )
        if not column:
            raise HTTPException(status_code=404, detail="Column not found")

        # Map column name to issue status (simple mapping - can be enhanced)
        # This is a basic implementation - you may want to add a proper mapping table
        column_name_upper = column.name.upper().replace(" ", "_")
        from app.models.issue import IssueStatus

        try:
            issue_status = IssueStatus[column_name_upper]
            query = query.filter(Issue.status == issue_status)
        except KeyError:
            # If column name doesn't match any status, return empty list
            # In a real implementation, you might want a mapping table
            return []

    issues = query.offset(skip).limit(limit).all()

    return [
        {
            "id": issue.id,
            "title": issue.title,
            "description": issue.description,
            "status": issue.status.value,
            "priority": issue.priority.value,
            "issue_type": issue.issue_type.value,
            "project_id": issue.project_id,
            "reporter_id": issue.reporter_id,
            "assignee_id": issue.assignee_id,
            "sprint_id": issue.sprint_id,
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
            "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
        }
        for issue in issues
    ]
