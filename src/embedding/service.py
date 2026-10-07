from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from typing import List
from db.models import Chunk, Document
from config.settings import settings
import os

# Initialize SentenceTransformer
model = SentenceTransformer('BAAI/bge-small-en-v1.5')

# Initialize ChromaDB
chroma_client = PersistentClient(path=os.path.join(settings.UPLOAD_DIR, "..", "chroma_db"))

def embed_and_index_chunks(db_session, document_id: str, chunks: List[Chunk]):
    if not chunks:
        return
    
    doc = db_session.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        return
        
    project_id = doc.project_id
    collection_name = f"project_{project_id}"
    
    collection = chroma_client.get_or_create_collection(name=collection_name)
    
    ids = []
    documents = []
    metadatas = []
    embeddings = []
    
    # We embed the text in batches or all at once
    texts = [chunk.text for chunk in chunks]
    embeddings_list = model.encode(texts).tolist()
    
    for idx, chunk in enumerate(chunks):
        ids.append(chunk.chunk_id)
        documents.append(chunk.text)
        metadatas.append({
            "document_id": chunk.document_id,
            "version": doc.version,
            "page_start": chunk.page_start if chunk.page_start else 0,
            "page_end": chunk.page_end if chunk.page_end else 0,
            "section_path": chunk.section_path if chunk.section_path else "",
            "chunk_type": chunk.chunk_type
        })
        embeddings.append(embeddings_list[idx])
        
    # Upsert to ChromaDB
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )
    
    doc.status = "INDEXED"
    db_session.commit()
