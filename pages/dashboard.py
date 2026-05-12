import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db import get_session
from database.crud import (
    get_all_patients, get_pain_assessments, get_progress, search_patients,
    get_consultations, get_treatments, get_conversations
)

from database.models import Patient, Treatment, Conversation


def render():
    st.header("Dashboard / History")
    db = get_session()
    try:
        patients = get_all_patients(db)
    finally:
        db.close()

    if not patients:
        st.warning("No patients in the system.")
        return

    st.subheader("Search Patients")
    col1, col2, col3 = st.columns(3)
    with col1:
        search_id = st.text_input("Patient ID", placeholder="Enter ID")
    with col2:
        search_name = st.text_input("Name", placeholder="Search by name")
    with col3:
        search_mobile = st.text_input("Mobile", placeholder="Search by mobile")

    selected_patient = None
    db = get_session()
    try:
        if search_id and search_id.isdigit():
            patient = db.query(Patient).filter(Patient.patient_id == int(search_id)).first()
            if patient:
                selected_patient = patient
        elif search_name:
            results = search_patients(db, search_name)
            if results:
                selected_patient = results[0]
        elif search_mobile:
            results = search_patients(db, search_mobile)
            if results:
                selected_patient = results[0]
    finally:
        db.close()

    if not selected_patient:
        patient_dict = {f"{p.patient_id} - {p.full_name} ({p.mobile})": p for p in patients}
        selected_label = st.selectbox("Or select a patient", list(patient_dict.keys()))
        selected_patient = patient_dict[selected_label]

    if selected_patient:
        render_patient_dashboard(selected_patient)


def render_patient_dashboard(patient):
    db = get_session()
    try:
        assessments = get_pain_assessments(db, patient.patient_id)
        consultations = get_consultations(db, patient.patient_id)
        progress_entries = get_progress(db, patient.patient_id)
    finally:
        db.close()

    col1, col2, col3, col4 = st.columns(4)
    latest_pain = assessments[0].pain_severity if assessments else None
    latest_pain_display = f"{latest_pain}/10" if latest_pain is not None else "N/A"
    with col1:
        st.metric("Current Pain Score", latest_pain_display)
    with col2:
        st.metric("Session Count", len(progress_entries))
    with col3:
        latest_diag = consultations[0].preliminary_diagnosis if consultations else None
        latest_diag_display = latest_diag or "N/A"
        st.metric("Latest Diagnosis", latest_diag_display[:30] + "..." if len(str(latest_diag_display)) > 30 else latest_diag_display)
    with col4:
        if progress_entries:
            first = progress_entries[-1]
            last = progress_entries[0]
            first_score = first.current_pain_score if first.current_pain_score is not None else (first.previous_pain_score or 0)
            last_score = last.current_pain_score if last.current_pain_score is not None else 0
            diff = first_score - last_score
            status = "Improving" if diff > 0 else "Stable" if diff == 0 else "Worsening"
            st.metric("Recovery Status", status, delta=f"{diff:+d}" if diff != 0 else None)
        else:
            st.metric("Recovery Status", "No data")

    st.subheader("Patient Info")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write(f"**Name:** {patient.full_name}")
        st.write(f"**Age/Gender:** {patient.age}/{patient.gender}")
        st.write(f"**Mobile:** {patient.mobile}")
    with c2:
        st.write(f"**BMI:** {patient.bmi or 'N/A'}")
        st.write(f"**Lifestyle:** {patient.lifestyle or 'N/A'}")
        st.write(f"**Occupation:** {patient.occupation or 'N/A'}")
    with c3:
        st.write(f"**Existing Diseases:** {patient.existing_diseases or 'None'}")
        st.write(f"**Previous Surgery:** {patient.previous_spine_surgery or 'No'}")

    if progress_entries:
        st.subheader("Pain Trend")
        rows = []
        for i, p in enumerate(reversed(progress_entries)):
            if p.previous_pain_score is None and p.current_pain_score is None:
                continue
            rows.append({
                "session": p.session_number or i + 1,
                "previous": p.previous_pain_score,
                "current": p.current_pain_score,
                "date": p.progress_date or "",
            })

        if rows:
            progress_df = pd.DataFrame(rows)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=progress_df["session"], y=progress_df["previous"],
                mode="lines+markers", name="Previous Pain",
                line=dict(color="orange", width=2),
            ))
            fig.add_trace(go.Scatter(
                x=progress_df["session"], y=progress_df["current"],
                mode="lines+markers", name="Current Pain",
                line=dict(color="green", width=2),
            ))
            fig.update_layout(
                title="Pain Score Trend Across Sessions",
                xaxis_title="Session Number",
                yaxis_title="Pain Score (0-10)",
                yaxis=dict(range=[0, 10]),
                height=400,
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No pain score data available for chart.")

        if len(progress_entries) >= 2:
            st.subheader("Improvement Radar")
            last_entry = progress_entries[0]
            radar_data = {
                "Metric": ["Pain Reduction", "Mobility", "Sleep", "Numbness"],
                "Score": [
                    min(10, max(0, 10 - (last_entry.current_pain_score or 0))),
                    {"No Change": 2, "Slight Improvement": 4, "Improved": 6, "Significantly Improved": 9}.get(last_entry.mobility_improvement or "No Change", 2),
                    {"No Change": 2, "Slight Improvement": 4, "Improved": 6, "Significantly Improved": 9}.get(last_entry.sleep_improvement or "No Change", 2),
                    {"No Change": 2, "Slight Improvement": 4, "Improved": 6, "Significantly Improved": 9}.get(last_entry.numbness_improvement or "No Change", 2),
                ],
            }
            fig2 = px.line_polar(radar_data, r="Score", theta="Metric", line_close=True, range_r=[0, 10])
            fig2.update_traces(fill="toself", line_color="#2563eb")
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, width='stretch')

    if consultations:
        st.subheader("Consultations")
        consult_ids = [c.consultation_id for c in consultations]
        db_batch = get_session()
        try:
            all_treatments = db_batch.query(Treatment).filter(Treatment.consultation_id.in_(consult_ids)).all()
            all_conversations = db_batch.query(Conversation).filter(Conversation.consultation_id.in_(consult_ids)).all()
        finally:
            db_batch.close()

        treatments_by_consult = {}
        for t in all_treatments:
            treatments_by_consult.setdefault(t.consultation_id, []).append(t)
        convs_by_consult = {}
        for conv in all_conversations:
            convs_by_consult.setdefault(conv.consultation_id, []).append(conv)

        for c in consultations:
            with st.expander(f"{c.consultation_datetime or 'N/A'} - {c.preliminary_diagnosis or 'No diagnosis'}"):
                st.write(f"**Doctor:** {c.doctor_name or 'N/A'}")
                st.write(f"**Complaint:** {c.chief_complaint or 'N/A'}")
                st.write(f"**Findings:** {c.clinical_findings or 'N/A'}")
                st.write(f"**Diagnosis:** {c.preliminary_diagnosis or 'N/A'}")
                st.write(f"**Follow-up:** {c.followup_date or 'N/A'}")

                treatments_list = treatments_by_consult.get(c.consultation_id, [])
                if treatments_list:
                    st.write("**Treatments:**")
                    for t in treatments_list:
                        st.write(f"- {t.therapy_types} | Outcome: {t.session_outcome or 'N/A'}")

                conversations = convs_by_consult.get(c.consultation_id, [])
                if conversations:
                    st.write("**Conversations:**")
                    for conv in conversations:
                        st.write(f"- {conv.source_type} ({conv.language}) | Keywords: {conv.pain_keywords or 'N/A'}")
                        if conv.transcript:
                            with st.expander("View Transcript"):
                                st.text(conv.transcript[:1000] + ("..." if len(conv.transcript) > 1000 else ""))

    if assessments:
        st.subheader("Pain Assessment History")
        data = [{
            "Date": a.created_at.strftime("%d-%m-%Y") if a.created_at else "",
            "Severity": f"{a.pain_severity}/10" if a.pain_severity is not None else "-",
            "Areas": a.pain_areas or "-",
            "Duration": a.duration or "-",
            "Numbness": a.numbness or "-",
        } for a in assessments]
        st.dataframe(pd.DataFrame(data), width='stretch', hide_index=True)

        fig3 = px.bar(
            pd.DataFrame([{"date": a.created_at.strftime("%d-%m-%Y") if a.created_at else f"#{i+1}", "severity": a.pain_severity or 0} for i, a in enumerate(assessments[::-1])]),
            x="date", y="severity", title="Pain Severity Over Time",
            labels={"date": "Date", "severity": "Pain Level"},
            color="severity", color_continuous_scale="RdYlGn_r",
            range_y=[0, 10],
        )
        fig3.update_layout(height=350)
        st.plotly_chart(fig3, width='stretch')
