from src.embedding.service import chroma_client, model
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
import numpy as np

# Initialize a small, fast cross-encoder for re-ranking
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def retrieve_chunks(project_id: str, query: str, top_k: int = 5, document_filter: str = None, version_filter: str = None) -> List[Dict[str, Any]]:
    collection_name = f"project_{project_id}"
    try:
        collection = chroma_client.get_collection(name=collection_name)
    except Exception:
        return [] # Collection not found
        
    query_embedding = model.encode([query]).tolist()[0]
    
    where_clause = {}
    if document_filter:
        where_clause["document_id"] = document_filter
    if version_filter:
        where_clause["version"] = version_filter
        
    if len(where_clause) == 1:
        where = where_clause
    elif len(where_clause) > 1:
        where = {"$and": [{k: v} for k, v in where_clause.items()]}
    else:
        where = None
        
    # Phase 1a: Retrieve broad set of chunks (Top 25) using fast Vector Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=25,
        where=where,
        include=["documents", "metadatas", "distances"]
    )
    
    # Phase 1b: Fetch all chunks for the document to do BM25 Keyword Search
    from rank_bm25 import BM25Okapi
    all_docs = collection.get(where=where, include=["documents", "metadatas"])
    
    candidates_dict = {} # Use dict to deduplicate by chunk_id
    
    # Add Vector Search candidates
    if results and results['ids'] and results['ids'][0]:
        for i in range(len(results['ids'][0])):
            chunk_id = results['ids'][0][i]
            candidates_dict[chunk_id] = {
                "chunk_id": chunk_id,
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
            }
            
    # Add BM25 Keyword Search candidates
    if all_docs and all_docs['ids']:
        tokenized_corpus = [doc.lower().split(" ") for doc in all_docs['documents']]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = query.lower().split(" ")
        bm25_scores = bm25.get_scores(tokenized_query)
        
        top_n = min(25, len(bm25_scores))
        top_indices = np.argsort(bm25_scores)[::-1][:top_n]
        
        for idx in top_indices:
            chunk_id = all_docs['ids'][idx]
            if chunk_id not in candidates_dict:
                candidates_dict[chunk_id] = {
                    "chunk_id": chunk_id,
                    "text": all_docs['documents'][idx],
                    "metadata": all_docs['metadatas'][idx],
                }
                
    candidates = list(candidates_dict.values())
    if not candidates:
        return []
        
    # Phase 2: Use Cross-Encoder to Re-rank the candidates based on true semantic meaning
    pairs = [[query, candidate['text']] for candidate in candidates]
    scores = reranker.predict(pairs)
    
    # Attach scores and sort
    for i, candidate in enumerate(candidates):
        candidate['rerank_score'] = float(scores[i])
        
    candidates.sort(key=lambda x: x['rerank_score'], reverse=True)
    
    # Return the absolute best `top_k` chunks
    return candidates[:top_k]
