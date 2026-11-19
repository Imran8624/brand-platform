"""Six-dimension brand governance scanner (deterministic, offline)."""

import json
import math
import os
import re
from datetime import datetime
from collections import Counter
from typing import Any, Dict, List, Tuple

from PIL import Image

from .database import SessionLocal
from .models import Asset, BannedTerm, BrandGuideline, FactSheetRow, Flag, Scan, ScanStatus, VoiceRule

DIMENSIONS = [
    "Tone & Voice Drift",
    "Terminology & Naming",
    "Messaging Alignment",
    "Fact & Claim Verification",
    "Visual Brand Consistency",
    "Accessibility Compliance",
]

SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_active_guideline(db):
    return db.query(BrandGuideline).filter(BrandGuideline.is_active == True).first()  # noqa: E712


def _luminance(r: int, g: int, b: int) -> float:
    def channel(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    l1, l2 = _luminance(*c1), _luminance(*c2)
    light, dark = max(l1, l2), min(l1, l2)
    return (light + 0.05) / (dark + 0.05)


def _extract_claims(text: str) -> List[dict]:
    """Pull out candidate factual claims: percentages, superlatives, numbers+units."""
    claims = []
    # percentages
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*%", text):
        claims.append({"type": "percentage", "value": m.group(0), "span": m.group(0)})
    # superlatives
    for m in re.finditer(r"(fastest|slowest|best|worst|largest|smallest|cheapest|most|number one|#1|first)", text, re.I):
        claims.append({"type": "superlative", "value": m.group(0), "span": m.group(0)})
    # big round numbers / certifications
    for m in re.finditer(r"(certified|ISO [0-9]+|guaranteed|100 percent|100%)", text, re.I):
        claims.append({"type": "certification", "value": m.group(0), "span": m.group(0)})
    return claims


# ---------------------------------------------------------------------------
# Dimension 1: Tone & Voice Drift
# ---------------------------------------------------------------------------

def _scan_tone(db, text: str, guideline: BrandGuideline) -> dict:
    flags: List[dict] = []
    hits = 0
    for vr in (guideline.voice_rules if guideline else []):
        pat = vr.pattern.lower()
        for m in re.finditer(re.escape(pat), text.lower()):
            hits += 1
            flags.append({
                "element": text[max(0, m.start()-20):m.end()+20],
                "rationale": (vr.description or f"Phrase '{vr.pattern}' deviates from brand voice."),
                "source_citation": f"Voice rule (v{guideline.version if guideline else '?'}): {vr.pattern}",
                "suggested_fix": f"Rephrase '{m.group(0)}' using the approved brand tone.",
                "severity": vr.severity,
                "category": vr.category,
            })
    # Generic aggressive-hype heuristic
    hype = re.findall(r"(act now|limited time|buy now|amazing|incredible|revolutionary|guaranteed|no risk)", text, re.I)
    for h in hype:
        hits += 1
        flags.append({
            "element": h,
            "rationale": "Aggressive sales hype detected; off-brand tone.",
            "source_citation": "Brand voice guideline: avoid aggressive sales hype.",
            "suggested_fix": f"Replace '{h}' with a measured, benefit-led statement.",
            "severity": "medium",
            "category": "aggressive_hype",
        })
    score = max(0, 100 - hits * 10)
    return {
        "dimension": "Tone & Voice Drift",
        "status": ScanStatus.FLAG if flags else ScanStatus.PASS,
        "score": score,
        "detection_method": "deterministic",
        "flags": flags,
    }


# ---------------------------------------------------------------------------
# Dimension 2: Terminology & Naming
# ---------------------------------------------------------------------------

def _scan_terminology(db, text: str, guideline: BrandGuideline) -> dict:
    flags: List[dict] = []
    hits = 0
    terms = guideline.banned_terms if guideline else []
    for bt in terms:
        pattern = re.escape(bt.term)
        for m in re.finditer(pattern, text, re.IGNORECASE):
            hits += 1
            replacement = bt.replacement or "an approved alternative"
            flags.append({
                "element": m.group(0),
                "rationale": f"'{bt.term}' is a {bt.category or 'restricted'} term and should not be used.",
                "source_citation": f"Banned term (v{guideline.version if guideline else '?'}): {bt.term}",
                "suggested_fix": f"Replace '{m.group(0)}' with '{replacement}'.",
                "severity": bt.severity,
                "category": bt.category or "terminology",
            })
    # ALL-CAPS shouting heuristic (tokens > 4 chars fully uppercase)
    for m in re.finditer(r"\b[A-Z]{5,}\b", text):
        hits += 1
        flags.append({
            "element": m.group(0),
            "rationale": "All-caps shouting detected; inconsistent with brand typography/tone.",
            "source_citation": "Brand voice guideline: avoid all-caps emphasis.",
            "suggested_fix": f"Use sentence case: '{m.group(0)}'.",
            "severity": "low",
            "category": "capitalization",
        })
    score = max(0, 100 - hits * 10)
    return {
        "dimension": "Terminology & Naming",
        "status": ScanStatus.FLAG if flags else ScanStatus.PASS,
        "score": score,
        "detection_method": "deterministic",
        "flags": flags,
    }



# ---------------------------------------------------------------------------
# Dimension 3: Messaging Alignment
# ---------------------------------------------------------------------------

def _scan_messaging(db, text: str, guideline: BrandGuideline) -> dict:
    """Checks whether approved value propositions / positioning pillars appear."""
    flags: List[dict] = []
    hits = 0
    low = text.lower()
    expected = []
    if guideline:
        for vr in guideline.voice_rules:
            expected.append(vr.pattern)
    if not expected:
        expected = ["quality", "reliable", "trusted", "innovation", "customer"]
    missing = [e for e in expected if e.lower() not in low]
    if missing:
        hits += len(missing)
        flags.append({
            "element": ", ".join(missing),
            "rationale": "Key positioning pillars / approved value propositions missing from draft.",
            "source_citation": "Messaging alignment: approved brand pillars.",
            "suggested_fix": f"Weave in: {', '.join(missing)}.",
            "severity": "medium",
            "category": "messaging",
        })
    score = max(0, 100 - hits * 10)
    return {
        "dimension": "Messaging Alignment",
        "status": ScanStatus.FLAG if flags else ScanStatus.PASS,
        "score": score,
        "detection_method": "deterministic",
        "flags": flags,
    }


# ---------------------------------------------------------------------------
# Dimension 4: Fact & Claim Verification
# ---------------------------------------------------------------------------

def _scan_facts(db, text: str, guideline: BrandGuideline) -> dict:
    flags: List[dict] = []
    hits = 0
    facts = guideline.fact_rows if guideline else []
    claims = _extract_claims(text)

    fact_lookup: Dict[str, Dict[str, str]] = {}
    for fr in facts:
        fact_lookup.setdefault(fr.entity.lower(), {})[fr.claim.lower()] = fr.value

    for cl in claims:
        span = cl["span"]
        unverified = True
        for entity_map in fact_lookup.values():
            for claim_name, val in entity_map.items():
                if cl["value"].replace("%", "") == val.replace("%", ""):
                    unverified = False
                    break
            if not unverified:
                break
        if unverified and cl["type"] in ("percentage", "superlative", "certification"):
            hits += 1
            flags.append({
                "element": span,
                "rationale": f"Unsubstantiated {cl['type']} claim '{span}' not found in approved fact sheet.",
                "source_citation": "Fact sheet: cross-reference approved values.",
                "suggested_fix": f"Replace '{span}' with a verified figure from the fact sheet or remove it.",
                "severity": "high",
                "category": "fact_claim",
            })
    score = max(0, 100 - hits * 15)
    return {
        "dimension": "Fact & Claim Verification",
        "status": ScanStatus.FLAG if flags else ScanStatus.PASS,
        "score": score,
        "detection_method": "deterministic",
        "flags": flags,
    }


# ---------------------------------------------------------------------------
# Dimension 5: Visual Brand Consistency
# ---------------------------------------------------------------------------

def _scan_visual(db, asset: Asset) -> dict:
    flags: List[dict] = []
    hits = 0
    import os
    guideline = _get_active_guideline(db)
    palette: List[Tuple[int, int, int]] = []
    if guideline:
        for m in re.finditer(r"#([0-9A-Fa-f]{6})", guideline.content_text):
            h = m.group(1)
            palette.append(tuple(int(h[i:i+2], 16) for i in (0, 2, 4)))

    file_path = asset.file_path
    if file_path and os.path.exists(file_path) and asset.file_type and asset.file_type.startswith("image"):
        try:
            with Image.open(file_path) as img:
                img = img.convert("RGB")
                w, h = img.size
                ar = w / h if h else 0
                if ar > 2.5 or ar < 0.4:
                    hits += 1
                    flags.append({
                        "element": f"image {w}x{h}",
                        "rationale": f"Image aspect ratio ({ar:.2f}) suggests a stretched/distorted logo.",
                        "source_citation": "Visual brand guideline: logo proportions.",
                        "suggested_fix": "Re-insert the logo at its original aspect ratio; do not stretch.",
                        "severity": "high",
                        "category": "logo_stretch",
                    })
                small = img.resize((40, 40))
                colors = Counter(small.getdata())
                top_colors = [c for c, _ in colors.most_common(6)]
                if palette:
                    for c in top_colors:
                        if all(math.dist(c, p) > 60 for p in palette):
                            hits += 1
                            flags.append({
                                "element": f"color rgb{c}",
                                "rationale": f"Color {c} is off-palette vs approved hex set.",
                                "source_citation": f"Visual brand guideline: approved palette v{guideline.version}",
                                "suggested_fix": "Replace with an approved hex color from the brand palette.",
                                "severity": "medium",
                                "category": "off_palette",
                            })
                            break
        except Exception as exc:  # noqa: BLE001
            flags.append({
                "element": "image",
                "rationale": f"Could not analyze image: {exc}",
                "source_citation": "Visual brand guideline.",
                "suggested_fix": "Upload a valid image file.",
                "severity": "low",
                "category": "image_error",
            })
    score = max(0, 100 - hits * 20)
    return {
        "dimension": "Visual Brand Consistency",
        "status": ScanStatus.FLAG if flags else ScanStatus.PASS,
        "score": score,
        "detection_method": "deterministic",
        "flags": flags,
    }


# ---------------------------------------------------------------------------
# Dimension 6: Accessibility Compliance
# ---------------------------------------------------------------------------

def _scan_accessibility(db, text: str, asset: Asset) -> dict:
    flags: List[dict] = []
    hits = 0
    guideline = _get_active_guideline(db)
    palette: List[Tuple[int, int, int]] = []
    if guideline:
        for m in re.finditer(r"#([0-9A-Fa-f]{6})", guideline.content_text):
            h = m.group(1)
            palette.append(tuple(int(h[i:i+2], 16) for i in (0, 2, 4)))

    for m in re.finditer(r"(?:fg|color|foreground)\s*:?\s*#([0-9A-Fa-f]{6}).{0,40}?(?:bg|background)\s*:?\s*#([0-9A-Fa-f]{6})", text, re.I | re.S):
        c1 = tuple(int(m.group(1)[i:i+2], 16) for i in (0, 2, 4))
        c2 = tuple(int(m.group(2)[i:i+2], 16) for i in (0, 2, 4))
        cr = contrast_ratio(c1, c2)
        if cr < 4.5:
            hits += 1
            flags.append({
                "element": f"contrast {cr:.2f}:1",
                "rationale": f"Text-to-background contrast {cr:.2f}:1 is below WCAG AA (4.5:1).",
                "source_citation": "Accessibility guideline: WCAG 2.1 AA contrast.",
                "suggested_fix": "Darken the text or lighten the background to reach at least 4.5:1 contrast.",
                "severity": "high",
                "category": "contrast",
            })

    if asset.file_type and asset.file_type.startswith("image"):
        if not re.search(r"alt\s*=\s*[\"'][^\"']+[\"']", text, re.I):
            hits += 1
            flags.append({
                "element": "image",
                "rationale": "Image missing alt-text (screen-reader inaccessible).",
                "source_citation": "Accessibility guideline: WCAG alt-text requirement.",
                "suggested_fix": "Add descriptive alt-text to the image.",
                "severity": "high",
                "category": "alt_text",
            })
    for m in re.finditer(r"(\d+)\s*px", text):
        if int(m.group(1)) < 12:
            hits += 1
            flags.append({
                "element": f"{m.group(1)}px",
                "rationale": "Font size below minimum readable size (12px).",
                "source_citation": "Accessibility guideline: minimum font size.",
                "suggested_fix": "Increase to at least 12px.",
                "severity": "medium",
                "category": "font_size",
            })
            break
    score = max(0, 100 - hits * 15)
    return {
        "dimension": "Accessibility Compliance",
        "status": ScanStatus.FLAG if flags else ScanStatus.PASS,
        "score": score,
        "detection_method": "deterministic",
        "flags": flags,
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

DISPATCH = {
    "Tone & Voice Drift": _scan_tone,
    "Terminology & Naming": _scan_terminology,
    "Messaging Alignment": _scan_messaging,
    "Fact & Claim Verification": _scan_facts,
    "Visual Brand Consistency": _scan_visual,
    "Accessibility Compliance": _scan_accessibility,
}


def run_scan_all(db, asset: Asset) -> List[dict]:
    """Run all six dimensions against an asset, persisting Scan + Flag rows."""
    guideline = _get_active_guideline(db)
    text = asset.content_text or ""

    # clear previous scans/flags for this asset (re-scan on edit)
    db.query(Flag).filter(Flag.asset_id == asset.id).delete(synchronize_session=False)
    db.query(Scan).filter(Scan.asset_id == asset.id).delete(synchronize_session=False)
    db.commit()

    results = []
    for dim in DIMENSIONS:
        fn = DISPATCH[dim]
        if dim == "Visual Brand Consistency":
            res = fn(db, asset)
        elif dim == "Accessibility Compliance":
            res = fn(db, text, asset)
        else:
            res = fn(db, text, guideline)

        scan = Scan(
            asset_id=asset.id,
            dimension=res["dimension"],
            status=res["status"],
            score=res["score"],
            details=json.dumps({"flags": res["flags"], "method": res["detection_method"]}),
            detection_method=res["detection_method"],
        )
        db.add(scan)
        db.flush()
        for fl in res["flags"]:
            db.add(Flag(
                scan_id=scan.id,
                asset_id=asset.id,
                dimension=dim,
                severity=fl.get("severity", "medium"),
                element=fl.get("element"),
                rationale=fl.get("rationale"),
                source_citation=fl.get("source_citation"),
                suggested_fix=fl.get("suggested_fix"),
                original_text=fl.get("element"),
                status="open",
            ))
        results.append({
            "dimension": dim,
            "status": res["status"],
            "score": res["score"],
            "detection_method": res["detection_method"],
            "flag_count": len(res["flags"]),
        })
    db.commit()
    asset.updated_at = datetime.now()
    db.add(asset)
    db.commit()
    return results
