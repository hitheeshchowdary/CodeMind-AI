from app.services.chat_service import ChatService
from app.agents.state import AgentState


chat_service = ChatService()


def fast_rag_node(
    state: AgentState,
) -> AgentState:
    """
    Execute the existing RepoMind AI RAG pipeline
    through ChatService.
    """

    result = chat_service.ask(
        repository_name=state["repository_name"],
        question=state["question"],
        top_k=state.get("top_k", 3),
    )

    return {
        **state,
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "question_type": result.get(
            "question_type",
            state.get("question_type", "general"),
        ),
    }