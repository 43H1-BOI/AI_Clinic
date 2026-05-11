# Dr Rajat AI Clinic — Viva Guide

## Project Overview

**Dr Rajat AI Clinic** is a Streamlit-based clinical management system for a multi-specialty clinic (Chiropractic, Osteopathy, Ayurveda, Panchakarma, Spine Care). It combines an EMR (Electronic Medical Records) system with AI-powered analysis — including rule-based risk scoring, OpenAI GPT-4o-mini transcript summarization, and Faster-Whisper audio transcription.

The system tracks patients through the full care journey: registration → pain assessment → consultation → treatment → conversation recording → AI analysis → progress tracking → dashboard analytics.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | Python |
| Database | SQLite via SQLAlchemy 2.0 ORM |
| Validation | Pydantic 2.0 |
| LLM | OpenAI GPT-4o-mini |
| Transcription | Faster-Whisper (base, int8) |
| Charts | Plotly |
| Data | Pandas |

### Database Schema (6 tables)

```
patients ──1:N──► pain_assessments
patients ──1:N──► progress_tracking
patients ──1:N──► consultations ──1:N──► treatments
                                   ──1:N──► conversations ──1:N──► ai_outputs
```

### Architecture

```
app.py (entry point, lazy-loads pages)
  └── pages/ (8 pages — registration, assessment, consultation, treatment,
  │            conversation, AI analysis, progress tracker, dashboard)
  │     └── database/crud.py (22 CRUD functions)
  │           └── database/models.py (6 SQLAlchemy models)
  │                 └── clinic.db (SQLite)
  │
  └── ai/ (4 modules)
        ├── whisper_service.py (Faster-Whisper transcription)
        ├── symptom_extractor.py (keyword extraction)
        ├── risk_engine.py (rule-based risk scoring)
        └── llm_service.py (GPT-4o-mini integration)
              └── prompts.py (system/user prompts)
```

### File Map

| File | Purpose |
|------|---------|
| `app.py` | Entry point, sidebar navigation, lazy page loading |
| `database/db.py` | SQLAlchemy engine + session factory |
| `database/models.py` | 6 ORM models |
| `database/schema.py` | 9 Pydantic validation schemas |
| `database/crud.py` | 22 CRUD functions |
| `database/seed_data.py` | Seeds from `data.xlsx` with 9 disease templates |
| `ai/risk_engine.py` | 8-factor risk scoring → LOW/MODERATE/HIGH/CRITICAL |
| `ai/llm_service.py` | GPT-4o-mini with JSON response, Pydantic validated |
| `ai/prompts.py` | Clinical assistant prompts for LLM |
| `ai/whisper_service.py` | Local Faster-Whisper transcription |
| `ai/symptom_extractor.py` | Keyword-based pain/body-part extraction |
| `pages/patient_registration.py` | Add/Search/Edit/Delete patients, auto-BMI |
| `pages/pain_assessment.py` | Pain scoring form (0-10), multi-select pain areas |
| `pages/consultation.py` | Clinical notes, report uploads, follow-up |
| `pages/treatment.py` | Multi-therapy session (chiropractic, Ayurveda, etc.) |
| `pages/conversation.py` | Audio upload + Whisper OR manual transcript entry |
| `pages/ai_analysis.py` | Orchestrates risk engine + LLM, saves results |
| `pages/progress_tracker.py` | Session-wise pain/mobility/sleep tracking |
| `pages/dashboard.py` | Charts: pain trend, improvement radar, full history |
| `utils/constants.py` | Domain constants (20 pain areas, 34 spine levels, 12 therapies, etc.) |
| `utils/helpers.py` | UUID filenames, date formatting |
| `utils/ui_helpers.py` | Streamlit CSS theme, notification helpers |
| `utils/validators.py` | Mobile, email, age validators |

---

## Viva Questions & Answers

### General / Architecture

**Q1. What is the project about?**
A Streamlit-based clinic management system with AI features — tracks patients through registration, pain assessment, consultation, treatment, conversation recording, AI analysis (GPT + rule-based risk scoring), progress tracking, and dashboard analytics. Designed for chiropractic, osteopathy, Ayurveda, and spine care.

**Q2. Why Streamlit instead of Django/Flask?**
Streamlit lets you build data-driven UIs with pure Python — no HTML/CSS/JS needed. Ideal for internal clinic tools where fast prototyping and minimal frontend code matters. Not suited for multi-user production apps, but fine for an MVP.

**Q3. Explain the database schema and relationships.**
6 tables. `patients` is the root — linked to `pain_assessments` (1:N), `progress_tracking` (1:N), and `consultations` (1:N). `consultations` branches to `treatments` (1:N) and `conversations` (1:N). `conversations` links to `ai_outputs` (1:N). It's a star-like schema centered on the patient, with a consultation→conversation→AIOutput chain.

**Q4. Why SQLite instead of PostgreSQL/MySQL?**
Single-user desktop clinic app. SQLite needs zero setup, no server process, the database is a single file (`clinic.db`) that's easy to back up. Sufficient for MVP scale. SQLAlchemy makes it trivial to switch to PostgreSQL later by changing one connection string.

**Q5. How does lazy page loading work?**
`app.py` maps sidebar labels to module name strings (e.g., `"Add Patient": "patient_registration"`). When a user selects a page, `importlib.import_module(f"pages.{page_name}")` imports only that module, then calls `module.render()`. This avoids loading all 8 pages at startup, reducing memory and import time.

**Q6. What design patterns are used?**
- **Singleton:** OpenAI client and Whisper model are lazily created once, cached globally
- **Facade:** `crud.py` functions wrap SQLAlchemy session logic, pages never touch models directly
- **Strategy:** `ai_analysis.py` can use rule-based risk assessment, LLM analysis, or both — interchangeable
- **Template Method:** Each page follows the same pattern — `render()` function called from `app.py`

**Q7. How is error handling done?**
- OpenAI calls have retry logic (2 retries), graceful fallback with `{"fallback": True}`
- DB sessions are wrapped in try/finally to ensure closure
- Pydantic validates LLM JSON responses — malformed responses trigger fallback
- `ui_helpers.py` provides `show_success()`/`show_error()`/`show_warning()` for user-facing messages

### Database / ORM

**Q8. What is SQLAlchemy and why use it over raw SQL?**
SQLAlchemy is an ORM that maps Python classes to database tables. You write object-oriented code instead of SQL strings — avoids SQL injection, makes schema changes easier, and lets you switch database backends by changing one URL.

**Q9. Explain the Pydantic schemas and their role.**
Pydantic schemas (in `schema.py`) serve two purposes: (1) validate user input before writing to DB (e.g., `mobile` must be 10+ digits, `age` 0-150), and (2) validate the JSON response from GPT-4o-mini (`AIAnalysisOutput`) — if the LLM returns bad data, the Pydantic model rejects it and the system falls back gracefully.

**Q10. What is the seed data mechanism?**
`seed_data.py` reads `data.xlsx` and creates realistic test data. It has 9 predefined disease templates (back pain, sciatica, slip disc, etc.) with appropriate pain areas, spine levels, severity ranges, diagnoses, therapies, and bilingual Hindi/English conversation scripts. Uses fuzzy string matching to map free-text disease names to templates.

**Q11. How are file uploads handled?**
Medical reports go to `uploads/reports/` with UUID filenames (via `generate_unique_filename()`). Audio files go to `uploads/audio/`. Transcripts are saved to `uploads/transcripts/`. The DB stores only the file path, not the file itself.

### AI / LLM

**Q12. Explain the two-tier AI system.**
**Tier 1 — Rule-based risk engine** (`risk_engine.py`): Always available, no API key needed. Scores 0-8 based on 8 clinical factors (pain severity, numbness, nerve radiation, muscle weakness, sleep disturbance, previous surgery). Outputs LOW/MODERATE/HIGH/CRITICAL. Runs instantly.

**Tier 2 — GPT-4o-mini** (`llm_service.py`): Requires OpenAI API key. Sends transcript + consultation notes + assessment data to GPT with a structured prompt requesting JSON output. Validated against Pydantic schema. Falls back gracefully if unavailable.

**Q13. How does the risk scoring work?**
Each clinical factor adds points:
- Severe pain (>7) + numbness → +3
- High pain (>6) + nerve radiation → +2
- Muscle weakness → +2
- Numbness + radiation → +2
- Previous spine surgery → +1
- Pain affecting sleep → +1
- Low pain (<4) → -1 (min 0)

Total score 0-8 maps to: 0-1 LOW, 2-3 MODERATE, 4-5 HIGH, 6+ CRITICAL.

**Q14. How does the Whisper integration work?**
`whisper_service.py` lazy-loads a Faster-Whisper "base" model on CPU with int8 quantization (~1.5GB RAM). `transcribe_audio()` takes a file path, returns transcript text with segmented timestamps. Auto-detects language (supports Hindi and English mixed speech). Used by `conversation.py` when user uploads MP3/WAV/M4A.

**Q15. What if the OpenAI API key is not configured?**
The `analyze_with_llm()` function returns `{"fallback": True}` and the system falls back to rule-based analysis only. All AI analysis features still work — just without the LLM-generated summary, symptom extraction, and recommendations.

**Q16. How is the LLM prompt structured?**
`prompts.py` contains a system prompt (sets the AI as Dr. Rajat's clinical assistant specializing in chiropractic/osteopathy/Ayurveda) and a user prompt template with `{patient_info}`, `{transcript}`, `{consultation_notes}`, `{assessment_data}` placeholders. The prompt explicitly requests a JSON response with 12 specific fields.

**Q17. What are the limitations of the symptom extractor?**
`symptom_extractor.py` uses simple keyword matching against two hardcoded lists (17 pain words, 26 body parts). It doesn't understand negation ("no pain in the back" would still match "pain" and "back"), context, or severity. It's a lightweight fallback for when the LLM is unavailable.

### Streamlit / Frontend

**Q18. How does navigation work?**
Streamlit's `st.sidebar.radio` creates a menu from `SIDEBAR_OPTIONS` (8 items). When the selection changes, Streamlit re-runs the entire script from top to bottom. `app.py` reads the selected option, looks up the module name in `PAGE_MAP`, dynamically imports it, and calls `render()`.

**Q19. How is state managed?**
Minimal state management — Streamlit re-runs the entire script on every interaction, so variables don't persist between runs. DB queries re-fetch on every interaction. The `@st.cache_data` decorator isn't used (deliberately, since clinic data changes frequently). Sessions are opened/closed per interaction.

**Q20. Explain the Dashboard visualizations.**
The dashboard uses Plotly for two charts: (1) Pain Trend — line chart comparing previous vs current pain scores across sessions, (2) Improvement Radar — polar chart with 4 axes (pain, mobility, sleep, numbness improvement). Also shows metric cards (current pain, session count, diagnosis, recovery status) and expandable history sections.

### Deployment / DevOps

**Q21. How would you deploy this?**
Simplest: run `streamlit run app.py` on the clinic machine. For remote access: deploy on Streamlit Community Cloud, Railway, or a VPS with Nginx reverse proxy. Since it uses SQLite, only one user can write at a time — for multi-user, switch to PostgreSQL.

**Q22. How would you make this multi-user?**
Replace SQLite with PostgreSQL, add user authentication (Streamlit's `st.authenticator` or a custom login), add role-based access (doctor vs receptionist vs admin), and use connection pooling for the database.

**Q23. What security considerations exist?**
- OpenAI API key stored in `.env` (not in code)
- SQLAlchemy prevents SQL injection through parameterized queries
- File uploads use UUID filenames to prevent path traversal
- No user authentication currently (MVP limitation)
- Pydantic validation on all inputs
- No patient data encryption at rest (SQLite limitation)

### Project-Specific

**Q24. What would you add next?**
- Patient appointment scheduling with calendar view
- Email/SMS reminders for follow-ups
- Multi-language support (currently bilingual Hindi/English in seed data only)
- Drug interaction checker for Ayurveda medicines
- Export to PDF (clinical summary, prescription)
- Mobile app (or at least responsive design)

**Q25. What was the hardest problem?**
The LLM integration — getting consistent JSON output from GPT required careful prompt engineering plus Pydantic validation as a safety net. The seed data was also complex — 9 disease templates with realistic clinical data spanning all 6 tables, plus bilingual conversation scripts.

**Q26. How does the treatment page handle different therapy types?**
The treatment page uses multi-select for therapy types (12 options from `THERAPY_TYPES` constant). Depending on selection, different form fields appear: chiropractic areas for chiropractic, Panchakarma type + oil for Ayurveda, etc. All stored in a single `treatments` table with nullable columns.

**Q27. How is the progress tracker different from pain assessment?**
Pain assessment is a one-time snapshot (could be at intake or any visit). Progress tracker is explicitly session-based (session 1, 2, 3...) and compares previous vs current pain scores to show improvement. It also tracks mobility, sleep, and numbness improvement on a scale.

**Q28. Explain the consultation→conversation→AIOutput pipeline.**
A patient has a consultation. During/after that consultation, the doctor records a conversation (audio upload or manual transcript). Then the AI Analysis page loads that conversation, runs rule-based risk scoring and optionally GPT-4o-mini analysis, and stores the combined result as an AIOutput record linked to that conversation.

**Q29. What data does the LLM receive?**
Up to 4000 characters of transcript, 2000 characters of consultation notes (diagnosis + clinical findings), and 2000 characters of pain assessment data. All truncated to fit token limits while preserving clinical context.

**Q30. How does the system handle bilingual (Hindi/English) data?**
Whisper auto-detects mixed-language audio. The seed data includes Hindi-English conversation scripts. The LLM prompt doesn't specify a language, so GPT handles both. Pain keywords in `symptom_extractor.py` are English-only (limitation).

**Q31. What is the purpose of `__init__.py` files?**
They mark directories as Python packages, enabling `from pages import patient_registration` and `from database import db` style imports. Most are empty.

**Q32. Explain the consultation page's file upload mechanism.**
`st.file_uploader` accepts PDF, JPG, PNG, DCM files. Files are saved with UUID names to `uploads/reports/` using `generate_unique_filename()`. The path is stored in `consultation.uploaded_report_path`. Supported types are defined in the page's `allowed_types` parameter.

**Q33. How are patient IDs generated?**
Auto-incrementing integer primary key assigned by SQLite. No custom ID scheme — the `patient_id` is the database's internal sequential integer.

**Q34. Can the system work completely offline?**
Yes. SQLite is local. Faster-Whisper runs locally (model downloaded once). The only feature requiring internet is the OpenAI GPT analysis — and the system degrades gracefully without it, using rule-based analysis instead.

**Q35. What testing strategy is used?**
The project doesn't currently have automated tests. Testing is manual through the Streamlit UI. The seed data mechanism serves as a kind of integration test — if seed data loads without errors, the schema and CRUD functions work correctly.
