# GraphResearchAI

Turn research PDFs into a queryable Neo4j knowledge graph, using an LLM to
extract entities/relationships and to translate natural-language questions
into Cypher.

## What changed from the original repo

The original `src/` files were disconnected script fragments, not runnable
code: undefined variables (`llm`, `cypher_query`, `text`), hardcoded
credentials and questions, missing imports, and one file (`Relationship_Extraction.py`)
that wasn't valid Python at all. `pydantic`, `streamlit`, and `python-dotenv`
were listed in `requirements.txt` but never used anywhere.

This version is a real, importable package:

| File | Purpose |
|---|---|
| `config.py` | Loads credentials/settings from `.env` (`python-dotenv`) instead of hardcoding them |
| `schemas.py` | Pydantic models (`Entity`, `Relationship`) that validate every LLM output before it touches the database |
| `pdf_loader.py` | Loads a PDF into text |
| `chunker.py` | Splits text into overlapping chunks |
| `llm.py` | One shared, cached LLM client |
| `entity_extraction.py` | Extracts entities, parses/validates JSON, skips malformed items instead of crashing |
| `relationship_extraction.py` | Extracts relationships, cross-validates ids against known entities |
| `graph_writer.py` | Writes to Neo4j using parameterized Cypher |
| `cypher_generation.py` | Question -> Cypher, with a guardrail that rejects any generated write query |
| `qa_engine.py` | Runs the generated Cypher and synthesizes a final answer |
| `pipeline.py` | Orchestrates load -> chunk -> extract -> write for a whole PDF, with a `tqdm` progress bar |
| `app.py` | Streamlit UI: upload a PDF to ingest, ask questions against the graph |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in GOOGLE_API_KEY and NEO4J_PASSWORD
```

You need a running Neo4j instance (e.g. `docker run -p 7687:7687 -p 7474:7474 neo4j`)
and a Google AI Studio API key.

## Run

```bash
streamlit run src/app.py
```

Or use the pipeline directly:

```python
from src.pipeline import ingest_pdf
from src.qa_engine import answer_question
from src.graph_writer import GraphWriter
from src.llm import get_llm

ingest_pdf("paper.pdf")

with GraphWriter() as writer:
    print(answer_question("Which models use self attention?", writer.driver, get_llm()))
```

## Known limitations / next steps

- Entity/relationship extraction runs per-chunk with no cross-chunk entity
  resolution, so the same real-world entity mentioned in two chunks can be
  written as two separate nodes if the LLM picks a different `id` each time.
  Consider a name-normalization or embedding-based dedup pass.
- No retry/backoff around LLM calls; add one before running this against a
  large PDF batch.
- No automated tests yet — the modules are structured (pure functions taking
  an `llm`/`driver` argument) specifically so they can be unit-tested with
  mocks.
