import os
import pandas as pd

def load_all_data():
    """Load all data files with fallback to existing intake_logs"""
    data = {
        'patients': pd.read_csv("data/patients.csv"),
        'visits': pd.read_csv("data/visits.csv"),
        'resources': pd.read_csv("data/resources.csv"),
        'costs': pd.read_csv("data/costs.csv")
    }
    
    # Merge with existing intake logs if available
    if os.path.exists("data/intake_logs.csv"):
        intake_logs = pd.read_csv("data/intake_logs.csv")
        data['patients'] = pd.concat([data['patients'], intake_logs], ignore_index=True)
    
    return data