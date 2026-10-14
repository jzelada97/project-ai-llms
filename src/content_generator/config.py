"""Configuración de la app: lee variables de entorno (.env) o st.secrets.

Nada de claves en el código: la API key solo vive en `.env` (local) o en los
Secrets de Streamlit Cloud (demo pública).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_MODELS = {
    "groq": "openai/gpt-oss-120b",
    "ollama": "llama3.2",
}
DEFAULT_TEMPERATURE = 0.7
DEFAULT_OLLAMA_URL = "http://localhost:11434"


class ConfigError(Exception):
    """Configuración inválida o incompleta (mensaje apto para mostrar al usuario)."""


@dataclass(frozen=True)
class Settings:
    provider: str
    model: str
    temperature: float
    groq_api_key: str | None
    ollama_base_url: str


def _read(name: str, default: str | None = None) -> str | None:
    """Busca `name` en el entorno y, si no está, en `st.secrets` (Streamlit Cloud)."""
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st

        return st.secrets.get(name, default)
    except Exception:  # sin streamlit o sin archivo de secrets: usamos el default
        return default


def load_settings() -> Settings:
    """Carga y valida la configuración. Lanza `ConfigError` con un mensaje claro."""
    load_dotenv()

    provider = (_read("LLM_PROVIDER", "groq") or "groq").strip().lower()
    if provider not in DEFAULT_MODELS:
        raise ConfigError(
            f"LLM_PROVIDER='{provider}' no es válido. Usa 'groq' u 'ollama'."
        )

    api_key = _read("GROQ_API_KEY")
    if provider == "groq" and not api_key:
        raise ConfigError(
            "Falta GROQ_API_KEY. Crea una clave gratuita en https://console.groq.com/keys "
            "y ponla en tu archivo .env (ver .env.example)."
        )

    return Settings(
        provider=provider,
        model=_read("MODEL_NAME") or DEFAULT_MODELS[provider],
        temperature=DEFAULT_TEMPERATURE,
        groq_api_key=api_key,
        ollama_base_url=_read("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL) or DEFAULT_OLLAMA_URL,
    )
