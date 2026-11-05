"""Runbook Retriever Agent — RAG over PDF runbooks and SOPs."""
from __future__ import annotations

from typing import Any, Dict, Optional

from .base import BaseAgent

try:
    import chromadb
    from chromadb.utils import embedding_functions
except Exception:  # pragma: no cover - chromadb optional at import time
    chromadb = None


class RunbookRetrieverAgent(BaseAgent):
    name = "runbook_retriever"

    def __init__(self):
        super().__init__()
        self.client = None
        self.collection = None
        if chromadb:
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection("runbooks")

    async def run(
        self,
        description: str,
        artifacts: Dict[str, Any],
        traces: Optional[list] = None,
        retriever: Optional[Any] = None,
    ) -> Dict[str, Any]:
        pdf_text = artifacts.get("pdf", "")
        prompt = f"""
You are the Runbook Retriever Agent for Nexus.

Incident: {description}

Available runbook content (from PDFs):
{pdf_text[:4000]}

Retrieve and summarize:
1. Relevant SOPs for this incident type
2. Recommended first-response actions
3. Escalation contacts / runbook owners
4. Past similar incidents and resolutions

Respond ONLY in JSON:
{{
  "applicable_sops": ["..."],
  "first_response_actions": ["..."],
  "escalation_contacts": ["..."],
  "past_incidents": ["..."],
  "confidence": 0.0-1.0
}}
"""
        raw = self._llm(prompt)
        return self._parse_json(raw, {
            "applicable_sops": [],
            "first_response_actions": [],
            "escalation_contacts": [],
            "past_incidents": [],
            "confidence": 0.5,
        })

    @staticmethod
    def _parse_json(raw: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        import json
        import re

        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        return fallback
