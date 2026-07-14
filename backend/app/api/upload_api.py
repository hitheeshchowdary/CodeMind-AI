from pathlib import Path
import shutil
import zipfile

from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

# Folder where uploaded ZIP files will be stored
UPLOAD_DIR = Path("uploads")

# Create the folder if it doesn't exist
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/repository/upload")
async def upload_repository(file: UploadFile = File(...)):

    # Check if the uploaded file is a ZIP
    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are allowed."
        )

    # Destination path
    destination = UPLOAD_DIR / file.filename

    # Save the uploaded file
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        extract_folder = UPLOAD_DIR / "extracted" / destination.stem
        extract_folder.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(destination, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

    return {
        "message": "Repository uploaded successfully!",
        "filename": file.filename,
        "saved_to": destination.as_posix()
    }