# Nexus — Autonomous Multimodal Incident Response Agent

NovaStark Hacks 2026 submission — Generative AI & Agentic Systems track.

## What it does

Nexus ingests multimodal incident evidence (logs, screenshots, runbook PDFs, chat transcripts), runs six autonomous agents in parallel, correlates root cause across text + images + documents, and drafts a remediation plan with a human-in-the-loop approval gate.

## Project structure

```
nexus-agentic/
├── PROJECT_SPEC.md          # Full spec + problem statement (copy into your PPT)
├── backend/
│   ├── main.py              # FastAPI app + WebSocket stream
│   ├── orchestrator.py      # Autonomous agent loop with approval gates
│   ├── ingestion.py         # Multimodal parser (PDF, image, text)
│   ├── rag.py               # Runbook retriever stub
│   ├── requirements.txt
│   └── agents/
│       ├── base.py          # Base agent + LLM wrapper
│       ├── registry.py      # Agent registry
│       ├── triage.py
│       ├── log_analyst.py
│       ├── visual_parser.py
│       ├── runbook_retriever.py
│       ├── rca_synthesizer.py
│       └── remediation_planner.py
└── frontend/
    └── index.html           # Single-file demo UI (Tailwind, zero build step)
```

## Quick start

```bash
cd nexus-agentic/backend
pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY if you have one
python main.py
```

Then open `frontend/index.html` (serve it with any static server, or just open the file) and point it at `http://localhost:8000`.

## Without an API key (demo mode)

If you don't set `OPENAI_API_KEY`, the LLM wrapper falls back to demo-mode responses so you can still demonstrate the full agentic flow, WebSocket streaming, and UI end-to-end.

## Round 1 submission

1. Register your 2–4 person crew by **7 Dec 2026** on Hack4Hack.
2. Push this repo to GitHub (public).
3. Build a PPT: problem statement (from PROJECT_SPEC.md), architecture diagram, tech stack, demo screenshots/video.
4. Submit PPT + GitHub link by **10 Dec 2026, 11:59 PM IST**.

## Extend for the finale

- Swap the placeholder LLM calls for real OpenAI GPT-4o / GPT-4V calls.
- Replace the ticket stub with real Jira/Slack webhook integration.
- Add ChromaDB vector search over runbooks instead of keyword matching.
- Add WebRTC / screen-capture ingestion for live war-room input.
