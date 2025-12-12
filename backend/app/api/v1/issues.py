from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel, computed_field
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.base import get_db, Base
from app.models.issue import Issue, Comment, IssueType, IssuePriority, IssueStatus

router = APIRouter()


# Pydantic schemas
class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    issue_type: IssueType
    priority: IssuePriority
    status: IssueStatus
    project_id: int
    assignee_id: Optional[int] = None
    reporter_id: int
    parent_issue_id: Optional[int] = None


class IssueCreate(IssueBase):
    pass


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[IssueType] = None
    priority: Optional[IssuePriority] = None
    status: Optional[IssueStatus] = None
    assignee_id: Optional[int] = None
    parent_issue_id: Optional[int] = None


class IssueResponse(IssueBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @computed_field
    @property
    def key(self) -> str:
        """Computed field: project key + issue id (e.g., 'PROJ-123')"""
        return f"PROJ-{self.id}"


class CommentResponse(BaseModel):
    id: int
    body: str
    author_id: int
    issue_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AttachmentResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    content_type: str
    uploader_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Routes
@router.get("/", response_model=List[IssueResponse])
async def get_issues(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    project_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    reporter_id: Optional[int] = None,
    status: Optional[IssueStatus] = None,
    issue_type: Optional[IssueType] = None,
    priority: Optional[IssuePriority] = None,
    parent_issue_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all issues with filtering and pagination"""
    query = db.query(Issue)

    # Apply filters
    if project_id is not None:
        query = query.filter(Issue.project_id == project_id)

    if assignee_id is not None:
        query = query.filter(Issue.assignee_id == assignee_id)

    if reporter_id is not None:
        query = query.filter(Issue.reporter_id == reporter_id)

    if status is not None:
        query = query.filter(Issue.status == status)

    if issue_type is not None:
        query = query.filter(Issue.issue_type == issue_type)

    if priority is not None:
        query = query.filter(Issue.priority == priority)

    if parent_issue_id is not None:
        query = query.filter(Issue.parent_issue_id == parent_issue_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Issue.title.ilike(search_term)) |
            (Issue.description.ilike(search_term))
        )

    # Order by most recent first
    query = query.order_by(Issue.created_at.desc())

    issues = query.offset(skip).limit(limit).all()
    return issues


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(issue_id: int, db: Session = Depends(get_db)):
    """Get a specific issue by ID"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    return issue


@router.get("/key/{issue_key}", response_model=IssueResponse)
async def get_issue_by_key(issue_key: str, db: Session = Depends(get_db)):
    """Get a specific issue by key (e.g., "PROJ-123")"""
    # Parse the key to extract issue ID
    try:
        parts = issue_key.split("-")
        if len(parts) != 2:
            raise ValueError("Invalid key format")

        issue_id = int(parts[1])
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=400,
            detail="Invalid issue key format. Expected format: PROJ-123"
        )

    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # TODO: Verify project key matches when needed

    return issue


@router.post("/", response_model=IssueResponse, status_code=201)
async def create_issue(
    issue: IssueCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)  # Uncomment when auth is ready
):
    """Create a new issue"""
    # TODO: Verify project exists
    # from app.models.project import Project
    # project = db.query(Project).filter(Project.id == issue.project_id).first()
    # if not project:
    #     raise HTTPException(status_code=404, detail="Project not found")

    # TODO: Verify assignee exists if provided
    # if issue.assignee_id:
    #     from app.models.user import User
    #     assignee = db.query(User).filter(User.id == issue.assignee_id).first()
    #     if not assignee:
    #         raise HTTPException(status_code=404, detail="Assignee not found")

    # TODO: Verify reporter exists
    # from app.models.user import User
    # reporter = db.query(User).filter(User.id == issue.reporter_id).first()
    # if not reporter:
    #     raise HTTPException(status_code=404, detail="Reporter not found")

    # Verify parent issue exists if provided
    if issue.parent_issue_id:
        parent = db.query(Issue).filter(Issue.id == issue.parent_issue_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent issue not found")

        # Verify parent is in the same project
        if parent.project_id != issue.project_id:
            raise HTTPException(
                status_code=400,
                detail="Parent issue must be in the same project"
            )

    # Create issue
    db_issue = Issue(**issue.dict())
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)

    return db_issue


@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: int,
    issue: IssueUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)  # Uncomment when auth is ready
):
    """Update an existing issue"""
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    update_data = issue.dict(exclude_unset=True)

    # Verify assignee exists if provided
    if "assignee_id" in update_data and update_data["assignee_id"]:
        # TODO: Check if user exists
        # from app.models.user import User
        # assignee = db.query(User).filter(User.id == update_data["assignee_id"]).first()
        # if not assignee:
        #     raise HTTPException(status_code=404, detail="Assignee not found")
        pass

    # Verify parent issue if provided
    if "parent_issue_id" in update_data and update_data["parent_issue_id"]:
        parent = db.query(Issue).filter(
            Issue.id == update_data["parent_issue_id"]
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent issue not found")

        # Prevent circular dependencies
        if parent.id == issue_id:
            raise HTTPException(
                status_code=400,
                detail="Issue cannot be its own parent"
            )

        # Verify parent is in the same project
        if parent.project_id != db_issue.project_id:
            raise HTTPException(
                status_code=400,
                detail="Parent issue must be in the same project"
            )

    # Apply updates
    for field, value in update_data.items():
        setattr(db_issue, field, value)

    db.commit()
    db.refresh(db_issue)

    return db_issue


@router.patch("/{issue_id}/assign", response_model=IssueResponse)
async def assign_issue(
    issue_id: int,
    assignee_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)  # Uncomment when auth is ready
):
    """Assign an issue to a user"""
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # TODO: Verify assignee exists
    # from app.models.user import User
    # assignee = db.query(User).filter(User.id == assignee_id).first()
    # if not assignee:
    #     raise HTTPException(status_code=404, detail="User not found")

    db_issue.assignee_id = assignee_id
    db.commit()
    db.refresh(db_issue)

    return db_issue


@router.patch("/{issue_id}/status", response_model=IssueResponse)
async def update_issue_status(
    issue_id: int,
    status: IssueStatus,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)  # Uncomment when auth is ready
):
    """Update the status of an issue"""
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    db_issue.status = status
    db.commit()
    db.refresh(db_issue)

    return db_issue


@router.patch("/{issue_id}/priority", response_model=IssueResponse)
async def update_issue_priority(
    issue_id: int,
    priority: IssuePriority,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)  # Uncomment when auth is ready
):
    """Update the priority of an issue"""
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    db_issue.priority = priority
    db.commit()
    db.refresh(db_issue)

    return db_issue


@router.delete("/{issue_id}", status_code=204)
async def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)  # Uncomment when auth is ready
):
    """Delete an issue"""
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # TODO: Check permissions - only reporter, assignee, or admin can delete

    # Check if this issue has child issues (sub_tasks)
    if db_issue.sub_tasks:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete issue with {len(db_issue.sub_tasks)} child issues. Delete child issues first."
        )

    # The cascade="all, delete-orphan" on comments relationship will handle deletion
    db.delete(db_issue)
    db.commit()

    return None


@router.get("/{issue_id}/comments", response_model=List[CommentResponse])
async def get_issue_comments(issue_id: int, db: Session = Depends(get_db)):
    """Get all comments for an issue"""
    # Verify issue exists
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Get comments through the relationship
    return issue.comments


@router.get("/{issue_id}/attachments", response_model=List[AttachmentResponse])
async def get_issue_attachments(issue_id: int, db: Session = Depends(get_db)):
    """Get all attachments for an issue"""
    # Verify issue exists
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Get attachments - this will work once Attachment model is properly set up
    try:
        from app.models.attachment import Attachment
        attachments = db.query(Attachment).filter(
            Attachment.issue_id == issue_id
        ).order_by(Attachment.created_at.desc()).all()
        return attachments
    except ImportError:
        return []


@router.get("/{issue_id}/history", response_model=List[dict])
async def get_issue_history(
    issue_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get change history for an issue"""
    # Verify issue exists
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # TODO: Implement history tracking when IssueHistory model is available
    # For now, return empty list
    return []


@router.get("/{issue_id}/subtasks", response_model=List[IssueResponse])
async def get_issue_subtasks(
    issue_id: int,
    db: Session = Depends(get_db)
):
    """Get all subtasks (child issues) for an issue"""
    # Verify parent issue exists
    parent = db.query(Issue).filter(Issue.id == issue_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Return sub_tasks through the relationship
    return parent.sub_tasks
