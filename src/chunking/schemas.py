from pydantic import BaseModel
from typing import Optional

class Block(BaseModel):
    """
    Represents a parsed element from the document parser.
    This acts as the input contract for the chunking service.
    """
    text: str
    page: Optional[int] = None
    section_path: Optional[str] = None
    block_type: str # 'text', 'table', 'heading'
    ocr: bool = False
