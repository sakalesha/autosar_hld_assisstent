import uuid
import hashlib
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from db.models import Document
from config.settings import settings

def process_upload(db: Session, file: UploadFile, project_id: str, name: str, version: str, uploaded_by: str = None) -> Document:
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only .pdf files are allowed.")
    
    existing_doc = db.query(Document).filter(
        Document.project_id == project_id,
        Document.name == name,
        Document.version == version
    ).first()
    
    if existing_doc:
        raise HTTPException(status_code=409, detail=f"Document '{name}' version '{version}' for project '{project_id}' already exists.")

    document_id = str(uuid.uuid4())
    
    try:
        header = file.file.read(5)
        if header != b'%PDF-':
            raise HTTPException(status_code=400, detail="File is not a valid PDF document based on signature.")
            
        file.file.seek(0)
        content = file.file.read()
        size_bytes = len(content)
        
        if size_bytes > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(status_code=413, detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB.")
            
        file_hash = hashlib.sha256(content).hexdigest()
        
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
    from db.session import SessionLocal
    from src.parsing.service import parse_pdf_bytes
    from src.chunking.service import chunk_blocks
    from src.embedding.service import embed_and_index_chunks
    
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.document_id == document_id).first()
        if not doc:
            return
            
        blocks = parse_pdf_bytes(doc.file_content)
        doc.status = "PARSED"
        db.commit()
        
        chunks = chunk_blocks(db, document_id, blocks)
        
        embed_and_index_chunks(db, document_id, chunks)
        
    except Exception as e:
        print(f"Pipeline failed for document {document_id}: {e}")
        db.rollback()
    finally:
        db.close()
