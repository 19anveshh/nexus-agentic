# Nexus Architecture

## Overview

Nexus is an autonomous multimodal incident response agent. It ingests evidence from multiple modalities, runs six specialized agents in a directed workflow, and produces a root cause analysis with a remediation plan — subject to human approval.

## Data Flow

```
Incident Description + Evidence Files
        │
        ▼
┌─────────────────┐
│  Triage Agent   │── Plan investigation → decompose into tasks
└────────┬────────┘
         │
         ▼
┌─────────────────┐─────────────────────────────────────┐
│ Parallel Agents │                                     │
│                 │                                     │
│ Log Analyst     │──► errors, exceptions, anomalies    │
│ Visual Parser   │──► screenshot text + structure      │
│ Runbook Ret.    │──► relevant remediation steps       │
└────────┬────────┘                                     │
         │                                              │
         ▼                                              │
┌─────────────────┐                                     │
│ RCA Synthesizer │──► correlate all traces → root cause│
└────────┬────────┘                                     │
         │                                              │
         ▼                                              │
┌─────────────────┐                                     │
│ Remediation Pl. │──► action plan + ticket stub        │
└────────┬────────┘                                     │
         │                                              │
         ▼                                              │
┌─────────────────┐◄────────────────────────────────────┘
│ Human Approval  │── approve / reject before ticketing
└────────┬────────┘
         │
      approved?
         │ yes
         ▼
   Remediation Ticket Created
```

## Components

| Component | File | Responsibility |
|-----------|------|----------------|
| Orchestrator | `backend/orchestrator.py` | Autonomous 6-phase loop with approval gate |
| API | `backend/main.py` | FastAPI app + WebSocket stream + session store |
| Ingestion | `backend/ingestion.py` | Multimodal parser (PDF, image, text) |
| RAG | `backend/rag.py` | Runbook retriever stub |
| Agents | `backend/agents/` | Six specialized agent implementations |
| Frontend | `frontend/index.html` | Zero-build Tailwind UI |

## Agent Details

| Agent | Input | Output |
|-------|-------|--------|
| Triage | description, artifacts | Investigation plan |
| Log Analyst | parsed artifacts | Log errors & anomalies |
| Visual Parser | image files | Extracted text + structure |
| Runbook Retriever | description, artifacts | Relevant runbook steps |
| RCA Synthesizer | all traces, artifacts | Root cause analysis |
| Remediation Planner | RCA, traces | Action plan + ticket |

## Key Design Decisions

- **IncidentPacket dataclass**: Carries session state through all phases (description, evidence, parsed artifacts, agent traces, final report, approval status)
- **WebSocket streaming**: Each agent yields structured trace events streamed live to the frontend
- **Human-in-the-loop**: Approval gate pauses execution until the operator approves or rejects via `/api/approve` or `/api/reject`
- **Demo mode**: LLM wrapper falls back to placeholder responses when no API key is configured
- **In-memory sessions**: `SESSIONS` dict stores orchestrators per session (replace with Redis/Postgres for production)

## Limitations

- In-memory session store resets on server restart
- Ticket creation is a stub (replace with real Jira/Slack webhooks)
- Runbook retrieval is keyword-based (upgrade to ChromaDB vector search)
- No authentication or multi-tenant isolation