import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from helpers.navigation import setup_navigation
from helpers.auth import check_authentication

# 1. Page config (must be first)
st.set_page_config(
    page_title="SEPCO Dashboard - Traffic Insights",
    layout="wide"
)

# 2. Authentication check
check_authentication()

# 3. Setup custom navigation (hides auto sidebar)
setup_navigation()

# 4. Set current page
st.session_state.current_page = "Traffic Insights"

# Page content
st.title("🚦 Traffic Insights")

# Load data with caching and error handling
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    try:
        with sqlite3.connect("sepco_meters.db") as conn:
            df = pd.read_sql("SELECT * FROM meter_data WHERE `Sr. No.` != '0';", conn)
        
        # Data cleaning
        df['Sanction Load'] = pd.to_numeric(df['Sanction Load'], errors='coerce')
        df['Transformer Capacity'] = pd.to_numeric(df['Transformer Capacity'], errors='coerce')
        df['Installation Date'] = pd.to_datetime(df['Installation Date'], errors='coerce')
        
        # Filter based on user access
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
    
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        return pd.DataFrame()

df = load_data()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filter Options")
    
    # Circle filter
    circle_options = ["All"] + sorted(df['Circle'].dropna().unique().tolist())
    selected_circle = st.selectbox("Select Circle:", circle_options)
    
    # Division filter
    division_options = ["All"] + sorted(df['Division'].dropna().unique().tolist())
    selected_div = st.selectbox("Select Division:", division_options)
    
    # Sub-Division filter
    subdiv_options = ["All"] + sorted(df['Sub-Division'].dropna().unique().tolist())
    selected_subdiv = st.selectbox("Select Sub-Division:", subdiv_options)
    
    # Feeder filter
    feeder_options = ["All"] + sorted(df['Feeder'].dropna().unique().tolist())
    selected_feeder = st.selectbox("Select Feeder:", feeder_options)

# Apply filters
filtered_df = df.copy()
if selected_circle != "All":
    filtered_df = filtered_df[filtered_df['Circle'] == selected_circle]
if selected_div != "All":
    filtered_df = filtered_df[filtered_df['Division'] == selected_div]
if selected_subdiv != "All":
    filtered_df = filtered_df[filtered_df['Sub-Division'] == selected_subdiv]
if selected_feeder != "All":
    filtered_df = filtered_df[filtered_df['Feeder'] == selected_feeder]

# Main content tabs
tab1, tab2 = st.tabs(["📊 Tariff Analysis", "⚡ Load Analysis"])

with tab1:
    # Tariff Distribution
    st.subheader("📘 Tariff Category Distribution")
    if not filtered_df.empty:
        tariff_counts = filtered_df['Tariff'].value_counts().reset_index()
        tariff_counts.columns = ['Tariff', 'Count']
        
        fig_tariff = px.pie(
            tariff_counts, 
            names='Tariff', 
            values='Count',
            hole=0.3,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_tariff.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_tariff, use_container_width=True)
        
        # Detailed tariff data
        with st.expander("View Detailed Tariff Data"):
            st.dataframe(
                tariff_counts.sort_values('Count', ascending=False),
                use_container_width=True
            )
    else:
        st.warning("No data available for selected filters")

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Sanction Load Distribution
        st.subheader("🔌 Sanction Load (kW)")
        if not filtered_df.empty:
            fig_sanction = px.histogram(
                filtered_df, 
                x='Sanction Load', 
                nbins=20,
                color_discrete_sequence=['#636EFA']
            )
            fig_sanction.update_layout(
                xaxis_title="Sanction Load (kW)",
                yaxis_title="Number of Meters"
            )
            st.plotly_chart(fig_sanction, use_container_width=True)
    
    with col2:
        # Transformer Capacity
        st.subheader("⚡ Transformer Capacity (kVA)")
        if not filtered_df.empty:
            cap_by_div = filtered_df.groupby('Division')['Transformer Capacity'].sum().reset_index()
            fig_cap = px.bar(
                cap_by_div, 
                x='Division', 
                y='Transformer Capacity',
                color='Division',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_cap.update_layout(
                xaxis_title="Division",
                yaxis_title="Total Capacity (kVA)",
                showlegend=False
            )
            st.plotly_chart(fig_cap, use_container_width=True)
    
    # Installation Trend
    st.subheader("📅 Meter Installation Trend")
    if not filtered_df.empty:
        install_trend = filtered_df.groupby(
            filtered_df['Installation Date'].dt.to_period('M')
        ).size().reset_index(name='Count')
        install_trend['Installation Date'] = install_trend['Installation Date'].astype(str)
        
        fig_trend = px.line(
            install_trend, 
            x='Installation Date', 
            y='Count',
            markers=True,
            color_discrete_sequence=['#00CC96']
        )
        fig_trend.update_layout(
            xaxis_title="Installation Month",
            yaxis_title="Number of Installations"
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# Download button for filtered data
st.sidebar.download_button(
    label="📥 Download Filtered Data",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name=f"tariff_insights_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
    mime='text/csv'
)