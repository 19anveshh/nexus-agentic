"""Autonomous agent orchestrator with human-in-the-loop approval gates."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, List, Optional

from agents.registry import AGENT_REGISTRY, BaseAgent
from ingestion import parse_evidence
from rag import RunbookRetriever


@dataclass
class IncidentPacket:
    session_id: str
    description: str
    evidence_paths: List[str] = field(default_factory=list)
    parsed_artifacts: Dict[str, Any] = field(default_factory=dict)
    agent_traces: List[Dict[str, Any]] = field(default_factory=list)
    final_report: Optional[Dict[str, Any]] = None
    approval_status: str = "pending"  # pending | approved | rejected


class NexusOrchestrator:
    """
    Goal-driven autonomous loop:
    1. Ingest & parse multimodal evidence
    2. Plan investigation (decompose into agent tasks)
    3. Run agents in parallel where possible
    4. Synthesize root cause
    5. Draft remediation + ticket
    6. Wait for human approval
    """

    def __init__(self, session_id: str, description: str = ""):
        self.session_id = session_id
        self.packet = IncidentPacket(session_id=session_id, description=description)
        self.retriever = RunbookRetriever()
        self._agents: Dict[str, BaseAgent] = {
            name: cls() for name, cls in AGENT_REGISTRY.items()
        }

    async def run(self) -> AsyncIterator[Dict[str, Any]]:
        yield {"type": "status", "message": "Initializing Nexus investigation...", "agent": "system"}

        # --- Phase 1: Ingest ---
        yield {"type": "status", "message": "Parsing multimodal evidence...", "agent": "ingestion"}
        self.packet.parsed_artifacts = parse_evidence(self.packet.evidence_paths)
        yield {
            "type": "artifact",
            "agent": "ingestion",
            "data": {
                "files": len(self.packet.evidence_paths),
                "modalities": list(self.packet.parsed_artifacts.keys()),
                "preview": str(self.packet.parsed_artifacts)[:500],
            },
        }

        # --- Phase 2: Plan ---
        yield {"type": "status", "message": "Planning agent workflow...", "agent": "triage"}
        plan = await self._agents["triage"].run(
            description=self.packet.description,
            artifacts=self.packet.parsed_artifacts,
        )
        self.packet.agent_traces.append({"agent": "triage", "output": plan, "ts": datetime.utcnow().isoformat()})
        yield {"type": "trace", "agent": "triage", "data": plan}

        # --- Phase 3: Investigate (parallel agents) ---
        yield {"type": "status", "message": "Running parallel investigation agents...", "agent": "system"}
        investigation_tasks = [
            self._run_agent("log_analyst"),
            self._run_agent("visual_parser"),
            self._run_agent("runbook_retriever"),
        ]
        results = await asyncio.gather(*investigation_tasks, return_exceptions=True)

        for name, result in zip(["log_analyst", "visual_parser", "runbook_retriever"], results):
            if isinstance(result, Exception):
                yield {"type": "error", "agent": name, "data": str(result)}
                continue
            self.packet.agent_traces.append(
                {"agent": name, "output": result, "ts": datetime.utcnow().isoformat()}
            )
            yield {"type": "trace", "agent": name, "data": result}

        # --- Phase 4: Synthesize RCA ---
        yield {"type": "status", "message": "Synthesizing root cause...", "agent": "rca_synthesizer"}
        rca = await self._agents["rca_synthesizer"].run(
            description=self.packet.description,
            traces=self.packet.agent_traces,
            artifacts=self.packet.parsed_artifacts,
        )
        self.packet.agent_traces.append({"agent": "rca_synthesizer", "output": rca, "ts": datetime.utcnow().isoformat()})
        yield {"type": "trace", "agent": "rca_synthesizer", "data": rca}

        # --- Phase 5: Remediation plan ---
        yield {"type": "status", "message": "Drafting remediation plan...", "agent": "remediation_planner"}
        remediation = await self._agents["remediation_planner"].run(
            rca=rca,
            traces=self.packet.agent_traces,
        )
        self.packet.agent_traces.append(
            {"agent": "remediation_planner", "output": remediation, "ts": datetime.utcnow().isoformat()}
        )
        yield {"type": "trace", "agent": "remediation_planner", "data": remediation}

        # --- Phase 6: Human approval gate ---
        self.packet.final_report = {
            "rca": rca,
            "remediation": remediation,
            "traces": self.packet.agent_traces,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.packet.approval_status = "pending"
        yield {
            "type": "approval_required",
            "agent": "system",
            "data": {
                "message": "Human review required: approve RCA before ticket creation.",
                "report_summary": rca.get("summary", ""),
            },
        }

        # Wait loop — in production this pauses until the operator approves via the UI
        while self.packet.approval_status == "pending":
            await asyncio.sleep(1)

        if self.packet.approval_status == "approved":
            yield {"type": "status", "message": "Creating remediation ticket...", "agent": "system"}
            ticket = await self._create_ticket(remediation, rca)
            yield {"type": "ticket", "agent": "system", "data": ticket}
            yield {"type": "status", "message": "Investigation complete.", "agent": "system"}
        else:
            yield {"type": "status", "message": "Investigation rejected by operator.", "agent": "system"}

    async def _run_agent(self, name: str) -> Dict[str, Any]:
        agent = self._agents[name]
        return await agent.run(
            description=self.packet.description,
            artifacts=self.packet.parsed_artifacts,
            traces=self.packet.agent_traces,
            retriever=self.retriever,
        )

    async def _create_ticket(self, remediation: Dict[str, Any], rca: Dict[str, Any]) -> Dict[str, Any]:
        """Stub: create Jira/Slack ticket. Replace with real API calls."""
        return {
            "ticket_id": "NEXUS-101",
            "title": f"RCA: {rca.get('root_cause', 'Incident')}",
            "description": remediation.get("action_plan", ""),
            "status": "Open",
            "url": "https://jira.example.com/browse/NEXUS-101",
        }

    def approve(self) -> None:
        self.packet.approval_status = "approved"

    def reject(self) -> None:
        self.packet.approval_status = "rejected"

    @property
    def final_report(self) -> Optional[Dict[str, Any]]:
        return self.packet.final_report

    @final_report.setter
    def final_report(self, value: Optional[Dict[str, Any]]) -> None:
        self.packet.final_report = value
