import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Custom CSS for styling ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f1ec;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        padding: 20px 50px;
    }
    .stButton>button {
        background-color: #8B5E3C;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        font-size: 16px;
        margin-top: 10px;
    }
    .stTextInput>div>input, .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 8px;
    }
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Page Config ---
st.set_page_config(page_title="Batho Pele Intake AI", layout="wide")

# --- Paths and Data ---
DATA_DIR = "data"
LOG_PATH = os.path.join(DATA_DIR, "intake_logs.csv")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

try:
    df_logs = pd.read_csv(LOG_PATH, encoding="utf-8-sig")
    # Ensure the expected columns exist
    expected_cols = ["name","nationality","doc_type","doc_number","legal_status","result","timestamp"]
    if not all(col in df_logs.columns for col in expected_cols):
        st.warning("Warning: intake_logs.csv missing expected columns. Reinitializing logs.")
        df_logs = pd.DataFrame(columns=expected_cols)
except FileNotFoundError:
    df_logs = pd.DataFrame(columns=["name","nationality","doc_type","doc_number","legal_status","result","timestamp"])

# --- Header with Logo and Doctor Photo ---
col1, col2 = st.columns([3, 1])
with col1:
    st.image("Batho_pele.png", width=180)  # Your logo file here
    st.title("🩺 Batho Pele Hospital Intake AI")
    st.write("Supporting fair, ethical hospital intake decisions to preserve healthcare resources.")
with col2:
    st.image("Hospital-1.jpg", width=130, caption="Dr. N. Mokoena, Chief Medical Officer")  # Doctor image file

# --- Summary Metrics ---
total_patients = len(df_logs)

st.write("Current log columns:", df_logs.columns.tolist())
st.write("Number of rows in logs:", total_patients)

if 'result' in df_logs.columns:
    eligible_patients = df_logs['result'].astype(str).str.contains("Eligible").sum() if not df_logs.empty else 0
    manual_reviews = df_logs['result'].astype(str).str.contains("Manual Review").sum() if not df_logs.empty else 0
else:
    eligible_patients = 0
    manual_reviews = 0

m1, m2, m3 = st.columns(3)
m1.metric("Total Patients Processed", total_patients)
m2.metric("Eligible for Care", eligible_patients)
m3.metric("Needs Manual Review", manual_reviews)

st.markdown("---")

# --- Intake Form ---
with st.expander("📋 Patient Intake Form", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name")
        nationality = st.selectbox("Nationality", [
            "South African", "Zimbabwe", "Mozambique", "Somalia", "Bangladesh",
            "Lesotho", "Malawi", "Nigeria", "Congo", "Other"
        ])
    with col2:
        doc_type = st.selectbox("Document Type", [
            "RSA ID", "Passport", "Permit", "Asylum", "No Document"
        ])
        doc_number = st.text_input("Document Number")

submit = st.button("🔍 Check Eligibility")

# --- Eligibility Logic ---
def classify_patient(nationality, doc_type, legal_status):
    if nationality == "South African" and doc_type == "RSA ID" and legal_status == "Valid":
        return "✅ Eligible for Free Public Healthcare"
    elif doc_type in ["Permit", "Asylum"] and legal_status == "Valid":
        return "🟡 Eligible for Subsidized or Emergency Care"
    elif doc_type in ["Passport", "No Document"] or legal_status == "Invalid":
        return "🔴 Payment Required or Refer to Admin"
    else:
        return "⚠️ Needs Manual Review"

# --- Simulated Home Affairs Verification (mock) ---
def verify_legal_status(name, nationality, doc_type, doc_number):
    try:
        df = pd.read_csv("mock_home_affairs.csv")
        name_clean = name.strip().lower()
        nationality_clean = nationality.strip().lower()
        doc_type_clean = doc_type.strip().lower()
        doc_number_clean = doc_number.strip()

        match = df[
            (df['full_name'].str.lower() == name_clean) &
            (df['nationality'].str.lower() == nationality_clean) &
            (df['doc_type'].str.lower() == doc_type_clean) &
            (df['doc_number'] == doc_number_clean)
        ]
        if not match.empty:
            return match.iloc[0]['legal_status']
        else:
            return "Unknown"
    except Exception as e:
        return f"Error: {e}"

# --- Log Result Function ---
def log_result(name, nationality, doc_type, doc_number, legal_status, result):
    new_log = pd.DataFrame([{
        "name": name,
        "nationality": nationality,
        "doc_type": doc_type,
        "doc_number": doc_number,
        "legal_status": legal_status,
        "result": result,
        "timestamp": datetime.now()
    }])
    write_header = not os.path.exists(LOG_PATH)
    new_log.to_csv(LOG_PATH, mode='a', index=False, header=write_header)

# --- On Submit ---
if submit:
    if not name or not doc_number:
        st.error("Please enter all required fields (Name and Document Number).")
    else:
        legal_status = verify_legal_status(name, nationality, doc_type, doc_number)
        result = classify_patient(nationality, doc_type, legal_status)

        st.subheader(f"🩺 Eligibility Result for {name}:")
        st.info(result)
        st.caption(f"🛂 Verified Legal Status: **{legal_status}**")

        # Log and reload logs to update metrics and sidebar display immediately
        log_result(name, nationality, doc_type, doc_number, legal_status, result)
        df_logs = pd.read_csv(LOG_PATH, encoding="utf-8-sig")

st.markdown("---")

# --- Sidebar Admin Tools ---
with st.sidebar:
    st.header("👩🏽‍⚕️ Admin Tools")
    if st.checkbox("Show Logged Patients"):
        st.dataframe(df_logs)

    if st.button("Download Logs CSV"):
        csv = df_logs.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="intake_logs.csv", mime="text/csv")

    st.markdown("---")
    st.write("Contact: support@bathopele.gov.za")

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 Batho Pele Initiative | support@bathopele.gov.za")