import streamlit as st
from PIL import Image
import os

# Page config
st.set_page_config(page_title="SEPCO Dashboard", layout="wide")

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

# --- Background Styling ---
st.markdown("""
    <style>
    .header-title {
        flex-grow: 1;
        text-align: center;
        color: white;
    }
    .header-title h1 {
        margin: 0;
        font-size: 30px;
        font-weight: bold;
    }
    .header-title h3 {
        margin: 5px 0 0;
        font-size: 20px;
        font-family: 'Noto Nastaliq Urdu', 'Arial', sans-serif; /* Fallback font */
    }
    .welcome {
        background: rgba(255, 255, 255, 0.9);
        padding: 30px;
        margin-top: 30px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header Section ---
col1, col2, col3 = st.columns([1, 6, 1])

# Inject style
st.markdown("""
    <style>
    .header-title {
        text-align: center;
        color: var(--text-color);  /* ✅ adapts to theme */
    }
    .header-title h1 {
        font-size: 32px;
        margin-bottom: 0;
    }
    .header-title h3 {
        font-size: 20px;
        margin-top: 0;
    }
    </style>
""", unsafe_allow_html=True)

with col1:
    if left_logo:
        st.image(left_logo, width=100)

with col2:
    st.markdown("""
        <div class="header-title">
            <h1>SUKKUR ELECTRIC POWER COMPANY</h1>
            <h3>سکر الیکٹرک پاور کمپنی</h3>
        </div>
    """, unsafe_allow_html=True)


# --- Welcome Section (Theme-safe) ---
st.markdown("""
    <div style="
        padding: 25px;
        border-radius: 10px;
        margin-top: 30px;
        background-color: rgba(240, 240, 240, 0.1);
        border: 1px solid rgba(200, 200, 200, 0.2);
    ">
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
