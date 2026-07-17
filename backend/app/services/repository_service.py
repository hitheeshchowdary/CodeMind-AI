from pathlib import Path

from app.parser.repository_parser import parse_repository


class RepositoryService:
    """
    Handles all repository analysis operations.
    """

    def analyze_repository(self, repository_path: Path):
        """
        Analyze the extracted repository.

        Args:
            repository_path (Path): Path to extracted repository

        Returns:
            list: Repository file metadata
        """

        files = parse_repository(str(repository_path))

        return files