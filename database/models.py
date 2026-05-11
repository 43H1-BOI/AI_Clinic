from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.db import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(200), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    dob = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    occupation = Column(String(200), nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    address = Column(Text, nullable=True)
    lifestyle = Column(String(100), nullable=True)
    smoking_alcohol = Column(String(100), nullable=True)
    existing_diseases = Column(Text, nullable=True)
    previous_spine_surgery = Column(String(10), nullable=True)
    emergency_contact = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pain_assessments = relationship("PainAssessment", back_populates="patient", cascade="all, delete-orphan")
    progress_trackings = relationship("ProgressTracking", back_populates="patient", cascade="all, delete-orphan")


class PainAssessment(Base):
    __tablename__ = "pain_assessments"

    assessment_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    main_problem = Column(String(500), nullable=True)
    pain_areas = Column(Text, nullable=True)
    spine_level = Column(String(200), nullable=True)
    pain_severity = Column(Integer, nullable=True)
    pain_type = Column(String(100), nullable=True)
    duration = Column(String(100), nullable=True)
    triggering_activity = Column(Text, nullable=True)
    movement_limitation = Column(Text, nullable=True)
    numbness = Column(String(10), nullable=True)
    muscle_weakness = Column(String(10), nullable=True)
    nerve_radiation = Column(String(10), nullable=True)
    sleep_disturbance = Column(String(10), nullable=True)
    posture_problem = Column(String(200), nullable=True)
    stress_level = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="pain_assessments")


class Consultation(Base):
    __tablename__ = "consultations"

    consultation_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    doctor_name = Column(String(200), nullable=True)
    specialization = Column(String(200), nullable=True)
    consultation_datetime = Column(String(30), nullable=True)
    chief_complaint = Column(Text, nullable=True)
    clinical_findings = Column(Text, nullable=True)
    examination_notes = Column(Text, nullable=True)
    preliminary_diagnosis = Column(Text, nullable=True)
    recommended_scan = Column(Text, nullable=True)
    uploaded_report_path = Column(String(500), nullable=True)
    followup_date = Column(String(20), nullable=True)

    treatments = relationship("Treatment", back_populates="consultation", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="consultation", cascade="all, delete-orphan")


class Treatment(Base):
    __tablename__ = "treatments"

    treatment_id = Column(Integer, primary_key=True, autoincrement=True)
    consultation_id = Column(Integer, ForeignKey("consultations.consultation_id"), nullable=False)
    therapy_types = Column(Text, nullable=True)
    chiropractic_area = Column(String(200), nullable=True)
    soft_tissue_therapy = Column(Text, nullable=True)
    nerve_handling = Column(Text, nullable=True)
    muscle_therapy = Column(Text, nullable=True)
    bone_alignment = Column(Text, nullable=True)
    ayurveda_medicine = Column(Text, nullable=True)
    panchakarma_type = Column(String(200), nullable=True)
    oil_used = Column(String(200), nullable=True)
    home_exercise = Column(Text, nullable=True)
    posture_advice = Column(Text, nullable=True)
    session_duration = Column(Integer, nullable=True)
    session_outcome = Column(Text, nullable=True)

    consultation = relationship("Consultation", back_populates="treatments")


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id = Column(Integer, primary_key=True, autoincrement=True)
    consultation_id = Column(Integer, ForeignKey("consultations.consultation_id"), nullable=False)
    source_type = Column(String(50), nullable=True)
    audio_path = Column(String(500), nullable=True)
    transcript = Column(Text, nullable=True)
    language = Column(String(50), nullable=True)
    speaker_separation = Column(Text, nullable=True)
    emotional_state = Column(String(200), nullable=True)
    pain_keywords = Column(Text, nullable=True)
    additional_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    consultation = relationship("Consultation", back_populates="conversations")
    ai_outputs = relationship("AIOutput", back_populates="conversation", cascade="all, delete-orphan")


class AIOutput(Base):
    __tablename__ = "ai_outputs"

    ai_result_id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.conversation_id"), nullable=False)
    ai_summary = Column(Text, nullable=True)
    extracted_symptoms = Column(Text, nullable=True)
    body_area_detected = Column(String(500), nullable=True)
    possible_condition = Column(String(500), nullable=True)
    predicted_pain_severity = Column(Integer, nullable=True)
    recommended_therapy = Column(Text, nullable=True)
    recommended_tests = Column(Text, nullable=True)
    suggested_ayurveda = Column(Text, nullable=True)
    risk_level = Column(String(50), nullable=True)
    surgery_probability = Column(String(50), nullable=True)
    recovery_prediction = Column(Text, nullable=True)
    followup_suggestion = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    raw_json = Column(Text, nullable=True)

    conversation = relationship("Conversation", back_populates="ai_outputs")


class ProgressTracking(Base):
    __tablename__ = "progress_tracking"

    progress_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    session_number = Column(Integer, nullable=True)
    progress_date = Column(String(20), nullable=True)
    previous_pain_score = Column(Integer, nullable=True)
    current_pain_score = Column(Integer, nullable=True)
    mobility_improvement = Column(String(50), nullable=True)
    sleep_improvement = Column(String(50), nullable=True)
    numbness_improvement = Column(String(50), nullable=True)
    patient_feedback = Column(Text, nullable=True)
    practitioner_remark = Column(Text, nullable=True)

    patient = relationship("Patient", back_populates="progress_trackings")
