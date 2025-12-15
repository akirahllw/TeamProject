"""Tests for users API endpoints"""

from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base, get_db
from app.main import app
from app.models.project import Project
from app.models.user import User

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
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
                hashed_password=pwd_context.hash("testpass123"),
                full_name="Test User",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


def test_get_users_empty():
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user():
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "password123",
        "is_active": True,
        "is_admin": False,
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "password" not in data


def test_create_user_duplicate_username():
    user = setup_test_user()
    user_data = {
        "username": user.username,
        "email": "different@example.com",
        "full_name": "Different User",
        "password": "password123",
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_user_duplicate_email():
    user = setup_test_user()
    user_data = {
        "username": "differentuser",
        "email": user.email,
        "full_name": "Different User",
        "password": "password123",
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_user_by_id():
    user = setup_test_user()
    response = client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["username"] == user.username


def test_get_user_by_username():
    user = setup_test_user()
    response = client.get(f"/api/v1/users/username/{user.username}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user.username


def test_get_user_not_found():
    response = client.get("/api/v1/users/99999")
    assert response.status_code == 404


def test_update_user():
    user = setup_test_user()
    update_data = {"full_name": "Updated Name", "is_active": False}
    response = client.put(f"/api/v1/users/{user.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["is_active"] is False


def test_update_user_duplicate_email():
    user1 = setup_test_user("user1", "user1@example.com")
    user2 = setup_test_user("user2", "user2@example.com")
    update_data = {"email": user2.email}
    response = client.put(f"/api/v1/users/{user1.id}", json=update_data)
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]


def test_delete_user():
    user = setup_test_user("deleteuser", "delete@example.com")
    response = client.delete(f"/api/v1/users/{user.id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/users/{user.id}")
    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_get_users_with_search():
    setup_test_user("alice", "alice@example.com")
    setup_test_user("bob", "bob@example.com")
    response = client.get("/api/v1/users/?search=alice")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(u["username"] == "alice" for u in data)


def test_get_users_with_filter():
    response = client.get("/api/v1/users/?is_active=true")
    assert response.status_code == 200
    data = response.json()
    assert all(u["is_active"] is True for u in data)


def setup_test_project(owner_id):
    db = TestingSessionLocal()
    try:
        # Check if project already exists
        project = db.query(Project).filter(Project.key == "TESTPROJ").first()
        if not project:
            project = Project(
                name="Test Project",
                key="TESTPROJ",
                description="Test",
                owner_id=owner_id,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
        return project
    finally:
        db.close()


def test_get_user_issues():
    user = setup_test_user()
    setup_test_project(user.id)
    response = client.get(f"/api/v1/users/{user.id}/issues?assigned=true")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_projects():
    user = setup_test_user()
    project = setup_test_project(user.id)
    response = client.get(f"/api/v1/users/{user.id}/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["id"] == project.id for p in data)
