"""
נקודת הכניסה של המערכת: מוודא שמסד הנתונים הוקטורי קיים לפני הפעלת השרת,
כדי שהרצה על מחשב נקי (docker-compose up) תעבוד ללא שלבים ידניים.
"""

import os

from dotenv import load_dotenv

load_dotenv()

from src.rag.vector_store import CHROMA_PERSIST_DIR, build_vector_store


def ensure_vector_store_exists():
    if os.path.isdir(CHROMA_PERSIST_DIR) and os.listdir(CHROMA_PERSIST_DIR):
        print("מסד הנתונים הוקטורי כבר קיים - מדלג על הבנייה.")
        return

    print("בונה מסד נתונים וקטורי מתוך data/knowledge_base ...")
    build_vector_store()
    print("מסד הנתונים הוקטורי נבנה בהצלחה.")


if __name__ == "__main__":
    ensure_vector_store_exists()

    from src.server import app

    app.run(host="0.0.0.0", port=5000)
