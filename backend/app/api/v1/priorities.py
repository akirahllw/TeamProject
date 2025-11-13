from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


# Pydantic schemas (placeholder - will be replaced with actual models later)
class PriorityBase(BaseModel):
    name: str
    description: str | None = None
    color: str | None = None  # Hex color code
    level: int  # Numeric level for sorting (1-5)


class PriorityCreate(PriorityBase):
    pass


class PriorityUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    level: int | None = None


class PriorityResponse(PriorityBase):
    id: int
    is_default: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=list[PriorityResponse])
async def get_priorities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all priorities
    """
    # TODO: Implement database query when models are added
    return []


@router.get("/{priority_id}", response_model=PriorityResponse)
async def get_priority(priority_id: int):
    """
    Get a specific priority by ID
    """
    # TODO: Implement database query when models are added
    raise HTTPException(status_code=404, detail="Priority not found")


@router.post("/", response_model=PriorityResponse, status_code=201)
async def create_priority(priority: PriorityCreate):
    """
    Create a new priority
    """
    # TODO: Implement database insert when models are added
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{priority_id}", response_model=PriorityResponse)
async def update_priority(priority_id: int, priority: PriorityUpdate):
    """
    Update an existing priority
    """
    # TODO: Implement database update when models are added
    raise HTTPException(status_code=404, detail="Priority not found")


@router.delete("/{priority_id}", status_code=204)
async def delete_priority(priority_id: int):
    """
    Delete a priority
    """
    # TODO: Implement database delete when models are added
    raise HTTPException(status_code=404, detail="Priority not found")


@router.get("/{priority_id}/issues", response_model=list[dict])
async def get_priority_issues(
    priority_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all issues with a specific priority
    """
    # TODO: Implement database query when models are added
    return []
