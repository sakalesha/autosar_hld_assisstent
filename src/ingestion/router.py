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

@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """
    List all uploaded documents.
    """
    from db.models import Document
    
    # We query all documents, but to keep the response light, we shouldn't return 
    # the massive `file_content` binary blob here. The Pydantic DocumentResponse 
    # schema naturally excludes `file_content` if we didn't explicitly include it in the schema.
    docs = db.query(Document).all()
    return docs

@router.post("/{document_id}/reprocess")
def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Idempotent re-run of the pipeline for a specific document.
    """
    from db.models import Document
    from fastapi import HTTPException
    
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    # Re-queue the background processing
    background_tasks.add_task(enqueue_processing, document_id)
    
    return {"message": f"Reprocessing triggered for document {document_id}"}

@router.get("/{document_id}/chunks")
def get_document_chunks(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve all parsed chunks for a document to verify parsing and chunking behavior.
    """
    from db.models import Chunk
    from src.ingestion.schemas import ChunkResponse
    
    chunks = db.query(Chunk).filter(Chunk.document_id == document_id).order_by(Chunk.page_start).all()
    
    # Return directly, FastAPI will parse it into JSON automatically
    return chunks

