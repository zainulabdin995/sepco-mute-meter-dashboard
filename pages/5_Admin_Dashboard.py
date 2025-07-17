# File: Admin_Dashboard.py

import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Admin Portal", layout="wide")
st.title("🔐 Admin Dashboard")

# --- Session State ---
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# --- Admin Login ---
if not st.session_state.admin_logged_in:
    with st.form("login_form", clear_on_submit=False):
        st.subheader("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username == "admin" and password == "admin123":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

# --- Admin Panel ---
st.sidebar.success("Admin Access Granted ✅")
st.subheader("🔧 Admin Tools")

# --- 🔄 Mute Reason Editor ---
with st.expander("🛠️ Update Mute Reason by Reference No."):
    ref_input = st.text_input("Enter Reference Number to Search:")
    if ref_input:
        conn = sqlite3.connect("sepco_meters.db")
        cursor = conn.cursor()
        query = "SELECT `Reference_no`, `Name`, `mute_reason` FROM meter_data WHERE `Reference_no` = ?"
        result = cursor.execute(query, (ref_input.strip(),)).fetchone()

        if result:
            ref_no, name, current_reason = result
            st.write(f"**Name**: {name}")
            st.write(f"**Current Mute Reason**: {current_reason if current_reason else 'None'}")

            new_reason = st.text_input("New Mute Reason (leave blank to remove):", value=current_reason or "")
            if st.button("Update Mute Reason"):
                updated_value = None if new_reason.strip() == "" else new_reason.strip()
                cursor.execute("UPDATE meter_data SET mute_reason = ? WHERE Reference_no = ?", (updated_value, ref_input.strip()))
                conn.commit()
                conn.close()
                st.success("Mute reason updated successfully.")
        else:
            st.error("Reference Number not found.")

# --- 📥 Data Import Section ---
with st.expander("📥 Import Meter Data (CSV or Excel)"):
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                new_data = pd.read_csv(uploaded_file, dtype={'Reference_no': str})
            else:
                new_data = pd.read_excel(uploaded_file, dtype={'Reference_no': str})

            new_data['Reference_no'] = new_data['Reference_no'].astype(str).str.strip()
            st.write("📋 File Preview:", new_data.head())

            required_columns = {
                "Reference_no", "Name", "Circle", "Division", "Sub-Division",
                "Feeder", "Latitude", "Longitude", "mute_reason"
            }

            if not required_columns.issubset(new_data.columns):
                st.error(f"❌ Missing required columns. Required: {', '.join(required_columns)}")
                st.stop()

            conn = sqlite3.connect("sepco_meters.db")
            existing_refs = pd.read_sql_query("SELECT Reference_no FROM meter_data", conn)
            existing_ref_set = set(existing_refs['Reference_no'].astype(str).str.strip())

            new_unique_rows = new_data[~new_data['Reference_no'].isin(existing_ref_set)]

            if not new_unique_rows.empty:
                new_unique_rows.to_sql("meter_data", conn, if_exists='append', index=False)
                st.success(f"✅ Imported {len(new_unique_rows)} new records.")
            else:
                st.info("ℹ️ No new records to import. All Reference Numbers already exist.")

            st.warning(f"🚫 Skipped {len(new_data) - len(new_unique_rows)} duplicate rows based on Reference_no.")
            conn.close()

        except Exception as e:
            st.error(f"❌ Error during import: {e}")

# --- 📤 Export & Delete Section ---
with st.expander("📤 Export & Delete Mute Meter Data"):
    def load_filtered_data():
        conn = sqlite3.connect("sepco_meters.db")
        df = pd.read_sql_query("SELECT * FROM meter_data", conn)
        conn.close()

        # Apply filters
        if circle != "All":
            df = df[df['Circle'] == circle]
        if division != "All":
            df = df[df['Division'] == division]
        if subdiv != "All":
            df = df[df['Sub-Division'] == subdiv]
        if feeder != "All":
            df = df[df['Feeder'] == feeder]

        # Filter only rows with mute reason
        return df[df['mute_reason'].notnull() & (df['mute_reason'].str.strip() != '')]

    # Load data once
    conn = sqlite3.connect("sepco_meters.db")
    full_df = pd.read_sql_query("SELECT * FROM meter_data", conn)
    conn.close()

    st.markdown("### 🔍 Filter Options")
    circle = st.selectbox("Select Circle:", ["All"] + sorted(full_df['Circle'].dropna().unique().tolist()))
    division = st.selectbox("Select Division:", ["All"] + sorted(full_df['Division'].dropna().unique().tolist()))
    subdiv = st.selectbox("Select Sub-Division:", ["All"] + sorted(full_df['Sub-Division'].dropna().unique().tolist()))
    feeder = st.selectbox("Select Feeder:", ["All"] + sorted(full_df['Feeder'].dropna().unique().tolist()))

    filtered_df = load_filtered_data()

    if filtered_df.empty:
        st.info("ℹ️ No mute meter records found for the selected filters.")
    else:
        st.success(f"✅ {len(filtered_df)} mute records found for selected filters.")
        st.dataframe(filtered_df)

        export_path = "filtered_export.xlsx"
        filtered_df.to_excel(export_path, index=False)

        with open(export_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Filtered Mute Data",
                data=f,
                file_name="filtered_mute_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.markdown("---")
        st.warning("⚠️ Deleting will permanently remove the above exported records from the database.")
        confirm = st.checkbox("I understand. Delete exported records.")

        if confirm and st.button("🗑️ Delete Exported Records"):
            try:
                conn = sqlite3.connect("sepco_meters.db")
                cursor = conn.cursor()
                ref_list = tuple(filtered_df['Reference_no'].astype(str).tolist())
                if ref_list:
                    query = f"DELETE FROM meter_data WHERE Reference_no IN ({','.join(['?']*len(ref_list))})"
                    cursor.execute(query, ref_list)
                    conn.commit()
                    st.success(f"🗑️ Successfully deleted {len(ref_list)} records.")
                    st.rerun()
                conn.close()
            except Exception as e:
                st.error(f"❌ Error deleting records: {e}")
