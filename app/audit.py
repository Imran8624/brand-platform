"""Tamper-evident append-only audit trail."""

from .database import SessionLocal
from .models import AuditLog


def log(
    db,
    asset_id: int,
    action: str,
    actor: str,
    actor_role: str,
    old_state: str = None,
    new_state: str = None,
    details: dict = None,
):
    import json
    entry = AuditLog(
        asset_id=asset_id,
        action=action,
        actor=actor,
        actor_role=actor_role,
        old_state=old_state,
        new_state=new_state,
        details=json.dumps(details or {}),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_audit_trail(db, asset_id: int):
    rows = (
        db.query(AuditLog)
        .filter(AuditLog.asset_id == asset_id)
        .order_by(AuditLog.timestamp.asc())
        .all()
    )
    return [
        {
            "id": r.id,
            "action": r.action,
            "actor": r.actor,
            "actor_role": r.actor_role,
            "old_state": r.old_state,
            "new_state": r.new_state,
            "details": r.details,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        }
        for r in rows
    ]
