from pathlib import Path


class AnalyticsService:
    """
    Handles repository analytics and builds a JSON-safe
    API response for the frontend.
    """

    def build_response(
        self,
        repository_name,
        files,
    ):
        """
        Build repository metadata without returning internal
        Chunk objects to the frontend.
        """

        languages = set()
        safe_files = []

        for file_data in files:
            if not isinstance(file_data, dict):
                continue

            language = file_data.get(
                "language",
                "Unknown",
            )

            if language:
                languages.add(str(language))

            file_path = (
                file_data.get("path")
                or file_data.get("file_path")
                or file_data.get("name")
                or file_data.get("file_name")
                or ""
            )

            if not file_path:
                continue

            safe_file = {
                "name": Path(
                    str(file_path)
                ).name,
                "path": str(file_path),
                "language": str(language),
            }

            safe_files.append(safe_file)

        safe_files.sort(
            key=lambda item: item["path"].lower()
        )

        return {
            "message": (
                "Repository uploaded successfully!"
            ),
            "repository_name": str(
                repository_name
            ),
            "total_files": len(safe_files),
            "languages": sorted(languages),
            "files": safe_files,
        }