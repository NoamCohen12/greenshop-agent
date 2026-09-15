"""
הגדרת הגרף המלא של GreenShop: מחבר את 5 הצמתים באמצעות LangGraph,
כולל ה-Conditional Edges שהופכים אותו לזרימה אוטונומית ולא רצף קבוע.
"""

from langgraph.graph import END, START, StateGraph

from src.nodes.generation import generation_node
from src.nodes.input_guardrail_router import input_guardrail_router_node, route_after_input_guardrail
from src.nodes.output_guardrail import output_guardrail_node
from src.nodes.retrieval import retrieval_node
from src.nodes.tool_execution import tool_execution_node
from src.state import GreenShopState

BLOCKED_MESSAGE = "מצטערים, לא נוכל לסייע בבקשה זו. אנא פנה בשאלה הקשורה לשירות הלקוחות של GreenShop."


def blocked_input_node(state: GreenShopState) -> dict:
    """מטפל בהודעות שנפסלו על ידי ה-Input Guardrail - מחזיר תשובת סירוב מנומסת."""
    return {"is_output_safe": True, "final_answer": BLOCKED_MESSAGE}


def route_after_output_guardrail(state: GreenShopState) -> str:
    """Conditional Edge: אם התשובה נפסלה ועוד נשארו ניסיונות, חוזרים ל-generation לתיקון."""
    if state["is_output_safe"] or state["final_answer"] is not None:
        return "end"
    return "retry_generation"


def build_graph():
    graph = StateGraph(GreenShopState)

    graph.add_node("input_guardrail_router", input_guardrail_router_node)
    graph.add_node("blocked_input", blocked_input_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("tool_execution", tool_execution_node)
    graph.add_node("generation", generation_node)
    graph.add_node("output_guardrail", output_guardrail_node)

    graph.add_edge(START, "input_guardrail_router")

    graph.add_conditional_edges(
        "input_guardrail_router",
        route_after_input_guardrail,
        {
            "blocked": "blocked_input",
            "knowledge_question": "retrieval",
            "customer_specific": "tool_execution",
        },
    )

    graph.add_edge("retrieval", "generation")
    graph.add_edge("tool_execution", "generation")
    graph.add_edge("generation", "output_guardrail")

    graph.add_conditional_edges(
        "output_guardrail",
        route_after_output_guardrail,
        {
            "retry_generation": "generation",
            "end": END,
        },
    )

    graph.add_edge("blocked_input", END)

    return graph.compile()


greenshop_graph = build_graph()
