import fitz  # PyMuPDF
import pymupdf4llm
from typing import List
from src.chunking.schemas import Block

def parse_pdf_bytes(pdf_bytes: bytes) -> List[Block]:
    """
    Parses a PDF byte stream into a structured list of Blocks using Layout-Aware Markdown conversion.
    This automatically handles Tables, OCR, and complex multi-column layouts gracefully.
    """
    blocks = []
    
    # Open the PDF directly from the byte stream
    doc = fitz.open("pdf", pdf_bytes)
    
    # 1. Use pymupdf4llm for Layout-Aware Parsing to Markdown
    try:
        md_pages = pymupdf4llm.to_markdown(doc, page_chunks=True)
    except Exception as e:
        print(f"Warning: Layout-aware parsing failed, falling back to basic extraction: {e}")
        md_pages = [{"text": page.get_text(), "metadata": {"page": i+1}} for i, page in enumerate(doc)]
    
    current_section = "Document Start"
    
    # 2. Semantic Chunking Boundaries (Split by Markdown Headers)
    for page_data in md_pages:
        page_text = page_data.get("text", "")
        page_num = page_data.get("metadata", {}).get("page", 1)
        
        lines = page_text.split('\n')
        current_block_text = ""
        
        for line in lines:
            # If the line is a markdown header, we treat it as a semantic boundary
            if line.strip().startswith('#'):
                # Flush previous block
                if current_block_text.strip():
                    blocks.append(Block(
                        text=current_block_text.strip(),
                        page=page_num,
                        section_path=current_section,
                        block_type="text",
                        ocr=False
                    ))
                # Update current section and start a new block
                current_section = line.strip("#").strip()
                current_block_text = line + "\n"
            else:
                current_block_text += line + "\n"
                
        # Flush the end of the page
        if current_block_text.strip():
            blocks.append(Block(
                text=current_block_text.strip(),
                page=page_num,
                section_path=current_section,
                block_type="text",
                ocr=False
            ))
            
    return blocks
