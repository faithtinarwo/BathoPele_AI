import pandas as pd
import os
import streamlit as st
from datetime import datetime, timedelta

def load_all_data():
    """Load all application data with real-time metrics support"""
    base_path = "data"
    os.makedirs(base_path, exist_ok=True)
    
    # ====== COLUMN DEFINITIONS WITH ENHANCED DATA TYPES ======
    patients_columns = {
        'id': 'string',
        'timestamp': 'datetime64[ns]',
        'full_name': 'string',
        'nationality': 'category',
        'id_number': 'string',
        'passport_number': 'string',
        'document_type': 'category',
        'legal_status': 'category',
        'status': 'string',
        'last_visit': 'datetime64[ns]'
    }
    
    visits_columns = {
        'visit_id': 'string',
        'patient_id': 'string',
        'patient_name': 'string',
        'hospital': 'category',
        'visit_date': 'datetime64[ns]',
        'visit_type': 'category',
        'doctor': 'string',
        'diagnosis': 'string',
        'ward': 'category',
        'medication': 'string',
        'cost': 'float64',
        'duration_minutes': 'int64'
    }
    
    resources_columns = {
        'resource_id': 'string',
        'resource_type': 'category',
        'name': 'string',
        'quantity': 'float64',
        'unit': 'category',
        'status': 'category',
        'location': 'string',
        'last_updated': 'datetime64[ns]'
    }
    
    costs_columns = {
        'date': 'datetime64[ns]',
        'total_cost': 'float64',
        'medication_cost': 'float64',
        'staff_cost': 'float64',
        'facility_cost': 'float64',
        'patient_count': 'int64'
    }

    # ====== COMPREHENSIVE SAMPLE DATA ======
    sample_patients = [
        {
            'id': 'PAT-001',
            'timestamp': datetime.now(),
            'full_name': 'Julius Malema',
            'nationality': 'South African',
            'id_number': '8103035054084',
            'document_type': 'RSA ID',
            'legal_status': 'Valid',
            'status': '✅ Eligible for Free Healthcare',
            'last_visit': None
        },
        {
            'id': 'PAT-002',
            'timestamp': datetime.now(),
            'full_name': 'Lindiwe Sisulu',
            'nationality': 'South African',
            'id_number': '5904045055083',
            'document_type': 'RSA ID',
            'legal_status': 'Valid',
            'status': '✅ Eligible for Free Healthcare',
            'last_visit': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        }
    ]
    
    sample_visits = [
        {
            'visit_id': 'VIS-001',
            'patient_id': 'PAT-002',
            'patient_name': 'Lindiwe Sisulu',
            'hospital': 'Central Hospital',
            'visit_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'visit_type': 'Consultation',
            'doctor': 'Dr. Khumalo',
            'diagnosis': 'Hypertension',
            'ward': 'Ward A',
            'medication': 'Amlodipine 5mg',
            'cost': 1200.50,
            'duration_minutes': 30
        }
    ]
    
    sample_resources = [
        {
            'resource_id': 'BED-001',
            'resource_type': 'Bed',
            'name': 'Ward A Bed 01',
            'quantity': 1,
            'unit': 'bed',
            'status': 'Available',
            'location': 'Ward A',
            'last_updated': datetime.now()
        },
        {
            'resource_id': 'MED-001',
            'resource_type': 'Medication',
            'name': 'Amlodipine 5mg',
            'quantity': 150,
            'unit': 'tablets',
            'status': 'In Stock',
            'location': 'Pharmacy A',
            'last_updated': datetime.now()
        },
        {
            'resource_id': 'STAFF-001',
            'resource_type': 'Staff',
            'name': 'Dr. Khumalo',
            'quantity': 1,
            'unit': 'doctor',
            'status': 'On Duty',
            'location': 'Ward A',
            'last_updated': datetime.now()
        }
    ]
    
    sample_costs = {
        'date': [datetime.now().strftime('%Y-%m-%d')],
        'total_cost': [20126.75],
        'medication_cost': [8245.00],
        'staff_cost': [9876.50],
        'facility_cost': [2005.25],
        'patient_count': [47]
    }

    # ====== ENHANCED DATA LOADER ======
    def load_or_initialize(filepath, columns, sample_data=None):
        try:
            if os.path.exists(filepath):
                df = pd.read_csv(filepath, parse_dates=True)
                
                # Convert columns to proper types
                for col, dtype in columns.items():
                    if col in df.columns:
                        try:
                            df[col] = df[col].astype(dtype)
                        except:
                            df[col] = None
                    else:
                        df[col] = pd.Series(dtype=dtype)
                
                return df
            else:
                if sample_data:
                    df = pd.DataFrame(sample_data)
                    # Ensure all columns exist with correct types
                    for col, dtype in columns.items():
                        if col not in df.columns:
                            df[col] = pd.Series(dtype=dtype)
                else:
                    df = pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in columns.items()})
                
                # Save with proper types
                df.to_csv(filepath, index=False)
                return df
        except Exception as e:
            st.error(f"Error loading {filepath}: {str(e)}")
            return pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in columns.items()})

    # Load data with proper typing
    patients = load_or_initialize(
        f"{base_path}/patients.csv", 
        patients_columns,
        sample_patients
    )
    
    visits = load_or_initialize(
        f"{base_path}/visits.csv", 
        visits_columns,
        sample_visits
    )
    
    resources = load_or_initialize(
        f"{base_path}/resources.csv", 
        resources_columns,
        sample_resources
    )
    
    costs = load_or_initialize(
        f"{base_path}/costs.csv", 
        costs_columns,
        sample_costs
    )
    
    # Process intake logs
    intake_logs_path = f"{base_path}/intake_logs.csv"
    if os.path.exists(intake_logs_path):
        try:
            intake_logs = pd.read_csv(intake_logs_path, parse_dates=['timestamp'])
            patients = pd.concat([patients, intake_logs], ignore_index=True)
            
            # Update last visit dates
            if not visits.empty:
                visits['visit_date'] = pd.to_datetime(visits['visit_date'])
                latest_visits = visits.groupby('patient_name')['visit_date'].max()
                
                for idx, patient in patients.iterrows():
                    if patient['full_name'] in latest_visits:
                        patients.at[idx, 'last_visit'] = latest_visits[patient['full_name']]
        except Exception as e:
            st.error(f"Error processing intake logs: {str(e)}")
    
    return patients, visits, resources, costs

def get_realtime_metrics(patients_df, visits_df, resources_df):
    """Calculate real-time metrics for dashboard"""
    metrics = {
        'sa_patients': 0,
        'legal_immigrants': 0,
        'needs_review': 0,
        'beds_available': 0,
        'med_stock_days': 9,  # Default value
        'today_cost': 0
    }
    
    try:
        # Patient metrics
        if not patients_df.empty:
            metrics['sa_patients'] = len(patients_df[
                (patients_df['nationality'] == 'South African') & 
                (patients_df['legal_status'] == 'Valid')
            ])
            
            metrics['legal_immigrants'] = len(patients_df[
                patients_df['nationality'].isin(['Zimbabwean', 'Malawian', 'Mozambican']) & 
                (patients_df['legal_status'] == 'Valid')
            ])
            
            metrics['needs_review'] = len(patients_df[
                patients_df['legal_status'] == 'Needs Review'
            ])
        
        # Resource metrics
        if not resources_df.empty:
            # Beds available
            metrics['beds_available'] = len(resources_df[
                (resources_df['resource_type'] == 'Bed') & 
                (resources_df['status'] == 'Available')
            ])
            
            # Medication stock (simplified calculation)
            meds = resources_df[resources_df['resource_type'] == 'Medication']
            if not meds.empty:
                metrics['med_stock_days'] = int(meds['quantity'].mean() / 10)  # Example calculation
        
        # Cost metrics (today's cost)
        if not visits_df.empty:
            today = datetime.now().date()
            visits_df['visit_date'] = pd.to_datetime(visits_df['visit_date']).dt.date
            today_visits = visits_df[visits_df['visit_date'] == today]
            metrics['today_cost'] = today_visits['cost'].sum()
            
    except Exception as e:
        st.error(f"Error calculating metrics: {str(e)}")
    
    return metrics