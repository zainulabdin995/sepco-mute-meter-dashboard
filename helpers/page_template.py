import streamlit as st
from helpers.auth import check_authentication
from helpers.navigation import hide_default_sidebar, show_custom_sidebar

def setup_page(page_title, page_name):
    """Standard setup for all pages"""
    st.set_page_config(page_title=page_title, layout="wide")
    check_authentication()
    hide_default_sidebar()
    show_custom_sidebar()
    st.session_state.current_page = page_name