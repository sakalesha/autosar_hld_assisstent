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
