import uuid
import hashlib
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import Document
from config.settings import settings

def process_upload(
    db: Session,
    file: UploadFile,
    project_id: str,
    name: str,
    version: str,
    uploaded_by: str = None
) -> Document:
    """
    Core business logic for handling a document upload.
    1. Validates the file extension.
    2. Checks the database for existing duplicates (project + name + version).
    3. Validates the PDF signature in-memory.
    4. Hashes the file and enforces size limits in-memory.
    5. Saves the metadata and file content directly to the database.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only .pdf files are allowed.")
    
    # 2. Check if this document version already exists in the database
    existing_doc = db.query(Document).filter(
        Document.project_id == project_id,
        Document.name == name,
        Document.version == version
    ).first()
    
    if existing_doc:
        raise HTTPException(status_code=409, detail=f"Document '{name}' version '{version}' for project '{project_id}' already exists.")

    # Generate a unique system ID for this document
    document_id = str(uuid.uuid4())
    
    try:
        # 3. Deep validate that the file is genuinely a PDF in-memory
        header = file.file.read(5)
        if header != b'%PDF-':
            raise HTTPException(status_code=400, detail="File is not a valid PDF document based on signature.")
            
        # Reset file pointer back to start
        file.file.seek(0)
        
        # 4. Read the full file into memory to compute hash and enforce size limits
        content = file.file.read()
        size_bytes = len(content)
        
        # Enforce max upload size
        if size_bytes > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(status_code=413, detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB.")
            
        file_hash = hashlib.sha256(content).hexdigest()
        
        # 5. Create and save the Document record in the database
        new_doc = Document(
            document_id=document_id,
            project_id=project_id,
            name=name,
            version=version,
            status="REGISTERED",
            original_filename=file.filename,
            file_content=content,
            size_bytes=size_bytes,
            sha256=file_hash,
            uploaded_by=uploaded_by
        )
        
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        
        return new_doc
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error during upload: {str(e)}")

def enqueue_processing(document_id: str):
    """
    Handoff mechanism triggered asynchronously after upload succeeds.
    This kicks off the heavy lifting: parsing, chunking, and embedding.
    """
    print(f"Enqueuing document {document_id} for processing (parsing, chunking, etc.)")
    pass

