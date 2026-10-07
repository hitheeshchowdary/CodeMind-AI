from app.agents.state import AgentState
from app.llm.prompt_builder import PromptBuilder
from app.llm.llm_service import LLMService


class AnswerGeneratorAgent:
    """
    Agent responsible for generating a repository-grounded
    answer from verified repository evidence.
    """

    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.llm_service = LLMService()

    def generate(self, state: AgentState) -> AgentState:
        question = state["question"]

        question_type = state.get(
            "question_type",
            "general",
        )

        retrieved_chunks = state.get(
            "retrieved_chunks",
            [],
        )
        # Keep the verifier's full evidence, but send only the
        # strongest evidence to the final LLM.
        if question_type in {"architecture", "repository_overview"}:
            llm_chunks = retrieved_chunks[:5]
        else:
            llm_chunks = retrieved_chunks[:4]

        repository_summary = state.get(
            "repository_summary",
            "",
        )

        verification_status = state.get(
            "verification_status",
            "insufficient",
        )

        # -----------------------------------------
        # No evidence
        # -----------------------------------------

        if not retrieved_chunks:
            return {
                **state,
                "answer": (
                    "I couldn't find that information "
                    "in the repository."
                ),
                "sources": [],
            }

        # -----------------------------------------
        # Do not generate unsupported answers
        # -----------------------------------------

        if verification_status == "insufficient":
            return {
                **state,
                "answer": (
                    "I couldn't find enough reliable "
                    "evidence in the repository to "
                    "answer this question confidently."
                ),
                "sources": [],
            }

        print(
            "[AnswerGeneratorAgent] "
            f"Generating grounded answer from "
            f"{len(llm_chunks)} verified chunks"
        )

        # -----------------------------------------
        # Build repository prompt
        # -----------------------------------------

        prompt = self.prompt_builder.build_prompt(
            question=question,
            retrieved_chunks=llm_chunks,
            question_type=question_type,
            repository_summary=repository_summary,
        )

        # -----------------------------------------
        # Additional grounding instructions
        # -----------------------------------------

        grounding_instructions = """

STRICT EVIDENCE RULES FOR THIS ANSWER:

1. Use ONLY facts explicitly supported by the
   repository context.

2. Do NOT invent or assume:
   - files
   - classes
   - functions
   - APIs
   - data flows
   - technologies
   - responsibilities
   - relationships between components

3. For architecture questions, describe a relationship
   only when the provided repository files clearly support it.

4. Do NOT infer that one component calls another unless
   the provided code or configuration demonstrates it.

5. If something is unclear or missing from the retrieved
   evidence, explicitly say that the repository evidence
   does not establish it.

6. Prefer precise filenames, classes, functions, and
   implementation details found in the evidence.

7. Separate confirmed implementation details from
   reasonable interpretation.

8. Never describe planned or future functionality as
   currently implemented.

9. Keep the answer focused on the user's question.

10. Accuracy is more important than completeness.
"""

        prompt = (
            prompt
            + "\n\n"
            + grounding_instructions.strip()
        )

        # -----------------------------------------
        # Generate answer
        # -----------------------------------------

        answer = self.llm_service.generate_response(
            prompt
        )

        # -----------------------------------------
        # Build unique sources
        # -----------------------------------------

        sources = []
        seen_files = set()

        for chunk in retrieved_chunks:

            file_path = chunk.get(
                "file_path",
                "",
            )

            if not file_path:
                continue

            if file_path in seen_files:
                continue

            seen_files.add(file_path)

            distance = chunk.get(
                "distance",
                0,
            )

            if isinstance(
                distance,
                (int, float),
            ):
                relevance = 1 / (
                    1 + distance
                )
            else:
                relevance = None

            sources.append(
                {
                    "file": chunk.get(
                        "file_name",
                        "Unknown",
                    ),
                    "path": file_path,
                    "relevance": relevance,
                }
            )

        print(
            "[AnswerGeneratorAgent] "
            f"Generated grounded answer using "
            f"{len(sources)} source files"
        )

        return {
            **state,
            "answer": answer,
            "sources": sources,
        }


answer_generator_agent = AnswerGeneratorAgent()


def answer_generator_node(
    state: AgentState,
) -> AgentState:
    """
    LangGraph node wrapper for the Answer Generator Agent.
    """

    return answer_generator_agent.generate(state)