"""Agent registry — maps agent names to classes."""
from .base import BaseAgent
from .triage import TriageAgent
from .log_analyst import LogAnalystAgent
from .visual_parser import VisualParserAgent
from .runbook_retriever import RunbookRetrieverAgent
from .rca_synthesizer import RCASynthesizerAgent
from .remediation_planner import RemediationPlannerAgent

AGENT_REGISTRY = {
    "triage": TriageAgent,
    "log_analyst": LogAnalystAgent,
    "visual_parser": VisualParserAgent,
    "runbook_retriever": RunbookRetrieverAgent,
    "rca_synthesizer": RCASynthesizerAgent,
    "remediation_planner": RemediationPlannerAgent,
}

__all__ = ["AGENT_REGISTRY", "BaseAgent"]
