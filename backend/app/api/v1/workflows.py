from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


# Pydantic schemas (placeholder - will be replaced with actual models later)
class WorkflowBase(BaseModel):
    name: str
    project_id: int | None = None
    description: str | None = None


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class WorkflowResponse(WorkflowBase):
    id: int
    is_default: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=list[WorkflowResponse])
async def get_workflows(
    project_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all workflows with optional filtering
    """
    # TODO: Implement database query when models are added
    return []


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: int):
    """
    Get a specific workflow by ID
    """
    # TODO: Implement database query when models are added
    raise HTTPException(status_code=404, detail="Workflow not found")


@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(workflow: WorkflowCreate):
    """
    Create a new workflow
    """
    # TODO: Implement database insert when models are added
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(workflow_id: int, workflow: WorkflowUpdate):
    """
    Update an existing workflow
    """
    # TODO: Implement database update when models are added
    raise HTTPException(status_code=404, detail="Workflow not found")


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: int):
    """
    Delete a workflow
    """
    # TODO: Implement database delete when models are added
    raise HTTPException(status_code=404, detail="Workflow not found")


@router.get("/{workflow_id}/statuses", response_model=list[dict])
async def get_workflow_statuses(workflow_id: int):
    """
    Get all statuses in a workflow
    """
    # TODO: Implement database query when models are added
    return []


@router.post("/{workflow_id}/statuses/{status_id}", status_code=201)
async def add_status_to_workflow(
    workflow_id: int, status_id: int, position: int | None = None
):
    """
    Add a status to a workflow
    """
    # TODO: Implement status addition to workflow when models are added
    raise HTTPException(status_code=404, detail="Workflow or status not found")


@router.delete("/{workflow_id}/statuses/{status_id}", status_code=204)
async def remove_status_from_workflow(workflow_id: int, status_id: int):
    """
    Remove a status from a workflow
    """
    # TODO: Implement status removal from workflow when models are added
    raise HTTPException(status_code=404, detail="Workflow or status not found")


@router.post("/{workflow_id}/transitions", status_code=201)
async def create_workflow_transition(workflow_id: int, transition_data: dict):
    """
    Create a transition between statuses in a workflow
    """
    # TODO: Implement transition creation when models are added
    raise HTTPException(status_code=404, detail="Workflow not found")
