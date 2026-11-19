"""Brand Governance Platform — FastAPI backend."""

import json
import os
import shutil
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import audit as audit_mod
from . import dashboard as dash_mod
from . import ingest as ingest_mod
from . import inkloom_api
from . import remediate as rem_mod
from . import scan as scan_mod
from .database import Base, SessionLocal, engine
from .models import (
    Asset,
    AssetState,
    AuditLog,
    BannedTerm,
    BrandGuideline,
    FactSheetRow,
    Flag,
    FlagDecision,
    Scan,
    ScanStatus,
    UserRole,
    VoiceRule,
)

# ---------------------------------------------------------------------------
# App & DB init
# ---------------------------------------------------------------------------

app = FastAPI(title="Brand Governance Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inkloom_api.router)

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Simple in-memory session (hackathon demo). In prod: proper auth + DB sessions.
SESSION = {"user": {"name": "Demo Creator", "role": UserRole.CREATOR.value}}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Session / current user
# ---------------------------------------------------------------------------

@app.get("/api/me")
def me():
    return SESSION["user"]


@app.post("/api/session/role")
def set_role(role: str = Form(...)):
    if role not in [r.value for r in UserRole]:
        raise HTTPException(status_code=400, detail="Invalid role")
    SESSION["user"]["role"] = role
    # adjust display name by role
    name_map = {
        UserRole.CREATOR.value: "Demo Creator",
        UserRole.BRAND_MANAGER.value: "Brand Manager",
        UserRole.LEGAL_REVIEWER.value: "Legal Reviewer",
        UserRole.ADMIN.value: "Admin",
        UserRole.ADMIN_COMPANY_REVIEW.value: "Admin & Company Review",
    }
    SESSION["user"]["name"] = name_map.get(role, "User")
    return SESSION["user"]


def require_roles(allowed: List[str]):
    def checker():
        user = SESSION["user"]
        user_role = user.get("role")
        if user_role == UserRole.ADMIN_COMPANY_REVIEW.value:
            if any(r in [UserRole.ADMIN.value, UserRole.LEGAL_REVIEWER.value, UserRole.ADMIN_COMPANY_REVIEW.value] for r in allowed):
                return user
        if user_role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user['role']}' not authorized. Required: {allowed}",
            )
        return user
    return checker


# ---------------------------------------------------------------------------
# Guidelines (single source of truth)
# ---------------------------------------------------------------------------

@app.get("/api/guidelines")
def list_guidelines():
    return ingest_mod.list_guidelines()


@app.post("/api/guidelines/upload")
def upload_guideline(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    version: Optional[str] = Form(None),
    user=Depends(require_roles([UserRole.ADMIN.value, UserRole.BRAND_MANAGER.value])),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".txt", ".docx"):
        raise HTTPException(status_code=400, detail="Only .pdf/.txt/.docx allowed")
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        gl = ingest_mod.ingest_guideline(save_path, title=title, version=version)
        audit_mod.log(
            SessionLocal(),
            asset_id=0,
            action="guideline_upload",
            actor=user["name"],
            actor_role=user["role"],
            new_state=gl.version,
            details={"title": gl.title, "file": file.filename},
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        file.file.close()
    return {
        "id": gl.id,
        "version": gl.version,
        "title": gl.title,
        "source_file": gl.source_file,
        "fact_count": len(gl.fact_rows),
        "banned_count": len(gl.banned_terms),
        "voice_count": len(gl.voice_rules),
    }


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

def _serialize_asset(db, a: Asset) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "author_name": a.author_name,
        "author_role": a.author_role,
        "content_text": a.content_text,
        "file_path": a.file_path,
        "file_type": a.file_type,
        "state": a.state.value if isinstance(a.state, AssetState) else a.state,
        "current_guideline_version": a.current_guideline_version,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "updated_at": a.updated_at.isoformat() if a.updated_at else None,
        "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
        "approved_at": a.approved_at.isoformat() if a.approved_at else None,
        "published_at": a.published_at.isoformat() if a.published_at else None,
    }


@app.get("/api/assets")
def list_assets():
    db = SessionLocal()
    try:
        rows = db.query(Asset).order_by(Asset.created_at.desc()).all()
        return [_serialize_asset(db, a) for a in rows]
    finally:
        db.close()


@app.post("/api/assets")
def create_asset(
    title: str = Form(...),
    author_name: str = Form("Demo Creator"),
    author_role: str = Form(UserRole.CREATOR.value),
    content_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user=Depends(require_roles([UserRole.CREATOR.value, UserRole.ADMIN.value, UserRole.BRAND_MANAGER.value])),
):
    db = SessionLocal()
    try:
        gl = db.query(BrandGuideline).filter(BrandGuideline.is_active == True).first()  # noqa: E712
        file_path = None
        file_type = None
        if file is not None:
            save_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_path = save_path
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"):
                file_type = "image"
            elif ext == ".pdf":
                file_type = "pdf"
            elif ext == ".docx":
                file_type = "docx"
            elif ext == ".txt":
                file_type = "text"
            else:
                file_type = "other"

        a = Asset(
            title=title,
            author_name=author_name,
            author_role=author_role,
            content_text=content_text,
            file_path=file_path,
            file_type=file_type,
            state=AssetState.DRAFT,
            current_guideline_version=gl.version if gl else None,
        )
        db.add(a)
        db.commit()
        db.refresh(a)
        audit_mod.log(
            db, a.id, "asset_created", user["name"], user["role"],
            new_state=a.state.value,
            details={"title": title},
        )
        return _serialize_asset(db, a)
    finally:
        db.close()
        if file is not None:
            file.file.close()


@app.get("/api/assets/{asset_id}")
def get_asset(asset_id: int):
    db = SessionLocal()
    try:
        a = db.query(Asset).filter(Asset.id == asset_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Asset not found")
        return _serialize_asset(db, a)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Submit for review (Draft -> In Review)
# ---------------------------------------------------------------------------

@app.post("/api/assets/{asset_id}/submit")
def submit_for_review(asset_id: int, user=Depends(require_roles([UserRole.CREATOR.value, UserRole.ADMIN.value]))):
    db = SessionLocal()
    try:
        a = db.query(Asset).filter(Asset.id == asset_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Asset not found")
        if a.state != AssetState.DRAFT:
            raise HTTPException(status_code=400, detail="Only Draft assets can be submitted")
        old = a.state.value
        a.state = AssetState.IN_REVIEW
        a.submitted_at = datetime.now()
        db.add(a)
        db.commit()
        audit_mod.log(db, a.id, "state_change", user["name"], user["role"], old_state=old, new_state=a.state.value)
        return {"id": a.id, "state": a.state.value}
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------

@app.post("/api/assets/{asset_id}/scan")
def run_scan(asset_id: int, user=Depends(require_roles([UserRole.CREATOR.value, UserRole.ADMIN.value, UserRole.BRAND_MANAGER.value, UserRole.LEGAL_REVIEWER.value]))):
    db = SessionLocal()
    try:
        a = db.query(Asset).filter(Asset.id == asset_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Asset not found")
        results = scan_mod.run_scan_all(db, a)
        audit_mod.log(db, a.id, "scan_run", user["name"], user["role"],
                      details={"results": results})
        return {"asset_id": a.id, "results": results}
    finally:
        db.close()


@app.get("/api/assets/{asset_id}/scan")
def get_scans(asset_id: int):
    db = SessionLocal()
    try:
        scans = db.query(Scan).filter(Scan.asset_id == asset_id).all()
        return [
            {
                "id": s.id,
                "dimension": s.dimension,
                "status": s.status.value if isinstance(s.status, ScanStatus) else s.status,
                "score": s.score,
                "detection_method": s.detection_method,
                "scanned_at": s.scanned_at.isoformat() if s.scanned_at else None,
                "details": json.loads(s.details) if s.details else {},
            }
            for s in scans
        ]
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Flags (human-in-the-loop decisions)
# ---------------------------------------------------------------------------

@app.get("/api/assets/{asset_id}/flags")
def list_flags(asset_id: int):
    db = SessionLocal()
    try:
        rows = db.query(Flag).filter(Flag.asset_id == asset_id).order_by(Flag.id.asc()).all()
        return [
            {
                "id": f.id,
                "dimension": f.dimension,
                "severity": f.severity,
                "element": f.element,
                "rationale": f.rationale,
                "source_citation": f.source_citation,
                "suggested_fix": f.suggested_fix,
                "original_text": f.original_text,
                "status": f.status.value if isinstance(f.status, FlagDecision) else f.status,
                "decided_by": f.decided_by,
                "decided_by_role": f.decided_by_role,
                "decided_at": f.decided_at.isoformat() if f.decided_at else None,
                "decision_reason": f.decision_reason,
                "resolved_text": f.resolved_text,
            }
            for f in rows
        ]
    finally:
        db.close()


@app.post("/api/flags/{flag_id}/decide")
def decide_flag(
    flag_id: int,
    decision: str = Form(...),
    reason: Optional[str] = Form(None),
    resolved_text: Optional[str] = Form(None),
    user=Depends(require_roles([UserRole.CREATOR.value, UserRole.ADMIN.value, UserRole.BRAND_MANAGER.value, UserRole.LEGAL_REVIEWER.value])),
):
    if decision not in [d.value for d in FlagDecision]:
        raise HTTPException(status_code=400, detail="Invalid decision")
    db = SessionLocal()
    try:
        f = db.query(Flag).filter(Flag.id == flag_id).first()
        if not f:
            raise HTTPException(status_code=404, detail="Flag not found")
        old = f.status.value if isinstance(f.status, FlagDecision) else f.status
        f.status = FlagDecision(decision)
        f.decided_by = user["name"]
        f.decided_by_role = user["role"]
        f.decided_at = datetime.now()
        f.decision_reason = reason
        if resolved_text is not None:
            f.resolved_text = resolved_text
            f.status = FlagDecision.EDITED
        db.add(f)
        db.commit()
        audit_mod.log(
            db, f.asset_id, "flag_decision", user["name"], user["role"],
            old_state=old, new_state=f.status.value,
            details={"flag_id": f.id, "dimension": f.dimension, "decision": decision, "reason": reason},
        )
        return {"id": f.id, "status": f.status.value}
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Approve / Reject / Publish (role-gated state transitions)
# ---------------------------------------------------------------------------

@app.post("/api/assets/{asset_id}/approve")
def approve_asset(asset_id: int, user=Depends(require_roles([UserRole.BRAND_MANAGER.value, UserRole.LEGAL_REVIEWER.value, UserRole.ADMIN.value]))):
    db = SessionLocal()
    try:
        a = db.query(Asset).filter(Asset.id == asset_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Asset not found")
        if a.state != AssetState.IN_REVIEW:
            raise HTTPException(status_code=400, detail="Only In Review assets can be approved")
        pending = (
            db.query(Flag)
            .filter(Flag.asset_id == asset_id, Flag.status == "open",
                    Flag.severity.in_(["critical", "high"]))
            .count()
        )
        if pending:
            raise HTTPException(
                status_code=400,
                detail=f"{pending} critical/high flags must be resolved before approval",
            )
        old = a.state.value
        a.state = AssetState.APPROVED
        a.approved_at = datetime.now()
        db.add(a)
        db.commit()
        audit_mod.log(db, a.id, "state_change", user["name"], user["role"], old_state=old, new_state=a.state.value)
        return {"id": a.id, "state": a.state.value}
    finally:
        db.close()


@app.post("/api/assets/{asset_id}/reject")
def reject_asset(
    asset_id: int,
    reason: Optional[str] = Form(None),
    user=Depends(require_roles([UserRole.BRAND_MANAGER.value, UserRole.LEGAL_REVIEWER.value, UserRole.ADMIN.value])),
):
    db = SessionLocal()
    try:
        a = db.query(Asset).filter(Asset.id == asset_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Asset not found")
        old = a.state.value
        a.state = AssetState.DRAFT
        db.add(a)
        db.commit()
        audit_mod.log(db, a.id, "state_change", user["name"], user["role"],
                      old_state=old, new_state=a.state.value,
                      details={"reason": reason})
        return {"id": a.id, "state": a.state.value}
    finally:
        db.close()


@app.post("/api/assets/{asset_id}/publish")
def publish_asset(asset_id: int, user=Depends(require_roles([UserRole.BRAND_MANAGER.value, UserRole.ADMIN.value]))):
    db = SessionLocal()
    try:
        a = db.query(Asset).filter(Asset.id == asset_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Asset not found")
        if a.state != AssetState.APPROVED:
            raise HTTPException(status_code=400, detail="Only Approved assets can be published")
        old = a.state.value
        a.state = AssetState.PUBLISHED
        a.published_at = datetime.now()
        db.add(a)
        db.commit()
        audit_mod.log(db, a.id, "state_change", user["name"], user["role"], old_state=old, new_state=a.state.value)
        return {"id": a.id, "state": a.state.value}
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Audit trail
# ---------------------------------------------------------------------------

@app.get("/api/assets/{asset_id}/audit")
def get_audit(asset_id: int):
    db = SessionLocal()
    try:
        return audit_mod.get_audit_trail(db, asset_id)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Dashboard / telemetry
# ---------------------------------------------------------------------------

@app.get("/api/dashboard")
def dashboard():
    return {
        "overview": dash_mod.overview(),
        "flags_by_dimension": dash_mod.flags_by_dimension(),
        "top_broken_rules": dash_mod.top_broken_rules(),
        "override_rate": dash_mod.override_rate(),
        "recent_escapes": dash_mod.recent_escapes(),
    }


# ---------------------------------------------------------------------------
# Static frontend + file serving
# ---------------------------------------------------------------------------

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse("frontend/index.html")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return JSONResponse(status_code=204, content=None)
