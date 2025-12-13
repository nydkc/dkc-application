import pytest
from unittest.mock import patch, MagicMock


def test_save_profile(client, login, mock_user):
    with patch("dkc.application.profile.ndb.put_multi") as mock_put_multi:
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
        assert mock_put_multi.called


def test_save_personal_statement(client, login, mock_user):
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


def test_save_projects(client, login, mock_user):
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


def test_save_involvement(client, login, mock_user):
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


def test_save_activities(client, login, mock_user):
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


def test_save_other(client, login, mock_user):
    response = client.post(
        "/application/other",
        data={
            "outstanding-awards": "Best Club",
            "recommender-checkbox": "on",
            "recommender-points": "Good student",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert mock_user.application.get().put.called


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
