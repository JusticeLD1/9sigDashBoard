#log in / sign up page

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import modules
import modules.portfolio



def signup():
    st.title("Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password")
    confirm_password = st.text_input("Confirm Password")
    if st.button("Sign Up", key="signup_button"):
        st.success("Sign Up Successful")

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password")
    if st.button("Login", key="login_button"):
        st.success("Login Successful")
    

