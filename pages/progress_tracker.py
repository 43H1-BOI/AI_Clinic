import streamlit as st
from database.db import get_session
from database.crud import get_all_patients, get_pain_assessments, create_progress, get_progress
from utils.ui_helpers import show_success, show_error
from utils.helpers import get_today_date
import pandas as pd


def render():
    st.header("Progress Tracker")
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
        assessments = get_pain_assessments(db, patient_id)
        previous_entries = get_progress(db, patient_id)
    finally:
        db.close()

    last_pain_score = 0
    session_count = len(previous_entries) + 1
    if assessments and assessments[0].pain_severity is not None:
        last_pain_score = assessments[0].pain_severity
    if previous_entries:
        last_entry = previous_entries[0]
        if last_entry.current_pain_score is not None:
            last_pain_score = last_entry.current_pain_score
        session_count = (last_entry.session_number + 1) if last_entry.session_number is not None else len(previous_entries) + 1

    st.subheader(f"Session #{session_count}")
    with st.form("progress_form"):
        col1, col2 = st.columns(2)
        with col1:
            previous_pain_score = st.number_input("Previous Pain Score (0-10)", value=last_pain_score, min_value=0, max_value=10, step=1)
            current_pain_score = st.slider("Current Pain Score (0-10)", 0, 10, last_pain_score)
            progress_date = st.text_input("Date", value=get_today_date())
        with col2:
            mobility_improvement = st.selectbox("Mobility Improvement", ["", "No Change", "Slight Improvement", "Improved", "Significantly Improved"])
            sleep_improvement = st.selectbox("Sleep Improvement", ["", "No Change", "Slight Improvement", "Improved", "Significantly Improved"])
            numbness_improvement = st.selectbox("Numbness Improvement", ["", "No Change", "Slight Improvement", "Improved", "Significantly Improved"])

        patient_feedback = st.text_area("Patient Feedback", placeholder="What does the patient say?")
        practitioner_remark = st.text_area("Practitioner Remark", placeholder="Clinical observation and remarks")

        submitted = st.form_submit_button("Save Progress", type="primary", width='stretch')

        if submitted:
            data = {
                "patient_id": patient_id,
                "session_number": session_count,
                "progress_date": progress_date.strip() if progress_date else get_today_date(),
                "previous_pain_score": previous_pain_score,
                "current_pain_score": current_pain_score,
                "mobility_improvement": mobility_improvement if mobility_improvement else None,
                "sleep_improvement": sleep_improvement if sleep_improvement else None,
                "numbness_improvement": numbness_improvement if numbness_improvement else None,
                "patient_feedback": patient_feedback.strip() if patient_feedback else None,
                "practitioner_remark": practitioner_remark.strip() if practitioner_remark else None,
            }
            db = get_session()
            try:
                existing_progress = get_progress(db, patient_id)
                if any(p.session_number == session_count for p in existing_progress):
                    show_error(f"Session #{session_count} already exists. Refresh the page to continue.")
                else:
                    create_progress(db, data)
                    show_success("Progress saved!")
            except Exception as e:
                show_error(f"Error: {str(e)}")
            finally:
                db.close()

    if previous_entries:
        st.subheader("Progress History")
        data = [{
            "Session": p.session_number or "-",
            "Date": p.progress_date or "",
            "Previous Pain": f"{p.previous_pain_score}/10" if p.previous_pain_score is not None else "-",
            "Current Pain": f"{p.current_pain_score}/10" if p.current_pain_score is not None else "-",
            "Mobility": p.mobility_improvement or "-",
            "Sleep": p.sleep_improvement or "-",
            "Numbness": p.numbness_improvement or "-",
        } for p in previous_entries]
        df = pd.DataFrame(data)
        st.dataframe(df, width='stretch', hide_index=True)

        first_entry = previous_entries[-1]
        last_entry = previous_entries[0]
        first_score = first_entry.current_pain_score if first_entry.current_pain_score is not None else 0
        last_score = last_entry.current_pain_score if last_entry.current_pain_score is not None else 0
        improvement = first_score - last_score
        if improvement > 0:
            st.metric("Pain Reduction", f"-{improvement}/10", delta=f"↓ {improvement}")
        elif improvement < 0:
            st.metric("Pain Increase", f"+{abs(improvement)}/10", delta=f"↑ {abs(improvement)}", delta_color="inverse")
