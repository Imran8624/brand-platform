"""SQLAlchemy models for the Brand Governance platform."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from .database import Base


class AssetState(str, enum.Enum):
    DRAFT = "Draft"
    IN_REVIEW = "In Review"
    LEGAL_REVIEW = "Legal Review"
    APPROVED = "Approved"
    PUBLISHED = "Published"
    REJECTED = "Rejected"


class UserRole(str, enum.Enum):
    CREATOR = "Creator"
    BRAND_MANAGER = "Brand Manager"
    LEGAL_REVIEWER = "Legal Reviewer"
    ADMIN = "Admin"
    ADMIN_COMPANY_REVIEW = "Admin & Company Review"


class ScanStatus(str, enum.Enum):
    PASS = "pass"
    FLAG = "flag"
    REVIEW = "review"


class FlagDecision(str, enum.Enum):
    OPEN = "open"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    EDITED = "edited"


class BrandGuideline(Base):
    __tablename__ = "brand_guidelines"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, nullable=False, index=True)  # e.g. "2026.1"
    title = Column(String, nullable=False)
    content_text = Column(Text, nullable=False)  # full extracted text
    source_file = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    fact_rows = relationship("FactSheetRow", back_populates="guideline", cascade="all, delete-orphan")
    banned_terms = relationship("BannedTerm", back_populates="guideline", cascade="all, delete-orphan")
    voice_rules = relationship("VoiceRule", back_populates="guideline", cascade="all, delete-orphan")

class FactSheetRow(Base):
    __tablename__ = "fact_sheet"

    id = Column(Integer, primary_key=True, index=True)
    guideline_id = Column(Integer, ForeignKey("brand_guidelines.id"), nullable=False)
    entity = Column(String, nullable=False)        # e.g. "Product X"
    claim = Column(String, nullable=False)         # e.g. "uptime"
    value = Column(String, nullable=False)         # e.g. "99.9%"
    source_quote = Column(String, nullable=True)   # exact quote from guideline
    category = Column(String, nullable=True)       # e.g. "performance", "pricing"
    created_at = Column(DateTime, default=func.now())

    guideline = relationship("BrandGuideline", back_populates="fact_rows")


class BannedTerm(Base):
    __tablename__ = "banned_terms"

    id = Column(Integer, primary_key=True, index=True)
    guideline_id = Column(Integer, ForeignKey("brand_guidelines.id"), nullable=False)
    term = Column(String, nullable=False)
    replacement = Column(String, nullable=True)
    category = Column(String, nullable=True)       # e.g. "deprecated_name", "jargon", "banned_word"
    severity = Column(String, default="medium")    # low/medium/high/critical
    created_at = Column(DateTime, default=func.now())

    guideline = relationship("BrandGuideline", back_populates="banned_terms")


class VoiceRule(Base):
    __tablename__ = "voice_rules"

    id = Column(Integer, primary_key=True, index=True)
    guideline_id = Column(Integer, ForeignKey("brand_guidelines.id"), nullable=False)
    pattern = Column(String, nullable=False)       # keyword / regex-ish phrase to watch
    category = Column(String, nullable=True)       # e.g. "aggressive_hype", "jargon", "passive_voice"
    description = Column(String, nullable=True)    # plain-language rationale
    severity = Column(String, default="medium")
    created_at = Column(DateTime, default=func.now())

    guideline = relationship("BrandGuideline", back_populates="voice_rules")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author_name = Column(String, nullable=False)
    author_role = Column(String, nullable=False)   # Creator / Agency / AI-Tool
    content_text = Column(Text, nullable=True)     # extracted text (for text/doc/pdf assets)
    file_path = Column(String, nullable=True)      # stored asset (image/doc)
    file_type = Column(String, nullable=True)      # text/image/pdf/docx
    state = Column(Enum(AssetState), default=AssetState.DRAFT, nullable=False)
    current_guideline_version = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)

    scans = relationship("Scan", back_populates="asset", cascade="all, delete-orphan")
    flags = relationship("Flag", back_populates="asset", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="asset", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    dimension = Column(String, nullable=False)     # one of the six dimensions
    status = Column(Enum(ScanStatus), default=ScanStatus.PASS, nullable=False)
    score = Column(Integer, default=100)           # 0-100 compliance score for the dimension
    details = Column(Text, nullable=True)          # JSON string of per-flag details
    scanned_at = Column(DateTime, default=func.now())
    detection_method = Column(String, default="deterministic")  # deterministic / heuristic / ai

    asset = relationship("Asset", back_populates="scans")
    flags = relationship("Flag", back_populates="scan", cascade="all, delete-orphan")


class Flag(Base):
    __tablename__ = "flags"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    dimension = Column(String, nullable=False)
    severity = Column(String, nullable=False)      # low / medium / high / critical
    element = Column(String, nullable=True)        # what was flagged (quote / region)
    rationale = Column(Text, nullable=False)       # plain-language why
    source_citation = Column(String, nullable=True)  # guideline / fact-sheet ref
    suggested_fix = Column(Text, nullable=True)    # non-destructive rewrite
    original_text = Column(Text, nullable=True)    # the flagged snippet
    status = Column(Enum(FlagDecision), default=FlagDecision.OPEN, nullable=False)
    decided_by = Column(String, nullable=True)
    decided_by_role = Column(String, nullable=True)
    decided_at = Column(DateTime, nullable=True)
    decision_reason = Column(Text, nullable=True)  # why accept/dismiss/edit
    resolved_text = Column(Text, nullable=True)    # final text after human edit

    scan = relationship("Scan", back_populates="flags")
    asset = relationship("Asset", back_populates="flags")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    action = Column(String, nullable=False)        # e.g. "state_change", "flag_decision", "scan_run"
    actor = Column(String, nullable=False)
    actor_role = Column(String, nullable=False)
    old_state = Column(String, nullable=True)
    new_state = Column(String, nullable=True)
    details = Column(Text, nullable=True)          # JSON string
    timestamp = Column(DateTime, default=func.now())

    asset = relationship("Asset", back_populates="audit_logs")
