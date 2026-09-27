# AI Agent & Copilot Instructions: EXAM-AI-COACH

## Project Overview
`EXAM-AI-COACH` is an intelligent, offline-capable multi-exam preparation platform for SSC CPO, SSC JE (CS/IT), and WBP/KP Police exams. It combines Item Response Theory (IRT), 80/20 Pareto Yield Scoring, Speed x Accuracy telemetry, automated Mistake Vault archiving, and FSRS Spaced Repetition.

## Architectural Guardrails
1. **Language & Tech Stack**:
   - Backend: Python 3.11+ / 3.13, FastAPI (async), Pydantic v2, SQLAlchemy 2.0 with SQLite.
   - Frontend: React 19, Vite, Tailwind CSS, Lucide Icons, Dexie.js (IndexedDB).
   - Spaced Repetition: `py-fsrs` (Free Spaced Repetition Scheduler).
   - Knowledge Base: Markdown files with bi-directional `[[WikiLinks]]` compatible with Obsidian.
2. **Deterministic vs. Generative Separation**:
   - Math calculations, timer recordings, IRT scoring, and FSRS intervals MUST be 100% deterministic (Python code/SQL queries).
   - LLMs (Gemini 2.5 Flash) are used ONLY for OCR extraction, reasoning explanations, multilingual parsing, and JEV verification.
3. **Multilingual & Math Safety**:
   - Support English, Bengali (বাংলা - UTF-8), and Hindi (हिंदी).
   - Mathematical expressions MUST use valid LaTeX syntax (`$x^2 + y^2 = r^2$` or `$$...$$`) compatible with KaTeX.
   - Never strip Bengali compound characters (যুক্তাক্ষর) during text cleaning.
4. **Token Optimization Rule for In-Editor Agents**:
   - Generate ONLY the exact requested class, function, or file diff.
   - Do NOT rewrite entire unchanged files or add unnecessary comments/boilerplate.
   - Always adhere to strict type annotations and Pydantic BaseModel definitions.
