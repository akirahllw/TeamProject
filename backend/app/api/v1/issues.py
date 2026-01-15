from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.issue import Issue, IssuePriority, IssueStatus, IssueType
from app.models.project import Project
from app.models.user import User

router = APIRouter()


# Pydantic schemas
class IssueBase(BaseModel):
    title: str
    description: str | None = None
    issue_type: IssueType
    priority: IssuePriority
    project_id: int
    assignee_id: int | None = None
    reporter_id: int
    sprint_id: int | None = None
    parent_issue_id: int | None = None


class IssueCreate(IssueBase):
    pass


class IssueUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    issue_type: IssueType | None = None
    priority: IssuePriority | None = None
    assignee_id: int | None = None
    sprint_id: int | None = None
    parent_issue_id: int | None = None


class IssueResponse(BaseModel):
    id: int
    key: str  # e.g., "PROJ-123"
    title: str
    description: str | None = None
    issue_type: IssueType
    priority: IssuePriority
    status: IssueStatus
    project_id: int
    assignee_id: int | None = None
    reporter_id: int
    sprint_id: int | None = None
    parent_issue_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


def _generate_issue_key(project_key: str, issue_id: int) -> str:
    """Generate issue key in format PROJ-123"""
    return f"{project_key}-{issue_id}"


def _issue_to_response(issue: Issue) -> IssueResponse:
    """Convert Issue model to IssueResponse with generated key"""
    return IssueResponse(
        id=issue.id,
        key=_generate_issue_key(issue.project.key, issue.id),
        title=issue.title,
        description=issue.description,
        issue_type=issue.issue_type,
        priority=issue.priority,
        status=issue.status,
        project_id=issue.project_id,
        assignee_id=issue.assignee_id,
        reporter_id=issue.reporter_id,
        sprint_id=issue.sprint_id,
        parent_issue_id=issue.parent_issue_id,
        created_at=issue.created_at,
        updated_at=issue.updated_at,
    )


@router.get("/", response_model=list[IssueResponse])
async def get_issues(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    project_id: int | None = None,
    assignee_id: int | None = None,
    reporter_id: int | None = None,
    sprint_id: int | None = None,
    issue_type: IssueType | None = None,
    priority: IssuePriority | None = None,
    status: IssueStatus | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Get all issues with filtering and pagination
    """
    query = db.query(Issue)

    if project_id is not None:
        query = query.filter(Issue.project_id == project_id)
    if assignee_id is not None:
        query = query.filter(Issue.assignee_id == assignee_id)
    if reporter_id is not None:
        query = query.filter(Issue.reporter_id == reporter_id)
    if sprint_id is not None:
        query = query.filter(Issue.sprint_id == sprint_id)
    if issue_type is not None:
        query = query.filter(Issue.issue_type == issue_type)
    if priority is not None:
        query = query.filter(Issue.priority == priority)
    if status is not None:
        query = query.filter(Issue.status == status)
    if search is not None:
        search_filter = or_(
            Issue.title.ilike(f"%{search}%"),
            Issue.description.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    issues = query.order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()
    return [_issue_to_response(issue) for issue in issues]


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(issue_id: int, db: Session = Depends(get_db)):
    """
    Get a specific issue by ID
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return _issue_to_response(issue)


@router.get("/key/{issue_key}", response_model=IssueResponse)
async def get_issue_by_key(issue_key: str, db: Session = Depends(get_db)):
    """
    Get a specific issue by key (e.g., "PROJ-123")
    """
    # Parse issue key (format: PROJ-123)
    try:
        project_key, issue_id_str = issue_key.rsplit("-", 1)
        issue_id = int(issue_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid issue key format")

    # Find project by key
    project = db.query(Project).filter(Project.key == project_key).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Find issue
    issue = (
        db.query(Issue)
        .filter(Issue.id == issue_id, Issue.project_id == project.id)
        .first()
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    return _issue_to_response(issue)


@router.post("/", response_model=IssueResponse, status_code=201)
async def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    """
    Create a new issue
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == issue.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify reporter exists
    reporter = db.query(User).filter(User.id == issue.reporter_id).first()
    if not reporter:
        raise HTTPException(status_code=404, detail="Reporter not found")

    # Verify assignee if provided
    if issue.assignee_id is not None:
        assignee = db.query(User).filter(User.id == issue.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")

    # Verify parent issue if provided
    if issue.parent_issue_id is not None:
        parent_issue = (
            db.query(Issue).filter(Issue.id == issue.parent_issue_id).first()
        )
        if not parent_issue:
            raise HTTPException(status_code=404, detail="Parent issue not found")
        if parent_issue.project_id != issue.project_id:
            raise HTTPException(
                status_code=400, detail="Parent issue must be in the same project"
            )

    # Create new issue
    db_issue = Issue(
        title=issue.title,
        description=issue.description,
        issue_type=issue.issue_type,
        priority=issue.priority,
        project_id=issue.project_id,
        reporter_id=issue.reporter_id,
        assignee_id=issue.assignee_id,
        sprint_id=issue.sprint_id,
        parent_issue_id=issue.parent_issue_id,
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return _issue_to_response(db_issue)


@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: int, issue: IssueUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing issue
    """
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Update fields if provided
    if issue.title is not None:
        db_issue.title = issue.title
    if issue.description is not None:
        db_issue.description = issue.description
    if issue.issue_type is not None:
        db_issue.issue_type = issue.issue_type
    if issue.priority is not None:
        db_issue.priority = issue.priority
    if issue.assignee_id is not None:
        # Verify assignee exists
        assignee = db.query(User).filter(User.id == issue.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")
        db_issue.assignee_id = issue.assignee_id
    if issue.sprint_id is not None:
        db_issue.sprint_id = issue.sprint_id
    if issue.parent_issue_id is not None:
        if issue.parent_issue_id == issue_id:
            raise HTTPException(
                status_code=400, detail="Issue cannot be its own parent"
            )
        parent_issue = (
            db.query(Issue).filter(Issue.id == issue.parent_issue_id).first()
        )
        if not parent_issue:
            raise HTTPException(status_code=404, detail="Parent issue not found")
        if parent_issue.project_id != db_issue.project_id:
            raise HTTPException(
                status_code=400, detail="Parent issue must be in the same project"
            )
        db_issue.parent_issue_id = issue.parent_issue_id

    db.commit()
    db.refresh(db_issue)
    return _issue_to_response(db_issue)


class AssignIssueRequest(BaseModel):
    assignee_id: int


@router.patch("/{issue_id}/assign", response_model=IssueResponse)
async def assign_issue(
    issue_id: int, request: AssignIssueRequest, db: Session = Depends(get_db)
):
    """
    Assign an issue to a user
    """
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Verify assignee exists
    assignee = db.query(User).filter(User.id == request.assignee_id).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assignee not found")

    db_issue.assignee_id = request.assignee_id
    db.commit()
    db.refresh(db_issue)
    return _issue_to_response(db_issue)


class UpdateStatusRequest(BaseModel):
    status: IssueStatus


@router.patch("/{issue_id}/status", response_model=IssueResponse)
async def update_issue_status(
    issue_id: int, request: UpdateStatusRequest, db: Session = Depends(get_db)
):
    """
    Update the status of an issue
    """
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    db_issue.status = request.status
    db.commit()
    db.refresh(db_issue)
    return _issue_to_response(db_issue)


class UpdatePriorityRequest(BaseModel):
    priority: IssuePriority


@router.patch("/{issue_id}/priority", response_model=IssueResponse)
async def update_issue_priority(
    issue_id: int, request: UpdatePriorityRequest, db: Session = Depends(get_db)
):
    """
    Update the priority of an issue
    """
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    db_issue.priority = request.priority
    db.commit()
    db.refresh(db_issue)
    return _issue_to_response(db_issue)


@router.delete("/{issue_id}", status_code=204)
async def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    """
    Delete an issue
    """
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    db.delete(db_issue)
    db.commit()
    return None


@router.get("/{issue_id}/comments", response_model=list[dict])
async def get_issue_comments(issue_id: int, db: Session = Depends(get_db)):
    """
    Get all comments for an issue
    """
    # Verify issue exists
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    from app.models.issue import Comment

    comments = (
        db.query(Comment)
        .filter(Comment.issue_id == issue_id)
        .order_by(Comment.created_at.asc())
        .all()
    )

    return [
        {
            "id": comment.id,
            "body": comment.body,
            "author_id": comment.author_id,
            "issue_id": comment.issue_id,
            "created_at": comment.created_at.isoformat() if comment.created_at else None,
        }
        for comment in comments
    ]


@router.get("/{issue_id}/attachments", response_model=list[dict])
async def get_issue_attachments(issue_id: int, db: Session = Depends(get_db)):
    """
    Get all attachments for an issue
    """
    # Verify issue exists
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # TODO: Implement when Attachment model is added
    return []


@router.get("/{issue_id}/history", response_model=list[dict])
async def get_issue_history(issue_id: int, db: Session = Depends(get_db)):
    """
    Get change history for an issue
    """
    # Verify issue exists
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # TODO: Implement when IssueHistory model is added
    return []
