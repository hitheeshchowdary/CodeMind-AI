from app.agents.state import AgentState


class EvidenceRanker:
    """
    Ranks and filters retrieved repository evidence
    before it is passed to the verifier and answer generator.
    """

    PRIORITY_FILES = {
        "architecture": {
            "readme.md": 10,
            "main.py": 10,
            "app.py": 9,
            "chat_api.py": 9,
            "repository_service.py": 9,
            "upload_service.py": 8,
            "chroma_service.py": 8,
            "llm_service.py": 8,
            "graph.py": 8,
            "router.py": 8,
        },
        "repository_overview": {
            "readme.md": 10,
            "main.py": 9,
        },
        "technology": {
            "requirements.txt": 10,
            "package.json": 10,
            "readme.md": 9,
        },
    }

    def rank(self, state: AgentState) -> AgentState:
        question_type = state.get(
            "question_type",
            "general",
        )

        retrieved_chunks = state.get(
            "retrieved_chunks",
            [],
        )

        if not retrieved_chunks:
            return state

        priorities = self.PRIORITY_FILES.get(
            question_type,
            {},
        )

        scored_chunks = []

        for chunk in retrieved_chunks:
            file_name = chunk.get(
                "file_name",
                "",
            ).lower()

            file_path = chunk.get(
                "file_path",
                "",
            ).lower()

            distance = chunk.get(
                "distance",
                999,
            )

            # Semantic relevance score.
            semantic_score = 1 / (1 + distance)

            # File importance score.
            file_priority = priorities.get(
                file_name,
                0,
            )

            # Penalize test files and package markers
            # for repository-level reasoning.
            penalty = 0

            if file_name.startswith("test_"):
                penalty = 4

            if file_name == "__init__.py":
                penalty = 3

            if "/tests/" in file_path:
                penalty = 3

            final_score = (
                semantic_score
                + (file_priority * 0.05)
                - (penalty * 0.05)
            )

            scored_chunks.append(
                (
                    final_score,
                    chunk,
                )
            )

        scored_chunks.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        # Keep the strongest evidence while
        # preserving multi-file coverage.
        max_chunks = 8

        ranked_chunks = [
            chunk
            for _, chunk in scored_chunks[:max_chunks]
        ]

        print(
            f"[EvidenceRanker] Ranked "
            f"{len(retrieved_chunks)} chunks"
        )

        print(
            f"[EvidenceRanker] Selected "
            f"{len(ranked_chunks)} strongest chunks"
        )

        return {
            **state,
            "retrieved_chunks": ranked_chunks,
        }


evidence_ranker = EvidenceRanker()


def evidence_ranker_node(
    state: AgentState,
) -> AgentState:
    """
    LangGraph node wrapper for Evidence Ranker.
    """

    return evidence_ranker.rank(state)