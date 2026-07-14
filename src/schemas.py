"""
Pydantic models describing the knowledge graph schema.

Every piece of data extracted by the LLM is validated against these models
before it is allowed anywhere near Neo4j. This is the piece the original
scripts were missing entirely (pydantic was in requirements.txt but unused).
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class EntityType(str, Enum):
    MODEL = "Model"
    DATASET = "Dataset"
    METHOD = "Method"
    METRIC = "Metric"
    TASK = "Task"


class RelationType(str, Enum):
    USES = "USES"
    BASED_ON = "BASED_ON"
    EVALUATED_ON = "EVALUATED_ON"
    OUTPERFORMS = "OUTPERFORMS"


class Entity(BaseModel):
    id: str = Field(..., min_length=1, description="Stable unique key, e.g. slugified name")
    name: str = Field(..., min_length=1)
    type: EntityType
    properties: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "id")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v


class Relationship(BaseModel):
    source_id: str = Field(..., min_length=1)
    target_id: str = Field(..., min_length=1)
    type: RelationType
    properties: dict[str, Any] = Field(default_factory=dict)


class ExtractionResult(BaseModel):
    """What we expect back from the entity/relationship extraction LLM calls."""
    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
