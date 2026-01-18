"""Tests for issues API endpoints"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base, get_db
from app.main import app
from app.models.issue import Issue, IssuePriority, IssueStatus, IssueType
from app.models.project import Project
from app.models.user import User

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_issues.db"
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
        user = db.query(User).filter(User.username == "issuetestuser").first()
        if not user:
            user = User(
                username="issuetestuser",
                email="issuetest@example.com",
                hashed_password="hashed_password_here",
                full_name="Issue Test User",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


def setup_test_project(owner_id):
    """Create a test project"""
    db = TestingSessionLocal()
    try:
        project = db.query(Project).filter(Project.key == "ISSUETEST").first()
        if not project:
            project = Project(
                name="Issue Test Project",
                key="ISSUETEST",
                description="Test project for issues",
                owner_id=owner_id,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
        return project
    finally:
        db.close()


def test_get_issues_empty():
    """Test getting issues when none exist"""
    response = client.get("/api/v1/issues/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_issue():
    """Test creating a new issue"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    issue_data = {
        "title": "Test Issue",
        "description": "This is a test issue",
        "issue_type": "TASK",
        "priority": "MEDIUM",
        "project_id": project.id,
        "reporter_id": user.id,
    }

    response = client.post("/api/v1/issues/", json=issue_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == issue_data["title"]
    assert data["project_id"] == project.id
    assert data["reporter_id"] == user.id
    assert data["issue_type"] == "TASK"
    assert data["priority"] == "MEDIUM"
    assert data["status"] == "TO_DO"  # Default status
    assert "id" in data
    assert "key" in data
    assert data["key"] == f"{project.key}-{data['id']}"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_issue_invalid_project():
    """Test creating an issue with non-existent project"""
    user = setup_test_user()

    issue_data = {
        "title": "Test Issue",
        "issue_type": "TASK",
        "priority": "MEDIUM",
        "project_id": 99999,
        "reporter_id": user.id,
    }

    response = client.post("/api/v1/issues/", json=issue_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_issue_invalid_reporter():
    """Test creating an issue with non-existent reporter"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    issue_data = {
        "title": "Test Issue",
        "issue_type": "TASK",
        "priority": "MEDIUM",
        "project_id": project.id,
        "reporter_id": 99999,
    }

    response = client.post("/api/v1/issues/", json=issue_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_issue_by_id():
    """Test getting an issue by ID"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    # Create an issue
    db = TestingSessionLocal()
    try:
        issue = Issue(
            title="Test Issue",
            description="Test issue description",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)

        response = client.get(f"/api/v1/issues/{issue.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == issue.id
        assert data["title"] == issue.title
        assert data["key"] == f"{project.key}-{issue.id}"
    finally:
        db.close()


def test_get_issue_not_found():
    """Test getting a non-existent issue"""
    response = client.get("/api/v1/issues/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_issue_by_key():
    """Test getting an issue by key"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    # Create an issue
    db = TestingSessionLocal()
    try:
        issue = Issue(
            title="Test Issue",
            description="Test issue description",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)

        issue_key = f"{project.key}-{issue.id}"
        response = client.get(f"/api/v1/issues/key/{issue_key}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == issue.id
        assert data["key"] == issue_key
    finally:
        db.close()


def test_get_issue_by_key_invalid_format():
    """Test getting an issue with invalid key format"""
    response = client.get("/api/v1/issues/key/INVALID")
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


def test_get_issue_by_key_not_found():
    """Test getting an issue with non-existent key"""
    response = client.get("/api/v1/issues/key/INVALID-99999")
    assert response.status_code == 404


def test_get_issues_filtered_by_project():
    """Test getting issues filtered by project_id"""
    user = setup_test_user()
    project1 = setup_test_project(user.id)

    # Create another project
    db = TestingSessionLocal()
    try:
        project2 = Project(
            name="Second Project",
            key="ISSUETEST2",
            description="Second test project",
            owner_id=user.id,
        )
        db.add(project2)
        db.commit()
        db.refresh(project2)

        # Create issues for both projects
        issue1 = Issue(
            title="Issue 1",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project1.id,
            reporter_id=user.id,
        )
        issue2 = Issue(
            title="Issue 2",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project2.id,
            reporter_id=user.id,
        )
        db.add(issue1)
        db.add(issue2)
        db.commit()
        db.refresh(issue1)
        db.refresh(issue2)

        # Get issues for project1
        response = client.get(f"/api/v1/issues/?project_id={project1.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(i["project_id"] == project1.id for i in data)
    finally:
        db.close()


def test_get_issues_filtered_by_status():
    """Test getting issues filtered by status"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    # Create issues with different statuses
    db = TestingSessionLocal()
    try:
        issue1 = Issue(
            title="To Do Issue",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        issue2 = Issue(
            title="In Progress Issue",
            status=IssueStatus.IN_PROGRESS,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue1)
        db.add(issue2)
        db.commit()

        # Get TO_DO issues
        response = client.get("/api/v1/issues/?status=TO_DO")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(i["status"] == "TO_DO" for i in data)
    finally:
        db.close()


def test_get_issues_search():
    """Test searching issues by title/description"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    # Create issues
    db = TestingSessionLocal()
    try:
        issue1 = Issue(
            title="Bug Fix",
            description="Fix the critical bug",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.HIGH,
            issue_type=IssueType.BUG,
            project_id=project.id,
            reporter_id=user.id,
        )
        issue2 = Issue(
            title="New Feature",
            description="Add new feature",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue1)
        db.add(issue2)
        db.commit()

        # Search for "bug"
        response = client.get("/api/v1/issues/?search=bug")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any("bug" in i["title"].lower() or "bug" in (i.get("description") or "").lower() for i in data)
    finally:
        db.close()


def test_update_issue():
    """Test updating an issue"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    # Create an issue
    db = TestingSessionLocal()
    try:
        issue = Issue(
            title="Original Title",
            description="Original description",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)

        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "priority": "HIGH",
        }

        response = client.put(f"/api/v1/issues/{issue.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert data["priority"] == "HIGH"
    finally:
        db.close()


def test_update_issue_not_found():
    """Test updating a non-existent issue"""
    update_data = {"title": "Updated Title"}
    response = client.put("/api/v1/issues/99999", json=update_data)
    assert response.status_code == 404


def test_assign_issue():
    """Test assigning an issue to a user"""
    user1 = setup_test_user()
    project = setup_test_project(user1.id)

    # Create another user
    db = TestingSessionLocal()
    try:
        user2 = User(
            username="issuetestuser2",
            email="issuetest2@example.com",
            hashed_password="hashed_password_here",
            full_name="Issue Test User 2",
            is_active=True,
        )
        db.add(user2)
        db.commit()
        db.refresh(user2)

        issue = Issue(
            title="Test Issue",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user1.id,
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)

        assign_data = {"assignee_id": user2.id}
        response = client.patch(f"/api/v1/issues/{issue.id}/assign", json=assign_data)
        assert response.status_code == 200
        data = response.json()
        assert data["assignee_id"] == user2.id
    finally:
        db.close()


def test_assign_issue_invalid_assignee():
    """Test assigning an issue to non-existent user"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    # Create an issue
    db = TestingSessionLocal()
    try:
        issue = Issue(
            title="Test Issue",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)

        assign_data = {"assignee_id": 99999}
        response = client.patch(f"/api/v1/issues/{issue.id}/assign", json=assign_data)
        assert response.status_code == 404
    finally:
        db.close()


def test_update_issue_status():
    """Test updating issue status"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    # Create an issue
    db = TestingSessionLocal()
    try:
        issue = Issue(
            title="Test Issue",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)

        status_data = {"status": "IN_PROGRESS"}
        response = client.patch(f"/api/v1/issues/{issue.id}/status", json=status_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "IN_PROGRESS"
    finally:
        db.close()


def test_update_issue_priority():
    """Test updating issue priority"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    # Create an issue
    db = TestingSessionLocal()
    try:
        issue = Issue(
            title="Test Issue",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)

        priority_data = {"priority": "HIGH"}
        response = client.patch(
            f"/api/v1/issues/{issue.id}/priority", json=priority_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "HIGH"
    finally:
        db.close()


def test_delete_issue():
    """Test deleting an issue"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    # Create an issue
    db = TestingSessionLocal()
    try:
        issue = Issue(
            title="Issue to delete",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)

        response = client.delete(f"/api/v1/issues/{issue.id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/v1/issues/{issue.id}")
        assert get_response.status_code == 404
    finally:
        db.close()


def test_delete_issue_not_found():
    """Test deleting a non-existent issue"""
    response = client.delete("/api/v1/issues/99999")
    assert response.status_code == 404


def test_get_issue_comments():
    """Test getting comments for an issue"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    # Create an issue with comments
    db = TestingSessionLocal()
    try:
        from app.models.issue import Comment

        issue = Issue(
            title="Test Issue",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)

        comment1 = Comment(
            body="First comment",
            issue_id=issue.id,
            author_id=user.id,
        )
        comment2 = Comment(
            body="Second comment",
            issue_id=issue.id,
            author_id=user.id,
        )
        db.add(comment1)
        db.add(comment2)
        db.commit()

        response = client.get(f"/api/v1/issues/{issue.id}/comments")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(c["issue_id"] == issue.id for c in data)
    finally:
        db.close()


def test_get_issue_comments_not_found():
    """Test getting comments for non-existent issue"""
    response = client.get("/api/v1/issues/99999/comments")
    assert response.status_code == 404


def test_create_issue_with_parent():
    """Test creating an issue with a parent issue"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    # Create parent issue
    db = TestingSessionLocal()
    try:
        parent_issue = Issue(
            title="Parent Issue",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.EPIC,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(parent_issue)
        db.commit()
        db.refresh(parent_issue)

        # Create child issue
        child_data = {
            "title": "Child Issue",
            "issue_type": "TASK",
            "priority": "MEDIUM",
            "project_id": project.id,
            "reporter_id": user.id,
            "parent_issue_id": parent_issue.id,
        }

        response = client.post("/api/v1/issues/", json=child_data)
        assert response.status_code == 201
        data = response.json()
        assert data["parent_issue_id"] == parent_issue.id
    finally:
        db.close()


def test_create_issue_invalid_parent():
    """Test creating an issue with invalid parent"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    issue_data = {
        "title": "Child Issue",
        "issue_type": "TASK",
        "priority": "MEDIUM",
        "project_id": project.id,
        "reporter_id": user.id,
        "parent_issue_id": 99999,
    }

    response = client.post("/api/v1/issues/", json=issue_data)
    assert response.status_code == 404


def test_get_issues_pagination():
    """Test pagination for issues"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    # Create multiple issues
    db = TestingSessionLocal()
    try:
        for i in range(5):
            issue = Issue(
                title=f"Issue {i}",
                status=IssueStatus.TO_DO,
                priority=IssuePriority.MEDIUM,
                issue_type=IssueType.TASK,
                project_id=project.id,
                reporter_id=user.id,
            )
            db.add(issue)
        db.commit()

        # Test pagination
        response = client.get("/api/v1/issues/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

        response2 = client.get("/api/v1/issues/?skip=2&limit=2")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) <= 2
    finally:
        db.close()

