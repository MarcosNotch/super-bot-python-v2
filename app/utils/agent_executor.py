"""AgentExecutor: clase para ejecutar prompts con LLM y structured output.

Centraliza la lógica de:
- Invocación del LLM
- Validación de respuestas con Pydantic
- Manejo de errores y retries
- Parsing defensivo de JSON
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, ValidationError

from app.utils.openai_client import get_llm

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class AgentExecutorError(Exception):
    """Error al ejecutar el agente LLM."""

    pass

class AgentExecutor:
    """Service for executing LLM requests with structured outputs."""

    @staticmethod
    async def execute(system_prompt: str, user_prompt: str,  response_model: Type[T],  context: Optional[Dict[str, Any]] = None,) -> T:
        """Execute an LLM request with structured output."""
        context_str = f" [{context}]" if context else ""
        logger.debug(f"Ejecutando LLM{context_str}")
        llm = get_llm()
        structured_llm = llm.with_structured_output(response_model)

        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

        return await structured_llm.ainvoke(messages)


# Singleton instance
agent_executor = AgentExecutor()

