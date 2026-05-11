# Dr Rajat AI Clinic

AI-powered clinical management platform for chiropractic, osteopathy, Ayurveda, and spine care.

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python 3.12
- **Database:** SQLite + SQLAlchemy ORM
- **AI:** Faster-Whisper, OpenAI GPT-4o-mini
- **Visualization:** Plotly
- **Validation:** Pydantic

## Features

- **Patient Management:** Registration, edit, delete, search, auto-BMI calculation
- **Pain Assessment:** Pain scoring, multi-select pain areas, spine level mapping
- **Consultation:** Clinical notes, diagnosis, report uploads, follow-up scheduling
- **Treatment:** Multi-therapy tracking, Ayurveda/Panchakarma support, exercise prescription
- **Conversation Capture:** Audio upload + Faster-Whisper transcription, Hindi/English support
- **AI Analysis:** Rule-based risk engine + GPT-4o-mini summarization, symptom extraction
- **Progress Tracking:** Session-wise tracking, pain trends, improvement metrics
- **Dashboard:** Charts, pain trends, recovery radar, full patient history

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your-openai-api-key-here
```

The app runs without an API key (falls back to rule-based analysis).

## Run

```bash
streamlit run app.py
```

## Project Structure

```
dr_rajat_ai_clinic/
├── app.py                 # Main entry
├── requirements.txt
├── README.md
├── .env
├── database/
│   ├── db.py             # DB connection
│   ├── models.py         # ORM models
│   ├── crud.py           # CRUD operations
│   ├── schema.py         # Pydantic schemas
│   └── seed_data.py      # Sample data
├── pages/
│   ├── patient_registration.py
│   ├── pain_assessment.py
│   ├── consultation.py
│   ├── treatment.py
│   ├── conversation.py
│   ├── ai_analysis.py
│   ├── progress_tracker.py
│   └── dashboard.py
├── ai/
│   ├── whisper_service.py
│   ├── llm_service.py
│   ├── risk_engine.py
│   ├── symptom_extractor.py
│   └── prompts.py
├── utils/
│   ├── validators.py
│   ├── constants.py
│   ├── helpers.py
│   └── ui_helpers.py
└── uploads/
    ├── audio/
    ├── reports/
    └── transcripts/
```

## Deployment

- **Local:** `streamlit run app.py`
- **Streamlit Cloud:** Connect GitHub repo and deploy
- **Docker:** Build and run container

## Future Scope

- PostgreSQL migration
- FastAPI backend
- React frontend
- ML models for prediction
- Multi-language support
- Video consultation integration
