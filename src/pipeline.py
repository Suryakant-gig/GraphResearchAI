"""
Orchestrates the full PDF -> knowledge graph ingestion pipeline.
This connects the pieces that, in the original repo, existed only as
disconnected scripts with no entry point tying them together.
"""
from __future__ import annotations

import logging

from tqdm import tqdm

from chunker import chunk_text
from config import load_settings
from entity_extraction import extract_entities
from graph_writer import GraphWriter
from llm import get_llm
from pdf_loader import load_pdf_text
from relationship_extraction import extract_relationships

logger = logging.getLogger(__name__)


def ingest_pdf(path: str) -> dict[str, int]:
    """Ingest a single PDF into the Neo4j knowledge graph.

    Returns a small summary dict: {"chunks": N, "entities": N, "relationships": N}.
    """
    settings = load_settings()
    llm = get_llm()

    text = load_pdf_text(path)
    chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
    logger.info("Split %s into %d chunks", path, len(chunks))

    total_entities = 0
    total_relationships = 0

    with GraphWriter(settings) as writer:
        for chunk in tqdm(chunks, desc=f"Ingesting {path}"):
            entities = extract_entities(chunk, llm)
            if not entities:
                continue

            relationships = extract_relationships(chunk, entities, llm)

            writer.write_entities(entities)
            if relationships:
                writer.write_relationships(relationships)

            total_entities += len(entities)
            total_relationships += len(relationships)

    return {
        "chunks": len(chunks),
        "entities": total_entities,
        "relationships": total_relationships,
    }
