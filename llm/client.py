"""
llm/client.py
-------------
Cliente único para el LLM del sistema.
El resto del proyecto NUNCA importa Ollama o Gemini directamente —
solo llama a get_llm() y recibe un modelo listo para usar.

Por qué esto importa:
    Cambiar de proveedor = cambiar UNA variable de entorno.
    Ningún otro módulo necesita saber que algo cambió.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """
    Retorna el LLM configurado según LLM_PROVIDER en .env
    
    Returns:
        BaseChatModel: instancia lista para usar en LangGraph o LangChain
        
    Raises:
        ValueError: si LLM_PROVIDER no es 'ollama' ni 'gemini'
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:14b"),
            temperature=0.1,  # Bajo: queremos respuestas consistentes, no creativas
        )

    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1,
        )

    else:
        raise ValueError(
            f"LLM_PROVIDER='{provider}' no válido. "
            "Usa 'ollama' o 'gemini' en tu archivo .env"
        )


def get_provider_name() -> str:
    """Retorna el nombre del proveedor activo — útil para logs y métricas."""
    return os.getenv("LLM_PROVIDER", "ollama").lower()