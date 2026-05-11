import streamlit as st
import os
from database.db import get_session
from database.crud import get_all_patients, create_consultation, get_consultations
from utils.constants import SPECIALIZATIONS
from utils.ui_helpers import show_success, show_error
from utils.helpers import generate_unique_filename
import pandas as pd


UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "reports")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def render():
    st.header("Consultation Entry")
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

    with st.form("consultation_form"):
        col1, col2 = st.columns(2)
        with col1:
            doctor_name = st.text_input("Doctor Name", value="Dr. Rajat")
            specialization = st.selectbox("Specialization", SPECIALIZATIONS)
            consultation_datetime = st.text_input("Date & Time", placeholder="DD-MM-YYYY HH:MM")
        with col2:
            followup_date = st.text_input("Follow-up Date", placeholder="DD-MM-YYYY")
            uploaded_file = st.file_uploader("Upload Report (PDF, MRI, X-ray)", type=["pdf", "jpg", "jpeg", "png", "dcm"])

        chief_complaint = st.text_area("Chief Complaint", placeholder="Patient's main complaint in their own words...")
        clinical_findings = st.text_area("Clinical Findings", placeholder="Physical examination findings...")
        examination_notes = st.text_area("Examination Notes", placeholder="Additional examination notes...")
        preliminary_diagnosis = st.text_area("Preliminary Diagnosis", placeholder="Working diagnosis...")
        recommended_scan = st.text_area("Recommended Scan / Tests", placeholder="MRI, X-ray, Blood tests...")

        submitted = st.form_submit_button("Save Consultation", type="primary", width='stretch')

        if submitted:
            report_path = None
            if uploaded_file:
                filename = generate_unique_filename(uploaded_file.name)
                report_path = os.path.join(UPLOAD_DIR, filename)
                with open(report_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            data = {
                "patient_id": patient_id,
                "doctor_name": doctor_name.strip() if doctor_name else None,
                "specialization": specialization,
                "consultation_datetime": consultation_datetime.strip() if consultation_datetime else None,
                "chief_complaint": chief_complaint.strip() if chief_complaint else None,
                "clinical_findings": clinical_findings.strip() if clinical_findings else None,
                "examination_notes": examination_notes.strip() if examination_notes else None,
                "preliminary_diagnosis": preliminary_diagnosis.strip() if preliminary_diagnosis else None,
                "recommended_scan": recommended_scan.strip() if recommended_scan else None,
                "uploaded_report_path": report_path,
                "followup_date": followup_date.strip() if followup_date else None,
            }
            db = get_session()
            try:
                create_consultation(db, data)
                show_success("Consultation saved!")
            except Exception as e:
                show_error(f"Error: {str(e)}")
            finally:
                db.close()

    db = get_session()
    try:
        consultations = get_consultations(db, patient_id)
        if consultations:
            st.subheader("Consultation History")
            for c in consultations:
                with st.expander(f"{c.consultation_datetime or 'N/A'} - {c.preliminary_diagnosis or 'No diagnosis'}"):
                    st.write(f"**Doctor:** {c.doctor_name or 'N/A'} ({c.specialization or 'N/A'})")
                    st.write(f"**Complaint:** {c.chief_complaint or 'N/A'}")
                    st.write(f"**Findings:** {c.clinical_findings or 'N/A'}")
                    st.write(f"**Diagnosis:** {c.preliminary_diagnosis or 'N/A'}")
                    st.write(f"**Follow-up:** {c.followup_date or 'N/A'}")
                    if c.uploaded_report_path and os.path.exists(c.uploaded_report_path):
                        st.write(f"[View Report]({c.uploaded_report_path})")
    finally:
        db.close()
