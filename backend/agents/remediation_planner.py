"""Remediation Planner Agent — drafts fix plan and ticket content."""
from __future__ import annotations

from typing import Any, Dict, Optional

from .base import BaseAgent


class RemediationPlannerAgent(BaseAgent):
    name = "remediation_planner"

    async def run(
        self,
        rca: Dict[str, Any],
        traces: Optional[list] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        prompt = f"""
You are the Remediation Planner Agent for Nexus.

Root Cause Analysis:
{rca}

Draft a remediation plan:
1. Immediate containment actions
2. Long-term fix
3. Prevention / monitoring recommendations
4. Rollback plan
5. Estimated effort

Respond ONLY in JSON:
{{
  "containment": ["..."],
  "action_plan": "...",
  "prevention": ["..."],
  "rollback": "...",
  "estimated_effort": "...",
  "ticket_description": "..."
}}
"""
        raw = self._llm(prompt)
        return self._parse_json(raw, {
            "containment": [],
            "action_plan": "pending",
            "prevention": [],
            "rollback": "pending",
            "estimated_effort": "unknown",
            "ticket_description": "pending",
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
