"""
PDF ingestion. Replaces the original loader.py, which referenced
PyPDFLoader without importing it and had no function boundary at all.
"""
from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


def load_pdf_text(path: str | Path) -> str:
    """Load a PDF and return its full text content as a single string."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    loader = PyPDFLoader(str(path))
    docs = loader.load()

    if not docs:
        raise ValueError(f"No extractable text found in {path}")

    return "\n".join(doc.page_content for doc in docs)
