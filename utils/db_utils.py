# 📁 utils/db_utils.py

import sqlite3
import pandas as pd

DB_PATH = "sepco_meters.db"

def load_customer_by_ref(ref_no):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT rowid, * FROM meter_data WHERE Reference_no = ?",
        conn,
        params=(ref_no,)
    )
    conn.close()
    return df

def update_mute_reason(reference_no, reason):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE meter_data SET mute_reason = ? WHERE Reference_no = ? AND (mute_reason IS NULL OR mute_reason = '')",
        (reason, reference_no)
    )
    conn.commit()
    conn.close()
