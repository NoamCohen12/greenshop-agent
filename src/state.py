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

    # תוצאת צומת 3 (Tool Execution): מה n8n החזיר
    tool_result: Optional[dict]

    # תוצאת צומת 4 (Generation): התשובה שנוסחה ללקוח
    draft_answer: Optional[str]

    # תוצאת צומת 5 (Output Guardrail)
    is_output_safe: bool
    final_answer: Optional[str]
    guardrail_feedback: Optional[str]
    regeneration_attempts: int
