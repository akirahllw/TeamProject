"""Tests for boards API endpoints"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base, get_db
from app.main import app
from app.models.board import Board, BoardType
from app.models.issue import Issue, IssuePriority, IssueStatus, IssueType
from app.models.project import Project
from app.models.user import User

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_boards.db"
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
        user = db.query(User).filter(User.username == "boardtestuser").first()
        if not user:
            user = User(
                username="boardtestuser",
                email="boardtest@example.com",
                hashed_password="hashed_password_here",
                full_name="Board Test User",
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
        project = db.query(Project).filter(Project.key == "BOARDTEST").first()
        if not project:
            project = Project(
                name="Board Test Project",
                key="BOARDTEST",
                description="Test project for boards",
                owner_id=owner_id,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
        return project
    finally:
        db.close()


def setup_test_board(project_id):
    """Create a test board"""
    db = TestingSessionLocal()
    try:
        board = Board(
            name="Test Board",
            project_id=project_id,
            board_type=BoardType.KANBAN,
            description="Test board",
        )
        db.add(board)
        db.commit()
        db.refresh(board)
        return board
    finally:
        db.close()


def test_get_boards_empty():
    """Test getting boards when none exist"""
    response = client.get("/api/v1/boards/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_board():
    """Test creating a new board"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    board_data = {
        "name": "Test Board",
        "project_id": project.id,
        "board_type": "kanban",
        "description": "A test board",
    }

    response = client.post("/api/v1/boards/", json=board_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == board_data["name"]
    assert data["project_id"] == project.id
    assert data["board_type"] == board_data["board_type"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_board_scrum():
    """Test creating a scrum board"""
    user = setup_test_user()
    project = setup_test_project(user.id)

    board_data = {
        "name": "Scrum Board",
        "project_id": project.id,
        "board_type": "scrum",
        "description": "A scrum board",
    }

    response = client.post("/api/v1/boards/", json=board_data)
    assert response.status_code == 201
    data = response.json()
    assert data["board_type"] == "scrum"


def test_create_board_invalid_project():
    """Test creating a board with non-existent project"""
    board_data = {
        "name": "Test Board",
        "project_id": 99999,
        "board_type": "kanban",
    }

    response = client.post("/api/v1/boards/", json=board_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_board_by_id():
    """Test getting a board by ID"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    board = setup_test_board(project.id)

    response = client.get(f"/api/v1/boards/{board.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == board.id
    assert data["name"] == board.name


def test_get_board_not_found():
    """Test getting a non-existent board"""
    response = client.get("/api/v1/boards/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_boards_filtered_by_project():
    """Test getting boards filtered by project_id"""
    user = setup_test_user()
    project1 = setup_test_project(user.id)

    # Create another project
    db = TestingSessionLocal()
    try:
        project2 = Project(
            name="Second Project",
            key="BOARDTEST2",
            description="Second test project",
            owner_id=user.id,
        )
        db.add(project2)
        db.commit()
        db.refresh(project2)

        # Create boards for both projects
        board1 = Board(
            name="Board 1",
            project_id=project1.id,
            board_type=BoardType.KANBAN,
        )
        board2 = Board(
            name="Board 2",
            project_id=project2.id,
            board_type=BoardType.KANBAN,
        )
        db.add(board1)
        db.add(board2)
        db.commit()
        db.refresh(board1)
        db.refresh(board2)

        # Get boards for project1
        response = client.get(f"/api/v1/boards/?project_id={project1.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(b["project_id"] == project1.id for b in data)
    finally:
        db.close()


def test_update_board():
    """Test updating a board"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    board = setup_test_board(project.id)

    update_data = {
        "name": "Updated Board",
        "description": "Updated description",
        "board_type": "scrum",
    }

    response = client.put(f"/api/v1/boards/{board.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Board"
    assert data["description"] == "Updated description"
    assert data["board_type"] == "scrum"


def test_update_board_partial():
    """Test updating a board with partial data"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    board = setup_test_board(project.id)

    update_data = {"name": "Partially Updated Board"}

    response = client.put(f"/api/v1/boards/{board.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Partially Updated Board"
    # Other fields should remain unchanged
    assert data["project_id"] == project.id


def test_update_board_not_found():
    """Test updating a non-existent board"""
    update_data = {"name": "Updated Board"}
    response = client.put("/api/v1/boards/99999", json=update_data)
    assert response.status_code == 404


def test_delete_board():
    """Test deleting a board"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    board = setup_test_board(project.id)

    response = client.delete(f"/api/v1/boards/{board.id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/v1/boards/{board.id}")
    assert get_response.status_code == 404


def test_delete_board_not_found():
    """Test deleting a non-existent board"""
    response = client.delete("/api/v1/boards/99999")
    assert response.status_code == 404


def test_get_board_columns_empty():
    """Test getting columns for a board with no columns"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    board = setup_test_board(project.id)

    response = client.get(f"/api/v1/boards/{board.id}/columns")
    assert response.status_code == 200
    assert response.json() == []


def test_create_board_column():
    """Test creating a column for a board"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    board = setup_test_board(project.id)

    column_data = {
        "name": "To Do",
        "description": "Tasks to be done",
        "position": 0,
    }

    response = client.post(f"/api/v1/boards/{board.id}/columns", json=column_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == column_data["name"]
    assert data["board_id"] == board.id
    assert data["position"] == 0
    assert "id" in data
    assert "created_at" in data


def test_create_board_column_auto_position():
    """Test creating columns with auto-positioning"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    board = setup_test_board(project.id)

    # Create first column
    column1_data = {"name": "To Do", "position": 0}
    response1 = client.post(f"/api/v1/boards/{board.id}/columns", json=column1_data)
    assert response1.status_code == 201

    # Create second column without position (should auto-assign)
    column2_data = {"name": "In Progress"}
    response2 = client.post(f"/api/v1/boards/{board.id}/columns", json=column2_data)
    assert response2.status_code == 201
    data2 = response2.json()
    assert data2["position"] == 1  # Should be next position


def test_create_board_column_invalid_board():
    """Test creating a column for non-existent board"""
    column_data = {"name": "To Do"}
    response = client.post("/api/v1/boards/99999/columns", json=column_data)
    assert response.status_code == 404


def test_get_board_columns():
    """Test getting all columns for a board"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    board = setup_test_board(project.id)

    # Create multiple columns
    columns_data = [
        {"name": "To Do", "position": 0},
        {"name": "In Progress", "position": 1},
        {"name": "Done", "position": 2},
    ]

    for col_data in columns_data:
        client.post(f"/api/v1/boards/{board.id}/columns", json=col_data)

    response = client.get(f"/api/v1/boards/{board.id}/columns")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Check that columns are ordered by position
    positions = [col["position"] for col in data]
    assert positions == sorted(positions)


def test_get_board_columns_invalid_board():
    """Test getting columns for non-existent board"""
    response = client.get("/api/v1/boards/99999/columns")
    assert response.status_code == 404


def test_get_board_issues():
    """Test getting issues for a board"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    board = setup_test_board(project.id)

    # Create some issues for the project
    db = TestingSessionLocal()
    try:
        issue1 = Issue(
            title="Test Issue 1",
            description="First issue",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        issue2 = Issue(
            title="Test Issue 2",
            description="Second issue",
            status=IssueStatus.IN_PROGRESS,
            priority=IssuePriority.HIGH,
            issue_type=IssueType.BUG,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue1)
        db.add(issue2)
        db.commit()
        db.refresh(issue1)
        db.refresh(issue2)

        response = client.get(f"/api/v1/boards/{board.id}/issues")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(issue["project_id"] == project.id for issue in data)
    finally:
        db.close()


def test_get_board_issues_filtered_by_column():
    """Test getting issues filtered by column"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    board = setup_test_board(project.id)

    # Create a column
    column_data = {"name": "TO_DO", "position": 0}
    column_response = client.post(
        f"/api/v1/boards/{board.id}/columns", json=column_data
    )
    column_id = column_response.json()["id"]

    # Create issues with different statuses
    db = TestingSessionLocal()
    try:
        issue_todo = Issue(
            title="To Do Issue",
            description="Issue in to do",
            status=IssueStatus.TO_DO,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        issue_in_progress = Issue(
            title="In Progress Issue",
            description="Issue in progress",
            status=IssueStatus.IN_PROGRESS,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.TASK,
            project_id=project.id,
            reporter_id=user.id,
        )
        db.add(issue_todo)
        db.add(issue_in_progress)
        db.commit()

        # Get issues filtered by column (should match TO_DO status)
        response = client.get(f"/api/v1/boards/{board.id}/issues?column_id={column_id}")
        assert response.status_code == 200
        data = response.json()
        # Should only return TO_DO issues
        assert all(issue["status"] == "TO_DO" for issue in data)
    finally:
        db.close()


def test_get_board_issues_invalid_board():
    """Test getting issues for non-existent board"""
    response = client.get("/api/v1/boards/99999/issues")
    assert response.status_code == 404


def test_get_board_issues_invalid_column():
    """Test getting issues with invalid column_id"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    board = setup_test_board(project.id)

    response = client.get(f"/api/v1/boards/{board.id}/issues?column_id=99999")
    assert response.status_code == 404


def test_get_board_issues_pagination():
    """Test pagination for board issues"""
    user = setup_test_user()
    project = setup_test_project(user.id)
    board = setup_test_board(project.id)

    # Create multiple issues
    db = TestingSessionLocal()
    try:
        for i in range(5):
            issue = Issue(
                title=f"Issue {i}",
                description=f"Description {i}",
                status=IssueStatus.TO_DO,
                priority=IssuePriority.MEDIUM,
                issue_type=IssueType.TASK,
                project_id=project.id,
                reporter_id=user.id,
            )
            db.add(issue)
        db.commit()

        # Test pagination
        response = client.get(f"/api/v1/boards/{board.id}/issues?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

        response2 = client.get(f"/api/v1/boards/{board.id}/issues?skip=2&limit=2")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) <= 2
    finally:
        db.close()
