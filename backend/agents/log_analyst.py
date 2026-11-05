"""Log Analyst Agent — parses text logs and error streams."""
from __future__ import annotations

from typing import Any, Dict, Optional

from .base import BaseAgent


class LogAnalystAgent(BaseAgent):
    name = "log_analyst"

    async def run(
        self,
        description: str,
        artifacts: Dict[str, Any],
        traces: Optional[list] = None,
        retriever: Optional[Any] = None,
    ) -> Dict[str, Any]:
        logs = artifacts.get("text", "") or artifacts.get("logs", "")
        prompt = f"""
You are the Log Analyst Agent for Nexus.

Incident: {description}

Log evidence:
{logs[:6000]}

Analyze the logs and return:
1. Error patterns / stack traces found
2. Timestamps of anomalies
3. Likely failing components
4. Correlation candidates with other modalities

Respond ONLY in JSON:
{{
  "errors_found": ["..."],
  "anomaly_timestamps": ["..."],
  "failing_components": ["..."],
  "correlation_hints": ["..."],
  "confidence": 0.0-1.0
}}
"""
        raw = self._llm(prompt)
        return self._parse_json(raw, {
            "errors_found": [],
            "anomaly_timestamps": [],
            "failing_components": [],
            "correlation_hints": [],
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
