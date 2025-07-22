import streamlit as st
import os
from PIL import Image
from helpers.auth import check_authentication
from helpers.navigation import setup_navigation

# Page config MUST BE FIRST and called only once
st.set_page_config(
    page_title="SEPCO Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication check
check_authentication()

# Setup navigation
setup_navigation()

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Welcome"

# Function to load image with error handling
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

# Load images using PIL
logo_path = "logo.png"
left_logo = load_image(logo_path)

# --- Combined CSS Styling ---
st.markdown("""
    <style>
    .header-title {
        text-align: center;
        color: var(--text-color, #000000); /* Fallback to black if theme variable not available */
        flex-grow: 1;
    }
    .header-title h1 {
        font-size: 32px;
        margin-bottom: 0;
        font-weight: bold;
    }
    .header-title h2 {
        font-size: 20px;
        margin-top: 5px;
        font-family: 'Noto Nastaliq Urdu', 'Arial', sans-serif; /* Fallback font */
    }
    .welcome {
        padding: 25px;
        border-radius: 10px;
        margin-top: 30px;
        background-color: var(--background-color, rgba(240, 240, 240, 0.1)); /* Theme-safe */
        border: 1px solid var(--border-color, rgba(200, 200, 200, 0.2)); /* Theme-safe */
    }
    </style>
""", unsafe_allow_html=True)

# --- Header Section ---
col1, col2, col3 = st.columns([1, 6, 1])

with col1:
    if left_logo:
        st.image(left_logo, width=100)

with col2:
    st.markdown("""
        <div class="header-title">
            <h1>SUKKUR ELECTRIC POWER COMPANY</h1>
            <h1>سکر اليڪٽرڪ پاور ڪمپني</h1>
        </div>
    """, unsafe_allow_html=True)

# --- Welcome Section ---
st.markdown("""
    <div class="welcome">
        <h3>👋 Welcome to the <strong>SEPCO Mute Meter Dashboard</strong></h3>
        <p style="font-size: 16px;">
            This dashboard enables the <b>SUKKUR ELECTRIC POWER COMPANY (SEPCO)</b> to manage and monitor 
            <b>mute meters</b> across its operational regions.
        </p>
        <p style="font-weight: bold;">Use the sidebar to:</p>
        <ul style="line-height: 1.8;">
            <li>🔍 <b>Search and edit mute reasons</b></li>
            <li>📊 <b>View mute meter analytics</b></li>
            <li>📈 <b>Traffic insights</b> and data trends</li>
            <li>📤 <b>Export reports and raw data</b></li>
        </ul>
    </div>
""", unsafe_allow_html=True)