from app.agents.state import AgentState


class QueryPlanner:
    """
    Generates targeted evidence queries for complex
    repository-level questions.

    On the first attempt, queries focus on broad semantic
    retrieval. If verification fails, the planner generates
    a different set of targeted queries for the retry.
    """

    def plan(self, state: AgentState) -> AgentState:
        question = state["question"]

        question_type = state.get(
            "question_type",
            "general",
        )

        retry_count = state.get(
            "retry_count",
            0,
        )

        # Increment retry count when the previous
        # verification attempt found insufficient evidence.
        if state.get("verification_status") == "insufficient":
            retry_count += 1

        queries = []

        # =================================================
        # RETRY STRATEGY
        # =================================================

        if retry_count > 0:

            print(
                "[QueryPlanner] Using adaptive retry strategy"
            )

            # ---------------------------------------------
            # Architecture retry
            # ---------------------------------------------

            if question_type == "architecture":
                queries = [
                    (
                        f"backend main entrypoint API routers "
                        f"services repository processing flow {question}"
                    ),
                    (
                        f"frontend components API calls "
                        f"request response communication {question}"
                    ),
                    (
                        f"repository indexing parser chunk "
                        f"embedding vector storage pipeline {question}"
                    ),
                    (
                        f"LLM prompt generation answer response "
                        f"chat service workflow {question}"
                    ),
                ]

            # ---------------------------------------------
            # Repository overview retry
            # ---------------------------------------------

            elif question_type == "repository_overview":
                queries = [
                    (
                        f"README project purpose features "
                        f"main modules implementation {question}"
                    ),
                    (
                        f"application entrypoint API services "
                        f"repository workflow implementation {question}"
                    ),
                    (
                        f"frontend backend components "
                        f"communication implementation {question}"
                    ),
                ]

            # ---------------------------------------------
            # Technology retry
            # ---------------------------------------------

            elif question_type == "technology":
                queries = [
                    (
                        f"requirements dependencies installed "
                        f"Python packages frameworks {question}"
                    ),
                    (
                        f"frontend package.json React dependencies "
                        f"backend Python libraries {question}"
                    ),
                    (
                        f"database vector database embeddings "
                        f"LLM infrastructure configuration {question}"
                    ),
                ]

            # ---------------------------------------------
            # Code / file retry
            # ---------------------------------------------

            else:
                queries = [
                    (
                        f"exact implementation source code "
                        f"function class method definition {question}"
                    ),
                    (
                        f"usage caller imports dependencies "
                        f"execution flow {question}"
                    ),
                ]

        # =================================================
        # FIRST RETRIEVAL STRATEGY
        # =================================================

        else:

            # ---------------------------------------------
            # Architecture
            # ---------------------------------------------

            if question_type == "architecture":
                queries = [
                    (
                        f"project architecture major components "
                        f"modules services {question}"
                    ),
                    (
                        f"frontend backend communication "
                        f"API request flow {question}"
                    ),
                    (
                        f"backend services repository processing "
                        f"workflow {question}"
                    ),
                    (
                        f"database storage embeddings vector database "
                        f"LLM components {question}"
                    ),
                ]

            # ---------------------------------------------
            # Repository overview
            # ---------------------------------------------

            elif question_type == "repository_overview":
                queries = [
                    (
                        f"project purpose main functionality "
                        f"features {question}"
                    ),
                    (
                        f"main application components "
                        f"repository workflow {question}"
                    ),
                ]

            # ---------------------------------------------
            # Technology
            # ---------------------------------------------

            elif question_type == "technology":
                queries = [
                    (
                        f"programming languages frameworks "
                        f"libraries dependencies {question}"
                    ),
                    (
                        f"database storage infrastructure "
                        f"configuration technologies {question}"
                    ),
                ]

            # ---------------------------------------------
            # Code / file questions
            # ---------------------------------------------

            else:
                queries = [
                    (
                        f"code implementation function class "
                        f"method logic {question}"
                    ),
                ]

        print(
            f"[QueryPlanner] Generated "
            f"{len(queries)} search queries"
        )

        print(
            f"[QueryPlanner] Retry count: "
            f"{retry_count}"
        )

        return {
            **state,
            "search_queries": queries,
            "retry_count": retry_count,
        }


query_planner = QueryPlanner()


def query_planner_node(
    state: AgentState,
) -> AgentState:
    """
    LangGraph node wrapper for the query planner.
    """

    return query_planner.plan(state)