# auth_enhancer.py
import time
from datetime import datetime, timedelta
import streamlit as st

class AuthProtector:
    def __init__(self):
        self.failed_attempts = {}
        self.lockouts = {}
        self.IP_TRACKING = {}  # For IP-based protection
        self.MAX_ATTEMPTS = 5
        self.LOCKOUT_MINUTES = 15
        
    def secure_validate(self, username, password, client_ip=None):
        """Enhanced validation with brute-force protection"""
        # Check if IP/username is locked out
        if self._is_locked_out(username, client_ip):
            st.error("Too many failed attempts. Please try again later.")
            return False
            
        # Your existing validation (will be replaced with actual check)
        is_valid = username == "Mpho_Hlalele" and password == "674692Plum"  
        
        if is_valid:
            self._clear_attempts(username, client_ip)
            return True
        else:
            self._record_failed_attempt(username, client_ip)
            remaining = self.MAX_ATTEMPTS - self.failed_attempts.get(username, {}).get('count', 0)
            if remaining > 0:
                st.error(f"Invalid credentials. {remaining} attempts remaining.")
            return False
    
    def _is_locked_out(self, username, client_ip=None):
        """Check if username or IP is in lockout period"""
        now = datetime.now()
        # Check username lockout
        if username in self.lockouts and self.lockouts[username] > now:
            return True
        # Check IP lockout
        if client_ip and client_ip in self.lockouts and self.lockouts[client_ip] > now:
            return True
        return False
    
    def _record_failed_attempt(self, username, client_ip=None):
        """Track failed attempts"""
        # Track by username
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {'count': 0, 'last_attempt': datetime.now()}
        self.failed_attempts[username]['count'] += 1
        self.failed_attempts[username]['last_attempt'] = datetime.now()
        
        # Track by IP if available
        if client_ip:
            if client_ip not in self.IP_TRACKING:
                self.IP_TRACKING[client_ip] = {'count': 0, 'last_attempt': datetime.now()}
            self.IP_TRACKING[client_ip]['count'] += 1
            self.IP_TRACKING[client_ip]['last_attempt'] = datetime.now()
        
        # Check if we should lock out
        if self.failed_attempts[username]['count'] >= self.MAX_ATTEMPTS:
            self.lockouts[username] = datetime.now() + timedelta(minutes=self.LOCKOUT_MINUTES)
        if client_ip and self.IP_TRACKING[client_ip]['count'] >= self.MAX_ATTEMPTS:
            self.lockouts[client_ip] = datetime.now() + timedelta(minutes=self.LOCKOUT_MINUTES)
    
    def _clear_attempts(self, username, client_ip=None):
        """Reset tracking after successful login"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        if username in self.lockouts:
            del self.lockouts[username]
        if client_ip and client_ip in self.IP_TRACKING:
            del self.IP_TRACKING[client_ip]
        if client_ip and client_ip in self.lockouts:
            del self.lockouts[client_ip]

# Global instance
auth_protector = AuthProtector()

def secure_validate(username, password):
    """Wrapper for Streamlit compatibility"""
    # Get client IP (approximation since Streamlit doesn't expose this directly)
    client_ip = st.experimental_get_query_params().get('client_ip', [''])[0]
    return auth_protector.secure_validate(username, password, client_ip)