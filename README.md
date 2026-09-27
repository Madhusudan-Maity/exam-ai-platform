# EXAM-AI-COACH: Intelligent Multi-Exam Preparation Platform

An adaptive, offline-capable, AI-driven personal preparation coach designed for competitive government exams:
- **SSC CPO** (Sub-Inspector in Delhi Police & CAPFs)
- **SSC JE (CS/IT)** (Junior Engineer Technical & Non-Tech)
- **WBP & Kolkata Police** (Constable & Sub-Inspector — Prelims & Mains)

---

## 🎯 Core Features & Capabilities

1. **The 80/20 Pareto Yield Engine**: Pinpoints high-frequency, high-yield topics to maximize scoring potential in minimum study time.
2. **"Master Once, Calibrate Everywhere" Multi-Exam Core**: A shared knowledge graph mapping conceptual mastery ($\theta$) across 3 distinct difficulty tiers:
   - **Level 1 (Basic/Direct Fact)**: 20–30s pacing (WBP Constable).
   - **Level 2 (Applied Concept)**: 35–45s pacing (SSC JE Paper 1, WBP SI).
   - **Level 3 (Advanced/Multi-Variable)**: 50–70s pacing (SSC CPO).
3. **Speed $\times$ Accuracy Telemetry**: Real-time pacing analysis, trap question detection ($>2.5\times$ target time), and negative-marking risk prevention.
4. **Automated Mistake Vault**: Automatically captures and categorizes every error (Conceptual Gap, Calculation Slip, Trap/Misread, Panic) for targeted re-testing.
5. **Multi-Tier Spaced Repetition (FSRS)**: Daily Morning Active Recall $\rightarrow$ Weekly Sunday Interleaved Practice $\rightarrow$ Monthly Benchmark Simulation $\rightarrow$ Final 48-Hour Exam Digest.
6. **Living Markdown Knowledge Base (Obsidian Compatible)**: All concepts, formulas, syllabi, cutoffs, and mistakes exist as linked `.md` files in `vault/`.
7. **Omnichannel Delivery**: High-speed Progressive Web App (PWA) with offline IndexedDB caching + 24/7 Telegram Hermes Micro-Coach Bot.

---

## 🏗️ Tech Stack

- **Backend**: Python 3.11+ / 3.13, FastAPI (async), SQLAlchemy 2.0, Pydantic v2, `py-fsrs`.
- **Database**: SQLite (local single-file database) with async support.
- **Knowledge Core**: Markdown LLM-Wiki (`vault/`) compatible with Obsidian.
- **AI & Quality Control**: Google Gemini 2.5 Flash API + JEV (Judge-Evaluator-Verifier) harness.
- **Frontend / Client**: React 19, Vite, Tailwind CSS v4, Dexie.js (IndexedDB for offline PWA).
- **Remote Access**: Cloudflare Zero Trust Tunnel (encrypted HTTPS mobile access).

---

## 📁 Repository Structure

```text
exam-ai-platform/
├── .github/
│   └── copilot-instructions.md   # VS Code AI Customization & Token Optimization Rules
├── .vscode/
│   └── settings.json             # Workspace formatters & Python interpreter settings
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI endpoints (exams, questions, diagnostic, etc.)
│   │   ├── engines/              # Pareto Yield, IRT/BKT Student Model, FSRS, Telemetry
│   │   ├── ingestion/            # Multilingual OCR, parser & JEV Verifier
│   │   ├── models/               # SQLAlchemy database tables
│   │   ├── schemas/              # Pydantic data schemas
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── tests/                    # Automated pytest test suites
│   ├── pytest.ini
│   └── requirements.txt
├── vault/                        # Your Obsidian Markdown Knowledge Base
│   ├── concepts/                 # Evergreen theory summaries
│   ├── formulas/                 # Math & CS formula cheatsheets
│   ├── traps/                    # Common exam tricks & negative-marking traps
│   ├── mistakes/                 # Mistake Vault error cards
│   ├── syllabi/                  # Official syllabus checklists
│   ├── cutoffs/                  # Category-wise cutoff trend charts
│   ├── notifications/            # Active exam timelines & rules
│   └── resources/                # Raw PDF papers & attachments
├── scripts/
│   ├── init_db.py                # Database creation & taxonomy seeder
│   ├── ingest_pyqs.py            # Multilingual PYQ ingestion pipeline
│   └── sample_pyqs.json          # Multi-exam sample question bank
├── docs/
│   └── progress.md               # Phase-wise milestone tracker
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Setup Backend Virtual Environment
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Initialize Database & Seed Taxonomies
```powershell
python ..\scripts\init_db.py
```

### 3. Ingest Sample Multilingual PYQs
```powershell
python ..\scripts\ingest_pyqs.py ..\scripts\sample_pyqs.json
```

### 4. Run Automated Test Suite
```powershell
pytest
```

### 5. Start the FastAPI Local Server
```powershell
uvicorn app.main:app --reload --port 8000
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser for the interactive API documentation.
