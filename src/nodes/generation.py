"""
צומת 4: Generation.
מנסח תשובה ללקוח על סמך המידע שנאסף (מ-RAG או מ-n8n), בטון נציג שירות אדיב ומדויק.
"""

from langchain.messages import HumanMessage, SystemMessage

from src.model_provider import get_chat_model
from src.state import GreenShopState

GENERATION_SYSTEM_PROMPT = """
את/ה נציג/ת שירות לקוחות וירטואלי/ת של GreenShop, חנות אונליין ידידותית לסביבה.
ענה/י ללקוח בעברית, בטון מנומס, ברור ותמציתי.
התבסס/י אך ורק על המידע שסופק לך למטה - אל תמציא/י פרטים שאינם מופיעים בו.
אם המידע שסופק אינו מספיק כדי לענות, ציין/י זאת בכנות והצע/י לפנות לנציג אנושי.
"""


def generation_node(state: GreenShopState) -> dict:
    model = get_chat_model()

    context_parts = []
    if state.get("retrieved_context"):
        context_parts.append(f"מידע מבסיס הידע:\n{state['retrieved_context']}")
    if state.get("tool_result"):
        context_parts.append(f"תוצאת בדיקה במערכות החברה:\n{state['tool_result']}")
    if state.get("tool_agent_message"):
        context_parts.append(
            "לא בוצעה בדיקה במערכות החברה כי חסר פרט מזהה. "
            f"יש לבקש מהלקוח את הפרט החסר, בהתאם לכך:\n{state['tool_agent_message']}"
        )
    if state.get("guardrail_feedback"):
        context_parts.append(
            f"הטיוטה הקודמת נפסלה על ידי בקרת האיכות מהסיבה הבאה - יש לתקן אותה: {state['guardrail_feedback']}"
        )

    context_text = "\n\n".join(context_parts) if context_parts else "לא נמצא מידע רלוונטי."

    response = model.invoke(
        [
            SystemMessage(content=GENERATION_SYSTEM_PROMPT),
            HumanMessage(content=f"שאלת הלקוח: {state['user_message']}\n\n{context_text}"),
        ]
    )

    return {"draft_answer": response.content}
