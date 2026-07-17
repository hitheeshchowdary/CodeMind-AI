from pathlib import Path
import shutil
import zipfile

from fastapi import UploadFile


class UploadService:
    """
    Handles all upload-related operations:
    - Save uploaded ZIP file
    - Extract ZIP contents
    """

    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)

    def save_and_extract(self, file: UploadFile):
        """
        Saves the uploaded ZIP file and extracts it.

        Args:
            file (UploadFile): Uploaded ZIP file

        Returns:
            tuple:
                destination (Path): Path to the saved ZIP file
                extract_folder (Path): Path to the extracted repository
        """

        # Save ZIP file
        destination = self.upload_dir / file.filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create extraction folder
        extract_folder = (
            self.upload_dir / "extracted" / destination.stem
        )

        extract_folder.mkdir(parents=True, exist_ok=True)

        # Extract ZIP
        with zipfile.ZipFile(destination, "r") as zip_ref:
            zip_ref.extractall(extract_folder)

        return destination, extract_folder