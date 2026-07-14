"""
Relationship extraction. The original Relationship_Extraction.py wasn't
even valid Python (a docstring-less top-level "Extract relationships." line
outside any string, followed by an f-string-style {chunk} placeholder
outside any function).
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError

from schemas import Entity, Relationship

logger = logging.getLogger(__name__)

RELATIONSHIP_PROMPT = """Extract relationships between the entities below, based on the text.

Known entities (use these exact ids as source_id / target_id):
{entity_list}

Allowed relationship types:
- USES
- BASED_ON
- EVALUATED_ON
- OUTPERFORMS

Return ONLY valid JSON, in this exact shape, with no markdown fences and no commentary:
{{
  "relationships": [
    {{"source_id": "<id>", "target_id": "<id>", "type": "<one of the types above>"}}
  ]
}}

Text:
{chunk}
"""


def _extract_json(raw: str) -> dict[str, Any]:
    cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def extract_relationships(
    chunk: str,
    entities: list[Entity],
    llm: ChatGoogleGenerativeAI,
) -> list[Relationship]:
    """Extract relationships, dropping any that reference an unknown entity id."""
    if not entities:
        return []

    entity_list = "\n".join(f"- {e.id} ({e.type.value}): {e.name}" for e in entities)
    response = llm.invoke(RELATIONSHIP_PROMPT.format(entity_list=entity_list, chunk=chunk))

    try:
        payload = _extract_json(response.content)
    except json.JSONDecodeError as err:
        logger.warning("Could not parse relationship extraction JSON: %s", err)
        return []

    valid_ids = {e.id for e in entities}
    relationships: list[Relationship] = []

    for raw_rel in payload.get("relationships", []):
        try:
            rel = Relationship(**raw_rel)
        except ValidationError as err:
            logger.warning("Skipping invalid relationship %r: %s", raw_rel, err)
            continue

        if rel.source_id not in valid_ids or rel.target_id not in valid_ids:
            logger.warning(
                "Skipping relationship with unknown entity id(s): %s -> %s",
                rel.source_id, rel.target_id,
            )
            continue

        relationships.append(rel)

    return relationships
