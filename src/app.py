"""
Streamlit front end. Streamlit was in requirements.txt but had no UI code
anywhere in the original repo -- this is the missing entry point.

Run with: streamlit run src/app.py
"""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import streamlit as st

from config import load_settings
from graph_writer import GraphWriter
from llm import get_llm
from pipeline import ingest_pdf
from qa_engine import answer_question

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="GraphResearchAI", page_icon="🕸️", layout="centered")
st.title("🕸️ GraphResearchAI")
st.caption("Turn research PDFs into a queryable Neo4j knowledge graph.")

tab_ingest, tab_ask = st.tabs(["📄 Ingest a paper", "❓ Ask a question"])

with tab_ingest:
    uploaded = st.file_uploader("Upload a research paper (PDF)", type="pdf")
    if uploaded and st.button("Ingest into graph"):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(uploaded.read())
            tmp_path = Path(tmp.name)

        with st.spinner("Extracting entities and relationships..."):
            try:
                summary = ingest_pdf(str(tmp_path))
                st.success(
                    f"Done: {summary['chunks']} chunks, "
                    f"{summary['entities']} entities, "
                    f"{summary['relationships']} relationships written."
                )
            except Exception as exc:  # surfaced to the user, not just the logs
                st.error(f"Ingestion failed: {exc}")
            finally:
                tmp_path.unlink(missing_ok=True)

with tab_ask:
    question = st.text_input("Ask a question about the ingested papers")
    if question and st.button("Ask"):
        with st.spinner("Querying the graph..."):
            try:
                settings = load_settings()
                llm = get_llm()
                with GraphWriter(settings) as writer:
                    answer = answer_question(question, writer.driver, llm)
                st.markdown(f"**Answer:** {answer}")
            except Exception as exc:
                st.error(f"Query failed: {exc}")
