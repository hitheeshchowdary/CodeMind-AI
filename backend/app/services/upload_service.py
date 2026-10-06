from pathlib import Path
import os
import shutil
import zipfile
import subprocess
import re
import stat

from fastapi import UploadFile


class UploadService:
    """
    Handles repository source operations:

    - Save uploaded ZIP file
    - Extract ZIP contents
    - Clone public GitHub repositories
    """

    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)

        self.extracted_dir = self.upload_dir / "extracted"
        self.extracted_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save_and_extract(
        self,
        file: UploadFile,
    ):
        """
        Saves and extracts an uploaded ZIP file.

        Returns:
            tuple:
                destination (Path): Saved ZIP path
                extract_folder (Path): Extracted repository path
        """

        destination = self.upload_dir / file.filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        extract_folder = self.extracted_dir / destination.stem

        extract_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        with zipfile.ZipFile(
            destination,
            "r",
        ) as zip_ref:
            zip_ref.extractall(extract_folder)

        return (
            destination,
            extract_folder,
        )

    def clone_github_repository(
        self,
        repository_url: str,
    ) -> Path:
        """
        Clones a public GitHub repository.

        Returns:
            Path: Cloned repository directory.
        """

        repository_url = repository_url.strip()

        pattern = (
            r"^https://github\.com/[\w.-]+/"
            r"[\w.-]+(?:\.git)?/?$"
        )

        if not re.match(pattern, repository_url):
            raise ValueError(
                "Please provide a valid public GitHub repository URL."
            )

        repository_name = (
            repository_url.rstrip("/")
            .split("/")[-1]
        )

        if repository_name.endswith(".git"):
            repository_name = repository_name[:-4]

        repository_path = (
            self.extracted_dir / repository_name
        )

        def remove_readonly(
            func,
            path,
            exc_info,
        ):
            try:
                os.chmod(
                    path,
                    stat.S_IWRITE,
                )
                func(path)
            except Exception:
                raise

        # Remove previous clone if it exists
        if repository_path.exists():
            try:
                shutil.rmtree(
                    repository_path,
                    onerror=remove_readonly,
                )
            except Exception as exc:
                raise RuntimeError(
                    "Unable to remove existing "
                    f"repository directory: {exc}"
                )

        # Clone repository
        try:
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    repository_url,
                    str(repository_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        except FileNotFoundError:
            raise RuntimeError(
                "Git is not installed or is not "
                "available in the system PATH."
            )

        except subprocess.CalledProcessError as exc:
            error_message = (
                exc.stderr.strip()
                or "Git clone failed."
            )

            raise RuntimeError(error_message)

        # Git metadata is not required for analysis.
        git_directory = repository_path / ".git"

        if git_directory.exists():
            try:
                shutil.rmtree(
                    git_directory,
                    onerror=remove_readonly,
                )
            except Exception as exc:
                raise RuntimeError(
                    "Repository was cloned, but the "
                    f".git directory could not be removed: {exc}"
                )

        return repository_path