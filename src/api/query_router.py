from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from pydantic import BaseModel
from typing import List, Optional

from src.retrieval.service import retrieve_chunks
from src.llm.service import generate_answer

router = APIRouter(prefix="/query", tags=["query"])

class QueryRequest(BaseModel):
    project_id: str
    query: str
    document_id: Optional[str] = None
    version: Optional[str] = None
    top_k: int = 5

class Citation(BaseModel):
    chunk_id: str
    page_start: Optional[int]
    document_id: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    limitation: str

@router.post("", response_model=QueryResponse)
def ask_question(request: QueryRequest, db: Session = Depends(get_db)):
    chunks = retrieve_chunks(
        project_id=request.project_id,
        query=request.query,
        top_k=request.top_k,
        document_filter=request.document_id,
        version_filter=request.version
    )
    
    result = generate_answer(request.query, chunks)
    return result
