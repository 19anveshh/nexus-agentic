"""Triage Agent — classifies incident severity and decomposes the investigation."""
from __future__ import annotations

from typing import Any, Dict, Optional

from .base import BaseAgent


class TriageAgent(BaseAgent):
    name = "triage"

    async def run(
        self,
        description: str,
        artifacts: Dict[str, Any],
        traces: Optional[list] = None,
        retriever: Optional[Any] = None,
    ) -> Dict[str, Any]:
        prompt = f"""
You are the Triage Agent for Nexus, an autonomous incident-response system.

Incident description: {description}
Available evidence modalities: {list(artifacts.keys())}

Your job:
1. Classify severity (P1-P4).
2. Identify likely affected systems.
3. Decompose the investigation into 3-5 concrete agent tasks.
4. Decide which agents should run in parallel vs. sequentially.

Respond ONLY in JSON:
{{
  "severity": "P1|P2|P3|P4",
  "affected_systems": ["..."],
  "hypothesis": "short initial hypothesis",
  "plan": [
    {{"agent": "log_analyst", "task": "..."}},
    {{"agent": "visual_parser", "task": "..."}},
    {{"agent": "runbook_retriever", "task": "..."}}
  ],
  "parallel": ["log_analyst", "visual_parser", "runbook_retriever"]
}}
"""
        raw = self._llm(prompt)
        return self._parse_json(raw, {
            "severity": "P2",
            "affected_systems": ["unknown"],
            "hypothesis": "pending analysis",
            "plan": [],
            "parallel": [],
        })

    @staticmethod
    def _parse_json(raw: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        import json
        import re

        try:
            # Extract JSON block if wrapped in markdown
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        return fallback
