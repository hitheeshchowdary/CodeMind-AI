import json
from pathlib import Path


class RepositoryMetadataService:
    """
    Stores lightweight repository metadata.

    File content and chunks are stored separately
    in ChromaDB.
    """

    def __init__(
        self,
        storage_path: str = "data/repositories.json",
    ):

        self.storage_path = Path(
            storage_path
        )

        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.storage_path.exists():

            self._save_data({})

    def save_repository(
        self,
        repository_name: str,
        files: list,
    ):
        """
        Save or update repository metadata.
        """

        data = self._load_data()

        data[repository_name] = {
            "repository_name": repository_name,
            "files": files,
        }

        self._save_data(data)

    def get_repository(
        self,
        repository_name: str,
    ) -> dict | None:
        """
        Retrieve repository metadata.
        """

        data = self._load_data()

        return data.get(
            repository_name
        )

    def delete_repository(
        self,
        repository_name: str,
    ):
        """
        Delete repository metadata.
        """

        data = self._load_data()

        if repository_name in data:

            del data[
                repository_name
            ]

            self._save_data(data)

    def _load_data(
        self,
    ) -> dict:

        try:

            with open(
                self.storage_path,
                "r",
                encoding="utf-8",
            ) as file:

                return json.load(file)

        except (
            FileNotFoundError,
            json.JSONDecodeError,
        ):

            return {}

    def _save_data(
        self,
        data: dict,
    ):
        """
        Save metadata to JSON.
        """

        with open(
            self.storage_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
            )