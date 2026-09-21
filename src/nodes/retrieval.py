"""
צומת 2: Retrieval (RAG).
מופעל כשהלקוח שואל שאלת ידע כללית (מדיניות, מפרט מוצר).
שולף את הקטעים הרלוונטיים ביותר מבסיס הידע הוקטורי ומוסיף אותם ל-State.
"""

from functools import lru_cache

from src.rag.vector_store import load_vector_store
from src.state import GreenShopState

NUM_RESULTS_TO_RETRIEVE = 3


@lru_cache(maxsize=1)
def get_vector_store():
    """
    טוען את המסד הוקטורי פעם אחת בלבד ושומר אותו בזיכרון.
    בלי זה, כל שאלה של לקוח הייתה פותחת מחדש את החיבור ל-ChromaDB.
    """
    return load_vector_store()


def retrieval_node(state: GreenShopState) -> dict:
    vector_store = get_vector_store()

    results = vector_store.similarity_search(state["user_message"], k=NUM_RESULTS_TO_RETRIEVE)
    context_text = "\n\n---\n\n".join(doc.page_content for doc in results)

    return {"retrieved_context": context_text}
