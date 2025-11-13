from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class IssueType(str, Enum):
    TASK = "task"
    BUG = "bug"
    STORY = "story"
    EPIC = "epic"
    SUBTASK = "subtask"


class IssuePriority(str, Enum):
    LOWEST = "lowest"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    HIGHEST = "highest"


router = APIRouter()


# Pydantic schemas (placeholder - will be replaced with actual models later)
class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    issue_type: IssueType
    priority: IssuePriority
    project_id: int
    assignee_id: Optional[int] = None
    reporter_id: int
    status_id: Optional[int] = None
    sprint_id: Optional[int] = None
    story_points: Optional[int] = None
    due_date: Optional[datetime] = None


class IssueCreate(IssueBase):
    pass


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[IssueType] = None
    priority: Optional[IssuePriority] = None
    assignee_id: Optional[int] = None
    status_id: Optional[int] = None
    sprint_id: Optional[int] = None
    story_points: Optional[int] = None
    due_date: Optional[datetime] = None


class IssueResponse(IssueBase):
    id: int
    key: str  # e.g., "PROJ-123"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[IssueResponse])
async def get_issues(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    project_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    reporter_id: Optional[int] = None,
    status_id: Optional[int] = None,
    sprint_id: Optional[int] = None,
    issue_type: Optional[IssueType] = None,
    priority: Optional[IssuePriority] = None,
    search: Optional[str] = None,
):
    """
    Get all issues with filtering and pagination
    """
    # TODO: Implement database query with filters when models are added
    return []


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(issue_id: int):
    """
    Get a specific issue by ID
    """
    # TODO: Implement database query when models are added
    raise HTTPException(status_code=404, detail="Issue not found")


@router.get("/key/{issue_key}", response_model=IssueResponse)
async def get_issue_by_key(issue_key: str):
    """
    Get a specific issue by key (e.g., "PROJ-123")
    """
    # TODO: Implement database query when models are added
    raise HTTPException(status_code=404, detail="Issue not found")


@router.post("/", response_model=IssueResponse, status_code=201)
async def create_issue(issue: IssueCreate):
    """
    Create a new issue
    """
    # TODO: Implement database insert when models are added
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(issue_id: int, issue: IssueUpdate):
    """
    Update an existing issue
    """
    # TODO: Implement database update when models are added
    raise HTTPException(status_code=404, detail="Issue not found")


@router.patch("/{issue_id}/assign", response_model=IssueResponse)
async def assign_issue(issue_id: int, assignee_id: int):
    """
    Assign an issue to a user
    """
    # TODO: Implement assignment logic when models are added
    raise HTTPException(status_code=404, detail="Issue not found")


@router.patch("/{issue_id}/status", response_model=IssueResponse)
async def update_issue_status(issue_id: int, status_id: int):
    """
    Update the status of an issue
    """
    # TODO: Implement status update logic when models are added
    raise HTTPException(status_code=404, detail="Issue not found")


@router.patch("/{issue_id}/priority", response_model=IssueResponse)
async def update_issue_priority(issue_id: int, priority: IssuePriority):
    """
    Update the priority of an issue
    """
    # TODO: Implement priority update logic when models are added
    raise HTTPException(status_code=404, detail="Issue not found")


@router.delete("/{issue_id}", status_code=204)
async def delete_issue(issue_id: int):
    """
    Delete an issue
    """
    # TODO: Implement database delete when models are added
    raise HTTPException(status_code=404, detail="Issue not found")


@router.get("/{issue_id}/comments", response_model=List[dict])
async def get_issue_comments(issue_id: int):
    """
    Get all comments for an issue
    """
    # TODO: Implement database query when models are added
    return []


@router.get("/{issue_id}/attachments", response_model=List[dict])
async def get_issue_attachments(issue_id: int):
    """
    Get all attachments for an issue
    """
    # TODO: Implement database query when models are added
    return []


@router.get("/{issue_id}/history", response_model=List[dict])
async def get_issue_history(issue_id: int):
    """
    Get change history for an issue
    """
    # TODO: Implement database query when models are added
    return []
