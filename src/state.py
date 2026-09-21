"""
הגדרת ה-State של הגרף - המידע שעובר ומצטבר בין הצמתים לאורך כל השיחה.
"""

from typing import Literal, Optional, TypedDict


class GreenShopState(TypedDict):
    # ההודעה המקורית שהלקוח שלח
    user_message: str

    # תוצאת צומת 1 (Input Guardrail & Router): לאן לנתב, ולמה אם נחסם
    is_input_valid: bool
    block_reason: Optional[str]
    route: Optional[Literal["knowledge_question", "customer_specific"]]

    # תוצאת צומת 2 (Retrieval): קטעי מידע רלוונטיים מבסיס הידע
    retrieved_context: Optional[str]

    # תוצאת צומת 3 (Tool Execution): מה n8n החזיר (כטקסט, כפי שהכלי מחזיר אותו)
    tool_result: Optional[str]

    # אם הסוכן בחר לא לקרוא לכלי (למשל חסר מספר הזמנה) - התשובה שניסח במקום
    tool_agent_message: Optional[str]

    # תוצאת צומת 4 (Generation): התשובה שנוסחה ללקוח
    draft_answer: Optional[str]

    # תוצאת צומת 5 (Output Guardrail)
    is_output_safe: bool
    final_answer: Optional[str]
    guardrail_feedback: Optional[str]
    regeneration_attempts: int


def build_initial_state(user_message: str) -> GreenShopState:
    """
    בונה State התחלתי עם כל השדות מאותחלים.
    מרוכז כאן כדי שהוספת שדה ל-State תדרוש שינוי במקום אחד בלבד,
    ולא בכל מקום שמפעיל את הגרף (שרת, בדיקות).
    """
    return {
        "user_message": user_message,
        "is_input_valid": True,
        "block_reason": None,
        "route": None,
        "retrieved_context": None,
        "tool_result": None,
        "tool_agent_message": None,
        "draft_answer": None,
        "is_output_safe": False,
        "final_answer": None,
        "guardrail_feedback": None,
        "regeneration_attempts": 0,
    }
