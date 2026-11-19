"""Seed additional multi-modal formats for Inkloom AI (Banner, PDF, Video)."""

from app.database import SessionLocal
from app.models import Asset, AssetState, BrandGuideline
from app import scan as scan_mod

def seed_formats():
    db = SessionLocal()
    try:
        gl = db.query(BrandGuideline).filter(BrandGuideline.is_active == True).first()
        gl_version = gl.version if gl else "2026.1"

        # Check existing titles
        titles = [a.title for a in db.query(Asset).all()]

        # 1. Banner
        if "Summer Cyber Sale Banner" not in titles:
            banner_text = (
                "Superfast Cloud Availability\n"
                "Experience measured 99.9% uptime with instant failover.\n"
                "Start 14-Day Free Trial\n"
                "fg:#FFFFFF bg:#09090B btn:#DB2777 14px\n"
                '<img src="stretched_logo.png" alt="Nova X Brand Logo" />'
            )
            banner_asset = Asset(
                title="Summer Cyber Sale Banner",
                author_name="Jordan (Internal Employee)",
                author_role="Creator",
                content_text=banner_text,
                file_type="banner",
                state=AssetState.IN_REVIEW,
                current_guideline_version=gl_version,
            )
            db.add(banner_asset)
            db.commit()
            db.refresh(banner_asset)
            scan_mod.run_scan_all(db, banner_asset)
            print("Seeded banner asset:", banner_asset.id)

        # 2. PDF
        if "Annual Security Whitepaper" not in titles:
            pdf_text = (
                "Nova X Enterprise Security Architecture Overview\n"
                "Certified ISO 27001 continuous compliance framework.\n"
                "Confidential project details: mentions Project Apollo preliminary benchmark.\n"
                "fg:#FFFFFF bg:#18181B 12px\n"
            )
            pdf_asset = Asset(
                title="Annual Security Whitepaper",
                author_name="Taylor (Compliance Lead)",
                author_role="Creator",
                content_text=pdf_text,
                file_type="pdf",
                state=AssetState.DRAFT,
                current_guideline_version=gl_version,
            )
            db.add(pdf_asset)
            db.commit()
            db.refresh(pdf_asset)
            scan_mod.run_scan_all(db, pdf_asset)
            print("Seeded PDF asset:", pdf_asset.id)

        # 3. Video & Spoken Script
        if "Nova X Product Launch Teaser" not in titles:
            video_text = (
                "[00:00 - 00:08] Scene 1 (Opening Hook): "
                "Voiceover: 'Introducing Nova X Pro, the most powerful engine for modern work.'\n"
                "[00:08 - 00:19] Scene 2 (Feature Walkthrough): "
                "Voiceover: 'With 100% guaranteed uptime and seamless collaboration across all your projects.'\n"
                "[00:19 - 00:30] Scene 3 (Closing Call to Action): "
                "Voiceover: 'Coming March 2026. Built in secret under Project Titan. Act now to join the VIP waitlist.'\n"
                "Captions: Enabled & Compliant. fg:#FFFFFF bg:#09090B 16px"
            )
            video_asset = Asset(
                title="Nova X Product Launch Teaser",
                author_name="Sam (Video Producer)",
                author_role="Agency",
                content_text=video_text,
                file_type="video",
                state=AssetState.DRAFT,
                current_guideline_version=gl_version,
            )
            db.add(video_asset)
            db.commit()
            db.refresh(video_asset)
            scan_mod.run_scan_all(db, video_asset)
            print("Seeded Video asset:", video_asset.id)

    finally:
        db.close()

if __name__ == "__main__":
    seed_formats()
