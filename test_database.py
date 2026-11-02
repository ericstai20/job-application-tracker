# test_database.py
# Automated checks for database.py. Run them all with:  pytest
# Each test sets up a situation, calls a function, then uses assert to
# check the result. If an assert is False, pytest reports that test as
# failed and shows what the values actually were.

import sqlite3

import pytest

import database


# A fixture is setup code that pytest runs before each test that asks
# for it by name. autouse=True means every test gets it automatically.
@pytest.fixture(autouse=True)
def temporary_database(tmp_path, monkeypatch):
    """Point database.py at a fresh, empty database for each test,
    so tests never touch my real applications.db."""
    # tmp_path is a new empty folder that pytest deletes afterwards.
    # monkeypatch changes DB_PATH for this test only, then puts it back.
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_db()


def add_example(company="Acme", role="Engineer", status="Applied",
                date_applied="2026-10-01", **optional):
    """Add an application with sensible defaults, so each test only
    has to spell out the details it cares about."""
    database.add_application(company, role, status, date_applied, **optional)


def test_new_database_is_empty():
    assert database.get_applications() == []


def test_added_application_comes_back_with_every_field():
    add_example(location="Austin, TX", job_link="https://example.com/job",
                notes="Referral from Sam")

    [application] = database.get_applications()
    assert application["company"] == "Acme"
    assert application["role"] == "Engineer"
    assert application["status"] == "Applied"
    assert application["date_applied"] == "2026-10-01"
    assert application["location"] == "Austin, TX"
    assert application["job_link"] == "https://example.com/job"
    assert application["notes"] == "Referral from Sam"


def test_optional_fields_default_to_none():
    add_example()

    [application] = database.get_applications()
    assert application["location"] is None
    assert application["job_link"] is None
    assert application["notes"] is None


def test_applications_are_newest_first():
    add_example(company="Middle", date_applied="2026-10-15")
    add_example(company="Oldest", date_applied="2026-09-01")
    add_example(company="Newest", date_applied="2026-10-30")

    companies = [app["company"] for app in database.get_applications()]
    assert companies == ["Newest", "Middle", "Oldest"]


def test_filter_by_status_returns_only_that_status():
    add_example(company="A", status="Applied")
    add_example(company="B", status="Interviewing")
    add_example(company="C", status="Applied")

    applied = database.get_applications("Applied")
    assert sorted(app["company"] for app in applied) == ["A", "C"]


def test_filter_with_no_matches_returns_empty_list():
    add_example(status="Applied")
    add_example(status="Interviewing")

    assert database.get_applications("Rejected") == []


def test_count_by_status_includes_statuses_with_zero():
    add_example(status="Applied")
    add_example(status="Applied")
    add_example(status="Offer")

    assert database.count_by_status() == {
        "Applied": 2,
        "Interviewing": 0,
        "Offer": 1,
        "Rejected": 0,
    }


def test_update_changes_only_that_application():
    add_example(company="Keep me")
    add_example(company="Change me")
    by_company = {app["company"]: app for app in database.get_applications()}
    target = by_company["Change me"]

    database.update_application(target["id"], "Changed", "Senior Engineer",
                                "Offer", "2026-10-02", notes="New notes")

    updated = {app["id"]: app for app in database.get_applications()}
    assert updated[target["id"]]["company"] == "Changed"
    assert updated[target["id"]]["status"] == "Offer"
    assert updated[target["id"]]["notes"] == "New notes"
    # The other application must be exactly as it was.
    assert updated[by_company["Keep me"]["id"]] == by_company["Keep me"]


def test_delete_removes_only_that_application():
    add_example(company="Keep me")
    add_example(company="Delete me")
    by_company = {app["company"]: app for app in database.get_applications()}

    database.delete_application(by_company["Delete me"]["id"])

    companies = [app["company"] for app in database.get_applications()]
    assert companies == ["Keep me"]


def test_init_db_again_keeps_existing_data():
    # The app calls init_db() on every rerun, so it must never wipe data.
    add_example()
    database.init_db()

    assert len(database.get_applications()) == 1


# parametrize runs this one test once for each status in the list.
@pytest.mark.parametrize("status", database.STATUSES)
def test_every_status_in_the_list_is_accepted(status):
    # Catches STATUSES and the CHECK rule in init_db() drifting apart.
    add_example(status=status)

    assert database.get_applications()[0]["status"] == status


def test_unknown_status_is_rejected():
    # pytest.raises passes only if the code inside raises this error.
    with pytest.raises(sqlite3.IntegrityError):
        add_example(status="Ghosted")
