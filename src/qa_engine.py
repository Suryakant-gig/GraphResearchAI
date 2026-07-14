"""
Question answering pipeline: question -> Cypher -> Neo4j -> synthesized answer.

Replaces ans_execution.py, which referenced an undefined `cypher_query`,
an undefined `llm`, hardcoded credentials, a hardcoded question string, and
assumed every result row had a literal "m.name" key.
"""
from __future__ import annotations

import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from neo4j import Driver

from cypher_generation import generate_cypher

logger = logging.getLogger(__name__)

ANSWER_PROMPT = """Question:
{question}

Database results:
{context}

Using only the database results above, generate a concise answer.
If the results are empty, say you couldn't find relevant information in the graph.
"""


def answer_question(question: str, driver: Driver, llm: ChatGoogleGenerativeAI) -> str:
    cypher_query = generate_cypher(question, llm)
    logger.info("Generated Cypher: %s", cypher_query)

    with driver.session() as session:
        result = session.run(cypher_query)
        # record.data() works regardless of what fields the generated query returns,
        # instead of assuming a fixed column name like "m.name".
        rows = [record.data() for record in result]

    context = "\n".join(str(row) for row in rows) if rows else "(no matching results)"

    response = llm.invoke(ANSWER_PROMPT.format(question=question, context=context))
    return response.content.strip()
