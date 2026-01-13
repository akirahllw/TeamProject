"""Tests for notifications API endpoints"""

from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base, get_db
from app.main import app
from app.models.notification import Notification, NotificationType
from app.models.user import User

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def setup_test_user(username="testuser", email="test@example.com"):
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(
                username=username,
                email=email,
                hashed_password=pwd_context.hash("testpass"),
                full_name="Test User",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


def setup_test_notification(user_id, title="Test Notification"):
    db = TestingSessionLocal()
    try:
        notification = Notification(
            type=NotificationType.DIRECT,
            title=title,
            description="Test notification description",
            author="Test Author",
            user_id=user_id,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    finally:
        db.close()


def test_get_notifications_empty():
    user = setup_test_user()
    response = client.get(f"/api/v1/notifications/?user_id={user.id}")
    assert response.status_code == 200
    assert response.json() == []


def test_create_notification():
    user = setup_test_user()
    notification_data = {
        "type": "Direct",
        "title": "mentioned you in",
        "description": "PROJ-123: Test Issue",
        "author": "John Doe",
        "user_id": user.id,
    }
    response = client.post("/api/v1/notifications/", json=notification_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == notification_data["title"]
    assert data["author"] == notification_data["author"]
    assert data["is_read"] is False
    assert "id" in data


def test_create_notification_user_not_found():
    notification_data = {
        "type": "Direct",
        "title": "Test",
        "description": "Test",
        "author": "Test",
        "user_id": 99999,
    }
    response = client.post("/api/v1/notifications/", json=notification_data)
    assert response.status_code == 404


def test_get_notification_by_id():
    user = setup_test_user()
    notification = setup_test_notification(user.id)

    response = client.get(f"/api/v1/notifications/{notification.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == notification.id
    assert data["title"] == notification.title


def test_get_notification_not_found():
    response = client.get("/api/v1/notifications/99999")
    assert response.status_code == 404


def test_mark_notification_as_read():
    user = setup_test_user()
    notification = setup_test_notification(user.id)

    response = client.patch(f"/api/v1/notifications/{notification.id}/read")
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True


def test_toggle_notification_read_status():
    user = setup_test_user()
    notification = setup_test_notification(user.id)

    response = client.patch(f"/api/v1/notifications/{notification.id}/toggle")
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True

    # Toggle again
    response = client.patch(f"/api/v1/notifications/{notification.id}/toggle")
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is False


def test_mark_all_notifications_read():
    user = setup_test_user()
    setup_test_notification(user.id, "Notification 1")
    setup_test_notification(user.id, "Notification 2")

    response = client.patch(f"/api/v1/notifications/mark-all-read?user_id={user.id}")
    assert response.status_code == 200
    assert "message" in response.json()


def test_get_unread_count():
    user = setup_test_user()
    setup_test_notification(user.id, "Unread 1")
    setup_test_notification(user.id, "Unread 2")

    response = client.get(f"/api/v1/notifications/unread/count?user_id={user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 2


def test_delete_notification():
    user = setup_test_user()
    notification = setup_test_notification(user.id)

    response = client.delete(f"/api/v1/notifications/{notification.id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/notifications/{notification.id}")
    assert get_response.status_code == 404


def test_filter_notifications_by_type():
    user = setup_test_user()
    setup_test_notification(user.id, "Direct Notification")

    response = client.get(f"/api/v1/notifications/?user_id={user.id}&type=Direct")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(n["type"] == "Direct" for n in data)


def test_filter_notifications_unread_only():
    user = setup_test_user()
    setup_test_notification(user.id, "Unread Notification")

    response = client.get(f"/api/v1/notifications/?user_id={user.id}&unread_only=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(not n["is_read"] for n in data)


def test_notifications_pagination():
    user = setup_test_user()
    for i in range(5):
        setup_test_notification(user.id, f"Notification {i}")

    response = client.get(f"/api/v1/notifications/?user_id={user.id}&skip=0&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
