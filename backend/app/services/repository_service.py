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
        """

        files = parse_repository(str(repository_path))

        all_chunks = []

        for file in files:
            all_chunks.extend(file["chunks"])

        if all_chunks:
            self.chroma_service.add_chunks(all_chunks)

        return files