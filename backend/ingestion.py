"""Multimodal evidence ingestion pipeline."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def parse_evidence(paths: List[str]) -> Dict[str, Any]:
    """
    Parse uploaded files into modality buckets:
      - text: .log, .txt, .md, chat transcripts
      - pdf:  .pdf (extracted text)
      - images: .png, .jpg, .jpeg, .webp (paths for VLM)
    """
    buckets: Dict[str, List[str]] = {"text": [], "pdf": [], "images": []}

    for p in paths:
        path = Path(p)
        if not path.exists():
            continue
        suffix = path.suffix.lower()

        if suffix in {".log", ".txt", ".md", ".csv", ".json"}:
            try:
                buckets["text"].append(path.read_text(errors="ignore"))
            except Exception:
                buckets["text"].append(f"[unreadable: {path.name}]")

        elif suffix == ".pdf":
            try:
                import pypdf

                reader = pypdf.PdfReader(str(path))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                buckets["pdf"].append(text)
            except Exception:
                buckets["pdf"].append(f"[pdf parse failed: {path.name}]")

        elif suffix in {".png", ".jpg", ".jpeg", ".webp"}:
            buckets["images"].append({"path": str(path), "name": path.name})

    # Merge lists into single strings for LLM prompts
    return {
        "text": "\n\n---FILE BOUNDARY---\n\n".join(buckets["text"]),
        "pdf": "\n\n---PDF BOUNDARY---\n\n".join(buckets["pdf"]),
        "images": buckets["images"],
    }
