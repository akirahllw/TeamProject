import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db, Base
from app.models.attachment import Attachment
from app.models.issue import Issue
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()

# Configuration
UPLOAD_DIR = Path("uploads/attachments")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "document": [".pdf", ".doc", ".docx", ".txt", ".md", ".csv", ".xlsx", ".xls"],
    "archive": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "other": [".json", ".xml", ".log"]
}
ALLOWED_CONTENT_TYPES = {
    # Images
    "image/jpeg", "image/png", "image/gif", "image/bmp", "image/webp",
    # Documents
    "application/pdf", "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain", "text/markdown", "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    # Archives
    "application/zip", "application/x-tar", "application/gzip",
    "application/x-rar-compressed", "application/x-7z-compressed",
    # Other
    "application/json", "application/xml", "text/xml"
}

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Pydantic schemas
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


# Utility functions
def validate_file(file: UploadFile) -> tuple[bool, str | None]:
    """Validate file type and return (is_valid, error_message)"""
    # Check content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        return False, f"File type '{file.content_type}' not allowed"

    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    all_allowed_extensions = []
    for extensions in ALLOWED_EXTENSIONS.values():
        all_allowed_extensions.extend(extensions)

    if file_ext not in all_allowed_extensions:
        return False, f"File extension '{file_ext}' not allowed"

    return True, None


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename to prevent collisions"""
    file_ext = Path(original_filename).suffix
    unique_id = uuid.uuid4().hex
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}{file_ext}"


async def save_upload_file(file: UploadFile, destination: Path) -> int:
    """Save uploaded file and return file size"""
    file_size = 0
    with open(destination, "wb") as buffer:
        while chunk := await file.read(8192):  # Read in 8KB chunks
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                # Clean up partial file
                buffer.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
                )
            buffer.write(chunk)
    return file_size


# Routes
@router.get("/", response_model=list[AttachmentResponse])
async def get_attachments(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    issue_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all attachments with optional filtering by issue_id
    """
    query = db.query(Attachment)

    if issue_id is not None:
        # Verify the issue exists and user has access
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found"
            )
        query = query.filter(Attachment.issue_id == issue_id)

    attachments = query.offset(skip).limit(limit).all()
    return attachments


@router.get("/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(
    attachment_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get a specific attachment by ID
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    return attachment


@router.post("/", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    issue_id: int,
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Upload an attachment to an issue
    """
    # Verify the issue exists
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    # Validate file
    is_valid, error_message = validate_file(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / unique_filename

    # Save file
    try:
        file_size = await save_upload_file(file, file_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Create attachment record
    attachment = Attachment(
        issue_id=issue_id,
        uploader_id=current_user.id,
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        content_type=file.content_type
    )

    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return attachment


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Download an attachment file
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    file_path = Path(attachment.file_path)

    # Check if file exists on disk
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )

    # Return file response
    return FileResponse(
        path=file_path,
        filename=attachment.filename,
        media_type=attachment.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{attachment.filename}"'
        }
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Delete an attachment
    Only the uploader or superuser can delete an attachment
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    # Check permissions: only uploader or superuser can delete
    if attachment.uploader_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this attachment"
        )

    # Delete file from storage
    file_path = Path(attachment.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Failed to delete file {file_path}: {str(e)}")

    # Delete attachment record
    db.delete(attachment)
    db.commit()

    return None


@router.get("/statistics/summary")
async def get_attachment_statistics(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    issue_id: int | None = None
):
    """
    Get attachment statistics (total count, total size, etc.)
    """
    query = db.query(Attachment)

    if issue_id is not None:
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found"
            )
        query = query.filter(Attachment.issue_id == issue_id)

    attachments = query.all()

    total_count = len(attachments)
    total_size = sum(att.file_size for att in attachments)

    # Group by content type
    content_types = {}
    for att in attachments:
        content_type = att.content_type
        if content_type not in content_types:
            content_types[content_type] = {"count": 0, "total_size": 0}
        content_types[content_type]["count"] += 1
        content_types[content_type]["total_size"] += att.file_size

    return {
        "total_count": total_count,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "by_content_type": content_types
    }
