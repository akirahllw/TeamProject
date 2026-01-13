"""Pytest fixtures for testing - shared across all test files"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base, get_db
from app.main import app
from app.models.board import Board, BoardColumn, BoardType
from app.models.issue import Issue, IssuePriority, IssueStatus, IssueType
from app.models.project import Project
from app.models.sprint import Sprint, SprintStatus
from app.models.status import Status, StatusCategory
from app.models.user import User
from app.models.workflow import Workflow

# Use in-memory database for better test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override the get_db dependency"""

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    return _override_get_db


@pytest.fixture(scope="function")
def client(override_get_db):
    """Create a test client with database override"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user"""
    # Clean up any existing test user
    db_session.query(User).filter(User.username == "testuser").delete()
    db_session.commit()

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=pwd_context.hash("testpass123"),
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_user_custom(db_session):
    """Create a test user with custom parameters"""

    def _create_user(
        username="testuser", email="test@example.com", password="testpass123"
    ):
        # Clean up any existing user with this username
        db_session.query(User).filter(User.username == username).delete()
        db_session.commit()

        user = User(
            username=username,
            email=email,
            hashed_password=pwd_context.hash(password),
            full_name=f"{username} User",
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture(scope="function")
def test_project(db_session, test_user):
    """Create a test project"""

    def _create_project(
        name="Test Project", key="TEST", description="Test project", owner_id=None
    ):
        if owner_id is None:
            owner_id = test_user.id

        # Clean up any existing project with this key
        db_session.query(Project).filter(Project.key == key).delete()
        db_session.commit()

        project = Project(
            name=name,
            key=key,
            description=description,
            owner_id=owner_id,
        )
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        return project

    return _create_project


@pytest.fixture(scope="function")
def test_status(db_session):
    """Create a test status"""

    def _create_status(
        name="Test Status",
        category=StatusCategory.TODO,
        color="#FF0000",
        project_id=None,
    ):
        status = Status(
            name=name,
            category=category,
            color=color,
            project_id=project_id,
        )
        db_session.add(status)
        db_session.commit()
        db_session.refresh(status)
        return status

    return _create_status


@pytest.fixture(scope="function")
def test_issue(db_session):
    """Create a test issue"""

    def _create_issue(
        project_id,
        reporter_id,
        title="Test Issue",
        description="Test issue description",
        status=IssueStatus.TO_DO,
        priority=IssuePriority.MEDIUM,
        issue_type=IssueType.TASK,
        assignee_id=None,
        sprint_id=None,
    ):
        issue = Issue(
            title=title,
            description=description,
            status=status,
            priority=priority,
            issue_type=issue_type,
            project_id=project_id,
            reporter_id=reporter_id,
            assignee_id=assignee_id,
            sprint_id=sprint_id,
        )
        db_session.add(issue)
        db_session.commit()
        db_session.refresh(issue)
        return issue

    return _create_issue


@pytest.fixture(scope="function")
def test_sprint(db_session):
    """Create a test sprint"""

    def _create_sprint(
        project_id,
        name="Test Sprint",
        start_date=None,
        end_date=None,
        goal="Test sprint goal",
        status=SprintStatus.PLANNED,
    ):
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=14)

        sprint = Sprint(
            name=name,
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
            goal=goal,
            status=status,
        )
        db_session.add(sprint)
        db_session.commit()
        db_session.refresh(sprint)
        return sprint

    return _create_sprint


@pytest.fixture(scope="function")
def test_workflow(db_session):
    """Create a test workflow"""

    def _create_workflow(
        name="Test Workflow", description="Test workflow", project_id=None
    ):
        workflow = Workflow(
            name=name,
            description=description,
            project_id=project_id,
        )
        db_session.add(workflow)
        db_session.commit()
        db_session.refresh(workflow)
        return workflow

    return _create_workflow


@pytest.fixture(scope="function")
def test_board(db_session):
    """Create a test board"""

    def _create_board(
        project_id,
        name="Test Board",
        board_type=BoardType.KANBAN,
        description="Test board description",
    ):
        board = Board(
            name=name,
            project_id=project_id,
            board_type=board_type,
            description=description,
        )
        db_session.add(board)
        db_session.commit()
        db_session.refresh(board)
        return board

    return _create_board


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    response = client.post(
        "/api/v1/auth/login", data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
