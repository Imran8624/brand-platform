"""Seed the database with a sample brand guideline + a demo asset with violations."""

from datetime import datetime

from .database import SessionLocal, engine
from .models import (
    Asset,
    AssetState,
    Base,
    BannedTerm,
    BrandGuideline,
    FactSheetRow,
    Flag,
    FlagDecision,
    Scan,
    ScanStatus,
    VoiceRule,
)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Avoid double-seeding
        if db.query(BrandGuideline).count() > 0:
            print("Already seeded. Skipping.")
            return

        # Deactivate any prior guidelines
        db.query(BrandGuideline).filter(BrandGuideline.is_active == True).update(  # noqa: E712
            {BrandGuideline.is_active: False}
        )

        gl = BrandGuideline(
            version="2026.1",
            title="Nova Brand Guidelines 2026",
            content_text=(
                "Nova Brand Guidelines 2026\n"
                "Tone: professional, measured, benefit-led. Avoid aggressive sales hype.\n"
                "Voice: avoid jargon and passive voice.\n"
                "Palette: #1A3E5C #2E86AB #F4A261 #E76F51\n"
                "Nova X | uptime | 99.9%\n"
                "Nova X | launch date | March 2026\n"
                "Nova X | certification | ISO 27001\n"
                "DO NOT USE: Nova X Pro -> Nova X\n"
                "DO NOT USE: synergy -> collaboration\n"
                "DO NOT USE: game-changing -> innovative\n"
            ),
            source_file="nova_brand_guidelines_2026.txt",
            is_active=True,
        )
        db.add(gl)
        db.flush()

        fact_rows = [
            FactSheetRow(guideline_id=gl.id, entity="Nova X", claim="uptime", value="99.9%", source_quote="Nova X | uptime | 99.9%", category="performance"),
            FactSheetRow(guideline_id=gl.id, entity="Nova X", claim="launch date", value="March 2026", source_quote="Nova X | launch date | March 2026", category="timing"),
            FactSheetRow(guideline_id=gl.id, entity="Nova X", claim="certification", value="ISO 27001", source_quote="Nova X | certification | ISO 27001", category="compliance"),
        ]
        for fr in fact_rows:
            db.add(fr)

        banned = [
            BannedTerm(guideline_id=gl.id, term="Nova X Pro", replacement="Nova X", category="deprecated_name", severity="critical"),
            BannedTerm(guideline_id=gl.id, term="synergy", replacement="collaboration", category="banned_word", severity="medium"),
            BannedTerm(guideline_id=gl.id, term="game-changing", replacement="innovative", category="banned_word", severity="high"),
        ]
        for bt in banned:
            db.add(bt)

        voices = [
            VoiceRule(guideline_id=gl.id, pattern="aggressive sales hype", category="aggressive_hype", description="Avoid hard-sell hype phrases.", severity="medium"),
            VoiceRule(guideline_id=gl.id, pattern="jargon", category="jargon", description="Avoid off-brand jargon.", severity="medium"),
            VoiceRule(guideline_id=gl.id, pattern="passive voice", category="passive_voice", description="Prefer active voice.", severity="low"),
        ]
        for vr in voices:
            db.add(vr)

        db.commit()
        db.refresh(gl)

        # Demo asset with intentional violations
        demo_text = (
            "Introducing Nova X Pro, the game-changing platform with "
            "100% guaranteed uptime and unbeatable synergy across teams. "
            "Act now for limited-time pricing! The launch happens in March 2026. "
            "fg:#FFFFFF bg:#000000 10px\n"
            '<img src="logo.png" />'
        )
        asset = Asset(
            title="Q3 Campaign Blog Draft",
            author_name="Alex (External Agency)",
            author_role="Agency",
            content_text=demo_text,
            file_type="text",
            state=AssetState.DRAFT,
            current_guideline_version=gl.version,
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)

        from . import scan as scan_mod
        results = scan_mod.run_scan_all(db, asset)
        print("Seeded demo asset:", asset.id)
        print("Scan results:", results)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
