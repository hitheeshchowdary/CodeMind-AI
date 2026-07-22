from typing import Dict, Any


class PromptBuilder:
    """
    Builds prompts for the LLM using retrieved repository chunks.
    """

    SYSTEM_PROMPT = """
You are CodeMind AI, an AI Repository Assistant.

Your job is to answer questions ONLY using the provided repository context.

Rules:
1. Use only the provided repository context.
2. Do NOT make up functions, files, or implementations.
3. If the answer is not found in the context, reply:
   "I couldn't find that information in the repository."
4. Explain code clearly and concisely.
5. Mention relevant filenames whenever possible.
""".strip()

    def build_prompt(
        self,
        question: str,
        retrieved_chunks: Dict[str, Any]
    ) -> str:
        """
        Builds a prompt from ChromaDB search results.

        Args:
            question: User's question.
            retrieved_chunks: Result returned by ChromaDB.

        Returns:
            Formatted prompt string.
        """

        context = []

        documents = retrieved_chunks.get("documents", [[]])
        metadatas = retrieved_chunks.get("metadatas", [[]])

        if documents and metadatas:

            for document, metadata in zip(documents[0], metadatas[0]):

                file_name = metadata.get("file_name", "Unknown File")
                file_path = metadata.get("file_path", "")

                context.append(
                    f"""
File: {file_name}
Path: {file_path}

Code:
{document}

------------------------------------------------------------
""".strip()
                )

        repository_context = "\n\n".join(context)

        prompt = f"""
{self.SYSTEM_PROMPT}

==================== Repository Context ====================

{repository_context}

============================================================

User Question:
{question}

Answer:
""".strip()

        return prompt