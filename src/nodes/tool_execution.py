"""
צומת 3: Tool Execution.
מופעל כשהלקוח מבקש מידע/פעולה שקשורים להזמנה ספציפית שלו.
הסוכן מחליט בעצמו (בסגנון ReAct) איך לקרוא לכלי call_n8n_webhook, על סמך הודעת הלקוח.
"""

from langchain.agents import create_agent
from langchain.messages import HumanMessage

from src.model_provider import get_chat_model
from src.state import GreenShopState
from src.tools.n8n_tool import call_n8n_webhook

TOOL_EXECUTION_SYSTEM_PROMPT = """
את/ה סוכן שירות לקוחות של GreenShop.
המשתמש פנה עם בקשה שקשורה להזמנה ספציפית שלו (סטטוס הזמנה או בקשת החזר כספי).
עליך לחלץ מתוך הודעת הלקוח את מספר ההזמנה (אם צוין) ואת סוג הבקשה,
ולהשתמש בכלי call_n8n_webhook כדי לברר את המידע או לבצע את הפעולה בפועל.
אם הלקוח לא ציין מספר הזמנה, בקש זאת ממנו בתשובתך במקום להשתמש בכלי.
"""


def tool_execution_node(state: GreenShopState) -> dict:
    model = get_chat_model()
    agent = create_agent(
        model=model,
        tools=[call_n8n_webhook],
        system_prompt=TOOL_EXECUTION_SYSTEM_PROMPT,
    )

    response = agent.invoke({"messages": [HumanMessage(content=state["user_message"])]})

    # מחפשים אם הסוכן אכן קרא לכלי, ואם כן - שולפים את התוצאה שהתקבלה מ-n8n
    tool_result = None
    for message in response["messages"]:
        if getattr(message, "name", None) == "call_n8n_webhook":
            tool_result = message.content
            break

    # אם הסוכן בחר לא לקרוא לכלי (למשל הלקוח לא ציין מספר הזמנה),
    # התשובה שלו היא המידע היחיד שיש - שומרים אותה כדי שצומת ה-Generation
    # יוכל לבקש מהלקוח את הפרט החסר במקום לענות תשובה גנרית.
    tool_agent_message = None
    if tool_result is None:
        last_message = response["messages"][-1]
        if getattr(last_message, "content", None):
            tool_agent_message = last_message.content

    return {"tool_result": tool_result, "tool_agent_message": tool_agent_message}
