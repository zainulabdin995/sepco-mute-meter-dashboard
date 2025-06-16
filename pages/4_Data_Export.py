# 📁 File: pages/4_Data_Export.py

import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="📤 Data Export", layout="wide")
st.title("📤 Export Filtered Meter Data")

# --- Load Data ---
@st.cache_data

def load_data():
    conn = sqlite3.connect("sepco_meters.db")
    df = pd.read_sql("SELECT * FROM meter_data", conn)
    conn.close()
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")

selected_circle = st.sidebar.selectbox("Select Circle:", ["All Circles"] + sorted(df['Circle'].dropna().unique()))
filtered_df = df.copy()
if selected_circle != "All Circles":
    filtered_df = filtered_df[filtered_df['Circle'] == selected_circle]

selected_division = st.sidebar.selectbox("Select Division:", ["All Divisions"] + sorted(filtered_df['Division'].dropna().unique()))
if selected_division != "All Divisions":
    filtered_df = filtered_df[filtered_df['Division'] == selected_division]

selected_subdivision = st.sidebar.selectbox("Select Sub-Division:", ["All Sub-Divisions"] + sorted(filtered_df['Sub-Division'].dropna().unique()))
if selected_subdivision != "All Sub-Divisions":
    filtered_df = filtered_df[filtered_df['Sub-Division'] == selected_subdivision]

selected_feeder = st.sidebar.selectbox("Select Feeder:", ["All Feeders"] + sorted(filtered_df['Feeder'].dropna().unique()))
if selected_feeder != "All Feeders":
    filtered_df = filtered_df[filtered_df['Feeder'] == selected_feeder]

# --- Display Table ---
st.subheader("📋 Filtered Data Preview")
st.dataframe(filtered_df, use_container_width=True)

# --- Export to CSV ---
st.subheader("📥 Download Data")

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(filtered_df)
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="filtered_meter_data.csv",
    mime="text/csv"
)
