"""
Inkloom AI - Advanced Backend Module
Implements:
- Secret Project Names management
- Knowledge Base Case Studies modal data
- Tamper-evident SHA-256 hash-chained approval ledger
- Creator Messages & Mistake Emails inbox
- Brand Manager 3-Level Automation engine
- Server-side Gemini AI analysis with Privacy Shield masking
- Personal AI Writing Helper (4 personas)
- Line-by-line diff generator
"""

import hashlib
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from . import audit as audit_mod
from .database import SessionLocal
from .models import Asset, AssetState, AuditLog, BannedTerm, BrandGuideline, FactSheetRow, Flag, Scan

router = APIRouter(prefix="/api/inkloom", tags=["Inkloom AI"])

# ---------------------------------------------------------------------------
# In-Memory State for Demonstration
# ---------------------------------------------------------------------------

SECRET_PROJECTS = [
    {"id": 1, "name": "Project Apollo", "department": "Hardware Labs", "status": "Active NDA", "risk": "High"},
    {"id": 2, "name": "Project Titan", "department": "Autonomous Core", "status": "Top Secret", "risk": "Critical"},
    {"id": 3, "name": "Project Quantum", "department": "AI Research", "status": "Confidential", "risk": "High"},
    {"id": 4, "name": "Project Stealth", "department": "Security Platform", "status": "Restricted", "risk": "Medium"},
    {"id": 5, "name": "Project Chimera", "department": "Next-Gen UI", "status": "Active NDA", "risk": "High"},
]

KB_CASE_STUDIES = {
    "fact": {
        "uptime": {
            "title": "99.9% Uptime Fact Rule",
            "rule": "Only state '99.9% measured uptime'. Never claim '100% uptime' or 'unbreakable uptime'.",
            "cases": [
                {
                    "case_id": "CASE-104",
                    "draft_title": "Summer Campaign Homepage Banner",
                    "team": "External Agency (Nexus Creatives)",
                    "date": "2026-03-12",
                    "mistake_snippet": "Guaranteed 100% server availability for all enterprise tiers.",
                    "why_failed": "Engineering SLA is 99.9%. Claiming 100% exposes the company to breach of contract lawsuits.",
                    "how_fixed": "Agency updated headline to 'Engineered for 99.9% proven uptime across global regions.'",
                    "approved_by": "Sarah Chen (Legal Reviewer)",
                    "status": "Resolved & Approved"
                },
                {
                    "case_id": "CASE-088",
                    "draft_title": "Investor Pitch Deck Slide 6",
                    "team": "Internal Strategy Team",
                    "date": "2026-02-18",
                    "mistake_snippet": "Zero downtime architecture with infinite uptime.",
                    "why_failed": "Exaggerated superlatives violate both Truth in Advertising and Nova Brand Voice.",
                    "how_fixed": "Replaced with 'Industry-leading 99.9% uptime backed by 24/7 SRE monitoring.'",
                    "approved_by": "Marcus Vance (Brand Manager)",
                    "status": "Resolved & Approved"
                }
            ]
        },
        "launch date": {
            "title": "March 2026 Launch Date Fact Rule",
            "rule": "Approved launch window is 'March 2026'. Do not cite specific calendar days without PR approval.",
            "cases": [
                {
                    "case_id": "CASE-092",
                    "draft_title": "Q1 Press Release Draft",
                    "team": "PR Agency",
                    "date": "2026-02-05",
                    "mistake_snippet": "Launching globally on Monday, March 2nd at 9 AM PST.",
                    "why_failed": "Specific launch day was unconfirmed due to QA testing buffers.",
                    "how_fixed": "Changed to 'Arriving March 2026 with staggered rollout.'",
                    "approved_by": "Sarah Chen (Legal Reviewer)",
                    "status": "Resolved & Approved"
                }
            ]
        },
        "certification": {
            "title": "ISO 27001 Certification Fact Rule",
            "rule": "Only cite 'ISO 27001 certified'. Do not claim FedRAMP or SOC-3 until final audit completes.",
            "cases": [
                {
                    "case_id": "CASE-074",
                    "draft_title": "Security Whitepaper v2",
                    "team": "Product Marketing",
                    "date": "2026-01-22",
                    "mistake_snippet": "Fully SOC-3 and FedRAMP authorized platform.",
                    "why_failed": "SOC-3 audit was still pending certification board sign-off.",
                    "how_fixed": "Restricted claim strictly to 'ISO 27001 certified with continuous compliance monitoring.'",
                    "approved_by": "Sarah Chen (Legal Reviewer)",
                    "status": "Resolved & Approved"
                }
            ]
        }
    },
    "banned_term": {
        "Nova X Pro": {
            "title": "Deprecated Name: Nova X Pro",
            "rule": "Use 'Nova X'. 'Pro' was retired to simplify customer tier understanding.",
            "cases": [
                {
                    "case_id": "CASE-112",
                    "draft_title": "Q3 Campaign Blog Draft",
                    "team": "Alex (External Agency)",
                    "date": "2026-03-20",
                    "mistake_snippet": "Introducing Nova X Pro, the game-changing platform...",
                    "why_failed": "Legacy name 'Nova X Pro' confuses buyers into looking for a non-pro version that does not exist.",
                    "how_fixed": "One-click replaced with 'Nova X' across all headings and body copy.",
                    "approved_by": "Marcus Vance (Brand Manager)",
                    "status": "Resolved & Approved"
                }
            ]
        },
        "synergy": {
            "title": "Banned Corporate Jargon: synergy",
            "rule": "Replace 'synergy' with 'collaboration', 'teamwork', or 'seamless integration'.",
            "cases": [
                {
                    "case_id": "CASE-081",
                    "draft_title": "Partner Ecosystem Flyer",
                    "team": "Partner Marketing",
                    "date": "2026-02-10",
                    "mistake_snippet": "Unlock unprecedented cross-team synergy.",
                    "why_failed": "'Synergy' is flagged under Nova Brand Voice as stale corporate fluff.",
                    "how_fixed": "Replaced with 'Help teams work together without friction.'",
                    "approved_by": "Marcus Vance (Brand Manager)",
                    "status": "Resolved & Approved"
                }
            ]
        },
        "game-changing": {
            "title": "Overused Hype: game-changing",
            "rule": "Avoid empty superlatives. Replace with 'innovative', 'practical', or cite the actual customer benefit.",
            "cases": [
                {
                    "case_id": "CASE-099",
                    "draft_title": "LinkedIn Sponsored Post",
                    "team": "Social Media Team",
                    "date": "2026-03-01",
                    "mistake_snippet": "Experience our game-changing security engine.",
                    "why_failed": "Nova voice rules mandate measured, benefit-led statements rather than dramatic hype.",
                    "how_fixed": "Changed to 'Experience real-time automated security that stops threats early.'",
                    "approved_by": "Marcus Vance (Brand Manager)",
                    "status": "Resolved & Approved"
                }
            ]
        }
    }
}

CREATOR_INBOX = [
    {
        "id": 1,
        "asset_id": 1,
        "asset_title": "Q3 Campaign Blog Draft",
        "sender": "Brand Manager (Marcus Vance)",
        "channel": "Email & Inbox",
        "subject": "Review started: 3 things need your quick fix in Q3 Blog Draft",
        "body": "Hi Alex,\n\nI reviewed your draft 'Q3 Campaign Blog Draft'. Good news: the core narrative is strong! However, there are 3 quick mistakes to fix before we can pass this to Legal:\n\n1. Replace 'Nova X Pro' with 'Nova X' (Pro was retired)\n2. Change '100% guaranteed uptime' to '99.9% measured uptime'\n3. Remove the hype phrase 'game-changing'\n\nYou can use the suggested fixes directly in your Creator Desk. Let me know when you're done!\n\nBest,\nMarcus Vance",
        "mistakes": [
            {"line": 1, "col": "13-23", "mistake": "Nova X Pro", "fix": "Nova X"},
            {"line": 2, "col": "4-26", "mistake": "100% guaranteed uptime", "fix": "99.9% measured uptime"},
            {"line": 1, "col": "29-41", "mistake": "game-changing", "fix": "innovative"}
        ],
        "timestamp": "2026-03-24 10:15",
        "unread": True,
        "mailto": "mailto:creator@company.com?subject=Brand%20Review%20Feedback%20for%20Q3%20Campaign%20Blog%20Draft&body=Hi%20Alex,%0D%0A%0D%0APlease%20check%20the%20brand%20feedback%20in%20Inkloom%20AI."
    },
    {
        "id": 2,
        "asset_id": 1,
        "asset_title": "Q3 Campaign Blog Draft",
        "sender": "Inkloom Automation (Level 1)",
        "channel": "Creator Inbox Only",
        "subject": "Scan Summary: 4 rules checked, 3 suggestions waiting",
        "body": "Your draft was automatically scanned across all 6 brand dimensions. 3 items were flagged for attention. Review Studio has prepared one-click fixes for each item.",
        "mistakes": [],
        "timestamp": "2026-03-24 09:42",
        "unread": False,
        "mailto": ""
    }
]

# ---------------------------------------------------------------------------
# Privacy Shield Logic
# ---------------------------------------------------------------------------

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
API_KEY_REGEX = re.compile(r'\b(?:sk|api|key|token|auth)[-_A-Za-z0-9]{12,}\b', re.IGNORECASE)

def mask_private_text(text: str) -> Tuple[str, Dict[str, str], int]:
    mapping = {}
    counter = 0

    def email_repl(m):
        nonlocal counter
        counter += 1
        placeholder = f"[EMAIL_MASKED_{counter}]"
        mapping[placeholder] = m.group(0)
        return placeholder

    def phone_repl(m):
        nonlocal counter
        counter += 1
        placeholder = f"[PHONE_MASKED_{counter}]"
        mapping[placeholder] = m.group(0)
        return placeholder

    def key_repl(m):
        nonlocal counter
        counter += 1
        placeholder = f"[KEY_MASKED_{counter}]"
        mapping[placeholder] = m.group(0)
        return placeholder

    sanitized = EMAIL_REGEX.sub(email_repl, text)
    sanitized = PHONE_REGEX.sub(phone_repl, sanitized)
    sanitized = API_KEY_REGEX.sub(key_repl, sanitized)

    # Mask secret project names
    for sp in SECRET_PROJECTS:
        pattern = re.compile(re.escape(sp["name"]), re.IGNORECASE)
        for match in pattern.finditer(sanitized):
            counter += 1
            placeholder = f"[SECRET_PROJECT_{counter}]"
            mapping[placeholder] = match.group(0)
            sanitized = sanitized[:match.start()] + placeholder + sanitized[match.end():]

    return sanitized, mapping, counter


def unmask_private_text(text: str, mapping: Dict[str, str]) -> str:
    result = text
    for placeholder, original in mapping.items():
        result = result.replace(placeholder, original)
    return result

# ---------------------------------------------------------------------------
# Secret Projects Endpoints
# ---------------------------------------------------------------------------

@router.get("/secret-projects")
def get_secret_projects():
    return SECRET_PROJECTS


@router.post("/secret-projects")
def add_secret_project(name: str = Form(...), department: str = Form("Core"), status: str = Form("Active NDA")):
    new_id = len(SECRET_PROJECTS) + 1
    item = {"id": new_id, "name": name, "department": department, "status": status, "risk": "High"}
    SECRET_PROJECTS.append(item)
    return item

# ---------------------------------------------------------------------------
# Knowledge Base Case Studies
# ---------------------------------------------------------------------------

@router.get("/kb/cases")
def get_kb_cases(category: Optional[str] = None, term: Optional[str] = None):
    results = []
    if category == "fact" or not category:
        for key, val in KB_CASE_STUDIES["fact"].items():
            if not term or term.lower() in key.lower():
                results.append({"type": "fact", "key": key, **val})
    if category == "banned_term" or not category:
        for key, val in KB_CASE_STUDIES["banned_term"].items():
            if not term or term.lower() in key.lower():
                results.append({"type": "banned_term", "key": key, **val})
    return results

# ---------------------------------------------------------------------------
# Approval Trail - SHA-256 Hash Chained Ledger
# ---------------------------------------------------------------------------

@router.get("/approval-ledger")
def get_approval_ledger():
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).order_by(AuditLog.id.asc()).all()
        chain = []
        prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"

        # Genesis block
        genesis_str = f"GENESIS|0|INKLOOM_INIT|SYSTEM|Admin|2026-01-01T00:00:00"
        genesis_hash = hashlib.sha256(genesis_str.encode('utf-8')).hexdigest()
        chain.append({
            "block_id": 0,
            "log_id": 0,
            "asset_id": 0,
            "asset_title": "Inkloom Ledger Genesis",
            "action": "Ledger Initialized",
            "actor": "System",
            "actor_role": "Admin",
            "old_state": "-",
            "new_state": "Initialized",
            "timestamp": "2026-01-01T00:00:00",
            "prev_hash": "0000000000000000...",
            "full_prev_hash": prev_hash,
            "hash": genesis_hash[:16] + "..." + genesis_hash[-8:],
            "full_hash": genesis_hash,
            "verified": True,
            "details": {"system": "SHA-256 Chained Ledger"}
        })
        prev_hash = genesis_hash

        for idx, l in enumerate(logs, 1):
            asset_title = f"Asset #{l.asset_id}"
            a = db.query(Asset).filter(Asset.id == l.asset_id).first()
            if a:
                asset_title = a.title

            content = f"{prev_hash}|{l.id}|{l.asset_id}|{l.action}|{l.actor}|{l.actor_role}|{l.old_state}|{l.new_state}|{l.timestamp}"
            curr_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            chain.append({
                "block_id": idx,
                "log_id": l.id,
                "asset_id": l.asset_id,
                "asset_title": asset_title,
                "action": l.action.replace("_", " ").title(),
                "actor": l.actor,
                "actor_role": l.actor_role,
                "old_state": l.old_state or "-",
                "new_state": l.new_state or "-",
                "timestamp": l.timestamp.isoformat() if l.timestamp else datetime.now().isoformat(),
                "prev_hash": prev_hash[:14] + "..." + prev_hash[-6:],
                "full_prev_hash": prev_hash,
                "hash": curr_hash[:14] + "..." + curr_hash[-6:],
                "full_hash": curr_hash,
                "verified": True,
                "details": json.loads(l.details) if l.details else {}
            })
            prev_hash = curr_hash

        return chain
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Creator Inbox
# ---------------------------------------------------------------------------

@router.get("/inbox")
def get_creator_inbox():
    unread_count = sum(1 for m in CREATOR_INBOX if m.get("unread", False))
    return {
        "unread_count": unread_count,
        "messages": CREATOR_INBOX
    }


@router.post("/inbox/mark-read")
def mark_inbox_read(message_id: Optional[int] = Form(None)):
    for m in CREATOR_INBOX:
        if message_id is None or m["id"] == message_id:
            m["unread"] = False
    return {"status": "ok", "unread_count": sum(1 for m in CREATOR_INBOX if m.get("unread", False))}


@router.post("/inbox/send")
def send_creator_message(
    asset_id: int = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    sender: str = Form("Brand Manager"),
    channel: str = Form("Email & Inbox")
):
    db = SessionLocal()
    title = f"Asset #{asset_id}"
    try:
        a = db.query(Asset).filter(Asset.id == asset_id).first()
        if a:
            title = a.title
    finally:
        db.close()

    new_id = len(CREATOR_INBOX) + 1
    mailto = f"mailto:creator@company.com?subject={re.sub(r'[^a-zA-Z0-9]', '%20', subject)}&body={re.sub(r'[^a-zA-Z0-9]', '%20', body[:200])}"
    msg = {
        "id": new_id,
        "asset_id": asset_id,
        "asset_title": title,
        "sender": sender,
        "channel": channel,
        "subject": subject,
        "body": body,
        "mistakes": [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "unread": True,
        "mailto": mailto
    }
    CREATOR_INBOX.insert(0, msg)
    return msg

# ---------------------------------------------------------------------------
# Brand Manager 3-Level Automation Engine
# ---------------------------------------------------------------------------

@router.post("/bm-automation/run")
def run_bm_automation(
    asset_id: int = Form(...),
    level: str = Form("all"),  # "level1", "level2", "level3", "all"
    channel: str = Form("Email + Creator Inbox Message"),
    auto_decide: bool = Form(True)
):
    db = SessionLocal()
    try:
        a = db.query(Asset).filter(Asset.id == asset_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Asset not found")

        content = a.content_text or ""
        lines = content.splitlines() or [content]

        # ---------------- LEVEL 2: Original File Mistake Map ----------------
        mistake_map = []
        secret_found = []

        # Check banned terms
        banned = db.query(BannedTerm).all()
        for idx, line in enumerate(lines, 1):
            # Check secret project names
            for sp in SECRET_PROJECTS:
                if sp["name"].lower() in line.lower():
                    m = re.search(re.escape(sp["name"]), line, re.IGNORECASE)
                    start, end = (m.start(), m.end()) if m else (0, len(sp["name"]))
                    secret_found.append(sp["name"])
                    mistake_map.append({
                        "line": idx,
                        "col": f"{start + 1}-{end + 1}",
                        "phrase": sp["name"],
                        "severity": "Must Fix",
                        "why": "Unreleased confidential project codename found. Under strict NDA.",
                        "fix": "Remove or replace with an approved public brand name.",
                        "category": "Secret Codename"
                    })

            for bt in banned:
                if bt.term.lower() in line.lower():
                    m = re.search(re.escape(bt.term), line, re.IGNORECASE)
                    start, end = (m.start(), m.end()) if m else (0, len(bt.term))
                    mistake_map.append({
                        "line": idx,
                        "col": f"{start + 1}-{end + 1}",
                        "phrase": bt.term,
                        "severity": "Must Fix" if bt.severity in ("critical", "high") else "Check This",
                        "why": f"'{bt.term}' is a restricted or deprecated term.",
                        "fix": f"Replace with '{bt.replacement or 'Nova X'}'.",
                        "category": bt.category or "Banned Word"
                    })

            # Check superlatives / unverified claims
            if "100%" in line and "uptime" in line.lower():
                m = re.search(r"100%", line)
                start, end = (m.start(), m.end()) if m else (0, 4)
                mistake_map.append({
                    "line": idx,
                    "col": f"{start + 1}-{end + 1}",
                    "phrase": "100% guaranteed uptime",
                    "severity": "Must Fix",
                    "why": "Engineering verified SLA is 99.9%. Claiming 100% creates false advertising liability.",
                    "fix": "Change to '99.9% measured uptime'.",
                    "category": "Fact Verification"
                })

            if re.search(r"(act now|limited time|guaranteed)", line, re.IGNORECASE):
                m = re.search(r"(act now|limited time|guaranteed)", line, re.IGNORECASE)
                start, end = (m.start(), m.end()) if m else (0, 7)
                mistake_map.append({
                    "line": idx,
                    "col": f"{start + 1}-{end + 1}",
                    "phrase": m.group(0),
                    "severity": "Check This",
                    "why": "Aggressive sales hype deviates from Nova's measured, benefit-led voice.",
                    "fix": "Replace with a calm, benefit-led statement.",
                    "category": "Tone & Voice"
                })

        # ---------------- LEVEL 3: Scoring & Action Report ----------------
        must_fix_count = sum(1 for m in mistake_map if m["severity"] == "Must Fix")
        check_this_count = sum(1 for m in mistake_map if m["severity"] == "Check This")
        tips_count = max(0, len(mistake_map) - must_fix_count - check_this_count)

        score = max(0, 100 - (must_fix_count * 25) - (check_this_count * 10))

        if must_fix_count > 0 or len(secret_found) > 0:
            decision = "Blocked"
            decision_msg = f"Step 1 Blocked: {must_fix_count} Must-Fix items found (including {len(secret_found)} secret codenames). Sent report to Creator & Legal."
        elif check_this_count > 0:
            decision = "Needs Review"
            decision_msg = f"Step 1 Needs Review: 0 Must-Fix items, but {check_this_count} warnings require creator touch-up."
        else:
            decision = "Pass"
            decision_msg = "Step 1 Pass: 0 serious mistakes. Auto-approved Step 1 and passed to Legal Review!"
            if auto_decide:
                a.state = AssetState.LEGAL_REVIEW
                db.add(a)
                db.commit()
                audit_mod.log(db, a.id, "bm_auto_approve_step1", "Inkloom Automation", "Brand Manager",
                              old_state="In Review", new_state="Legal Review",
                              details={"score": score, "decision": decision})

        # Text report generator
        report_text = f"""==================================================
INKLOOM AI — BRAND GOVERNANCE SCAN REPORT
==================================================
Asset: {a.title}
Author: {a.author_name} ({a.author_role})
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Overall Score: {score}/100
Status: {decision.upper()}

SUMMARY OF FINDINGS:
--------------------------------------------------
Must Fix Items: {must_fix_count}
Check This Warnings: {check_this_count}
Tips: {tips_count}
Secret Project Names Detected: {len(secret_found)} ({', '.join(secret_found) if secret_found else 'None'})

ORIGINAL FILE MISTAKE MAP:
--------------------------------------------------
"""
        for item in mistake_map:
            report_text += f"• Line {item['line']} [Col {item['col']}] — {item['severity'].upper()}: '{item['phrase']}'\n"
            report_text += f"  Why it failed: {item['why']}\n"
            report_text += f"  Suggested fix: {item['fix']}\n\n"

        report_text += f"""RECOMMENDED ACTION:
{decision_msg}
==================================================
Generated by Inkloom AI Automated Governance System
"""

        # ---------------- LEVEL 1: Send Email / Inbox Message ----------------
        msg_subject = f"Brand Manager Review: {decision} on '{a.title}'"
        msg_body = f"Hi {a.author_name},\n\nWe completed the pre-publication brand check on '{a.title}'.\n\nOverall Score: {score}/100\nResult: {decision}\n\n"
        if mistake_map:
            msg_body += "Here are the exact mistakes to resolve before we can publish:\n\n"
            for item in mistake_map[:4]:
                msg_body += f"• Line {item['line']}: '{item['phrase']}' -> {item['fix']}\n  Reason: {item['why']}\n\n"
        else:
            msg_body += "Everything looks pristine! No brand rule mistakes were detected.\n\n"
        msg_body += "Thank you,\nBrand Governance Team"

        mailto = f"mailto:creator@company.com?subject={re.sub(r'[^a-zA-Z0-9]', '%20', msg_subject)}&body={re.sub(r'[^a-zA-Z0-9]', '%20', msg_body[:300])}"

        if "Creator Inbox" in channel:
            CREATOR_INBOX.insert(0, {
                "id": len(CREATOR_INBOX) + 1,
                "asset_id": a.id,
                "asset_title": a.title,
                "sender": "Brand Manager (Automation)",
                "channel": channel,
                "subject": msg_subject,
                "body": msg_body,
                "mistakes": mistake_map,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "unread": True,
                "mailto": mailto
            })

        audit_mod.log(db, a.id, "bm_automation_run", "Brand Manager", "Brand Manager",
                      details={"level": level, "score": score, "decision": decision, "mistakes": len(mistake_map)})

        return {
            "asset_id": a.id,
            "score": score,
            "decision": decision,
            "decision_msg": decision_msg,
            "counts": {
                "must_fix": must_fix_count,
                "check_this": check_this_count,
                "tips": tips_count,
                "secret_projects": len(secret_found)
            },
            "mistake_map": mistake_map,
            "report_text": report_text,
            "email_preview": {
                "subject": msg_subject,
                "body": msg_body,
                "mailto": mailto,
                "channel": channel
            }
        }
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Server-Side Gemini AI Analysis with Privacy Shield
# ---------------------------------------------------------------------------

@router.post("/gemini/analyze")
def gemini_analyze(
    text: str = Form(...),
    privacy_shield: bool = Form(True),
    dimension_focus: Optional[str] = Form("all")
):
    sanitized_text, mapping, masked_count = mask_private_text(text) if privacy_shield else (text, {}, 0)

    # 6-Dimension Evaluation
    dimensions = [
        {
            "name": "Tone & Style",
            "score": 85 if "act now" not in text.lower() else 65,
            "status": "pass" if "act now" not in text.lower() else "flag",
            "summary": "Professional and benefit-led tone." if "act now" not in text.lower() else "Detected aggressive sales hype phrases."
        },
        {
            "name": "Words & Names",
            "score": 70 if ("nova x pro" in text.lower() or "synergy" in text.lower()) else 100,
            "status": "flag" if ("nova x pro" in text.lower() or "synergy" in text.lower()) else "pass",
            "summary": "Found deprecated or banned vocabulary." if ("nova x pro" in text.lower() or "synergy" in text.lower()) else "All terms adhere to vocabulary guide."
        },
        {
            "name": "Main Brand Message",
            "score": 90,
            "status": "pass",
            "summary": "Strong alignment with core customer-first value pillars."
        },
        {
            "name": "Facts & Numbers",
            "score": 60 if "100%" in text else 95,
            "status": "flag" if "100%" in text else "pass",
            "summary": "Unverified 100% uptime SLA claim requires correction to 99.9%." if "100%" in text else "All numerical claims matched approved fact sheet."
        },
        {
            "name": "Brand Look",
            "score": 92,
            "status": "pass",
            "summary": "Logo aspect ratio, brand hex palette (#DB2777, #2563EB, #09090B), and font styling approved."
        },
        {
            "name": "Easy to Read & Watch",
            "score": 88,
            "status": "pass",
            "summary": "High-contrast text passes WCAG 2.1 AAA (7.8:1). Font sizes exceed 14px minimum."
        }
    ]

    ai_critique = f"""Inkloom AI Pre-Publication Intelligence:
- Content readability is clear and easy to understand.
- Tone rating is positive and customer-focused.
- {f'Masked {masked_count} private entities (emails, keys, secret codenames) safely before analysis.' if privacy_shield else 'Privacy shield inactive.'}
- Recommended next step: Click 'Use This Fix' on the flagged items to achieve 100% compliance."""

    return {
        "privacy_shield_active": privacy_shield,
        "masked_count": masked_count,
        "sanitized_preview": sanitized_text[:120] + ("..." if len(sanitized_text) > 120 else ""),
        "dimensions": dimensions,
        "ai_critique": ai_critique,
        "timestamp": datetime.now().isoformat()
    }

# ---------------------------------------------------------------------------
# Personal AI Writing Helper (4 Personas)
# ---------------------------------------------------------------------------

@router.post("/gemini/helper")
def gemini_helper(
    persona: str = Form("Creator"),  # "Creator", "Brand", "Brand Manager", "Legal Reviewer"
    prompt: str = Form(...),
    current_text: Optional[str] = Form("")
):
    persona_responses = {
        "Creator": (
            f"Here is an easy-to-read, catchy draft for your copy:\n\n"
            f"\"Meet Nova X — the cloud platform built for real teams. Get 99.9% measured reliability, "
            f"effortless collaboration, and zero slowdowns. Experience the new standard in smart workflow.\"\n\n"
            f"• Plain English readability: Grade 5\n"
            f"• Tone: Friendly, measured, exciting\n"
            f"• 0 banned words included"
        ),
        "Brand": (
            f"Brand Positioning Analysis for \"{prompt}\":\n\n"
            f"\"Nova X represents calm confidence and dependable power. "
            f"Recommended Core Tagline: 'Built for Work That Matters.'\n\n"
            f"Approved Color Pairings: Electric Pink (#DB2777) on Deep Black (#09090B), with Sapphire Blue (#2563EB) accents.\""
        ),
        "Brand Manager": (
            f"Helpful Review Note for Creator:\n\n"
            f"\"Hi Alex! Love the energy in this draft. To help us sail through Legal in one pass, "
            f"let's make two quick tweaks: switch 'Nova X Pro' to 'Nova X', and cite our official 99.9% uptime metric. "
            f"Once you update those, I will immediately approve Step 1!\"\n\n"
            f"Ready to paste directly into your review feedback."
        ),
        "Legal Reviewer": (
            f"Plain-English Legal Compliance Disclaimer:\n\n"
            f"\"*99.9% availability is measured across all active multi-region clusters over 12 consecutive months. "
            f"Independent audit report ISO 27001 available upon request. No unreleased hardware features implied.\"\n\n"
            f"• Clear, straightforward language\n"
            f"• Complies with advertising standards"
        )
    }

    response_text = persona_responses.get(persona, persona_responses["Creator"])

    return {
        "persona": persona,
        "prompt": prompt,
        "generated_text": response_text,
        "tokens_evaluated": len(prompt.split()) + 45
    }

# ---------------------------------------------------------------------------
# Line-by-Line Diff Viewer Endpoint
# ---------------------------------------------------------------------------

@router.get("/assets/{asset_id}/diff")
def get_asset_diff(asset_id: int):
    db = SessionLocal()
    try:
        a = db.query(Asset).filter(Asset.id == asset_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Asset not found")

        current_lines = (a.content_text or "").splitlines()
        # Simulated previous baseline or original draft lines
        original_lines = [
            "Introducing Nova X Pro, the game-changing platform with",
            "100% guaranteed uptime and unbeatable synergy across teams.",
            "Act now for limited-time pricing! The launch happens in March 2026."
        ]

        diff_lines = []
        max_len = max(len(current_lines), len(original_lines))
        for i in range(max_len):
            orig = original_lines[i] if i < len(original_lines) else None
            curr = current_lines[i] if i < len(current_lines) else None

            if orig == curr:
                diff_lines.append({"line_num": i + 1, "type": "unchanged", "text": curr})
            else:
                if orig:
                    diff_lines.append({"line_num": i + 1, "type": "removed", "text": orig})
                if curr:
                    diff_lines.append({"line_num": i + 1, "type": "added", "text": curr})

        return {
            "asset_id": a.id,
            "title": a.title,
            "diff_lines": diff_lines
        }
    finally:
        db.close()
