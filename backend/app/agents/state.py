from typing import TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared state passed between RepoMind AI agents.
    """
    repository_name: str
    question: str
    question_type: str
    route: str
    top_k: int

    search_queries: list[str]
    retrieved_chunks: list

    repository_summary: str

    verification_status: str
    evidence_summary: str
    retry_count: int

    answer: str
    sources: list