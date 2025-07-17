# File: pages/2_Mute_Analytics.py

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Mute Analytics", layout="wide")
st.title("📊 Mute Reason Analytics Dashboard")

# --- Load Data ---
@st.cache_data
def load_data():
    conn = sqlite3.connect("sepco_meters.db")
    df = pd.read_sql_query("SELECT * FROM meter_data", conn)
    conn.close()
    df['mute_reason'] = df['mute_reason'].replace('', 'None')
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")
circle = st.sidebar.selectbox("Select Circle:", ["All"] + sorted(df['Circle'].dropna().unique().tolist()))
if circle != "All":
    df = df[df['Circle'] == circle]

division = st.sidebar.selectbox("Select Division:", ["All"] + sorted(df['Division'].dropna().unique().tolist()))
if division != "All":
    df = df[df['Division'] == division]

subdiv = st.sidebar.selectbox("Select Sub-Division:", ["All"] + sorted(df['Sub-Division'].dropna().unique().tolist()))
if subdiv != "All":
    df = df[df['Sub-Division'] == subdiv]

feeder = st.sidebar.selectbox("Select Feeder:", ["All"] + sorted(df['Feeder'].dropna().unique().tolist()))
if feeder != "All":
    df = df[df['Feeder'] == feeder]

# --- Filter only mute meters ---
mute_df = df[df['mute_reason'].notnull() & (df['mute_reason'] != 'None')]

if mute_df.empty:
    st.warning("No mute meters available for selected filters.")
    st.stop()

# --- Bar Graph: Top Mute Reasons ---
st.subheader("🔧 Top Mute Reasons")
mute_counts = mute_df['mute_reason'].value_counts().reset_index()
mute_counts.columns = ['Mute Reason', 'Count']
fig_mute = px.bar(mute_counts, x='Mute Reason', y='Count', color='Mute Reason')
st.plotly_chart(fig_mute, use_container_width=True)

# --- Map: Mute Meter Locations ---
st.subheader("🗺️ Mute Meter Map")
mute_map = mute_df.dropna(subset=['Latitude', 'Longitude'])
if not mute_map.empty:
    fig_map = px.scatter_mapbox(
        mute_map,
        lat='Latitude',
        lon='Longitude',
        color='mute_reason',
        hover_data=['Reference_no', 'Name', 'Feeder', 'Division'],
        mapbox_style='open-street-map',
        zoom=5,
        height=500
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("No valid GPS data available for selected mute meters.")
