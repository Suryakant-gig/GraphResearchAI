"""
Single place that constructs the LLM client, so every module shares one
configured instance instead of each script assuming a global `llm` exists.
"""
from __future__ import annotations

from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from .config import load_settings


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    settings = load_settings()
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.google_api_key,
        temperature=temperature,
    )
