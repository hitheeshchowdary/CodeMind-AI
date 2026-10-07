from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.agents.router import AgentRouter
from app.agents.rag_node import fast_rag_node
from app.agents.code_agent import code_search_node
from app.agents.query_planner import query_planner_node
from app.agents.verifier_agent import evidence_verifier_node
from app.agents.answer_agent import answer_generator_node
from app.agents.evidence_ranker import evidence_ranker_node


router = AgentRouter()


def route_question(state: AgentState) -> AgentState:
    """
    Route the question using the existing question classifier.
    """

    return router.route(state)


def choose_route(state: AgentState) -> str:
    """
    Choose between the existing fast RAG path
    and the Agentic RAG path.
    """

    return state["route"]


def choose_after_verification(state: AgentState) -> str:
    """
    Decide whether to retry retrieval or generate
    the final answer.
    """

    verification_status = state.get(
        "verification_status",
        "insufficient",
    )

    retry_count = state.get(
        "retry_count",
        0,
    )

    if (
        verification_status == "insufficient"
        and retry_count < 1
    ):
        return "retry"

    return "answer"


def build_agent_graph():
    """
    Build the RepoMind AI hybrid Agentic RAG graph.
    """

    graph = StateGraph(AgentState)

    # -----------------------------------------
    # Nodes
    # -----------------------------------------

    graph.add_node(
        "router",
        route_question,
    )

    graph.add_node(
        "fast_rag",
        fast_rag_node,
    )

    graph.add_node(
        "query_planner",
        query_planner_node,
    )

    graph.add_node(
        "code_search",
        code_search_node,
    )

    graph.add_node(
        "evidence_ranker",
        evidence_ranker_node,
    )

    graph.add_node(
        "evidence_verifier",
        evidence_verifier_node,
    )

    graph.add_node(
        "answer_generator",
        answer_generator_node,
    )

    # -----------------------------------------
    # Entry
    # -----------------------------------------

    graph.add_edge(
        START,
        "router",
    )

    # -----------------------------------------
    # Router
    # -----------------------------------------

    graph.add_conditional_edges(
        "router",
        choose_route,
        {
            "fast_rag": "fast_rag",
            "agentic": "query_planner",
        },
    )

    # -----------------------------------------
    # Agentic retrieval pipeline
    # -----------------------------------------

    graph.add_edge(
        "query_planner",
        "code_search",
    )

    graph.add_edge(
        "code_search",
        "evidence_ranker",
    )

    graph.add_edge(
        "evidence_ranker",
        "evidence_verifier",
    )

    # -----------------------------------------
    # Verification decision
    # -----------------------------------------

    graph.add_conditional_edges(
        "evidence_verifier",
        choose_after_verification,
        {
            "retry": "query_planner",
            "answer": "answer_generator",
        },
    )

    # -----------------------------------------
    # End nodes
    # -----------------------------------------

    graph.add_edge(
        "answer_generator",
        END,
    )

    graph.add_edge(
        "fast_rag",
        END,
    )

    return graph.compile()


agent_graph = build_agent_graph()