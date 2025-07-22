import streamlit as st
import pandas as pd
import sqlite3
import bcrypt
from helpers.navigation import setup_navigation
from helpers.auth import check_authentication

# PAGE CONFIG
st.set_page_config(page_title="SEPCO Dashboard - Admin Portal", layout="wide")
check_authentication()

if st.session_state.get('user_role') != "admin":
    st.error("⛔ Access Denied: Admin privileges required")
    st.switch_page("pages/0_Welcome.py")
    st.stop()

setup_navigation()
st.session_state.current_page = "Admin Dashboard"
st.title("🔐 Admin Dashboard")

# Helpers
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def load_filter_options():
    try:
        with sqlite3.connect("sepco_meters.db") as conn:
            df = pd.read_sql_query(
                "SELECT Circle, Division, `Sub-Division`, Feeder FROM meter_data", conn
            )
        return {
            'circles': ["All"] + sorted(df['Circle'].dropna().unique().tolist()),
            'divisions': ["All"] + sorted(df['Division'].dropna().unique().tolist()),
            'subdivisions': ["All"] + sorted(df['Sub-Division'].dropna().unique().tolist()),
            'feeders': ["All"] + sorted(df['Feeder'].dropna().unique().tolist())
        }
    except:
        return {'circles': ["All"], 'divisions': ["All"], 'subdivisions': ["All"], 'feeders': ["All"]}

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["👥 User Management", "🛠️ Mute Reason Editor", "📥 Data Import", "📤 Data Export"])

with tab1:
    st.subheader("User Management")

    # Add User
    with st.expander("➕ Add New User", expanded=True):
        with st.form("add_user_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["user", "admin"])
            filters = load_filter_options()
            col1, col2 = st.columns(2)
            with col1:
                circle = st.selectbox("Circle", filters['circles'])
                division = st.selectbox("Division", filters['divisions'])
            with col2:
                subdivision = st.selectbox("Sub-Division", filters['subdivisions'])
                feeder = st.selectbox("Feeder", filters['feeders'])

            if st.form_submit_button("Add User"):
                if len(password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    try:
                        hashed = hash_password(password)
                        with sqlite3.connect("sepco_meters.db") as conn:
                            conn.execute("""
                                INSERT INTO users (email, password, role, circle, division, subdivision, feeder)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                email.strip(), hashed, role,
                                None if circle == "All" else circle,
                                None if division == "All" else division,
                                None if subdivision == "All" else subdivision,
                                None if feeder == "All" else feeder
                            ))
                            conn.commit()
                        st.success("✅ User added")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Email already exists")
                    except Exception as e:
                        st.error(str(e))

    # View/Edit/Delete
    with st.expander("📋 View/Edit/Delete Users", expanded=True):
        try:
            with sqlite3.connect("sepco_meters.db") as conn:
                df = pd.read_sql_query(
                    "SELECT id, email, role, circle, division, subdivision, feeder FROM users", conn
                )

            st.dataframe(df.drop(columns=['id']), use_container_width=True, height=300)
            selected_email = st.selectbox("Select User", df['email'].tolist())

            if selected_email:
                user = df[df['email'] == selected_email].iloc[0]
                with st.form("edit_user_form"):
                    new_email = st.text_input("Email", value=user['email'])
                    new_password = st.text_input("New Password (leave blank to keep)", type="password")
                    new_role = st.selectbox("Role", ["user", "admin"], index=0 if user['role'] == "user" else 1)
                    filters = load_filter_options()
                    col1, col2 = st.columns(2)
                    with col1:
                        new_circle = st.selectbox("Circle", filters['circles'], index=filters['circles'].index(user['circle'] or "All"))
                        new_division = st.selectbox("Division", filters['divisions'], index=filters['divisions'].index(user['division'] or "All"))
                    with col2:
                        new_subdivision = st.selectbox("Sub-Division", filters['subdivisions'], index=filters['subdivisions'].index(user['subdivision'] or "All"))
                        new_feeder = st.selectbox("Feeder", filters['feeders'], index=filters['feeders'].index(user['feeder'] or "All"))

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update User"):
                            try:
                                with sqlite3.connect("sepco_meters.db") as conn:
                                    if new_password:
                                        hashed = hash_password(new_password)
                                        conn.execute("""
                                            UPDATE users SET email=?, password=?, role=?, circle=?, division=?, subdivision=?, feeder=?
                                            WHERE id=?
                                        """, (
                                            new_email.strip(), hashed, new_role,
                                            None if new_circle == "All" else new_circle,
                                            None if new_division == "All" else new_division,
                                            None if new_subdivision == "All" else new_subdivision,
                                            None if new_feeder == "All" else new_feeder,
                                            int(user['id'])
                                        ))
                                    else:
                                        conn.execute("""
                                            UPDATE users SET email=?, role=?, circle=?, division=?, subdivision=?, feeder=?
                                            WHERE id=?
                                        """, (
                                            new_email.strip(), new_role,
                                            None if new_circle == "All" else new_circle,
                                            None if new_division == "All" else new_division,
                                            None if new_subdivision == "All" else new_subdivision,
                                            None if new_feeder == "All" else new_feeder,
                                            int(user['id'])
                                        ))
                                    conn.commit()
                                st.success("✅ User updated")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

                    with col2:
                        if st.form_submit_button("Delete User"):
                            try:
                                with sqlite3.connect("sepco_meters.db") as conn:
                                    conn.execute("DELETE FROM users WHERE id = ?", (int(user['id']),))
                                    conn.commit()
                                st.success("✅ User deleted")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

        except Exception as e:
            st.error(f"Error loading users: {str(e)}")


with tab2:
    # Mute Reason Editor
    st.subheader("Mute Reason Editor")
    
    with st.expander("🔍 Search and Update Mute Reason", expanded=True):
        ref_input = st.text_input(
            "Enter Reference Number to Search:",
            help="Enter the exact meter reference number"
        )
        
        if ref_input:
            try:
                with sqlite3.connect("sepco_meters.db") as conn:
                    cursor = conn.cursor()
                    query = """SELECT Reference_no, Name, mute_reason 
                               FROM meter_data 
                               WHERE Reference_no = ?"""
                    result = cursor.execute(query, (ref_input.strip(),)).fetchone()
                
                if result:
                    ref_no, name, current_reason = result
                    st.write(f"**Name**: {name}")
                    st.write(f"**Current Mute Reason**: {current_reason if current_reason else 'None'}")
                    
                    new_reason = st.text_input(
                        "New Mute Reason (leave blank to remove):",
                        value=current_reason or ""
                    )
                    
                    if st.button("Update Mute Reason"):
                        updated_value = None if new_reason.strip() == "" else new_reason.strip()
                        with sqlite3.connect("sepco_meters.db") as conn:
                            conn.execute(
                                "UPDATE meter_data SET mute_reason = ? WHERE Reference_no = ?",
                                (updated_value, ref_input.strip())
                            )
                            conn.commit()
                        st.success("✅ Mute reason updated successfully")
                        st.rerun()
                else:
                    st.error("❌ Reference Number not found")
            except Exception as e:
                st.error(f"❌ Error updating mute reason: {str(e)}")

with tab3:
    # Data Import Section
    st.subheader("Data Import")
    
    with st.expander("📥 Import Meter Data", expanded=True):
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file", 
            type=["csv", "xlsx"],
            help="File must contain required columns"
        )
        
        if uploaded_file:
            try:
                # Read uploaded file
                if uploaded_file.name.endswith('.csv'):
                    new_data = pd.read_csv(uploaded_file, dtype={'Reference_no': str})
                else:
                    new_data = pd.read_excel(uploaded_file, dtype={'Reference_no': str})
                
                # Clean data
                new_data['Reference_no'] = new_data['Reference_no'].astype(str).str.strip()
                
                # Check required columns
                required_columns = {
                    "Reference_no", "Name", "Circle", "Division", "Sub-Division",
                    "Feeder", "Latitude", "Longitude", "mute_reason"
                }
                if not required_columns.issubset(new_data.columns):
                    missing = required_columns - set(new_data.columns)
                    st.error(f"❌ Missing required columns: {', '.join(missing)}")
                else:
                    # Check for duplicates
                    with sqlite3.connect("sepco_meters.db") as conn:
                        existing_refs = pd.read_sql_query(
                            "SELECT Reference_no FROM meter_data", 
                            conn
                        )
                    
                    existing_ref_set = set(existing_refs['Reference_no'].astype(str).str.strip())
                    new_unique_rows = new_data[~new_data['Reference_no'].isin(existing_ref_set)]
                    
                    if not new_unique_rows.empty:
                        with sqlite3.connect("sepco_meters.db") as conn:
                            new_unique_rows.to_sql(
                                "meter_data", 
                                conn, 
                                if_exists='append', 
                                index=False
                            )
                            conn.commit()
                        st.success(f"✅ Imported {len(new_unique_rows)} new records")
                    else:
                        st.info("ℹ️ No new records to import. All Reference Numbers already exist")
                    
                    st.warning(f"⚠️ Skipped {len(new_data) - len(new_unique_rows)} duplicate rows")
                
            except Exception as e:
                st.error(f"❌ Error during import: {str(e)}")

with tab4:
    # Data Export Section
    st.subheader("Data Export")
    
    try:
        with sqlite3.connect("sepco_meters.db") as conn:
            full_df = pd.read_sql_query("SELECT * FROM meter_data", conn)
        
        # Filter options in columns
        with st.expander("🔍 Filter Options", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                circle = st.selectbox(
                    "Select Circle:", 
                    ["All"] + sorted(full_df['Circle'].dropna().unique().tolist()),
                    key="export_circle"
                )
                division = st.selectbox(
                    "Select Division:", 
                    ["All"] + sorted(full_df['Division'].dropna().unique().tolist()),
                    key="export_division"
                )
            with col2:
                subdiv = st.selectbox(
                    "Select Sub-Division:", 
                    ["All"] + sorted(full_df['Sub-Division'].dropna().unique().tolist()),
                    key="export_subdivision"
                )
                feeder = st.selectbox(
                    "Select Feeder:", 
                    ["All"] + sorted(full_df['Feeder'].dropna().unique().tolist()),
                    key="export_feeder"
                )
        
        # Apply filters
        filtered_df = full_df.copy()
        if circle != "All":
            filtered_df = filtered_df[filtered_df['Circle'] == circle]
        if division != "All":
            filtered_df = filtered_df[filtered_df['Division'] == division]
        if subdiv != "All":
            filtered_df = filtered_df[filtered_df['Sub-Division'] == subdiv]
        if feeder != "All":
            filtered_df = filtered_df[filtered_df['Feeder'] == feeder]
        
        # Filter mute meters only
        mute_df = filtered_df[
            filtered_df['mute_reason'].notnull() & 
            (filtered_df['mute_reason'].str.strip() != '')
        ]
        
        if mute_df.empty:
            st.info("ℹ️ No mute meter records found for the selected filters")
        else:
            st.success(f"✅ Found {len(mute_df)} mute records")
            
            # Preview data in separate expander
            with st.expander("📋 Preview Data", expanded=False):
                st.dataframe(
                    mute_df,
                    use_container_width=True,
                    height=300
                )
            
            # Export options section
            st.markdown("### 📤 Export Options")
            col1, col2 = st.columns(2)
            
            with col1:
                # Excel export
                excel_buffer = BytesIO()
                mute_df.to_excel(excel_buffer, index=False)
                st.download_button(
                    label="💾 Download Excel",
                    data=excel_buffer.getvalue(),
                    file_name="sepco_mute_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col2:
                # CSV export
                csv_buffer = BytesIO()
                mute_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_buffer.getvalue(),
                    file_name="sepco_mute_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Delete section with confirmation
            st.markdown("---")
            st.markdown("### 🗑️ Delete Records")
            st.warning("This action cannot be undone. Deleted records will be permanently removed.")
            
            with st.expander("⚠️ Delete Options", expanded=False):
                confirm = st.checkbox(
                    "I understand this action is irreversible",
                    key="delete_confirm"
                )
                
                if confirm:
                    if st.button(
                        "Permanently Delete Selected Records",
                        type="primary",
                        help="Delete all records matching current filters",
                        use_container_width=True
                    ):
                        try:
                            with sqlite3.connect("sepco_meters.db") as conn:
                                cursor = conn.cursor()
                                ref_list = mute_df['Reference_no'].astype(str).tolist()
                                if ref_list:
                                    query = f"""DELETE FROM meter_data 
                                              WHERE Reference_no IN ({','.join(['?']*len(ref_list))})"""
                                    cursor.execute(query, ref_list)
                                    conn.commit()
                                    st.success(f"✅ Deleted {len(ref_list)} records successfully")
                                    st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error deleting records: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")