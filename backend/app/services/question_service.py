import re


class QuestionService:
    """
    Classifies repository questions so RepoMind AI can
    select the appropriate retrieval and answer strategy.
    """

    REPOSITORY_OVERVIEW_KEYWORDS = [
        "what is this project",
        "what does this project do",
        "what does the project do",
        "explain this project",
        "describe this project",
        "project overview",
        "about this project",
        "tell me about this project",
        "project purpose",
        "purpose of this project",
    ]

    PROJECT_STRUCTURE_KEYWORDS = [
        "project structure",
        "repository structure",
        "folder structure",
        "file structure",
        "directory structure",
        "structure of this project",
        "structure of the project",
        "explain the structure",
        "show the structure",
        "show project structure",
    ]

    ARCHITECTURE_KEYWORDS = [
        # Explicit architecture
        "architecture",
        "project architecture",
        "system architecture",
        "application architecture",

        # System / application behaviour
        "how does this project work",
        "how does the project work",
        "how does this system work",
        "how does the system work",
        "how does the application work",
        "how does the application work",

        # Frontend / backend communication
        "how does frontend communicate",
        "how does the frontend communicate",
        "how does backend communicate",
        "how does the backend communicate",
        "frontend backend communication",
        "frontend and backend communication",
        "frontend communicate with backend",
        "backend communicate with frontend",

        # Flow / pipeline / workflow
        "data flow",
        "workflow",
        "application flow",
        "system flow",
        "request flow",
        "execution flow",
        "complete flow",
        "end to end flow",
        "end-to-end flow",
        "pipeline",
        "processing pipeline",
        "indexing pipeline",
        "repository indexing",
        "upload to searchable",
        "upload to being searchable",

        # Component relationships
        "how do the components work together",
        "how do components work together",
        "how do the services work together",
        "how do backend services work together",
        "how do the modules work together",
        "how do the modules interact",
        "how do the components interact",
        "how do these components work together",
        "how do these components interact",

        # Repository-level reasoning
        "repository level",
        "repository-level",
        "across files",
        "across multiple files",
        "multiple components",
        "multiple services",

        # Agentic RAG / system workflow
        "agentic rag",
        "agentic workflow",
        "agentic rag workflow",
        "how does a user question flow",
        "user question flow",
        "question flow",
        "question to answer flow",

        # RAG path comparison
        "difference between the fast rag path",
        "difference between fast rag",
        "fast rag path and agentic rag path",
    ]

    TECHNOLOGY_KEYWORDS = [
        "technologies",
        "technology stack",
        "tech stack",
        "framework",
        "frameworks",
        "database",
        "databases",
        "libraries",
        "dependencies",
        "programming language",
        "programming languages",
        "which technology",
        "what technology",
        "what technologies",
        "tools used",
        "packages used",
    ]

    FILE_EXTENSIONS = [
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".html",
        ".css",
        ".json",
        ".md",
        ".xml",
        ".yml",
        ".yaml",
    ]

    def classify_question(
        self,
        question: str,
    ) -> str:
        """
        Returns one of:

        - repository_overview
        - project_structure
        - architecture
        - technology
        - file_question
        - code_question
        - general
        """

        normalized_question = (
            question.lower()
            .strip()
        )

        if not normalized_question:
            return "general"

        # -----------------------------------------
        # File-specific question
        # -----------------------------------------

        if self._contains_file_reference(
            normalized_question
        ):
            return "file_question"

        # -----------------------------------------
        # Project structure
        # -----------------------------------------

        if self._contains_keyword(
            normalized_question,
            self.PROJECT_STRUCTURE_KEYWORDS,
        ):
            return "project_structure"

        # -----------------------------------------
        # Repository overview
        # -----------------------------------------

        if self._contains_keyword(
            normalized_question,
            self.REPOSITORY_OVERVIEW_KEYWORDS,
        ):
            return "repository_overview"

        # -----------------------------------------
        # Architecture
        # -----------------------------------------

        if self._contains_keyword(
            normalized_question,
            self.ARCHITECTURE_KEYWORDS,
        ):
            return "architecture"

        # -----------------------------------------
        # Architecture / component relationships
        #
        # This check is intentionally BEFORE
        # technology detection.
        #
        # Example:
        # "How do parser, chunking, embedding,
        # and vector database components work together?"
        #
        # Although "database" appears in the question,
        # the actual intent is architecture.
        # -----------------------------------------

        ARCHITECTURE_RELATIONSHIP_PATTERNS = [
            "work together",
            "works together",
            "interact",
            "communicate with",
            "communicate between",
            "connect",
            "connected together",
            "fit together",
            "work with each other",
            "components work",
            "services work",
            "modules work",
        ]

        if self._contains_keyword(
            normalized_question,
            ARCHITECTURE_RELATIONSHIP_PATTERNS,
        ):
            return "architecture"

        # -----------------------------------------
        # Technology
        # -----------------------------------------

        if self._contains_keyword(
            normalized_question,
            self.TECHNOLOGY_KEYWORDS,
        ):
            return "technology"

        # -----------------------------------------
        # Code question
        # -----------------------------------------

        code_patterns = [
            "explain",
            "what does",
            "how does",
            "function",
            "class",
            "method",
            "code",
            "implementation",
            "logic",
        ]

        if self._contains_keyword(
            normalized_question,
            code_patterns,
        ):
            return "code_question"

        # -----------------------------------------
        # General
        # -----------------------------------------

        return "general"

    def _contains_keyword(
        self,
        question: str,
        keywords: list[str],
    ) -> bool:
        """
        Check whether the question contains
        any known keyword or phrase.
        """

        return any(
            keyword in question
            for keyword in keywords
        )

    def _contains_file_reference(
        self,
        question: str,
    ) -> bool:
        """
        Detect explicit file names such as:

        App.py
        UserService.java
        package.json
        """

        pattern = (
            r"\b[\w\-.]+(?:"
            + "|".join(
                re.escape(extension)
                for extension
                in self.FILE_EXTENSIONS
            )
            + r")\b"
        )

        return bool(
            re.search(
                pattern,
                question,
                re.IGNORECASE,
            )
        )