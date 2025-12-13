import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_user():
    """
    Provides a mock authenticated user with a mock application.

    The mock user has all required authentication properties and a fully
    configured mock application with common fields pre-filled.
    """
    user = MagicMock()
    user.is_authenticated = True
    user.is_active = True
    user.is_anonymous = False
    user.get_id.return_value = "test_auth_id"
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"

    mock_app = MagicMock()
    mock_app.key.urlsafe.return_value = b"safe_key"
    mock_app.submit_time = None

    # Common fields
    mock_app.grade = "12"
    mock_app.address = "123 St"
    mock_app.city = "City"
    mock_app.zip_code = "12345"
    mock_app.phone_number = "555-1234"
    mock_app.division = "1"
    mock_app.ltg = "LTG"
    mock_app.school = "School"
    mock_app.school_address = "School St"
    mock_app.school_city = "City"
    mock_app.school_zip_code = "12345"
    mock_app.club_president = "Prez"
    mock_app.club_president_phone_number = "555-1234"
    mock_app.faculty_advisor = "Advisor"
    mock_app.faculty_advisor_phone_number = "555-1234"

    # Verification fields (default to False/None)
    mock_app.verification_ltg = False
    mock_app.verification_club_president = False
    mock_app.verification_faculty_advisor = False
    mock_app.verification_applicant = False

    user.application.get.return_value = mock_app
    return user


@pytest.fixture
def auth_patches(mock_user):
    """Patches User authentication methods to return the mock_user."""
    with patch(
        "dkc.auth.models.User.get_authenticated_user", return_value=mock_user
    ), patch("dkc.auth.models.User.find_by_auth_credential_id", return_value=mock_user):
        yield mock_user


@pytest.fixture
def login(client, auth_patches):
    """Logs in the mock user and returns the authenticated client."""
    client.post(
        "/login",
        data={"email": "test@example.com", "password": "password"},
        follow_redirects=True,
    )
    return client
