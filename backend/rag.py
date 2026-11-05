"""Runbook RAG stub — ChromaDB-backed retrieval for SOPs."""
from __future__ import annotations

from typing import Any, List, Optional


class RunbookRetriever:
    """Lightweight retrieval over ingested runbook text.

    In production: chunk PDFs, embed with sentence-transformers, store in ChromaDB,
    and run semantic search. For the demo, keyword matching over ingested PDF text
    is sufficient and runs with zero extra dependencies.
    """

    def __init__(self):
        self.documents: List[str] = []

    def add(self, text: str) -> None:
        self.documents.append(text)

    def search(self, query: str, top_k: int = 3) -> List[str]:
        if not self.documents:
            return []
        query_terms = set(query.lower().split())
        scored = []
        for doc in self.documents:
            doc_lower = doc.lower()
            score = sum(1 for t in query_terms if t in doc_lower)
            if score > 0:
                scored.append((score, doc[:500]))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [doc for _, doc in scored[:top_k]]
