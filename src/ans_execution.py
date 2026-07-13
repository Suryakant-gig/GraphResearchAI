from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)

with driver.session() as session:
    result = session.run(cypher_query)

    data = []

    for record in result:
        data.append(record["m.name"])

print(data)

context = "\n".join(
    record["m.name"]
    for record in data
)

print(context)
answer_prompt = f"""
Question:
Which models use self attention?

Database Results:
{context}

Generate a concise answer.
"""

answer = llm.invoke(answer_prompt)

print(answer.content)