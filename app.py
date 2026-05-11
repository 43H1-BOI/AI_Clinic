import streamlit as st
from database.db import init_db
from database.seed_data import seed_database
from utils.ui_helpers import set_page_config, apply_custom_css
from utils.constants import SIDEBAR_OPTIONS
PAGE_MAP = {
    "Add Patient": "patient_registration",
    "Pain Assessment": "pain_assessment",
    "Consultation Entry": "consultation",
    "Treatment Session": "treatment",
    "Upload Conversation": "conversation",
    "AI Analysis": "ai_analysis",
    "Progress Tracker": "progress_tracker",
    "Dashboard / History": "dashboard",
}


def main():
    set_page_config()
    apply_custom_css()

    init_db()
    seed_database()

    st.sidebar.title("Dr Rajat AI Clinic")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Navigation")

    selection = st.sidebar.radio("Go to", SIDEBAR_OPTIONS, label_visibility="collapsed")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Specialties:**")
    st.sidebar.markdown("""
    - Chiropractic
    - Osteopathy
    - Ayurveda
    - Panchakarma
    - Spine Care
    """)
    st.sidebar.markdown("---")
    st.sidebar.caption("v1.0.0 | MVP")

    page_name = PAGE_MAP.get(selection)
    if page_name:
        import importlib
        module = importlib.import_module(f"pages.{page_name}")
        module.render()


if __name__ == "__main__":
    main()
