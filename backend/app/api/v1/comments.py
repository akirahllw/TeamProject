from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# Pydantic schemas (placeholder - will be replaced with actual models later)
class CommentBase(BaseModel):
    content: str
    issue_id: int


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: str


class CommentResponse(CommentBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CommentResponse])
async def get_comments(
    issue_id: Optional[int] = None,
    author_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all comments with optional filtering
    """
    # TODO: Implement database query when models are added
    return []


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int):
    """
    Get a specific comment by ID
    """
    # TODO: Implement database query when models are added
    raise HTTPException(status_code=404, detail="Comment not found")


@router.post("/", response_model=CommentResponse, status_code=201)
async def create_comment(comment: CommentCreate):
    """
    Create a new comment on an issue
    """
    # TODO: Implement database insert when models are added
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, comment: CommentUpdate):
    """
    Update an existing comment
    """
    # TODO: Implement database update when models are added
    raise HTTPException(status_code=404, detail="Comment not found")


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(comment_id: int):
    """
    Delete a comment
    """
    # TODO: Implement database delete when models are added
    raise HTTPException(status_code=404, detail="Comment not found")
