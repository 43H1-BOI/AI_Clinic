import streamlit as st
from database.db import get_session
from database.crud import get_all_patients, get_consultations, create_treatment, get_treatments
from utils.constants import THERAPY_TYPES, CHIROPRACTIC_AREAS, PANCHAKARMA_TYPES, OILS
from utils.ui_helpers import show_success, show_error
import pandas as pd


def render():
    st.header("Treatment Session")
    db = get_session()
    try:
        patients = get_all_patients(db)
    finally:
        db.close()

    if not patients:
        st.warning("Register a patient first.")
        return

    patient_dict = {f"{p.patient_id} - {p.full_name} ({p.mobile})": p.patient_id for p in patients}
    selected = st.selectbox("Select Patient", list(patient_dict.keys()))
    patient_id = patient_dict[selected]

    db = get_session()
    try:
        consultations = get_consultations(db, patient_id)
    finally:
        db.close()

    if not consultations:
        st.warning("Create a consultation first.")
        return

    consult_dict = {f"{c.consultation_id} - {c.consultation_datetime or 'N/A'}": c.consultation_id for c in consultations}
    consult_selected = st.selectbox("Select Consultation", list(consult_dict.keys()))
    consultation_id = consult_dict[consult_selected]

    with st.form("treatment_form"):
        st.subheader("Therapy Details")
        therapy_types = st.multiselect("Therapy Types", THERAPY_TYPES)
        col1, col2 = st.columns(2)
        with col1:
            chiropractic_area = st.multiselect("Chiropractic Area(s)", CHIROPRACTIC_AREAS)
            session_duration = st.number_input("Session Duration (minutes)", min_value=5, max_value=180, value=30, step=5)
        with col2:
            panchakarma_type = st.selectbox("Panchakarma Type", [""] + PANCHAKARMA_TYPES)
            oil_used = st.selectbox("Oil Used", [""] + OILS)

        soft_tissue_therapy = st.text_area("Soft Tissue Therapy", placeholder="Myofascial release, trigger point therapy...")
        nerve_handling = st.text_area("Nerve Handling", placeholder="Nerve flossing, slider exercises...")
        muscle_therapy = st.text_area("Muscle Therapy", placeholder="Strengthening, activation exercises...")
        bone_alignment = st.text_area("Bone Alignment", placeholder="Adjustments, manipulations...")
        ayurveda_medicine = st.text_area("Ayurveda Medicine", placeholder="Medicines prescribed...")
        home_exercise = st.text_area("Home Exercise Program", placeholder="Exercises prescribed for home...")
        posture_advice = st.text_area("Posture Advice", placeholder="Postural corrections, ergonomic advice...")
        session_outcome = st.text_area("Session Outcome", placeholder="How did the patient respond?")

        submitted = st.form_submit_button("Save Treatment", type="primary", width='stretch')

        if submitted:
            data = {
                "consultation_id": consultation_id,
                "therapy_types": ", ".join(therapy_types) if therapy_types else None,
                "chiropractic_area": ", ".join(chiropractic_area) if chiropractic_area else None,
                "soft_tissue_therapy": soft_tissue_therapy.strip() if soft_tissue_therapy else None,
                "nerve_handling": nerve_handling.strip() if nerve_handling else None,
                "muscle_therapy": muscle_therapy.strip() if muscle_therapy else None,
                "bone_alignment": bone_alignment.strip() if bone_alignment else None,
                "ayurveda_medicine": ayurveda_medicine.strip() if ayurveda_medicine else None,
                "panchakarma_type": panchakarma_type if panchakarma_type else None,
                "oil_used": oil_used if oil_used else None,
                "home_exercise": home_exercise.strip() if home_exercise else None,
                "posture_advice": posture_advice.strip() if posture_advice else None,
                "session_duration": session_duration,
                "session_outcome": session_outcome.strip() if session_outcome else None,
            }
            db = get_session()
            try:
                create_treatment(db, data)
                show_success("Treatment session saved!")
            except Exception as e:
                show_error(f"Error: {str(e)}")
            finally:
                db.close()

    db = get_session()
    try:
        treatments = get_treatments(db, consultation_id)
        if treatments:
            st.subheader("Treatment Records")
            for t in treatments:
                with st.expander(f"Treatment #{t.treatment_id} - {t.therapy_types or 'N/A'}"):
                    st.write(f"**Therapies:** {t.therapy_types or 'N/A'}")
                    st.write(f"**Chiropractic:** {t.chiropractic_area or 'N/A'}")
                    st.write(f"**Soft Tissue:** {t.soft_tissue_therapy or 'N/A'}")
                    st.write(f"**Exercises:** {t.home_exercise or 'N/A'}")
                    st.write(f"**Outcome:** {t.session_outcome or 'N/A'}")
    finally:
        db.close()
