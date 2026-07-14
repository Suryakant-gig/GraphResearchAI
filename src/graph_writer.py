"""
Writes validated Entity/Relationship objects into Neo4j.

Replaces ans_execution.py's inline, hardcoded-credential driver instance
with a reusable class using parameterized Cypher (never string-interpolate
untrusted values into a query -- only the fixed enum label/type names are
interpolated, values always go through query parameters).
"""
from __future__ import annotations

import logging

from neo4j import Driver, GraphDatabase

from .config import Settings, load_settings
from .schemas import Entity, Relationship

logger = logging.getLogger(__name__)


class GraphWriter:
    def __init__(self, settings: Settings | None = None):
        self._settings = settings or load_settings()
        self._driver: Driver = GraphDatabase.driver(
            self._settings.neo4j_uri,
            auth=(self._settings.neo4j_user, self._settings.neo4j_password),
        )

    @property
    def driver(self) -> Driver:
        return self._driver

    def close(self) -> None:
        self._driver.close()

    def __enter__(self) -> "GraphWriter":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()

    def write_entities(self, entities: list[Entity]) -> None:
        with self._driver.session() as session:
            for entity in entities:
                # entity.type.value is a validated Enum member, safe to interpolate
                # as a label; id/name/properties always go through parameters.
                session.run(
                    f"""
                    MERGE (n:{entity.type.value} {{id: $id}})
                    SET n.name = $name, n += $props
                    """,
                    id=entity.id,
                    name=entity.name,
                    props=entity.properties,
                )
        logger.info("Wrote %d entities", len(entities))

    def write_relationships(self, relationships: list[Relationship]) -> None:
        with self._driver.session() as session:
            for rel in relationships:
                session.run(
                    f"""
                    MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
                    MERGE (a)-[r:{rel.type.value}]->(b)
                    SET r += $props
                    """,
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    props=rel.properties,
                )
        logger.info("Wrote %d relationships", len(relationships))
