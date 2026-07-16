from pathlib import Path
from app.parser.python_parser import parse_python_file
import os

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
    "dist",
    "build",
}


def parse_repository(repository_path: str):
    files = []

    print(f"\nScanning Repository: {repository_path}\n")

    for root, dirs, filenames in os.walk(repository_path):

        print(f"Current Folder: {root}")
        print(f"Files Found: {filenames}\n")

        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]

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
            if extension == ".py":
                file_info.update(parse_python_file(file_path))

            files.append(file_info)

    print(f"\nTotal Files Parsed: {len(files)}")

    return files