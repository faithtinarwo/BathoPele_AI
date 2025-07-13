import pandas as pd
import os
from datetime import datetime, timedelta
import random

def initialize_data_files():
    os.makedirs("data", exist_ok=True)
    
    # 1. Create visits.csv if missing
    if not os.path.exists("data/visits.csv"):
        visits = []
        for i in range(1, 101):
            visits.append({
                'id': i,
                'patient_id': random.randint(1, 100),
                'patient_name': f"Patient {i}",  # Added patient_name for merging
                'hospital': random.choice(["Joburg General", "Ekurhuleni District", "Tshwane Central"]),
                'visit_date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                'visit_type': random.choice(["Consultation", "Emergency", "Follow-up"]),
                'cost': round(random.uniform(150, 2500), 2)
            })
        pd.DataFrame(visits).to_csv("data/visits.csv", index=False)
    
    # 2. Create resources.csv if missing
    if not os.path.exists("data/resources.csv"):
        pd.DataFrame([{
            'beds_available': random.randint(5, 50),
            'medication_stock': random.randint(1, 30),
            'staff_available': random.randint(10, 45),
            'utilization': random.randint(60, 95)
        }]).to_csv("data/resources.csv", index=False)
    
    # 3. Create/Update costs.csv with all required columns
    costs_data = {
        'daily_cost': [round(random.uniform(10000, 30000), 2)],
        'avg_patient_cost': [round(random.uniform(500, 1500), 2)],
        'medication_cost': [round(random.uniform(5000, 10000), 2)],
        'staff_cost': [round(random.uniform(8000, 15000), 2)],
        'facility_cost': [round(random.uniform(3000, 6000), 2)]
    }
    pd.DataFrame(costs_data).to_csv("data/costs.csv", index=False)
    
    print("All data files initialized/updated successfully!")

if __name__ == "__main__":
    initialize_data_files()