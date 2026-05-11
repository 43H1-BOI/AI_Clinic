# Detailed Project Explanation — Dr Rajat AI Clinic

## 1. Project Overview

**Title:** Hierarchical Structuring of Unstructured Clinical Conversations Using Hybrid Speech-NLP Modeling

**Subtitle:** A Real-Time Clinical Conversation Intelligence System for Transforming Doctor-Patient Dialogue into Structured Medical Records

**Type:** Academic Dissertation Project  
**Degree:** Bachelor of Computer Applications (BCA), Semester VI  
**Session:** July–December 2026  
**Institution:** International Institute of Professional Studies (IIPS), Devi Ahilya Vishwavidyalaya (DAVV), Indore, M.P.  

**Students:** Abhishek Yadav (IC-2K23-06), Dhairya Joshi (IC-2K23-26)  
**Guide:** Mr. Shaligram Prajapat  

---

## 2. Problem Statement

The Dr. Rajat multi-specialty clinic (Chiropractic, Osteopathy, Ayurveda, Panchakarma, Spine Care) managed patient records entirely through paper files, disconnected Excel spreadsheets, and undocumented verbal consultations. This caused six critical problems:

| # | Problem | Impact |
|---|---------|--------|
| 1 | Fragmented patient records | 10–15 min to retrieve complete history |
| 2 | Manual pain assessment (paper VAS) | No digitization, trend tracking, or cross-visit comparison |
| 3 | Error-prone consultation workflow | Handwritten notes → manual Excel transcription → data entry errors |
| 4 | No AI integration | Zero analysis of doctor-patient conversations |
| 5 | No progress tracking | Pain scores as isolated data points, no longitudinal view |
| 6 | No analytics | No dashboards, outcome analysis, or quality reporting |

---

## 3. Solution Architecture

The system is a **desktop-based AI-powered clinical management system** with a **5-layer architecture**:

### 3.1 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | Streamlit | 1.28+ | Python-native UI framework |
| Backend | Python | 3.12+ | Core logic & orchestration |
| Database | SQLite | 3.x | Embedded zero-config DB |
| ORM | SQLAlchemy | 2.0+ | Database abstraction |
| Validation | Pydantic | 2.0+ | Rust-based runtime type checking (5–50× faster than v1) |
| LLM | GPT-4o-mini | Latest | Clinical summarization & entity extraction |
| ASR | Faster-Whisper | Latest | CPU-based bilingual Hindi-English transcription (int8) |
| Visualization | Plotly | 5.17+ | Interactive clinical charts |
| Data | Pandas | 2.0+ | Data processing & seed data |

### 3.2 System Layers (4-Tier)

```
┌─────────────────────────────────────────────────────┐
│  PRESENTATION LAYER (Streamlit)                      │
│  8 pages: registration, pain_assessment,             │
│  consultation, treatment, conversation,              │
│  ai_analysis, progress_tracker, dashboard            │
├─────────────────────────────────────────────────────┤
│  APPLICATION LAYER (Python)                          │
│  app.py → importlib dynamic routing + session mgmt   │
├─────────────────────────────────────────────────────┤
│  AI SERVICES LAYER                                    │
│  whisper_service │ llm_service │ risk_engine │       │
│  symptom_extractor │ prompts                         │
├─────────────────────────────────────────────────────┤
│  DATA ACCESS LAYER                                    │
│  db │ models │ crud │ schema │ seed_data              │
│  ┌───────────┐                                       │
│  │  SQLite   │                                       │
│  └───────────┘                                       │
└─────────────────────────────────────────────────────┘
```

### 3.3 Codebase (24 Files, ~2,700 Lines)

| Layer | Files | Lines |
|-------|-------|-------|
| Presentation (pages/) | 8 modules | ~1,084 |
| Application (root) | app.py | 51 |
| AI Services (ai/) | 5 modules | 213 |
| Data Access (database/) | 5 modules | 1,329 |
| Utilities (utils/) | 4 modules | 168 |

---

## 4. Core Innovation: The 5-Layer AI Pipeline

```
┌────────────────────────────────────────────────────────┐
│ Layer 5: RECORD GENERATION                              │
│ Pydantic AIAnalysisOutput schema → <1ms validation     │
├────────────────────────────────────────────────────────┤
│ Layer 4: LLM DEEP ANALYSIS                              │
│ GPT-4o-mini → summary, entities, therapy recs → 2-4s  │
├────────────────────────────────────────────────────────┤
│ Layer 3: RISK ASSESSMENT                                │
│ 7-param deterministic engine → 4 levels → <10ms        │
│                  ╔═══ OFFLINE ═══╗                     │
├────────────────────────────────────────────────────────┤
│ Layer 2: KEYWORD EXTRACTION                             │
│ 18 pain keywords + 26 body parts → pattern match       │
├────────────────────────────────────────────────────────┤
│ Layer 1: SPEECH RECOGNITION                             │
│ Faster-Whisper base int8 → CPU → Hindi/English         │
│ 5-min audio → ~30s │ WER 16% │ ~1.5 GB RAM             │
└────────────────────────────────────────────────────────┘
```

### Layer 1 — Speech Recognition
- **Model:** Faster-Whisper base (int8 quantized, CPU)
- **Language:** Auto-detect (bilingual Hindi-English)
- **Performance:** 5-min audio ~30s, 10-min audio ~58s
- **Memory:** ~1.5 GB RAM
- **WER:** base int8 16.0%, large-v3-turbo int8 9.5%

### Layer 2 — Keyword Extraction
- **Approach:** Simple rule-based matching against hardcoded lists
- **Keywords:** 17 pain descriptors (pain, ache, numb, tingling, burning, etc.)
- **Body Parts:** 26 anatomical regions (neck, shoulder, back, lumbar, etc.)
- **Limitation:** No negation handling (known limitation)

### Layer 3 — Risk Assessment (Deterministic, Always Offline)
- **Parameters:** pain_severity, numbness, nerve_radiation, muscle_weakness, previous_surgery, sleep_disturbance
- **Scoring:**
  - Pain ≥8 AND numbness: +3
  - Pain ≥7 AND nerve_radiation: +2
  - Muscle weakness: +2
  - Numbness AND nerve_radiation: +2
  - Prior surgery: +1
  - Pain ≥6 AND sleep_disturbance: +1
  - Pain ≤3: -1 (floor at 0)
- **Classification:** CRITICAL (≥6), HIGH (≥4), MODERATE (≥2), LOW (<2)
- **Latency:** <10 ms

### Layer 4 — LLM Deep Analysis (Online, Optional)
- **Model:** GPT-4o-mini (temperature 0.1)
- **Context:** Transcript (4K chars) + consultation notes (2K chars) + assessment (2K chars)
- **Output:** summary, symptoms[], possible_condition, recommended_therapy[], recommended_tests[], pain_severity, recovery_prediction, followup, confidence_score
- **Latency:** 2–4 seconds
- **Fallback:** Returns error message on API failure (graceful degradation)
- **Accuracy:** 142.66 pts (78.5%) on MedicalBenchmark MIR 2025

### Layer 5 — Record Generation
- **Validator:** Pydantic AIAnalysisOutput schema (Rust-based core)
- **Validation time:** <1 ms
- **Retry:** Up to 2 automatic retries on validation failure
- **Storage:** Raw JSON preserved alongside validated fields

---

## 5. Database Design (7 Tables, 3NF)

```
patients (1) ──┬── (N) pain_assessments
               ├── (N) progress_tracking
               └── (N) consultations
                          └── (N) treatments
                          └── (N) conversations
                                       └── (N) ai_outputs
```

All relationships use `cascade="all, delete-orphan"`. Database uses SQLite with WAL mode for improved concurrency. Size: ~50 MB with full seed data (supports 50k+ patients).

---

## 6. End-to-End Workflow

```
Patient Arrives
      ↓
[1] REGISTRATION → Personal info + medical history → auto-BMI → save
      ↓
[2] PAIN ASSESSMENT → VAS 0-10 + pain areas + spine levels + neuro symptoms → save
      ↓
[3] CONSULTATION → Structured notes + diagnosis + report upload → follow-up date
      ↓
[4] TREATMENT → Multi-therapy selection + conditional fields → exercise prescription
      ↓
[5] CONVERSATION → Audio upload OR manual transcript → Whisper → keyword extraction
      ↓
[6] AI ANALYSIS → Risk engine (<10ms) + GPT-4o-mini (2-4s) → Pydantic validation → save
      ↓
[7] PROGRESS TRACKER → Session comparison + improvement metrics → patient feedback
      ↓
[8] DASHBOARD → Metric cards + Plotly charts + full history → search & export
```

---

## 7. Development Timeline (12 Weeks, Agile Scrum)

| Sprint | Weeks | Deliverable |
|--------|-------|-------------|
| 1 | 1–2 | Requirements, system architecture, DB schema |
| 2 | 2–3 | ORM models, CRUD layer, Pydantic schemas |
| 3 | 3–4 | Patient registration module |
| 4 | 4–5 | Pain assessment with VAS |
| 5 | 5–6 | Consultation entry with file upload |
| 6 | 6–7 | Multi-therapy treatment management |
| 7 | 7–8 | Conversation + Whisper integration |
| 8 | 8–9 | AI risk engine + LLM pipeline |
| 9 | 9–10 | Progress tracking + Plotly dashboard |
| 10 | 10–11 | Seed data generation + comprehensive testing |
| 11–12 | 11–12 | Deployment, documentation, final report |

---

## 8. Testing (58 Test Cases, 100% Pass)

| Type | Count | Pass | Fail | Rate |
|------|-------|------|------|------|
| Black Box | 16 | 16 | 0 | 100% |
| White Box | 14 | 14 | 0 | 100% |
| Unit | 22 | 22 | 0 | 100% |
| Integration | 10 | 10 | 0 | 100% |
| System | 10 | 10 | 0 | 100% |
| **Total** | **58** | **58** | **0** | **100%** |

**Seed Data:** 209 patients · 431 consultations · 1,059 progress records · 9 disease templates

---

## 9. Benchmarks

| Metric | Result |
|--------|--------|
| Whisper (5-min audio → text) | ~30 s |
| Whisper (10-min audio → text) | ~58 s |
| Risk Engine (7 params) | <10 ms |
| LLM Analysis (GPT-4o-mini) | 2–4 s |
| Pydantic Validation | <1 ms |
| SQLAlchemy single INSERT | 5–15 ms |
| SQLAlchemy batch SELECT (1000) | ~50 ms |
| Database (209 patients + 1700+ records) | ~50 MB |

---

## 10. Key Achievements

- Complete digitization of patient care lifecycle across 8 modules
- Dual-tier AI (deterministic risk + LLM) with graceful fallback
- Bilingual Hindi-English speech-to-text with auto-language detection
- 100% test pass rate on 58 test cases
- Offline-first: core CRUD + risk engine work without internet
- Zero software licensing cost (all open-source + optional OpenAI API)
- Paper cost elimination: 15,000–25,000 INR/year savings
- Consultations saved: 5–10 minutes per visit (instant history access)

---

## 11. Limitations

| Limitation | Impact | Future Fix |
|-----------|--------|------------|
| SQLite concurrency (single writer) | No multi-user simultaneous writes | Migrate to PostgreSQL |
| No authentication/roles | All users have full access | Add Streamlit auth + RBAC |
| Whisper base WER 16% | May miss accented/low-quality audio | Upgrade to large-v3-turbo |
| LLM requires internet + API key | No deep analysis offline | Local LLM (Llama/Gemma) |
| Hindi + English only | Regional languages not supported | Add Marathi, Gujarati, etc. |
| No FHIR compliance | No healthcare interoperability | Implement HL7 FHIR R4 |
| Static risk engine (rule-based) | No ML-powered predictions | Train on accumulated data |
| Seed data only (synthetic) | No real clinical validation | IRB-approved pilot deployment |

---

## 12. Financial Summary

| Item | Cost |
|------|------|
| Development (all open-source) | $0 |
| Optional: OpenAI API credits | ~$50 |
| Hardware | Existing clinic PC |
| **Total** | **< $50** |

| Annual Savings | INR |
|----------------|-----|
| Paper elimination | 15,000–25,000 |
| Staff time (3–5 hrs/week) | 60,000–100,000 |
| **Total** | **75,000–125,000** |

ROI: Immediate from day one.
