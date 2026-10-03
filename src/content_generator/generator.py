"""Lógica de generación: valida la petición y ejecuta la cadena LangChain (LCEL).

La cadena es `PROMPT | llm | StrOutputParser()`:
  1. PROMPT rellena la plantilla con las variables  -> mensajes
  2. llm genera la respuesta                         -> AIMessage
  3. StrOutputParser extrae el texto del mensaje     -> str
El operador `|` es LCEL: cada pieza es un "Runnable" y la salida de una es la
entrada de la siguiente.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser

from .config import Settings, load_settings
from .llm import get_llm
from .prompts import (
    AUDIENCE_RULES,
    LENGTHS,
    PLATFORM_RULES,
    PROMPT,
    TONE_RULES,
    prompt_variables,
)

logger = logging.getLogger(__name__)

TOPIC_MAX_CHARS = 200
EXTRA_MAX_CHARS = 300


class GenerationError(Exception):
    """Error al generar (mensaje legible para el usuario, sin trazas)."""


@dataclass(frozen=True)
class ContentRequest:
    """Lo que el usuario pide generar."""

    topic: str
    platform: str
    audience: str
    tone: str = "Cercano"
    length: str = "Media"
    extra: str = ""

    def validate(self) -> None:
        """Comprueba longitudes y que las opciones estén en las listas permitidas."""
        topic = self.topic.strip()
        if not topic:
            raise GenerationError("Escribe un tema para generar contenido.")
        if len(topic) > TOPIC_MAX_CHARS:
            raise GenerationError(f"El tema no puede superar {TOPIC_MAX_CHARS} caracteres.")
        if len(self.extra) > EXTRA_MAX_CHARS:
            raise GenerationError(
                f"Las instrucciones extra no pueden superar {EXTRA_MAX_CHARS} caracteres."
            )
        for value, allowed, label in (
            (self.platform, PLATFORM_RULES, "plataforma"),
            (self.audience, AUDIENCE_RULES, "audiencia"),
            (self.tone, TONE_RULES, "tono"),
            (self.length, LENGTHS, "longitud"),
        ):
            if value not in allowed:
                raise GenerationError(f"Valor no permitido para {label}: {value!r}.")


def build_chain(llm: BaseChatModel):
    """Monta la cadena LCEL: prompt | modelo | parser de texto."""
    return PROMPT | llm | StrOutputParser()


def _friendly_error(exc: Exception) -> GenerationError:
    """Traduce errores del proveedor a mensajes comprensibles."""
    status = getattr(exc, "status_code", None)
    text = str(exc).lower()
    if status == 429 or "rate limit" in text:
        return GenerationError("Límite de peticiones alcanzado. Espera unos segundos y reintenta.")
    if status in (401, 403) or "api key" in text or "authentication" in text:
        return GenerationError("La API key no es válida. Revisa tu configuración (.env).")
    if status == 404 or "not found" in text or "decommissioned" in text:
        return GenerationError("El modelo configurado no está disponible. Revisa MODEL_NAME.")
    if "connect" in text or "connection" in text:
        return GenerationError(
            "No se pudo conectar con el proveedor del modelo "
            "(¿está Ollama en marcha o hay conexión a internet?)."
        )
    return GenerationError("No se pudo generar el contenido. Inténtalo de nuevo en unos segundos.")


def generate_content(
    request: ContentRequest,
    settings: Settings | None = None,
    llm: BaseChatModel | None = None,
) -> str:
    """Genera el contenido para `request`.

    `llm` permite inyectar un modelo (útil en tests con un modelo falso); si no se
    pasa, se crea el configurado en el `.env`. Puede lanzar `ConfigError` o
    `GenerationError`.
    """
    request.validate()
    if llm is None:
        settings = settings or load_settings()
        llm = get_llm(settings, max_tokens=LENGTHS[request.length][1])

    variables = prompt_variables(
        topic=request.topic.strip(),
        platform=request.platform,
        audience=request.audience,
        tone=request.tone,
        length=request.length,
        extra=request.extra.strip(),
    )
    try:
        return build_chain(llm).invoke(variables).strip()
    except Exception as exc:  # los proveedores lanzan tipos de error muy distintos
        logger.warning("Fallo del proveedor (%s): %s", type(exc).__name__, exc)
        raise _friendly_error(exc) from exc
