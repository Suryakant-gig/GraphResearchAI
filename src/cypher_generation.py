"""
Natural-language -> Cypher generation.

The original cypher_generation.py hardcoded the question
("Which models use self attention?") directly into the prompt, so it could
never answer anything else. This version takes the question as an argument.
"""
from __future__ import annotations

import re

from langchain_google_genai import ChatGoogleGenerativeAI

GRAPH_SCHEMA = """
Nodes:
- Model
- Dataset
- Method
- Metric
- Task

Relationships:
- USES
- BASED_ON
- EVALUATED_ON
- OUTPERFORMS
"""

CYPHER_PROMPT = """You are a Cypher query generator for a Neo4j research knowledge graph.

Database schema:
{schema}

Convert the user's question into a single read-only Cypher query.
Only use MATCH / WHERE / RETURN / OPTIONAL MATCH clauses.
Never use CREATE, MERGE, DELETE, SET, or REMOVE.
Return ONLY the Cypher query -- no markdown fences, no explanation.

Question:
{question}
"""

# Guardrail: reject anything that looks like a write query, even if the
# LLM ignores the prompt instructions.
_WRITE_KEYWORDS = re.compile(r"\b(CREATE|MERGE|DELETE|SET|REMOVE|DROP)\b", re.IGNORECASE)


def generate_cypher(question: str, llm: ChatGoogleGenerativeAI) -> str:
    """Generate a read-only Cypher query for the given natural-language question."""
    response = llm.invoke(CYPHER_PROMPT.format(schema=GRAPH_SCHEMA, question=question))
    query = response.content.strip().strip("`").strip()

    if query.lower().startswith("cypher"):
        query = query[len("cypher"):].strip()

    if _WRITE_KEYWORDS.search(query):
        raise ValueError(
            f"Generated query contains a write operation, refusing to run it:\n{query}"
        )

    return query
