from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr

router = APIRouter()


# Pydantic schemas (placeholder - will be replaced with actual models later)
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


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=list[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str | None = None,
    is_active: bool | None = None,
):
    """
    Get all users with pagination and optional filtering
    """
    # TODO: Implement database query when models are added
    return []


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """
    Get a specific user by ID
    """
    # TODO: Implement database query when models are added
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str):
    """
    Get a specific user by username
    """
    # TODO: Implement database query when models are added
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """
    Create a new user (admin only)
    """
    # TODO: Implement database insert with password hashing when models are added
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate):
    """
    Update an existing user
    """
    # TODO: Implement database update when models are added
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """
    Delete a user (soft delete - set is_active to False)
    """
    # TODO: Implement soft delete when models are added
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/{user_id}/issues", response_model=list[dict])
async def get_user_issues(
    user_id: int,
    assigned: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get issues assigned to or reported by a user
    """
    # TODO: Implement database query when models are added
    return []


@router.get("/{user_id}/projects", response_model=list[dict])
async def get_user_projects(user_id: int):
    """
    Get projects where user is a member or lead
    """
    # TODO: Implement database query when models are added
    return []
