import streamlit as st
import pytz
import os
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import logging
from document_verifier import verify_document
from data_loader import load_all_data, get_realtime_metrics
from reporting import display_dashboard

# ====== CONFIGURATION ======
SA_TIMEZONE = pytz.timezone('Africa/Johannesburg')
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
logging.basicConfig(filename='app_errors.log', level=logging.ERROR)

# ====== DATA INITIALIZATION ======
def initialize_data_files():
    """Initialize all required data files with enhanced sample data"""
    try:
        # Patients database
        patients_db = f"{DATA_DIR}/patients.csv"
        if not os.path.exists(patients_db):
            patients_columns = [
                'name', 'dob', 'nationality', 'doc_type', 'doc_number', 
                'medical_aid', 'conditions', 'timestamp', 'verified_by',
                'result', 'legal_status', 'details'
            ]
            sample_patients = [
                ['John Nkosi', '1985-05-15', 'South African', 'RSA ID', '8505151234088', 
                 'GOLD123', 'Hypertension', '2023-10-01 09:30:00', 'admin', 
                 'Valid', 'Valid', 'Automatically verified'],
                ['Maria Molotsi', '1990-11-22', 'Mozambican', 'Passport', 'P12345678', 
                 '', '', '2023-10-02 10:15:00', 'admin', 
                 'Valid', 'Valid', 'Automatically verified'],
                ['James Khumalo', '1978-03-30', 'South African', 'RSA ID', '7803305432087', 
                 '', 'Diabetes', '2023-10-03 11:00:00', 'admin', 
                 'Valid', 'Valid', 'Automatically verified']
            ]
            pd.DataFrame(sample_patients, columns=patients_columns).to_csv(patients_db, index=False)

        # Visits database
        visits_db = f"{DATA_DIR}/visits.csv"
        if not os.path.exists(visits_db):
            visits_columns = [
                'patient_name', 'visit_date', 'hospital', 'visit_type', 'doctor',
                'diagnosis', 'ward', 'bed_number', 'medication', 'medication_qty',
                'cost', 'duration_minutes', 'treatment', 'notes'
            ]
            sample_visits = [
                ['John Doe', '2023-10-01', 'Johannesburg General', 'Consultation', 'Dr Smith',
                 'Hypertension', 'Outpatient', 'N/A', 'Lisinopril 10mg', '1',
                 350, 30, 'Daily medication', 'Follow up in 3 months'],
                ['Maria Garcia', '2023-10-02', 'Johannesburg General', 'Emergency', 'Dr Jones',
                 'Fractured wrist', 'Emergency', 'E12', 'Ibuprofen 400mg', '2',
                 1200, 45, 'Cast application', 'Return in 6 weeks']
            ]
            pd.DataFrame(sample_visits, columns=visits_columns).to_csv(visits_db, index=False)

        # Enhanced resources database with proper sample data
        resources_db = f"{DATA_DIR}/resources.csv"
        if not os.path.exists(resources_db):
            resources_columns = [
                'hospital', 'ward', 'total_beds', 'available_beds', 
                'medications', 'medication_stock', 'doctors', 'nurses',
                'last_updated'
            ]
            sample_resources = [
                ['Johannesburg General', 'Emergency', 50, 12, 'Paracetamol,Amoxicillin', '100,50', 'Dr TS Moreki,Dr M Gule', 'Nurse Amanda,Nurse Bongiwe', datetime.now().strftime('%Y-%m-%d')],
                ['Johannesburg General', 'Pediatrics', 40, 8, 'Ibuprofen,Calpol', '75,60', 'Dr N Dwarka,Dr MF Kleinhans', 'Nurse Cathy,Nurse Dion', datetime.now().strftime('%Y-%m-%d')],
                ['Cape Town Central', 'Surgery', 60, 15, 'Morphine,Antibiotics', '30,40', 'Dr BB Mbambela,Dr D Skete', 'Nurse Ellen,Nurse Fikile', datetime.now().strftime('%Y-%m-%d')],
                ['Durban Coastal', 'Maternity', 35, 10, 'Pethidine,Oxytocin', '25,30', 'Dr GO Matlaga Khan,Dr P Naidoo', 'Nurse Gugu,Nurse Happy', datetime.now().strftime('%Y-%m-%d')]
            ]
            pd.DataFrame(sample_resources, columns=resources_columns).to_csv(resources_db, index=False)

        # Costs database
        costs_db = f"{DATA_DIR}/costs.csv"
        if not os.path.exists(costs_db):
            costs_columns = ['patient_name', 'date', 'description', 'amount', 'category']
            sample_costs = [
                ['John Nkosi', '2023-10-01', 'Hypertension consultation', 350, 'Consultation'],
                ['Maria Molotsi', '2023-10-02', 'Wrist fracture treatment', 1200, 'Emergency']
            ]
            pd.DataFrame(sample_costs, columns=costs_columns).to_csv(costs_db, index=False)
            
    except Exception as e:
        logging.error(f"Error initializing data files: {str(e)}")
        st.error("Failed to initialize data files")

initialize_data_files()

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
        patients_df, visits_df, resources_df, costs_df = load_all_data()
        
        # Ensure required columns exist with proper defaults
        patients_df['name'] = patients_df['name'].fillna('Unknown')
        patients_df['doc_number'] = patients_df['doc_number'].fillna('')
        
        # Fix status errors - ensure nationality matches document type
        for idx, row in patients_df.iterrows():
            if row['doc_type'] == 'Passport' and row['nationality'] == 'South African':
                patients_df.at[idx, 'result'] = 'Needs Verification'
                patients_df.at[idx, 'legal_status'] = 'Pending'
            elif row['doc_type'] == 'RSA ID' and row['nationality'] != 'South African':
                patients_df.at[idx, 'result'] = 'Needs Verification'
                patients_df.at[idx, 'legal_status'] = 'Pending'
        
        # Ensure resources data has all required columns
        required_resource_cols = ['hospital', 'ward', 'total_beds', 'available_beds', 
                                'medications', 'medication_stock', 'doctors', 'nurses']
        for col in required_resource_cols:
            if col not in resources_df.columns:
                resources_df[col] = '' if col in ['medications', 'doctors', 'nurses'] else 0
        
        # Process dates
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

# Get real-time metrics for sidebar
metrics = get_realtime_metrics(patients_df, visits_df, resources_df)

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
    
    # Navigation Menu
    nav_option = st.radio(
        "Navigation Menu",
        ["🏠 Dashboard", "📋 Patient Intake", "👥 Patient Search", "🏥 Resource Monitoring"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.divider()
    st.subheader("Patient Metrics")
    
    # Calculate patient metrics
    sa_patients = len(patients_df[patients_df['nationality'] == 'South African'])
    foreign_patients = len(patients_df[patients_df['nationality'] != 'South African'])
    needs_referral = len(patients_df[patients_df['legal_status'] == 'Pending'])
    
    # Clickable metrics - store which one was clicked in session state
    if st.button(f"SA Patients: {sa_patients}", key="sa_patients_btn", 
                use_container_width=True, help="Click to view South African patients"):
        st.session_state.patient_metric_clicked = "sa_patients"
    
    if st.button(f"🌍 Foreign Nationals: {foreign_patients}", key="foreign_patients_btn", 
                use_container_width=True, help="Click to view foreign national patients"):
        st.session_state.patient_metric_clicked = "foreign_patients"
    
    if st.button(f"⚠️ Needs Referral: {needs_referral}", key="referral_patients_btn", 
                use_container_width=True, help="Click to view patients needing referral"):
        st.session_state.patient_metric_clicked = "needs_referral"
    
    st.divider()
    st.subheader("Resource Monitoring")
    
    # Calculate resource metrics
    total_beds = resources_df['available_beds'].sum()
    med_stock = sum(int(x) for med in resources_df['medication_stock'] for x in str(med).split(',') if x.isdigit())
    doctors = sum(len(str(x).split(',')) for x in resources_df['doctors'])
    nurses = sum(len(str(x).split(',')) for x in resources_df['nurses'])
    
    # Resource summary
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
        
        # Display patient lists if a metric was clicked
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
        
        try:
            display_dashboard(patients_df, visits_df, resources_df, costs_df)
        except Exception as e:
            st.error(f"Error displaying dashboard: {str(e)}")
            st.write("## Patients Overview")
            st.dataframe(patients_df.head(3), use_container_width=True)
            st.write("## Resources Overview")
            st.dataframe(resources_df.head(3), use_container_width=True)

elif current_page == "patient_intake":
    with st.container():
        st.markdown('<div class="header"><h1>📋 Patient Intake</h1></div>', unsafe_allow_html=True)
        
        # ========== COMPREHENSIVE TREATMENT PLANS ==========
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

        # ========== PATIENT INTAKE FORM ==========
        st.title("🏥 Patient Intake System")

        # First form - Patient Information
        with st.expander("📋 Patient Information", expanded=True):
            with st.form("patient_intake_form"):
                cols = st.columns(2)
                
                # Column 1
                name = cols[0].text_input("Full Name*", placeholder="First Last")
                nationality = cols[0].selectbox("Nationality*", 
                                              ["South African", "Zimbabwean", "Malawian", "Mozambican", "Other"])
                doc_number = cols[0].text_input("Document Number*", placeholder="ID/Passport Number")
                
                # Column 2
                dob_col = cols[1]
                dob_col.markdown("Date of Birth*")
                dob_known = dob_col.checkbox("Known DOB", value=True, key="dob_known")
                
                if dob_known:
                    dob = dob_col.date_input("", 
                                           min_value=datetime(1900,1,1), 
                                           max_value=datetime.now(),
                                           label_visibility="collapsed")
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
                        # Verification logic
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

        # Second form - Treatment Information
        if st.session_state.get('show_treatment_form', False) and 'last_patient' in st.session_state:
            patient = st.session_state.last_patient
            with st.expander("🩺 Treatment Information", expanded=True):
                with st.form("treatment_form"):
                    st.write("### Diagnosis and Treatment")
                    
                    diagnosis = st.selectbox("Diagnosis*", list(treatment_plans.keys()) + ["Other"])
                    
                    # Auto-populate treatment plan if standard diagnosis
                    if diagnosis in treatment_plans:
                        treatment_plan = st.text_area(
                            "Treatment Plan*", 
                            value=treatment_plans[diagnosis]["plan"],
                            key="treatment_plan"
                        )
                        
                        # Display recommended medications
                        st.write("### Recommended Medications")
                        for med in treatment_plans[diagnosis]["medications"]:
                            st.markdown(f"• **{med['name']}**: {med['dosage']} {med['frequency']}")
                        
                        # Auto-calculate cost based on patient status
                        if patient['nationality'] == 'South African':
                            cost = treatment_plans[diagnosis]["costs"]["SA Residents"]
                        elif patient['legal_status'] == 'Valid':
                            cost = treatment_plans[diagnosis]["costs"]["Legal Immigrants"]
                        else:
                            cost = treatment_plans[diagnosis]["costs"]["Illegal Immigrants"]
                    else:
                        treatment_plan = st.text_area("Treatment Plan*")
                        cost = st.number_input("Treatment Cost (R)*", min_value=0, value=1500)
                    
                    # Medication prescription
                    st.write("### Medication Prescribed")
                    med_cols = st.columns(3)
                    medication = med_cols[0].text_input("Medication name", placeholder="Enter medication")
                    dosage = med_cols[1].text_input("Dosage", placeholder="e.g., 500mg")
                    frequency = med_cols[2].text_input("Frequency", placeholder="e.g., 3x daily")
                    
                    st.write(f"### Estimated Cost: R{cost:,.2f}")
                    notes = st.text_area("Additional Notes", placeholder="Any special instructions")
                    
                    treatment_submitted = st.form_submit_button("Submit Treatment Details")
                    
                    if treatment_submitted:
                        if not diagnosis or not treatment_plan:
                            st.error("Please fill in required diagnosis and treatment fields")
                        else:
                            try:
                                # Create visit record
                                visit_data = {
                                    "patient_name": patient['name'],
                                    "diagnosis": diagnosis,
                                    "treatment": treatment_plan,
                                    "medication": f"{medication} {dosage} {frequency}" if medication else "None",
                                    "cost": cost,
                                    "notes": notes,
                                    "timestamp": datetime.now(SA_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
                                }
                                
                                # Here you would save to your database (commented for example)
                                # save_to_database(visit_data)
                                
                                st.success("Treatment details saved successfully!")
                                st.session_state.treatment_details = visit_data
                                st.session_state.show_actions = True
                                
                            except Exception as e:
                                logging.error(f"Error saving treatment: {str(e)}")
                                st.error(f"Error saving treatment: {str(e)}")

        # Action buttons section
        if st.session_state.get('show_actions', False):
            st.markdown("---")
            st.subheader("Patient Actions")
            
            action_cols = st.columns(3)
            patient = st.session_state.last_patient
            treatment = st.session_state.treatment_details
            
            # Generate Invoice button
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
                    
                    # Download button
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
            
            # Referral button (conditionally shown)
            if patient.get('legal_status') == 'Pending':
                if action_cols[1].button("⚠️ Refer to Home Affairs"):
                    # Here you would update your database
                    st.success(f"Patient {patient['name']} referred to Home Affairs")
            
            # View Patient Record button
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
        
        # Search fields
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
            
            # Show visit history for selected patient
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
        
        st.subheader("🏨 Hospital Resources by Ward")
        try:
            if not resources_df.empty:
                hospitals = resources_df['hospital'].unique()
                selected_hospital = st.selectbox("Select Hospital", hospitals)
                
                hospital_resources = resources_df[resources_df['hospital'] == selected_hospital]
                
                for _, ward_data in hospital_resources.iterrows():
                    with st.expander(f"🏥 {ward_data['ward']} Ward", expanded=True):
                        cols = st.columns([1, 2, 2, 1])
                        
                        # Beds
                        total_beds = int(ward_data.get('total_beds', 0))
                        available_beds = int(ward_data.get('available_beds', 0))
                        bed_percentage = (available_beds / total_beds * 100) if total_beds > 0 else 0
                        cols[0].metric("Beds", f"{available_beds}/{total_beds}", f"{bed_percentage:.1f}% available")
                        
                        # Detailed bed information
                        with cols[1]:
                            st.markdown("**Bed Availability**")
                            st.markdown(f"**Total Beds:** {total_beds}")
                            st.markdown(f"**Available Beds:** {available_beds}")
                        
                        # Staff information
                        with cols[2]:
                            st.markdown("**Staff on Duty**")
                            doctors = str(ward_data.get('doctors', '')).split(',')
                            nurses = str(ward_data.get('nurses', '')).split(',')
                            
                            st.markdown("**Doctors:**")
                            for doctor in doctors:
                                if doctor.strip():
                                    st.markdown(f"- {doctor.strip()}")
                            
                            st.markdown("**Nurses:**")
                            for nurse in nurses:
                                if nurse.strip():
                                    st.markdown(f"- {nurse.strip()}")
                        
                        # Medication information
                        with cols[3]:
                            st.markdown("**Medications**")
                            medications = str(ward_data.get('medications', '')).split(',')
                            stocks = str(ward_data.get('medication_stock', '')).split(',')
                            
                            for med, stock in zip(medications, stocks):
                                if med.strip():
                                    st.markdown(f"- {med.strip()}: {stock.strip()}")
                
                # Hospital summary
                st.subheader("🏥 Hospital Summary")
                summary_cols = st.columns(3)
                
                # Total beds
                total_hospital_beds = hospital_resources['total_beds'].sum()
                available_hospital_beds = hospital_resources['available_beds'].sum()
                summary_cols[0].metric("Total Beds", 
                                     f"{available_hospital_beds}/{total_hospital_beds}",
                                     f"{available_hospital_beds/total_hospital_beds*100:.1f}% available" if total_hospital_beds > 0 else "0%")
                
                # Staff count
                doctors_count = sum(len(str(x).split(',')) for x in hospital_resources['doctors'])
                nurses_count = sum(len(str(x).split(',')) for x in hospital_resources['nurses'])
                summary_cols[1].metric("Staff On Duty", f"{doctors_count} Doctors, {nurses_count} Nurses")
                
                # Medication stock
                total_meds = sum(int(x) for med in hospital_resources['medication_stock'] for x in str(med).split(',') if x.isdigit())
                summary_cols[2].metric("Total Medication Stock", total_meds)
                
                # Current patients
                st.subheader("Current Patients by Ward")
                current_visits = visits_df[visits_df['hospital'] == selected_hospital]
                if not current_visits.empty:
                    ward_patients = current_visits.groupby('ward')['patient_name'].count().reset_index()
                    ward_patients.columns = ['Ward', 'Patient Count']
                    st.dataframe(ward_patients, use_container_width=True)
                else:
                    st.info("No current patients in this hospital")
                
            else:
                st.warning("No resource data available")
                
        except Exception as e:
            logging.error(f"Error displaying resource data: {str(e)}")
            st.error(f"Error displaying resource data: {str(e)}")

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