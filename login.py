import streamlit as st
import sqlite3
import bcrypt
import os
from PIL import Image
from helpers.auth import hash_password, verify_password

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False,
        'user_role': None,
        'user_email': None,
        'current_page': None,
        'access': {
            'circle': None,
            'division': None,
            'subdivision': None,
            'feeder': None
        }
    })

# Page config
st.set_page_config(
    page_title="SEPCO Login",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load logo
def load_image(image_path):
    try:
        if os.path.exists(image_path):
            return Image.open(image_path)
        else:
            st.error(f"Image file '{image_path}' not found.")
            return None
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

logo_path = "logo.png"
logo = load_image(logo_path)

# Authentication
def authenticate(email, password, role):
    if not email or not password:
        st.error("Email and password are required.")
        return False
    if role not in ["user", "admin"]:
        st.error("Invalid role selected.")
        return False
    if not email.endswith("@sepco.com.pk"):
        st.error("Email must be a valid SEPCO email (e.g., user@sepco.com.pk).")
        return False

    db_file = "sepco_meters.db"
    if not os.path.exists(db_file):
        st.error("Database file not found. Please contact the administrator.")
        return False

    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT email, password, role, circle, division, subdivision, feeder 
                FROM users WHERE email = ? AND role = ?""",
                (email, role)
            )
            user = cursor.fetchone()
            if not user:
                st.error("User not found or incorrect role.")
                return False
            if not verify_password(password, user[1]):
                st.error("Incorrect password.")
                return False

            st.session_state.update({
                'logged_in': True,
                'user_role': user[2],
                'user_email': user[0],
                'current_page': "Welcome",
                'access': {
                    'circle': user[3],
                    'division': user[4],
                    'subdivision': user[5],
                    'feeder': user[6]
                }
            })
            return True
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return False

# --- HEADER (Logo + Title in one row, title won't wrap)
col1, col2 = st.columns([1, 5])
with col1:
    if logo:
        st.image(logo, width=80)
with col2:
    st.markdown(
        "<h1 style='font-size: 32px; margin-top: 15px; white-space: nowrap;'>SEPCO Mute Meter Dashboard</h1>",
        unsafe_allow_html=True
    )

# --- SUBHEADER
st.markdown("<h3 style='margin-bottom: 0.5em; color: #666;'>Login</h3>", unsafe_allow_html=True)

# --- LOGIN FORM
with st.form("login_form"):
    email = st.text_input("📧 Email", placeholder="user@sepco.com.pk")
    password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
    role = st.radio("🛂 Select Role", ["user", "admin"], horizontal=True, index=0)
    login = st.form_submit_button("🔐 Login")

    if login:
        if authenticate(email, password, role):
            try:
                if os.path.exists("pages/0_Welcome.py"):
                    st.success(f"✅ Login successful as {role.capitalize()}. Redirecting...")
                    st.switch_page("pages/0_Welcome.py")
                else:
                    st.error("Welcome page not found.")
            except Exception as e:
                st.error(f"Error redirecting to Welcome page: {e}")

# --- CUSTOM STYLING
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none !important; }
        .stTextInput input {
            font-size: 16px;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: #f9f9f9;
        }
        .stRadio > label {
            font-size: 16px;
        }
        .stButton button {
            font-size: 16px;
            padding: 10px 24px;
            background-color: #4CAF50;
            color: white;
            border-radius: 6px;
            border: none;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        h1 {
            font-family: 'Segoe UI', sans-serif;
            white-space: nowrap;
        }
        h3 {
            font-family: 'Segoe UI', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)
