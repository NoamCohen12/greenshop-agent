"""
כלי (Tool) שמאפשר לסוכן לבצע פעולה בפועל במערכות GreenShop,
על ידי שליחת בקשה ל-workflow חיצוני שרץ ב-n8n.
"""

import os

import requests
from langchain.tools import tool


@tool
def call_n8n_webhook(request_type: str, order_id: str, details: str = "") -> dict:
    """
    שולח בקשה למערכת n8n לביצוע פעולה על הזמנת לקוח.

    יש להשתמש בכלי הזה כאשר הלקוח מבקש מידע או פעולה שקשורים
    להזמנה ספציפית שלו, כגון בדיקת סטטוס משלוח או בקשת החזר כספי.

    Args:
        request_type: סוג הבקשה. אחד מהערכים: "order_status" (בדיקת סטטוס הזמנה)
            או "refund_request" (בקשת החזר כספי).
        order_id: מספר ההזמנה של הלקוח.
        details: פרטים נוספים רלוונטיים לבקשה (למשל, סיבת ההחזר).
    """
    webhook_url = os.environ.get("N8N_WEBHOOK_URL")
    if not webhook_url:
        return {"success": False, "error": "N8N_WEBHOOK_URL לא מוגדר ב-.env"}

    try:
        response = requests.post(
            webhook_url,
            json={"request_type": request_type, "order_id": order_id, "details": details},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        return {"success": False, "error": str(error)}
