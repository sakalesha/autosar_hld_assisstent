from openai import OpenAI
from config.settings import settings

def generate_answer(query: str, chunks: list) -> dict:
    if not chunks:
        return {
            "answer": "Not found in the document",
            "citations": [],
            "limitation": "No evidence found"
        }
        
    # Build context
    context = ""
    citations = []
    for i, chunk in enumerate(chunks):
        context += f"\n--- Chunk {chunk['chunk_id']} (Page {chunk['metadata'].get('page_start', 'unknown')}) ---\n{chunk['text']}\n"
        citations.append({
            "chunk_id": chunk['chunk_id'],
            "page_start": chunk['metadata'].get('page_start'),
            "document_id": chunk['metadata'].get('document_id')
        })
        
    prompt = f"""You are an AUTOSAR Architecture Assistant.
Answer the user's question ONLY using the provided document chunks below.
If you cannot find the answer, explain what information you DO have in the chunks.
Please cite the chunk ID for facts you state, e.g., [chunk_id].

Context:
{context}

Question: {query}
Answer:"""

    api_key = settings.GROQ_API_KEY
    if not api_key:
        return {
            "answer": "Error: GROQ_API_KEY not set in .env.",
            "citations": [],
            "limitation": "API key missing"
        }
        
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a helpful engineering assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        answer = response.choices[0].message.content
        return {
            "answer": answer,
            "citations": citations,
            "limitation": "Based only on retrieved chunks"
        }
    except Exception as e:
        return {
            "answer": f"Error calling Groq LLM: {str(e)}",
            "citations": [],
            "limitation": "LLM Error"
        }
