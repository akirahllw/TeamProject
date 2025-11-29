"""Tests for sprints API endpoints"""

from datetime import datetime, timedelta

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
        project = db.query(Project).filter(Project.key == "SPRINTTEST").first()
        if not project:
            project = Project(
                name="Sprint Test Project",
                key="SPRINTTEST",
                description="Test",
                owner_id=owner_id,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
        return project
    finally:
        db.close()


def test_get_sprints_empty():
    response = client.get("/api/v1/sprints/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_sprint():
    user = setup_test_user()
    project = setup_test_project(user.id)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)

    sprint_data = {
        "name": "Sprint 1",
        "project_id": project.id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "goal": "Complete features",
    }
    response = client.post("/api/v1/sprints/", json=sprint_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sprint_data["name"]
    assert data["project_id"] == project.id
    assert "id" in data


def test_create_sprint_invalid_dates():
    user = setup_test_user()
    project = setup_test_project(user.id)
    start_date = datetime.now()
    end_date = start_date - timedelta(days=1)

    sprint_data = {
        "name": "Invalid Sprint",
        "project_id": project.id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    response = client.post("/api/v1/sprints/", json=sprint_data)
    assert response.status_code == 400


def test_create_sprint_project_not_found():
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)

    sprint_data = {
        "name": "Sprint 1",
        "project_id": 99999,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    response = client.post("/api/v1/sprints/", json=sprint_data)
    assert response.status_code == 404


def test_get_sprint_by_id():
    user = setup_test_user()
    project = setup_test_project(user.id)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)

    sprint_data = {
        "name": "Sprint 2",
        "project_id": project.id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    create_response = client.post("/api/v1/sprints/", json=sprint_data)
    sprint_id = create_response.json()["id"]

    response = client.get(f"/api/v1/sprints/{sprint_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sprint_id


def test_get_sprint_not_found():
    response = client.get("/api/v1/sprints/99999")
    assert response.status_code == 404


def test_update_sprint():
    user = setup_test_user()
    project = setup_test_project(user.id)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)

    sprint_data = {
        "name": "Sprint 3",
        "project_id": project.id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    create_response = client.post("/api/v1/sprints/", json=sprint_data)
    sprint_id = create_response.json()["id"]

    update_data = {"name": "Updated Sprint", "goal": "New goal"}
    response = client.put(f"/api/v1/sprints/{sprint_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Sprint"
    assert data["goal"] == "New goal"


def test_delete_sprint():
    user = setup_test_user()
    project = setup_test_project(user.id)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)

    sprint_data = {
        "name": "Sprint 4",
        "project_id": project.id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    create_response = client.post("/api/v1/sprints/", json=sprint_data)
    sprint_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/sprints/{sprint_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/sprints/{sprint_id}")
    assert get_response.status_code == 404


def test_start_sprint():
    user = setup_test_user()
    project = setup_test_project(user.id)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)

    sprint_data = {
        "name": "Sprint 5",
        "project_id": project.id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    create_response = client.post("/api/v1/sprints/", json=sprint_data)
    sprint_id = create_response.json()["id"]

    response = client.patch(f"/api/v1/sprints/{sprint_id}/start")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACTIVE"


def test_close_sprint():
    user = setup_test_user()
    project = setup_test_project(user.id)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)

    sprint_data = {
        "name": "Sprint 6",
        "project_id": project.id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    create_response = client.post("/api/v1/sprints/", json=sprint_data)
    sprint_id = create_response.json()["id"]

    response = client.patch(f"/api/v1/sprints/{sprint_id}/close")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CLOSED"


def test_get_sprint_issues():
    user = setup_test_user()
    project = setup_test_project(user.id)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)

    sprint_data = {
        "name": "Sprint 7",
        "project_id": project.id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    create_response = client.post("/api/v1/sprints/", json=sprint_data)
    sprint_id = create_response.json()["id"]

    response = client.get(f"/api/v1/sprints/{sprint_id}/issues")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_sprint_stats():
    user = setup_test_user()
    project = setup_test_project(user.id)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)

    sprint_data = {
        "name": "Sprint 8",
        "project_id": project.id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    create_response = client.post("/api/v1/sprints/", json=sprint_data)
    sprint_id = create_response.json()["id"]

    response = client.get(f"/api/v1/sprints/{sprint_id}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["sprint_id"] == sprint_id
    assert "total_issues" in data
    assert "done_issues" in data
    assert "completion_percentage" in data


def test_get_sprints_by_project():
    user = setup_test_user()
    project = setup_test_project(user.id)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)

    sprint_data = {
        "name": "Sprint 9",
        "project_id": project.id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    _ = client.post("/api/v1/sprints/", json=sprint_data)

    response = client.get(f"/api/v1/sprints/?project_id={project.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
