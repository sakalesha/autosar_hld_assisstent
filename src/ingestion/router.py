from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from db.session import get_db
from src.ingestion.schemas import DocumentResponse
from src.ingestion.service import process_upload, enqueue_processing

# Create an APIRouter specifically for document-related endpoints
router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

@router.post("", response_model=DocumentResponse)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    project_id: str = Form(...),
    name: str = Form(...),
    version: str = Form(...),
    uploaded_by: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Endpoint to handle uploading a new document.
    Expects multipart/form-data containing the file and metadata.
    
    This function delegates the complex business logic (saving the file,
    validating size/type, DB insertion) to `process_upload`.
    """
    # 1. Process upload synchronously (store to disk, validate, hash, DB insert)
    doc = process_upload(
        db=db,
        file=file,
        project_id=project_id,
        name=name,
        version=version,
        uploaded_by=uploaded_by
    )
    
    # 2. Handoff to the next pipeline stage (parsing)
    # Using FastAPI BackgroundTasks allows us to return a fast response to the client
    # while the parsing and vector embedding happens asynchronously.
    background_tasks.add_task(enqueue_processing, doc.document_id)
    
    # 3. Return the registered document metadata to the client
    return doc
