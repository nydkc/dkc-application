import pytest
from unittest.mock import patch, MagicMock
from dkc.auth.models import User
from dkc.application.models import Application
from common.datastore import db


def test_verification_page_access(client, login, mock_user):
    response = client.get("/application/verification")
    assert response.status_code == 200
    assert b"Verification" in response.data


def test_send_ltg_verification_email(client, login, mock_user, mock_email_provider):
    """Test sending LTG verification email."""
    with patch(
        "dkc.application.verification.get_email_provider",
        return_value=mock_email_provider,
    ) as mock_get_provider, patch(
        "dkc.application.verification.create_verification_auth_token"
    ) as mock_create_token:

        mock_token_key = MagicMock()
        mock_token_key.urlsafe.return_value = b"safe_token_key"
        mock_create_token.return_value = mock_token_key

        response = client.post(
            "/application/verification",
            data={"task": "ltg", "ltg-email": "ltg@example.com"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert mock_email_provider.send_email.called

        call_args = mock_email_provider.send_email.call_args
        assert call_args is not None
        kwargs = call_args[1]
        assert kwargs["to_email"].email == "ltg@example.com"
        assert "Distinguished Key Clubber Application" in kwargs["subject"].line

        # Verify verification email and token are set
        saved_app = mock_user.application.get()
        assert saved_app.verification_ltg_email == "ltg@example.com"
        assert saved_app.verification_ltg_sent is True
        assert saved_app.verification_ltg_token == mock_token_key


def test_verification_incomplete_profile(client, login, mock_user):
    mock_user.application.get.return_value.school = None

    response = client.post(
        "/application/verification",
        data={"task": "ltg", "ltg-email": "ltg@example.com"},
        follow_redirects=True,
    )

    assert response.status_code == 400


def test_verification_after_submission(client, login, mock_user):
    mock_user.application.get.return_value.submit_time = MagicMock()

    response = client.post(
        "/application/verification",
        data={"task": "ltg", "ltg-email": "ltg@example.com"},
        follow_redirects=True,
    )

    assert response.status_code == 409


def test_verification_invalid_task(client, login, mock_user):
    """Test verification with invalid task type."""
    with patch(
        "dkc.application.verification.create_verification_auth_token"
    ) as mock_create_token:

        mock_token_key = MagicMock()
        mock_token_key.urlsafe.return_value = b"safe_token_key"
        mock_create_token.return_value = mock_token_key

        response = client.post(
            "/application/verification",
            data={"task": "invalid-task", "email": "test@example.com"},
            follow_redirects=True,
        )

        assert response.status_code == 400


def test_send_club_president_verification(client, login, mock_user, mock_email_provider):
    """Test sending club president verification email."""
    with patch(
        "dkc.application.verification.get_email_provider",
        return_value=mock_email_provider,
    ), patch(
        "dkc.application.verification.create_verification_auth_token"
    ) as mock_create_token:

        mock_token_key = MagicMock()
        mock_token_key.urlsafe.return_value = b"safe_token_key"
        mock_create_token.return_value = mock_token_key

        response = client.post(
            "/application/verification",
            data={"task": "club-president", "club-president-email": "president@example.com"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert mock_email_provider.send_email.called

        call_args = mock_email_provider.send_email.call_args
        kwargs = call_args[1]
        assert kwargs["to_email"].email == "president@example.com"

        # Verify verification email and token are set
        saved_app = mock_user.application.get()
        assert saved_app.verification_club_president_email == "president@example.com"
        assert saved_app.verification_club_president_sent is True
        assert saved_app.verification_club_president_token == mock_token_key


def test_send_faculty_advisor_verification(client, login, mock_user, mock_email_provider):
    """Test sending faculty advisor verification email."""
    with patch(
        "dkc.application.verification.get_email_provider",
        return_value=mock_email_provider,
    ), patch(
        "dkc.application.verification.create_verification_auth_token"
    ) as mock_create_token:

        mock_token_key = MagicMock()
        mock_token_key.urlsafe.return_value = b"safe_token_key"
        mock_create_token.return_value = mock_token_key

        response = client.post(
            "/application/verification",
            data={"task": "faculty-advisor", "faculty-advisor-email": "advisor@example.com"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert mock_email_provider.send_email.called

        call_args = mock_email_provider.send_email.call_args
        kwargs = call_args[1]
        assert kwargs["to_email"].email == "advisor@example.com"

        # Verify verification email and token are set
        saved_app = mock_user.application.get()
        assert saved_app.verification_faculty_advisor_email == "advisor@example.com"
        assert saved_app.verification_faculty_advisor_sent is True
        assert saved_app.verification_faculty_advisor_token == mock_token_key
