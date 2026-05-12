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
        .main > div { padding: 1rem 1.5rem; }
        div[data-testid="stMetricValue"] { font-size: 2rem; }
        div[data-testid="stMetricLabel"] { font-size: 0.9rem; }
        .stDataFrame { border-radius: 8px; border: 1px solid #e2e8f0; }
        .stButton > button {
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
        }

        [data-theme="light"] .stApp { background-color: #f8f9fa; }
        [data-theme="light"] h1, [data-theme="light"] h2, [data-theme="light"] h3 { color: #1a365d; }
        [data-theme="light"] .stButton > button { background-color: #2563eb; color: white; border: none; }
        [data-theme="light"] .stButton > button:hover { background-color: #1d4ed8; }
        [data-theme="light"] div[data-testid="stMetricValue"] { color: #1a365d; }
        [data-theme="light"] div[data-testid="stMetricLabel"] { color: #64748b; }
        [data-theme="light"] .stDataFrame { border: 1px solid #e2e8f0; }
        [data-theme="light"] .stSelectbox label, [data-theme="light"] .stTextInput label, [data-theme="light"] .stNumberInput label { color: #334155; }

        [data-theme="dark"] .stApp { background-color: #0e1117; }
        [data-theme="dark"] h1, [data-theme="dark"] h2, [data-theme="dark"] h3 { color: #e0e6ed; }
        [data-theme="dark"] .stButton > button { background-color: #3b82f6; color: white; border: none; }
        [data-theme="dark"] .stButton > button:hover { background-color: #2563eb; }
        [data-theme="dark"] div[data-testid="stMetricValue"] { color: #60a5fa; }
        [data-theme="dark"] div[data-testid="stMetricLabel"] { color: #94a3b8; }
        [data-theme="dark"] .stDataFrame { border: 1px solid #334155; }
        [data-theme="dark"] .stSelectbox label, [data-theme="dark"] .stTextInput label, [data-theme="dark"] .stNumberInput label { color: #cbd5e1; }
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
