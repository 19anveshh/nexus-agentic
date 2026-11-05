"""Base agent class for the Nexus multi-agent system."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

try:
    from chromadb import Client as ChromaClient
except Exception:  # chromadb optional for demo
    ChromaClient = None


class BaseAgent:
    name: str = "base"

    async def run(
        self,
        description: str,
        artifacts: Dict[str, Any],
        traces: Optional[list] = None,
        retriever: Optional[ChromaClient] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def _llm(self, prompt: str, system: str = "You are a senior site reliability engineer.") -> str:
        """
        Thin wrapper around an LLM call.
        Provider chosen by LLM_PROVIDER env var: 'groq' (default) or 'openai'.
        Falls back to demo mode if no API key is configured.
        """
        provider = os.getenv("LLM_PROVIDER", "groq")

        if provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return self._demo_response(prompt)
            try:
                from groq import Groq

                client = Groq(api_key=api_key)
                resp = client.chat.completions.create(
                    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                return resp.choices[0].message.content or ""
            except Exception as e:
                return f"[GROQ ERROR] {e}"

        # openai provider
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._demo_response(prompt)
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            return resp.choices[0].message.content or ""
        except Exception:
            return self._demo_response(prompt)

    def _demo_response(self, prompt: str) -> str:
        """Return a realistic structured response per agent, keyed off self.name."""
        desc_match = None
        for key in ("Incident:", "incident:", "description:"):
            if key in prompt:
                desc_match = prompt.split(key, 1)[1].strip()[:200]
                break
        description = desc_match or "unspecified incident"

        templates = {
            "triage": {
                "severity": "P2",
                "affected_systems": ["payment-gateway", "checkout-service"],
                "hypothesis": "Upstream payment provider returning elevated 5xx errors since 14:30 UTC.",
                "plan": [
                    {"agent": "log_analyst", "task": "Scan payment-gateway logs for 502/504 spikes and correlate timestamps"},
                    {"agent": "visual_parser", "task": "Inspect CloudWatch dashboard screenshots for latency spikes"},
                    {"agent": "runbook_retriever", "task": "Retrieve payment-outage runbook and escalation contacts"},
                ],
                "parallel": ["log_analyst", "visual_parser", "runbook_retriever"],
            },
            "log_analyst": {
                "errors_found": [
                    "502 Bad Gateway from payment-gateway at 14:32-14:45 UTC",
                    "Upstream timeout connecting to stripe-prod.api (30s)",
                    "Connection pool exhausted on checkout-service (98% utilization)",
                ],
                "anomaly_timestamps": ["2026-11-05T14:32:00Z", "2026-11-05T14:35:00Z", "2026-11-05T14:40:00Z"],
                "failing_components": ["payment-gateway", "checkout-service", "stripe-prod.api"],
                "correlation_hints": [
                    "Error spike coincides with dashboard latency jump shown in visual evidence",
                    "Runbook lists stripe-prod.api as a known single point of failure",
                ],
                "confidence": 0.92,
            },
            "visual_parser": {
                "visual_findings": [
                    "CloudWatch dashboard shows 300% spike in 5xx errors at 14:30 UTC",
                    "Latency graph: p99 jumped from 200ms to 4.2s during incident window",
                    "Architecture diagram: checkout-service → payment-gateway → stripe-prod.api (no circuit breaker)",
                ],
                "dashboard_anomalies": [
                    "Error rate flatlined at ~12% of traffic from 14:30-14:45 UTC",
                    "CPU on payment-gateway nodes at 85%+, no autoscaling trigger fired",
                ],
                "architecture_issues": [
                    "Missing circuit breaker between payment-gateway and stripe-prod.api",
                    "No retry with exponential backoff configured on checkout path",
                ],
                "confidence": 0.88,
            },
            "runbook_retriever": {
                "applicable_sops": [
                    "PAY-001: Payment Gateway Outage — Immediate Response",
                    "PAY-003: Stripe API Degradation — Fallback to Alternate Processor",
                ],
                "first_response_actions": [
                    "Fail over to alternate payment processor (adyen-fallback)",
                    "Enable circuit breaker on stripe-prod.api calls",
                    "Page on-call payments engineer",
                ],
                "escalation_contacts": ["payments-oncall@company.com", "+1-555-0100"],
                "past_incidents": [
                    "INC-2026-1012: Similar stripe 5xx spike on Oct 12, resolved by failover",
                ],
                "confidence": 0.85,
            },
            "rca_synthesizer": {
                "root_cause": "Stripe production API returning intermittent 502 errors, compounded by missing circuit breaker on payment-gateway causing cascading failures in checkout-service.",
                "contributing_factors": [
                    "No circuit breaker between payment-gateway and stripe-prod.api",
                    "Autoscaling policy did not trigger on elevated CPU (85%+)",
                    "Checkout service lacks fallback payment processor",
                ],
                "timeline": [
                    "14:30 UTC — Stripe 5xx errors begin",
                    "14:32 UTC — payment-gateway 502 spike detected",
                    "14:35 UTC — checkout-service CPU hits 85%, latency rises",
                    "14:40 UTC — 12% of checkout traffic failing",
                ],
                "evidence_chain": [
                    "log_analyst: 502 errors and upstream timeout in payment-gateway logs",
                    "visual_parser: dashboard latency spike + missing circuit breaker in diagram",
                    "runbook_retriever: PAY-001/PAY-003 SOPs confirm stripe-prod.api as SPOF",
                ],
                "summary": "Cascading payment failure caused by unmitigated Stripe API degradation without circuit breaker protection.",
                "confidence": 0.9,
            },
            "remediation_planner": {
                "containment": [
                    "Enable circuit breaker on stripe-prod.api calls immediately",
                    "Route checkout traffic to adyen-fallback processor",
                    "Scale up payment-gateway instances to handle backlog",
                ],
                "action_plan": "Deploy circuit breaker configuration to payment-gateway, enable adyen-fallback in checkout-service, and monitor error rate for 30 minutes before declaring resolution.",
                "prevention": [
                    "Add circuit breaker with exponential backoff to all external payment calls",
                    "Configure autoscaling on CPU > 70% and error rate > 5%",
                    "Add synthetic checkout probes alerting on > 1% failure rate",
                ],
                "rollback": "Revert circuit breaker config and disable adyen-fallback if new processor introduces errors.",
                "estimated_effort": "2-4 hours",
                "ticket_description": "P2 Payment outage — Stripe 5xx causing 12% checkout failures. RCA: missing circuit breaker. Fix: enable circuit breaker + adyen fallback.",
            },
        }

        return json.dumps(templates.get(self.name, {"note": "demo mode — no agent response available"}), indent=2)
