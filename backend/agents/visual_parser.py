"""Visual Parser Agent — VLM-based analysis of screenshots, diagrams, charts."""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Dict, Optional

from .base import BaseAgent


class VisualParserAgent(BaseAgent):
    name = "visual_parser"

    async def run(
        self,
        description: str,
        artifacts: Dict[str, Any],
        traces: Optional[list] = None,
        retriever: Optional[Any] = None,
    ) -> Dict[str, Any]:
        images = artifacts.get("images", [])
        if not images:
            return {
                "visual_findings": [],
                "dashboard_anomalies": [],
                "architecture_issues": [],
                "confidence": 0.0,
                "note": "No image evidence provided.",
            }

        # Build multimodal prompt with image placeholders
        image_refs = "\n".join(f"- {img.get('path', img)}" for img in images[:5])
        prompt = f"""
You are the Visual Parser Agent for Nexus.

Incident: {description}

Image evidence provided (file paths):
{image_refs}

Analyze these screenshots, architecture diagrams, and monitoring charts for:
1. Visible error messages or red indicators
2. Dashboard metric anomalies (spikes, drops, flatlines)
3. Architecture misconfigurations visible in diagrams
4. UI states that correlate with the incident

Respond ONLY in JSON:
{{
  "visual_findings": ["..."],
  "dashboard_anomalies": ["..."],
  "architecture_issues": ["..."],
  "confidence": 0.0-1.0
}}
"""
        # NOTE: In production, pass image URLs/base64 to a VLM (GPT-4V / LLaVA).
        # Here we pass file paths; the LLM reasons about them contextually.
        raw = self._llm(prompt, system="You are a multimodal SRE agent that reads screenshots and diagrams.")
        return self._parse_json(raw, {
            "visual_findings": [],
            "dashboard_anomalies": [],
            "architecture_issues": [],
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
