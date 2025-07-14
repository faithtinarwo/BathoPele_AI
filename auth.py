# auth.py (updated)
import hashlib
import streamlit as st
from auth_enhancer import secure_validate  # <-- New import

def authenticate_user():
    if not st.session_state.get('authenticated'):
        with st.container():
            st.title("BathoPele_AI Staff Login")
            
            cols = st.columns([1, 2, 1])
            with cols[1]:
                st.image("assets/Batho_pele.png", use_container_width=True)

                with st.form("login"):
                    user = st.text_input("Username")
                    pwd = st.text_input("Password", type="password")
                    
                    if st.form_submit_button("Login"):
                        if secure_validate(user, pwd):  # <-- Changed to use enhanced validation
                            st.session_state.authenticated = True
                            st.rerun()
                        else:
                            # Error message handled by secure_validate
                            pass
                return False
    return True

# Keep original validate_credentials for reference (but it won't be used)
def validate_credentials(username, password):
    return username == "Mpho_Hlalele" and hashlib.sha256(password.encode()).hexdigest() == "907fbbb4869dc75cb3d3493f580adb2bedbf5da51f5d60465722941a9042fa9c"

