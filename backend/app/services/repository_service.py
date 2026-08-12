from pathlib import Path

from app.parser.repository_parser import parse_repository
from app.vectorstore import ChromaService


class RepositoryService:
    """
    Handles all repository analysis operations.
    """

    def __init__(self):
        self.chroma_service = ChromaService()

    def analyze_repository(self, repository_path: Path):
        """
        Analyze repository and store all chunks in ChromaDB.

        Existing chunks for the same repository are removed
        before storing the newly generated chunks.
        """

        repository_name = repository_path.name

        # Remove existing chunks for this repository
        self.chroma_service.delete_repository_chunks(
            repository_name
        )

        # Parse repository
        files = parse_repository(
            str(repository_path)
        )

        # Collect all chunks
        all_chunks = []

        for file in files:
            all_chunks.extend(
                file["chunks"]
            )

        # Store fresh chunks in ChromaDB
        if all_chunks:
            self.chroma_service.add_chunks(
                all_chunks
            )

        return files