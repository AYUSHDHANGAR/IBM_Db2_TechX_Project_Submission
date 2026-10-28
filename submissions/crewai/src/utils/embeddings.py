"""
Shared Local Embedding Utilities using IBM Granite Embedding Model.
Model: ibm-granite/granite-embedding-311m-multilingual-r2
Dimensions: 768 (Supports Matryoshka truncation: 512, 384, 256, 128)
"""

import os
from typing import List, Optional

_MODEL_INSTANCE = None


def get_embedding_model_name() -> str:
    """Get the embedding model name from environment."""
    return os.getenv("EMBEDDING_MODEL", "ibm-granite/granite-embedding-311m-multilingual-r2")


def get_embedding_dimension() -> int:
    """Get the target embedding dimension (default 768 for Granite 311M)."""
    return int(os.getenv("EMBEDDING_DIMENSION", "768"))


def get_sentence_transformer_model():
    """Singleton loader for local SentenceTransformer model."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for local offline embeddings. "
                "Install it via: pip install sentence-transformers torch"
            )

        model_name = get_embedding_model_name()
        print(f"📦 Loading local embedding model: '{model_name}'...")
        _MODEL_INSTANCE = SentenceTransformer(model_name)
        print(" Local embedding model loaded successfully.")
    return _MODEL_INSTANCE


def local_embedding_function(text: str) -> List[float]:
    """
    Custom embedding function for CrewAI DB2VectorSearchTool.
    Encodes text using the local IBM Granite embedding model.
    Applies Matryoshka truncation if EMBEDDING_DIMENSION is configured.
    """
    model = get_sentence_transformer_model()
    target_dim = get_embedding_dimension()

    # Generate dense vector
    vector = model.encode(text).tolist()

    # Matryoshka slicing if a smaller dimension (e.g., 512, 768) is specified
    if target_dim < len(vector):
        vector = vector[:target_dim]

    return vector
