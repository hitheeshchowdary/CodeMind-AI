from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.chat_service import ChatService


router = APIRouter()


class ChatRequest(BaseModel):
    """
    Request model for repository chat.
    """

    repository_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the indexed repository."
    )

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question about the repository."
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of repository chunks to retrieve."
    )


class Source(BaseModel):
    """
    Source file used to generate the answer.
    """

    file: str
    path: str
    relevance: float | None = None


class ChatResponse(BaseModel):
    """
    Response returned by the chat endpoint.
    """

    answer: str
    sources: list[Source]


@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(request: ChatRequest):
    """
    Ask a question about an indexed repository.
    """

    try:
        chat_service = ChatService()

        result = chat_service.ask(
            repository_name=request.repository_name,
            question=request.question,
            top_k=request.top_k,
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )