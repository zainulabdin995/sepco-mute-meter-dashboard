import streamlit as st
import sqlite3
import pandas as pd
from helpers.navigation import setup_navigation
from helpers.auth import check_authentication

# 1. Page config (must be first)
st.set_page_config(
    page_title="SEPCO Dashboard - Customer Search",
    layout="wide"
)

# 2. Authentication check
check_authentication()

# 3. Setup custom navigation (hides auto sidebar)
setup_navigation()

# 4. Set current page
st.session_state.current_page = "Customer Search"

# Page content
st.title("🔍 Customer Search")

# Define mute reasons
MUTE_REASONS = [
    "Cable Jumper Loose", "Extra Phase Wire Loop", "GPRS Meter Bypass",
    "Meter Washout", "Network Error", "Offline Due To Load Sheading",
    "Screen Opened Slow", "SIM Card Faulty", "Structure Fallen Down",
    "T/B Lock Heatup Slow", "Units Pending", "Running Direct", "Transformer Not At Site",
    "No Communication", "D-FUSE Cut Off", "Service Drop Disconnected", "MDI Supply Fail",
    "Display Opened", "Not In Use", "Not Found", "Pending Units",
    "Supply Cut Off Due To Non-Payment", "MCO Not Take Up", "T/F Not At Site",
    "Transformer Faulty", "T/F Burnt", "11KV Line Disconnected", "Wash Out",
    "Meter Line Disconnected", "Meter Burnt", "LT Line Disconnected", "HT Line Disconnect",
    "No Meter At Site"
]

# Filter data based on user access
def filter_data(df):
    if st.session_state.user_role != "admin":
        access = st.session_state.access
        if access.get('circle'):
            df = df[df['Circle'] == access['circle']]
        if access.get('division'):
            df = df[df['Division'] == access['division']]
        if access.get('subdivision'):
            df = df[df['Sub-Division'] == access['subdivision']]
        if access.get('feeder'):
            df = df[df['Feeder'] == access['feeder']]
    return df

# Function to check if reference number exists
def check_reference_exists(conn, ref_no):
    try:
        query = "SELECT COUNT(*) FROM meter_data WHERE Reference_no = ?"
        result = conn.execute(query, (ref_no,)).fetchone()[0]
        return result > 0
    except Exception as e:
        st.error(f"Error checking reference number: {str(e)}")
        return False

# Initialize session state for search results
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'ref_no_searched' not in st.session_state:
    st.session_state.ref_no_searched = ""
if 'mute_reason_submitted' not in st.session_state:
    st.session_state.mute_reason_submitted = False
if 'selected_reason' not in st.session_state:
    st.session_state.selected_reason = None

# Search form
with st.form("customer_search_form"):
    ref_no = st.text_input("🔢 Enter Customer Reference No.", 
                          value=st.session_state.ref_no_searched, 
                          key="ref_no_input")
    submitted = st.form_submit_button("Search")

if submitted and ref_no:
    try:
        with sqlite3.connect("sepco_meters.db") as conn:
            # Check if reference number exists
            if not check_reference_exists(conn, ref_no):
                st.warning("⚠️ No customer found with that Reference No.")
                st.session_state.search_results = None
                st.session_state.ref_no_searched = ""
                st.session_state.mute_reason_submitted = False
                st.stop()

            df = pd.read_sql_query(
                "SELECT * FROM meter_data WHERE Reference_no = ?", 
                conn, 
                params=(ref_no,)
            )
            df = filter_data(df)

        if not df.empty:
            st.session_state.search_results = df
            st.session_state.ref_no_searched = ref_no
            st.session_state.mute_reason_submitted = False
            st.success("✅ Customer record found")
        else:
            st.session_state.search_results = None
            st.session_state.ref_no_searched = ""
            st.session_state.mute_reason_submitted = False
            st.warning("⚠️ No customer found with that Reference No or you lack access.")
            
    except Exception as e:
        st.error(f"�බ Database error: {str(e)}")
        st.session_state.search_results = None
        st.session_state.ref_no_searched = ""
        st.session_state.mute_reason_submitted = False
elif submitted and not ref_no:
    st.warning("⚠️ Please enter a reference number")

# Display search results and mute reason form
if st.session_state.search_results is not None:
    st.dataframe(st.session_state.search_results.style.highlight_null(props="color: red;"), 
                use_container_width=True)
    
    current_reason = st.session_state.search_results.iloc[0]["mute_reason"]
    if pd.notna(current_reason) and str(current_reason).strip() != "":
        st.info(f"🛑 Mute reason already set: **{current_reason}**")
        st.warning("You cannot edit the mute reason again.")
    elif not st.session_state.mute_reason_submitted:
        with st.form("mute_reason_form"):
            selected_reason = st.selectbox(
                "📌 Select Mute Reason:", 
                MUTE_REASONS,
                key="reason_select"
            )
            if st.form_submit_button("💾 Submit Mute Reason"):
                try:
                    with sqlite3.connect("sepco_meters.db") as conn:
                        conn.execute(
                            "UPDATE meter_data SET mute_reason = ? WHERE Reference_no = ?", 
                            (selected_reason, st.session_state.ref_no_searched)
                        )
                        conn.commit()
                    # Update search results with new mute reason
                    st.session_state.search_results.iloc[0]["mute_reason"] = selected_reason
                    st.session_state.mute_reason_submitted = True
                    st.session_state.selected_reason = selected_reason
                    st.success(f"✅ Mute reason updated to: **{selected_reason}**")
                except Exception as e:
                    st.error(f"⚠️ Failed to update mute reason: {str(e)}")

    # Show confirmation if mute reason was submitted
    if st.session_state.mute_reason_submitted:
        st.info(f"🛑 Mute reason set: **{st.session_state.selected_reason}**")