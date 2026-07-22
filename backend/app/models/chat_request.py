from pydantic import BaseModel


class ChatRequest(BaseModel):
    repository_name: str
    question: str

class ChatResponse(BaseModel):
    answer: str