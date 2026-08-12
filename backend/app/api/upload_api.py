from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.services.upload_service import UploadService
from app.services.repository_service import RepositoryService
from app.services.analytics_service import AnalyticsService


router = APIRouter()


class UploadResponse(BaseModel):
    """
    Response returned after repository upload and analysis.
    """

    message: str
    repository_name: str
    total_files: int
    languages: list[str]
    files: list


@router.post(
    "/repository/upload",
    response_model=UploadResponse
)
async def upload_repository(
    file: UploadFile = File(...)
):
    """
    Upload a GitHub repository ZIP, extract it,
    analyze it, and return repository metadata.
    """

    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A file is required."
        )

    # Validate file type
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are allowed."
        )

    try:
        # Save and extract repository
        upload_service = UploadService()

        destination, extract_folder = (
            upload_service.save_and_extract(file)
        )

        # Analyze repository
        repository_service = RepositoryService()

        files = repository_service.analyze_repository(
            extract_folder
        )

        # Build analytics response
        analytics_service = AnalyticsService()

        response = analytics_service.build_response(
            repository_name=destination.stem,
            files=files
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Repository upload failed: {str(e)}"
        )