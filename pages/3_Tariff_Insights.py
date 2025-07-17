# 📁 File: pages/3_Tariff_Insights.py

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Tariff & Load Insights", layout="wide")
st.title("📈 Tariff & Load Insights")

@st.cache_data

def load_data():
    conn = sqlite3.connect("sepco_meters.db")
    df = pd.read_sql("SELECT * FROM meter_data WHERE `Sr. No.` != '0';", conn)
    conn.close()
    df['Sanction Load'] = pd.to_numeric(df['Sanction Load'], errors='coerce')
    df['Transformer Capacity'] = pd.to_numeric(df['Transformer Capacity'], errors='coerce')
    df['Installation Date'] = pd.to_datetime(df['Installation Date'], errors='coerce')
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Options")
selected_circle = st.sidebar.selectbox("Select Circle:", ["All Circles"] + sorted(df['Circle'].dropna().unique()))
filtered_df = df.copy()
if selected_circle != "All Circles":
    filtered_df = filtered_df[filtered_df['Circle'] == selected_circle]

selected_div = st.sidebar.selectbox("Select Division:", ["All Divisions"] + sorted(filtered_df['Division'].dropna().unique()))
if selected_div != "All Divisions":
    filtered_df = filtered_df[filtered_df['Division'] == selected_div]

selected_subdiv = st.sidebar.selectbox("Select Sub-Division:", ["All Sub-Divisions"] + sorted(filtered_df['Sub-Division'].dropna().unique()))
if selected_subdiv != "All Sub-Divisions":
    filtered_df = filtered_df[filtered_df['Sub-Division'] == selected_subdiv]

selected_feeder = st.sidebar.selectbox("Select Feeder:", ["All Feeders"] + sorted(filtered_df['Feeder'].dropna().unique()))
if selected_feeder != "All Feeders":
    filtered_df = filtered_df[filtered_df['Feeder'] == selected_feeder]

# Charts
st.subheader("📘 Tariff Distribution")
tariff_counts = filtered_df['Tariff'].value_counts().reset_index()
tariff_counts.columns = ['Tariff', 'Count']
fig_tariff = px.bar(tariff_counts, x='Tariff', y='Count', color='Tariff')
st.plotly_chart(fig_tariff, use_container_width=True)

st.subheader("🔌 Transformer Capacity")
cap_by_div = filtered_df.groupby('Division')['Transformer Capacity'].sum().reset_index()
fig_cap = px.bar(cap_by_div, x='Division', y='Transformer Capacity', color='Division')
st.plotly_chart(fig_cap, use_container_width=True)

st.subheader("⚡ Sanction Load Distribution")
fig_sanction = px.histogram(filtered_df, x='Sanction Load', nbins=50)
st.plotly_chart(fig_sanction, use_container_width=True)

st.subheader("📦 Meter Model Distribution")
model_counts = filtered_df['Model'].value_counts().reset_index()
model_counts.columns = ['Model', 'Count']
fig_model = px.bar(model_counts, x='Model', y='Count', color='Model')
st.plotly_chart(fig_model, use_container_width=True)

st.subheader("📅 Installation Trend")
install_trend = filtered_df.groupby(filtered_df['Installation Date'].dt.to_period('M')).size().reset_index(name='Count')
install_trend['Installation Date'] = install_trend['Installation Date'].astype(str)
fig_trend = px.line(install_trend, x='Installation Date', y='Count', title="Installation Over Time")
st.plotly_chart(fig_trend, use_container_width=True)
