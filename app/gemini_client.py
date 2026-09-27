import os
 
import numpy as np
import google.generativeai as genai
 
_EMBED_MODEL = "models/gemini-embedding-001"
_CHAT_MODEL = "gemini-3.5-flash-lite" 
 
 
def configure(api_key: str = None):
    """Call once at app startup. Reads GEMINI_API_KEY from env if not passed."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "No Gemini API key found. Set GEMINI_API_KEY in your .env file "
            "(get a free key at https://aistudio.google.com/apikey)."
        )
    genai.configure(api_key=key)
 
 
def embed_text(text: str, task_type: str = "retrieval_document") -> np.ndarray:
    """
    task_type is 'retrieval_document' when embedding chunks at upload time,
    and 'retrieval_query' when embedding the user's question — Gemini's
    embedding model is tuned differently for each, which measurably improves
    retrieval quality over using one task_type for both.
    """
    result = genai.embed_content(model=_EMBED_MODEL, content=text, task_type=task_type)
    return np.array(result["embedding"])
 
 
def generate_answer(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(no relevant context found)"
    prompt = f"""You are a research assistant answering questions about an uploaded document.
Answer using ONLY the context below. If the context doesn't contain the answer, say so plainly
instead of guessing.
 
CONTEXT:
{context}
 
QUESTION: {question}
 
ANSWER:"""
    model = genai.GenerativeModel(_CHAT_MODEL)
    response = model.generate_content(prompt)
    return response.text
 