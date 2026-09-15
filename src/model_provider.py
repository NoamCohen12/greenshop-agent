"""
בוחר את מודל השפה שישמש את הסוכן, לפי משתנה הסביבה MODEL_PROVIDER.
מאפשר החלפה בין Ollama (מקומי, כמו בקורס) לבין OpenAI, בלי לשנות קוד בשאר הפרויקט.
"""

import os


def get_chat_model():
    provider = os.environ.get("MODEL_PROVIDER", "ollama").lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        model_name = os.environ.get("OLLAMA_MODEL", "llama3.2")
        return ChatOllama(model=model_name, temperature=0)

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY חסר ב-.env כאשר MODEL_PROVIDER=openai")

        model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(model=model_name, api_key=api_key, temperature=0)

    raise ValueError(f"MODEL_PROVIDER לא מוכר: '{provider}'. יש להשתמש ב-'ollama' או 'openai'")
