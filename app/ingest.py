"""Document ingestion: extract text from PDF/TXT/DOCX and seed the versioned KB."""

import os
import re
from datetime import datetime
from typing import List, Tuple

import pdfplumber
from docx import Document as DocxDocument

from .database import SessionLocal
from .models import (
    BannedTerm,
    BrandGuideline,
    FactSheetRow,
    VoiceRule,
)


def extract_text(file_path: str) -> str:
    """Extract plain text from a .txt / .pdf / .docx file."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext == ".pdf":
        parts: List[str] = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                parts.append(page.extract_text() or "")
        return "\n".join(parts)
    if ext == ".docx":
        doc = DocxDocument(file_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    raise ValueError(f"Unsupported file type: {ext}")


def _lines(text: str) -> List[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def parse_guideline(text: str) -> Tuple[str, List[dict], List[dict], List[dict]]:
    """
    Heuristically parse a brand guideline document into:
      (title, fact_rows, banned_terms, voice_rules)

    Deterministic (no external LLM). A real deployment would hand the raw text
    to an LLM for structured extraction; here we keep it fully offline.
    """
    lines = _lines(text)
    title = lines[0] if lines else "Brand Guidelines"

    fact_rows: List[dict] = []
    banned_terms: List[dict] = []
    voice_rules: List[dict] = []

    # Fact sheet rows: "Entity | Claim | Value" style lines
    fact_pat = re.compile(
        r"^(?P<entity>[A-Z][A-Za-z0-9 &'_\-]{2,40})\s*[\|:]\s*"
        r"(?P<claim>[A-Za-z0-9 %._\-]{2,40})\s*[\|:]\s*"
        r"(?P<value>[0-9]+(?:\.[0-9]+)?%?\$?[A-Za-z]*)$"
    )
    for ln in lines:
        m = fact_pat.match(ln)
        if m:
            fact_rows.append({
                "entity": m.group("entity").strip(),
                "claim": m.group("claim").strip(),
                "value": m.group("value").strip(),
                "source_quote": ln,
                "category": "performance",
            })

    # Banned terms: "DO NOT USE: term -> replacement"
    banned_pat = re.compile(
        r"(?:do not use|banned|deprecated|avoid)\s*[:\-]\s*(?P<term>[A-Za-z0-9 &_\-]+)"
        r"(?:\s*[-–>]\s*(?P<replacement>[A-Za-z0-9 &_\-]+))?",
        re.IGNORECASE,
    )
    for ln in lines:
        m = banned_pat.search(ln)
        if m:
            banned_terms.append({
                "term": m.group("term").strip(),
                "replacement": (m.group("replacement") or "").strip() or None,
                "category": "deprecated_name",
                "severity": "high",
            })

    # Voice rules: lines mentioning tone / voice
    voice_keywords = ["tone", "voice", "voice:", "hype", "aggressive", "jargon", "passive"]
    for ln in lines:
        low = ln.lower()
        if any(k in low for k in voice_keywords) and len(ln) < 120:
            category = "jargon"
            if "aggressive" in low or "hype" in low:
                category = "aggressive_hype"
            elif "passive" in low:
                category = "passive_voice"
            voice_rules.append({
                "pattern": ln,
                "category": category,
                "description": f"Avoid phrasing like: {ln}",
                "severity": "medium",
            })

    return title, fact_rows, banned_terms, voice_rules


def ingest_guideline(file_path: str, title: str = None, version: str = None):
    """Extract + parse a guideline file and persist it as a new KB version."""
    text = extract_text(file_path)
    if not text.strip():
        raise ValueError("No text could be extracted from the file.")

    parsed_title, fact_rows, banned_terms, voice_rules = parse_guideline(text)
    title = title or parsed_title
    version = version or datetime.now().strftime("%Y.%m")

    db = SessionLocal()
    try:
        # Deactivate previous active guidelines (single source of truth = latest active)
        db.query(BrandGuideline).filter(BrandGuideline.is_active == True).update(  # noqa: E712
            {BrandGuideline.is_active: False}
        )

        guideline = BrandGuideline(
            version=version,
            title=title,
            content_text=text,
            source_file=os.path.basename(file_path),
            is_active=True,
        )
        db.add(guideline)
        db.flush()  # get guideline.id

        for fr in fact_rows:
            db.add(FactSheetRow(guideline_id=guideline.id, **fr))
        for bt in banned_terms:
            db.add(BannedTerm(guideline_id=guideline.id, **bt))
        for vr in voice_rules:
            db.add(VoiceRule(guideline_id=guideline.id, **vr))

        db.commit()
        db.refresh(guideline)
        # Eager-load relationships while the session is still open so the
        # returned object can be inspected after the session closes.
        _ = len(guideline.fact_rows)
        _ = len(guideline.banned_terms)
        _ = len(guideline.voice_rules)
        return guideline
    finally:
        db.close()


def list_guidelines():
    db = SessionLocal()
    try:
        rows = db.query(BrandGuideline).order_by(BrandGuideline.created_at.desc()).all()
        return [
            {
                "id": r.id,
                "version": r.version,
                "title": r.title,
                "source_file": r.source_file,
                "is_active": r.is_active,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "fact_count": len(r.fact_rows),
                "banned_count": len(r.banned_terms),
                "voice_count": len(r.voice_rules),
            }
            for r in rows
        ]
    finally:
        db.close()
