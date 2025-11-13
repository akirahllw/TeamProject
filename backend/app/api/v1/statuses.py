from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


# Pydantic schemas (placeholder - will be replaced with actual models later)
class StatusBase(BaseModel):
    name: str
    description: str | None = None
    color: str | None = None  # Hex color code
    category: str  # e.g., "todo", "in_progress", "done"


class StatusCreate(StatusBase):
    pass


class StatusUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    category: str | None = None


class StatusResponse(StatusBase):
    id: int
    is_default: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=list[StatusResponse])
async def get_statuses(
    category: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all statuses with optional filtering
    """
    # TODO: Implement database query when models are added
    return []


@router.get("/{status_id}", response_model=StatusResponse)
async def get_status(status_id: int):
    """
    Get a specific status by ID
    """
    # TODO: Implement database query when models are added
    raise HTTPException(status_code=404, detail="Status not found")


@router.post("/", response_model=StatusResponse, status_code=201)
async def create_status(status: StatusCreate):
    """
    Create a new status
    """
    # TODO: Implement database insert when models are added
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{status_id}", response_model=StatusResponse)
async def update_status(status_id: int, status: StatusUpdate):
    """
    Update an existing status
    """
    # TODO: Implement database update when models are added
    raise HTTPException(status_code=404, detail="Status not found")


@router.delete("/{status_id}", status_code=204)
async def delete_status(status_id: int):
    """
    Delete a status
    """
    # TODO: Implement database delete when models are added
    raise HTTPException(status_code=404, detail="Status not found")


@router.get("/{status_id}/issues", response_model=list[dict])
async def get_status_issues(
    status_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all issues with a specific status
    """
    # TODO: Implement database query when models are added
    return []
