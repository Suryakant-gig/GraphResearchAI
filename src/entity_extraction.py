"""
Entity extraction. The original Entity_Extraction.py was a bare prompt
string with a stray, syntactically-invalid `Text:\n{chunk}` line after it
and no function, no LLM call, and no parsing.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError

from .schemas import Entity

logger = logging.getLogger(__name__)

ENTITY_PROMPT = """Extract entities from the research text below.

Categories:
- Model
- Dataset
- Method
- Metric
- Task

Return ONLY valid JSON, in this exact shape, with no markdown fences and no commentary:
{{
  "entities": [
    {{"id": "<slug>", "name": "<display name>", "type": "<one of the categories above>"}}
  ]
}}

Text:
{chunk}
"""


def _extract_json(raw: str) -> dict[str, Any]:
    """LLMs frequently wrap JSON in ```json fences despite instructions; strip them."""
    cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def extract_entities(chunk: str, llm: ChatGoogleGenerativeAI) -> list[Entity]:
    """Extract entities from a single text chunk, returning only validated results."""
    response = llm.invoke(ENTITY_PROMPT.format(chunk=chunk))

    try:
        payload = _extract_json(response.content)
    except json.JSONDecodeError as err:
        logger.warning("Could not parse entity extraction JSON: %s", err)
        return []

    entities: list[Entity] = []
    for raw_entity in payload.get("entities", []):
        try:
            entities.append(Entity(**raw_entity))
        except ValidationError as err:
            logger.warning("Skipping invalid entity %r: %s", raw_entity, err)

    return entities
