from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class PatientCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., pattern="^(Male|Female|Other)$")
    dob: Optional[str] = None
    mobile: str = Field(..., min_length=10, max_length=20)
    email: Optional[str] = None
    occupation: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    address: Optional[str] = None
    lifestyle: Optional[str] = None
    smoking_alcohol: Optional[str] = None
    existing_diseases: Optional[str] = None
    previous_spine_surgery: Optional[str] = None
    emergency_contact: Optional[str] = None

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v):
        digits = "".join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError("Mobile must have at least 10 digits")
        return v


class PainAssessmentCreate(BaseModel):
    patient_id: int
    main_problem: Optional[str] = None
    pain_areas: Optional[str] = None
    spine_level: Optional[str] = None
    pain_severity: Optional[int] = Field(None, ge=0, le=10)
    pain_type: Optional[str] = None
    duration: Optional[str] = None
    triggering_activity: Optional[str] = None
    movement_limitation: Optional[str] = None
    numbness: Optional[str] = None
    muscle_weakness: Optional[str] = None
    nerve_radiation: Optional[str] = None
    sleep_disturbance: Optional[str] = None
    posture_problem: Optional[str] = None
    stress_level: Optional[str] = None


class ConsultationCreate(BaseModel):
    patient_id: int
    doctor_name: Optional[str] = None
    specialization: Optional[str] = None
    consultation_datetime: Optional[str] = None
    chief_complaint: Optional[str] = None
    clinical_findings: Optional[str] = None
    examination_notes: Optional[str] = None
    preliminary_diagnosis: Optional[str] = None
    recommended_scan: Optional[str] = None
    followup_date: Optional[str] = None


class TreatmentCreate(BaseModel):
    consultation_id: int
    therapy_types: Optional[str] = None
    chiropractic_area: Optional[str] = None
    soft_tissue_therapy: Optional[str] = None
    nerve_handling: Optional[str] = None
    muscle_therapy: Optional[str] = None
    bone_alignment: Optional[str] = None
    ayurveda_medicine: Optional[str] = None
    panchakarma_type: Optional[str] = None
    oil_used: Optional[str] = None
    home_exercise: Optional[str] = None
    posture_advice: Optional[str] = None
    session_duration: Optional[int] = None
    session_outcome: Optional[str] = None


class ConversationCreate(BaseModel):
    consultation_id: int
    source_type: Optional[str] = None
    audio_path: Optional[str] = None
    transcript: Optional[str] = None
    language: Optional[str] = None
    speaker_separation: Optional[str] = None
    emotional_state: Optional[str] = None
    pain_keywords: Optional[str] = None
    additional_notes: Optional[str] = None


class AIOutputCreate(BaseModel):
    conversation_id: int
    ai_summary: Optional[str] = None
    extracted_symptoms: Optional[str] = None
    body_area_detected: Optional[str] = None
    possible_condition: Optional[str] = None
    predicted_pain_severity: Optional[int] = None
    recommended_therapy: Optional[str] = None
    recommended_tests: Optional[str] = None
    suggested_ayurveda: Optional[str] = None
    risk_level: Optional[str] = None
    surgery_probability: Optional[str] = None
    recovery_prediction: Optional[str] = None
    followup_suggestion: Optional[str] = None
    confidence_score: Optional[float] = None
    raw_json: Optional[str] = None


class ProgressTrackingCreate(BaseModel):
    patient_id: int
    session_number: Optional[int] = None
    progress_date: Optional[str] = None
    previous_pain_score: Optional[int] = None
    current_pain_score: Optional[int] = Field(None, ge=0, le=10)
    mobility_improvement: Optional[str] = None
    sleep_improvement: Optional[str] = None
    numbness_improvement: Optional[str] = None
    patient_feedback: Optional[str] = None
    practitioner_remark: Optional[str] = None


class AIAnalysisInput(BaseModel):
    transcript: str
    consultation_notes: Optional[str] = None
    assessment_data: Optional[str] = None


class AIAnalysisOutput(BaseModel):
    summary: str = ""
    symptoms: list[str] = []
    possible_condition: str = ""
    risk_level: str = "LOW"
    recommended_therapy: list = []
    recommended_tests: list = []
    pain_severity: int = 0
    recovery_prediction: str = ""
    followup: str = ""
    confidence_score: float = 0.0
