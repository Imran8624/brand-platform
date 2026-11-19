# Brand Governance Platform

Operational, human-in-the-loop pre-publication control system that transforms static brand
guidelines into enforceable, explainable guardrails — preventing off-brand, inaccurate, or
non-compliant content from reaching the public while accelerating team review cycles.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Imran8624/brand-platform)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/Imran8624/brand-platform)

Built for a hackathon. **Fully offline** — no external LLM/API keys required. All detection is
deterministic/rule-based with clearly-labeled detection methods (deterministic / heuristic),
satisfying the "AI Transparency" requirement.

## 🚀 One-Click Deploy Links

- **Deploy on Render**: [Deploy to Render](https://render.com/deploy?repo=https://github.com/Imran8624/brand-platform)
- **Deploy on Railway**: [Deploy on Railway](https://railway.app/new/template?template=https://github.com/Imran8624/brand-platform)
- **GitHub Repository**: [https://github.com/Imran8624/brand-platform](https://github.com/Imran8624/brand-platform)

## What it delivers

* **Single source of truth** — ingest PDF/TXT/DOCX brand guidelines into a live, versioned
  knowledge base (fact sheet, banned terms, voice rules). Latest version is enforced.
* **Six-dimension detection** on every draft before publication:
  1. Tone & Voice Drift
  2. Terminology & Naming Consistency
  3. Messaging Alignment
  4. Fact & Claim Verification
  5. Visual Brand Consistency (logo stretch, off-palette colors)
  6. Accessibility Compliance (WCAG contrast, alt text, min font size)
* **Explainable remediation** — every flag carries plain-language rationale, a source citation
  to the exact guideline/fact-sheet row, and a non-destructive suggested fix.
* **Human authority** — creators/reviewers Accept, Manually Edit, or Dismiss-with-Reason.
* **Role-based approval & audit trail** — `Draft → In Review → Approved → Published` across
  Creator / Brand Manager / Legal Reviewer / Admin. Approval is blocked until critical/high
  flags are resolved. Every action is timestamped in an immutable audit log.
* **Governance intelligence dashboard** — flag telemetry by dimension, top broken rules,
  override rate, recent potential escapes.
* **Confidentiality & transparency** — deterministic processing, detection-method labeling per scan.

## Stack

* Python 3.14, FastAPI, SQLAlchemy, SQLite
* `pdfplumber`, `python-docx`, `Pillow` (ingest & visual analysis)
* Frontend: vanilla HTML/JS + Tailwind CSS + Chart.js (single page, CDN)

## Run it

```bash
# from the hackaton folder
python -m pip install -r requirements.txt
python run.py
```

`run.py` seeds sample brand guidelines ("Nova Brand Guidelines 2026") plus a demo agency draft
loaded with intentional violations, then starts the API at `http://localhost:8000`.

Open `http://localhost:8000` in a browser for the UI. Switch roles in the nav to try
Creator → Brand Manager → Legal Reviewer → Admin workflows.

## API highlights

| Endpoint | Purpose |
|---|---|
| `GET /api/me` | current user / role |
| `POST /api/session/role` | switch role (demo auth) |
| `POST /api/guidelines/upload` | ingest a brand guideline (Admin/Brand Manager) |
| `GET /api/guidelines` | list versioned KB |
| `POST /api/assets` | create a draft asset |
| `POST /api/assets/{id}/submit` | Draft → In Review (Creator) |
| `POST /api/assets/{id}/scan` | run six-dimension scan |
| `GET /api/assets/{id}/flags` | list explainable flags |
| `POST /api/flags/{id}/decide` | accept / dismiss / edit (human decision) |
| `POST /api/assets/{id}/approve` | In Review → Approved (blocked if critical/high open) |
| `POST /api/assets/{id}/publish` | Approved → Published |
| `GET /api/assets/{id}/audit` | tamper-evident audit trail |
| `GET /api/dashboard` | governance telemetry |

## Sample data

Seeding creates:
* `BrandGuideline v2026.1` with fact sheet, banned terms, and voice rules
* A demo asset "Q3 Campaign Blog Draft" (authored by an external agency) containing deprecated
  product names, banned words, an unsubstantiated `100%` claim, aggressive hype, low font size,
  and missing alt-text — designed to trigger flags across all six dimensions.

## Notes / limitations (hackathon scope)

* Authentication is a simple in-memory role switch (no real identity provider).
* Detection is deterministic/heuristic; production would layer an LLM for nuanced tone and
  messaging alignment while keeping the rule-based guardrails for hard compliance.
* Visual analysis uses Pillow dominant-color/aspect-ratio heuristics (no OCR).
* SQLite is used for zero-config local deployment; swap the engine for Postgres in production.
