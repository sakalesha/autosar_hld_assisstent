from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentResponse(BaseModel):
    document_id: str
    project_id: str
    name: str
    version: str
    status: str
    original_filename: str
    size_bytes: int
    uploaded_at: datetime
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class ChunkResponse(BaseModel):
    chunk_id: str
    document_id: str
    page_start: Optional[int]
    page_end: Optional[int]
    section_path: Optional[str]
    chunk_type: str
    ocr: bool
    text: str

    class Config:
        from_attributes = True
