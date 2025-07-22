import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from helpers.navigation import setup_navigation
from helpers.auth import check_authentication

# 1. Page config (must be first)
st.set_page_config(
    page_title="SEPCO Dashboard - Mute Analytics",
    layout="wide"
)

# 2. Authentication check
check_authentication()

# 3. Setup custom navigation (hides auto sidebar)
setup_navigation()

# 4. Set current page
st.session_state.current_page = "Mute Analytics"

# Page content
st.title("📊 Mute Analytics")

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

# Load data with caching
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    try:
        with sqlite3.connect("sepco_meters.db") as conn:
            df = pd.read_sql_query("SELECT * FROM meter_data", conn)
        df['mute_reason'] = df['mute_reason'].replace('', 'None')
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        return pd.DataFrame()

df = load_data()
df = filter_data(df)

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filter Options")
    
    # Circle filter
    circle_options = ["All"] + sorted(df['Circle'].dropna().unique().tolist())
    circle = st.selectbox("Select Circle:", circle_options)
    if circle != "All":
        df = df[df['Circle'] == circle]
    
    # Division filter
    division_options = ["All"] + sorted(df['Division'].dropna().unique().tolist())
    division = st.selectbox("Select Division:", division_options)
    if division != "All":
        df = df[df['Division'] == division]
    
    # Sub-Division filter
    subdiv_options = ["All"] + sorted(df['Sub-Division'].dropna().unique().tolist())
    subdiv = st.selectbox("Select Sub-Division:", subdiv_options)
    if subdiv != "All":
        df = df[df['Sub-Division'] == subdiv]
    
    # Feeder filter
    feeder_options = ["All"] + sorted(df['Feeder'].dropna().unique().tolist())
    feeder = st.selectbox("Select Feeder:", feeder_options)
    if feeder != "All":
        df = df[df['Feeder'] == feeder]

# Filter only mute meters
mute_df = df[df['mute_reason'].notnull() & (df['mute_reason'] != 'None')]

if mute_df.empty:
    st.warning("No mute meters available for selected filters.")
    st.stop()

# Main content layout
tab1, tab2 = st.tabs(["📊 Mute Reasons Analysis", "🗺️ Geographic Distribution"])

with tab1:
    # Bar Graph: Top Mute Reasons
    st.subheader("🔧 Top Mute Reasons")
    mute_counts = mute_df['mute_reason'].value_counts().reset_index()
    mute_counts.columns = ['Mute Reason', 'Count']
    
    # Sort by count and limit to top 20 for better visualization
    mute_counts = mute_counts.sort_values('Count', ascending=False).head(20)
    
    fig_mute = px.bar(
        mute_counts, 
        x='Mute Reason', 
        y='Count', 
        color='Mute Reason',
        text='Count',
        height=500
    )
    fig_mute.update_traces(textposition='outside')
    fig_mute.update_layout(
        xaxis_title="Mute Reason",
        yaxis_title="Count",
        showlegend=False,
        xaxis={'categoryorder':'total descending'}
    )
    st.plotly_chart(fig_mute, use_container_width=True)

    # Data table
    st.subheader("📋 Detailed Mute Meter Data")
    st.dataframe(
        mute_df[['Reference_no', 'Name', 'Circle', 'Division', 'Sub-Division', 'Feeder', 'mute_reason']],
        use_container_width=True,
        height=400
    )

with tab2:
    # Map: Mute Meter Locations
    st.subheader("🗺️ Mute Meter Geographic Distribution")
    mute_map = mute_df.dropna(subset=['Latitude', 'Longitude'])
    
    if not mute_map.empty:
        fig_map = px.scatter_mapbox(
            mute_map,
            lat='Latitude',
            lon='Longitude',
            color='mute_reason',
            hover_data=['Reference_no', 'Name', 'Feeder', 'Division'],
            mapbox_style="open-street-map",
            zoom=5,
            height=600
        )
        fig_map.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            mapbox=dict(center=dict(lat=mute_map['Latitude'].mean(), lon=mute_map['Longitude'].mean()))
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No valid GPS coordinates available for the selected mute meters.")

# Download button for filtered data
st.sidebar.download_button(
    label="📥 Download Filtered Data",
    data=mute_df.to_csv(index=False).encode('utf-8'),
    file_name=f"mute_meters_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
    mime='text/csv'
)