import streamlit as st


def set_page_config():
    st.set_page_config(
        page_title="Dr Rajat AI Clinic",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_custom_css():
    st.markdown("""
    <style>
        .stApp { background-color: #f8f9fa; }
        .main > div { padding: 1rem 1.5rem; }
        h1, h2, h3 { color: #1a365d; }
        .stButton > button {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            border: none;
        }
        .stButton > button:hover { background-color: #1d4ed8; }
        div[data-testid="stMetricValue"] { font-size: 2rem; color: #1a365d; }
        div[data-testid="stMetricLabel"] { font-size: 0.9rem; color: #64748b; }
        .stDataFrame { border-radius: 8px; border: 1px solid #e2e8f0; }
        .stSelectbox label, .stTextInput label, .stNumberInput label {
            font-weight: 500; color: #334155;
        }
        .sidebar .sidebar-content { background-color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)


def show_success(msg: str):
    st.success(msg)


def show_error(msg: str):
    st.error(msg)


def show_info(msg: str):
    st.info(msg)


def show_warning(msg: str):
    st.warning(msg)
