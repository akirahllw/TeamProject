from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.issue import Issue
from app.models.project import Project, ProjectMember
from app.models.user import User

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    password: str | None = None


class UserResponse(UserBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


@router.get("/", response_model=list[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    """
    Get all users with pagination and optional filtering
    """
    query = db.query(User)

    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.full_name.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """
    Get a specific user by username
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user (admin only)
    """
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail=f"User with username '{user.username}' already exists",
        )

    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=400, detail=f"User with email '{user.email}' already exists"
        )

    hashed_password = pwd_context.hash(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_admin,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """
    Update an existing user
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.email is not None:
        existing_email = (
            db.query(User).filter(User.email == user.email, User.id != user_id).first()
        )
        if existing_email:
            raise HTTPException(
                status_code=400, detail=f"Email '{user.email}' is already taken"
            )
        db_user.email = user.email

    if user.username is not None:
        existing_username = (
            db.query(User)
            .filter(User.username == user.username, User.id != user_id)
            .first()
        )
        if existing_username:
            raise HTTPException(
                status_code=400, detail=f"Username '{user.username}' is already taken"
            )
        db_user.username = user.username

    if user.full_name is not None:
        db_user.full_name = user.full_name

    if user.is_active is not None:
        db_user.is_active = user.is_active

    if user.is_admin is not None:
        db_user.is_superuser = user.is_admin

    if user.password is not None:
        db_user.hashed_password = pwd_context.hash(user.password)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user (soft delete - set is_active to False)
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.is_active = False
    db.commit()
    return None


@router.get("/{user_id}/issues", response_model=list[dict])
async def get_user_issues(
    user_id: int,
    assigned: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get issues assigned to or reported by a user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(Issue)

    if assigned:
        query = query.filter(Issue.assignee_id == user_id)
    else:
        query = query.filter(Issue.reporter_id == user_id)

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


@router.get("/{user_id}/projects", response_model=list[dict])
async def get_user_projects(user_id: int, db: Session = Depends(get_db)):
    """
    Get projects where user is a member or owner
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    owned_projects = db.query(Project).filter(Project.owner_id == user_id).all()

    member_projects = (
        db.query(Project)
        .join(ProjectMember)
        .filter(ProjectMember.user_id == user_id)
        .all()
    )

    all_projects = {p.id: p for p in owned_projects}
    for p in member_projects:
        all_projects[p.id] = p

    return [
        {
            "id": project.id,
            "name": project.name,
            "key": project.key,
            "description": project.description,
            "owner_id": project.owner_id,
        }
        for project in all_projects.values()
    ]
