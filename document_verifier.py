import pandas as pd
import os
from datetime import datetime

def initialize_verification_db(db_path="data/mock_home_affairs.csv"):
    """Create comprehensive verification database with all required sample data"""
    sample_data = {
        'id_number': [
            '9001011234087',  # Thabo Mbeki
            '5502025052086',  # Nkosazana Dlamini-Zuma
            '5711175053085',  # Cyril Ramaphosa
            '8103035054084',  # Julius Malema (added)
            '5904045055083',  # Lindiwe Sisulu
            '', '', '', '', ''
        ],
        'passport_number': ['']*5 + [
            'ZW2023AB001',    # Tendai Biti
            'MW2023CD002',    # Lazarus Chakwera
            'MZ2023EF003',    # Filipe Nyusi
            'REF12345678',    # Ahmed Abdi
            'REF12345679'     # Fatima Hussein
        ],
        'nationality': [
            'South African', 'South African', 'South African',
            'South African', 'South African',  # Julius Malema added here
            'Zimbabwean', 'Malawian', 'Mozambican',
            'Asylum Seeker', 'Asylum Seeker'
        ],
        'full_name': [
            'Thabo Mbeki', 'Nkosazana Dlamini-Zuma', 'Cyril Ramaphosa',
            'Julius Malema', 'Lindiwe Sisulu',  # Added Julius Malema
            'Tendai Biti', 'Lazarus Chakwera', 'Filipe Nyusi',
            'Ahmed Abdi', 'Fatima Hussein'
        ],
        'legal_status': ['Valid'] * 10
    }
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    pd.DataFrame(sample_data).to_csv(db_path, index=False)

def verify_document(doc_type, doc_number, nationality, home_affairs_db="data/mock_home_affairs.csv"):
    """Enhanced document verification with proper South African ID handling"""
    try:
        # Create database if it doesn't exist
        if not os.path.exists(home_affairs_db):
            initialize_verification_db(home_affairs_db)
            return "⚠️ Needs Manual Review (New database initialized)"
        
        # Load verification database
        try:
            df = pd.read_csv(home_affairs_db)
            if df.empty:
                return "⚠️ Needs Manual Review (Empty database)"
        except Exception as e:
            return f"Verification error: Failed to load database - {str(e)}"

        # RSA ID validation - special handling for South Africans
        if doc_type == "RSA ID":
            if len(doc_number) != 13 or not doc_number.isdigit():
                return "Invalid (Invalid format)"
            
            # Basic date validation
            try:
                year = int(doc_number[0:2])
                month = int(doc_number[2:4])
                day = int(doc_number[4:6])
                if month < 1 or month > 12 or day < 1 or day > 31:
                    return "Invalid (Invalid date)"
            except:
                return "Invalid (Date parse error)"
            
            # For South Africans, valid format = valid document
            if nationality == "South African":
                return "Valid"
            
            # For non-South Africans with RSA ID, check records
            match = df[(df['id_number'] == doc_number)]
            return "Valid" if not match.empty else "Invalid (Not found in records)"

        # Passport validation
        elif doc_type == "Passport":
            if len(doc_number) < 3 or not doc_number[:2].isalpha() or not doc_number[2:].isdigit():
                return "Invalid (Invalid format)"
            
            # Check country code matches nationality
            country_code = doc_number[:2].upper()
            expected_codes = {
                "South African": "ZA",
                "Zimbabwean": "ZW",
                "Malawian": "MW",
                "Mozambican": "MZ"
            }
            
            if nationality in expected_codes and country_code != expected_codes[nationality]:
                return f"Invalid (Country code {country_code} doesn't match {nationality})"
            
            match = df[(df['passport_number'] == doc_number) &
                     (df['nationality'] == nationality)]
            return "Valid" if not match.empty else "Invalid (Not found in records)"

        # Asylum permit validation
        elif doc_type == "Asylum Permit":
            if not doc_number.startswith("REF"):
                return "Invalid (Must start with REF)"
            if len(doc_number) != 11 or not doc_number[3:].isdigit():
                return "Invalid (Invalid format)"
            return "Valid"  # All REF documents considered valid
        
        return "Unknown document type"
    
    except Exception as e:
        return f"Verification error: {str(e)}"