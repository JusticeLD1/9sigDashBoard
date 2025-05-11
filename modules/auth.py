import streamlit as st
from modules.database import PortfolioDB
from typing import Tuple, Optional, Dict, Any

__all__ = ['PortfolioAuth']  # Explicitly declare what this module exports

class PortfolioAuth:
    """Authentication handler for Portfolio Tracker"""
    
    def __init__(self, db: PortfolioDB):
        """Initialize the authentication module"""
        self.db = db
        
        # Initialize session state variables if they don't exist
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
    
    def login_form(self) -> bool:
        """
        Display the login form and handle authentication
        Returns True if the user is logged in successfully
        """
        # If already authenticated, return True
        if st.session_state.authenticated:
            return True
        
        # Create a simple login form
        st.write("Please log in to access your portfolio dashboard.")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Log In")
            
            if submit:
                if self.db.verify_user(username, password):
                    # Authentication successful
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_data = self.db.get_user(username)
                    st.success("Login successful!")
                    st.rerun()  # Rerun the app to update the UI
                    return True
                else:
                    # Authentication failed
                    st.error("Invalid username or password")
                    return False
        
        # Add registration option
        st.write("Don't have an account? Register below.")
        
        with st.form("register_form"):
            st.write("### Create a new account")
            new_username = st.text_input("Username", key="new_username")
            new_password = st.text_input("Password", type="password", key="new_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            email = st.text_input("Email")
            full_name = st.text_input("Full Name")
            register = st.form_submit_button("Register")
            
            if register:
                # Validate form
                if not new_username or not new_password:
                    st.error("Username and password are required")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    # Create new user
                    if self.db.add_user(new_username, new_password, email, full_name):
                        st.success("Registration successful! You can now log in.")
                        # Automatically log in the new user
                        st.session_state.authenticated = True
                        st.session_state.username = new_username
                        st.session_state.user_data = self.db.get_user(new_username)
                        st.rerun()  # Rerun the app to update the UI
                        return True
                    else:
                        st.error("Username already exists")
                        return False
        
        return False
    
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated"""
        return st.session_state.authenticated
    
    def get_username(self) -> Optional[str]:
        """Get the username of the authenticated user"""
        return st.session_state.username if self.is_authenticated() else None
    
    def get_user_data(self) -> Optional[Dict[str, Any]]:
        """Get the user data of the authenticated user"""
        return st.session_state.user_data if self.is_authenticated() else None
    
    def logout(self):
        """Log out the current user"""
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.user_data = None
        st.rerun()  # Rerun the app to update the UI
    
    def require_login(self) -> bool:
        """
        Require user to be logged in to continue
        Returns True if the user is authenticated, False otherwise
        """
        if not self.is_authenticated():
            self.login_form()
            return False
        return True