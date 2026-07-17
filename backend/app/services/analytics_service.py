class AnalyticsService:
    """
    Handles repository analytics and builds the API response.
    """

    def build_response(self, repository_name, files):
        # Collect unique languages
        languages = list({file["language"] for file in files})

        # Count total files
        total_files = len(files)

        return {
            "message": "Repository uploaded successfully!",
            "repository_name": repository_name,
            "total_files": total_files,
            "languages": languages,
            "files": files
        }