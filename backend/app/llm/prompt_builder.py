class PromptBuilder:
    """
    Builds context-aware prompts for RepoMind AI.
    """

    SYSTEM_PROMPT = """
You are RepoMind AI, an expert AI repository assistant.

Your task is to answer questions using ONLY the repository context provided.

Important rules:

1. Use only the provided repository context.
2. Do not invent files, classes, functions, variables, APIs, or implementations.
3. If the repository context does not contain enough information, clearly say:
   "I couldn't find that information in the repository."
4. Give a direct and clear answer before adding technical details.
5. Mention relevant filenames when explaining code.
6. For architecture questions, infer relationships only when they are clearly supported by the provided files and code.
7. For project overview questions, explain the project's purpose based on the repository content.
8. Do not claim that a technology is used unless it appears in the provided repository context.
9. Use headings and bullet points when they improve readability.
10. Do not mention that you are an AI language model.
""".strip()

    def build_prompt(
        self,
        question: str,
        retrieved_chunks: list,
        question_type: str = "general",
        repository_summary: str = "",
    ) -> str:
        """
        Build a repository-aware LLM prompt.
        """

        context_blocks = []

        for chunk in retrieved_chunks:
            context_blocks.append(
                f"""
File: {chunk.get("file_name", "Unknown")}
Path: {chunk.get("file_path", "")}
Language: {chunk.get("language", "")}
Chunk Number: {chunk.get("chunk_index", 0)}

Content:
{chunk.get("content", "")}
""".strip()
            )

        repository_context = "\n\n".join(context_blocks)

        return f"""
{self.SYSTEM_PROMPT}

Question Category:
{question_type}

Repository Metadata:
{repository_summary}

================ REPOSITORY CONTEXT ================

{repository_context}

=====================================================

User Question:
{question}

Answer the user's question clearly and accurately using
only the information above.

Answer:
""".strip()