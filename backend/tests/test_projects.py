"""Tests for projects API endpoints"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base, get_db
from app.main import app
from app.models.user import User

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def setup_test_user():
    """Create a test user for testing"""
    db = TestingSessionLocal()
    try:
        # Check if user already exists
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            user = User(
                username="testuser",
                email="test@example.com",
                hashed_password="hashed_password_here",  # In real tests, hash properly
                full_name="Test User",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


def test_get_projects_empty():
    """Test getting projects when none exist"""
    response = client.get("/api/v1/projects/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_project():
    """Test creating a new project"""
    # First, create a test user
    user = setup_test_user()

    project_data = {
        "name": "Test Project",
        "key": "TEST",
        "description": "A test project",
        "owner_id": user.id,
    }

    response = client.post("/api/v1/projects/", json=project_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == project_data["name"]
    assert data["key"] == project_data["key"]
    assert data["owner_id"] == user.id
    assert "id" in data


def test_create_project_duplicate_key():
    """Test creating a project with duplicate key"""
    user = setup_test_user()

    project_data = {
        "name": "Test Project",
        "key": "TESTDUP",
        "description": "A test project",
        "owner_id": user.id,
    }

    # Create first project
    response1 = client.post("/api/v1/projects/", json=project_data)
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = client.post("/api/v1/projects/", json=project_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


def test_get_project_by_id():
    """Test getting a project by ID"""
    user = setup_test_user()

    # Create a project
    project_data = {
        "name": "Test Project",
        "key": "TEST2",
        "description": "A test project",
        "owner_id": user.id,
    }
    create_response = client.post("/api/v1/projects/", json=project_data)
    project_id = create_response.json()["id"]

    # Get the project
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == project_data["name"]


def test_get_project_not_found():
    """Test getting a non-existent project"""
    response = client.get("/api/v1/projects/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_project():
    """Test updating a project"""
    user = setup_test_user()

    # Create a project
    project_data = {
        "name": "Test Project",
        "key": "TEST3",
        "description": "Original description",
        "owner_id": user.id,
    }
    create_response = client.post("/api/v1/projects/", json=project_data)
    project_id = create_response.json()["id"]

    # Update the project
    update_data = {"name": "Updated Project", "description": "Updated description"}
    response = client.put(f"/api/v1/projects/{project_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project"
    assert data["description"] == "Updated description"


def test_delete_project():
    """Test deleting a project"""
    user = setup_test_user()

    # Create a project
    project_data = {
        "name": "Test Project",
        "key": "TEST4",
        "description": "A test project",
        "owner_id": user.id,
    }
    create_response = client.post("/api/v1/projects/", json=project_data)
    project_id = create_response.json()["id"]

    # Delete the project
    response = client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_response.status_code == 404


def test_get_project_stats():
    """Test getting project statistics"""
    user = setup_test_user()

    # Create a project
    project_data = {
        "name": "Test Project",
        "key": "TEST5",
        "description": "A test project",
        "owner_id": user.id,
    }
    create_response = client.post("/api/v1/projects/", json=project_data)
    project_id = create_response.json()["id"]

    # Get stats
    response = client.get(f"/api/v1/projects/{project_id}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == project_id
    assert "total_issues" in data
    assert "open_issues" in data
    assert "done_issues" in data
    assert "total_members" in data
