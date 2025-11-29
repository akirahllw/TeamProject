from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.issue import Issue
from app.models.project import Project
from app.models.sprint import Sprint, SprintStatus

router = APIRouter()


class SprintBase(BaseModel):
    name: str
    project_id: int
    start_date: datetime
    end_date: datetime
    goal: str | None = None


class SprintCreate(SprintBase):
    pass


class SprintUpdate(BaseModel):
    name: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    goal: str | None = None


class SprintResponse(SprintBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=list[SprintResponse])
def get_sprints(
    project_id: int | None = Query(None),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get all sprints with optional filtering
    """
    query = db.query(Sprint)

    if project_id:
        query = query.filter(Sprint.project_id == project_id)

    if status:
        try:
            status_enum = SprintStatus(status.upper())
            query = query.filter(Sprint.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {[s.value for s in SprintStatus]}",
            ) from None

    sprints = query.order_by(Sprint.start_date.desc()).offset(skip).limit(limit).all()
    return sprints


@router.get("/{sprint_id}", response_model=SprintResponse)
def get_sprint(sprint_id: int, db: Session = Depends(get_db)):
    """
    Get a specific sprint by ID
    """
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return sprint


@router.post("/", response_model=SprintResponse, status_code=201)
def create_sprint(sprint: SprintCreate, db: Session = Depends(get_db)):
    """
    Create a new sprint
    """
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if sprint.start_date >= sprint.end_date:
        raise HTTPException(
            status_code=400, detail="Start date must be before end date"
        )

    db_sprint = Sprint(
        name=sprint.name,
        project_id=sprint.project_id,
        start_date=sprint.start_date,
        end_date=sprint.end_date,
        goal=sprint.goal,
        status=SprintStatus.PLANNED,
    )
    db.add(db_sprint)
    db.commit()
    db.refresh(db_sprint)

    return db_sprint


@router.put("/{sprint_id}", response_model=SprintResponse)
def update_sprint(sprint_id: int, sprint: SprintUpdate, db: Session = Depends(get_db)):
    """
    Update an existing sprint
    """
    db_sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not db_sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    if sprint.name is not None:
        db_sprint.name = sprint.name

    if sprint.start_date is not None:
        end_date = sprint.end_date if sprint.end_date else db_sprint.end_date
        if sprint.start_date >= end_date:
            raise HTTPException(
                status_code=400, detail="Start date must be before end date"
            )
        db_sprint.start_date = sprint.start_date

    if sprint.end_date is not None:
        start_date = sprint.start_date if sprint.start_date else db_sprint.start_date
        if start_date >= sprint.end_date:
            raise HTTPException(
                status_code=400, detail="Start date must be before end date"
            )
        db_sprint.end_date = sprint.end_date

    if sprint.goal is not None:
        db_sprint.goal = sprint.goal

    db.commit()
    db.refresh(db_sprint)
    return db_sprint


@router.delete("/{sprint_id}", status_code=204)
def delete_sprint(sprint_id: int, db: Session = Depends(get_db)):
    """
    Delete a sprint
    """
    db_sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not db_sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    db.delete(db_sprint)
    db.commit()
    return None


@router.patch("/{sprint_id}/start", response_model=SprintResponse)
def start_sprint(sprint_id: int, db: Session = Depends(get_db)):
    """
    Start a sprint (change status to active)
    """
    db_sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not db_sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    if db_sprint.status == SprintStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Sprint is already active")

    if db_sprint.status == SprintStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Cannot start a closed sprint")

    db_sprint.status = SprintStatus.ACTIVE
    db.commit()
    db.refresh(db_sprint)

    return db_sprint


@router.patch("/{sprint_id}/close", response_model=SprintResponse)
def close_sprint(sprint_id: int, db: Session = Depends(get_db)):
    """
    Close a sprint (change status to closed)
    """
    db_sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not db_sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    if db_sprint.status == SprintStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Sprint is already closed")

    db_sprint.status = SprintStatus.CLOSED
    db.commit()
    db.refresh(db_sprint)

    return db_sprint


@router.get("/{sprint_id}/issues", response_model=list[dict])
def get_sprint_issues(
    sprint_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get all issues in a sprint
    """
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    issues = (
        db.query(Issue)
        .filter(Issue.sprint_id == sprint_id)
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


@router.post("/{sprint_id}/issues/{issue_id}", status_code=201)
def add_issue_to_sprint(sprint_id: int, issue_id: int, db: Session = Depends(get_db)):
    """
    Add an issue to a sprint
    """
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue.project_id != sprint.project_id:
        raise HTTPException(
            status_code=400,
            detail="Issue must belong to the same project as the sprint",
        )

    issue.sprint_id = sprint_id
    db.commit()
    db.refresh(issue)

    return {"message": "Issue added to sprint successfully", "issue_id": issue_id}


@router.delete("/{sprint_id}/issues/{issue_id}", status_code=204)
def remove_issue_from_sprint(
    sprint_id: int, issue_id: int, db: Session = Depends(get_db)
):
    """
    Remove an issue from a sprint
    """
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue.sprint_id != sprint_id:
        raise HTTPException(status_code=400, detail="Issue is not in this sprint")

    issue.sprint_id = None
    db.commit()

    return None


@router.get("/{sprint_id}/stats", response_model=dict)
def get_sprint_stats(sprint_id: int, db: Session = Depends(get_db)):
    """
    Get sprint statistics (total issues, completed issues, etc.)
    """
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    from app.models.issue import IssueStatus

    total_issues = db.query(Issue).filter(Issue.sprint_id == sprint_id).count()
    done_issues = (
        db.query(Issue)
        .filter(Issue.sprint_id == sprint_id, Issue.status == IssueStatus.DONE)
        .count()
    )
    in_progress_issues = (
        db.query(Issue)
        .filter(Issue.sprint_id == sprint_id, Issue.status == IssueStatus.IN_PROGRESS)
        .count()
    )

    return {
        "sprint_id": sprint_id,
        "total_issues": total_issues,
        "done_issues": done_issues,
        "in_progress_issues": in_progress_issues,
        "completion_percentage": (
            round((done_issues / total_issues * 100), 2) if total_issues > 0 else 0
        ),
    }
