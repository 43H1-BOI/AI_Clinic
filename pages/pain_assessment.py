import streamlit as st
from database.db import get_session
from database.crud import get_all_patients, create_pain_assessment, get_pain_assessments
from utils.constants import PAIN_AREAS, SPINE_LEVELS, PAIN_TYPES, PAIN_DURATIONS, STRESS_LEVELS
from utils.ui_helpers import show_success, show_error
import pandas as pd


def render():
    st.header("Pain Assessment")
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

    with st.form("pain_form"):
        st.subheader("Pain Details")
        main_problem = st.text_area("Main Problem", placeholder="Describe the main problem...")
        col1, col2 = st.columns(2)
        with col1:
            pain_areas = st.multiselect("Pain Areas", PAIN_AREAS)
            spine_level = st.multiselect("Spine Level(s)", SPINE_LEVELS)
            pain_severity = st.slider("Pain Severity", 0, 10, 5)
            pain_type = st.selectbox("Pain Type", [""] + PAIN_TYPES)
        with col2:
            duration = st.selectbox("Duration", [""] + PAIN_DURATIONS)
            triggering_activity = st.text_area("Triggering Activity", placeholder="What makes it worse?")
            movement_limitation = st.text_area("Movement Limitation", placeholder="Any restriction in movement?")

        st.subheader("Associated Symptoms")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            numbness = st.selectbox("Numbness", ["", "No", "Yes"])
        with c2:
            muscle_weakness = st.selectbox("Muscle Weakness", ["", "No", "Yes"])
        with c3:
            nerve_radiation = st.selectbox("Nerve Radiation", ["", "No", "Yes"])
        with c4:
            sleep_disturbance = st.selectbox("Sleep Disturbance", ["", "No", "Yes"])

        col1, col2 = st.columns(2)
        with col1:
            posture_problem = st.text_input("Posture Problem", placeholder="e.g., Forward head, Anterior pelvic tilt")
        with col2:
            stress_level = st.selectbox("Stress Level", [""] + STRESS_LEVELS)

        submitted = st.form_submit_button("Save Assessment", type="primary", width='stretch')

        if submitted:
            data = {
                "patient_id": patient_id,
                "main_problem": main_problem.strip() if main_problem else None,
                "pain_areas": ", ".join(pain_areas) if pain_areas else None,
                "spine_level": ", ".join(spine_level) if spine_level else None,
                "pain_severity": pain_severity,
                "pain_type": pain_type if pain_type else None,
                "duration": duration if duration else None,
                "triggering_activity": triggering_activity.strip() if triggering_activity else None,
                "movement_limitation": movement_limitation.strip() if movement_limitation else None,
                "numbness": numbness if numbness else None,
                "muscle_weakness": muscle_weakness if muscle_weakness else None,
                "nerve_radiation": nerve_radiation if nerve_radiation else None,
                "sleep_disturbance": sleep_disturbance if sleep_disturbance else None,
                "posture_problem": posture_problem.strip() if posture_problem else None,
                "stress_level": stress_level if stress_level else None,
            }
            db = get_session()
            try:
                create_pain_assessment(db, data)
                show_success("Pain assessment saved!")
            except Exception as e:
                show_error(f"Error: {str(e)}")
            finally:
                db.close()

    db = get_session()
    try:
        assessments = get_pain_assessments(db, patient_id)
        if assessments:
            st.subheader("Previous Assessments")
            data = [{
                "Date": a.created_at.strftime("%d-%m-%Y") if a.created_at else "",
                "Pain Level": f"{a.pain_severity}/10" if a.pain_severity is not None else "-",
                "Areas": a.pain_areas or "-",
                "Type": a.pain_type or "-",
                "Duration": a.duration or "-",
                "Numbness": a.numbness or "-",
            } for a in assessments]
            st.dataframe(pd.DataFrame(data), width='stretch', hide_index=True)
    finally:
        db.close()
