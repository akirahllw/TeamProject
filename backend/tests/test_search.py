"""Tests for search API endpoints"""

from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base, get_db
from app.main import app
from app.models.issue import Issue, IssuePriority, IssueStatus, IssueType
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


def setup_test_project(owner_id, key="SEARCHTEST"):
    db = TestingSessionLocal()
    try:
        project = db.query(Project).filter(Project.key == key).first()
        if not project:
            project = Project(
                name="Search Test Project",
                key=key,
                description="Test project for search",
                owner_id=owner_id,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
        return project
    finally:
        db.close()


def setup_test_issue(project_id, reporter_id, title="Test Issue"):
    db = TestingSessionLocal()
    try:
        issue = Issue(
            title=title,
            description="Test issue description",
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


def test_search_empty():
    response = client.get("/api/v1/search/?q=test")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test"
    assert isinstance(data["results"], list)


def test_search_issues():
    user = setup_test_user()
    project = setup_test_project(user.id)
    _ = setup_test_issue(project.id, user.id, "Searchable Issue Title")

    response = client.get("/api/v1/search/?q=Searchable&type=issue")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) >= 1
    assert any(r["type"] == "issue" for r in data["results"])


def test_search_projects():
    user = setup_test_user()
    setup_test_project(user.id, "SEARCHPROJ")

    response = client.get("/api/v1/search/?q=Search&type=project")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) >= 1
    assert any(r["type"] == "project" for r in data["results"])


def test_search_users():
    setup_test_user("searchuser", "search@example.com")

    response = client.get("/api/v1/search/?q=searchuser&type=user")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) >= 1
    assert any(r["type"] == "user" for r in data["results"])


def test_search_issues_endpoint():
    user = setup_test_user()
    project = setup_test_project(user.id)
    _ = setup_test_issue(project.id, user.id, "Advanced Search Issue")

    response = client.get("/api/v1/search/issues/?q=Advanced")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_search_issues_with_filters():
    user = setup_test_user()
    project = setup_test_project(user.id)
    _ = setup_test_issue(project.id, user.id, "Filtered Issue")

    response = client.get(f"/api/v1/search/issues/?q=Filtered&project_id={project.id}")
    assert response.status_code == 200
    data = response.json()
    assert all(issue["project_id"] == project.id for issue in data)


def test_search_issues_by_status():
    user = setup_test_user()
    project = setup_test_project(user.id)
    _ = setup_test_issue(project.id, user.id, "Status Issue")

    response = client.get("/api/v1/search/issues/?q=Status&status=TO_DO")
    assert response.status_code == 200
    data = response.json()
    assert all(issue["status"] == "TO_DO" for issue in data)


def test_search_projects_endpoint():
    user = setup_test_user()
    setup_test_project(user.id, "SEARCHPROJ2")

    response = client.get("/api/v1/search/projects/?q=Search")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_search_users_endpoint():
    setup_test_user("searchuser2", "search2@example.com")

    response = client.get("/api/v1/search/users/?q=searchuser2")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(u["username"] == "searchuser2" for u in data)


def test_search_pagination():
    user = setup_test_user()
    setup_test_project(user.id)

    response = client.get("/api/v1/search/?q=test&skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page_size"] == 5
    assert len(data["results"]) <= 5


def test_search_invalid_status():
    response = client.get("/api/v1/search/issues/?q=test&status=INVALID")
    assert response.status_code == 400


def test_search_min_length():
    response = client.get("/api/v1/search/?q=")
    assert response.status_code == 422
