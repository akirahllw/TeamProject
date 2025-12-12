from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.base import get_db, Base
from app.models.issue import Comment
from app.models.user import User

router = APIRouter()


# Pydantic schemas
class CommentBase(BaseModel):
    body: str
    issue_id: int


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    body: str


class CommentResponse(CommentBase):
    id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Routes
@router.get("/", response_model=List[CommentResponse])
async def get_comments(
    issue_id: Optional[int] = None,
    author_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all comments with optional filtering"""
    query = db.query(Comment)

    if issue_id is not None:
        query = query.filter(Comment.issue_id == issue_id)

    if author_id is not None:
        query = query.filter(Comment.author_id == author_id)

    comments = query.order_by(Comment.created_at.asc()).offset(skip).limit(limit).all()
    return comments


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """Get a specific comment by ID"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment


@router.post("/", response_model=CommentResponse, status_code=201)
async def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)  # Uncomment when auth is ready
):
    """Create a new comment on an issue"""
    # TODO: Check if issue exists
    # from app.models.issue import Issue
    # issue = db.query(Issue).filter(Issue.id == comment.issue_id).first()
    # if not issue:
    #     raise HTTPException(status_code=404, detail="Issue not found")

    # For now, use a placeholder author_id (replace with current_user.id)
    db_comment = Comment(
        body=comment.body,
        issue_id=comment.issue_id,
        author_id=1  # Replace with current_user.id
    )

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    return db_comment


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)  # Uncomment when auth is ready
):
    """Update an existing comment"""
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # TODO: Check if user is the author or superuser
    # if db_comment.author_id != current_user.id and not current_user.is_superuser:
    #     raise HTTPException(status_code=403, detail="Not authorized")

    db_comment.body = comment.body
    db.commit()
    db.refresh(db_comment)

    return db_comment


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)  # Uncomment when auth is ready
):
    """Delete a comment"""
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # TODO: Check if user is the author or superuser
    # if db_comment.author_id != current_user.id and not current_user.is_superuser:
    #     raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(db_comment)
    db.commit()

    return None
