"""RCA Synthesizer Agent — correlates all agent outputs into a root cause."""
from __future__ import annotations

from typing import Any, Dict, Optional

from .base import BaseAgent


class RCASynthesizerAgent(BaseAgent):
    name = "rca_synthesizer"

    async def run(
        self,
        description: str,
        artifacts: Dict[str, Any],
        traces: Optional[list] = None,
        retriever: Optional[Any] = None,
    ) -> Dict[str, Any]:
        trace_summary = "\n".join(
            f"[{t['agent']}] {t['output']}" for t in (traces or [])
        )
        prompt = f"""
You are the RCA Synthesizer Agent for Nexus.

Incident: {description}

Agent traces:
{trace_summary[:8000]}

Synthesize a single coherent root cause analysis:
1. Primary root cause
2. Contributing factors
3. Timeline of failure
4. Evidence chain (which agent found what)
5. Confidence score

Respond ONLY in JSON:
{{
  "root_cause": "...",
  "contributing_factors": ["..."],
  "timeline": ["..."],
  "evidence_chain": ["..."],
  "summary": "...",
  "confidence": 0.0-1.0
}}
"""
        raw = self._llm(prompt)
        return self._parse_json(raw, {
            "root_cause": "under investigation",
            "contributing_factors": [],
            "timeline": [],
            "evidence_chain": [],
            "summary": "synthesis pending",
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
