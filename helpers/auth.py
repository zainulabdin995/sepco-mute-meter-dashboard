import streamlit as st
import sqlite3
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def check_authentication():
    # Check if logged in
    if not st.session_state.get('logged_in', False):
        st.error("Please log in to access the dashboard")
        st.switch_page("login.py")
        st.stop()
    
    # Ensure access object exists
    if st.session_state.user_role != "admin" and not hasattr(st.session_state, 'access'):
        st.error("Access permissions not properly initialized")
        st.switch_page("login.py")
        st.stop()