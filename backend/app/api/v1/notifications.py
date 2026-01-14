from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.notification import Notification, NotificationType
from app.models.user import User

router = APIRouter()


class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    description: str
    author: str


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationResponse(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime
    time: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_time(cls, notification: Notification):
        # Calculate relative time
        now = datetime.now(notification.created_at.tzinfo)
        diff = now - notification.created_at

        if diff.days > 0:
            time_str = f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            time_str = f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            minutes = diff.seconds // 60
            time_str = f"{minutes} minute{'s' if minutes > 1 else ''} ago"

        return cls(
            id=notification.id,
            type=notification.type,
            title=notification.title,
            description=notification.description,
            author=notification.author,
            is_read=notification.is_read,
            created_at=notification.created_at,
            time=time_str,
        )


@router.get("/", response_model=list[NotificationResponse])
async def get_notifications(
    user_id: int,
    type: NotificationType | None = Query(None),
    unread_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get notifications for a user"""
    query = db.query(Notification).filter(Notification.user_id == user_id)

    if type:
        query = query.filter(Notification.type == type)

    if unread_only:
        query = query.filter(not Notification.is_read)

    notifications = (
        query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    )

    return [NotificationResponse.from_orm_with_time(n) for n in notifications]


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(notification_id: int, db: Session = Depends(get_db)):
    """Get a specific notification"""
    notification = (
        db.query(Notification).filter(Notification.id == notification_id).first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return NotificationResponse.from_orm_with_time(notification)


@router.post("/", response_model=NotificationResponse, status_code=201)
async def create_notification(
    notification: NotificationCreate, db: Session = Depends(get_db)
):
    """Create a new notification"""
    # Verify user exists
    user = db.query(User).filter(User.id == notification.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_notification = Notification(
        type=notification.type,
        title=notification.title,
        description=notification.description,
        author=notification.author,
        user_id=notification.user_id,
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    return NotificationResponse.from_orm_with_time(db_notification)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    """Mark notification as read"""
    notification = (
        db.query(Notification).filter(Notification.id == notification_id).first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()
    db.refresh(notification)

    return NotificationResponse.from_orm_with_time(notification)


@router.patch("/{notification_id}/toggle", response_model=NotificationResponse)
async def toggle_read_status(notification_id: int, db: Session = Depends(get_db)):
    """Toggle notification read status"""
    notification = (
        db.query(Notification).filter(Notification.id == notification_id).first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = not notification.is_read
    db.commit()
    db.refresh(notification)

    return NotificationResponse.from_orm_with_time(notification)


@router.patch("/mark-all-read")
async def mark_all_read(user_id: int, db: Session = Depends(get_db)):
    """Mark all notifications as read for a user"""
    db.query(Notification).filter(
        Notification.user_id == user_id, not Notification.is_read
    ).update({"is_read": True})
    db.commit()

    return {"message": "All notifications marked as read"}


@router.get("/unread/count")
async def get_unread_count(user_id: int, db: Session = Depends(get_db)):
    """Get unread notification count for a user"""
    count = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, not Notification.is_read)
        .count()
    )

    return {"unread_count": count}


@router.delete("/{notification_id}", status_code=204)
async def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    """Delete a notification"""
    notification = (
        db.query(Notification).filter(Notification.id == notification_id).first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notification)
    db.commit()
    return None
