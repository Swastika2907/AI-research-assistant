from dataclasses import dataclass, field
from typing import List
 
import numpy as np
from PyPDF2 import PdfReader
 
 
@dataclass
class Chunk:
    text: str
    doc_name: str
    embedding: np.ndarray = None
 
 
@dataclass
class DocumentStore:
    """Holds every chunk from every uploaded PDF, in memory, per server run."""
    chunks: List[Chunk] = field(default_factory=list)
 
    def add(self, chunks: List[Chunk]):
        self.chunks.extend(chunks)
 
    def is_empty(self) -> bool:
        return len(self.chunks) == 0
 
    def search(self, query_embedding: np.ndarray, top_k: int = 4) -> List[Chunk]:
        if self.is_empty():
            return []
        matrix = np.array([c.embedding for c in self.chunks])
        query = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-8
        matrix_normed = matrix / norms
        sims = matrix_normed @ query
        top_idx = np.argsort(sims)[::-1][:top_k]
        return [self.chunks[i] for i in top_idx]
 
 
def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join((page.extract_text() or "") for page in reader.pages)
 
 
def chunk_text(text: str, doc_name: str, chunk_size: int = 500, overlap: int = 50) -> List[Chunk]:
    """
    Word-based chunking with overlap, so a fact split across a chunk
    boundary still has a decent chance of being retrieved by one chunk
    or the other.
    """
    words = text.split()
    if not words:
        return []
 
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(Chunk(text=" ".join(chunk_words), doc_name=doc_name))
        start = end - overlap  # step forward, but re-include the overlap window
    return chunks