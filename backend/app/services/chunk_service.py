import hashlib

from app.models.chunk import Chunk
from app.embeddings.embedding_service import EmbeddingService


class ChunkService:
    """
    Service responsible for splitting text into chunks.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def chunk_text(
        self,
        repository_name: str,
        file_name: str,
        file_path: str,
        language: str,
        text: str,
        chunk_size: int = 50,
        overlap: int = 10,
    ) -> list[Chunk]:

        if not text.strip():
            return []

        lines = text.splitlines()
        chunks = []

        start = 0

        while start < len(lines):

            end = start + chunk_size

            chunk_content = "\n".join(lines[start:end])

            embedding = self.embedding_service.generate_embedding(
                chunk_content
            )

            # Create a unique chunk ID
            raw_id = f"{repository_name}:{file_path}:{len(chunks)}"

            chunk_id = hashlib.md5(
                raw_id.encode("utf-8")
            ).hexdigest()

            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    repository_name=repository_name,
                    file_name=file_name,
                    file_path=file_path,
                    language=language,
                    chunk_index=len(chunks),
                    content=chunk_content,
                    embedding=embedding,
                )
            )

            start += chunk_size - overlap

        return chunks