"""Tests for comments API endpoints"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base, get_db
from app.main import app
from app.models.issue import Comment, Issue, IssuePriority, IssueStatus, IssueType
from app.models.project import Project
from app.models.user import User

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_comments.db"
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
        user = db.query(User).filter(User.username == "commenttestuser").first()
        if not user:
            user = User(
                username="commenttestuser",
                email="commenttest@example.com",
                hashed_password="hashed_password_here",
                full_name="Comment Test User",
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
        project = db.query(Project).filter(Project.key == "COMMENTTEST").first()
        if not project:
            project = Project(
                name="Comment Test Project",
                key="COMMENTTEST",
                description="Test project for comments",
                owner_id=owner_id,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
        return project
    finally:
        db.close()


def setup_test_issue(project_id, reporter_id):
    """Create a test issue"""
    db = TestingSessionLocal()
    try:
        issue = Issue(
            title="Test Issue",
            description="Test issue for comments",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project_id,
            reporter_id=reporter_id,
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)
        return issue
    finally:
        db.close()


def test_get_comments_empty():
    """Test getting comments when none exist"""
    response = client.get("/api/v1/comments/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_comment():
    """Test creating a new comment"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    issue = setup_test_issue(project.id, user.id)

    comment_data = {
        "body": "This is a test comment",
        "issue_id": issue.id,
    }

    response = client.post(
        f"/api/v1/comments/?author_id={user.id}", json=comment_data
    )
    assert response.status_code == 201
    data = response.json()
    assert data["body"] == comment_data["body"]
    assert data["issue_id"] == issue.id
    assert data["author_id"] == user.id
    assert "id" in data
    assert "created_at" in data


def test_create_comment_invalid_issue():
    """Test creating a comment with non-existent issue"""
    user = setup_test_user()

    comment_data = {
        "body": "This is a test comment",
        "issue_id": 99999,
    }

    response = client.post(
        f"/api/v1/comments/?author_id={user.id}", json=comment_data
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_comment_by_id():
    """Test getting a comment by ID"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    issue = setup_test_issue(project.id, user.id)

    # Create a comment
    db = TestingSessionLocal()
    try:
        comment = Comment(
            body="Test comment",
            issue_id=issue.id,
            author_id=user.id,
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)

        response = client.get(f"/api/v1/comments/{comment.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == comment.id
        assert data["body"] == comment.body
        assert data["author_id"] == user.id
    finally:
        db.close()


def test_get_comment_not_found():
    """Test getting a non-existent comment"""
    response = client.get("/api/v1/comments/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_comments_filtered_by_issue():
    """Test getting comments filtered by issue_id"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    issue1 = setup_test_issue(project.id, user.id)

    # Create another issue
    db = TestingSessionLocal()
    try:
        issue2 = Issue(
            title="Second Issue",
            description="Second test issue",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue2)
        db.commit()
        db.refresh(issue2)

        # Create comments for both issues
        comment1 = Comment(
            body="Comment on issue 1",
            issue_id=issue1.id,
            author_id=user.id,
        )
        comment2 = Comment(
            body="Comment on issue 2",
            issue_id=issue2.id,
            author_id=user.id,
        )
        db.add(comment1)
        db.add(comment2)
        db.commit()
        db.refresh(comment1)
        db.refresh(comment2)

        # Get comments for issue1
        response = client.get(f"/api/v1/comments/?issue_id={issue1.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(c["issue_id"] == issue1.id for c in data)
    finally:
        db.close()


def test_get_comments_filtered_by_author():
    """Test getting comments filtered by author_id"""
    user1 = setup_test_user()

    # Create another user
    db = TestingSessionLocal()
    try:
        user2 = User(
            username="commenttestuser2",
            email="commenttest2@example.com",
            hashed_password="hashed_password_here",
            full_name="Comment Test User 2",
            is_active=True,
        )
        db.add(user2)
        db.commit()
        db.refresh(user2)

        project = setup_test_project(user1.id)
        issue = setup_test_issue(project.id, user1.id)

        # Create comments by both users
        comment1 = Comment(
            body="Comment by user 1",
            issue_id=issue.id,
            author_id=user1.id,
        )
        comment2 = Comment(
            body="Comment by user 2",
            issue_id=issue.id,
            author_id=user2.id,
        )
        db.add(comment1)
        db.add(comment2)
        db.commit()
        db.refresh(comment1)
        db.refresh(comment2)

        # Get comments by user1
        response = client.get(f"/api/v1/comments/?author_id={user1.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(c["author_id"] == user1.id for c in data)
    finally:
        db.close()


def test_get_comments_pagination():
    """Test pagination for comments"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    issue = setup_test_issue(project.id, user.id)

    # Create multiple comments
    db = TestingSessionLocal()
    try:
        for i in range(5):
            comment = Comment(
                body=f"Comment {i}",
                issue_id=issue.id,
                author_id=user.id,
            )
            db.add(comment)
        db.commit()

        # Test pagination
        response = client.get(f"/api/v1/comments/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

        response2 = client.get(f"/api/v1/comments/?skip=2&limit=2")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) <= 2
    finally:
        db.close()


def test_update_comment():
    """Test updating a comment"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    issue = setup_test_issue(project.id, user.id)

    # Create a comment
    db = TestingSessionLocal()
    try:
        comment = Comment(
            body="Original comment",
            issue_id=issue.id,
            author_id=user.id,
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)

        update_data = {"body": "Updated comment"}

        response = client.put(f"/api/v1/comments/{comment.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["body"] == "Updated comment"
        assert data["id"] == comment.id
    finally:
        db.close()


def test_update_comment_not_found():
    """Test updating a non-existent comment"""
    update_data = {"body": "Updated comment"}
    response = client.put("/api/v1/comments/99999", json=update_data)
    assert response.status_code == 404


def test_delete_comment():
    """Test deleting a comment"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    issue = setup_test_issue(project.id, user.id)

    # Create a comment
    db = TestingSessionLocal()
    try:
        comment = Comment(
            body="Comment to delete",
            issue_id=issue.id,
            author_id=user.id,
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)

        response = client.delete(f"/api/v1/comments/{comment.id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/v1/comments/{comment.id}")
        assert get_response.status_code == 404
    finally:
        db.close()


def test_delete_comment_not_found():
    """Test deleting a non-existent comment"""
    response = client.delete("/api/v1/comments/99999")
    assert response.status_code == 404


def test_get_comments_multiple_filters():
    """Test getting comments with multiple filters"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    issue1 = setup_test_issue(project.id, user.id)
    issue2 = setup_test_issue(project.id, user.id)

    # Create another user
    db = TestingSessionLocal()
    try:
        user2 = User(
            username="commenttestuser3",
            email="commenttest3@example.com",
            hashed_password="hashed_password_here",
            full_name="Comment Test User 3",
            is_active=True,
        )
        db.add(user2)
        db.commit()
        db.refresh(user2)

        # Create comments
        comment1 = Comment(
            body="Comment 1 by user1 on issue1",
            issue_id=issue1.id,
            author_id=user.id,
        )
        comment2 = Comment(
            body="Comment 2 by user2 on issue1",
            issue_id=issue1.id,
            author_id=user2.id,
        )
        comment3 = Comment(
            body="Comment 3 by user1 on issue2",
            issue_id=issue2.id,
            author_id=user.id,
        )
        db.add(comment1)
        db.add(comment2)
        db.add(comment3)
        db.commit()

        # Get comments by user1 on issue1
        response = client.get(
            f"/api/v1/comments/?issue_id={issue1.id}&author_id={user.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(
            c["issue_id"] == issue1.id and c["author_id"] == user.id for c in data
        )
    finally:
        db.close()

