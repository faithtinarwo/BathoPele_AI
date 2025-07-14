import streamlit as st
import pandas as pd
import hashlib
import logging
from datetime import datetime, timedelta
import pytz
from treatment_ai import generate_treatment_plan
from resource_predictor import predict_resources

# ====== CONSTANTS ======
SA_TIMEZONE = pytz.timezone('Africa/Johannesburg')

# ====== AUTHENTICATION ======
def authenticate_user():
    """User authentication with session management"""
    if not st.session_state.get('authenticated'):
        with st.container():
            st.title("BathoPele_AI Staff Login")
            st.image("assets/Batho_pele.png", use_column_width=True)
            
            with st.form("login"):
                user = st.text_input("Username")
                pwd = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login"):
                    if validate_credentials(user, pwd):
                        st.session_state.authenticated = True
                        st.session_state.username = user
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            return False
    return True

def validate_credentials(username, password):
    """Validate user credentials against stored hashes"""
    credentials = {
        "admin": hashlib.sha256("admin123".encode()).hexdigest(),
        "clerk": hashlib.sha256("clerk123".encode()).hexdigest(),
        "Mpho_Hlalele": "907fbbb4869dc75cb3d3493f580adb2bedbf5da51f5d60465722941a9042fa9c"
    }
    return username in credentials and hashlib.sha256(password.encode()).hexdigest() == credentials[username]

if not authenticate_user():
    st.stop()

# ====== DATA LOADING ======
@st.cache_data(ttl=300)
def load_data():
    """Load all application data with caching"""
    try:
        # Replace with actual CSV/database load in production
        patients_df = pd.DataFrame(columns=['name', 'doc_number', 'doc_type', 'nationality', 'result', 'legal_status', 'timestamp'])
        visits_df = pd.DataFrame(columns=['patient_name', 'visit_date', 'diagnosis', 'treatment', 'cost', 'hospital', 'ward'])
        resources_df = pd.DataFrame(columns=['hospital', 'ward', 'total_beds', 'available_beds', 'medications', 'medication_stock', 'doctors', 'nurses'])
        costs_df = pd.DataFrame(columns=['date', 'amount'])

        # Ensure required columns exist with proper defaults
        patients_df['name'] = patients_df['name'].fillna('Unknown')
        patients_df['doc_number'] = patients_df['doc_number'].fillna('')

        # Fix status errors
        for idx, row in patients_df.iterrows():
            if row['doc_type'] == 'Passport' and row['nationality'] == 'South African':
                patients_df.at[idx, 'result'] = 'Needs Verification'
                patients_df.at[idx, 'legal_status'] = 'Pending'
            elif row['doc_type'] == 'RSA ID' and row['nationality'] != 'South African':
                patients_df.at[idx, 'result'] = 'Needs Verification'
                patients_df.at[idx, 'legal_status'] = 'Pending'

        required_resource_cols = ['hospital', 'ward', 'total_beds', 'available_beds', 
                                 'medications', 'medication_stock', 'doctors', 'nurses']
        for col in required_resource_cols:
            if col not in resources_df.columns:
                resources_df[col] = '' if col in ['medications', 'doctors', 'nurses'] else 0

        visits_df['visit_date'] = pd.to_datetime(
            visits_df.get('visit_date', datetime.now(SA_TIMEZONE).strftime('%Y-%m-%d')),
            errors='coerce'
        ).dt.strftime('%Y-%m-%d')

        costs_df['date'] = pd.to_datetime(
            costs_df.get('date', datetime.now(SA_TIMEZONE).strftime('%Y-%m-%d')),
            errors='coerce'
        )
        costs_df = costs_df[costs_df['date'].notna()]
        costs_df['date'] = costs_df['date'].dt.strftime('%Y-%m-%d')
        costs_df['amount'] = pd.to_numeric(costs_df.get('amount', 0), errors='coerce')

        return patients_df, visits_df, resources_df, costs_df

    except Exception as e:
        logging.error(f"Error loading data: {str(e)}")
        st.error("Failed to load application data")
        st.stop()

try:
    patients_df, visits_df, resources_df, costs_df = load_data()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# ====== UI CONFIG ======
st.set_page_config(layout="wide", page_title="Batho Pele Hospital System")
st.markdown("""
<style>
:root {
    --primary: #003366;
    --secondary: #f0f8ff;
}
.stApp { background-color: var(--secondary); }
.header { background: var(--primary); color: white; padding: 1rem; border-radius: 0 0 15px 15px; }
.stButton>button { background: var(--primary) !important; color: white !important; }
.metric-card { border-left: 5px solid var(--primary); }
.sidebar-button { width: 100%; margin-bottom: 0.5rem; }
.sidebar-metric { font-size: 1.1rem; font-weight: bold; }
.ward-card { border: 1px solid #ddd; border-radius: 5px; padding: 1rem; margin-bottom: 1rem; }
.med-item { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
.doctor-item { margin-bottom: 0.5rem; }
.clickable-metric { cursor: pointer; transition: all 0.3s ease; }
.clickable-metric:hover { background-color: #f0f0f0; }
.treatment-form { background-color: #f9f9f9; padding: 1rem; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# ====== SIDEBAR NAVIGATION ======
with st.sidebar:
    st.image("assets/Batho_pele.png", use_container_width=True)
    st.title(f"Welcome {st.session_state.username}")
    st.divider()
    
    nav_option = st.radio(
        "Navigation Menu",
        ["🏠 Dashboard", "📋 Patient Intake", "👥 Patient Search", "🏥 Resource Monitoring"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.divider()
    st.subheader("Patient Metrics")
    sa_patients = len(patients_df[patients_df['nationality'] == 'South African'])
    foreign_patients = len(patients_df[patients_df['nationality'] != 'South African'])
    needs_referral = len(patients_df[patients_df['legal_status'] == 'Pending'])

    if st.button(f"SA Patients: {sa_patients}", key="sa_patients_btn", use_container_width=True):
        st.session_state.patient_metric_clicked = "sa_patients"
    if st.button(f"🌍 Foreign Nationals: {foreign_patients}", key="foreign_patients_btn", use_container_width=True):
        st.session_state.patient_metric_clicked = "foreign_patients"
    if st.button(f"⚠️ Needs Referral: {needs_referral}", key="referral_patients_btn", use_container_width=True):
        st.session_state.patient_metric_clicked = "needs_referral"

    st.divider()
    st.subheader("Resource Monitoring")
    total_beds = resources_df['available_beds'].sum()
    med_stock = sum(int(x) for med in resources_df['medication_stock'] for x in str(med).split(',') if x.isdigit())
    doctors = sum(len(str(x).split(',')) for x in resources_df['doctors'])
    nurses = sum(len(str(x).split(',')) for x in resources_df['nurses'])

    with st.expander("🏥 Beds by Ward"):
        for _, ward in resources_df.iterrows():
            st.markdown(f"**{ward['ward']}**: {ward['available_beds']}/{ward['total_beds']} available")
    with st.expander("💊 Medication Stock"):
        all_meds = {}
        for _, ward in resources_df.iterrows():
            meds = str(ward['medications']).split(',')
            stocks = str(ward['medication_stock']).split(',')
            for med, stock in zip(meds, stocks):
                if med.strip():
                    all_meds[med.strip()] = all_meds.get(med.strip(), 0) + int(stock.strip() if stock.strip().isdigit() else 0)
        for med, stock in all_meds.items():
            st.markdown(f"**{med}**: {stock}")
    with st.expander("👨‍⚕️ Staff on Duty"):
        all_doctors = set()
        all_nurses = set()
        for _, ward in resources_df.iterrows():
            doctors = str(ward['doctors']).split(',')
            nurses = str(ward['nurses']).split(',')
            all_doctors.update([d.strip() for d in doctors if d.strip()])
            all_nurses.update([n.strip() for n in nurses if n.strip()])
        st.markdown("**Doctors:**")
        for doctor in sorted(all_doctors):
            st.markdown(f"- {doctor}")
        st.markdown("**Nurses:**")
        for nurse in sorted(all_nurses):
            st.markdown(f"- {nurse}")
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ====== MAIN CONTENT ======
page_mapping = {
    "🏠 Dashboard": "dashboard",
    "📋 Patient Intake": "patient_intake",
    "👥 Patient Search": "patient_search",
    "🏥 Resource Monitoring": "resource_monitoring"
}
current_page = page_mapping.get(nav_option, "dashboard")

if current_page == "dashboard":
    with st.container():
        st.markdown('<div class="header"><h1>🏥 Batho Pele Hospital System</h1></div>', unsafe_allow_html=True)
        if st.session_state.get('patient_metric_clicked'):
            if st.session_state.patient_metric_clicked == "sa_patients":
                st.subheader("🇿🇦 South African Patients")
                sa_patients = patients_df[patients_df['nationality'] == 'South African']
                st.dataframe(sa_patients[['name', 'doc_number', 'timestamp']], use_container_width=True)
            elif st.session_state.patient_metric_clicked == "foreign_patients":
                st.subheader("🌍 Foreign National Patients")
                foreign_patients = patients_df[patients_df['nationality'] != 'South African']
                st.dataframe(foreign_patients[['name', 'nationality', 'doc_type', 'doc_number']], use_container_width=True)
            elif st.session_state.patient_metric_clicked == "needs_referral":
                st.subheader("⚠️ Patients Needing Referral to Home Affairs")
                referral_patients = patients_df[patients_df['legal_status'] == 'Pending']
                st.dataframe(referral_patients[['name', 'nationality', 'doc_type', 'doc_number', 'timestamp']], use_container_width=True)
            if st.button("Clear Filter"):
                st.session_state.patient_metric_clicked = None
                st.rerun()
        # Optionally add dashboard widgets here

elif current_page == "patient_intake":
    with st.container():
        st.markdown('<div class="header"><h1>📋 Patient Intake</h1></div>', unsafe_allow_html=True)
        # === TREATMENT PLANS DICTIONARY ===
        treatment_plans = {
            "Hypertension": {
                "plan": "Lifestyle changes (salt reduction, exercise, stress management) and medication based on severity",
                "medications": [
                    {"name": "Amlodipine", "dosage": "5-10 mg", "frequency": "Once daily"},
                    {"name": "Hydrochlorothiazide", "dosage": "12.5-25 mg", "frequency": "Once daily"},
                    {"name": "Enalapril/Losartan", "dosage": "10-40 mg", "frequency": "Once daily"}
                ],
                "costs": {
                    "SA Residents": 0,
                    "Legal Immigrants": 350,
                    "Illegal Immigrants": 800
                }
            },
            "Type 2 Diabetes": {
                "plan": "Diet and lifestyle modification with oral hypoglycemics or insulin therapy",
                "medications": [
                    {"name": "Metformin", "dosage": "500-1000 mg", "frequency": "Twice daily"},
                    {"name": "Glibenclamide", "dosage": "5 mg", "frequency": "Once daily"},
                    {"name": "Insulin", "dosage": "As prescribed", "frequency": "As prescribed"}
                ],
                "costs": {
                    "SA Residents": 0,
                    "Legal Immigrants": 510,
                    "Illegal Immigrants": 1150
                }
            },
            "HIV/AIDS": {
                "plan": "Antiretroviral therapy (ART) with regular monitoring",
                "medications": [
                    {"name": "Tenofovir + Emtricitabine + Efavirenz", "dosage": "1 tablet", "frequency": "Once daily"}
                ],
                "costs": {
                    "SA Residents": 0,
                    "Legal Immigrants": 390,
                    "Illegal Immigrants": 870
                }
            },
            "Tuberculosis (TB)": {
                "plan": "Directly observed therapy (DOT) for 6 months",
                "medications": [
                    {"name": "Isoniazid", "dosage": "300 mg", "frequency": "Daily"},
                    {"name": "Rifampicin", "dosage": "600 mg", "frequency": "Daily"},
                    {"name": "Pyrazinamide", "dosage": "1500 mg", "frequency": "Daily"},
                    {"name": "Ethambutol", "dosage": "1200 mg", "frequency": "Daily"}
                ],
                "costs": {
                    "SA Residents": 0,
                    "Legal Immigrants": 370,
                    "Illegal Immigrants": 850
                }
            },
            "Asthma": {
                "plan": "Avoid triggers and regular use of inhalers",
                "medications": [
                    {"name": "Salbutamol Inhaler", "dosage": "100 mcg/puff", "frequency": "As needed"},
                    {"name": "Beclomethasone Inhaler", "dosage": "100-200 mcg", "frequency": "Twice daily"}
                ],
                "costs": {
                    "SA Residents": 0,
                    "Legal Immigrants": 270,
                    "Illegal Immigrants": 620
                }
            },
            "Common Infections": {
                "plan": "Appropriate antibiotics with follow-up if symptoms persist",
                "medications": [
                    {"name": "Amoxicillin", "dosage": "500 mg", "frequency": "3 times daily"},
                    {"name": "Ciprofloxacin", "dosage": "500 mg", "frequency": "Twice daily"}
                ],
                "costs": {
                    "SA Residents": 0,
                    "Legal Immigrants": 190,
                    "Illegal Immigrants": 450
                }
            },
            "Mental Health": {
                "plan": "Counseling/psychotherapy with medication if required",
                "medications": [
                    {"name": "Fluoxetine", "dosage": "20 mg", "frequency": "Once daily"},
                    {"name": "Amitriptyline", "dosage": "25 mg", "frequency": "Once daily"}
                ],
                "costs": {
                    "SA Residents": 0,
                    "Legal Immigrants": 370,
                    "Illegal Immigrants": 900
                }
            }
        }
        st.title("🏥 Patient Intake System")
        with st.expander("📋 Patient Information", expanded=True):
            with st.form("patient_intake_form"):
                cols = st.columns(2)
                name = cols[0].text_input("Full Name*", placeholder="First Last")
                nationality = cols[0].selectbox("Nationality*", 
                                                ["South African", "Zimbabwean", "Malawian", "Mozambican", "Other"])
                doc_number = cols[0].text_input("Document Number*", placeholder="ID/Passport Number")
                dob_col = cols[1]
                dob_col.markdown("Date of Birth*")
                dob_known = dob_col.checkbox("Known DOB", value=True, key="dob_known")
                if dob_known:
                    dob = dob_col.date_input("", min_value=datetime(1900,1,1), max_value=datetime.now(), label_visibility="collapsed")
                else:
                    dob_col.markdown("Using estimated age (DOB unknown)")
                    age = dob_col.number_input("Estimated Age", min_value=0, max_value=120, value=30)
                    dob = (datetime.now() - timedelta(days=age*365)).date()
                doc_type = cols[1].selectbox("Document Type*", ["RSA ID", "Passport", "Asylum Seeker Permit"])
                medical_aid = cols[1].text_input("Medical Aid Number (if applicable)", placeholder="Leave blank if none")
                conditions = st.text_area("Known Medical Conditions", placeholder="List any known conditions")
                submitted = st.form_submit_button("Submit Patient Information")
            if submitted:
                if not name or not doc_number:
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    try:
                        verification_result = {
                            'result': 'Valid',
                            'legal_status': 'Valid',
                            'details': 'Automatically verified'
                        }
                        if (doc_type == 'RSA ID' and nationality != 'South African') or \
                           (doc_type == 'Passport' and nationality == 'South African'):
                            verification_result['result'] = 'Needs Verification'
                            verification_result['legal_status'] = 'Pending'
                        patient_data = {
                            "name": name,
                            "dob": dob.strftime('%Y-%m-%d') if dob_known else f"Estimated age: {age}",
                            "nationality": nationality,
                            "doc_type": doc_type,
                            "doc_number": doc_number,
                            "medical_aid": medical_aid if medical_aid else "None",
                            "conditions": conditions if conditions else "None reported",
                            "timestamp": datetime.now(SA_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S'),
                            **verification_result
                        }
                        st.session_state.last_patient = patient_data
                        st.success("Patient record created successfully!")
                        st.session_state.show_treatment_form = True
                    except Exception as e:
                        logging.error(f"Error processing patient: {str(e)}")
                        st.error(f"Error processing patient: {str(e)}")
        if st.session_state.get('show_treatment_form', False) and 'last_patient' in st.session_state:
            patient = st.session_state.last_patient
            with st.expander("🩺 Treatment Information", expanded=True):
                diagnosis = st.selectbox("Diagnosis*", list(treatment_plans.keys()) + ["Other"], key="diagnosis_select")
                if diagnosis != "Other":
                    treatment_plan = treatment_plans[diagnosis]["plan"]
                    cost = (
                        treatment_plans[diagnosis]["costs"]["SA Residents"]
                        if patient['nationality'] == 'South African'
                        else treatment_plans[diagnosis]["costs"]["Legal Immigrants"]
                        if patient['legal_status'] == 'Valid'
                        else treatment_plans[diagnosis]["costs"]["Illegal Immigrants"]
                    )
                    st.text_area("Treatment Plan*", value=treatment_plan, key="treatment_plan_area")
                    st.write(f"### Estimated Cost: R{cost:,.2f}")
                    st.write("### Recommended Medications")
                    for med in treatment_plans[diagnosis]["medications"]:
                        st.markdown(f"• **{med['name']}**: {med['dosage']} {med['frequency']}")
                else:
                    treatment_plan = st.text_area("Treatment Plan*")
                    cost = st.number_input("Treatment Cost (R)*", min_value=0, value=1500)
                med_cols = st.columns(3)
                medication = med_cols[0].text_input("Medication name", placeholder="Enter medication")
                dosage = med_cols[1].text_input("Dosage", placeholder="e.g., 500mg")
                frequency = med_cols[2].text_input("Frequency", placeholder="e.g., 3x daily")
                notes = st.text_area("Additional Notes", placeholder="Any special instructions")
                if st.button("Submit Treatment Details"):
                    if not diagnosis or not treatment_plan:
                        st.error("Please fill in required diagnosis and treatment fields")
                    else:
                        try:
                            visit_data = {
                                "patient_name": patient['name'],
                                "diagnosis": diagnosis,
                                "treatment": treatment_plan,
                                "medication": f"{medication} {dosage} {frequency}" if medication else "None",
                                "cost": cost,
                                "notes": notes,
                                "timestamp": datetime.now(SA_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
                            }
                            st.success("Treatment details saved successfully!")
                            st.session_state.treatment_details = visit_data
                            st.session_state.show_actions = True
                        except Exception as e:
                            logging.error(f"Error saving treatment: {str(e)}")
                            st.error(f"Error saving treatment: {str(e)}")
        if st.session_state.get('show_actions', False):
            st.markdown("---")
            st.subheader("Patient Actions")
            action_cols = st.columns(3)
            patient = st.session_state.last_patient
            treatment = st.session_state.treatment_details
            if action_cols[0].button("📄 Generate Invoice"):
                with st.expander("🧾 Invoice", expanded=True):
                    st.subheader(f"Invoice for {patient['name']}")
                    st.write(f"**Date:** {datetime.now(SA_TIMEZONE).strftime('%Y-%m-%d')}")
                    st.write(f"**Patient:** {patient['name']} ({patient['nationality']})")
                    st.write(f"**Document:** {patient['doc_type']} {patient['doc_number']}")
                    st.write(f"**Diagnosis:** {treatment['diagnosis']}")
                    st.write(f"**Treatment:** {treatment['treatment']}")
                    if treatment['medication'] != "None":
                        st.write(f"**Medication:** {treatment['medication']}")
                    st.write(f"**Total Cost:** R{treatment['cost']:,.2f}")
                    invoice_text = f"""
                    BATHO PELE HEALTHCARE INITIATIVE
                    ---------------------------------
                    Invoice Date: {datetime.now(SA_TIMEZONE).strftime('%Y-%m-%d')}
                    Patient: {patient['name']}
                    ID: {patient['doc_number']}
                    ---------------------------------
                    Diagnosis: {treatment['diagnosis']}
                    Treatment: {treatment['treatment']}
                    Medication: {treatment['medication']}
                    ---------------------------------
                    TOTAL COST: R{treatment['cost']:,.2f}
                    """
                    st.download_button(
                        label="Download Invoice",
                        data=invoice_text,
                        file_name=f"invoice_{patient['name']}_{datetime.now(SA_TIMEZONE).strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
            if patient.get('legal_status') == 'Pending':
                if action_cols[1].button("⚠️ Refer to Home Affairs"):
                    st.success(f"Patient {patient['name']} referred to Home Affairs")
            if action_cols[2].button("👤 View Full Record"):
                with st.expander("Patient Record Summary", expanded=True):
                    st.write(f"**Name:** {patient['name']}")
                    st.write(f"**DOB:** {patient['dob']}")
                    st.write(f"**Nationality:** {patient['nationality']}")
                    st.write(f"**Status:** {patient.get('legal_status', 'Valid')}")
                    st.write(f"**Conditions:** {patient['conditions']}")
                    st.write("---")
                    st.write(f"**Last Treatment:** {treatment['diagnosis']}")
                    st.write(f"**Medication:** {treatment['medication']}")
                    st.write(f"**Cost:** R{treatment['cost']:,.2f}")
                    st.write(f"**Last Updated:** {treatment['timestamp']}")

elif current_page == "patient_search":
    with st.container():
        st.markdown('<div class="header"><h1>👥 Patient Search</h1></div>', unsafe_allow_html=True)
        search_cols = st.columns(3)
        name_search = search_cols[0].text_input("Name")
        id_search = search_cols[1].text_input("ID/Passport Number")
        nationality_filter = search_cols[2].selectbox("Nationality", ["All"] + list(patients_df['nationality'].dropna().unique()))
        filtered_patients = patients_df.copy()
        if name_search:
            filtered_patients = filtered_patients[
                filtered_patients['name'].notna() & 
                filtered_patients['name'].str.contains(name_search, case=False, na=False)
            ]
        if id_search:
            filtered_patients = filtered_patients[
                filtered_patients['doc_number'].notna() & 
                filtered_patients['doc_number'].str.contains(id_search, case=False, na=False)
            ]
        if nationality_filter != "All":
            filtered_patients = filtered_patients[filtered_patients['nationality'] == nationality_filter]
        if not filtered_patients.empty:
            st.subheader(f"Found {len(filtered_patients)} patients")
            show_cols = ['name', 'nationality', 'doc_type', 'doc_number', 'legal_status', 'timestamp']
            st.dataframe(
                filtered_patients[show_cols].rename(columns={
                    'name': 'Name',
                    'nationality': 'Nationality',
                    'doc_type': 'Document Type',
                    'doc_number': 'Document Number',
                    'legal_status': 'Status',
                    'timestamp': 'Last Updated'
                }),
                use_container_width=True,
                hide_index=True
            )
            selected_patient = st.selectbox("Select patient to view history", filtered_patients['name'].unique())
            patient_visits = visits_df[visits_df['patient_name'] == selected_patient]
            if not patient_visits.empty:
                st.subheader(f"Visit History for {selected_patient}")
                st.dataframe(
                    patient_visits[['visit_date', 'diagnosis', 'treatment', 'cost']].rename(columns={
                        'visit_date': 'Date',
                        'diagnosis': 'Diagnosis',
                        'treatment': 'Treatment',
                        'cost': 'Cost (R)'
                    }),
                    use_container_width=True
                )
        else:
            st.info("No patients found matching your criteria")

elif current_page == "resource_monitoring":
    with st.container():
        st.markdown('<div class="header"><h1>🏥 Resource Monitoring</h1></div>', unsafe_allow_html=True)
        st.subheader("Daily Hospital Resource Metrics")
        if resources_df.empty:
            st.warning("No resource data available.")
        else:
            hospitals = resources_df['hospital'].dropna().unique()
            selected_hospital = st.selectbox("Select Hospital", hospitals)
            hospital_resources = resources_df[resources_df['hospital'] == selected_hospital]
            resource_types = ["Beds", "Doctors", "Nurses", "Medications"]
            selected_resource = st.selectbox("Select resource to predict", resource_types)
            forecast = predict_resources(selected_resource.lower())
            if forecast is not None:
                st.write(f"### Next 7 Days Forecast for {selected_resource}")
                st.dataframe(forecast, use_container_width=True)
            else:
                st.info("Not enough historical data for prediction.")
            for _, ward_data in hospital_resources.iterrows():
                ward_name = ward_data.get('ward', 'Unknown')
                st.markdown(f"### 🏥 Ward: {ward_name}")
                cols = st.columns([1, 2, 2, 2])
                total_beds = int(ward_data.get('total_beds', 0))
                available_beds = int(ward_data.get('available_beds', 0))
                bed_percentage = (available_beds / total_beds * 100) if total_beds > 0 else 0
                cols[0].metric("Available Beds", f"{available_beds}/{total_beds}", f"{bed_percentage:.1f}% available")
                doctors = [d.strip() for d in str(ward_data.get('doctors', '')).split(',') if d.strip()]
                nurses = [n.strip() for n in str(ward_data.get('nurses', '')).split(',') if n.strip()]
                cols[1].markdown("**Doctors on Duty:**")
                for doctor in doctors:
                    cols[1].markdown(f"- {doctor}")
                cols[1].markdown("**Nurses on Duty:**")
                for nurse in nurses:
                    cols[1].markdown(f"- {nurse}")
                medications = [m.strip() for m in str(ward_data.get('medications', '')).split(',') if m.strip()]
                stocks = [s.strip() for s in str(ward_data.get('medication_stock', '')).split(',') if s.strip()]
                med_stock_map = {}
                for med, stock in zip(medications, stocks):
                    med_stock_map[med] = int(stock) if stock.isdigit() else stock
                cols[2].markdown("**Medication Stock:**")
                for med, stock in med_stock_map.items():
                    cols[2].markdown(f"- {med}: {stock}")
                today_str = datetime.now(SA_TIMEZONE).strftime('%Y-%m-%d')
                today_patients = visits_df[
                    (visits_df['hospital'] == selected_hospital) &
                    (visits_df['ward'] == ward_name) &
                    (visits_df['visit_date'] == today_str)
                ]
                cols[3].markdown("**Patients Admitted Today:**")
                if not today_patients.empty:
                    for pname in today_patients['patient_name']:
                        cols[3].markdown(f"- {pname}")
                else:
                    cols[3].markdown("_No new patients today_")
            st.subheader("Hospital Daily Summary")
            total_hospital_beds = hospital_resources['total_beds'].sum()
            available_hospital_beds = hospital_resources['available_beds'].sum()
            st.metric("Total Beds Available", f"{available_hospital_beds}/{total_hospital_beds}")
            doctors_names = set()
            nurses_names = set()
            medication_stock_total = {}
            for _, ward in hospital_resources.iterrows():
                doctors_names.update([d.strip() for d in str(ward.get('doctors', '')).split(',') if d.strip()])
                nurses_names.update([n.strip() for n in str(ward.get('nurses', '')).split(',') if n.strip()])
                meds = [m.strip() for m in str(ward.get('medications', '')).split(',') if m.strip()]
                stocks = [s.strip() for s in str(ward.get('medication_stock', '')).split(',') if s.strip()]
                for med, stock in zip(meds, stocks):
                    medication_stock_total[med] = medication_stock_total.get(med, 0) + (int(stock) if stock.isdigit() else 0)
            st.write("**Doctors on Duty Today:**")
            for d in sorted(doctors_names):
                st.write(f"- {d}")
            st.write("**Nurses on Duty Today:**")
            for n in sorted(nurses_names):
                st.write(f"- {n}")
            st.write("**Total Medication Stock Today:**")
            for med, stock in medication_stock_total.items():
                st.write(f"- {med}: {stock}")

# ====== FOOTER ======
st.markdown("---")
footer = """
<div style="text-align: center; padding: 20px; background-color: #f0f8ff; border-radius: 5px;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <p style="font-size: 14px; color: #003366;">© 2025 Batho Pele Initiative | National Department of Health</p>
        </div>
        <div>
            <p style="font-size: 12px; color: #666;">System Status: <span style="color: green;">● Operational</span></p>
            <p style="font-size: 12px; color: #666;">Last Updated: {}</p>
        </div>
    </div>
    <div style="margin-top: 10px;">
        <p style="font-size: 12px; color: #666;">For support, contact: <a href="mailto:support@bathopele.gov.za">support@bathopele.gov.za</a></p>
    </div>
</div>
""".format(datetime.now(SA_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S'))
st.markdown(footer, unsafe_allow_html=True)