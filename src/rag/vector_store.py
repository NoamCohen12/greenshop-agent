"""
בניית וטעינת מסד הנתונים הוקטורי (ChromaDB) עבור בסיס הידע של GreenShop
(מדיניות החזרות, מפרטי מוצרים וכו').
"""

import glob
import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "knowledge_base")
COLLECTION_NAME = "greenshop_knowledge"


def get_embedding_model():
    provider = os.environ.get("MODEL_PROVIDER", "ollama").lower()

    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings

        return OllamaEmbeddings(model=os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"))

    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(model=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))


def build_vector_store() -> Chroma:
    """
    קורא את כל המסמכים מ-data/knowledge_base, מפצל אותם לקטעים (chunks),
    ובונה מהם מסד נתונים וקטורי חדש (מריץ פעם אחת, כשמעדכנים את בסיס הידע).
    """
    documents = []
    for file_path in glob.glob(os.path.join(KNOWLEDGE_BASE_DIR, "*.txt")):
        with open(file_path, encoding="utf-8") as file:
            documents.append(
                Document(
                    page_content=file.read(),
                    metadata={"source": os.path.basename(file_path)},
                )
            )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=get_embedding_model(),
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    return vector_store


def load_vector_store() -> Chroma:
    """טוען מסד נתונים וקטורי קיים מהדיסק (משמש בזמן ריצה רגיל של הסוכן)."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=CHROMA_PERSIST_DIR,
    )


if __name__ == "__main__":
    print("בונה מסד נתונים וקטורי מתוך data/knowledge_base ...")
    build_vector_store()
    print(f"הושלם. נשמר ב-{CHROMA_PERSIST_DIR}")
