# Inkloom AI — Master Specification Prompt (Updated & Hardened)

Build "Inkloom AI", a full-stack pre-publication brand governance and approval web application using React, TypeScript, Tailwind CSS, a Node/Express server, a Python deterministic rule-checking backend, and server-side Gemini AI (gemini-4-hydrogen) analysis.

### 1. Visual Theme & Language Style
- **Color Palette**: High-contrast dark theme using Black (`#09090B` background, `#18181B` cards/panels), Electric Pink (`#DB2777`) for primary buttons, alerts, and active highlights, and Sapphire Blue (`#2563EB`) for navigation tabs, secondary actions, and workflow progress.
- **Language Rule**: Write ALL UI labels, rule explanations, mistake messages, emails, video scripts, and AI responses in basic, simple, everyday English (short sentences, no corporate/legal/technical jargon) so anyone can read it aloud and understand immediately.

### 2. Navigation Views (4 Main Tabs + New Draft Modal)
1. **Review Studio**: Role-isolated workspace for checking drafts across 4 formats (Text, Banner, PDF, Video & Spoken Script).
2. **Knowledge Base**: Live, editable "Brand Rules & Guide" containing Fact Sheet rules (approved numbers, prices, SLAs, security badges), Words & Names rules (banned/deprecated terms and capitalization), Brand Voice & Main Points, and Secret Project Names. Clicking any Fact Sheet or Word rule opens a detailed case view showing where mistakes happened and how past cases were fixed or approved.
3. **Approval Trail**: Pipeline table of drafts, a "Changes Since Last Approval" line-by-line diff viewer, and a tamper-evident "Locked Approval History" ledger with content hash chaining.
4. **Team Insights (Telemetry & Intelligence)**: Governance dashboard showing Serious Problems to Fix, Time Saved in Reviews, Published Drafts, Private Details Hidden, mistake breakdown by team/source (e.g., External Agency vs. Internal Employee), most broken rules, and frequently skipped rules.
   - **Zero-Crash Resilience**: Must safely handle unscanned content, empty scan lists, and zero-flag drafts without throwing exceptions, division-by-zero, or blank screens.
   - **Zero-Race Hydration**: Must pre-hydrate telemetry with instantaneous default states so automated browser assertions never fail or race async loading.
- Include a "New Draft" modal to create and immediately scan new Text, Banner, PDF, or Video Script drafts.

### 3. Strict Role Isolation & Sequential Approval Workflow
- **Role Switcher in Review Studio**: Creator (with unread message badge), Brand Manager, and Legal Reviewer. Switching roles isolates the UI so each person only sees their own workspace.
- **Strict Approval Order**: Draft -> 1. Brand Manager Review -> 2. Legal Review -> 3. Final Approval -> Published (or Rejected).
- **Visual Progress Bar**: Show a 3-stage color-coded (blue/pink) progress bar inside the workspace header tracking Step 1/3 (Brand Manager Review), Step 2/3 (Legal Review), and Step 3/3 (Final Approval) with percentage completion.
- **Creator Workspace ("Creator Desk")**:
  - Displays creator profile, editable content/banner/PDF/video script canvas, and submission/publish actions.
  - Creators cannot approve/review their own mistakes; instead, they receive updates in a "Creator Messages & Mistake Emails" inbox (with exact mistake locations, suggested fixes, and "Open in Email App" mailto links) when review starts, passes to Step 2, is approved by both reviewers, or is rejected/sent back.
- **Brand Manager & Legal Reviewer Workspaces**:
  - Display a "Secret Project Names" panel visible only to Brand Manager and Legal Reviewer so NDA codenames are clearly highlighted.
  - Display an expandable "Approved Words & Names" vocabulary reference directly inside the review panel.
  - Brand Manager handles Step 1 (approve or reject and pass to Legal); Legal Reviewer handles Step 2 and grants Final Approval only if Brand Manager approved and zero "Must Fix" items remain. If both reject (or Legal rejects), the asset moves to Rejected and emails the mistakes to the Creator.

### 4. Brand Manager Session — Complete 3-Level Automation
Inside the Brand Manager view only, build a dedicated "Brand Manager Session · Complete 3-Level Automation" control panel with a "Run All 3 Levels" button, individual level triggers, an "Auto-Run Step 1" toggle, and an "Auto-Decide from Report" toggle:
- **Level 1 (Send Email or Message)**: Automatically sends a plain-English status or mistake email/message to the creator via selectable channels (Email + Creator Inbox Message, Email Only, or Creator Inbox Message Only), updates the Creator inbox & Approval Trail, and provides Copy Message + Open in Email App actions.
- **Level 2 (Analyze Original File & Pinpoint Mistakes)**: Scans the draft's original file snapshot—or lets the Brand Manager upload a .txt, .md, .csv, or .pdf original file—and renders an "Original File Mistake Map" showing numbered lines/scenes, exact column ranges, the offending phrase, why it failed, and the suggested fix.
- **Level 3 (Action Based on Report)**: Generates a scored report (0–100, counts for Must Fix, Check This, Tips, secret project names, and a downloadable .txt report) from Level 2's findings and acts automatically depending on the report:
  - **Pass** (0 serious mistakes): Auto-approves Step 1 to Legal Review and notifies the creator.
  - **Needs Review** (minor warnings/tips only): Holds at Step 1 and sends the fix list to the creator.
  - **Blocked** (1+ Must-Fix mistakes or secret codenames): Auto-flags Step 1, forwards the report to Legal Review, and emails the exact original-file mistake lines to the creator.

### 5. Six-Dimension Pre-Publication Check & Multi-Modal Canvas
- Scan content across 6 dimensions using both deterministic Python/TypeScript rules and server-side Gemini AI:
  1. Tone & Style
  2. Words & Names
  3. Main Brand Message
  4. Facts & Numbers
  5. Brand Look (logo variant, aspect ratio, approved fonts, brand hex palette)
  6. Easy to Read & Watch (WCAG contrast ratio, minimum font size, alt text, video captions)
- **Finding Cards with Full Governance Metadata**:
  - Every finding card MUST visibly display its complete governance metadata directly on the card without hiding it behind an expand toggle:
    - **Severity Badge**: Color-coded `🔴 Must Fix`, `🟡 Check This`, `🔵 Tip`
    - **Dimension Tag**: Explicit check dimension (e.g. `Tone & Voice Drift`, `Terminology & Naming`, `Fact & Claim Verification`, `Visual Brand Consistency`, `Accessibility Compliance`)
    - **Policy Citation / Rule**: Exact guideline reference (`source_citation`)
    - **Exact Location**: Line and column label or section tag (`location`)
    - **Offending Phrase**: Snippet of the exact text or element flagged (`element` / `original_text`)
    - **Plain-English Rationale**: Clear, jargon-free explanation of why it failed (`rationale`)
    - **Suggested Fix**: Non-destructive, approved phrasing (`suggested_fix`)
    - **Action Buttons**: `✓ Use This Fix`, `✏ Edit Myself`, and `Skip This Check` (with required reason)
- **Multi-Modal Canvas & Dropzones**:
  - **Drag-and-Drop Dropzone**: Supports dragging and dropping audio (`.mp3`, `.wav`), video (`.mp4`, `.webm`), or script (`.txt`, `.md`, `.pdf`) directly onto the Creator Dashboard or Review Studio with automatic media duration detection and guideline validation.
  - **Queue Filter Dropdowns**: Clean Format (`All Formats`, `Text`, `Banner`, `PDF`, `Video`, `Audio`) and Status (`All Statuses`, `Draft`, `In Review`, `Approved`, `Published`, `Rejected`) filter dropdowns across Creator, Brand Manager, and Approval Trail queues.
  - **Approved Brand Color Preset Dropdown**: Pick approved brand palette presets directly in the Review Engine (`Cobalt Blue #2563EB`, `Signal Orange #F97316`, `Obsidian Black #080B12`, `Surface Slate #0F141F`, `Emerald Green #10B981`, `Signal Amber #F59E0B`, `Pure White #FFFFFF`) with live WCAG contrast checking.
  - **Text Canvas**: Live editable content with inline flag callouts.
  - **Banner Canvas**: Live preview with image upload, headline/color editing, and live WCAG button contrast and palette checks.
  - **PDF Canvas**: Document reader with page navigation and embedded policy violation callouts.
  - **Video & Script Canvas**: Interactive video timeline player, synced scene cards with timecodes, inline mistake highlights, secret codename badges, and captions toggle/check.
- **Privacy Shield ("Hide Private Info: On/Off")**: Locally masks emails, phone numbers, API keys, and secret project codenames before sending sanitized text to the external AI API, and restores placeholders locally afterward.

### 6. Personal AI Writing Helper
- Add an "AI Helper" slide-out drawer that lets the user draft plain-English copy or notes under four personas: Creator, Brand, Brand Manager, and Legal Reviewer, with one-click buttons to apply the generated text directly into the draft editor, review note box, or Creator mistake email.

### 7. Authentication Gate & Role-Based Access Control (RBAC)
- **Authentication Gate**: All users enter the platform through the split control-room authentication gate featuring Sign In and Register tabs.
- **Quick Demo Login Buttons**:
  - `Admin`: `admin@veritasbrand.io` (Sarah Chen) — Superadmin authority, user provisioning, full cross-dashboard role switching.
  - `Creator`: `creator@veritasbrand.io` (Alex Rivera) — Creator Desk, media dropzones, mistake emails, locked to creator workspace.
  - `Brand Manager`: `manager@veritasbrand.io` (Jordan Miller) — Step 1 governance, 3-level automations, locked to Brand Manager workspace.
  - `Company Review`: `legal@veritasbrand.io` (Elena Vance) — Legal compliance, SLA verification, secret name NDA checks, locked to Step 2 legal workspace.
- **Strict Role-Locking on Workspace Switching**:
  - Non-admin roles (Creator, Brand Manager, Company Review) are strictly locked to their single designated workspace upon login and cannot switch dashboards.
  - Admin users retain full multi-workspace switching across all dashboards for holistic review and verification.
- **Admin Access Control Panel** (Admin Only):
  - Accessible via `🛡️ Admin Access Control` in the global navbar.
  - User provisioning form (Name, Work Email, Role, Department).
  - Roster table with role reassignment dropdown and account suspension/restoration toggle.
  - Real-time telemetry on active vs. suspended accounts and RBAC enforcement.
- **Sign Out Flow**:
  - Dedicated `⎋ Sign Out` action returns the user securely to the authentication gate and unmounts workspace state.
