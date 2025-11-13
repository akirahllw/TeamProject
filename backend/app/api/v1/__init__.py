from fastapi import APIRouter
from . import (
    projects,
    issues,
    users,
    auth,
    comments,
    attachments,
    boards,
    sprints,
    workflows,
    statuses,
    priorities,
    search,
)

api_router = APIRouter()

# Include all routers
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(issues.router, prefix="/issues", tags=["issues"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(
    attachments.router, prefix="/attachments", tags=["attachments"]
)
api_router.include_router(boards.router, prefix="/boards", tags=["boards"])
api_router.include_router(sprints.router, prefix="/sprints", tags=["sprints"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(statuses.router, prefix="/statuses", tags=["statuses"])
api_router.include_router(priorities.router, prefix="/priorities", tags=["priorities"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
