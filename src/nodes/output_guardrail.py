"""
צומת 5: Output Guardrail.
בודק את התשובה שנוסחה לפני שליחתה ללקוח - מניעת הזיות והבטחות חורגות ממדיניות החברה.
"""

from pydantic import BaseModel, Field

from src.model_provider import get_chat_model
from src.state import GreenShopState

MAX_REGENERATION_ATTEMPTS = 2

OUTPUT_GUARDRAIL_SYSTEM_PROMPT = """
את/ה בודק/ת בקרת איכות עבור תשובות של סוכן שירות הלקוחות של GreenShop.
בדוק/י את הטיוטה של התשובה מול המידע שסופק לסוכן, ופסול/י אותה רק אם:
- היא מכילה מידע שלא מופיע במידע שסופק (הזיה).
- היא מבטיחה ללקוח פיצוי, החזר כספי, או הנחה שלא צוינו במידע שסופק.
- היא כוללת תוכן לא הולם או לא מקצועי.

חשוב: מידע שהוחזר ממערכות החברה (כגון קוד קופון, סכום פיצוי או סטטוס הזמנה)
נחשב מאושר, ומותר לסוכן למסור אותו ללקוח.
"""


class OutputCheck(BaseModel):
    is_safe: bool = Field(description="האם התשובה עומדת בכל הכללים ובטוחה לשליחה")
    issue: str = Field(description="אם לא בטוחה - תיאור קצר של הבעיה. אחרת מחרוזת ריקה")


FALLBACK_ANSWER = "מצטערים, נדרש בירור נוסף מול נציג אנושי כדי לענות על בקשתך בצורה מדויקת."


def output_guardrail_node(state: GreenShopState) -> dict:
    model = get_chat_model()
    checker_model = model.with_structured_output(OutputCheck)

    source_parts = []
    if state.get("retrieved_context"):
        source_parts.append(f"מידע מבסיס הידע:\n{state['retrieved_context']}")
    if state.get("tool_result"):
        source_parts.append(f"נתונים שהוחזרו ממערכות החברה:\n{state['tool_result']}")
    if state.get("tool_agent_message"):
        source_parts.append(
            "חסר פרט מזהה ולכן לא בוצעה בדיקה במערכות החברה - "
            "תשובה שמבקשת מהלקוח את הפרט החסר היא תקינה."
        )

    source_info = "\n\n".join(source_parts) if source_parts else "אין מידע נוסף"
    check: OutputCheck = checker_model.invoke(
        [
            {"role": "system", "content": OUTPUT_GUARDRAIL_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"מידע שסופק לסוכן:\n{source_info}\n\nטיוטת תשובה לבדיקה:\n{state['draft_answer']}",
            },
        ]
    )

    if check.is_safe:
        return {"is_output_safe": True, "final_answer": state["draft_answer"]}

    attempts = state.get("regeneration_attempts", 0) + 1
    if attempts > MAX_REGENERATION_ATTEMPTS:
        return {"is_output_safe": False, "final_answer": FALLBACK_ANSWER, "regeneration_attempts": attempts}

    return {
        "is_output_safe": False,
        "guardrail_feedback": check.issue,
        "regeneration_attempts": attempts,
    }
