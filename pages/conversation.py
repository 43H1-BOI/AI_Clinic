import streamlit as st
import os
from database.db import get_session
from database.crud import get_all_patients, get_consultations, create_conversation, get_conversations
from utils.ui_helpers import show_success, show_error
from utils.helpers import generate_unique_filename
from ai.whisper_service import transcribe_audio
from ai.symptom_extractor import extract_symptoms
import pandas as pd

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "audio")
TRANSCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "transcripts")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)


def render():
    st.header("Upload Conversation")
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

    tab1, tab2 = st.tabs(["Upload Audio", "Manual Transcript"])

    with tab1:
        st.subheader("Upload & Transcribe Audio")
        st.info("Supported formats: MP3, WAV, M4A. Supports Hindi + English.")

        audio_file = st.file_uploader("Choose audio file", type=["mp3", "wav", "m4a"])

        if audio_file:
            st.audio(audio_file, format=f"audio/{audio_file.type.split('/')[-1]}")

            if st.button("Transcribe Audio", type="primary"):
                filename = generate_unique_filename(audio_file.name)
                audio_path = os.path.join(AUDIO_DIR, filename)
                with open(audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())

                with st.spinner("Transcribing with Faster-Whisper..."):
                    result = transcribe_audio(audio_path)

                if result["success"]:
                    transcript = result["transcript"]
                    language = result.get("language", "unknown")

                    symptoms = extract_symptoms(transcript)

                    data = {
                        "consultation_id": consultation_id,
                        "source_type": "audio",
                        "audio_path": audio_path,
                        "transcript": transcript,
                        "language": language,
                        "pain_keywords": ", ".join(symptoms["pain_keywords"]),
                    }
                    db = get_session()
                    try:
                        conv = create_conversation(db, data)
                        transcript_filename = f"transcript_{conv.conversation_id}.txt"
                        transcript_path = os.path.join(TRANSCRIPT_DIR, transcript_filename)
                        with open(transcript_path, "w") as f:
                            f.write(transcript)
                        show_success("Transcription complete and saved!")
                    except Exception as e:
                        show_error(f"Error saving: {str(e)}")
                    finally:
                        db.close()
                else:
                    show_error(f"Transcription failed: {result.get('error', 'Unknown error')}")

    with tab2:
        st.subheader("Manual Transcript Entry")
        with st.form("transcript_form"):
            transcript = st.text_area("Transcript", height=300, placeholder="Paste or type conversation transcript here...")
            language = st.text_input("Language", placeholder="e.g., Hindi, English, Bilingual")
            speaker_separation = st.text_input("Speaker Separation", placeholder="e.g., Doctor: Dr. Rajat, Patient: Name")
            emotional_state = st.text_input("Emotional State", placeholder="e.g., Anxious, Calm, In pain")
            additional_notes = st.text_area("Additional Notes")

            submitted = st.form_submit_button("Save Transcript", type="primary", width='stretch')
            if submitted and transcript:
                symptoms = extract_symptoms(transcript)
                data = {
                    "consultation_id": consultation_id,
                    "source_type": "manual",
                    "transcript": transcript.strip(),
                    "language": language.strip() if language else None,
                    "speaker_separation": speaker_separation.strip() if speaker_separation else None,
                    "emotional_state": emotional_state.strip() if emotional_state else None,
                    "additional_notes": additional_notes.strip() if additional_notes else None,
                    "pain_keywords": ", ".join(symptoms["pain_keywords"]),
                }
                db = get_session()
                try:
                    create_conversation(db, data)
                    show_success("Transcript saved!")
                except Exception as e:
                    show_error(f"Error: {str(e)}")
                finally:
                    db.close()

    db = get_session()
    try:
        conversations = get_conversations(db, consultation_id)
        if conversations:
            st.subheader("Saved Conversations")
            for conv in conversations:
                with st.expander(f"{conv.source_type or 'N/A'} - {conv.created_at.strftime('%d-%m-%Y %H:%M') if conv.created_at else ''}"):
                    st.write(f"**Language:** {conv.language or 'N/A'}")
                    st.write(f"**Keywords:** {conv.pain_keywords or 'N/A'}")
                    if conv.transcript:
                        st.text_area("Transcript", value=conv.transcript, height=200, disabled=True, key=f"transcript_{conv.conversation_id}")
    finally:
        db.close()
