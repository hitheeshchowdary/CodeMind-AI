from pathlib import Path

from app.parser.repository_parser import (
    parse_repository,
)

from app.vectorstore.chroma_service import (
    ChromaService,
)

from app.services.repository_metadata_service import (
    RepositoryMetadataService,
)


class RepositoryService:
    """
    Handles repository parsing, indexing,
    and metadata storage.
    """

    def __init__(self):

        self.chroma_service = (
            ChromaService()
        )

        self.metadata_service = (
            RepositoryMetadataService()
        )

    def analyze_repository(
        self,
        repository_path: Path,
    ):
        """
        Analyze and index a repository.
        """

        repository_name = (
            repository_path.name
        )

        print(
            f"Indexing repository: "
            f"{repository_name}"
        )

        # -----------------------------------------
        # Remove previous data
        # -----------------------------------------

        self.chroma_service.delete_repository_chunks(
            repository_name
        )

        self.metadata_service.delete_repository(
            repository_name
        )

        # -----------------------------------------
        # Parse repository
        # -----------------------------------------

        files = parse_repository(
            str(repository_path)
        )

        # -----------------------------------------
        # Collect chunks
        # -----------------------------------------

        all_chunks = []

        for file in files:

            chunks = file.get(
                "chunks",
                [],
            )

            all_chunks.extend(
                chunks
            )

        # -----------------------------------------
        # Store chunks in ChromaDB
        # -----------------------------------------

        if all_chunks:

            self.chroma_service.add_chunks(
                all_chunks
            )

        # -----------------------------------------
        # Prepare metadata
        # -----------------------------------------

        metadata_files = []

        for file in files:

            metadata_files.append(
                {
                    "name": file.get(
                        "name"
                    ),

                    "path": file.get(
                        "path"
                    ),

                    "extension": file.get(
                        "extension"
                    ),

                    "language": file.get(
                        "language"
                    ),

                    "size_kb": file.get(
                        "size_kb"
                    ),
                }
            )

        # -----------------------------------------
        # Save metadata
        # -----------------------------------------

        self.metadata_service.save_repository(
            repository_name=repository_name,
            files=metadata_files,
        )

        print(
            f"Repository indexed successfully."
        )

        print(
            f"Files: {len(files)}"
        )

        print(
            f"Chunks: {len(all_chunks)}"
        )

        return files