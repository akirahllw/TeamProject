"""Tests for statuses API endpoints"""

from fastapi.testclient import TestClient
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


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def setup_test_user():
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            user = User(
                username="testuser",
                email="test@example.com",
                hashed_password="hashed",
                full_name="Test User",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


def setup_test_project(owner_id):
    db = TestingSessionLocal()
    try:
        project = db.query(Project).filter(Project.key == "STATUSTEST").first()
        if not project:
            project = Project(
                name="Status Test Project",
                key="STATUSTEST",
                description="Test",
                owner_id=owner_id,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
        return project
    finally:
        db.close()


def test_get_statuses_empty():
    response = client.get("/api/v1/statuses/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_status():
    status_data = {
        "name": "In Review",
        "description": "Issue is being reviewed",
        "color": "#FFA500",
        "category": "IN_PROGRESS",
    }
    response = client.post("/api/v1/statuses/", json=status_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == status_data["name"]
    assert data["category"] == status_data["category"]
    assert "id" in data


def test_create_status_with_project():
    user = setup_test_user()
    project = setup_test_project(user.id)
    status_data = {
        "name": "Project Status",
        "category": "TODO",
        "project_id": project.id,
    }
    response = client.post("/api/v1/statuses/", json=status_data)
    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == project.id


def test_create_status_invalid_category():
    status_data = {
        "name": "Invalid Status",
        "category": "INVALID",
    }
    response = client.post("/api/v1/statuses/", json=status_data)
    assert response.status_code == 400


def test_create_status_invalid_color():
    status_data = {
        "name": "Invalid Color",
        "category": "TODO",
        "color": "not-a-hex",
    }
    response = client.post("/api/v1/statuses/", json=status_data)
    assert response.status_code == 400


def test_get_status_by_id():
    status_data = {
        "name": "Test Status",
        "category": "DONE",
    }
    create_response = client.post("/api/v1/statuses/", json=status_data)
    status_id = create_response.json()["id"]

    response = client.get(f"/api/v1/statuses/{status_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == status_id
    assert data["name"] == status_data["name"]


def test_get_status_not_found():
    response = client.get("/api/v1/statuses/99999")
    assert response.status_code == 404


def test_update_status():
    status_data = {
        "name": "Original Status",
        "category": "TODO",
    }
    create_response = client.post("/api/v1/statuses/", json=status_data)
    status_id = create_response.json()["id"]

    update_data = {"name": "Updated Status", "color": "#00FF00"}
    response = client.put(f"/api/v1/statuses/{status_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Status"
    assert data["color"] == "#00FF00"


def test_delete_status():
    status_data = {
        "name": "Delete Status",
        "category": "TODO",
    }
    create_response = client.post("/api/v1/statuses/", json=status_data)
    status_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/statuses/{status_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/statuses/{status_id}")
    assert get_response.status_code == 404


def test_get_statuses_by_category():
    status_data = {
        "name": "Category Test",
        "category": "DONE",
    }
    _ = client.post("/api/v1/statuses/", json=status_data)

    response = client.get("/api/v1/statuses/?category=DONE")
    assert response.status_code == 200
    data = response.json()
    assert all(s["category"] == "DONE" for s in data)


def test_get_status_issues():
    status_data = {
        "name": "Status for Issues",
        "category": "TODO",
    }
    create_response = client.post("/api/v1/statuses/", json=status_data)
    status_id = create_response.json()["id"]

    response = client.get(f"/api/v1/statuses/{status_id}/issues")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
