import re


class QuestionService:
    """
    Classifies repository questions so CodeMind AI can
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
        "architecture",
        "explain the architecture",
        "project architecture",
        "system architecture",
        "how does this project work",
        "how does the system work",
        "how does the application work",
        "data flow",
        "workflow",
        "application flow",
        "how does frontend communicate",
        "how does the backend work",
        "frontend backend communication",
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