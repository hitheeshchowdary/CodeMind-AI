from pathlib import Path
import os

from app.parser.python_parser import parse_python_file
from app.services.file_reader_service import FileReaderService
from app.services.chunk_service import ChunkService


# =========================================================
# SUPPORTED FILE TYPES
# =========================================================

SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript React",
    ".ts": "TypeScript",
    ".tsx": "TypeScript React",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".md": "Markdown",
    ".json": "JSON",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".sql": "SQL",
}


# =========================================================
# DIRECTORIES TO IGNORE
# =========================================================
# These directories often contain dependencies, generated
# files, caches, virtual environments, or version control
# data. They should not be analyzed or stored in ChromaDB.
#
# This works for nested folders as well.
# Example:
#
# frontend/node_modules
# backend/node_modules
# backend/venv
#
# =========================================================

IGNORED_DIRECTORIES = {
    # Node.js dependencies
    "node_modules",

    # Git data
    ".git",

    # Python cache / virtual environments
    "__pycache__",
    ".venv",
    "venv",
    "env",

    # Build output
    "dist",
    "build",
    "out",

    # Framework-generated folders
    ".next",
    ".nuxt",
    ".cache",

    # Test coverage
    "coverage",

    # IDE files
    ".idea",
    ".vscode",

    # Python tooling
    ".pytest_cache",
    ".mypy_cache",

    # Package manager caches
    ".npm",
    ".yarn",

    # Other generated folders
    "target",
}


# =========================================================
# FILES TO IGNORE
# =========================================================

IGNORED_FILES = {
    # Operating system files
    ".DS_Store",
    "Thumbs.db",

    # Log files
    "npm-debug.log",
    "yarn-debug.log",
    "yarn-error.log",
}


# =========================================================
# FILE SIZE LIMIT
# =========================================================
# Avoid reading extremely large source or generated files.
# 2 MB is generally more than enough for individual code
# files in a repository analysis system.

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024


# =========================================================
# REPOSITORY PARSER
# =========================================================

def parse_repository(repository_path: str):
    """
    Parse a repository and extract useful supported files.

    Unnecessary directories such as node_modules, virtual
    environments, build folders, and caches are skipped
    before their contents are scanned.

    This improves:
    - Repository processing speed
    - Memory usage
    - ChromaDB storage
    - AI retrieval quality
    """

    repository_root = Path(repository_path)

    if not repository_root.exists():
        raise ValueError(
            f"Repository path does not exist: {repository_path}"
        )

    if not repository_root.is_dir():
        raise ValueError(
            f"Repository path is not a directory: {repository_path}"
        )

    files = []

    file_reader = FileReaderService()
    chunk_service = ChunkService()

    skipped_directories = []
    skipped_files = []
    skipped_large_files = []

    print("\n" + "=" * 60)
    print(f"SCANNING REPOSITORY: {repository_root.name}")
    print("=" * 60 + "\n")

    for root, dirs, filenames in os.walk(
        repository_root,
        topdown=True,
    ):
        current_path = Path(root)

        # -------------------------------------------------
        # Remove ignored directories BEFORE os.walk enters
        # them.
        #
        # This is the important part that prevents scanning
        # node_modules and other unnecessary directories.
        # -------------------------------------------------

        ignored_dirs_in_current_folder = [
            directory
            for directory in dirs
            if directory.lower() in {
                ignored_directory.lower()
                for ignored_directory in IGNORED_DIRECTORIES
            }
        ]

        if ignored_dirs_in_current_folder:
            for directory in ignored_dirs_in_current_folder:
                directory_path = (
                    current_path / directory
                )

                skipped_directories.append(
                    directory_path.as_posix()
                )

                print(
                    f"Skipping directory: "
                    f"{directory_path}"
                )

        dirs[:] = [
            directory
            for directory in dirs
            if directory.lower() not in {
                ignored_directory.lower()
                for ignored_directory in IGNORED_DIRECTORIES
            }
        ]

        # -------------------------------------------------
        # Process files
        # -------------------------------------------------

        for filename in filenames:

            file_path = current_path / filename

            # Ignore specifically listed files
            if filename.lower() in {
                ignored_file.lower()
                for ignored_file in IGNORED_FILES
            }:
                skipped_files.append(
                    file_path.as_posix()
                )

                print(
                    f"Ignoring file: {file_path}"
                )

                continue

            # Skip unsupported extensions
            extension = file_path.suffix.lower()

            if extension not in SUPPORTED_EXTENSIONS:
                continue

            # -------------------------------------------------
            # Skip very large files
            # -------------------------------------------------

            try:
                file_size = file_path.stat().st_size

            except OSError as error:
                print(
                    f"Unable to access {file_path}: "
                    f"{error}"
                )

                continue

            if file_size > MAX_FILE_SIZE_BYTES:
                skipped_large_files.append(
                    file_path.as_posix()
                )

                print(
                    f"Skipping large file: "
                    f"{file_path} "
                    f"({round(file_size / 1024 / 1024, 2)} MB)"
                )

                continue

            print(
                f"Adding file: {file_path}"
            )

            # -------------------------------------------------
            # Build file metadata
            # -------------------------------------------------

            language = SUPPORTED_EXTENSIONS[
                extension
            ]

            file_info = {
                "name": file_path.name,
                "path": file_path.as_posix(),
                "extension": extension,
                "language": language,
                "size_kb": round(
                    file_size / 1024,
                    2,
                ),
            }

            # -------------------------------------------------
            # Read file
            # -------------------------------------------------

            success, content = (
                file_reader.read_file(file_path)
            )

            if success:

                file_info["content"] = content

                # Generate chunks
                file_info["chunks"] = (
                    chunk_service.chunk_text(
                        repository_name=repository_root.name,
                        file_name=file_path.name,
                        file_path=file_path.as_posix(),
                        language=language,
                        text=content,
                    )
                )

            else:

                file_info["content"] = ""
                file_info["chunks"] = []

            # -------------------------------------------------
            # Python-specific AST parsing
            # -------------------------------------------------

            if extension == ".py":

                try:
                    file_info.update(
                        parse_python_file(
                            file_path
                        )
                    )

                except Exception as error:
                    print(
                        f"Python parsing failed for "
                        f"{file_path}: {error}"
                    )

            # -------------------------------------------------
            # Add valid file
            # -------------------------------------------------

            files.append(file_info)

    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    print("\n" + "=" * 60)
    print("REPOSITORY SCAN COMPLETED")
    print("=" * 60)

    print(
        f"Total files analyzed: {len(files)}"
    )

    print(
        f"Directories skipped: "
        f"{len(skipped_directories)}"
    )

    print(
        f"Files skipped: "
        f"{len(skipped_files)}"
    )

    print(
        f"Large files skipped: "
        f"{len(skipped_large_files)}"
    )

    print("=" * 60 + "\n")

    return files