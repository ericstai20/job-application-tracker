import streamlit as st

import database

# Make sure the table exists before we try to read from it.
database.init_db()

st.title("Job Application Tracker")

# --- Form for adding a new application ---
with st.form("add_application", clear_on_submit=True):
    st.subheader("Add an Application")
    company = st.text_input("Company *")
    role = st.text_input("Role *")
    status = st.selectbox("Status", database.STATUSES)
    date_applied = st.date_input("Date applied")
    location = st.text_input("Location")
    job_link = st.text_input("Job link")
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Add application")

if submitted:
    if not company.strip() or not role.strip():
        st.error("Company and role are required.")
    else:
        database.add_application(
            company.strip(),
            role.strip(),
            status,
            date_applied.isoformat(),
            # Empty optional fields are saved as None (NULL), not "".
            location.strip() or None,
            job_link.strip() or None,
            notes.strip() or None,
        )
        st.success(f"Added {role.strip()} at {company.strip()}.")

# --- Table of all applications ---
st.subheader("My Applications")
applications = database.get_applications()

if applications:
    st.dataframe(applications, hide_index=True)
else:
    st.info("No applications yet.")
