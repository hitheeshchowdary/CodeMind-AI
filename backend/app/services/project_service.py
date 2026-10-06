from collections import Counter
from pathlib import PurePath


class ProjectService:
    """
    Handles repository-level analysis such as:

    - Project structure
    - Project overview
    - Technology detection
    """

    def build_structure(
        self,
        files: list,
    ) -> str:
        """
        Build a clean repository file structure.
        """

        if not files:
            return "No files were found."

        paths = []

        for file in files:

            file_path = (
                file.get("path")
                or file.get("file_path")
                or ""
            )

            if file_path:
                paths.append(
                    file_path.replace(
                        "\\",
                        "/",
                    )
                )

        if not paths:
            return "No file paths were found."

        common_prefix = self._find_common_prefix(
            paths
        )

        relative_paths = []

        for path in paths:

            relative_path = path

            if common_prefix and path.startswith(
                common_prefix
            ):
                relative_path = path[
                    len(common_prefix):
                ].lstrip("/")

            relative_paths.append(
                relative_path
            )

        tree = {}

        for path in relative_paths:

            parts = [
                part
                for part in path.split("/")
                if part
            ]

            current = tree

            for part in parts:
                current = current.setdefault(
                    part,
                    {},
                )

        return self._format_tree(tree)

    def _find_common_prefix(
        self,
        paths: list[str],
    ) -> str:
        """
        Find the common parent directory of
        repository file paths.
        """

        if not paths:
            return ""

        split_paths = [
            path.split("/")
            for path in paths
        ]

        common_parts = []

        for parts in zip(*split_paths):

            if len(set(parts)) == 1:
                common_parts.append(parts[0])
            else:
                break

        if not common_parts:
            return ""

        return "/".join(
            common_parts
        )

    def _format_tree(
        self,
        tree: dict,
        prefix: str = "",
    ) -> str:
        """
        Convert a nested dictionary into a
        readable tree structure.
        """

        lines = []

        items = sorted(
            tree.items(),
            key=lambda item: (
                bool(item[1]),
                item[0].lower(),
            ),
        )

        for index, (name, children) in enumerate(
            items
        ):

            is_last = (
                index == len(items) - 1
            )

            connector = (
                "└── "
                if is_last
                else "├── "
            )

            lines.append(
                f"{prefix}{connector}{name}"
            )

            if children:

                extension = (
                    "    "
                    if is_last
                    else "│   "
                )

                lines.extend(
                    self._format_tree(
                        children,
                        prefix + extension,
                    ).splitlines()
                )

        return "\n".join(lines)

    def get_repository_summary(
        self,
        files: list,
    ) -> str:
        """
        Generate factual metadata about the repository.
        """

        if not files:
            return (
                "No repository files were found."
            )

        language_counter = Counter()
        extension_counter = Counter()

        for file in files:

            language = file.get(
                "language"
            )

            extension = file.get(
                "extension"
            )

            if language:
                language_counter[
                    language
                ] += 1

            if extension:
                extension_counter[
                    extension
                ] += 1

        lines = [
            f"Total files analyzed: {len(files)}"
        ]

        if language_counter:

            languages = ", ".join(
                f"{language} ({count})"
                for language, count
                in language_counter.most_common()
            )

            lines.append(
                f"Languages detected: {languages}"
            )

        if extension_counter:

            extensions = ", ".join(
                f"{extension} ({count})"
                for extension, count
                in extension_counter.most_common()
            )

            lines.append(
                f"File types: {extensions}"
            )

        return "\n".join(lines)

    def is_structure_question(
        self,
        question: str,
    ) -> bool:
        """
        Backward-compatible helper.
        """

        keywords = [
            "structure",
            "folder structure",
            "file structure",
            "repository structure",
            "project structure",
        ]

        normalized_question = (
            question.lower()
            .strip()
        )

        return any(
            keyword in normalized_question
            for keyword in keywords
        )