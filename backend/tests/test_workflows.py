"""Tests for workflows API endpoints"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base, get_db
from app.main import app
from app.models.project import Project
from app.models.status import Status
from app.models.user import User
from app.models.workflow import Workflow

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
        project = db.query(Project).filter(Project.key == "WORKFLOWTEST").first()
        if not project:
            project = Project(
                name="Workflow Test Project",
                key="WORKFLOWTEST",
                description="Test",
                owner_id=owner_id,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
        return project
    finally:
        db.close()


def setup_test_status(category="TODO"):
    db = TestingSessionLocal()
    try:
        status = Status(
            name=f"Test Status {category}",
            category=category,
            color="#FF0000",
        )
        db.add(status)
        db.commit()
        db.refresh(status)
        return status
    finally:
        db.close()


def test_get_workflows_empty():
    response = client.get("/api/v1/workflows/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_workflow():
    workflow_data = {
        "name": "Test Workflow",
        "description": "A test workflow",
    }
    response = client.post("/api/v1/workflows/", json=workflow_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == workflow_data["name"]
    assert "id" in data


def test_create_workflow_with_project():
    user = setup_test_user()
    project = setup_test_project(user.id)
    workflow_data = {
        "name": "Project Workflow",
        "project_id": project.id,
    }
    response = client.post("/api/v1/workflows/", json=workflow_data)
    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == project.id


def test_get_workflow_by_id():
    workflow_data = {"name": "Test Workflow 2"}
    create_response = client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]

    response = client.get(f"/api/v1/workflows/{workflow_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workflow_id


def test_get_workflow_not_found():
    response = client.get("/api/v1/workflows/99999")
    assert response.status_code == 404


def test_update_workflow():
    workflow_data = {"name": "Original Workflow"}
    create_response = client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]

    update_data = {"name": "Updated Workflow", "description": "New description"}
    response = client.put(f"/api/v1/workflows/{workflow_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Workflow"
    assert data["description"] == "New description"


def test_delete_workflow():
    workflow_data = {"name": "Delete Workflow"}
    create_response = client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/workflows/{workflow_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/workflows/{workflow_id}")
    assert get_response.status_code == 404


def test_add_status_to_workflow():
    workflow_data = {"name": "Workflow with Status"}
    create_response = client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]

    status = setup_test_status()
    response = client.post(
        f"/api/v1/workflows/{workflow_id}/statuses/{status.id}?position=0"
    )
    assert response.status_code == 201


def test_add_status_to_workflow_duplicate():
    workflow_data = {"name": "Workflow Duplicate"}
    create_response = client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]

    status = setup_test_status()
    _ = client.post(f"/api/v1/workflows/{workflow_id}/statuses/{status.id}")

    response = client.post(f"/api/v1/workflows/{workflow_id}/statuses/{status.id}")
    assert response.status_code == 400


def test_remove_status_from_workflow():
    workflow_data = {"name": "Workflow Remove"}
    create_response = client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]

    status = setup_test_status()
    _ = client.post(f"/api/v1/workflows/{workflow_id}/statuses/{status.id}")

    response = client.delete(f"/api/v1/workflows/{workflow_id}/statuses/{status.id}")
    assert response.status_code == 204


def test_get_workflow_statuses():
    workflow_data = {"name": "Workflow Statuses"}
    create_response = client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]

    status = setup_test_status()
    _ = client.post(f"/api/v1/workflows/{workflow_id}/statuses/{status.id}")

    response = client.get(f"/api/v1/workflows/{workflow_id}/statuses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_create_workflow_transition():
    workflow_data = {"name": "Workflow Transition"}
    create_response = client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]

    status1 = setup_test_status("TODO")
    status2 = setup_test_status("IN_PROGRESS")
    _ = client.post(f"/api/v1/workflows/{workflow_id}/statuses/{status1.id}")
    _ = client.post(f"/api/v1/workflows/{workflow_id}/statuses/{status2.id}")

    transition_data = {
        "from_status_id": status1.id,
        "to_status_id": status2.id,
    }
    response = client.post(
        f"/api/v1/workflows/{workflow_id}/transitions", json=transition_data
    )
    assert response.status_code == 201


def test_create_workflow_transition_duplicate():
    workflow_data = {"name": "Workflow Transition Duplicate"}
    create_response = client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]

    status1 = setup_test_status("TODO")
    status2 = setup_test_status("DONE")
    _ = client.post(f"/api/v1/workflows/{workflow_id}/statuses/{status1.id}")
    _ = client.post(f"/api/v1/workflows/{workflow_id}/statuses/{status2.id}")

    transition_data = {
        "from_status_id": status1.id,
        "to_status_id": status2.id,
    }
    _ = client.post(
        f"/api/v1/workflows/{workflow_id}/transitions", json=transition_data
    )

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/transitions", json=transition_data
    )
    assert response.status_code == 400


def test_get_workflows_by_project():
    user = setup_test_user()
    project = setup_test_project(user.id)
    workflow_data = {"name": "Project Workflow", "project_id": project.id}
    _ = client.post("/api/v1/workflows/", json=workflow_data)

    response = client.get(f"/api/v1/workflows/?project_id={project.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
