from pathlib import Path
import shutil
import zipfile

from app.parser.repository_parser import parse_repository
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

# Folder where uploaded ZIP files will be stored
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/repository/upload")
async def upload_repository(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are allowed."
        )

    # Destination path
    destination = UPLOAD_DIR / file.filename

    # Save the uploaded ZIP file
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract ZIP contents
    extract_folder = UPLOAD_DIR / "extracted" / destination.stem
    extract_folder.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(destination, "r") as zip_ref:
        zip_ref.extractall(extract_folder)

    # Parse repository files
    files = parse_repository(str(extract_folder))

    # Collect unique languages
    languages = list({file["language"] for file in files})

    # Count total files
    total_files = len(files)

    return {
        "message": "Repository uploaded successfully!",
        "repository_name": destination.stem,
        "total_files": total_files,
        "languages": languages,
        "files": files
    }
