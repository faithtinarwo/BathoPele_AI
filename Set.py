import pandas as pd
from datetime import datetime, timedelta
import random
import os

os.makedirs("data", exist_ok=True)

# Generate patients.csv
patients = []
for i in range(1, 101):
    is_sa = random.random() > 0.3
    patients.append({
        'id': i,
        'full_name': f"Patient {i}",
        'nationality': "South African" if is_sa else random.choice(["Zimbabwean", "Mozambican"]),
        'id_number': f"{random.randint(900000,999999)}{random.randint(1000,9999)}" if is_sa else "",
        'passport_number': "" if is_sa else f"{random.choice(['ZW','MZ'])}{random.randint(100000,999999)}",
        'document_type': "RSA ID" if is_sa else "Passport",
        'legal_status': "Valid" if random.random() > 0.7 else "Invalid",
        'status': "✅ Eligible" if is_sa else random.choice(["🟡 Needs Review", "🔴 Payment Required"]),
        'last_visit': (datetime.now() - timedelta(days=random.randint(0,30))).strftime('%Y-%m-%d')
    })
pd.DataFrame(patients).to_csv("data/patients.csv", index=False)

# Generate visits.csv
# [...] (similar generation logic for other files)

print("Sample data files created in data/ directory")