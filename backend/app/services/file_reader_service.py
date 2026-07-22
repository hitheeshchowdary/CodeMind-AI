from pathlib import Path


class FileReaderService:
    """
    Service responsible for reading source code files safely.
    """

    def read_file(self, file_path: Path):
        """
        Reads the content of a file.

        Args:
            file_path (Path): Path to the file.

        Returns:
            tuple:
                (True, content) if successful
                (False, "") if failed
        """

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            return True, content

        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False, ""