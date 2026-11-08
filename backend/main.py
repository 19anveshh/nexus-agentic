"""Nexus — FastAPI backend for autonomous multimodal incident response."""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from orchestrator import NexusOrchestrator, IncidentPacket
from agents.registry import AGENT_REGISTRY

app = FastAPI(title="Nexus Agentic Incident Response")

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML at the root path."""
    return HTMLResponse(content=Path("frontend/index.html").read_text(), status_code=200)

# In-memory session store (replace with Redis/Postgres for production)
SESSIONS: Dict[str, Dict[str, Any]] = {}

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class StartInvestigation(BaseModel):
    description: str
    session_id: Optional[str] = None


@app.post("/api/investigate")
async def start_investigation(payload: StartInvestigation):
    """Create a new investigation session."""
    session_id = payload.session_id or str(uuid.uuid4())
    orchestrator = NexusOrchestrator(session_id=session_id)
    SESSIONS[session_id] = {
        "orchestrator": orchestrator,
        "created_at": datetime.utcnow().isoformat(),
        "status": "initialized",
        "artifacts": [],
    }
    return {"session_id": session_id, "status": "initialized"}


@app.post("/api/session/{session_id}/evidence")
async def upload_evidence(session_id: str, files: List[UploadFile] = File(...)):
    """Attach multimodal evidence to a session."""
    if session_id not in SESSIONS:
        return JSONResponse({"error": "session not found"}, status_code=404)

    saved: List[str] = []
    for f in files:
        dest = UPLOAD_DIR / f"{session_id}_{f.filename}"
        contents = await f.read()
        dest.write_bytes(contents)
        saved.append(str(dest))
        SESSIONS[session_id].setdefault("evidence", []).append(
            {"filename": f.filename, "path": str(dest), "content_type": f.content_type}
        )
    SESSIONS[session_id]["status"] = "evidence_ready"
    return {"session_id": session_id, "files": saved}


@app.websocket("/api/session/{session_id}/stream")
async def stream_investigation(websocket: WebSocket, session_id: str):
    """Server-sent stream of agent reasoning traces via WebSocket."""
    await websocket.accept()
    if session_id not in SESSIONS:
        await websocket.send_json({"error": "session not found"})
        await websocket.close()
        return

    orchestrator: NexusOrchestrator = SESSIONS[session_id]["orchestrator"]
    try:
        async for event in orchestrator.run():
            await websocket.send_json(event)
            # small delay so the frontend can render progress
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()


@app.get("/api/session/{session_id}/report")
async def get_report(session_id: str):
    """Return the final RCA + remediation report."""
    if session_id not in SESSIONS:
        return JSONResponse({"error": "session not found"}, status_code=404)
    orchestrator: NexusOrchestrator = SESSIONS[session_id]["orchestrator"]
    return {
        "session_id": session_id,
        "report": orchestrator.final_report,
        "status": SESSIONS[session_id]["status"],
    }


@app.get("/api/health")
async def health():
    return {"status": "ok", "agents": list(AGENT_REGISTRY.keys())}


if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
