from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)
from pydantic import BaseModel

from app.services.upload_service import (
    UploadService,
)
from app.services.repository_service import (
    RepositoryService,
)
from app.services.analytics_service import (
    AnalyticsService,
)


router = APIRouter()


class RepositoryFile(BaseModel):
    """
    Safe file information returned to the frontend.
    """

    name: str
    path: str
    language: str


class UploadResponse(BaseModel):
    """
    Response returned after repository upload
    and analysis.
    """

    message: str
    repository_name: str
    total_files: int
    languages: list[str]
    files: list[RepositoryFile]


@router.post(
    "/repository/upload",
    response_model=UploadResponse,
)
async def upload_repository(
    file: UploadFile = File(...),
):
    """
    Upload a repository ZIP file, extract it,
    analyze it, and return repository metadata.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A file is required.",
        )

    if not file.filename.lower().endswith(
        ".zip"
    ):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are allowed.",
        )

    try:
        # Save and extract repository
        upload_service = UploadService()

        destination, extract_folder = (
            upload_service.save_and_extract(file)
        )

        # Analyze repository and store chunks
        repository_service = (
            RepositoryService()
        )

        files = (
            repository_service.analyze_repository(
                extract_folder
            )
        )

        # Build JSON-safe response
        analytics_service = (
            AnalyticsService()
        )

        response = (
            analytics_service.build_response(
                repository_name=extract_folder.name,
                files=files,
            )
        )

        return response

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Repository upload failed: "
                f"{str(error)}"
            ),
        )