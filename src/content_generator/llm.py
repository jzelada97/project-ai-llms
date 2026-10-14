"""Fábrica de modelos de chat.

LangChain da a todos los proveedores la misma interfaz (`BaseChatModel`), así que
el resto del código no sabe si habla con Groq o con Ollama: solo hace `.invoke()`.
Cambiar de proveedor es cambiar `LLM_PROVIDER` en el `.env`.
"""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel

from .config import Settings


def get_llm(settings: Settings, max_tokens: int) -> BaseChatModel:
    """Devuelve el modelo de chat configurado, limitando los tokens de salida."""
    if settings.provider == "groq":
        from langchain_groq import ChatGroq

        extra = {}
        if "gpt-oss" in settings.model:
            # Modelos de razonamiento: sin esto el "pensamiento" consume el tope de tokens
            extra["reasoning_effort"] = "low"
        return ChatGroq(
            model=settings.model,
            temperature=settings.temperature,
            max_tokens=max_tokens,
            api_key=settings.groq_api_key,
            **extra,
        )

    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=settings.model,
        temperature=settings.temperature,
        num_predict=max_tokens,  # en Ollama el límite de salida se llama num_predict
        base_url=settings.ollama_base_url,
    )
