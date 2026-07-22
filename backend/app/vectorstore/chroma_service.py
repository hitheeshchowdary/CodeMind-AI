import chromadb

from app.embeddings.embedding_service import EmbeddingService
from app.models.chunk import Chunk


class ChromaService:
    """
    Service responsible for storing and retrieving repository chunks
    using ChromaDB.
    """

    def __init__(self):
        # Create / Load persistent database
        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        # Create / Load collection
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
        Search the most relevant chunks for a user query.
        """

        query_embedding = self.embedding_service.generate_embedding(
            query
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "repository_name": repository_name
            }
        )

        return results

    def delete_collection(self):
        """
        Delete the current collection.
        """

        self.client.delete_collection("repository_chunks")

    def reset_collection(self):
        """
        Recreate the collection.
        """

        try:
            self.client.delete_collection("repository_chunks")
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name="repository_chunks"
        )