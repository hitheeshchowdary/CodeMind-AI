from fastapi import APIRouter, HTTPException

from app.services.project_service import (
    ProjectService,
)


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get("")
def get_projects():
    """
    Return all previously uploaded projects.
    """

    try:
        project_service = ProjectService()

        projects = (
            project_service.get_projects()
        )

        return {
            "projects": projects,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to retrieve project history: "
                f"{str(error)}"
            ),
        )


@router.get("/{repository_name}")
def get_project(
    repository_name: str,
):
    """
    Return one specific project.
    """

    try:
        project_service = ProjectService()

        project = (
            project_service.get_project(
                repository_name
            )
        )

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        return project

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to retrieve project: "
                f"{str(error)}"
            ),
        )


@router.delete("/{repository_name}")
def delete_project(
    repository_name: str,
):
    """
    Remove a project from project history.
    """

    try:
        project_service = ProjectService()

        deleted = (
            project_service.delete_project(
                repository_name
            )
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        return {
            "message": (
                "Project deleted successfully."
            ),
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to delete project: "
                f"{str(error)}"
            ),
        )