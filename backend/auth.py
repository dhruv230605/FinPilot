import streamlit as st
import json
import os

USER_FILE = "backend/users.json"

# Ensure the file exists
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

# Load users from file
def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

# Save users to file
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# Register a new user
def register_user(email, password):
    users = load_users()
    if email in users:
        st.warning("🚫 User already exists.")
    else:
        users[email] = password
        save_users(users)
        st.success("✅ User registered successfully.")

# Authenticate user
def login_user(email, password):
    users = load_users()
    if users.get(email) == password:
        st.session_state.current_user_email = email
        return True
    return False

# Logout user
def logout_user():
    if 'current_user_email' in st.session_state:
        del st.session_state.current_user_email
