from datetime import date

import streamlit as st

import ai_helper
import database

# Make sure the table exists before we try to read from it.
database.init_db()

st.title("Job Application Tracker")

# Overview is listed first so it's the tab you see when the app opens.
overview_tab, add_tab, manage_tab, letter_tab = st.tabs(
    ["Overview", "Add", "Edit / Delete", "Cover Letter"])


def describe(application):
    """Turn an application into a readable label for the dropdown."""
    return (f"{application['role']} at {application['company']} "
            f"({application['date_applied']})")


# Tabs only hide things on screen: Streamlit still runs every block
# below from top to bottom. So the Add and Edit / Delete blocks come
# before the Overview block, so the table shows any change in the same run.

# --- Form for adding a new application ---
with add_tab:
    # --- Let Claude fill in the form from a job posting ---
    # This has to sit outside the form: a form only sends its values when
    # its own submit button is pressed, so it can't hold a second button.
    st.subheader("Fill In From a Job Posting")
    fill_link = st.text_input("Job posting link")
    fill_text = st.text_area(
        "Or paste the posting text (use this if the link doesn't work)")

    if st.button("Fill in the form"):
        if not ai_helper.has_api_key():
            st.error("Add your ANTHROPIC_API_KEY to the .env file, "
                     "then restart the app.")
        elif not fill_link.strip() and not fill_text.strip():
            st.error("Enter a link or paste the posting text first.")
        else:
            with st.spinner("Claude is reading the posting..."):
                try:
                    details = ai_helper.extract_job_details(
                        fill_link.strip(), fill_text.strip())
                except ai_helper.AIError as error:
                    details = None
                    st.error(str(error))

            if details and not details["found"]:
                # When nothing is found, Claude explains why in notes.
                st.error(f"{details['notes']} If the site blocks Claude, "
                         "paste the posting text instead.")
            elif details:
                # Setting a widget's key in session_state before the widget
                # is drawn makes it start with that value. This works because
                # the form below hasn't been drawn yet in this run.
                st.session_state["add_company"] = details["company"]
                st.session_state["add_role"] = details["role"]
                st.session_state["add_location"] = details["location"]
                st.session_state["add_notes"] = details["notes"]
                if fill_link.strip():
                    st.session_state["add_job_link"] = fill_link.strip()
                st.success("Filled in the form below. "
                           "Check everything before adding.")

    # The keys let the code above put values into these boxes.
    with st.form("add_application", clear_on_submit=True):
        st.subheader("Add an Application")
        company = st.text_input("Company *", key="add_company")
        role = st.text_input("Role *", key="add_role")
        status = st.selectbox("Status", database.STATUSES)
        date_applied = st.date_input("Date applied")
        location = st.text_input("Location", key="add_location")
        job_link = st.text_input("Job link", key="add_job_link")
        notes = st.text_area("Notes", key="add_notes")
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

# --- Edit or delete an existing application ---
with manage_tab:
    applications = database.get_applications()

    if applications:
        st.subheader("Edit an Application")
        # The dropdown holds ids, not whole applications. Editing changes an
        # application's details but never its id, so Streamlit can still
        # find the one you picked after a save instead of resetting to the
        # first. The fixed key stops it treating the dropdown as new.
        by_id = {application["id"]: application for application in applications}
        selected_id = st.selectbox(
            "Application",
            list(by_id),
            format_func=lambda app_id: describe(by_id[app_id]),
            key="selected_app",
        )
        selected = by_id[selected_id]

        # Every field starts on the application's current value.
        # The form key includes the id so each application gets its own form.
        with st.form(f"edit_{selected['id']}"):
            company = st.text_input("Company *", selected["company"])
            role = st.text_input("Role *", selected["role"])
            status = st.selectbox(
                "Status",
                database.STATUSES,
                index=database.STATUSES.index(selected["status"]),
            )
            # The database stores dates as text, but date_input needs a date.
            date_applied = st.date_input(
                "Date applied", date.fromisoformat(selected["date_applied"]))
            # Empty optional fields are None, but text boxes need "".
            location = st.text_input("Location", selected["location"] or "")
            job_link = st.text_input("Job link", selected["job_link"] or "")
            notes = st.text_area("Notes", selected["notes"] or "")
            saved = st.form_submit_button("Save changes")

        if saved:
            if not company.strip() or not role.strip():
                st.error("Company and role are required.")
            else:
                database.update_application(
                    selected["id"],
                    company.strip(),
                    role.strip(),
                    status,
                    date_applied.isoformat(),
                    location.strip() or None,
                    job_link.strip() or None,
                    notes.strip() or None,
                )
                st.success(f"Saved changes to {role.strip()} at "
                           f"{company.strip()}.")

        st.subheader("Delete an Application")

        # Deleting can't be undone, so ask for confirmation first.
        confirm_delete = st.checkbox("Yes, I want to delete this application")
        if st.button("Delete application", disabled=not confirm_delete):
            database.delete_application(selected["id"])
            st.success(f"Deleted {describe(selected)}.")
    else:
        st.info("No applications yet. Add one in the Add tab.")

# --- Summary and table of all applications ---
with overview_tab:
    st.subheader("My Applications")

    # --- Summary: one number tile for the total and one per status ---
    counts = database.count_by_status()
    columns = st.columns(len(counts) + 1)
    columns[0].metric("Total", sum(counts.values()))
    # zip pairs each remaining column with one status and its count.
    for column, (status, count) in zip(columns[1:], counts.items()):
        column.metric(status, count)

    show = st.selectbox("Show", ["All"] + database.STATUSES)

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

# --- Draft a cover letter with Claude ---
# This block doesn't change any data, so its place in the file
# doesn't matter.
with letter_tab:
    st.subheader("Draft a Cover Letter")
    applications = database.get_applications()
    background = ai_helper.load_background()

    if not ai_helper.has_api_key():
        st.warning("Add your ANTHROPIC_API_KEY to the .env file, "
                   "then restart the app.")
    elif background is None:
        st.warning("Fill in background.md with your experience and an "
                   "example cover letter first.")
    elif not applications:
        st.info("No applications yet. Add one in the Add tab.")
    else:
        # Same id trick as the Edit / Delete tab, with its own key.
        by_id = {application["id"]: application for application in applications}
        letter_id = st.selectbox(
            "Application",
            list(by_id),
            format_func=lambda app_id: describe(by_id[app_id]),
            key="letter_app",
        )
        application = by_id[letter_id]

        job_posting = st.text_area("Job posting", height=250,
                                   key=f"posting_{letter_id}")

        if st.button("Draft cover letter"):
            if not job_posting.strip():
                st.error("Paste the job posting first.")
            else:
                with st.spinner("Claude is writing your letter..."):
                    try:
                        # session_state survives reruns, so the draft
                        # stays on screen after the next click.
                        st.session_state[f"letter_{letter_id}"] = (
                            ai_helper.draft_cover_letter(
                                background,
                                application["company"],
                                application["role"],
                                job_posting.strip(),
                            ))
                    except ai_helper.AIError as error:
                        st.error(str(error))

        letter = st.session_state.get(f"letter_{letter_id}")
        if letter:
            st.text_area("Your draft (edit it here, then copy it out)",
                         letter, height=450)
