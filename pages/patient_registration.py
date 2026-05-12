import streamlit as st
from database.db import get_session
from database.crud import create_patient, update_patient, delete_patient, search_patients, get_all_patients, get_patient_by_mobile
from utils.ui_helpers import show_success, show_error, show_info
from utils.validators import validate_mobile, validate_age
import pandas as pd


def render():
    st.header("Patient Registration")
    tab1, tab2, tab3 = st.tabs(["Add Patient", "Search / Edit", "All Patients"])

    with tab1:
        with st.form("patient_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name *", placeholder="Enter patient name")
                age = st.number_input("Age *", min_value=0, max_value=150, step=1)
                gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
                mobile = st.text_input("Mobile *", placeholder="10+ digits")
                email = st.text_input("Email", placeholder="optional")
                occupation = st.text_input("Occupation", placeholder="optional")
            with col2:
                height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, step=0.1, format="%.1f")
                weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.1, format="%.1f")
                bmi = None
                if height > 0 and weight > 0:
                    bmi = weight / ((height / 100) ** 2)
                    st.metric("Calculated BMI", f"{bmi:.1f}")
                dob = st.text_input("Date of Birth", placeholder="DD-MM-YYYY")
                lifestyle = st.selectbox("Lifestyle", ["", "Sedentary", "Moderately Active", "Active", "Highly Active"])
                smoking_alcohol = st.text_input("Smoking / Alcohol", placeholder="e.g., Occasional, Regular, No")

            address = st.text_area("Address", placeholder="optional")
            c1, c2 = st.columns(2)
            with c1:
                existing_diseases = st.text_area("Existing Diseases", placeholder="e.g., Diabetes, Hypertension")
                previous_spine_surgery = st.selectbox("Previous Spine Surgery", ["", "No", "Yes"])
            with c2:
                emergency_contact = st.text_input("Emergency Contact", placeholder="optional")

            submitted = st.form_submit_button("Save Patient", type="primary", width='stretch')

            if submitted:
                if not full_name or not mobile:
                    show_error("Full Name and Mobile are required.")
                elif not validate_mobile(mobile):
                    show_error("Mobile must have at least 10 digits.")
                elif not validate_age(age):
                    show_error("Invalid age.")
                else:
                    data = {
                        "full_name": full_name.strip(),
                        "age": int(age),
                        "gender": gender,
                        "mobile": mobile.strip(),
                        "email": email.strip() if email else None,
                        "occupation": occupation.strip() if occupation else None,
                        "height": height if height > 0 else None,
                        "weight": weight if weight > 0 else None,
                        "bmi": round(bmi, 1) if bmi is not None else None,
                        "dob": dob.strip() if dob else None,
                        "lifestyle": lifestyle if lifestyle else None,
                        "smoking_alcohol": smoking_alcohol.strip() if smoking_alcohol else None,
                        "address": address.strip() if address else None,
                        "existing_diseases": existing_diseases.strip() if existing_diseases else None,
                        "previous_spine_surgery": previous_spine_surgery if previous_spine_surgery else None,
                        "emergency_contact": emergency_contact.strip() if emergency_contact else None,
                    }
                    db = get_session()
                    try:
                        existing = get_patient_by_mobile(db, data["mobile"])
                        if existing:
                            show_error(f"Patient with this mobile already exists (ID: {existing.patient_id} - {existing.full_name}). Use Search/Edit tab to update.")
                        else:
                            patient = create_patient(db, data)
                            show_success(f"Patient registered successfully! ID: {patient.patient_id}")
                    except Exception as e:
                        show_error(f"Error: {str(e)}")
                    finally:
                        db.close()

    with tab2:
        search_query = st.text_input("Search by Name, Mobile, or ID", placeholder="Type to search...")
        db = get_session()
        try:
            if search_query:
                results = search_patients(db, search_query)
            else:
                results = []
            if results:
                for patient in results:
                    with st.expander(f"{patient.patient_id} - {patient.full_name} ({patient.mobile})"):
                        with st.form(f"edit_form_{patient.patient_id}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                name = st.text_input("Full Name", value=patient.full_name, key=f"name_{patient.patient_id}")
                                age = st.number_input("Age", value=patient.age or 0, key=f"age_{patient.patient_id}")
                                gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(patient.gender) if patient.gender in ["Male", "Female", "Other"] else 0, key=f"gender_{patient.patient_id}")
                                mobile = st.text_input("Mobile", value=patient.mobile or "", key=f"mobile_{patient.patient_id}")
                                email = st.text_input("Email", value=patient.email or "", key=f"email_{patient.patient_id}")
                                occupation = st.text_input("Occupation", value=patient.occupation or "", key=f"occ_{patient.patient_id}")
                            with col2:
                                height = st.number_input("Height (cm)", value=patient.height or 0.0, key=f"h_{patient.patient_id}")
                                weight = st.number_input("Weight (kg)", value=patient.weight or 0.0, key=f"w_{patient.patient_id}")
                                if height > 0 and weight > 0:
                                    st.metric("BMI", f"{weight / ((height / 100) ** 2):.1f}")
                                dob = st.text_input("Date of Birth", value=patient.dob or "", key=f"dob_{patient.patient_id}")
                                lifestyle = st.selectbox("Lifestyle", ["", "Sedentary", "Moderately Active", "Active", "Highly Active"], index=0 if not patient.lifestyle else (["", "Sedentary", "Moderately Active", "Active", "Highly Active"].index(patient.lifestyle) if patient.lifestyle in ["", "Sedentary", "Moderately Active", "Active", "Highly Active"] else 0), key=f"life_{patient.patient_id}")
                                smoking_alcohol = st.text_input("Smoking / Alcohol", value=patient.smoking_alcohol or "", key=f"sa_{patient.patient_id}")
                            existing = st.text_area("Existing Diseases", value=patient.existing_diseases or "", key=f"dis_{patient.patient_id}")
                            col3, col4 = st.columns(2)
                            with col3:
                                address = st.text_area("Address", value=patient.address or "", key=f"addr_{patient.patient_id}")
                                emergency_contact = st.text_input("Emergency Contact", value=patient.emergency_contact or "", key=f"emerg_{patient.patient_id}")
                            with col4:
                                prev_surg = st.selectbox("Previous Spine Surgery", ["", "No", "Yes"], index=0 if not patient.previous_spine_surgery else (1 if patient.previous_spine_surgery == "No" else 2), key=f"sur_{patient.patient_id}")
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.form_submit_button("Update", type="primary", width='stretch'):
                                    if not name or not mobile:
                                        show_error("Full Name and Mobile are required.")
                                    elif not validate_mobile(mobile):
                                        show_error("Mobile must have at least 10 digits.")
                                    elif not validate_age(age):
                                        show_error("Invalid age.")
                                    else:
                                        data = {
                                            "full_name": name.strip(),
                                            "age": int(age),
                                            "gender": gender,
                                            "mobile": mobile.strip(),
                                            "email": email.strip() if email else None,
                                            "occupation": occupation.strip() if occupation else None,
                                            "height": height if height > 0 else None,
                                            "weight": weight if weight > 0 else None,
                                            "bmi": round(weight / ((height / 100) ** 2), 1) if height > 0 and weight > 0 else None,
                                            "dob": dob.strip() if dob else None,
                                            "lifestyle": lifestyle if lifestyle else None,
                                            "smoking_alcohol": smoking_alcohol.strip() if smoking_alcohol else None,
                                            "address": address.strip() if address else None,
                                            "existing_diseases": existing.strip() if existing else None,
                                            "previous_spine_surgery": prev_surg if prev_surg else None,
                                            "emergency_contact": emergency_contact.strip() if emergency_contact else None,
                                        }
                                        update_patient(db, patient.patient_id, data)
                                        show_success("Patient updated!")
                            with c2:
                                if st.form_submit_button("Delete", width='stretch', type="secondary"):
                                    delete_patient(db, patient.patient_id)
                                    show_info("Patient deleted.")
            else:
                if search_query:
                    show_info("No patients found.")
        finally:
            db.close()

    with tab3:
        db = get_session()
        try:
            patients = get_all_patients(db)
            if patients:
                data = [{
                    "ID": p.patient_id, "Name": p.full_name, "Age": p.age,
                    "Gender": p.gender, "Mobile": p.mobile, "BMI": p.bmi or "-",
                    "Lifestyle": p.lifestyle or "-",
                } for p in patients]
                df = pd.DataFrame(data)
                st.dataframe(df, width='stretch', hide_index=True)
            else:
                show_info("No patients registered yet.")
        finally:
            db.close()
