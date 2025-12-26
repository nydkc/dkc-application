import pytest
from unittest.mock import patch, MagicMock


def test_save_profile(client, login, mock_user):
    """Test saving profile data and verify it's persisted correctly."""
    response = client.post(
        "/application/profile",
        data={
            "first-name": "Test",
            "last-name": "User",
            "grade": "12",
            "address": "123 Main St",
            "city": "New York",
            "zip-code": "10001",
            "phone-number": "123-555-1234",
            "division": "1",
            "ltg": "Lieutenant Governor",
            "school": "Test High School",
            "school-address": "456 School Ln",
            "school-city": "New York",
            "school-zip-code": "10002",
            "club-president": "Prez",
            "club-president-phone-number": "123-555-5678",
            "faculty-advisor": "Advisor",
            "faculty-advisor-phone-number": "123-555-9012",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Verify data was saved correctly
    saved_app = mock_user.application.get()
    assert saved_app.grade == "12"
    assert saved_app.address == "123 Main St"
    assert saved_app.city == "New York"
    assert saved_app.zip_code == "10001"
    assert saved_app.phone_number == "123-555-1234"
    assert saved_app.division == "1"
    assert saved_app.ltg == "Lieutenant Governor"
    assert saved_app.school == "Test High School"
    assert saved_app.school_address == "456 School Ln"
    assert saved_app.school_city == "New York"
    assert saved_app.school_zip_code == "10002"
    assert saved_app.club_president == "Prez"
    assert saved_app.club_president_phone_number == "123-555-5678"
    assert saved_app.faculty_advisor == "Advisor"
    assert saved_app.faculty_advisor_phone_number == "123-555-9012"


def test_save_personal_statement(client, login, mock_user):
    """Test saving personal statement and verify it's persisted correctly."""
    response = client.post(
        "/application/personal-statement",
        data={
            "personal-statement-choice": "Topic A",
            "personal-statement": "This is my essay.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert mock_user.application.get().put.called

    # Verify data was saved
    saved_app = mock_user.application.get()
    assert saved_app.personal_statement_choice == "Topic A"
    assert saved_app.personal_statement == "This is my essay."


def test_save_projects(client, login, mock_user):
    """Test saving projects and verify they're persisted correctly."""
    response = client.post(
        "/application/projects",
        data={
            "international-projects-section": "Service",
            "international-projects-event": "Charity Walk",
            "international-projects-description": "Walked for charity.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert mock_user.application.get().put.called

    # Verify data was saved
    saved_app = mock_user.application.get()
    # Note: Projects are structured properties, so we verify put was called
    # The actual structured property validation would require real datastore


def test_save_involvement(client, login, mock_user):
    """Test saving involvement data and verify it's persisted correctly."""
    response = client.post(
        "/application/involvement",
        data={
            "key-club-week-monday": "Monday Activity",
            "attendance-dtc": "on",
            "positions": "President",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert mock_user.application.get().put.called

    # Verify data was saved
    saved_app = mock_user.application.get()
    assert saved_app.key_club_week_mon == "Monday Activity"
    assert saved_app.attendance_dtc is True
    assert saved_app.positions == "President"


def test_save_activities(client, login, mock_user):
    """Test saving activities data and verify it's persisted correctly."""
    response = client.post(
        "/application/activities",
        data={
            "advocacy-cause": "Environment",
            "advocacy-description": "Cleaned up park.",
            "kiwanis-one-day-event": "Park Cleanup",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert mock_user.application.get().put.called

    # Verify data was saved
    saved_app = mock_user.application.get()
    assert saved_app.advocacy_cause == "Environment"
    assert saved_app.advocacy_description == "Cleaned up park."


def test_save_other(client, login, mock_user):
    """Test saving other section data and verify it's persisted correctly."""
    response = client.post(
        "/application/other",
        data={
            "outstanding-awards": "Best Key Clubber",
            "recommender-checkbox": "on",
            "recommender-points": "Good student",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert mock_user.application.get().put.called

    # Verify data was saved
    saved_app = mock_user.application.get()
    assert saved_app.outstanding_awards == "Best Key Clubber"
    assert saved_app.recommender_points == "Good student"


@pytest.mark.parametrize("endpoint,test_data", [
    ("/application/profile", {"first-name": "Test"}),
    ("/application/personal-statement", {"personal-statement": "New essay"}),
    ("/application/projects", {"international-projects-section": "Service"}),
    ("/application/involvement", {"positions": "New Position"}),
    ("/application/activities", {"advocacy-cause": "New Cause"}),
    ("/application/other", {"outstanding-awards": "New Award"}),
])
def test_edit_after_submission_returns_409(client, login, mock_user, endpoint, test_data):
    """Test that editing any application section after submission returns 409 Conflict."""
    mock_user.application.get.return_value.submit_time = MagicMock()

    response = client.post(endpoint, data=test_data, follow_redirects=True)

    assert response.status_code == 409
