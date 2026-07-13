schema = """
Nodes:
- Model
- Dataset
- Method
- Metric

Relationships:
- USES
- BASED_ON
- EVALUATED_ON
- OUTPERFORMS
"""
prompt = f"""
You are a Cypher query generator.

Database schema:

{schema}

Convert the user question into a Cypher query.

Question:
Which models use self attention?

Return ONLY the Cypher query.
"""

response = llm.invoke(prompt)

cypher_query = response.content.strip()

print(cypher_query)