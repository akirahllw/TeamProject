from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime

from app.db.base import get_db, Base

router = APIRouter()


# Database Model (you'll need to create this in app/models/ directory)
class Priority(Base):
    __tablename__ = "priorities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)
    level = Column(Integer, nullable=False, index=True)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Pydantic schemas
class PriorityBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    level: int


class PriorityCreate(PriorityBase):
    pass


class PriorityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    level: Optional[int] = None


class PriorityResponse(PriorityBase):
    id: int
    is_default: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Routes
@router.get("/", response_model=List[PriorityResponse])
async def get_priorities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all priorities"""
    priorities = db.query(Priority).order_by(Priority.level).offset(skip).limit(limit).all()
    return priorities


@router.get("/{priority_id}", response_model=PriorityResponse)
async def get_priority(priority_id: int, db: Session = Depends(get_db)):
    """Get a specific priority by ID"""
    priority = db.query(Priority).filter(Priority.id == priority_id).first()

    if not priority:
        raise HTTPException(status_code=404, detail="Priority not found")

    return priority


@router.post("/", response_model=PriorityResponse, status_code=201)
async def create_priority(
    priority: PriorityCreate,
    db: Session = Depends(get_db)
):
    """Create a new priority"""
    if priority.level < 1 or priority.level > 5:
        raise HTTPException(
            status_code=400,
            detail="Priority level must be between 1 and 5"
        )

    existing = db.query(Priority).filter(Priority.name == priority.name).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Priority with this name already exists"
        )

    db_priority = Priority(**priority.dict())
    db.add(db_priority)
    db.commit()
    db.refresh(db_priority)

    return db_priority


@router.put("/{priority_id}", response_model=PriorityResponse)
async def update_priority(
    priority_id: int,
    priority: PriorityUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing priority"""
    db_priority = db.query(Priority).filter(Priority.id == priority_id).first()

    if not db_priority:
        raise HTTPException(status_code=404, detail="Priority not found")

    update_data = priority.dict(exclude_unset=True)

    if "level" in update_data and (update_data["level"] < 1 or update_data["level"] > 5):
        raise HTTPException(
            status_code=400,
            detail="Priority level must be between 1 and 5"
        )

    if "name" in update_data:
        existing = db.query(Priority).filter(
            Priority.name == update_data["name"],
            Priority.id != priority_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Priority with this name already exists"
            )

    for field, value in update_data.items():
        setattr(db_priority, field, value)

    db.commit()
    db.refresh(db_priority)

    return db_priority


@router.delete("/{priority_id}", status_code=204)
async def delete_priority(priority_id: int, db: Session = Depends(get_db)):
    """Delete a priority"""
    db_priority = db.query(Priority).filter(Priority.id == priority_id).first()

    if not db_priority:
        raise HTTPException(status_code=404, detail="Priority not found")

    if db_priority.is_default:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete default priority"
        )

    # TODO: Check if priority is in use by any issues

    db.delete(db_priority)
    db.commit()

    return None


@router.get("/{priority_id}/issues", response_model=List[dict])
async def get_priority_issues(
    priority_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all issues with a specific priority"""
    priority = db.query(Priority).filter(Priority.id == priority_id).first()
    if not priority:
        raise HTTPException(status_code=404, detail="Priority not found")

    # TODO: Implement issue querying when needed
    return []
