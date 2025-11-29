from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.issue import Issue
from app.models.project import Project
from app.models.status import Status, StatusCategory

router = APIRouter()


class StatusBase(BaseModel):
    name: str
    description: str | None = None
    color: str | None = None
    category: str


class StatusCreate(StatusBase):
    project_id: int | None = None


class StatusUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    category: str | None = None


class StatusResponse(StatusBase):
    id: int
    is_default: bool = False
    project_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=list[StatusResponse])
def get_statuses(
    category: str | None = Query(None),
    project_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get all statuses with optional filtering
    """
    query = db.query(Status)

    if category:
        try:
            category_enum = StatusCategory(category.upper())
            query = query.filter(Status.category == category_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {[c.value for c in StatusCategory]}",
            )

    if project_id:
        query = query.filter(Status.project_id == project_id)

    statuses = query.offset(skip).limit(limit).all()
    return statuses


@router.get("/{status_id}", response_model=StatusResponse)
def get_status(status_id: int, db: Session = Depends(get_db)):
    """
    Get a specific status by ID
    """
    status = db.query(Status).filter(Status.id == status_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status


@router.post("/", response_model=StatusResponse, status_code=201)
def create_status(status: StatusCreate, db: Session = Depends(get_db)):
    """
    Create a new status
    """
    if status.project_id:
        project = db.query(Project).filter(Project.id == status.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

    try:
        category_enum = StatusCategory(status.category.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {[c.value for c in StatusCategory]}",
        )

    if status.color and not status.color.startswith("#"):
        raise HTTPException(
            status_code=400, detail="Color must be a hex code starting with #"
        )

    db_status = Status(
        name=status.name,
        description=status.description,
        color=status.color,
        category=category_enum,
        project_id=status.project_id,
        is_default=False,
    )
    db.add(db_status)
    db.commit()
    db.refresh(db_status)

    return db_status


@router.put("/{status_id}", response_model=StatusResponse)
def update_status(status_id: int, status: StatusUpdate, db: Session = Depends(get_db)):
    """
    Update an existing status
    """
    db_status = db.query(Status).filter(Status.id == status_id).first()
    if not db_status:
        raise HTTPException(status_code=404, detail="Status not found")

    if status.name is not None:
        db_status.name = status.name

    if status.description is not None:
        db_status.description = status.description

    if status.color is not None:
        if not status.color.startswith("#"):
            raise HTTPException(
                status_code=400, detail="Color must be a hex code starting with #"
            )
        db_status.color = status.color

    if status.category is not None:
        try:
            category_enum = StatusCategory(status.category.upper())
            db_status.category = category_enum
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {[c.value for c in StatusCategory]}",
            )

    db.commit()
    db.refresh(db_status)
    return db_status


@router.delete("/{status_id}", status_code=204)
def delete_status(status_id: int, db: Session = Depends(get_db)):
    """
    Delete a status
    Note: Since Issue uses IssueStatus enum directly (not a foreign key to Status),
    we can't check if issues are using this status. The status can be deleted safely.
    """
    db_status = db.query(Status).filter(Status.id == status_id).first()
    if not db_status:
        raise HTTPException(status_code=404, detail="Status not found")

    from app.models.workflow import WorkflowStatus

    workflow_statuses_count = (
        db.query(WorkflowStatus).filter(WorkflowStatus.status_id == status_id).count()
    )
    if workflow_statuses_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete status. It is being used by {workflow_statuses_count} workflow(s)",
        )

    db.delete(db_status)
    db.commit()
    return None


@router.get("/{status_id}/issues", response_model=list[dict])
def get_status_issues(
    status_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get all issues with a specific status
    Note: This endpoint maps Status model to IssueStatus enum.
    Since Issue uses IssueStatus enum directly, we map the Status category to IssueStatus.
    """
    status = db.query(Status).filter(Status.id == status_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    from app.models.issue import IssueStatus

    status_mapping = {
        StatusCategory.TODO: IssueStatus.TO_DO,
        StatusCategory.IN_PROGRESS: IssueStatus.IN_PROGRESS,
        StatusCategory.DONE: IssueStatus.DONE,
    }

    issue_status = status_mapping.get(status.category)
    if not issue_status:
        return []

    issues = (
        db.query(Issue)
        .filter(Issue.status == issue_status)
        .offset(skip)
        .limit(limit)
        .all()
    )

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
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
            "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
        }
        for issue in issues
    ]
