# logic.py
def classify_patient(nationality, doc_type, legal_status):
    if nationality == "South African":
        return " Eligible for Free Public Healthcare"
    elif doc_type in ["Permit", "Asylum"] and legal_status == "Valid":
        return "Eligible for Subsidized or Emergency Care"
    elif doc_type == "Passport" or doc_type == "No Document":
        return "Payment Required or Refer to Admin"
    else:
        return "Needs Manual Review"