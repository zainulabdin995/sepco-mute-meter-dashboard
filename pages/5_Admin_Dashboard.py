# File: Admin_Dashboard.py

import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Admin Portal", layout="wide")
st.title("🔐 Admin Dashboard")

# -- Session State --
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# -- Admin Login --
if not st.session_state.admin_logged_in:
    st.subheader("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "admin123":  # Temporary login logic
            st.session_state.admin_logged_in = True
            st.success("Logged in as Admin")
        else:
            st.error("Invalid credentials")
    st.stop()

# -- Admin Home --
st.sidebar.success("Admin Access Granted ✅")
st.subheader("🔧 Admin Tools")

# --- Future Tools (placeholders for now) ---
with st.expander("⚙️ Admin Utilities (Coming Soon)"):
    st.markdown("- Sync with external systems")
    st.markdown("- Add/remove admin users")
    st.markdown("- Export system logs")

# --- 🔄 Mute Reason Editor ---
st.subheader("🛠️ Update Mute Reason by Reference No.")

ref_input = st.text_input("Enter Reference Number to Search:")
if ref_input:
    conn = sqlite3.connect("sepco_meters.db")
    cursor = conn.cursor()
    query = "SELECT `Reference_no`, `Name`, `mute_reason` FROM meter_data WHERE `Reference_no` = ?"
    result = cursor.execute(query, (ref_input.strip(),)).fetchone()

    if result:
        ref_no, name, current_reason = result
        st.write(f"**Name**: {name}")
        st.write(f"**Current Mute Reason**: {current_reason if current_reason else 'None'}")

        new_reason = st.text_input("New Mute Reason (leave blank to remove):", value=current_reason or "")
        if st.button("Update Mute Reason"):
            updated_value = None if new_reason.strip() == "" else new_reason.strip()
            cursor.execute("UPDATE meter_data SET mute_reason = ? WHERE Reference_no = ?", (updated_value, ref_input.strip()))
            conn.commit()
            conn.close()
            st.success("Mute reason updated successfully.")
    else:
        st.error("Reference Number not found.")
