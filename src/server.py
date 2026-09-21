"""
שרת Flask שחושף את גרף GreenShop כ-API, ומאפשר תקשורת דו-כיוונית מול n8n.
"""

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request

from src.graph import greenshop_graph
from src.state import build_initial_state

app = Flask(__name__)


@app.route("/chat", methods=["POST"])
def chat():
    """מקבל הודעת לקוח, מריץ את הגרף, ומחזיר את התשובה הסופית."""
    body = request.get_json(silent=True) or {}
    user_message = body.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "יש לשלוח שדה 'message' לא ריק"}), 400

    result_state = greenshop_graph.invoke(build_initial_state(user_message))

    return jsonify({"answer": result_state["final_answer"]})


@app.route("/n8n-callback", methods=["POST"])
def n8n_callback():
    """
    Endpoint שמאפשר ל-n8n לקרוא בחזרה לשרת (למשל עדכון אסינכרוני על סטטוס פעולה).
    כרגע רק מקבל ומאשר קבלה - ניתן להרחיב בהמשך לפי הצורך.
    """
    body = request.get_json(silent=True) or {}
    print(f"התקבלה קריאה מ-n8n: {body}")
    return jsonify({"received": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
