import streamlit as st
import hashlib

def authenticate_user():
    if not st.session_state.get('authenticated'):
        with st.container():
            st.title("BathoPele_AI Staff Login")
            
            cols = st.columns([1, 2, 1])
            with cols[1]:
                # ✅ Add the logo at the top center of the form
                st.image("assets/Batho_pele.png", use_container_width=True)

                with st.form("login"):
                    user = st.text_input("Username")
                    pwd = st.text_input("Password", type="password")
                    
                    if st.form_submit_button("Login"):
                        if validate_credentials(user, pwd):
                            st.session_state.authenticated = True
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                return False
    return True

def validate_credentials(username, password):
    # Replace with proper authentication in production
    return username == "Mpho_Hlalele" and hashlib.sha256(password.encode()).hexdigest() == "907fbbb4869dc75cb3d3493f580adb2bedbf5da51f5d60465722941a9042fa9c"