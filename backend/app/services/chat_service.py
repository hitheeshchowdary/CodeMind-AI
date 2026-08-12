from app.vectorstore.chroma_service import ChromaService
from app.llm.prompt_builder import PromptBuilder
from app.llm.llm_service import LLMService


class ChatService:
    """
    Coordinates repository retrieval, prompt construction,
    and LLM response generation.
    """

    def __init__(self):
        self.chroma_service = ChromaService()
        self.prompt_builder = PromptBuilder()
        self.llm_service = LLMService()

    def ask(
        self,
        repository_name: str,
        question: str,
        top_k: int = 5,
    ) -> dict:
        """
        Answer a question using repository context.
        """

        # 1. Retrieve relevant chunks
        retrieved_chunks = self.chroma_service.search_chunks(
            repository_name=repository_name,
            query=question,
            top_k=top_k,
        )

        # 2. Check if anything was retrieved
        if not retrieved_chunks:
            return {
                "answer": (
                    "I couldn't find relevant information "
                    "in the repository."
                ),
                "sources": [],
            }

        # 3. Build prompt
        prompt = self.prompt_builder.build_prompt(
            question=question,
            retrieved_chunks=retrieved_chunks,
        )

        # 4. Generate answer using Llama
        answer = self.llm_service.generate_response(prompt)

        # 5. Build structured source information
        sources = []

        for chunk in retrieved_chunks:

            file_path = chunk.get("file_path")
            file_name = chunk.get("file_name")
            distance = chunk.get("distance")

            if not file_path:
                continue

            # Convert Chroma distance into a simple
            # similarity-style score for display.
            if distance is not None:
                relevance = round(
                    1 / (1 + distance),
                    3
                )
            else:
                relevance = None

            source = {
                "file": file_name,
                "path": file_path,
                "relevance": relevance,
            }

            # Prevent duplicate files
            if not any(
                existing["path"] == file_path
                for existing in sources
            ):
                sources.append(source)

        return {
            "answer": answer,
            "sources": sources,
        }