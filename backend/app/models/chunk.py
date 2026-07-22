from pydantic import BaseModel
from typing import Optional


class Chunk(BaseModel):
    """
    Represents one chunk of source code.
    """

    chunk_id: str

    repository_name: str

    file_name: str

    file_path: str

    language: str

    chunk_index: int

    content: str

    embedding: Optional[list[float]] = None