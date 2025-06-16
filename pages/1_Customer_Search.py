# 📁 pages/1_Customer_Search.py

import streamlit as st
from utils.db_utils import load_customer_by_ref, update_mute_reason

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

st.title("🔍 Customer Search & Mute Reason Edit")

ref_no = st.text_input("🔢 Enter Customer Reference No.")

if ref_no:
    df = load_customer_by_ref(ref_no)

    if not df.empty:
        st.success("✅ Customer record found")
        st.dataframe(df)

        current_reason = df.iloc[0]["mute_reason"]

        if current_reason and str(current_reason).strip() != "":
            st.info(f"🛑 Mute reason already set: **{current_reason}**")
            st.warning("You cannot edit the mute reason again.")
        else:
            selected_reason = st.selectbox("📌 Select Mute Reason:", MUTE_REASONS)

            if st.button("💾 Submit Mute Reason"):
                update_mute_reason(ref_no, selected_reason)

                # Reload to show new data
                df = load_customer_by_ref(ref_no)
                new_reason = df.iloc[0]["mute_reason"]

                if new_reason and new_reason == selected_reason:
                    st.success(f"✅ Mute reason updated to: **{new_reason}**")
                else:
                    st.error("❌ Failed to update mute reason. It may have already been set.")
    else:
        st.warning("⚠️ No customer found with that Reference No.")
