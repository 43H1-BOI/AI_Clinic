import streamlit as st
import json
from database.db import get_session
from database.crud import (
    get_all_patients, get_consultations, get_conversations,
    create_ai_output, get_ai_outputs, get_pain_assessments
)
from ai.llm_service import analyze_with_llm
from ai.risk_engine import assess_risk
from utils.ui_helpers import show_success, show_error, show_warning
import pandas as pd


def render():
    st.header("AI Analysis")
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

    db = get_session()
    try:
        conversations = get_conversations(db, consultation_id)
    finally:
        db.close()

    if not conversations:
        st.warning("No conversations found. Upload a conversation first.")
        return

    conv_dict = {f"{c.conversation_id} - {c.created_at.strftime('%d-%m-%Y %H:%M') if c.created_at else 'N/A'}": c.conversation_id for c in conversations}
    conv_selected = st.selectbox("Select Conversation", list(conv_dict.keys()))
    conversation_id = conv_dict[conv_selected]

    selected_conv = next((c for c in conversations if c.conversation_id == conversation_id), None)

    if selected_conv and selected_conv.transcript:
        st.subheader("Transcript Preview")
        st.text_area("Transcript", value=selected_conv.transcript[:2000], height=200, disabled=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Run AI Analysis", type="primary", width='stretch'):
            if not selected_conv or not selected_conv.transcript:
                show_error("No transcript available for analysis.")
            else:
                patient_info = f"Patient ID: {patient_id}"
                consultation_notes = ""
                assessment_data = ""

                db = get_session()
                latest_assessment = None
                try:
                    consultation = next((c for c in consultations if c.consultation_id == consultation_id), None)
                    if consultation:
                        consultation_notes = f"Diagnosis: {consultation.preliminary_diagnosis or ''}\nFindings: {consultation.clinical_findings or ''}"

                    assessments = get_pain_assessments(db, patient_id)
                    if assessments:
                        latest = assessments[0]
                        latest_assessment = latest
                        assessment_data = f"Pain severity: {latest.pain_severity}, Areas: {latest.pain_areas}, Numbness: {latest.numbness}, Weakness: {latest.muscle_weakness}, Radiation: {latest.nerve_radiation}"
                finally:
                    db.close()

                with st.spinner("Running AI analysis..."):
                    if latest_assessment:
                        risk_result = assess_risk({
                            "pain_severity": latest_assessment.pain_severity,
                            "numbness": latest_assessment.numbness,
                            "muscle_weakness": latest_assessment.muscle_weakness,
                            "nerve_radiation": latest_assessment.nerve_radiation,
                            "sleep_disturbance": latest_assessment.sleep_disturbance,
                            "previous_spine_surgery": "",
                        })
                    else:
                        risk_result = assess_risk({
                            "pain_severity": 0,
                            "numbness": "",
                            "muscle_weakness": "",
                            "nerve_radiation": "",
                            "sleep_disturbance": "",
                            "previous_spine_surgery": "",
                        })

                    llm_result = analyze_with_llm(
                        transcript=selected_conv.transcript,
                        patient_info=patient_info,
                        consultation_notes=consultation_notes,
                        assessment_data=assessment_data,
                    )

                ai_data = {
                    "conversation_id": conversation_id,
                    "ai_summary": llm_result.get("summary", "") if not llm_result.get("fallback") else "LLM unavailable, using rule-based analysis",
                    "extracted_symptoms": ", ".join(llm_result.get("symptoms", [])) if not llm_result.get("fallback") else "",
                    "possible_condition": llm_result.get("possible_condition", "") if not llm_result.get("fallback") else "",
                    "predicted_pain_severity": llm_result.get("pain_severity", 0) if not llm_result.get("fallback") else None,
                    "recommended_therapy": ", ".join(llm_result.get("recommended_therapy", [])) if not llm_result.get("fallback") else "",
                    "recommended_tests": ", ".join(llm_result.get("recommended_tests", [])) if not llm_result.get("fallback") else "",
                    "risk_level": risk_result.get("risk_level", "LOW"),
                    "surgery_probability": risk_result.get("surgery_probability", "LOW"),
                    "recovery_prediction": llm_result.get("recovery_prediction", "") if not llm_result.get("fallback") else "",
                    "followup_suggestion": llm_result.get("followup", "") if not llm_result.get("fallback") else "",
                    "confidence_score": llm_result.get("confidence_score", 0.0) if not llm_result.get("fallback") else 0.0,
                    "raw_json": json.dumps(llm_result) if not llm_result.get("fallback") else json.dumps(risk_result),
                }

                db = get_session()
                try:
                    create_ai_output(db, ai_data)
                    show_success("AI analysis complete!")
                except Exception as e:
                    show_error(f"Error saving: {str(e)}")
                finally:
                    db.close()

    with col2:
        if st.button("Run Rule-Based Risk Analysis Only", width='stretch'):
            db = get_session()
            try:
                assessments = get_pain_assessments(db, patient_id)
                latest_assessment = assessments[0] if assessments else None
                if latest_assessment:
                    risk_result = assess_risk({
                        "pain_severity": latest_assessment.pain_severity,
                        "numbness": latest_assessment.numbness,
                        "muscle_weakness": latest_assessment.muscle_weakness,
                        "nerve_radiation": latest_assessment.nerve_radiation,
                        "sleep_disturbance": latest_assessment.sleep_disturbance,
                        "previous_spine_surgery": "",
                    })
                    st.metric("Risk Level", risk_result["risk_level"])
                    st.metric("Surgery Probability", risk_result["surgery_probability"])
                    if risk_result["reasons"]:
                        st.write("**Risk Factors:**")
                        for r in risk_result["reasons"]:
                            st.write(f"- {r}")
                else:
                    show_warning("No assessment data found for risk analysis.")
            finally:
                db.close()

    db = get_session()
    try:
        outputs = get_ai_outputs(db, conversation_id)
        if outputs:
            st.subheader("AI Analysis Results")
            for out in outputs:
                with st.expander(f"Risk: {out.risk_level} | Confidence: {out.confidence_score or 'N/A'}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Risk Level", out.risk_level or "N/A")
                        st.metric("Surgery Probability", out.surgery_probability or "N/A")
                        st.metric("Pain Severity", out.predicted_pain_severity or "N/A")
                    with c2:
                        st.metric("Confidence Score", out.confidence_score or "N/A")
                    st.write(f"**Summary:** {out.ai_summary or 'N/A'}")
                    st.write(f"**Condition:** {out.possible_condition or 'N/A'}")
                    st.write(f"**Therapy:** {out.recommended_therapy or 'N/A'}")
                    st.write(f"**Tests:** {out.recommended_tests or 'N/A'}")
                    st.write(f"**Recovery:** {out.recovery_prediction or 'N/A'}")
                    st.write(f"**Follow-up:** {out.followup_suggestion or 'N/A'}")
    finally:
        db.close()
