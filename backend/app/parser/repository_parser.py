from pathlib import Path
import os

from app.parser.python_parser import parse_python_file
from app.services.file_reader_service import FileReaderService
from app.services.chunk_service import ChunkService

SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".md": "Markdown",
    ".json": "JSON",
    ".html": "HTML",
    ".css": "CSS",
}

IGNORED_DIRECTORIES = {
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
}

IGNORED_FILES = {
    "package-lock.json",
    "package.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    ".DS_Store",
}


def parse_repository(repository_path: str):
    """
    Parses a repository and extracts metadata from supported files.
    """

    files = []

    file_reader = FileReaderService()
    chunk_service = ChunkService()

    print(f"\nScanning Repository: {repository_path}\n")

    for root, dirs, filenames in os.walk(repository_path):

        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]

        print(f"Current Folder: {root}")
        print(f"Files Found: {filenames}\n")

        for filename in filenames:

            file_path = Path(root) / filename
            extension = file_path.suffix.lower()

            if extension not in SUPPORTED_EXTENSIONS:
                print(f"Skipping: {filename}")
                continue

            print(f"Adding: {filename}")

            file_info = {
                "name": file_path.name,
                "path": file_path.as_posix(),
                "extension": extension,
                "language": SUPPORTED_EXTENSIONS[extension],
                "size_kb": round(file_path.stat().st_size / 1024, 2),
            }

            # Read file
            success, content = file_reader.read_file(file_path)

            # Generate chunks
            if success:
                file_info["content"] = content
                file_info["chunks"] = chunk_service.chunk_text(
                    repository_name=Path(repository_path).name,
                    file_name=file_path.name,
                    file_path=file_path.as_posix(),
                    language=SUPPORTED_EXTENSIONS[extension],
                    text=content
                )
            else:
                file_info["content"] = ""
                file_info["chunks"] = []

            # Parse Python AST only for Python files
            if extension == ".py":
                file_info.update(parse_python_file(file_path))

            # Append EVERY supported file
            files.append(file_info)

    return files
