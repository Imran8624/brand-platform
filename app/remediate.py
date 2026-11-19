"""Intent-preserving remediation: rewrite / fix suggestions for each flag."""

import re
from typing import Dict


def suggest_remediation(flag: dict, full_text: str = "") -> dict:
    """
    Produce a non-destructive rewrite suggestion for a flag.
    Returns {suggested_fix, approach, preserves_intent: bool}.
    """
    category = (flag.get("category") or "").lower()
    element = flag.get("element") or ""
    existing = flag.get("suggested_fix") or ""

    if category in ("aggressive_hype",):
        return {
            "suggested_fix": f"Swap the hype phrase '{element}' for a measured, benefit-led claim you can substantiate.",
            "approach": "tone_softening",
            "preserves_intent": True,
        }
    if category in ("deprecated_name", "terminology", "capitalization"):
        return {
            "suggested_fix": existing or f"Replace '{element}' with the approved terminology.",
            "approach": "terminology_swap",
            "preserves_intent": True,
        }
    if category == "fact_claim":
        return {
            "suggested_fix": existing or f"Replace the unsubstantiated claim '{element}' with a figure from the approved fact sheet, or remove it.",
            "approach": "fact_substitution",
            "preserves_intent": True,
        }
    if category in ("off_palette", "logo_stretch"):
        return {
            "suggested_fix": existing or f"Correct the visual '{element}' per the brand asset vault (do not stretch; use approved hex).",
            "approach": "visual_correction",
            "preserves_intent": True,
        }
    if category in ("contrast", "alt_text", "font_size"):
        return {
            "suggested_fix": existing or f"Fix the accessibility issue '{element}' per WCAG guidance.",
            "approach": "accessibility_fix",
            "preserves_intent": True,
        }
    if category == "messaging":
        return {
            "suggested_fix": existing or "Reintroduce the missing positioning pillar while keeping your narrative structure.",
            "approach": "pillar_reintroduction",
            "preserves_intent": True,
        }
    return {
        "suggested_fix": existing or "Review and revise per the cited guideline.",
        "approach": "manual_review",
        "preserves_intent": True,
    }
