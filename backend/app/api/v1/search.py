from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.issue import Issue
from app.models.project import Project
from app.models.user import User

router = APIRouter()


class SearchResult(BaseModel):
    type: str
    id: int
    title: str
    description: str | None = None
    url: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    type: str | None = Query(None, description="Filter by type: issue, project, user"),
    project_id: int | None = Query(None, description="Filter by project"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
):
    """
    Global search across issues, projects, users, etc.
    """
    results: list[SearchResult] = []
    search_types = ["issue", "project", "user"] if type is None else [type.lower()]

    if "issue" in search_types:
        query = db.query(Issue)
        if project_id:
            query = query.filter(Issue.project_id == project_id)

        search_filter = or_(
            Issue.title.ilike(f"%{q}%"),
            Issue.description.ilike(f"%{q}%"),
        )
        issues = query.filter(search_filter).offset(skip).limit(limit).all()

        for issue in issues:
            results.append(
                SearchResult(
                    type="issue",
                    id=issue.id,
                    title=issue.title,
                    description=issue.description,
                    url=f"/api/v1/issues/{issue.id}",
                )
            )

    if "project" in search_types:
        query = db.query(Project)
        search_filter = or_(
            Project.name.ilike(f"%{q}%"),
            Project.key.ilike(f"%{q}%"),
            Project.description.ilike(f"%{q}%"),
        )
        projects = query.filter(search_filter).offset(skip).limit(limit).all()

        for project in projects:
            results.append(
                SearchResult(
                    type="project",
                    id=project.id,
                    title=project.name,
                    description=project.description,
                    url=f"/api/v1/projects/{project.id}",
                )
            )

    if "user" in search_types:
        search_filter = or_(
            User.username.ilike(f"%{q}%"),
            User.email.ilike(f"%{q}%"),
            User.full_name.ilike(f"%{q}%"),
        )
        users = db.query(User).filter(search_filter).offset(skip).limit(limit).all()

        for user in users:
            results.append(
                SearchResult(
                    type="user",
                    id=user.id,
                    title=user.username,
                    description=user.full_name,
                    url=f"/api/v1/users/{user.id}",
                )
            )

    total = len(results)

    return SearchResponse(
        query=q,
        results=results,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
    )


@router.get("/issues", response_model=list[dict])
def search_issues(
    q: str = Query(..., min_length=1),
    project_id: int | None = Query(None),
    assignee_id: int | None = Query(None),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search issues with advanced filtering
    """
    query = db.query(Issue)

    search_filter = or_(
        Issue.title.ilike(f"%{q}%"),
        Issue.description.ilike(f"%{q}%"),
    )
    query = query.filter(search_filter)

    if project_id:
        query = query.filter(Issue.project_id == project_id)

    if assignee_id:
        query = query.filter(Issue.assignee_id == assignee_id)

    if status:
        from app.models.issue import IssueStatus

        try:
            status_enum = IssueStatus(status.upper())
            query = query.filter(Issue.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {[s.value for s in IssueStatus]}",
            ) from None

    issues = query.offset(skip).limit(limit).all()

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


@router.get("/projects", response_model=list[dict])
def search_projects(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search projects
    """
    search_filter = or_(
        Project.name.ilike(f"%{q}%"),
        Project.key.ilike(f"%{q}%"),
        Project.description.ilike(f"%{q}%"),
    )
    projects = db.query(Project).filter(search_filter).offset(skip).limit(limit).all()

    return [
        {
            "id": project.id,
            "name": project.name,
            "key": project.key,
            "description": project.description,
            "owner_id": project.owner_id,
        }
        for project in projects
    ]


@router.get("/users", response_model=list[dict])
def search_users(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search users
    """
    search_filter = or_(
        User.username.ilike(f"%{q}%"),
        User.email.ilike(f"%{q}%"),
        User.full_name.ilike(f"%{q}%"),
    )
    users = db.query(User).filter(search_filter).offset(skip).limit(limit).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
        }
        for user in users
    ]
