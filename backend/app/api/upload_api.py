from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.upload_service import UploadService
from app.services.repository_service import RepositoryService
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.post("/repository/upload")
async def upload_repository(file: UploadFile = File(...)):
    """
    Upload a GitHub repository ZIP, extract it,
    analyze the repository, and return repository metadata.
    """

    # Validate file type
    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are allowed."
        )

    # Save and extract repository
    upload_service = UploadService()
    destination, extract_folder = upload_service.save_and_extract(file)

    # Analyze repository
    repository_service = RepositoryService()
    files = repository_service.analyze_repository(extract_folder)

    # Build analytics response
    analytics_service = AnalyticsService()
    response = analytics_service.build_response(
        repository_name=destination.stem,
        files=files
    )

    return response