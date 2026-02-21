# SEPCO Mute Meter Monitoring Dashboard

## Overview
Developed during an internship at the Management Information System Department of the Sukkur Electric Power Company (SEPCO). This web-based application replaces manual tracking processes with a centralized digital dashboard, streamlining the identification, tracking, and resolution of "mute" (non-communicative) electric meters across operational zones. 



## Tech Stack
* **Language:** Python
* **Frontend Framework:** Streamlit
* **Database:** SQLite
* **Data Processing & Export:** Pandas, OpenPyXL

## Key Features
* **Secure Data Management:** Allows authorized administrative staff to securely upload, update, filter, and export field data.
* **Automated Reporting:** Generates downloadable Excel reports for field teams to take corrective actions on mute meters.
* **Accessible UI:** Features a branded, bilingual interface (English and Urdu) with light/dark mode compatibility and collapsible modular sections for clean navigation.
* **Iterative Deployment:** Developed using a modular approach and deployed via Streamlit Cloud for staging and review.

## How to Run Locally
1. Clone the repository: `git clone https://github.com/zainulabdin995/sepco-mute-meter-dashboard.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Launch the web application: `streamlit run src/app.py`
4. Access the dashboard via your local browser at `http://localhost:8501`.
