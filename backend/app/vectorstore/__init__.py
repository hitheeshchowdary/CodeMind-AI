"""
Vector Store Package

This package provides services for storing and retrieving
repository embeddings using ChromaDB.
"""

from .chroma_service import ChromaService

__all__ = [
    "ChromaService"
]