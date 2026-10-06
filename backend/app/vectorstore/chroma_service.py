import time

import chromadb

from app.embeddings.embedding_service import EmbeddingService
from app.models.chunk import Chunk


class ChromaService:
    """
    Service responsible for storing and retrieving repository chunks
    using ChromaDB.
    """

    def __init__(self):
        # Create / load persistent database
        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        # Create / load collection
        self.collection = self.client.get_or_create_collection(
            name="repository_chunks"
        )

        # Embedding service
        self.embedding_service = EmbeddingService()

    def add_chunks(self, chunks: list[Chunk]):
        """
        Store multiple chunks in ChromaDB.
        """

        if not chunks:
            return

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk.chunk_id)

            documents.append(chunk.content)

            embeddings.append(chunk.embedding)

            metadatas.append(
                {
                    "repository_name": chunk.repository_name,
                    "file_name": chunk.file_name,
                    "file_path": chunk.file_path,
                    "language": chunk.language,
                    "chunk_index": chunk.chunk_index,
                }
            )

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search_chunks(
        self,
        repository_name: str,
        query: str,
        top_k: int = 5,
    ):
        """
        Search for the most relevant chunks in a repository.

        Returns:
            A list of clean chunk dictionaries.
        """

        total_start = time.perf_counter()

        # ----------------------------------------
        # Step 1: Generate query embedding
        # ----------------------------------------

        embedding_start = time.perf_counter()

        query_embedding = (
            self.embedding_service.generate_embedding(
                query
            )
        )

        embedding_time = (
            time.perf_counter() - embedding_start
        )

        print(
            f"Query embedding: "
            f"{embedding_time:.2f} seconds"
        )

        # ----------------------------------------
        # Step 2: Search ChromaDB
        # ----------------------------------------

        chroma_start = time.perf_counter()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "repository_name": repository_name
            },
        )

        chroma_time = (
            time.perf_counter() - chroma_start
        )

        print(
            f"ChromaDB query: "
            f"{chroma_time:.2f} seconds"
        )

        # ----------------------------------------
        # Step 3: Format results
        # ----------------------------------------

        documents = results.get(
            "documents",
            [[]],
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]],
        )[0]

        distances = results.get(
            "distances",
            [[]],
        )[0]

        retrieved_chunks = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            retrieved_chunks.append(
                {
                    "content": document,
                    "file_name": metadata.get(
                        "file_name",
                        "Unknown",
                    ),
                    "file_path": metadata.get(
                        "file_path",
                        "",
                    ),
                    "language": metadata.get(
                        "language",
                        "",
                    ),
                    "chunk_index": metadata.get(
                        "chunk_index",
                        0,
                    ),
                    "distance": distance,
                }
            )

        total_time = (
            time.perf_counter() - total_start
        )

        print(
            f"Total retrieval process: "
            f"{total_time:.2f} seconds"
        )

        return retrieved_chunks

    def delete_repository_chunks(
        self,
        repository_name: str,
    ):
        """
        Delete all chunks belonging to a specific repository.
        """

        self.collection.delete(
            where={
                "repository_name": repository_name
            }
        )

    def delete_collection(self):
        """
        Delete the entire ChromaDB collection.
        """

        self.client.delete_collection(
            "repository_chunks"
        )

    def reset_collection(self):
        """
        Delete and recreate the entire collection.
        """

        try:
            self.client.delete_collection(
                "repository_chunks"
            )
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name="repository_chunks"
        )