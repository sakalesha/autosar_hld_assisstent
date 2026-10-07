import hashlib
import tiktoken
from sqlalchemy.orm import Session
from db.models import Chunk, Document
from src.chunking.schemas import Block
from typing import List

# Using tiktoken for accurate token counting
# Architecture limits BGE embedding models to 512 tokens.
TOKENIZER = tiktoken.get_encoding("cl100k_base")
MAX_TOKENS = 500

def generate_chunk_id(document_id: str, sequence: int) -> str:
    """
    Generate a deterministic chunk ID based on the document ID and sequence number.
    This satisfies the idempotency requirement: re-running ingestion overwrites rather than duplicates.
    We truncate to 36 characters because the DB schema (db/models.py) specifies String(36).
    """
    base_string = f"{document_id}_{sequence}"
    # SHA-256 produces 64 chars. We take the first 36 to match the database schema.
    return hashlib.sha256(base_string.encode()).hexdigest()[:36]

def chunk_blocks(db: Session, document_id: str, blocks: List[Block]) -> List[Chunk]:
    """
    Takes parsed blocks, chunks them by section boundary and size, 
    and saves them to the database.
    """
    chunks_to_insert = []
    sequence = 0
    
    current_chunk_text = ""
    current_tokens = 0
    current_page_start = None
    current_page_end = None
    current_section = None
    
    def finalize_chunk():
        nonlocal current_chunk_text, current_tokens, current_page_start, current_page_end, current_section, sequence
        if not current_chunk_text.strip():
            return
            
        chunk = Chunk(
            chunk_id=generate_chunk_id(document_id, sequence),
            document_id=document_id,
            page_start=current_page_start,
            page_end=current_page_end,
            section_path=current_section,
            chunk_type="text",
            text=current_chunk_text.strip()
        )
        chunks_to_insert.append(chunk)
        sequence += 1
        
        # Reset accumulators for the next chunk
        current_chunk_text = ""
        current_tokens = 0
        current_page_start = None
        current_page_end = None

    for block in blocks:
        if block.block_type == "table":
            # Tables are always kept as their own separate chunk (Architecture 4.5)
            finalize_chunk() # Flush whatever we have
            
            table_chunk = Chunk(
                chunk_id=generate_chunk_id(document_id, sequence),
                document_id=document_id,
                page_start=block.page,
                page_end=block.page,
                section_path=block.section_path,
                chunk_type="table",
                ocr=block.ocr,
                text=block.text
            )
            chunks_to_insert.append(table_chunk)
            sequence += 1
            continue
            
        if block.block_type == "heading":
            # Headings signal a new section boundary
            finalize_chunk()
            current_section = block.section_path
            current_chunk_text = block.text + "\n\n"
            current_tokens = len(TOKENIZER.encode(current_chunk_text))
            current_page_start = block.page
            current_page_end = block.page
            continue
            
        # It's a normal text block
        # Check section boundaries
        if current_section != block.section_path:
            finalize_chunk()
            current_section = block.section_path
            
        block_tokens = len(TOKENIZER.encode(block.text))
        
        if current_tokens + block_tokens > MAX_TOKENS:
            # Too big! Finalize the current chunk first
            finalize_chunk()
            
            # Start a new chunk with this block
            current_chunk_text = block.text + "\n\n"
            current_tokens = block_tokens
            current_page_start = block.page
            current_page_end = block.page
        else:
            current_chunk_text += block.text + "\n\n"
            current_tokens += block_tokens
            if current_page_start is None:
                current_page_start = block.page
            current_page_end = block.page
            
    # Flush any remaining text at the very end
    finalize_chunk()
    
    # Database operations
    # 1. Idempotency: delete old chunks for this document if re-running
    db.query(Chunk).filter(Chunk.document_id == document_id).delete()
    
    # 2. Insert new chunks
    db.add_all(chunks_to_insert)
    
    # 3. Update document status
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if doc:
        doc.status = "CHUNKED"
        
    db.commit()
    
    return chunks_to_insert
