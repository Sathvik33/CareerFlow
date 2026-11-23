import os
from sentence_transformers import SentenceTransformer
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    class RecursiveCharacterTextSplitter:
        """Pure-Python fallback splitter when langchain_text_splitters is unavailable."""
        def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, separators: list[str] | None = None):
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap

        def split_text(self, text: str) -> list[str]:
            if not text:
                return []
            chunks = []
            start = 0
            step = max(1, self.chunk_size - self.chunk_overlap)
            while start < len(text):
                chunks.append(text[start : start + self.chunk_size])
                start += step
            return chunks

# Lazy-load model on first use so startup is instant and reload doesn't freeze the server.
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        os.environ["HF_HUB_OFFLINE"] = "1"
        try:
            _embedder = SentenceTransformer('all-MiniLM-L6-v2', local_files_only=True)
        except Exception:
            _embedder = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedder

class _LazyEmbedder:
    def encode(self, *args, **kwargs):
        return get_embedder().encode(*args, **kwargs)

embedder = _LazyEmbedder()

def get_text_chunks(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    """Splits text into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_text(text)

def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """Generates embeddings for a list of text chunks."""
    if not chunks:
        return []
    embeddings = embedder.encode(chunks)
    # Convert numpy arrays to lists of floats for pgvector
    return [emb.tolist() for emb in embeddings]
