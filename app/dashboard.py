"""Governance intelligence: aggregates review telemetry."""

from collections import Counter, defaultdict
from datetime import datetime, timedelta

from .database import SessionLocal
from .models import Asset, AuditLog, Flag, Scan, ScanStatus


def _db():
    return SessionLocal()


def overview():
    db = _db()
    try:
        total_assets = db.query(Asset).count()
        by_state = defaultdict(int)
        for r in db.query(Asset.state).all():
            by_state[r[0]] += 1
        total_flags = db.query(Flag).count()
        open_flags = db.query(Flag).filter(Flag.status == "open").count()
        accepted = db.query(Flag).filter(Flag.status == "accepted").count()
        dismissed = db.query(Flag).filter(Flag.status == "dismissed").count()
        edited = db.query(Flag).filter(Flag.status == "edited").count()
        return {
            "total_assets": total_assets,
            "by_state": dict(by_state),
            "total_flags": total_flags,
            "open_flags": open_flags,
            "decided_flags": accepted + dismissed + edited,
            "accept_rate": round(accepted / max(1, accepted + dismissed + edited) * 100, 1),
        }
    finally:
        db.close()


def flags_by_dimension():
    db = _db()
    try:
        rows = db.query(Flag.dimension, Flag.status).all()
        agg = defaultdict(lambda: Counter())
        for dim, status in rows:
            agg[dim][status] += 1
        return {dim: dict(cnt) for dim, cnt in agg.items()}
    finally:
        db.close()


def top_broken_rules(limit: int = 5):
    """Most frequently flagged dimensions (recurring compliance blind spots)."""
    db = _db()
    try:
        rows = db.query(Flag.dimension).all()
        cnt = Counter(r[0] for r in rows)
        return [{"rule": k, "flag_count": v} for k, v in cnt.most_common(limit)]
    finally:
        db.close()


def override_rate():
    """Share of flags dismissed or edited (high = ambiguous rules)."""
    db = _db()
    try:
        total = db.query(Flag).filter(Flag.status != "open").count()
        overridden = (
            db.query(Flag)
            .filter(Flag.status.in_(["dismissed", "edited"]))
            .count()
        )
        return {"override_rate": round(overridden / max(1, total) * 100, 1), "total": total, "overridden": overridden}
    finally:
        db.close()


def recent_escapes(limit: int = 10):
    """Published assets that had critical/high flags accepted (potential escapes)."""
    db = _db()
    try:
        rows = (
            db.query(Flag)
            .join(Asset, Flag.asset_id == Asset.id)
            .filter(Asset.state == "Published", Flag.severity.in_(["critical", "high"]))
            .order_by(Flag.id.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "asset_id": f.asset_id,
                "asset_title": db.query(Asset.title).filter(Asset.id == f.asset_id).scalar(),
                "dimension": f.dimension,
                "severity": f.severity,
                "decision": f.status,
            }
            for f in rows
        ]
    finally:
        db.close()
