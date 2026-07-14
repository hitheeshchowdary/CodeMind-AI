from fastapi import APIRouter
from app.parser.repository_parser import parse_repository

router = APIRouter()


@router.get("/repository/files")
def repository_files():
    repository_path = "."  # Temporary: scans backend folder
    return parse_repository(repository_path)