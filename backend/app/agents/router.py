from app.services.question_service import QuestionService

from app.agents.state import AgentState


class AgentRouter:
    """
    Routes repository questions between the existing
    fast RAG pipeline and the future agentic workflow.
    """

    def __init__(self):
        self.question_service = QuestionService()

    def route(self, state: AgentState) -> AgentState:
        """
        Classify the question and determine the execution route.
        """

        question = state["question"]

        question_type = (
            self.question_service.classify_question(
                question
            )
        )

        # -----------------------------------------
        # Simple questions → existing RAG
        # -----------------------------------------

        simple_types = {
            "file_question",
            "code_question",
            "technology",
            "general",
        }

        if question_type in simple_types:
            route = "fast_rag"

        # -----------------------------------------
        # Complex repository questions → agentic
        # -----------------------------------------

        else:
            route = "agentic"

        return {
            **state,
            "question_type": question_type,
            "route": route,
        }