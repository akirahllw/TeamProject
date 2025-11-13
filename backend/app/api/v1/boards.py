from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


# Pydantic schemas (placeholder - will be replaced with actual models later)
class BoardBase(BaseModel):
    name: str
    project_id: int
    board_type: str  # e.g., "scrum", "kanban"
    description: str | None = None


class BoardCreate(BoardBase):
    pass


class BoardUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    board_type: str | None = None


class BoardResponse(BoardBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=list[BoardResponse])
async def get_boards(
    project_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all boards with optional filtering
    """
    # TODO: Implement database query when models are added
    return []


@router.get("/{board_id}", response_model=BoardResponse)
async def get_board(board_id: int):
    """
    Get a specific board by ID
    """
    # TODO: Implement database query when models are added
    raise HTTPException(status_code=404, detail="Board not found")


@router.post("/", response_model=BoardResponse, status_code=201)
async def create_board(board: BoardCreate):
    """
    Create a new board
    """
    # TODO: Implement database insert when models are added
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{board_id}", response_model=BoardResponse)
async def update_board(board_id: int, board: BoardUpdate):
    """
    Update an existing board
    """
    # TODO: Implement database update when models are added
    raise HTTPException(status_code=404, detail="Board not found")


@router.delete("/{board_id}", status_code=204)
async def delete_board(board_id: int):
    """
    Delete a board
    """
    # TODO: Implement database delete when models are added
    raise HTTPException(status_code=404, detail="Board not found")


@router.get("/{board_id}/columns", response_model=list[dict])
async def get_board_columns(board_id: int):
    """
    Get all columns for a board (e.g., To Do, In Progress, Done)
    """
    # TODO: Implement database query when models are added
    return []


@router.post("/{board_id}/columns", status_code=201)
async def create_board_column(board_id: int, column_data: dict):
    """
    Create a new column for a board
    """
    # TODO: Implement column creation when models are added
    raise HTTPException(status_code=404, detail="Board not found")


@router.get("/{board_id}/issues", response_model=list[dict])
async def get_board_issues(
    board_id: int,
    column_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all issues on a board, optionally filtered by column
    """
    # TODO: Implement database query when models are added
    return []
