from sqlalchemy.orm import Session
from sqlalchemy import or_, String
from database.models import Patient, PainAssessment, Consultation, Treatment, Conversation, AIOutput, ProgressTracking


def calculate_bmi(height_cm, weight_kg):
    """Calculate BMI.

    Accepts height in centimeters or meters (auto-detects meters when value < 3).
    Coerces numeric-like inputs (strings) to float and returns None for invalid inputs.
    """
    try:
        if height_cm is None or weight_kg is None:
            return None
        h = float(height_cm)
        w = float(weight_kg)
    except (TypeError, ValueError):
        return None

    if h <= 0 or w <= 0:
        return None

    # If height looks like meters (e.g., 1.7) treat as meters; otherwise treat as cm
    if h < 3:
        height_m = h
    else:
        height_m = h / 100.0

    try:
        bmi = w / (height_m * height_m)
    except ZeroDivisionError:
        return None

    return round(bmi, 1)


def create_patient(db: Session, data: dict):
    if data.get("height") and data.get("weight"):
        data["bmi"] = calculate_bmi(data["height"], data["weight"])
    patient = Patient(**data)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def update_patient(db: Session, patient_id: int, data: dict):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        return None
    if data.get("height") and data.get("weight"):
        data["bmi"] = calculate_bmi(data["height"], data["weight"])
    for key, value in data.items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: Session, patient_id: int):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if patient:
        db.delete(patient)
        db.commit()
        return True
    return False


def get_patient(db: Session, patient_id: int):
    return db.query(Patient).filter(Patient.patient_id == patient_id).first()


def get_all_patients(db: Session):
    return db.query(Patient).order_by(Patient.created_at.desc()).all()


def search_patients(db: Session, query: str):
    q = f"%{query}%"
    return db.query(Patient).filter(
        or_(
            Patient.full_name.ilike(q),
            Patient.mobile.ilike(q),
            Patient.patient_id.cast(String).like(q),
        )
    ).all()


def create_pain_assessment(db: Session, data: dict):
    assessment = PainAssessment(**data)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_pain_assessments(db: Session, patient_id: int):
    return db.query(PainAssessment).filter(
        PainAssessment.patient_id == patient_id
    ).order_by(PainAssessment.created_at.desc()).all()


def create_consultation(db: Session, data: dict):
    consultation = Consultation(**data)
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation


def get_consultations(db: Session, patient_id: int):
    return db.query(Consultation).filter(
        Consultation.patient_id == patient_id
    ).order_by(Consultation.consultation_id.desc()).all()


def get_consultation(db: Session, consultation_id: int):
    return db.query(Consultation).filter(
        Consultation.consultation_id == consultation_id
    ).first()


def create_treatment(db: Session, data: dict):
    treatment = Treatment(**data)
    db.add(treatment)
    db.commit()
    db.refresh(treatment)
    return treatment


def get_treatments(db: Session, consultation_id: int):
    return db.query(Treatment).filter(
        Treatment.consultation_id == consultation_id
    ).all()


def create_conversation(db: Session, data: dict):
    conversation = Conversation(**data)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversations(db: Session, consultation_id: int):
    return db.query(Conversation).filter(
        Conversation.consultation_id == consultation_id
    ).order_by(Conversation.created_at.desc()).all()


def create_ai_output(db: Session, data: dict):
    output = AIOutput(**data)
    db.add(output)
    db.commit()
    db.refresh(output)
    return output


def get_ai_outputs(db: Session, conversation_id: int):
    return db.query(AIOutput).filter(
        AIOutput.conversation_id == conversation_id
    ).all()


def create_progress(db: Session, data: dict):
    progress = ProgressTracking(**data)
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


def get_progress(db: Session, patient_id: int):
    return db.query(ProgressTracking).filter(
        ProgressTracking.patient_id == patient_id
    ).order_by(ProgressTracking.session_number.desc()).all()


def get_all_consultations(db: Session):
    return db.query(Consultation).order_by(Consultation.consultation_datetime.desc()).all()


def get_all_conversations(db: Session):
    return db.query(Conversation).order_by(Conversation.created_at.desc()).all()


def get_all_treatments(db: Session):
    return db.query(Treatment).all()
