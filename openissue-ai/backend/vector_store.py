"""FAISS-based vector store for efficient similarity search."""

import faiss
import numpy as np
import json
import os
from pathlib import Path
from typing import Optional
from embeddings import generate_embedding, generate_embeddings_batch, preprocess_issue

VECTOR_DIM = 384  # Dimension for all-MiniLM-L6-v2
INDEX_PATH = "data/faiss_index.bin"
METADATA_PATH = "data/issues_metadata.json"

class VectorStore:
    def __init__(self):
        self.index: Optional[faiss.IndexFlatIP] = None
        self.metadata: list[dict] = []
        self._ensure_data_dir()
        self._load_or_create_index()
    
    def _ensure_data_dir(self):
        Path("data").mkdir(exist_ok=True)
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
            print("Loading existing FAISS index...")
            self.index = faiss.read_index(INDEX_PATH)
            with open(METADATA_PATH, 'r') as f:
                self.metadata = json.load(f)
            print(f"Loaded {self.index.ntotal} vectors")
        else:
            print("Creating new FAISS index...")
            self.index = faiss.IndexFlatIP(VECTOR_DIM)  # Inner product (cosine for normalized vectors)
            self.metadata = []
    
    def save(self):
        """Persist index and metadata to disk."""
        faiss.write_index(self.index, INDEX_PATH)
        with open(METADATA_PATH, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def add_issue(self, issue_id: str, title: str, body: str, issue_type: str = "unknown", 
                  priority: str = "medium", extra_metadata: dict = None):
        """Add a single issue to the vector store."""
        text = preprocess_issue(title, body)
        embedding = generate_embedding(text)
        
        self.index.add(embedding.reshape(1, -1))
        
        meta = {
            "id": issue_id,
            "title": title,
            "body": body[:500],  # Store truncated body
            "type": issue_type,
            "priority": priority,
            **(extra_metadata or {})
        }
        self.metadata.append(meta)
        self.save()
        return len(self.metadata) - 1
    
    def add_issues_batch(self, issues: list[dict]):
        """Add multiple issues efficiently."""
        if not issues:
            return
        
        texts = [preprocess_issue(i["title"], i["body"]) for i in issues]
        embeddings = generate_embeddings_batch(texts)
        
        self.index.add(embeddings)
        
        for issue in issues:
            meta = {
                "id": issue.get("id", f"issue-{len(self.metadata)}"),
                "title": issue["title"],
                "body": issue["body"][:500],
                "type": issue.get("type", "unknown"),
                "priority": issue.get("priority", "medium"),
            }
            self.metadata.append(meta)
        
        self.save()
        print(f"Added {len(issues)} issues. Total: {self.index.ntotal}")
    
    def search_similar(self, title: str, body: str, k: int = 3) -> list[dict]:
        """Find k most similar issues."""
        if self.index.ntotal == 0:
            return []
        
        text = preprocess_issue(title, body)
        query_embedding = generate_embedding(text)
        
        k = min(k, self.index.ntotal)
        scores, indices = self.index.search(query_embedding.reshape(1, -1), k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):
                result = {
                    **self.metadata[idx],
                    "similarity": float(score)
                }
                results.append(result)
        
        return results
    
    def get_stats(self) -> dict:
        """Get store statistics."""
        return {
            "total_issues": self.index.ntotal if self.index else 0,
            "vector_dimension": VECTOR_DIM
        }

# Global singleton
_store: Optional[VectorStore] = None

def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
