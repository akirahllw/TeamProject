from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.project import Project
from app.models.status import Status
from app.models.workflow import Workflow, WorkflowStatus, WorkflowTransition

router = APIRouter()


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


class WorkflowStatusResponse(BaseModel):
    id: int
    workflow_id: int
    status_id: int
    status_name: str
    position: int

    class Config:
        from_attributes = True


class WorkflowTransitionCreate(BaseModel):
    from_status_id: int
    to_status_id: int


@router.get("/", response_model=list[WorkflowResponse])
async def get_workflows(
    project_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get all workflows with optional filtering
    """
    query = db.query(Workflow)

    if project_id:
        query = query.filter(Workflow.project_id == project_id)

    workflows = query.offset(skip).limit(limit).all()
    return workflows


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """
    Get a specific workflow by ID
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    """
    Create a new workflow
    """
    if workflow.project_id:
        project = db.query(Project).filter(Project.id == workflow.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        project_id=workflow.project_id,
        is_default=False,
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)

    return db_workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int, workflow: WorkflowUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing workflow
    """
    db_workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.name is not None:
        db_workflow.name = workflow.name

    if workflow.description is not None:
        db_workflow.description = workflow.description

    db.commit()
    db.refresh(db_workflow)
    return db_workflow


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """
    Delete a workflow
    """
    db_workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    db.delete(db_workflow)
    db.commit()
    return None


@router.get("/{workflow_id}/statuses", response_model=list[WorkflowStatusResponse])
async def get_workflow_statuses(workflow_id: int, db: Session = Depends(get_db)):
    """
    Get all statuses in a workflow
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow_statuses = (
        db.query(WorkflowStatus)
        .filter(WorkflowStatus.workflow_id == workflow_id)
        .order_by(WorkflowStatus.position)
        .all()
    )

    result = []
    for ws in workflow_statuses:
        status = db.query(Status).filter(Status.id == ws.status_id).first()
        result.append(
            {
                "id": ws.id,
                "workflow_id": ws.workflow_id,
                "status_id": ws.status_id,
                "status_name": status.name if status else "Unknown",
                "position": ws.position,
            }
        )

    return result


@router.post("/{workflow_id}/statuses/{status_id}", status_code=201)
async def add_status_to_workflow(
    workflow_id: int,
    status_id: int,
    position: int | None = Query(None),
    db: Session = Depends(get_db),
):
    """
    Add a status to a workflow
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    status = db.query(Status).filter(Status.id == status_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    existing = (
        db.query(WorkflowStatus)
        .filter(
            WorkflowStatus.workflow_id == workflow_id,
            WorkflowStatus.status_id == status_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Status is already in this workflow"
        )

    if position is None:
        max_position = (
            db.query(WorkflowStatus)
            .filter(WorkflowStatus.workflow_id == workflow_id)
            .order_by(WorkflowStatus.position.desc())
            .first()
        )
        position = (max_position.position + 1) if max_position else 0

    workflow_status = WorkflowStatus(
        workflow_id=workflow_id, status_id=status_id, position=position
    )
    db.add(workflow_status)
    db.commit()
    db.refresh(workflow_status)

    return {
        "message": "Status added to workflow successfully",
        "workflow_status_id": workflow_status.id,
    }


@router.delete("/{workflow_id}/statuses/{status_id}", status_code=204)
async def remove_status_from_workflow(
    workflow_id: int, status_id: int, db: Session = Depends(get_db)
):
    """
    Remove a status from a workflow
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow_status = (
        db.query(WorkflowStatus)
        .filter(
            WorkflowStatus.workflow_id == workflow_id,
            WorkflowStatus.status_id == status_id,
        )
        .first()
    )
    if not workflow_status:
        raise HTTPException(status_code=404, detail="Status is not in this workflow")

    db.delete(workflow_status)
    db.commit()
    return None


@router.post("/{workflow_id}/transitions", status_code=201)
async def create_workflow_transition(
    workflow_id: int,
    transition: WorkflowTransitionCreate,
    db: Session = Depends(get_db),
):
    """
    Create a transition between statuses in a workflow
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    from_status = (
        db.query(Status).filter(Status.id == transition.from_status_id).first()
    )
    to_status = db.query(Status).filter(Status.id == transition.to_status_id).first()

    if not from_status:
        raise HTTPException(status_code=404, detail="From status not found")
    if not to_status:
        raise HTTPException(status_code=404, detail="To status not found")

    from_ws = (
        db.query(WorkflowStatus)
        .filter(
            WorkflowStatus.workflow_id == workflow_id,
            WorkflowStatus.status_id == transition.from_status_id,
        )
        .first()
    )
    to_ws = (
        db.query(WorkflowStatus)
        .filter(
            WorkflowStatus.workflow_id == workflow_id,
            WorkflowStatus.status_id == transition.to_status_id,
        )
        .first()
    )

    if not from_ws:
        raise HTTPException(
            status_code=400,
            detail="From status is not in this workflow",
        )
    if not to_ws:
        raise HTTPException(
            status_code=400,
            detail="To status is not in this workflow",
        )

    existing = (
        db.query(WorkflowTransition)
        .filter(
            WorkflowTransition.workflow_id == workflow_id,
            WorkflowTransition.from_status_id == transition.from_status_id,
            WorkflowTransition.to_status_id == transition.to_status_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="This transition already exists")

    transition_obj = WorkflowTransition(
        workflow_id=workflow_id,
        from_status_id=transition.from_status_id,
        to_status_id=transition.to_status_id,
    )
    db.add(transition_obj)
    db.commit()
    db.refresh(transition_obj)

    return {
        "message": "Transition created successfully",
        "transition_id": transition_obj.id,
    }
