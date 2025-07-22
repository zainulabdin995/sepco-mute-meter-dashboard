import streamlit as st
import pandas as pd
import sqlite3
from helpers.navigation import setup_navigation
from helpers.auth import check_authentication
from io import BytesIO

# 1. Page config (must be first)
st.set_page_config(
    page_title="SEPCO Dashboard - Data Export",
    layout="wide"
)

# 2. Authentication check
check_authentication()

# 3. Setup custom navigation (hides auto sidebar)
setup_navigation()

# 4. Set current page
st.session_state.current_page = "Data Export"

# Page content
st.title("📤 Data Export")

# Load data with caching and error handling
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    try:
        with sqlite3.connect("sepco_meters.db") as conn:
            df = pd.read_sql_query("SELECT * FROM meter_data", conn)
        df['mute_reason'] = df['mute_reason'].replace('', 'None')
        return df
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        return pd.DataFrame()

def filter_data(df):
    # Check if user is admin or if access exists in session state
    if st.session_state.user_role == "admin":
        return df  # Admins see all data
    
    # Safely check for access object
    if not hasattr(st.session_state, 'access'):
        st.error("Access permissions not properly initialized")
        st.stop()
    
    access = st.session_state.access
    
    # Apply filters only if they exist in the access object
    if access.get('circle'):
        df = df[df['Circle'] == access['circle']]
    if access.get('division'):
        df = df[df['Division'] == access['division']]
    if access.get('subdivision'):
        df = df[df['Sub-Division'] == access['subdivision']]
    if access.get('feeder'):
        df = df[df['Feeder'] == access['feeder']]
    
    return df

df = load_data()
df = filter_data(df)

# Filter options in expandable section
with st.expander("🔍 Filter Options", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        circle = st.selectbox(
            "Select Circle:", 
            ["All"] + sorted(df['Circle'].dropna().unique().tolist())
        )
        division = st.selectbox(
            "Select Division:", 
            ["All"] + sorted(df['Division'].dropna().unique().tolist())
        )
    
    with col2:
        subdiv = st.selectbox(
            "Select Sub-Division:", 
            ["All"] + sorted(df['Sub-Division'].dropna().unique().tolist())
        )
        feeder = st.selectbox(
            "Select Feeder:", 
            ["All"] + sorted(df['Feeder'].dropna().unique().tolist())
        )

# Apply filters
filtered_df = df.copy()
if circle != "All":
    filtered_df = filtered_df[filtered_df['Circle'] == circle]
if division != "All":
    filtered_df = filtered_df[filtered_df['Division'] == division]
if subdiv != "All":
    filtered_df = filtered_df[filtered_df['Sub-Division'] == subdiv]
if feeder != "All":
    filtered_df = filtered_df[filtered_df['Feeder'] == feeder]

# Data type selection
data_type = st.radio(
    "Select data type to export:",
    ["All Data", "Mute Meters Only"],
    horizontal=True
)

if data_type == "Mute Meters Only":
    export_df = filtered_df[filtered_df['mute_reason'].notnull() & (filtered_df['mute_reason'] != 'None')]
else:
    export_df = filtered_df

# Display results and export options
if export_df.empty:
    st.warning("⚠️ No records found matching your filters")
else:
    st.success(f"✅ Found {len(export_df)} records matching your criteria")
    
    with st.expander("🔍 Preview Data"):
        st.dataframe(
            export_df,
            height=400,
            use_container_width=True
        )
    
    # Export options
    st.markdown("### 📤 Export Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Excel export
        excel_buffer = BytesIO()
        export_df.to_excel(excel_buffer, index=False)
        st.download_button(
            label="💾 Download as Excel",
            data=excel_buffer.getvalue(),
            file_name="sepco_data_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        # CSV export
        csv_buffer = BytesIO()
        export_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv_buffer.getvalue(),
            file_name="sepco_data_export.csv",
            mime="text/csv"
        )
    
    with col3:
        # JSON export
        json_buffer = BytesIO()
        export_df.to_json(json_buffer, orient='records')
        st.download_button(
            label="📊 Download as JSON",
            data=json_buffer.getvalue(),
            file_name="sepco_data_export.json",
            mime="application/json"
        )

    # Additional statistics
    st.markdown("### 📊 Quick Statistics")
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    
    with stats_col1:
        st.metric("Total Records", len(export_df))
    
    with stats_col2:
        if 'mute_reason' in export_df.columns:
            mute_count = len(export_df[export_df['mute_reason'].notnull() & (export_df['mute_reason'] != 'None')])
            st.metric("Mute Meters", mute_count)
    
    with stats_col3:
        if 'Tariff' in export_df.columns:
            tariff_types = len(export_df['Tariff'].unique())
            st.metric("Tariff Types", tariff_types)