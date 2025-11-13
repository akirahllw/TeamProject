from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# Pydantic schemas (placeholder - will be replaced with actual models later)
class AttachmentBase(BaseModel):
    issue_id: int
    filename: str
    file_size: int
    content_type: str


class AttachmentResponse(AttachmentBase):
    id: int
    uploader_id: int
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AttachmentResponse])
async def get_attachments(
    issue_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all attachments with optional filtering
    """
    # TODO: Implement database query when models are added
    return []


@router.get("/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(attachment_id: int):
    """
    Get a specific attachment by ID
    """
    # TODO: Implement database query when models are added
    raise HTTPException(status_code=404, detail="Attachment not found")


@router.post("/", response_model=AttachmentResponse, status_code=201)
async def upload_attachment(
    issue_id: int,
    file: UploadFile = File(...),
):
    """
    Upload an attachment to an issue
    """
    # TODO: Implement file upload when models are added
    # 1. Validate file type and size
    # 2. Save file to storage
    # 3. Create attachment record in database
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{attachment_id}/download")
async def download_attachment(attachment_id: int):
    """
    Download an attachment file
    """
    # TODO: Implement file download when models are added
    # 1. Get attachment record
    # 2. Read file from storage
    # 3. Return file response
    raise HTTPException(status_code=404, detail="Attachment not found")


@router.delete("/{attachment_id}", status_code=204)
async def delete_attachment(attachment_id: int):
    """
    Delete an attachment
    """
    # TODO: Implement file deletion when models are added
    # 1. Get attachment record
    # 2. Delete file from storage
    # 3. Delete attachment record
    raise HTTPException(status_code=404, detail="Attachment not found")
