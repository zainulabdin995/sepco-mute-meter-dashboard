import streamlit as st

def setup_navigation():
    """Sets up organized sidebar navigation with clear sections"""
    st.markdown("""
        <style>
            /* Hide default sidebar */
            [data-testid="stSidebarNav"] { display: none !important; }
            
            /* Consistent button styling */
            .stButton button {
                width: 100% !important;
                margin: 3px 0 !important;
                padding: 10px !important;
                border-radius: 5px !important;
                transition: all 0.2s !important;
            }
            
            .stButton button:hover {
                transform: scale(1.02) !important;
            }
            
            /* Highlight current page */
            .current-page {
                background-color: #3ddc84 !important;
                color: white !important;
                font-weight: bold !important;
            }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.get('logged_in', False):
        with st.sidebar:
            # User info section
            st.markdown(f"**{st.session_state.user_email}**")
            st.caption(f"Role: {st.session_state.user_role}")
            
            # Logout button under user info
            if st.button(
                "🚪 Logout",
                key="logout_button",
                use_container_width=True,
                type="primary"
            ):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.switch_page("login.py")
            
            st.markdown("---")
            
            # Navigation section
            st.markdown("**Navigation:**")
            pages = {
                "Welcome": "0_Welcome.py",
                "Customer Search": "1_Customer_Search.py",
                "Mute Analytics": "2_Mute_Analytics.py",
                "Traffic Insights": "3_Traffic_Insights.py",
                "Data Export": "4_Data_Export.py"
            }
            
            if st.session_state.user_role == "admin":
                pages["Admin Dashboard"] = "5_Admin_Dashboard.py"
            
            for page_name, page_file in pages.items():
                button_type = "primary" if page_name == st.session_state.current_page else "secondary"
                if st.button(
                    page_name,
                    key=f"nav_{page_name}",
                    use_container_width=True,
                    type=button_type
                ):
                    st.session_state.current_page = page_name
                    st.switch_page(f"pages/{page_file}")
            
            st.markdown("---")
            
            # Action buttons section
            if st.session_state.current_page == "Data Export":
                st.download_button(
                    "⬇️ Download Data",
                    data="",  # Your data here
                    file_name="export.csv",
                    use_container_width=True
                )
                st.markdown("---")