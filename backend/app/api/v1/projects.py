from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.project import Project, ProjectMember, ProjectRole

router = APIRouter()


# Pydantic schemas
class ProjectBase(BaseModel):
    name: str
    key: str
    description: str | None = None
    owner_id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    owner_id: int | None = None


class ProjectResponse(ProjectBase):
    id: int

    class Config:
        from_attributes = True


class ProjectMemberResponse(BaseModel):
    user_id: int
    project_id: int
    role: ProjectRole

    class Config:
        from_attributes = True


@router.get("/", response_model=list[ProjectResponse])
def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Get all projects with pagination and optional search
    """
    query = db.query(Project)

    if search:
        search_filter = or_(
            Project.name.ilike(f"%{search}%"),
            Project.key.ilike(f"%{search}%"),
            Project.description.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Get a specific project by ID
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Create a new project
    """
    # Check if project key already exists
    existing_project = db.query(Project).filter(Project.key == project.key).first()
    if existing_project:
        raise HTTPException(
            status_code=400, detail=f"Project with key '{project.key}' already exists"
        )

    # Check if owner exists
    from app.models.user import User

    owner = db.query(User).filter(User.id == project.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user not found")

    # Create new project
    db_project = Project(
        name=project.name,
        key=project.key,
        description=project.description,
        owner_id=project.owner_id,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # Add owner as ADMIN member
    project_member = ProjectMember(
        user_id=project.owner_id,
        project_id=db_project.id,
        role=ProjectRole.ADMIN,
    )
    db.add(project_member)
    db.commit()

    return db_project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing project
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields if provided
    if project.name is not None:
        db_project.name = project.name
    if project.description is not None:
        db_project.description = project.description
    if project.owner_id is not None:
        # Verify new owner exists
        from app.models.user import User

        owner = db.query(User).filter(User.id == project.owner_id).first()
        if not owner:
            raise HTTPException(status_code=404, detail="Owner user not found")
        db_project.owner_id = project.owner_id

    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Delete a project
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(db_project)
    db.commit()
    return None


@router.get("/{project_id}/issues", response_model=list[dict])
def get_project_issues(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get all issues for a specific project
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    from app.models.issue import Issue

    issues = (
        db.query(Issue)
        .filter(Issue.project_id == project_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Convert to dict format (you can create a proper IssueResponse schema later)
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


@router.get("/{project_id}/stats", response_model=dict)
def get_project_stats(project_id: int, db: Session = Depends(get_db)):
    """
    Get statistics for a project (total issues, open issues, etc.)
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    from app.models.issue import Issue, IssueStatus

    total_issues = db.query(Issue).filter(Issue.project_id == project_id).count()
    open_issues = (
        db.query(Issue)
        .filter(
            Issue.project_id == project_id,
            Issue.status != IssueStatus.DONE,
        )
        .count()
    )
    done_issues = (
        db.query(Issue)
        .filter(
            Issue.project_id == project_id,
            Issue.status == IssueStatus.DONE,
        )
        .count()
    )
    total_members = (
        db.query(ProjectMember).filter(ProjectMember.project_id == project_id).count()
    )

    return {
        "project_id": project_id,
        "total_issues": total_issues,
        "open_issues": open_issues,
        "done_issues": done_issues,
        "total_members": total_members,
    }
