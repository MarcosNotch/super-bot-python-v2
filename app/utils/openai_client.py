"""Singleton para el cliente LLM (LangChain OpenAI).

Reglas:
- No crear instancias del LLM por request.
- Reutilizar el cliente cacheado.
- Configurar timeouts y retries explícitos.
"""

from __future__ import annotations

from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.config.settings import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """Devuelve un cliente de ChatOpenAI compartido.

    Returns:
        ChatOpenAI: Cliente configurado y cacheado.
    """

    # `langchain-openai` ha cambiado nombres de parámetros entre versiones.
    # `timeout` es el más común actualmente.
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        timeout=settings.llm_request_timeout,
        max_retries=settings.llm_max_retries,
    )
