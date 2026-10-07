import re
import time


from app.vectorstore.chroma_service import (
    ChromaService,
)


from app.llm.prompt_builder import (
    PromptBuilder,
)


from app.llm.llm_service import (
    LLMService,
)


from app.services.project_service import (
    ProjectService,
)


from app.services.question_service import (
    QuestionService,
)


from app.services.repository_metadata_service import (
    RepositoryMetadataService,
)


class ChatService:
    """
    Main orchestration service for RepoMind AI.

    Responsibilities:

    1. Classify user questions.
    2. Route questions to the appropriate strategy.
    3. Retrieve repository metadata.
    4. Retrieve relevant code chunks.
    5. Build prompts.
    6. Generate AI responses.
    7. Return relevant sources.
    """

    def __init__(self):

        self.chroma_service = (
            ChromaService()
        )

        self.prompt_builder = (
            PromptBuilder()
        )

        self.llm_service = (
            LLMService()
        )

        self.project_service = (
            ProjectService()
        )

        self.question_service = (
            QuestionService()
        )

        self.metadata_service = (
            RepositoryMetadataService()
        )

    def ask(
        self,
        repository_name: str,
        question: str,
        top_k: int = 5,
    ) -> dict:
        """
        Main entry point for repository questions.
        """

        total_start = time.perf_counter()

        print("\n" + "=" * 60)

        print(
            "RepoMind AI QUESTION"
        )

        print("=" * 60)

        print(
            f"Repository: {repository_name}"
        )

        print(
            f"Question: {question}"
        )

        # -----------------------------------------
        # 1. Classify question
        # -----------------------------------------

        question_type = (
            self.question_service.classify_question(
                question
            )
        )

        print(
            f"Question type: {question_type}"
        )

        # -----------------------------------------
        # 2. Get repository metadata
        # -----------------------------------------

        metadata = (
            self.metadata_service.get_repository(
                repository_name
            )
        )

        if not metadata:

            return {
                "answer": (
                    "I couldn't find the repository "
                    "metadata. Please make sure the "
                    "repository has been indexed."
                ),
                "sources": [],
                "question_type": question_type,
            }

        files = metadata.get(
            "files",
            [],
        )

        # -----------------------------------------
        # 3. Route project structure questions
        # -----------------------------------------

        if question_type == "project_structure":

            return (
                self._handle_structure_question(
                    files=files,
                    question_type=question_type,
                    total_start=total_start,
                )
            )

        # -----------------------------------------
        # 4. Build repository summary
        # -----------------------------------------

        repository_summary = (
            self.project_service.get_repository_summary(
                files
            )
        )

        # -----------------------------------------
        # 5. Retrieve relevant chunks
        # -----------------------------------------

        search_start = time.perf_counter()

        search_query = (
            self._build_search_query(
                question=question,
                question_type=question_type,
            )
        )

        print(
            f"Search query: {search_query}"
        )

        # -----------------------------------------
        # Detect exact file reference
        # -----------------------------------------

        file_reference = None

        if question_type == "file_question":

            file_reference = (
                self._extract_file_reference(
                    question
                )
            )

            if file_reference:

                print(
                    f"Detected file reference: "
                    f"{file_reference}"
                )

        # -----------------------------------------
        # Retrieve relevant chunks
        # -----------------------------------------

        retrieved_chunks = (
            self.chroma_service.search_chunks(
                repository_name=repository_name,
                query=search_query,
                top_k=self._get_top_k(
                    question_type,
                    top_k,
                ),
                file_name=file_reference,
            )
        )

        search_time = (
            time.perf_counter()
            - search_start
        )

        print(
            f"ChromaDB search: "
            f"{search_time:.2f} seconds"
        )

        # -----------------------------------------
        # 6. Handle no retrieval results
        # -----------------------------------------

        if not retrieved_chunks:

            return (
                self._handle_no_results(
                    question_type=question_type,
                    files=files,
                    repository_summary=repository_summary,
                )
            )

        # -----------------------------------------
        # 7. Build prompt
        # -----------------------------------------

        prompt_start = time.perf_counter()

        prompt = (
            self.prompt_builder.build_prompt(
                question=question,
                retrieved_chunks=retrieved_chunks,
                question_type=question_type,
                repository_summary=repository_summary,
            )
        )

        prompt_time = (
            time.perf_counter()
            - prompt_start
        )

        print(
            f"Prompt building: "
            f"{prompt_time:.2f} seconds"
        )

        # -----------------------------------------
        # 8. Generate AI response
        # -----------------------------------------

        llm_start = time.perf_counter()

        answer = (
            self.llm_service.generate_response(
                prompt
            )
        )

        llm_time = (
            time.perf_counter()
            - llm_start
        )

        print(
            f"LLM response: "
            f"{llm_time:.2f} seconds"
        )

        # -----------------------------------------
        # 9. Build sources
        # -----------------------------------------

        sources = (
            self._build_sources(
                retrieved_chunks
            )
        )

        # -----------------------------------------
        # 10. Log total request time
        # -----------------------------------------

        total_time = (
            time.perf_counter()
            - total_start
        )

        print(
            f"Total chat request: "
            f"{total_time:.2f} seconds"
        )

        print("=" * 60 + "\n")

        # -----------------------------------------
        # 11. Return result
        # -----------------------------------------

        return {
            "answer": answer,
            "sources": sources,
            "question_type": question_type,
        }

    def _handle_structure_question(
        self,
        files: list,
        question_type: str,
        total_start: float,
    ) -> dict:
        """
        Handle repository structure questions
        without calling the LLM.
        """

        structure = (
            self.project_service.build_structure(
                files
            )
        )

        answer = (
            "Here is the project structure based "
            "on the files analyzed during "
            "repository indexing:\n\n"
            f"```\n{structure}\n```"
        )

        total_time = (
            time.perf_counter()
            - total_start
        )

        print(
            "Repository structure generated: "
            f"{total_time:.2f} seconds"
        )

        return {
            "answer": answer,
            "sources": [],
            "question_type": question_type,
        }

    def _handle_no_results(
        self,
        question_type: str,
        files: list,
        repository_summary: str,
    ) -> dict:
        """
        Handle questions when ChromaDB does not
        return relevant chunks.
        """

        if question_type == "technology":

            answer = (
                "I couldn't retrieve enough code "
                "context to confidently identify "
                "the technologies used in this "
                "repository.\n\n"
                f"Repository summary:\n"
                f"{repository_summary}"
            )

        elif question_type == "repository_overview":

            answer = (
                "I couldn't retrieve enough "
                "repository context to provide "
                "an accurate project overview."
            )

        elif question_type == "architecture":

            answer = (
                "I couldn't find enough relevant "
                "repository code to accurately "
                "describe the project architecture."
            )

        else:

            answer = (
                "I couldn't find relevant "
                "information in the repository."
            )

        return {
            "answer": answer,
            "sources": [],
            "question_type": question_type,
        }

    def _extract_file_reference(
        self,
        question: str,
    ) -> str | None:
        """
        Extract an explicit filename from the user's question.

        Example:
            "Explain repository_service.py"
            -> "repository_service.py"
        """

        pattern = (
            r"\b[\w\-.]+(?:"
            + "|".join(
                re.escape(extension)
                for extension
                in self.question_service.FILE_EXTENSIONS
            )
            + r")\b"
        )

        match = re.search(
            pattern,
            question,
            re.IGNORECASE,
        )

        if not match:
            return None

        return match.group(0)

    def _build_search_query(
        self,
        question: str,
        question_type: str,
    ) -> str:
        """
        Expand search queries based on question type
        to improve semantic retrieval.
        """

        search_prefixes = {

            "repository_overview": (
                "project purpose application "
                "features functionality "
            ),

            "architecture": (
                "architecture application flow "
                "frontend backend services "
                "controllers models database "
            ),

            "technology": (
                "programming language framework "
                "dependencies libraries database "
                "configuration package "
            ),

            "file_question": (
                "file implementation code "
            ),

            "code_question": (
                "code implementation function "
                "class method logic "
            ),
        }

        prefix = (
            search_prefixes.get(
                question_type,
                "",
            )
        )

        return (
            f"{prefix}{question}"
        ).strip()

    def _get_top_k(
        self,
        question_type: str,
        default_top_k: int,
    ) -> int:
        """
        Select the number of chunks based on
        question complexity.
        """

        if question_type == "architecture":
            return 8

        if question_type == "repository_overview":
            return 8

        if question_type == "technology":
            return 8

        return default_top_k

    def _build_sources(
        self,
        retrieved_chunks: list,
    ) -> list:
        """
        Build unique source information from
        retrieved ChromaDB chunks.
        """

        sources = []

        for chunk in retrieved_chunks:

            file_path = chunk.get(
                "file_path"
            )

            file_name = chunk.get(
                "file_name"
            )

            distance = chunk.get(
                "distance"
            )

            if not file_path:
                continue

            relevance = (
                round(
                    1 / (
                        1 + distance
                    ),
                    3,
                )
                if distance is not None
                else None
            )

            source = {
                "file": file_name,
                "path": file_path,
                "relevance": relevance,
            }

            already_exists = any(
                existing["path"]
                == file_path
                for existing in sources
            )

            if not already_exists:

                sources.append(
                    source
                )

        return sources