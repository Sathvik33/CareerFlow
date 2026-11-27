import os
import logging
from dotenv import load_dotenv, find_dotenv
import httpx
import numpy as np

load_dotenv(find_dotenv(usecwd=True))

logger = logging.getLogger(__name__)

COHERE_EMBED_URL = "https://api.cohere.com/v2/embed"

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


def get_text_chunks(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    """Splits text into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_text(text)


def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """Generates 384-dim embeddings via Cohere API."""
    if not chunks:
        return []

    api_key = os.getenv("COHERE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("COHERE_API_KEY environment variable is not set.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "embed-english-light-v3.0",
        "texts": chunks,
        "input_type": "search_document",
        "embedding_types": ["float"],
    }

    try:
        response = httpx.post(COHERE_EMBED_URL, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        return response.json()["embeddings"]["float"]
    except httpx.HTTPStatusError as exc:
        logger.error("Cohere Embed API error (%s): %s", exc.response.status_code, exc.response.text)
        raise
    except Exception as exc:
        logger.error("Failed to generate embeddings via Cohere API: %s", exc)
        raise


class _LazyEmbedder:
    """Drop-in replacement for SentenceTransformer embedder object."""
    def encode(self, texts, *args, **kwargs):
        is_single = isinstance(texts, str)
        chunk_list = [texts] if is_single else list(texts)
        embeddings = generate_embeddings(chunk_list)
        arr = np.array(embeddings, dtype=np.float32)
        return arr[0] if is_single else arr


embedder = _LazyEmbedder()


def get_embedder():
    """Returns the embedder interface for backward compatibility."""
    return embedder
