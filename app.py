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


def describe(application):
    """Turn an application into a readable label for the dropdown."""
    return (f"{application['role']} at {application['company']} "
            f"({application['date_applied']})")


# --- Update or delete an existing application ---
# This section comes before the table so the table shows any change
# made here in the same run.
applications = database.get_applications()

if applications:
    st.subheader("Update an Application")
    selected = st.selectbox("Application", applications, format_func=describe)

    # Start the status dropdown on the application's current status.
    # The key includes the id so each application gets its own dropdown.
    new_status = st.selectbox(
        "New status",
        database.STATUSES,
        index=database.STATUSES.index(selected["status"]),
        key=f"status_{selected['id']}",
    )
    if st.button("Update status"):
        database.update_status(selected["id"], new_status)
        st.success(f"{describe(selected)} is now {new_status}.")

    # Deleting can't be undone, so ask for confirmation first.
    confirm_delete = st.checkbox("Yes, I want to delete this application")
    if st.button("Delete application", disabled=not confirm_delete):
        database.delete_application(selected["id"])
        st.success(f"Deleted {describe(selected)}.")

# --- Table of all applications ---
st.subheader("My Applications")

# --- Summary: one number tile for the total and one per status ---
counts = database.count_by_status()
columns = st.columns(len(counts) + 1)
columns[0].metric("Total", sum(counts.values()))
# zip pairs each remaining column with one status and its count.
for column, (status, count) in zip(columns[1:], counts.items()):
    column.metric(status, count)

show =st.selectbox("Show", ["All"] + database.STATUSES)

# "All" means no filter, so pass None instead of a status.
if show == "All":
    applications = database.get_applications()
else:
    applications = database.get_applications(show)

if applications:
    st.dataframe(applications, hide_index=True)
elif show == "All":
    st.info("No applications yet.")
else:
    st.info(f"No applications with status {show}.")
