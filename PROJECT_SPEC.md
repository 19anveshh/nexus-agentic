# Nexus — Autonomous Multimodal Incident Response & Root Cause Agent
**Track:** Generative AI & Agentic Systems — LLMs, multimodal agents, autonomous workflows  
**Hackathon:** NovaStark Hacks 2026 (Round 1 submission: PPT + GitHub, due 10 Dec 2026)

---

## 1. Problem Statement (for your PPT)

Modern IT operations teams are drowning in alert fatigue. When an incident fires, engineers must manually correlate evidence across five silos: log streams (text), dashboard screenshots (images), runbooks (PDFs), Slack threads (chat), and monitoring charts (images). Mean Time To Resolve (MTTR) stays high because the person on-call is copy-pasting between tabs instead of acting.

**Nexus** is an autonomous agentic system that ingests multimodal incident evidence, decomposes the investigation into parallel agent workflows, correlates root cause across text + images + documents, and drafts a remediation plan with human-in-the-loop approval — cutting MTTR from hours to minutes.

---

## 2. Why This Wins

| Judging Criterion | How Nexus Delivers |
|---|---|
| **Multimodal** | Parses logs (text), error screenshots & architecture diagrams (images), runbooks (PDFs), and chat transcripts in one pipeline |
| **Agentic** | 6 specialized agents run autonomously: Triage, Log Analyst, Visual Parser, Runbook Retriever, RCA Synthesizer, Remediation Planner |
| **Autonomous Workflow** | Goal-driven loop: ingest → plan → investigate → verify → report → ticket, with human approval gates |
| **Working Demo** | Upload incident packet → watch agents reason step-by-step → get RCA + remediation draft + Jira/Slack ticket |
| **Real Impact** | Directly reduces MTTR and on-call burnout; enterprise buyers pay for this |

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (React / HTML)                    │
│  Upload: logs, screenshots, runbooks, chat, describe issue  │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP / WebSocket
┌──────────────────▼──────────────────────────────────────────┐
│                 FASTAPI ORCHESTRATOR                         │
│  Session mgmt · artifact store · human approval gates · SSE │
└──────────────────┬──────────────────────────────────────────┘
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
┌─────────────┐         ┌─────────────┐
│  Triage     │────────▶│ Log Analyst │
│  Agent      │         │ (text LLM)  │
└──────┬──────┘         └──────┬──────┘
       │                       │
       ▼                       ▼
┌─────────────┐         ┌─────────────┐
│ Visual      │         │ Runbook     │
│ Parser      │────────▶│ Retriever   │
│ (VLM)       │         │ (PDF RAG)   │
└──────┬──────┘         └──────┬──────┘
       │                       │
       └───────────┬───────────┘
                   ▼
           ┌───────────────┐
           │ RCA Synthesizer│◀── correlates all evidence
           │ (LLM + graph)  │
           └───────┬───────┘
                   ▼
           ┌───────────────┐
           │ Remediation   │
           │ Planner       │──▶ draft fix + ticket
           └───────────────┘
```

**Human-in-the-loop gates:** After synthesis, the operator reviews the RCA draft and approves/edits before any ticket is created.

---

## 4. Tech Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn
- **Agent Orchestration:** Plain Python state machine (easy to swap to LangGraph later — no heavy install needed for demo)
- **LLM:** OpenAI GPT-4o / GPT-4o-mini (or local via Ollama — swap one line)
- **Multimodal:** GPT-4V for images, `pypdf` for PDFs, `python-docx` for docs
- **Vector Store:** ChromaDB (local, zero config) for runbook RAG
- **Frontend:** Vanilla HTML + Tailwind (zero build step — deployable anywhere)
- **Integrations:** Slack webhook, Jira REST (stubbed for demo)

---

## 5. Deliverables in This Repo

- `backend/main.py` — FastAPI app + websocket for live agent traces
- `backend/orchestrator.py` — autonomous agent loop with approval gates
- `backend/agents/` — 6 agent implementations
- `backend/ingestion.py` — multimodal parser (PDF, image, text, audio transcript)
- `backend/rag.py` — ChromaDB runbook retriever
- `frontend/index.html` — single-file demo UI
- `requirements.txt` — pinned dependencies
- `PROJECT_SPEC.md` — this document (copy into your PPT)

---

## 6. Round 1 Submission Checklist

- [ ] Team of 2–4 registered by 7 Dec 2026
- [ ] Public GitHub repo with this code + README
- [ ] PPT with: problem statement, architecture diagram, tech stack, demo screenshots
- [ ] GitHub repo/walkthrough link in submission
- [ ] Submit by 10 Dec 2026, 11:59 PM IST

---

## 7. Next Steps (Week by Week)

| Week | Milestone |
|------|-----------|
| 1 | Repo setup, agent skeleton, ingestion pipeline working |
| 2 | Visual parser + RAG runbooks, RCA synthesizer |
| 3 | Remediation planner, ticket drafting, approval gates |
| 4 | Frontend demo, end-to-end test with sample incident packet |
| 5 | Record walkthrough video, build PPT, polish README |
| 6 | Submit Round 1 by 10 Dec |

---

**Bottom line:** Nexus is high-end because it's not a chatbot — it's a multi-agent, multimodal, autonomous workflow that does real operational work. That's what wins hackathons.
