# treatment_plans.py
CONDITIONS = {
    "Hypertension": {
        "treatment_plan": "Lifestyle changes and medication based on severity",
        "medications": [
            {"name": "Amlodipine", "dosage": "5-10 mg", "frequency": "Once daily"},
            {"name": "Hydrochlorothiazide", "dosage": "12.5-25 mg", "frequency": "Once daily"}
        ],
        "costs": {
            "SA Residents": 0,
            "Legal Immigrants": 350,
            "Illegal Immigrants": 800
        }
    },
    "Type 2 Diabetes": {
        "treatment_plan": "Diet modification and glucose control",
        "medications": [
            {"name": "Metformin", "dosage": "500-1000 mg", "frequency": "Twice daily"},
            {"name": "Glibenclamide", "dosage": "5 mg", "frequency": "Once daily"}
        ],
        "costs": {
            "SA Residents": 0,
            "Legal Immigrants": 510,
            "Illegal Immigrants": 1150
        }
    },
    # Add all other conditions similarly
}

def get_condition_options():
    return list(CONDITIONS.keys())

def get_treatment_plan(condition, patient_status):
    plan = CONDITIONS.get(condition, {})
    cost = plan.get("costs", {}).get(patient_status, 0)
    return {
        "treatment": plan.get("treatment_plan", ""),
        "medications": plan.get("medications", []),
        "cost": cost
    }