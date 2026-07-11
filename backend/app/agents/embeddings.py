import os
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Load model once at module level. Set offline mode so it doesn't crash on DNS issues.
os.environ["HF_HUB_OFFLINE"] = "1"
embedder = SentenceTransformer('all-MiniLM-L6-v2')

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
