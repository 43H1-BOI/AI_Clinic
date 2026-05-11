# sExplain — Quick Reference: Dr Rajat AI Clinic

---

## What Is This Project?

A desktop-based AI-powered clinical management system that **transforms unstructured doctor-patient conversations into structured medical records** using speech recognition + LLM analysis.

**Students:** Abhishek Yadav (IC-2K23-06) · Dhairya Joshi (IC-2K23-26)  
**Guide:** Mr. Shaligram Prajapat · IIPS-DAVV, Indore · BCA Sem VI · 2026

---

## Why Was It Built?

A multi-specialty clinic (Chiropractic, Osteopathy, Ayurveda, Panchakarma, Spine Care) had:
- Paper files + Excel sheets — no unified system
- No AI analysis of consultations
- No progress tracking or dashboards

---

## Tech Stack

| Tool | What It Does |
|------|-------------|
| Python 3.12 | Backend logic |
| Streamlit | Desktop UI (8 pages) |
| SQLite + SQLAlchemy | Database + ORM |
| Pydantic v2 | Data validation (Rust-fast) |
| Faster-Whisper | Speech-to-text (Hindi/English, CPU, int8) |
| GPT-4o-mini | LLM clinical analysis |
| Plotly | Interactive charts |

---

## Architecture (4 Layers)

```
Streamlit UI (8 modules)
      ↓
Python app.py (orchestrator)
      ↓
AI Services (Whisper · LLM · Risk Engine · Keywords)
      ↓
Database (SQLAlchemy → SQLite, 7 tables)
```

24 files · ~2,700 lines of code.

---

## Core Innovation: 5-Layer AI Pipeline

```
Record Generation  ← Pydantic validation (<1ms)
LLM Deep Analysis  ← GPT-4o-mini (2-4s)
Risk Assessment    ← 7-param rule engine (<10ms) ← OFFLINE
Keyword Extraction ← 18 keywords + 26 body parts
Speech Recognition ← Faster-Whisper (5min→30s, WER 16%)
```

**Dual-tier:** Risk engine always works offline. LLM adds deep analysis when internet is available.

---

## Database (7 Tables)

`patients → consultations → conversations → ai_outputs`  
`patients → pain_assessments`  
`patients → progress_tracking`  
`consultations → treatments`

All in 3NF. SQLite with WAL mode. Scales to 50k+ patients.

---

## How It Works (End to End)

1. **Register** patient → auto-BMI, duplicate check
2. **Assess** pain → VAS 0-10, 20 pain areas, 34 spine levels, neuro symptoms
3. **Consult** → structured notes, diagnosis, report upload
4. **Treat** → 12 therapy types with conditional fields
5. **Capture** conversation → audio upload OR manual transcript
6. **Analyze** → risk engine (<10ms) + optional GPT-4o-mini (2-4s)
7. **Track** progress → session comparison, improvement metrics
8. **Dashboard** → Plotly charts, search, full history

---

## Testing

| Type | Count | Result |
|------|-------|--------|
| Black Box | 16 | ✅ 100% |
| White Box | 14 | ✅ 100% |
| Unit | 22 | ✅ 100% |
| Integration | 10 | ✅ 100% |
| System | 10 | ✅ 100% |
| **Total** | **58** | **✅ 100%** |

Seed data: 209 patients · 431 consultations · 1,059 progress records.

---

## Key Numbers

| Metric | Value |
|--------|-------|
| Whisper (5-min audio) | ~30 s |
| Risk Engine | <10 ms |
| LLM Analysis | 2–4 s |
| Pydantic Validation | <1 ms |
| Database (209 patients) | ~50 MB |
| Codebase | ~2,700 lines |
| Development cost | < $50 |
| Annual paper savings | 15,000–25,000 INR |

---

## Limitations (Quick)

- SQLite = one writer at a time
- No user login/roles
- Whisper base WER 16% (accents)
- LLM needs internet + API key
- Hindi + English only
- No FHIR standard compliance

---

## 6-Sprint Timeline

| Sprint | Deliverable |
|--------|-------------|
| 1 | Requirements + architecture |
| 2 | DB models + CRUD + Pydantic |
| 3–8 | All 8 modules (registration → dashboard) |
| 9 | Seed data + full testing |
| 10 | Deployment + report |

12 weeks total. Agile Scrum with 2-week sprints.

---

## TL;DR

> A Streamlit desktop app that listens to doctor-patient conversations (via Whisper), assesses clinical risk (rule engine), analyzes with GPT-4o-mini, and stores everything in a structured SQLite database — all while working offline for core features.
