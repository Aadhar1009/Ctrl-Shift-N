"""Embeddings module using sentence-transformers for local, fast embeddings."""

from sentence_transformers import SentenceTransformer
import numpy as np
from functools import lru_cache

# Use a lightweight, fast model optimized for semantic similarity
MODEL_NAME = "all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Load and cache the sentence transformer model."""
    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    return model

def generate_embedding(text: str) -> np.ndarray:
    """Generate embedding vector for a single text."""
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding.astype(np.float32)

def generate_embeddings_batch(texts: list[str]) -> np.ndarray:
    """Generate embeddings for multiple texts efficiently."""
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True, batch_size=32)
    return embeddings.astype(np.float32)

def preprocess_issue(title: str, body: str) -> str:
    """Preprocess issue text for embedding generation."""
    # Combine title and body with title weighted more
    combined = f"{title} {title} {body}"
    # Basic cleaning
    combined = combined.replace('\n', ' ').replace('\r', ' ')
    combined = ' '.join(combined.split())  # Normalize whitespace
    return combined[:2000]  # Truncate for efficiency
