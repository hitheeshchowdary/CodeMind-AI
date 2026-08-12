class PromptBuilder:
    """
    Builds prompts for the LLM using retrieved repository chunks.
    """

    SYSTEM_PROMPT = """
You are CodeMind AI, an AI Repository Assistant.

Your job is to answer questions ONLY using the provided repository context.

Rules:
1. Use only the provided repository context.
2. Do NOT invent files, functions, variables, or implementations.
3. If the answer cannot be determined from the provided context, say:
   "I couldn't find that information in the repository."
4. Explain the code clearly and concisely.
5. Mention the relevant filename when explaining something.
6. Do not assume that code exists if it is not present in the context.
""".strip()

    def build_prompt(
        self,
        question: str,
        retrieved_chunks: list
    ) -> str:
        """
        Build an LLM prompt from retrieved repository chunks.
        """

        context = []

        for chunk in retrieved_chunks:

            context.append(
                f"""
File: {chunk["file_name"]}
Path: {chunk["file_path"]}
Language: {chunk["language"]}
Chunk: {chunk["chunk_index"]}

Code:
{chunk["content"]}

------------------------------------------------------------
""".strip()
            )

        repository_context = "\n\n".join(context)

        return f"""
{self.SYSTEM_PROMPT}

==================== Repository Context ====================

{repository_context}

============================================================

User Question:
{question}

Answer:
""".strip()