# Batho Pele Hospital Intake AI 🏥🇿🇦

An AI-powered system that supports public hospitals in South Africa by verifying patient eligibility at the gate and ensuring equitable, ethical use of limited healthcare resources.

## 🔍 Problem

Public hospitals are overwhelmed by undocumented or unverified patients, resulting in bed shortages, medicine stock-outs, and diminished access for citizens.

## 🎯 Solution

- Verifies ID/passport/asylum documents
- Classifies patients: South African, Legal Immigrant, Undocumented
- Determines if patient should:
  - Receive free care
  - Pay partial or full fee
  - Be referred for manual admin review

## ⚙️ Tech Stack

- Frontend: Streamlit
- Backend: Flask / FastAPI
- AI: Rule-based logic
- DB: PostgreSQL / MySQL
- Deployment: Heroku or Google Cloud

## 🧠 AI Workflow

1. Scan ID / input data
2. Validate document
3. Run eligibility check
4. Output recommendation
5. Log data and alert if suspicious

## 📊 Features

- Identity Document Scanner
- Eligibility Classifier
- Admin Dashboard
- Red Flag Alerts
- Secure Data Handling (POPIA-compliant)

## 🌍 UN SDG Alignment

- SDG 3: Good Health & Well-being  
- SDG 10: Reduced Inequalities  
- SDG 16: Strong Institutions

## 🚀 Getting Started

Clone the repo, install requirements, and run Streamlit app:

```bash
git clone https://github.com/your-username/batho-pele-app.git
cd batho-pele-app
pip install -r requirements.txt
streamlit run app.py
