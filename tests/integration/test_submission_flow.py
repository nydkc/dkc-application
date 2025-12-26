import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from dkc.auth.models import User
from dkc.application.models import Application
from common.datastore import db


def test_submission_page_access(client, login, mock_user):
    response = client.get("/application/submit")
    assert response.status_code == 200
    assert b"Submit" in response.data


def test_submit_application(client, login, mock_user, mock_email_provider):
    mock_user.application.get.return_value.verification_ltg = True
    mock_user.application.get.return_value.verification_club_president = True
    mock_user.application.get.return_value.verification_faculty_advisor = True
    mock_user.application.get.return_value.verification_applicant = True

    # Patch the imported name in dkc.application.submit
    with patch(
        "dkc.application.submit.get_email_provider", return_value=mock_email_provider
    ):
        response = client.post("/application/submit", follow_redirects=True)

        assert response.status_code == 200
        assert mock_user.application.get().put.called
        assert mock_email_provider.send_email.called

        # Verify submit time was set
        saved_app = mock_user.application.get()
        assert saved_app.submit_time is not None
        assert isinstance(saved_app.submit_time, datetime)

        # Verify email content
        call_args = mock_email_provider.send_email.call_args
        kwargs = call_args[1]
        assert kwargs["to_email"].email == mock_user.email
        assert "Submission Confirmation" in kwargs["subject"].line


def test_submit_application_missing_verifications(client, login, mock_user):
    """Test submission with missing verifications."""
    # Mock only some verifications
    # Need fewer than 2 external verifications to fail
    mock_user.application.get.return_value.verification_ltg = True
    mock_user.application.get.return_value.verification_club_president = False
    mock_user.application.get.return_value.verification_faculty_advisor = False
    mock_user.application.get.return_value.verification_applicant = True

    response = client.post("/application/submit", follow_redirects=True)

    # Should return 400 Bad Request
    assert response.status_code == 400
    assert b"Your application is not complete!" in response.data

    # Ensure submit_time was NOT set (verification failing validation prevents submission)
    # We can check if application.put() was called.
    # In handle_post, put() is called only after successful checks.
    # Note: application.put mock is shared, so we assert not called or call count is 0 if we reset it?
    # But mock_user fixture is session/function scoped?
    # It's function scoped (default for pytest fixture).
    assert not mock_user.application.get().put.called


def test_submit_application_already_submitted(client, login, mock_user):
    mock_user.application.get.return_value.submit_time = MagicMock()

    response = client.post("/application/submit", follow_redirects=True)

    assert response.status_code == 409


def test_submit_application_incomplete(client, login, mock_user):
    mock_user.application.get.return_value.school = None

    response = client.post("/application/submit", follow_redirects=True)

    assert response.status_code == 400


def test_submit_application_email_failure(client, login, mock_user, mock_email_provider):
    """Test submission when email sending fails."""
    mock_user.application.get.return_value.verification_ltg = True
    mock_user.application.get.return_value.verification_club_president = True
    mock_user.application.get.return_value.verification_faculty_advisor = True
    mock_user.application.get.return_value.verification_applicant = True

    # Configure email provider to fail
    mock_email_provider.send_email.return_value = MagicMock(success=False, error="SMTP Error")

    with patch(
        "dkc.application.submit.get_email_provider", return_value=mock_email_provider
    ):
        response = client.post("/application/submit", follow_redirects=True)

        # Depending on implementation, this might still return 200 but log error,
        # or fail 500.
        # Looking at dkc/application/submit.py logic:
        # It calls send_submission_confirmation_email logic which logs error but doesn't raise exception?
        # Actually checking code:
        # submit.py calls `send_submission_confirmation_email`.
        # That function calls `email_provider.send_email`.
        # Only if it RAISES exception would it crash. If it returns False, usually ignored or logged.

        # The application aborts with 503 if email fails
        assert response.status_code == 503

        # Verify submit time was NOT set and application NOT saved
        assert not mock_user.application.get().put.called
