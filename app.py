import streamlit as st
import pandas as pd
import os
import hashlib

# File to store user account data
user_file = 'users.csv'
# File to store truck registration data
data_file = 'truck_data.csv'

# Initialize user_data and truck_data as empty dictionaries
user_data = {}
truck_data = {}

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to create an empty users.csv file with the correct headers
def create_user_file():
    pd.DataFrame(columns=["Username", "Password"]).to_csv(user_file, index=False)

# Function to create an empty truck_data.csv file with the correct headers
def create_data_file():
    pd.DataFrame(columns=["Truck Number", "Driver's Name", "Contact Number", "Registration Date", "Username"]).to_csv(data_file, index=False)

# Check if the user file exists
if not os.path.exists(user_file):
    create_user_file()
    st.warning(f"{user_file} created successfully.")

# Load existing user data if available
if os.path.exists(user_file):
    try:
        user_data = pd.read_csv(user_file).set_index('Username').to_dict(orient='index')
    except pd.errors.EmptyDataError:
        st.warning("The user file is empty. Please register an account.")
        create_user_file()

# Check if the data file exists
if not os.path.exists(data_file):
    create_data_file()
    st.warning(f"{data_file} created successfully.")

# Load existing truck data if available
if os.path.exists(data_file):
    try:
        truck_data_df = pd.read_csv(data_file)
        # Ensure the file is not empty and contains the correct columns
        if not truck_data_df.empty and "Truck Number" in truck_data_df.columns:
            truck_data = truck_data_df.set_index('Truck Number').to_dict(orient='index')
        else:
            st.warning("The truck data file is empty or missing the required columns.")
            create_data_file()
    except pd.errors.EmptyDataError:
        st.warning("The truck data file is empty. Please register some trucks.")
        create_data_file()

# Streamlit form for login or registration
st.title("🚚 Truck Registration and Login System")
st.write("Welcome to the **Truck Registration System**. You can create an account, log in, and register trucks easily!")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# Sign Up and Login tabs
tab1, tab2 = st.tabs(["📝 Sign Up", "🔑 Login"])

# Sign Up tab
with tab1:
    st.subheader("Create a New Account")
    st.info("Fill out the details below to register your account.")

    # Input fields for new user registration
    new_username = st.text_input("👤 Username", key="register_username")
    new_password = st.text_input("🔒 Password", type="password", key="register_password")
    
    if st.button("Create Account", key="register_button"):
        progress = st.progress(0)
        if new_username in user_data:
            st.error("Username already exists. Please choose a different username.")
        elif new_username and new_password:
            for percent_complete in range(100):
                progress.progress(percent_complete + 1)
            user_data[new_username] = {
                "Password": hash_password(new_password)
            }
            pd.DataFrame.from_dict(user_data, orient='index').reset_index().rename(columns={"index": "Username"}).to_csv(user_file, index=False)
            st.session_state.logged_in = True
            st.session_state.current_user = new_username
            st.success("🎉 Account registered successfully! You are now logged in.")
        else:
            st.error("Please fill out both fields.")

# Login tab
with tab2:
    st.subheader("Log in to Your Account")
    
    # Input fields for user login
    username = st.text_input("👤 Username", key="login_username")
    password = st.text_input("🔒 Password", type="password", key="login_password")
    
    if st.button("Login", key="login_button"):
        if username in user_data and user_data[username]["Password"] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.success(f"Welcome, {username}! 🎉")
        else:
            st.error("Invalid username or password. ❌")

# If logged in, show the truck registration form
if st.session_state.logged_in:
    st.subheader("🚛 Register a New Truck")
    st.write(f"Welcome, {st.session_state.current_user}! Register your truck below.")

    # Input fields for truck details
    truck_number = st.text_input("🚚 Truck Number")
    driver_name = st.text_input("👨‍✈️ Driver's Name")
    contact_number = st.text_input("📞 Contact Number")
    registration_date = st.date_input("📅 Registration Date")

    # Button to submit the form
    if st.button("Register Truck"):
        if truck_number and driver_name and contact_number:
            truck_data[truck_number] = {
                "Driver's Name": driver_name,
                "Contact Number": contact_number,
                "Registration Date": registration_date,
                "Username": st.session_state.current_user,
            }
            # Convert truck_data to DataFrame and save to CSV
            if truck_data:
                truck_data_df = pd.DataFrame.from_dict(truck_data, orient='index').reset_index().rename(columns={"index": "Truck Number"})
                truck_data_df.to_csv(data_file, index=False)
                st.success(f"Truck {truck_number} registered successfully! ✅")
            else:
                st.error("Error saving truck data.")
        else:
            st.error("Please fill out all the fields. 📝")
    
    # Display the registered trucks for the logged-in user
    st.subheader(f"🚛 Registered Trucks for {st.session_state.current_user}")
    user_trucks = {truck: details for truck, details in truck_data.items() if "Username" in details and details["Username"] == st.session_state.current_user}
    
    if user_trucks:
        for truck, details in user_trucks.items():
            st.write(f"**🚚 Truck Number:** {truck}")
            st.write(f"**👨‍✈️ Driver's Name:** {details['Driver\'s Name']}")
            st.write(f"**📞 Contact Number:** {details['Contact Number']}")
            st.write(f"**📅 Registration Date:** {details['Registration Date']}")
            st.write("---")
    else:
        st.write("No trucks registered yet. 📝")

# Logout button
if st.session_state.logged_in:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.success("Logged out successfully! 👋")
